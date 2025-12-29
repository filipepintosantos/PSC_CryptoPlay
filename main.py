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
from datetime import datetime, timedelta


from typing import Optional

import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def print_flush(*args, **kwargs):
    print(*args, flush=True, **kwargs)

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from api_yfinance import YFinanceCryptoAPI
from database import CryptoDatabase
from analysis import StatisticalAnalyzer
from excel_reporter import ExcelReporter
from volatility_analysis import VolatilityAnalyzer
from favorites_helper import validate_and_update_favorites, get_all_favorites_list

# Constants
DEFAULT_SYMBOLS = "BTC,ETH,ADA,XRP,SOL"


def _get_column_indices(header, date_column: str, price_column: str, skip_header: bool):
    """Get column indices from header or parse as integers."""
    if skip_header:
        try:
            date_idx = header.index(date_column)
            price_idx = header.index(price_column)
        except ValueError:
            date_idx = int(date_column)
            price_idx = int(price_column)
    else:
        date_idx = int(date_column)
        price_idx = int(price_column)
    return date_idx, price_idx


def _parse_csv_date(date_str: str, date_format: str = None):
    """Parse date string with optional format or auto-detection."""
    if date_format:
        return datetime.strptime(date_str, date_format)
    
    # Try common formats
    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))


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
        
        header = next(reader) if skip_header else None
        date_idx, price_idx = _get_column_indices(header, date_column, price_column, skip_header)
        
        count = 0
        for row_num, row in enumerate(reader, start=2 if skip_header else 1):
            try:
                date_str = row[date_idx].strip()
                price_str = row[price_idx].strip()
                
                date_obj = _parse_csv_date(date_str, date_format)
                price_val = float(price_str.replace(',', '').replace('€', '').replace('$', '').strip())
                
                quote = {
                    'symbol': symbol,
                    'name': symbol,
                    'close_eur': price_val,
                    'price_eur': price_val,  # Backward compatibility
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


def fetch_historical_range(api, symbols: list, days: int, db, throttle_seconds: float, 
                          retries: int, auto_range: bool = False) -> int:
    """
    Fetch historical data for a specific number of days or automatically from last quote.
    
    Args:
        api: API instance
        symbols: List of symbols to fetch
        days: Number of days (ignored if auto_range is True)
        db: Database instance
        throttle_seconds: Delay between symbols
        retries: Number of retries on error
        auto_range: If True, fetch from last quote date to today for each symbol
    
    Returns:
        Total number of quotes stored
    """
    if auto_range:
        print("Fetching historical range: auto-range mode (from last quote to today)")
    else:
        print(f"Fetching historical range: last {days} days")
    
    total_count = 0
    for idx, sym in enumerate(symbols, start=1):
        start_date = None
        
        if auto_range:
            # Get last quote date for this symbol from crypto_info
            last_date = db.get_last_quote_date_for_symbol(sym)
            today = datetime.now().date()
            if last_date:
                last_date_only = last_date.date()
                if last_date_only < today:
                    # Se última data < hoje, buscar de (last_date+1) até hoje
                        start_date = last_date + timedelta(days=1)
                        print(f"[{idx}/{len(symbols)}] {sym} → OHLCV from {start_date.date()} to {today}")
                else:
                        # Se última data == hoje, buscar ontem como start_date e atualizar ontem e hoje
                        start_date = today - timedelta(days=1)
                        # marcamos que depois devemos incluir também o quote de hoje para forçar atualização
                        include_today = True
                        print(f"[{idx}/{len(symbols)}] {sym} → OHLCV update for yesterday and today ({start_date} to {today})")
            else:
                # No previous data, fetch last 365 days
                start_date = None
                days_to_fetch = 365
                print(f"[{idx}/{len(symbols)}] {sym} → No previous data, fetching last {days_to_fetch} days")
        else:
            print(f"[{idx}/{len(symbols)}] {sym} → OHLCV daily between-dates")
            days_to_fetch = days
        
        attempt = 0
        while True:
            try:
                if auto_range and start_date:
                    sym_quotes = api.fetch_historical_range([sym], start_date=start_date)
                else:
                    sym_quotes = api.fetch_historical_range([sym], days=days_to_fetch if not auto_range else 365)
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
        # If needed, include today's live quote to force update when last_quote_date was today
        if auto_range and 'include_today' in locals() and include_today:
            try:
                today_quote = api.get_latest_quote(sym)
                if today_quote:
                    # Normalize timestamp to date for consistency with historical results
                    ts = today_quote.get('timestamp')
                    if hasattr(ts, 'date'):
                        today_quote['timestamp'] = ts.date()
                    sym_quotes.append(today_quote)
            except Exception:
                pass
        for q in sym_quotes:
            # Garante que todos os campos obrigatórios estão presentes
            q['close_eur'] = q.get('close_eur', 0.0) or 0.0
            q['low_eur'] = q.get('low_eur', 0.0) or 0.0
            q['high_eur'] = q.get('high_eur', 0.0) or 0.0
            q['daily_returns'] = q.get('daily_returns', 0.0) if q.get('daily_returns') is not None else 0.0
            q['timestamp'] = q.get('timestamp')
            if db.insert_or_update_quote(sym, q):
                inserted += 1

        # Garante atualização do last_quote_date mesmo se não houver novas cotações
        db.update_last_quote_date(sym)
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


def _add_volatility_to_reports(reports: dict, symbols: list, volatility_analyzer):
    """Add volatility statistics per period to reports."""
    period_days_map = {
        "12_months": 365,
        "6_months": 180,
        "3_months": 90,
        "1_month": 30
    }
    
    for symbol in symbols:
        if symbol in reports and "error" not in reports[symbol]:
            for period, days in period_days_map.items():
                if period in reports[symbol].get('periods', {}):
                    volatility_stats = volatility_analyzer.get_period_stats(symbol, days)
                    reports[symbol]['periods'][period]['volatility'] = volatility_stats


def generate_report(db, symbols: list, report_path: str, db_path: str, config: configparser.ConfigParser) -> int:
    """Generate statistical analysis and Excel report."""
    # Update favorites from config.ini before generating report
    print("Updating favorites from config...")
    validate_and_update_favorites(db, config)
    print()
    
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
    
    # Add volatility stats per period to reports
    _add_volatility_to_reports(reports, symbols, volatility_analyzer)
    
    # Get market caps for sorting
    market_caps = {}
    for symbol in symbols:
        crypto_info = db.get_crypto_info(symbol)
        if crypto_info and crypto_info.get('market_cap'):
            market_caps[symbol] = crypto_info.get('market_cap', 0) or 0
        else:
            market_caps[symbol] = 0
    
    # Get favorites organized by class from database
    favorites = {}
    for cls in ['A', 'B', 'C']:
        result = db.conn.execute('SELECT code FROM crypto_info WHERE favorite = ?', (cls,)).fetchall()
        favorites[cls] = [row[0] for row in result]
    
    # Generate Excel report with volatility detail sheet
    print(f"Generating Excel report: {report_path}")
    reporter = ExcelReporter(report_path)
    reporter.generate_report(reports, market_caps, favorites)
    
    print("✓ Analysis complete!")
    print(f"  Symbols analyzed: {', '.join(symbols)}")
    print(f"  Database: {db_path}")
    print(f"  Report: {report_path}")
    print("  Volatility details: See 'Volatility Detail' sheet in Excel")
    
    return 0


def _setup_argument_parser():
    """Setup and return the argument parser."""
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
        "--auto-range",
        action="store_true",
        help="Automatically fetch from last quote date to today (default for update_quotes.cmd)"
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
    
    return parser


def _handle_csv_import(args, db, symbols) -> int:
    """Handle CSV import if requested."""
    print(f"Importing from CSV: {args.import_csv}")
    
    if not Path(args.import_csv).exists():
        print(f"Error: CSV file not found: {args.import_csv}")
        return 1
    
    if not symbols or len(symbols) != 1:
        print("Error: Specify exactly one symbol with --symbols when importing CSV")
        return 1
    
    symbol = symbols[0]
    count = import_csv_data(
        args.import_csv, symbol, db,
        args.csv_date_col, args.csv_price_col,
        args.csv_date_format,
        skip_header=not args.csv_no_header
    )
    
    if count == 0:
        print("No data imported from CSV")
        return 1
    
    print(f"✓ Imported {count} quotes from CSV")
    return 0


def _fetch_price_data(args, symbols, db, fetch_mode, throttle_seconds, retries, upsert) -> int:
    """Fetch price data from Yahoo Finance."""
    print(f"Fetching prices for: {', '.join(symbols)}")
    print(f"Fetch mode: {fetch_mode}")
    
    try:
        api = YFinanceCryptoAPI()
        
        if args.days or args.auto_range:
            # Use historical range fetch
            auto_range = args.auto_range or (not args.days)  # Default to auto-range if neither specified
            days = args.days if args.days else 365  # Fallback days value
            fetch_historical_range(api, symbols, days, db, throttle_seconds, retries, auto_range)
        else:
            quotes = fetch_quotes_incremental(api, symbols, db, fetch_mode)
            if quotes:
                store_quotes(db, quotes, upsert, fetch_mode)
            else:
                print("No quotes retrieved from API")
                return 1
        return 0
    except Exception as e:
        print(f"Error fetching from Yahoo Finance: {e}")
        return 1


def main():
    """Main entry point for the cryptocurrency analysis tool."""
    parser = _setup_argument_parser()
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
        
        # Validate and update favorite classifications
        print("Validating favorite classifications...")
        updated = validate_and_update_favorites(db, config)
        if updated > 0:
            print(f"  ✓ Updated {updated} favorite classifications")
        
        # Handle CSV import if requested
        if args.import_csv:
            result = _handle_csv_import(args, db, symbols)
            if result != 0 or args.fetch_only:
                db.close()
                return result
        
        # Fetch data if not report-only mode
        if not args.report_only and not args.import_csv:
            result = _fetch_price_data(args, symbols, db, fetch_mode, throttle_seconds, retries, upsert)
            if result != 0:
                db.close()
                return result
        
        if args.fetch_only:
            print("Fetch-only mode: skipping report generation")
            db.close()
            return 0
        
        # Generate report
        result = generate_report(db, symbols, report_path, db_path, config)
        db.close()
        return result
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
