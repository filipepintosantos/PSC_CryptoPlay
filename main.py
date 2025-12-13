"""
Main script for cryptocurrency price tracking and analysis.
Orchestrates fetching, storing, analyzing, and reporting.
"""

import argparse
import sys
import configparser
import time
import csv
from pathlib import Path
from datetime import datetime

from typing import Optional

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from api_yfinance import YFinanceCryptoAPI
from database import CryptoDatabase
from analysis import StatisticalAnalyzer
from excel_reporter import ExcelReporter
from volatility_analysis import VolatilityAnalyzer

# Constants
DEFAULT_SYMBOLS = "BTC,ETH,ADA,XRP,SOL"


def import_csv_data(csv_path: str, symbol: str, db: CryptoDatabase,
                    date_column: str = '0', price_column: str = '1',
                    date_format: str = None, skip_header: bool = True) -> int:
    """
    Import historical data from CSV file.
    
    Args:
        csv_path: Path to CSV file
        symbol: Cryptocurrency symbol
        db: Database instance
        date_column: Date column name or index
        price_column: Price column name or index
        date_format: Date format string
        skip_header: Skip first row
    
    Returns:
        Number of quotes imported
    """
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Read header if present
        if skip_header:
            header = next(reader)
            try:
                date_idx = header.index(date_column)
                price_idx = header.index(price_column)
            except ValueError:
                date_idx = int(date_column)
                price_idx = int(price_column)
        else:
            date_idx = int(date_column)
            price_idx = int(price_column)
        
        count = 0
        for row_num, row in enumerate(reader, start=2 if skip_header else 1):
            try:
                date_str = row[date_idx].strip()
                price_str = row[price_idx].strip()
                
                # Parse date
                if date_format:
                    date_obj = datetime.strptime(date_str, date_format)
                else:
                    # Try common formats
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                
                # Parse price
                price_val = float(price_str.replace(',', '').replace('€', '').replace('$', '').strip())
                
                quote = {
                    'symbol': symbol,
                    'name': symbol,
                    'price_eur': price_val,
                    'timestamp': date_obj
                }
                
                if db.insert_or_update_quote(symbol, quote):
                    count += 1
                    
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping row {row_num}: {e}")
                continue
    
    return count


def load_config() -> configparser.ConfigParser:
    """Load configuration from config.ini file."""
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent / "config" / "config.ini"
    if config_path.exists():
        config.read(config_path)
    return config


def determine_symbols(args, config: configparser.ConfigParser, db_path: str) -> Optional[list]:
    """Determine which cryptocurrency symbols to process based on arguments."""
    if args.all_from_db:
        # Get all symbols from crypto_info table
        from database import CryptoDatabase
        temp_db = CryptoDatabase(db_path)
        result = temp_db.conn.execute('SELECT code FROM crypto_info ORDER BY market_cap DESC').fetchall()
        temp_db.close()
        symbols = [row[0] for row in result]
        if not symbols:
            print("No cryptocurrencies found in crypto_info table")
            return None
        return symbols
    elif args.symbols:
        return [s.strip().upper() for s in args.symbols.split(",")]
    elif args.all_symbols:
        symbols_str = config.get("symbols", "all", fallback=DEFAULT_SYMBOLS)
        return [s.strip().upper() for s in symbols_str.split(",")]
    else:
        # Both args.favorites and default case use favorites
        symbols_str = config.get("symbols", "favorites", fallback=DEFAULT_SYMBOLS)
        return [s.strip().upper() for s in symbols_str.split(",")]


def fetch_historical_range(api, symbols: list, days: int, db, throttle_seconds: float, retries: int) -> int:
    """Fetch historical data for a specific number of days."""
    print(f"Fetching historical range: last {days} days")
    total_count = 0
    for idx, sym in enumerate(symbols, start=1):
        print(f"[{idx}/{len(symbols)}] {sym} → OHLCV daily between-dates")
        attempt = 0
        while True:
            try:
                sym_quotes = api.fetch_historical_range([sym], days=days)
                break
            except Exception as e:
                attempt += 1
                if attempt > retries:
                    print(f"  ❌ Failed {sym} after {retries} retries: {e}")
                    sym_quotes = []
                    break
                sleep_s = min(throttle_seconds * (2 ** (attempt - 1)), 10)
                print(f"  Retry {attempt}/{retries} after {sleep_s:.1f}s due to: {e}")
                time.sleep(sleep_s)

        # Always upsert to avoid duplicates when refetching ranges
        inserted = 0
        for q in sym_quotes:
            if db.insert_or_update_quote(sym, q):
                inserted += 1
        total_count += inserted
        print(f"  ✓ Stored/updated {inserted} quotes for {sym}")

        # Throttle between symbols
        time.sleep(throttle_seconds)

    print(f"Successfully stored/updated {total_count} quotes in database")
    return total_count


