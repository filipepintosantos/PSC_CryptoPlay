"""
Main script for cryptocurrency price tracking and analysis.
Orchestrates fetching, storing, analyzing, and reporting.
"""

import argparse
import sys
import configparser
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from api import CoinMarketCapAPI
from database import CryptoDatabase
from analysis import StatisticalAnalyzer
from excel_reporter import ExcelReporter


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
        "--api-key",
        type=str,
        help="CoinMarketCap API key (or set CMC_API_KEY env variable)"
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
    
    args = parser.parse_args()
    
    # Load configuration
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent / "config" / "config.ini"
    if config_path.exists():
        config.read(config_path)
    
    # Determine symbols to use
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",")]
    elif args.all_symbols:
        symbols_str = config.get("symbols", "all", fallback="BTC,ETH,ADA,XRP,SOL")
        symbols = [s.strip().upper() for s in symbols_str.split(",")]
    elif args.favorites:
        symbols_str = config.get("symbols", "favorites", fallback="BTC,ETH,ADA,XRP,SOL")
        symbols = [s.strip().upper() for s in symbols_str.split(",")]
    else:
        symbols_str = config.get("symbols", "favorites", fallback="BTC,ETH,ADA,XRP,SOL")
        symbols = [s.strip().upper() for s in symbols_str.split(",")]
    
    # Get fetch mode from args or config
    fetch_mode = args.fetch_mode or config.get("fetch", "mode", fallback="incremental")
    upsert = config.getboolean("fetch", "upsert_duplicates", fallback=True)
    
    # Get database path
    db_path = args.db_path or config.get("database", "path", fallback="data/crypto_prices.db")
    
    # Get report path
    report_path = args.report_path or config.get("report", "output_path", fallback="reports/crypto_analysis.xlsx")
    
    try:
        # Initialize database
        print("Initializing database...")
        db = CryptoDatabase(db_path)
        
        if not args.report_only:
            # Fetch and store data
            print(f"Fetching prices for: {', '.join(symbols)}")
            print(f"Fetch mode: {fetch_mode}")
            try:
                api = CoinMarketCapAPI(args.api_key)
                
                # Determine fetch starting point based on mode
                # If user requested an explicit days range, use the historical range fetch
                if args.days:
                    print(f"Fetching historical range: last {args.days} days")
                    quotes = api.fetch_historical_range(symbols, days=args.days)
                elif fetch_mode == "full":
                    # Will fetch from oldest date, don't use database info
                    print("Mode: Full (fetching from oldest available data)")
                    quotes = api.fetch_and_parse(symbols, close_of_day=True)
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
                    quotes = api.fetch_and_parse(symbols, close_of_day=True)
                
                if quotes:
                    # Insert or update quotes
                    if upsert and fetch_mode == "full":
                        count = 0
                        for quote in quotes:
                            if db.insert_or_update_quote(quote.get("symbol"), quote):
                                count += 1
                        print(f"Successfully stored/updated {count} quotes in database")
                    else:
                        count = db.insert_quotes_batch(quotes)
                        print(f"Successfully stored {count} quotes in database")
                else:
                    print("No quotes retrieved from API")
                    return 1
            
            except Exception as e:
                print(f"Error fetching from CoinMarketCap: {e}")
                print("Make sure you have a valid CMC_API_KEY set in your .env file or passed via --api-key")
                return 1
        
        if args.fetch_only:
            print("Fetch-only mode: skipping report generation")
            db.close()
            return 0
        
        # Generate analysis report
        print("Generating statistical analysis...")
        reports = StatisticalAnalyzer.batch_generate_reports(
            symbols,
            lambda sym: db.get_quotes(sym)
        )
        
        # Check if any reports were generated successfully
        valid_reports = {k: v for k, v in reports.items() if "error" not in v}
        if not valid_reports:
            print("No valid data available for report generation")
            db.close()
            return 1
        
        # Generate Excel report
        print(f"Generating Excel report: {report_path}")
        reporter = ExcelReporter(report_path)
        reporter.generate_report(reports)
        
        print("✓ Analysis complete!")
        print(f"  Symbols analyzed: {', '.join(symbols)}")
        print(f"  Database: {db_path}")
        print(f"  Report: {report_path}")
        
        db.close()
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
