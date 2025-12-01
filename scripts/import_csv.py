"""
Utility to import historical price data from CSV files.
Supports importing date and price data for cryptocurrencies.
"""

import csv
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import CryptoDatabase


def parse_csv_file(csv_path: str, symbol: str, date_column: str, price_column: str, 
                   date_format: str = None, skip_header: bool = True) -> List[Dict]:
    """
    Parse CSV file and extract date and price data.
    
    Args:
        csv_path: Path to CSV file
        symbol: Cryptocurrency symbol (e.g., 'BTC')
        date_column: Name or index (0-based) of date column
        price_column: Name or index (0-based) of price column
        date_format: strptime format string (auto-detect if None)
        skip_header: Whether to skip first row
    
    Returns:
        List of quote dictionaries
    """
    quotes = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Read header if present
        if skip_header:
            header = next(reader)
            # Try to find column indices from names
            try:
                date_idx = header.index(date_column)
                price_idx = header.index(price_column)
            except ValueError:
                # Treat as numeric indices
                date_idx = int(date_column)
                price_idx = int(price_column)
        else:
            date_idx = int(date_column)
            price_idx = int(price_column)
        
        # Read data rows
        for row_num, row in enumerate(reader, start=2 if skip_header else 1):
            try:
                date_str = row[date_idx].strip()
                price_str = row[price_idx].strip()
                
                # Parse date
                if date_format:
                    date_obj = datetime.strptime(date_str, date_format)
                else:
                    # Try common formats
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', 
                                '%d-%m-%Y', '%m-%d-%Y', '%Y%m%d']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        # Try ISO format
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                
                # Parse price
                price_val = float(price_str.replace(',', '').replace('€', '').replace('$', '').strip())
                
                quotes.append({
                    'symbol': symbol,
                    'name': symbol,
                    'price_eur': price_val,
                    'timestamp': date_obj
                })
                
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping row {row_num}: {e}")
                continue
    
    return quotes


def import_csv_to_db(csv_path: str, symbol: str, db_path: str, 
                     date_column: str = '0', price_column: str = '1',
                     date_format: str = None, skip_header: bool = True,
                     upsert: bool = True) -> int:
    """
    Import CSV data into database.
    
    Args:
        csv_path: Path to CSV file
        symbol: Cryptocurrency symbol
        db_path: Path to database
        date_column: Date column name or index
        price_column: Price column name or index
        date_format: Date format string
        skip_header: Skip first row
        upsert: Use upsert (update if exists) instead of insert
    
    Returns:
        Number of quotes imported
    """
    print(f"Reading CSV: {csv_path}")
    print(f"Symbol: {symbol}")
    print(f"Date column: {date_column}, Price column: {price_column}")
    
    quotes = parse_csv_file(csv_path, symbol, date_column, price_column, 
                           date_format, skip_header)
    
    if not quotes:
        print("No valid quotes found in CSV")
        return 0
    
    print(f"Parsed {len(quotes)} quotes from CSV")
    print(f"Date range: {quotes[0]['timestamp']} to {quotes[-1]['timestamp']}")
    
    # Import to database
    db = CryptoDatabase(db_path)
    
    count = 0
    for quote in quotes:
        if upsert:
            if db.insert_or_update_quote(quote['symbol'], quote):
                count += 1
        else:
            if db.insert_quote(quote['symbol'], quote):
                count += 1
    
    db.close()
    
    print(f"Successfully imported {count} quotes to database")
    return count


def main():
    parser = argparse.ArgumentParser(
        description='Import cryptocurrency price data from CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import with header row (column names)
  python scripts/import_csv.py --csv data.csv --symbol BTC --date-col Date --price-col Price
  
  # Import without header (column indices)
  python scripts/import_csv.py --csv data.csv --symbol BTC --date-col 0 --price-col 1 --no-header
  
  # Specify date format
  python scripts/import_csv.py --csv data.csv --symbol ETH --date-col 0 --price-col 1 --date-format "%d/%m/%Y"
  
CSV format expected:
  Date,Price
  2024-01-01,42000.50
  2024-01-02,42500.75
        """
    )
    
    parser.add_argument('--csv', required=True, help='Path to CSV file')
    parser.add_argument('--symbol', required=True, help='Cryptocurrency symbol (e.g., BTC)')
    parser.add_argument('--db-path', default='data/crypto_prices.db', 
                       help='Database path (default: data/crypto_prices.db)')
    parser.add_argument('--date-col', default='0', 
                       help='Date column name or index (default: 0)')
    parser.add_argument('--price-col', default='1', 
                       help='Price column name or index (default: 1)')
    parser.add_argument('--date-format', 
                       help='Date format (e.g., %%Y-%%m-%%d). Auto-detect if not specified')
    parser.add_argument('--no-header', action='store_true', 
                       help='CSV has no header row')
    parser.add_argument('--no-upsert', action='store_true',
                       help='Insert only (fail on duplicates) instead of upsert')
    
    args = parser.parse_args()
    
    # Validate CSV exists
    if not Path(args.csv).exists():
        print(f"Error: CSV file not found: {args.csv}")
        return 1
    
    try:
        import_csv_to_db(
            args.csv,
            args.symbol.upper(),
            args.db_path,
            args.date_col,
            args.price_col,
            args.date_format,
            skip_header=not args.no_header,
            upsert=not args.no_upsert
        )
        return 0
    except Exception as e:
        print(f"Error importing CSV: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