def fetch_quotes_incremental(api, symbols: list, db, fetch_mode: str) -> list:
    """Fetch quotes based on fetch mode (incremental or full)."""
    if fetch_mode == "full":
        print("Mode: Full (fetching from oldest available data)")
        return api.fetch_and_parse(symbols)
    else:
        # Incremental mode: fetch from last date in database
        print("Mode: Incremental (fetching from last recorded date)")
        last_dates = {}
        for symbol in symbols:
            last_date = db.get_latest_timestamp(symbol)
            if last_date:
                last_dates[symbol] = last_date
                print(f"  {symbol}: last date = {last_date}")
            else:
                print(f"  {symbol}: no data in database yet")
        return api.fetch_and_parse(symbols)


def store_quotes(db, quotes: list, upsert: bool, fetch_mode: str) -> int:
    """Store fetched quotes in database."""
    if upsert and fetch_mode == "full":
        count = 0
        for quote in quotes:
            if db.insert_or_update_quote(quote.get("symbol"), quote):
                count += 1
        print(f"Successfully stored/updated {count} quotes in database")
        return count
    else:
        count = db.insert_quotes_batch(quotes)
        print(f"Successfully stored {count} quotes in database")
        return count


def generate_report(db, symbols: list, report_path: str, db_path: str) -> int:
    """Generate statistical analysis and Excel report."""
    print("Generating statistical analysis...")
    reports = StatisticalAnalyzer.batch_generate_reports(
        symbols,
        lambda sym: db.get_quotes(sym)
    )
    
    # Check if any reports were generated successfully
    valid_reports = {k: v for k, v in reports.items() if "error" not in v}
    if not valid_reports:
        print("No valid data available for report generation")
        return 1
    
    # Generate volatility analysis
    print("Analyzing volatility patterns...")
    volatility_analyzer = VolatilityAnalyzer(db)
    volatility_results = volatility_analyzer.analyze_all_symbols(symbols, days=365)
    
    # Export volatility to CSV
    volatility_analyzer.export_to_csv(volatility_results, "reports/volatility_analysis.csv")
    
    # Add volatility stats per period to reports
    period_days_map = {
        "12_months": 365,
        "6_months": 180,
        "3_months": 90,
        "1_month": 30
    }
    
    for symbol in symbols:
        if symbol in reports and "error" not in reports[symbol]:
            # Add volatility for each period
            for period, days in period_days_map.items():
                if period in reports[symbol].get('periods', {}):
                    volatility_stats = volatility_analyzer.get_period_stats(symbol, days)
                    reports[symbol]['periods'][period]['volatility'] = volatility_stats
    
    # Get market caps for sorting
    market_caps = {}
    for symbol in symbols:
        crypto_info = db.get_crypto_info(symbol)
        if crypto_info and crypto_info.get('market_cap'):
            market_caps[symbol] = crypto_info.get('market_cap', 0) or 0
        else:
            market_caps[symbol] = 0
    
    # Get favorites list from database
    result = db.conn.execute('SELECT code FROM crypto_info WHERE favorite = 1').fetchall()
    favorites = [row[0] for row in result]
    
    # Generate Excel report
    print(f"Generating Excel report: {report_path}")
    reporter = ExcelReporter(report_path)
    reporter.generate_report(reports, market_caps, favorites)
    
    print("✓ Analysis complete!")
    print(f"  Symbols analyzed: {', '.join(symbols)}")
    print(f"  Database: {db_path}")
    print(f"  Report: {report_path}")
    print(f"  Volatility CSV: reports/volatility_analysis.csv")
    
    return 0


