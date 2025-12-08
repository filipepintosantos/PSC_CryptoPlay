"""
Comprehensive tests for database module.
Tests all database operations to improve code coverage.
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import CryptoDatabase


class TestCryptoDatabaseComprehensive(unittest.TestCase):
    """Comprehensive tests for CryptoDatabase class."""
    
    def setUp(self):
        """Create temporary test database."""
        self.db = CryptoDatabase(":memory:")
    
    def tearDown(self):
        """Close database connection."""
        if self.db:
            self.db.close()
    
    def test_database_initialization(self):
        """Test database is initialized correctly."""
        self.assertIsNotNone(self.db.conn)
        self.assertEqual(self.db.db_path, ":memory:")
    
    def test_get_all_symbols_empty(self):
        """Test getting symbols from empty database."""
        symbols = self.db.get_all_symbols()
        self.assertEqual(symbols, [])
    
    def test_get_all_symbols_with_data(self):
        """Test getting all symbols after adding cryptocurrencies."""
        self.db.add_cryptocurrency("BTC", "Bitcoin")
        self.db.add_cryptocurrency("ETH", "Ethereum")
        
        symbols = self.db.get_all_symbols()
        self.assertEqual(len(symbols), 2)
        self.assertIn("BTC", symbols)
        self.assertIn("ETH", symbols)
    
    def test_insert_quotes_batch(self):
        """Test batch insertion of quotes."""
        quotes = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price_eur": 45000.0,
                "timestamp": datetime.now() - timedelta(days=2)
            },
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price_eur": 46000.0,
                "timestamp": datetime.now() - timedelta(days=1)
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "price_eur": 3000.0,
                "timestamp": datetime.now()
            }
        ]
        
        count = self.db.insert_quotes_batch(quotes)
        self.assertEqual(count, 3)
        
        # Verify data was inserted
        btc_quotes = self.db.get_quotes("BTC")
        self.assertEqual(len(btc_quotes), 2)
    
    def test_get_quotes_with_days_filter(self):
        """Test getting quotes with days parameter."""
        # Insert quotes for different days
        base_date = datetime.now()
        for i in range(10):
            quote = {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price_eur": 45000.0 + i * 100,
                "timestamp": base_date - timedelta(days=i)
            }
            self.db.insert_quote("BTC", quote)
        
        # Get last 5 days
        quotes_5_days = self.db.get_quotes("BTC", days=5)
        self.assertLessEqual(len(quotes_5_days), 5)
        
        # Get all
        all_quotes = self.db.get_quotes("BTC")
        self.assertEqual(len(all_quotes), 10)
    
    def test_get_latest_quote(self):
        """Test getting the most recent quote."""
        # Insert multiple quotes
        dates = [
            datetime.now() - timedelta(days=5),
            datetime.now() - timedelta(days=2),
            datetime.now()
        ]
        
        for i, date in enumerate(dates):
            quote = {
                "symbol": "SOL",
                "name": "Solana",
                "price_eur": 100.0 + i * 10,
                "timestamp": date
            }
            self.db.insert_quote("SOL", quote)
        
        latest = self.db.get_latest_quote("SOL")
        self.assertIsNotNone(latest)
        self.assertEqual(latest["price_eur"], 120.0)
    
    def test_get_latest_quote_not_found(self):
        """Test getting latest quote for non-existent symbol."""
        latest = self.db.get_latest_quote("NONEXISTENT")
        self.assertIsNone(latest)
    
    def test_get_latest_timestamp(self):
        """Test getting latest timestamp for a cryptocurrency."""
        now = datetime.now()
        quote = {
            "symbol": "ADA",
            "name": "Cardano",
            "price_eur": 0.5,
            "timestamp": now
        }
        self.db.insert_quote("ADA", quote)
        
        latest_ts = self.db.get_latest_timestamp("ADA")
        self.assertIsNotNone(latest_ts)
    
    def test_get_oldest_timestamp(self):
        """Test getting oldest timestamp for a cryptocurrency."""
        dates = [
            datetime.now() - timedelta(days=10),
            datetime.now() - timedelta(days=5),
            datetime.now()
        ]
        
        for date in dates:
            quote = {
                "symbol": "LINK",
                "name": "Chainlink",
                "price_eur": 15.0,
                "timestamp": date
            }
            self.db.insert_quote("LINK", quote)
        
        oldest = self.db.get_oldest_timestamp("LINK")
        self.assertIsNotNone(oldest)
    
    def test_get_quotes_empty(self):
        """Test getting quotes for symbol with no data."""
        quotes = self.db.get_quotes("EMPTY")
        self.assertEqual(quotes, [])
    
    def test_insert_duplicate_quote(self):
        """Test that duplicate quotes are handled correctly (upsert)."""
        now = datetime.now()
        quote1 = {
            "symbol": "BTC",
            "name": "Bitcoin",
            "price_eur": 45000.0,
            "timestamp": now
        }
        quote2 = {
            "symbol": "BTC",
            "name": "Bitcoin",
            "price_eur": 46000.0,  # Different price, same date
            "timestamp": now
        }
        
        # Insert first quote
        success1 = self.db.insert_quote("BTC", quote1)
        self.assertTrue(success1)
        
        # Insert duplicate (should update)
        success2 = self.db.insert_quote("BTC", quote2)
        self.assertTrue(success2)
        
        # Verify only one quote exists with updated price
        quotes = self.db.get_quotes("BTC")
        self.assertEqual(len(quotes), 1)
        self.assertEqual(quotes[0]["price_eur"], 46000.0)
    
    def test_add_crypto_info(self):
        """Test adding cryptocurrency info."""
        success = self.db.add_crypto_info(
            code="BTC",
            name="Bitcoin",
            market_entry=datetime(2009, 1, 3),
            market_cap=900000000000.0,
            favorite=True
        )
        self.assertTrue(success)
        
        # Try adding duplicate
        success2 = self.db.add_crypto_info(
            code="BTC",
            name="Bitcoin Updated",
            market_cap=950000000000.0
        )
        self.assertTrue(success2)
    
    def test_get_crypto_info(self):
        """Test retrieving crypto info."""
        self.db.add_crypto_info(
            code="ETH",
            name="Ethereum",
            market_cap=400000000000.0,
            favorite=False
        )
        
        info = self.db.get_crypto_info("ETH")
        self.assertIsNotNone(info)
        self.assertEqual(info["code"], "ETH")
        self.assertEqual(info["name"], "Ethereum")
        self.assertFalse(info["favorite"])
    
    def test_get_crypto_info_not_found(self):
        """Test getting info for non-existent crypto."""
        info = self.db.get_crypto_info("NOTFOUND")
        self.assertIsNone(info)
    
    def test_get_all_crypto_info(self):
        """Test getting all crypto info."""
        self.db.add_crypto_info("BTC", "Bitcoin", market_cap=900000000000.0)
        self.db.add_crypto_info("ETH", "Ethereum", market_cap=400000000000.0)
        self.db.add_crypto_info("SOL", "Solana", market_cap=50000000000.0)
        
        all_info = self.db.get_all_crypto_info()
        self.assertEqual(len(all_info), 3)
        
        # Verify order by market cap descending
        self.assertEqual(all_info[0]["code"], "BTC")
        self.assertEqual(all_info[1]["code"], "ETH")
        self.assertEqual(all_info[2]["code"], "SOL")
    
    def test_set_favorite(self):
        """Test marking crypto as favorite."""
        self.db.add_crypto_info("ADA", "Cardano", market_cap=15000000000.0)
        
        success = self.db.set_favorite("ADA", True)
        self.assertTrue(success)
        
        info = self.db.get_crypto_info("ADA")
        self.assertTrue(info["favorite"])
        
        # Unmark as favorite
        success = self.db.set_favorite("ADA", False)
        self.assertTrue(success)
        
        info = self.db.get_crypto_info("ADA")
        self.assertFalse(info["favorite"])
    
    def test_get_favorites(self):
        """Test getting favorite cryptocurrencies."""
        self.db.add_crypto_info("BTC", "Bitcoin", favorite=True)
        self.db.add_crypto_info("ETH", "Ethereum", favorite=True)
        self.db.add_crypto_info("SOL", "Solana", favorite=False)
        
        favorites = self.db.get_all_crypto_info(favorites_only=True)
        self.assertEqual(len(favorites), 2)
        codes = [f["code"] for f in favorites]
        self.assertIn("BTC", codes)
        self.assertIn("ETH", codes)
        self.assertNotIn("SOL", codes)
    
    def test_update_crypto_info(self):
        """Test updating crypto info."""
        self.db.add_crypto_info("BTC", "Bitcoin", market_cap=900000000000.0)
        
        # Update market cap
        success = self.db.update_crypto_info("BTC", market_cap=950000000000.0)
        self.assertTrue(success)
        
        info = self.db.get_crypto_info("BTC")
        self.assertEqual(info["market_cap"], 950000000000.0)
    
    def test_delete_crypto_info(self):
        """Test deleting crypto info."""
        self.db.add_crypto_info("XRP", "Ripple", market_cap=30000000000.0)
        
        # Verify it exists
        info = self.db.get_crypto_info("XRP")
        self.assertIsNotNone(info)
        
        # Delete it
        success = self.db.delete_crypto_info("XRP")
        self.assertTrue(success)
        
        # Verify it's gone
        info = self.db.get_crypto_info("XRP")
        self.assertIsNone(info)
    
    def test_context_manager(self):
        """Test database as context manager."""
        with CryptoDatabase(":memory:") as db:
            db.add_cryptocurrency("BTC", "Bitcoin")
            symbols = db.get_all_symbols()
            self.assertIn("BTC", symbols)


if __name__ == "__main__":
    unittest.main()
