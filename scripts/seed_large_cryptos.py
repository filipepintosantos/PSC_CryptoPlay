"""
Seed `crypto_info` with cryptocurrencies that have market cap > 1_000_000_000 USD
and that were added to the market more than 3 months ago.

This script uses the CoinMarketCap "listings/latest" endpoint and requires an
API key available either via the environment variable
`COINMARKETCAP_API_KEY` or in `config/config.ini` under section
`[coinmarketcap]` key `api_key`.

Usage (Windows cmd.exe):

    set COINMARKETCAP_API_KEY=your_key_here
    python scripts\seed_large_cryptos.py --db-path data\crypto_prices.db

Options:
  --dry-run    : print matches without inserting
  --limit      : results per page (default 100)
  --max-pages  : max pages to fetch (default 50)

Note: this script requires network access and a valid CoinMarketCap API key.
"""
from __future__ import annotations

import os
import time
import argparse
import configparser
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests

from src.database import CryptoDatabase


def get_api_key() -> Optional[str]:
    key = os.getenv("COINMARKETCAP_API_KEY")
    if key:
        return key
    cfg = configparser.ConfigParser()
    cfg.read("config/config.ini")
    if cfg.has_section("coinmarketcap") and cfg.has_option("coinmarketcap", "api_key"):
        return cfg.get("coinmarketcap", "api_key")
    return None


def parse_date_added(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    s = s.strip()
    # Handle trailing Z (Zulu) by replacing with +00:00 for fromisoformat
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except Exception:
        try:
            # fallback without fractional seconds
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")
        except Exception:
            return None


def seed_large_cryptos(db_path: str, dry_run: bool = False, limit: int = 100, max_pages: int = 50):
    api_key = get_api_key()
    if not api_key:
        print("ERROR: CoinMarketCap API key not found. Set COINMARKETCAP_API_KEY or put it in config/config.ini")
        return

    headers = {"X-CMC_PRO_API_KEY": api_key}
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    start = 1

    db = CryptoDatabase(db_path=db_path)

    total_added = 0
    try:
        for page in range(max_pages):
            params = {"start": start, "limit": limit, "convert": "USD"}
            try:
                resp = requests.get(url, headers=headers, params=params, timeout=30)
            except Exception as e:
                print(f"Request error: {e}")
                break

            if resp.status_code != 200:
                print(f"CoinMarketCap API returned status {resp.status_code}: {resp.text}")
                break

            payload = resp.json()
            data = payload.get("data") or []
            if not data:
                break

            for item in data:
                quote = item.get("quote", {}).get("USD", {})
                market_cap = quote.get("market_cap")
                if not market_cap:
                    continue
                if market_cap < 1_000_000_000:
                    # skip smaller market caps
                    continue

                date_added = parse_date_added(item.get("date_added"))
                if not date_added:
                    continue
                # Ensure date_added is timezone-aware for comparison
                if date_added.tzinfo is None:
                    date_added = date_added.replace(tzinfo=timezone.utc)

                if date_added > cutoff:
                    # less than ~3 months old
                    continue

                code = item.get("symbol")
                name = item.get("name")

                if dry_run:
                    print(f"DRY RUN: Would add {code} - {name} | market_cap={market_cap:.2f} | date_added={date_added.isoformat()}")
                else:
                    # store market_entry as ISO string (SQLite will accept text)
                    added_id = db.add_crypto_info(code=code, name=name, market_entry=date_added.isoformat(), market_cap=float(market_cap), favorite=False)
                    if added_id:
                        total_added += 1
                        print(f"Added {code} ({name}) id={added_id} market_cap={market_cap:.2f}")
                    else:
                        print(f"Exists or failed to add {code} ({name})")

            start += limit
            # be polite with rate limits
            time.sleep(1)

    finally:
        db.close()

    print(f"Finished. Total added: {total_added}")


def main():
    parser = argparse.ArgumentParser(description="Seed crypto_info with large, established cryptos")
    parser.add_argument("--db-path", default="data/crypto_prices.db", help="Path to SQLite DB file")
    parser.add_argument("--dry-run", action="store_true", help="Do not insert, only print matches")
    parser.add_argument("--limit", type=int, default=100, help="Results per page (default 100)")
    parser.add_argument("--max-pages", type=int, default=50, help="Maximum pages to fetch (default 50)")

    args = parser.parse_args()

    seed_large_cryptos(db_path=args.db_path, dry_run=args.dry_run, limit=args.limit, max_pages=args.max_pages)


if __name__ == "__main__":
    main()
