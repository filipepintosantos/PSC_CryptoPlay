#!/usr/bin/env python
"""
Initialize database with cryptocurrency information.
This script is called during setup.bat to create the database structure.
"""

import sys
import subprocess
import argparse
from datetime import datetime
from src.database import CryptoDatabase


def init_database(db_path: str = "data/crypto_prices.db"):
    """Initialize the database with default cryptocurrency information."""
    try:
        print("Initializing database...")
        db = CryptoDatabase(db_path)

        # List of default cryptocurrencies with their market entry dates
        default_cryptos = [
            ("BTC", "Bitcoin", datetime(2009, 1, 3), None, True),
            ("ETH", "Ethereum", datetime(2015, 7, 30), None, True),
            ("USDT", "Tether", datetime(2014, 11, 26), None, False),
            ("XRP", "XRP", datetime(2012, 8, 4), None, False),
            ("BNB", "Binance Coin", datetime(2017, 7, 25), None, False),
            ("SOL", "Solana", datetime(2020, 3, 16), None, True),
            ("USDC", "USD Coin", datetime(2018, 9, 26), None, False),
            ("TRX", "TRON", datetime(2017, 8, 30), None, False),
            ("DOGE", "Dogecoin", datetime(2013, 12, 6), None, False),
            ("ADA", "Cardano", datetime(2017, 10, 1), None, True),
            ("LINK", "Chainlink", datetime(2017, 9, 19), None, True),
            ("ATOM", "Cosmos", datetime(2019, 3, 13), None, True),
            ("XTZ", "Tezos", datetime(2018, 6, 30), None, False),
        ]

        # Add cryptocurrencies to database
        for code, name, market_entry, market_cap, favorite in default_cryptos:
            db.add_crypto_info(code, name, market_entry, market_cap, favorite)
            print(f"  ✓ Added {code} ({name})")

        db.close()
        print("Database initialized successfully!")
        return 0

    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")
        return 1


def run_seed_large(db_path: str):
    """Run the `scripts/seed_large_cryptos.py` script using the same Python interpreter."""
    cmd = [sys.executable, "scripts\\seed_large_cryptos.py", "--db-path", db_path]
    print("Running seed script:", " ".join(cmd))
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        print(f"ERROR: Failed to execute seed script: {e}")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize DB and optionally seed large cryptos")
    parser.add_argument("--db-path", default="data/crypto_prices.db", help="Path to SQLite DB file")
    parser.add_argument("--seed-large", action="store_true", help="Run seed script to add large, older cryptos from CoinMarketCap")
    args = parser.parse_args()

    rc = init_database(db_path=args.db_path)
    if rc != 0:
        sys.exit(rc)

    if args.seed_large:
        rc2 = run_seed_large(args.db_path)
        sys.exit(rc2)

    sys.exit(0)
