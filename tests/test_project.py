"""
Test suite for PSC CryptoPlay project.
Provides basic tests for all modules.
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import CryptoDatabase
from analysis import StatisticalAnalyzer
import pandas as pd


class TestDatabase(unittest.TestCase):
    """Tests for CryptoDatabase module."""
    
    def setUp(self):
        """Create temporary test database."""
        self.db = CryptoDatabase(":memory:")  # In-memory database for testing
    
    def tearDown(self):
        """Close database connection."""
        self.db.close()
    
    def test_create_tables(self):
        """Test that tables are created successfully."""
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        self.assertIn("cryptocurrencies", tables)
        self.assertIn("price_quotes", tables)
    
    def test_add_cryptocurrency(self):
        """Test adding a cryptocurrency."""
        crypto_id = self.db.add_cryptocurrency("BTC", "Bitcoin")
        self.assertIsNotNone(crypto_id)
        
        # Add same cryptocurrency again (should not create duplicate)
        crypto_id_2 = self.db.add_cryptocurrency("BTC", "Bitcoin")
        self.assertEqual(crypto_id, crypto_id_2)
    
    def test_insert_quote(self):
        """Test inserting a price quote."""
        quote_data = {
            "name": "Bitcoin",
            "price_eur": 45000.50,
            "market_cap_eur": 900000000,
            "volume_24h_eur": 25000000,
            "percent_change_24h": 2.5,
            "percent_change_7d": -1.2,
            "percent_change_30d": 15.0,
            "timestamp": datetime.now()
        }
        
        result = self.db.insert_quote("BTC", quote_data)
        self.assertTrue(result)
    
    def test_get_all_symbols(self):
        """Test retrieving all symbols."""
        self.db.add_cryptocurrency("BTC", "Bitcoin")
        self.db.add_cryptocurrency("ETH", "Ethereum")
        
        symbols = self.db.get_all_symbols()
        self.assertIn("BTC", symbols)
        self.assertIn("ETH", symbols)


class TestStatisticalAnalyzer(unittest.TestCase):
    """Tests for StatisticalAnalyzer module."""
    
    def test_calculate_statistics(self):
        """Test statistical calculations."""
        prices = [100, 150, 120, 180, 200]
        stats = StatisticalAnalyzer.calculate_statistics(prices)
        
        self.assertEqual(stats["min"], 100)
        self.assertEqual(stats["max"], 200)
        self.assertEqual(stats["count"], 5)
        self.assertIsNotNone(stats["mean"])
        self.assertIsNotNone(stats["std"])
    
    def test_calculate_statistics_empty(self):
        """Test statistics with empty list."""
        prices = []
        stats = StatisticalAnalyzer.calculate_statistics(prices)
        
        self.assertIsNone(stats["min"])
        self.assertIsNone(stats["max"])
        self.assertEqual(stats["count"], 0)
    
    def test_prepare_dataframe(self):
        """Test DataFrame preparation from quotes."""
        quotes = [
            {
                "symbol": "BTC",
                "price_eur": 45000,
                "timestamp": datetime.now()
            },
            {
                "symbol": "BTC",
                "price_eur": 45500,
                "timestamp": datetime.now() - timedelta(days=1)
            },
        ]
        
        df = StatisticalAnalyzer.prepare_dataframe_from_quotes(quotes)
        
        self.assertEqual(len(df), 2)
        self.assertIn("price_eur", df.columns)
        self.assertIn("timestamp", df.columns)
    
    def test_analyze_rolling_periods(self):
        """Test rolling period analysis."""
        now = datetime.now()
        quotes = []
        
        # Create 100 quotes spanning 1 year
        for i in range(100):
            quotes.append({
                "symbol": "BTC",
                "price_eur": 40000 + (i * 100),
                "timestamp": now - timedelta(days=365-i)
            })
        
        df = StatisticalAnalyzer.prepare_dataframe_from_quotes(quotes)
        results = StatisticalAnalyzer.analyze_rolling_periods(df)
        
        self.assertIn("12_months", results)
        self.assertIn("6_months", results)
        self.assertIn("3_months", results)
        self.assertIn("1_month", results)


if __name__ == "__main__":
    unittest.main()
