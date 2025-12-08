"""
Comprehensive test suite for PSC CryptoPlay project.
Tests for database, analysis, API, and main modules.
"""

import unittest
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import CryptoDatabase
from analysis import StatisticalAnalyzer
from api_yfinance import YFinanceCryptoAPI
import main
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
    
    def test_batch_generate_reports(self):
        """Test batch report generation."""
        def mock_get_quotes(symbol):
            quotes = []
            for i in range(100):
                quotes.append({
                    'price_eur': 100.0 + i,
                    'timestamp': datetime.now() - timedelta(days=i)
                })
            return quotes
        
        symbols = ['BTC', 'ETH', 'SOL']
        reports = StatisticalAnalyzer.batch_generate_reports(symbols, mock_get_quotes)
        
        self.assertEqual(len(reports), 3)
        for symbol in symbols:
            self.assertIn(symbol, reports)
            self.assertIn('data_points', reports[symbol])
    
    def test_generate_report_empty_data(self):
        """Test generating report with empty quotes."""
        report = StatisticalAnalyzer.generate_report('BTC', [])
        self.assertEqual(report['symbol'], 'BTC')
        self.assertEqual(report['data_points'], 0)
        self.assertIsNone(report['date_range'])


class TestYFinanceAPI(unittest.TestCase):
    """Tests for YFinance API module."""
    
    def setUp(self):
        """Set up test environment."""
        self.api = YFinanceCryptoAPI()
    
    def test_get_ticker_format(self):
        """Test ticker format conversion."""
        self.assertEqual(self.api.get_ticker('BTC'), 'BTC-EUR')
        self.assertEqual(self.api.get_ticker('ETH'), 'ETH-EUR')
    
    def test_get_latest_quotes_empty_list(self):
        """Test get_latest_quotes with empty symbol list."""
        quotes = self.api.get_latest_quotes([])
        self.assertEqual(quotes, [])
    
    def test_fetch_and_parse_compatibility(self):
        """Test fetch_and_parse compatibility method."""
        quotes = self.api.fetch_and_parse(['BTC'])
        self.assertIsInstance(quotes, list)


class TestMainModule(unittest.TestCase):
    """Tests for main module."""
    
    def test_import_csv_data(self):
        """Test CSV import functionality."""
        csv_content = """Date,Price
2024-01-01,45000.00
2024-01-02,46000.00"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write(csv_content)
            csv_path = f.name
        
        try:
            db = CryptoDatabase(":memory:")
            count = main.import_csv_data(
                csv_path=csv_path,
                symbol='BTC',
                db=db,
                date_column='Date',
                price_column='Price',
                skip_header=True
            )
            
            self.assertEqual(count, 2)
            db.close()
        finally:
            os.unlink(csv_path)
    
    def test_default_symbols_constant(self):
        """Test DEFAULT_SYMBOLS is defined."""
        self.assertIsNotNone(main.DEFAULT_SYMBOLS)
        self.assertIn('BTC', main.DEFAULT_SYMBOLS)


if __name__ == "__main__":
    unittest.main()
