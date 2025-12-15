"""
Seed crypto_info table with large, established cryptocurrencies using yfinance.
Criteria: Market cap > $100M USD and launch date > 3 months ago.
Uses CoinGecko API (free) to get comprehensive list of all cryptos.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import requests
import time
import configparser

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import CryptoDatabase
import yfinance as yf


def get_all_cryptos_from_coingecko(min_market_cap_usd: float = 100_000_000):
    """
    Get all cryptocurrencies from CoinGecko with market cap > threshold.
    Returns list of (symbol, name, market_cap_usd) tuples.
    """
    print("Fetching cryptocurrency list from CoinGecko...")
    
    all_cryptos = []
    page = 1
    per_page = 250  # Max allowed by CoinGecko
    
    while True:
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': per_page,
                'page': page,
                'sparkline': False
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            # Filter by market cap
            for coin in data:
                market_cap = coin.get('market_cap')
                if market_cap and market_cap >= min_market_cap_usd:
                    all_cryptos.append({
                        'symbol': coin['symbol'].upper(),
                        'name': coin['name'],
                        'market_cap': market_cap
                    })
            
            # If we got results below threshold, we can stop
            if data[-1].get('market_cap', 0) < min_market_cap_usd:
                break
            
            print(f"  Fetched page {page}: {len(data)} coins, {len(all_cryptos)} match criteria so far")
            page += 1
            time.sleep(1.1)  # Rate limit: max 50 calls/minute
            
        except Exception as e:
            print(f"  Error fetching page {page}: {e}")
            break
    
    print(f"\n✓ Found {len(all_cryptos)} cryptocurrencies with market cap > ${min_market_cap_usd:,.0f}")
    return all_cryptos


def get_large_established_cryptos():
    """
    Get list of cryptocurrencies with market cap > $100M and > 3 months old.
    Returns list of dicts with symbol, name, market_cap, market_entry.
    """
    # Get all cryptos from CoinGecko with market cap > $100M
    min_market_cap = 100_000_000
    candidates = get_all_cryptos_from_coingecko(min_market_cap)
    
    if not candidates:
        print("No cryptocurrencies found from CoinGecko!")
        return []
    
    results = []
    min_age_days = 90  # 3 months
    cutoff_date = (datetime.now() - timedelta(days=min_age_days)).replace(tzinfo=None)
    
    print(f"\nValidating {len(candidates)} cryptocurrencies with yfinance...")
    print(f"Criteria: Age > {min_age_days} days (launched before {cutoff_date.date()})")
    print()
    
    for idx, crypto in enumerate(candidates, 1):
        symbol = crypto['symbol']
        name = crypto['name']
        market_cap = crypto['market_cap']
        
        try:
            # First check EUR ticker availability
            ticker_eur = f"{symbol}-EUR"
            yf_crypto_eur = yf.Ticker(ticker_eur)
            
            # Try to get EUR history
            hist_eur = yf_crypto_eur.history(period='5d', interval='1d')
            if hist_eur.empty:
                print(f"[{idx}/{len(candidates)}] ⊘ {symbol}: No EUR price data available")
                continue
            
            # Now check USD ticker for launch date
            ticker_usd = f"{symbol}-USD"
            yf_crypto_usd = yf.Ticker(ticker_usd)
            
            # Try to get first trade date (launch date approximation)
            hist = yf_crypto_usd.history(period='max', interval='1d')
            if not hist.empty:
                first_datetime = hist.index[0].to_pydatetime().replace(tzinfo=None)
                first_date = first_datetime.date()
                
                if first_datetime > cutoff_date:
                    print(f"[{idx}/{len(candidates)}] ✗ {symbol}: Too new (launched {first_date})")
                    continue
            else:
                # No history available, skip
                print(f"[{idx}/{len(candidates)}] ⊘ {symbol}: No historical data available")
                continue
            
            results.append({
                'code': symbol,
                'name': name,
                'market_cap': market_cap,
                'market_entry': first_date,
                'favorite': False
            })
            
            print(f"[{idx}/{len(candidates)}] ✓ {symbol} ({name}): ${market_cap:,.0f} USD, launched {first_date}")
            
            # Rate limiting
            if idx % 10 == 0:
                time.sleep(1)
            
        except Exception as e:
            print(f"[{idx}/{len(candidates)}] ⚠ {symbol}: Error - {e}")
            continue
    
    return results


def seed_crypto_info(db_path: str = 'data/crypto_prices.db'):
    """
    Populate crypto_info table with large, established cryptocurrencies.
    """
    print("=" * 70)
    print("Seeding crypto_info with large, established cryptocurrencies")
    print("=" * 70)
    print()
    
    # Load favorites from config.ini
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent.parent / 'config' / 'config.ini'
    favorites_set = set()
    if config_path.exists():
        config.read(config_path)
        favorites_str = config.get('symbols', 'favorites', fallback='')
        favorites_set = {s.strip().upper() for s in favorites_str.split(',') if s.strip()}
        print(f"Loaded {len(favorites_set)} favorites from config.ini: {', '.join(sorted(favorites_set))}")
        print()
    
    cryptos = get_large_established_cryptos()
    
    if not cryptos:
        print("\nNo cryptocurrencies matched the criteria!")
        return 0
    
    print()
    print("=" * 70)
    print(f"Found {len(cryptos)} cryptocurrencies matching criteria")
    print("=" * 70)
    print()
    
    # Insert into database
    db = CryptoDatabase(db_path)
    count = 0
    
    for crypto in cryptos:
        # Check if this crypto is in favorites
        is_favorite = crypto['code'] in favorites_set
        
        crypto_id = db.add_crypto_info(
            code=crypto['code'],
            name=crypto['name'],
            market_entry=crypto['market_entry'],
            market_cap=crypto['market_cap'],
            favorite=is_favorite
        )
        
        if crypto_id:
            count += 1
            favorite_mark = " ⭐" if is_favorite else ""
            print(f"Added {crypto['code']} ({crypto['name']}) id={crypto_id} market_cap=${crypto['market_cap']:,.2f}{favorite_mark}")
    
    db.close()
    
    print()
    print("=" * 70)
    print(f"✓ Finished. Total added: {count}")
    print("=" * 70)
    
    return count


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Seed crypto_info with large, established cryptocurrencies'
    )
    parser.add_argument(
        '--db-path',
        default='data/crypto_prices.db',
        help='Path to database file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be added without modifying database'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No database changes will be made")
        print()
        cryptos = get_large_established_cryptos()
        print()
        print(f"Would add {len(cryptos)} cryptocurrencies to database")
    else:
        seed_crypto_info(args.db_path)
