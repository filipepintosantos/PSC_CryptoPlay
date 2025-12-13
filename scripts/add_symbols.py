"""
Helper script to add new cryptocurrency symbols to tracking with favorite classification.
Usage:
    python scripts/add_symbols.py BTC ETH --class A
    python scripts/add_symbols.py XRP BNB --class B
    python scripts/add_symbols.py --from-config
"""
import argparse
import configparser
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import CryptoDatabase
from favorites_helper import get_favorite_class


def add_symbol_with_classification(db: CryptoDatabase, symbol: str, favorite_class: str = None):
    """
    Add a symbol to crypto_info table with favorite classification.
    
    Args:
        db: Database instance
        symbol: Cryptocurrency symbol
        favorite_class: 'A', 'B', 'C', or None
    """
    symbol = symbol.upper()
    
    # Check if already exists
    existing = db.get_crypto_info(symbol)
    if existing:
        print(f"  ℹ {symbol} already exists")
        if favorite_class and existing.get('favorite') != favorite_class:
            db.set_favorite_class(symbol, favorite_class)
            print(f"    Updated favorite class: {existing.get('favorite')} → {favorite_class}")
    else:
        # Add new entry
        db.add_crypto_info(symbol, symbol, favorite=favorite_class)
        print(f"  ✓ Added {symbol}" + (f" (Class {favorite_class})" if favorite_class else ""))


def add_symbols_from_config(db: CryptoDatabase, config: configparser.ConfigParser):
    """Add all symbols from config file with their respective classifications."""
    added = {'A': 0, 'B': 0, 'C': 0, 'None': 0}
    
    # Get all symbols from config
    all_symbols_str = config.get('symbols', 'all', fallback='')
    all_symbols = [s.strip().upper() for s in all_symbols_str.split(',') if s.strip()]
    
    print(f"Adding {len(all_symbols)} symbols from config...")
    print()
    
    for symbol in all_symbols:
        favorite_class = get_favorite_class(symbol, config)
        add_symbol_with_classification(db, symbol, favorite_class)
        
        if favorite_class:
            added[favorite_class] += 1
        else:
            added['None'] += 1
    
    print()
    print("Summary:")
    print(f"  Class A (Top priority): {added['A']}")
    print(f"  Class B (Secondary): {added['B']}")
    print(f"  Class C (Tertiary): {added['C']}")
    print(f"  No classification: {added['None']}")
    print(f"  Total: {sum(added.values())}")


def main():
    parser = argparse.ArgumentParser(description='Add cryptocurrency symbols with favorite classification')
    parser.add_argument('symbols', nargs='*', help='Cryptocurrency symbols to add')
    parser.add_argument('--class', dest='favorite_class', choices=['A', 'B', 'C'], 
                       help='Favorite class (A, B, or C)')
    parser.add_argument('--from-config', action='store_true',
                       help='Add all symbols from config.ini with their classifications')
    
    args = parser.parse_args()
    
    # Load config
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    
    # Initialize database
    db = CryptoDatabase()
    
    if args.from_config:
        add_symbols_from_config(db, config)
    elif args.symbols:
        print(f"Adding {len(args.symbols)} symbol(s)...")
        print()
        for symbol in args.symbols:
            add_symbol_with_classification(db, symbol, args.favorite_class)
        print()
        print(f"✓ Done")
    else:
        parser.print_help()
        return 1
    
    db.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
