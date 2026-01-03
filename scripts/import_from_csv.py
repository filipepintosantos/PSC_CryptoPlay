#!/usr/bin/env python3
"""
Utility script to import cryptocurrency data from CSV files.

Usage:
    python scripts/import_from_csv.py <csv_file> <symbol> [options]

Examples:
    # Basic usage with default settings (columns 0 and 1)
    python scripts/import_from_csv.py data/BTC_prices.csv BTC
    
    # Using column names
    python scripts/import_from_csv.py data/prices.csv BTC --date-col Date --price-col Price
    
    # With custom date format
    python scripts/import_from_csv.py data/prices.csv BTC --date-format "%d-%m-%Y"
    
    # No header row
    python scripts/import_from_csv.py data/prices.csv BTC --no-header
    
    # Different delimiter
    python scripts/import_from_csv.py data/prices.csv BTC --delimiter ";"
"""

import argparse
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from csv_reader import CSVReader, CSVConfig, import_crypto_data
from database import CryptoDatabase


def main():
    """Main entry point for CSV import."""
    parser = argparse.ArgumentParser(
        description='Import cryptocurrency price data from CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('csv_file', help='Path to CSV file')
    parser.add_argument('symbol', help='Cryptocurrency symbol (e.g., BTC, ETH)')
    
    parser.add_argument(
        '--date-col',
        default='0',
        help='Date column name or index (default: 0)'
    )
    parser.add_argument(
        '--price-col',
        default='1',
        help='Price column name or index (default: 1)'
    )
    parser.add_argument(
        '--date-format',
        help='Date format string (e.g., "%%d-%%m-%%Y"). If not specified, auto-detects common formats'
    )
    parser.add_argument(
        '--no-header',
        action='store_true',
        help='CSV file has no header row'
    )
    parser.add_argument(
        '--skip-rows',
        type=int,
        default=0,
        help='Number of rows to skip at the beginning'
    )
    parser.add_argument(
        '--delimiter',
        default=',',
        help='Field delimiter (default: comma)'
    )
    parser.add_argument(
        '--encoding',
        default='utf-8',
        help='File encoding (default: utf-8)'
    )
    parser.add_argument(
        '--db',
        help='Database file path (default: data/crypto_prices.db)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Read and validate CSV without importing to database'
    )
    
    args = parser.parse_args()
    
    # Validate CSV file exists
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)
    
    # Determine if date/price columns are numeric or string
    try:
        date_col = int(args.date_col)
    except ValueError:
        date_col = args.date_col
    
    try:
        price_col = int(args.price_col)
    except ValueError:
        price_col = args.price_col
    
    # Create CSV configuration
    config = CSVConfig(
        date_column=date_col,
        price_column=price_col,
        has_header=not args.no_header,
        date_format=args.date_format,
        skip_rows=args.skip_rows,
        delimiter=args.delimiter,
        encoding=args.encoding
    )
    
    print(f"📖 Reading CSV file: {csv_path}")
    print(f"   Symbol: {args.symbol}")
    print(f"   Date column: {args.date_col} | Price column: {args.price_col}")
    
    try:
        # Read and parse CSV
        reader = CSVReader(config)
        rows = reader.read_file(csv_path)
        
        print(f"✓ Successfully read {len(rows)} data rows")
        
        if args.dry_run:
            print("\n📊 Sample data (first 5 rows):")
            for i, row in enumerate(rows[:5], 1):
                print(f"  {i}. {row['date'].date()} → €{row['price']:.2f}")
            if len(rows) > 5:
                print(f"  ... and {len(rows) - 5} more rows")
            print("\n(Use --dry-run=false or remove --dry-run to import to database)")
            return
        
        # Import to database
        db_path = args.db or "data/crypto_prices.db"
        db = CryptoDatabase(db_path)
        
        print(f"\n💾 Importing to database: {db_path}")
        count = 0
        for row in rows:
            quote = {
                'symbol': args.symbol,
                'name': args.symbol,
                'close_eur': row['price'],
                'price_eur': row['price'],
                'timestamp': row['date']
            }
            if db.insert_or_update_quote(args.symbol, quote):
                count += 1
        
        db.close()
        
        print(f"✓ Successfully imported {count} quotes")
        print(f"  Symbol: {args.symbol}")
        print(f"  Date range: {rows[0]['date'].date()} to {rows[-1]['date'].date()}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