def main():
    """Main entry point for the cryptocurrency analysis tool."""
    parser = argparse.ArgumentParser(
        description="Cryptocurrency Price Tracker and Analysis Tool"
    )
    parser.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of cryptocurrency symbols (overrides config file)"
    )
    parser.add_argument(
        "--all-symbols",
        action="store_true",
        help="Use all symbols from config file (all section)"
    )
    parser.add_argument(
        "--favorites",
        action="store_true",
        help="Use favorite symbols from config file (favorites section)"
    )
    parser.add_argument(
        "--all-from-db",
        action="store_true",
        help="Use all symbols from crypto_info table in database"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        help="Path to SQLite database (default from config)"
    )
    parser.add_argument(
        "--report-path",
        type=str,
        help="Path to output Excel report (default from config)"
    )
    parser.add_argument(
        "--fetch-mode",
        type=str,
        choices=["incremental", "full"],
        help="Fetch mode: 'incremental' (from last date) or 'full' (from oldest date)"
    )
    parser.add_argument(
        "--days",
        type=int,
        help="Fetch historical quotes for the last N days (e.g. 365)"
    )
    parser.add_argument(
        "--fetch-only",
        action="store_true",
        help="Only fetch and store data, don't generate report"
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only generate report from existing data, don't fetch"
    )
    parser.add_argument(
        "--import-csv",
        type=str,
        help="Import historical data from CSV file (format: date,price)"
    )
    parser.add_argument(
        "--csv-date-col",
        type=str,
        default="0",
        help="Date column name or index in CSV (default: 0)"
    )
    parser.add_argument(
        "--csv-price-col",
        type=str,
        default="1",
        help="Price column name or index in CSV (default: 1)"
    )
    parser.add_argument(
        "--csv-date-format",
        type=str,
        help="Date format for CSV (e.g., %%Y-%%m-%%d). Auto-detect if not specified"
    )
    parser.add_argument(
        "--csv-no-header",
        action="store_true",
        help="CSV file has no header row"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Initialize database path
    db_path = args.db_path or config.get("database", "path", fallback="data/crypto_prices.db")
    
    # Determine symbols to use
    symbols = determine_symbols(args, config, db_path)
    if symbols is None:
        return 1
    
    # Get configuration parameters
    fetch_mode = args.fetch_mode or config.get("fetch", "mode", fallback="incremental")
    upsert = config.getboolean("fetch", "upsert_duplicates", fallback=True)
    throttle_seconds = config.getfloat("fetch", "throttle_seconds", fallback=1.0)
    retries = config.getint("fetch", "retries", fallback=2)
    report_path = args.report_path or config.get("report", "output_path", fallback="reports/AnaliseCrypto.xlsx")
    
    try:
        # Initialize database
        print("Initializing database...")
        db = CryptoDatabase(db_path)
        
        # Handle CSV import if requested
        if args.import_csv:
            print(f"Importing from CSV: {args.import_csv}")
            if not Path(args.import_csv).exists():
                print(f"Error: CSV file not found: {args.import_csv}")
                return 1
            
            if not symbols or len(symbols) != 1:
                print("Error: Specify exactly one symbol with --symbols when importing CSV")
                return 1
            
            symbol = symbols[0]
            count = import_csv_data(
                args.import_csv,
                symbol,
                db,
                args.csv_date_col,
                args.csv_price_col,
                args.csv_date_format,
                skip_header=not args.csv_no_header
            )
            
            if count == 0:
                print("No data imported from CSV")
                return 1
            
            print(f"✓ Imported {count} quotes from CSV")
            
            if args.fetch_only:
                db.close()
                return 0
        
        # Fetch data if not report-only mode
        if not args.report_only and not args.import_csv:
            print(f"Fetching prices for: {', '.join(symbols)}")
            print(f"Fetch mode: {fetch_mode}")
            try:
                api = YFinanceCryptoAPI()
                
                if args.days:
                    # Fetch specific historical range
                    fetch_historical_range(api, symbols, args.days, db, throttle_seconds, retries)
                else:
                    # Fetch incremental or full
                    quotes = fetch_quotes_incremental(api, symbols, db, fetch_mode)
                    
                    if quotes:
                        store_quotes(db, quotes, upsert, fetch_mode)
                    else:
                        print("No quotes retrieved from API")
                        return 1
            
            except Exception as e:
                print(f"Error fetching from Yahoo Finance: {e}")
                return 1
        
        if args.fetch_only:
            print("Fetch-only mode: skipping report generation")
            db.close()
            return 0
        
        # Generate report
        result = generate_report(db, symbols, report_path, db_path)
        db.close()
        return result
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
