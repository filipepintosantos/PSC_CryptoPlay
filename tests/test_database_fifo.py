"""
Tests for database FIFO wallet functionality.
Tests rebuild_binance_wallet and _load_wallet_ops_config methods.
"""

import unittest
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from src.database import CryptoDatabase


class TestDatabaseFIFO(unittest.TestCase):
    """Test FIFO wallet functionality in CryptoDatabase."""
    
    def setUp(self):
        """Create a test database with sample data."""
        self.test_db = "data/test_fifo.db"
        # Remove if exists
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        
        self.db = CryptoDatabase(self.test_db)
        self.cursor = self.db.conn.cursor()
    
    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def _insert_transaction(self, coin, change, operation, price_eur=100.0):
        """Helper to insert a test transaction."""
        now = datetime.now(timezone.utc)
        self.cursor.execute(
            """INSERT INTO binance_transactions
               (utc_time, coin, change, operation, price_eur)
               VALUES (?, ?, ?, ?, ?)""",
            (now.isoformat(), coin, change, operation, price_eur)
        )
        self.db.conn.commit()
    
    def test_load_wallet_ops_config_defaults(self):
        """Test loading wallet operations from config.ini."""
        entries, exits = self.db._load_wallet_ops_config()
        
        # Check that entries and exits are loaded as sets
        self.assertIsInstance(entries, set)
        self.assertIsInstance(exits, set)
        self.assertGreater(len(entries), 0)
        self.assertGreater(len(exits), 0)
        
        # Config.ini should have Buy and Deposit as entries
        self.assertIn("Buy Crypto With Fiat", entries)
        self.assertIn("Deposit", entries)
        
        # Config.ini should have Sell as exit
        self.assertIn("Sell Crypto To Fiat", exits)
    
    def test_rebuild_binance_wallet_single_entry(self):
        """Test rebuild with a single buy entry."""
        self._insert_transaction("BTC", 0.5, "Buy Crypto With Fiat", 45000.0)
        
        lots_created = self.db.rebuild_binance_wallet()
        
        self.assertGreater(lots_created, 0)
        
        # Check wallet has the lot
        self.cursor.execute("SELECT COUNT(*) FROM binance_wallet WHERE crypto_id = 'BTC'")
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 1)
        
        # Check lot details
        self.cursor.execute(
            "SELECT amount_total, amount_remaining, price_eur FROM binance_wallet WHERE crypto_id = 'BTC'"
        )
        total, remaining, price = self.cursor.fetchone()
        self.assertEqual(total, 0.5)
        self.assertEqual(remaining, 0.5)
        self.assertEqual(price, 45000.0)
    
    def test_rebuild_binance_wallet_fifo_consumption(self):
        """Test FIFO consumption: buy 2 BTC, sell 1 (consume first lot)."""
        # Buy 1 BTC at 40000
        self._insert_transaction("BTC", 1.0, "Buy Crypto With Fiat", 40000.0)
        # Buy 1 BTC at 50000
        self._insert_transaction("BTC", 1.0, "Buy Crypto With Fiat", 50000.0)
        # Sell 0.5 BTC (should consume first lot partially)
        self._insert_transaction("BTC", -0.5, "Sell Crypto To Fiat", 55000.0)
        
        lots_created = self.db.rebuild_binance_wallet()
        
        # Should have 2 buy lots created
        self.assertGreater(lots_created, 0)
        
        # Check remaining amounts (FIFO: first lot should be partially consumed)
        self.cursor.execute(
            "SELECT amount_remaining FROM binance_wallet WHERE crypto_id = 'BTC' ORDER BY utc_time"
        )
        remainings = [row[0] for row in self.cursor.fetchall()]
        
        # First lot: 1.0 - 0.5 = 0.5 remaining
        # Second lot: 1.0 remaining
        self.assertIn(0.5, remainings)
        self.assertIn(1.0, remainings)
    
    def test_rebuild_binance_wallet_multiple_coins(self):
        """Test rebuild with multiple cryptocurrencies."""
        self._insert_transaction("BTC", 1.0, "Buy Crypto With Fiat", 45000.0)
        self._insert_transaction("ETH", 10.0, "Buy Crypto With Fiat", 3000.0)
        self._insert_transaction("ADA", 1000.0, "Buy Crypto With Fiat", 1.5)
        
        lots_created = self.db.rebuild_binance_wallet()
        
        self.assertEqual(lots_created, 3)
        
        # Check each coin has a lot
        self.cursor.execute("SELECT COUNT(DISTINCT crypto_id) FROM binance_wallet")
        coin_count = self.cursor.fetchone()[0]
        self.assertEqual(coin_count, 3)
    
    def test_rebuild_binance_wallet_airdrop_entry(self):
        """Test that airdrop distributions create lots."""
        self._insert_transaction("ADA", 100.0, "Earn - Airdrop Distribution", 1.5)
        
        lots_created = self.db.rebuild_binance_wallet()
        
        # Airdrop should create a lot if configured as entry
        self.assertGreater(lots_created, 0)
    
    def test_rebuild_binance_wallet_earn_redemption(self):
        """Test that deposit creates entry lots (configured entry operation)."""
        # Using Deposit which is in config.ini entries
        self._insert_transaction("USDC", 1000.0, "Deposit", 1.0)
        
        lots_created = self.db.rebuild_binance_wallet()
        
        # Should create a lot for deposit
        self.assertGreater(lots_created, 0)
        
        # Check USDC lot exists
        self.cursor.execute("SELECT COUNT(*) FROM binance_wallet WHERE crypto_id = 'USDC'")
        count = self.cursor.fetchone()[0]
        self.assertGreater(count, 0)
    
    def test_rebuild_binance_wallet_full_consumption(self):
        """Test FIFO where all lots are fully consumed."""
        self._insert_transaction("BTC", 1.0, "Buy Crypto With Fiat", 40000.0)
        self._insert_transaction("BTC", -1.0, "Sell Crypto To Fiat", 50000.0)
        
        lots_created = self.db.rebuild_binance_wallet()
        
        # Check lot is fully consumed
        self.cursor.execute(
            "SELECT amount_remaining FROM binance_wallet WHERE crypto_id = 'BTC'"
        )
        remaining = self.cursor.fetchone()[0]
        self.assertEqual(remaining, 0.0)
    
    def test_rebuild_binance_wallet_multiple_sells(self):
        """Test FIFO with multiple sells consuming multiple lots."""
        # Buy lots (positive change with entry operations)
        self._insert_transaction("BTC", 0.5, "Buy Crypto With Fiat", 40000.0)
        self._insert_transaction("BTC", 0.5, "Buy Crypto With Fiat", 45000.0)
        self._insert_transaction("BTC", 0.5, "Buy Crypto With Fiat", 50000.0)
        
        # Sell 1.2 BTC (negative change with exit operation)
        # This consumes: all of lot 1 (0.5) + all of lot 2 (0.5) + 0.2 of lot 3
        self._insert_transaction("BTC", -1.2, "Sell Crypto To Fiat", 55000.0)
        
        lots_created = self.db.rebuild_binance_wallet()
        
        # Check consumption - we should have 3 lots total from the buy operations
        self.cursor.execute(
            "SELECT COUNT(*) FROM binance_wallet WHERE crypto_id = 'BTC'"
        )
        total_lots = self.cursor.fetchone()[0]
        self.assertEqual(total_lots, 3)
        
        # Check remaining amounts in order (oldest first)
        self.cursor.execute(
            "SELECT amount_remaining FROM binance_wallet WHERE crypto_id = 'BTC' ORDER BY utc_time"
        )
        remainings = [row[0] for row in self.cursor.fetchall()]
        
        # Lot 1: 0.0 (0.5 - 0.5 = 0 fully consumed)
        # Lot 2: 0.0 (0.5 - 0.5 = 0 fully consumed)
        # Lot 3: 0.3 (0.5 - 0.2 = 0.3 partially consumed)
        self.assertAlmostEqual(remainings[0], 0.0, places=5)
        self.assertAlmostEqual(remainings[1], 0.0, places=5)
        self.assertAlmostEqual(remainings[2], 0.3, places=5)
    
    def test_rebuild_binance_wallet_oversell(self):
        """Test FIFO when trying to sell more than available."""
        self._insert_transaction("BTC", 1.0, "Buy Crypto With Fiat", 40000.0)
        self._insert_transaction("BTC", -2.0, "Sell Crypto To Fiat", 50000.0)  # More than available
        
        lots_created = self.db.rebuild_binance_wallet()
        
        # Should handle gracefully (lot goes to 0, excess remains)
        self.cursor.execute(
            "SELECT amount_remaining FROM binance_wallet WHERE crypto_id = 'BTC'"
        )
        remaining = self.cursor.fetchone()[0]
        self.assertLessEqual(remaining, 0.0)
    
    def test_rebuild_binance_wallet_empty_transactions(self):
        """Test rebuild with no transactions."""
        lots_created = self.db.rebuild_binance_wallet()
        
        self.assertEqual(lots_created, 0)
        
        # Wallet should be empty
        self.cursor.execute("SELECT COUNT(*) FROM binance_wallet")
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 0)
    
    def test_rebuild_binance_wallet_clears_old_data(self):
        """Test that rebuild clears previous wallet data."""
        # Insert first time
        self._insert_transaction("BTC", 1.0, "Buy Crypto With Fiat", 40000.0)
        self.db.rebuild_binance_wallet()
        
        # Check we have data
        self.cursor.execute("SELECT COUNT(*) FROM binance_wallet")
        first_count = self.cursor.fetchone()[0]
        self.assertGreater(first_count, 0)
        
        # Clear transactions and rebuild
        self.cursor.execute("DELETE FROM binance_transactions")
        self.db.conn.commit()
        
        lots_created = self.db.rebuild_binance_wallet()
        
        # Wallet should be empty now
        self.cursor.execute("SELECT COUNT(*) FROM binance_wallet")
        final_count = self.cursor.fetchone()[0]
        self.assertEqual(final_count, 0)


if __name__ == "__main__":
    unittest.main()
