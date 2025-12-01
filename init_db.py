#!/usr/bin/env python
"""
Initialize database with cryptocurrency information.
This script is called during setup.bat to create the database structure.
"""

import sys
from datetime import datetime
from src.database import CryptoDatabase

def init_database():
    """Initialize the database with default cryptocurrency information."""
    try:
        print("Initializing database...")
        db = CryptoDatabase("data/crypto_prices.db")
        
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

if __name__ == "__main__":
    sys.exit(init_database())
