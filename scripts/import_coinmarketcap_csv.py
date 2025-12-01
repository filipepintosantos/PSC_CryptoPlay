"""
Import Bitcoin historical data from CoinMarketCap CSV export.
Uses timeOpen as date and close as price in EUR.
"""

import csv
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import CryptoDatabase


def import_coinmarketcap_csv(csv_path: str, symbol: str = 'BTC', db_path: str = 'data/crypto_prices.db'):
    """
    Import historical data from CoinMarketCap CSV export.
    
    Expected CSV format (semicolon-delimited):
    timeOpen;timeClose;timeHigh;timeLow;name;open;high;low;close;volume;marketCap;...
    """
    print(f"Importing {symbol} data from: {csv_path}")
    
    db = CryptoDatabase(db_path)
    count = 0
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            try:
                # Extract timeOpen and close price
                time_open_str = row['timeOpen'].strip('"')
                close_price = float(row['close'])
                
                # Parse ISO datetime
                date_obj = datetime.fromisoformat(time_open_str.replace('Z', '+00:00'))
                
                quote = {
                    'symbol': symbol,
                    'name': symbol,
                    'price_eur': close_price,
                    'timestamp': date_obj
                }
                
                if db.insert_or_update_quote(symbol, quote):
                    count += 1
                    
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
    
    db.close()
    
    print(f"✓ Successfully imported {count} quotes for {symbol}")
    return count


if __name__ == '__main__':
    import glob
    
    # Map CSV files to symbols
    csv_mapping = {
        'Bitcoin_*.csv': 'BTC',
        'Ethereum_*.csv': 'ETH',
        'Cardano_*.csv': 'ADA',
        'Solana_*.csv': 'SOL',
        'Chainlink_*.csv': 'LINK',
        'Cosmos_*.csv': 'ATOM',
        'Tezos_*.csv': 'XTZ'
    }
    
    total_imported = 0
    
    print("=" * 60)
    print("Importing CoinMarketCap Historical Data")
    print("=" * 60)
    print()
    
    for pattern, symbol in csv_mapping.items():
        files = glob.glob(f'data/{pattern}')
        
        if not files:
            print(f"⚠ {symbol}: No CSV found (pattern: {pattern})")
            continue
        
        csv_file = files[0]  # Use first match
        try:
            count = import_coinmarketcap_csv(csv_file, symbol)
            total_imported += count
            print()
        except Exception as e:
            print(f"✗ {symbol}: Error - {e}")
            print()
    
    print("=" * 60)
    print(f"✓ Total imported: {total_imported} quotes")
    print("=" * 60)
