"""
Tests for main.py module.
"""

import unittest
import sys
import tempfile
import os
import configparser
from pathlib import Path
from datetime import datetime
from io import StringIO
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import main
from src.database import CryptoDatabase


class TestMainModule(unittest.TestCase):
    """Tests for main module functions."""
    
    def test_import_csv_data(self):
        """Test CSV import functionality."""
        # Create temporary CSV file
        csv_content = """Date,Price
2024-01-01,45000.00
2024-01-02,46000.00
2024-01-03,47000.00"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            csv_path = f.name
        
        try:
            # Create in-memory database
            db = CryptoDatabase(":memory:")
            
            # Import data
            count = main.import_csv_data(
                csv_path=csv_path,
                symbol='BTC',
                db=db,
                date_column='Date',
                price_column='Price',
                skip_header=True
            )
            
            # Verify import
            self.assertEqual(count, 3)
            
            # Verify data in database
            quotes = db.get_quotes('BTC')
            self.assertEqual(len(quotes), 3)
            
            db.close()
        finally:
            os.unlink(csv_path)
    
    def test_import_csv_data_with_numeric_columns(self):
        """Test CSV import with numeric column indices."""
        csv_content = """2024-01-01,45000.00
2024-01-02,46000.00"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            csv_path = f.name
        
        try:
            db = CryptoDatabase(":memory:")
            
            count = main.import_csv_data(
                csv_path=csv_path,
                symbol='ETH',
                db=db,
                date_column='0',
                price_column='1',
                skip_header=False
            )
            
            self.assertEqual(count, 2)
            db.close()
        finally:
            os.unlink(csv_path)
    
    def test_import_csv_data_with_date_format(self):
        """Test CSV import with custom date format."""
        csv_content = """Date,Price
01/01/2024,45000.00
02/01/2024,46000.00"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            csv_path = f.name
        
        try:
            db = CryptoDatabase(":memory:")
            
            count = main.import_csv_data(
                csv_path=csv_path,
                symbol='SOL',
                db=db,
                date_column='Date',
                price_column='Price',
                date_format='%d/%m/%Y',
                skip_header=True
            )
            
            self.assertEqual(count, 2)
            db.close()
        finally:
            os.unlink(csv_path)
    
    def test_import_csv_data_skips_invalid_rows(self):
        """Test CSV import handles invalid data gracefully."""
        csv_content = """Date,Price
2024-01-01,45000.00
INVALID_DATE,46000.00
2024-01-03,INVALID_PRICE
2024-01-04,47000.00"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            csv_path = f.name
        
        try:
            db = CryptoDatabase(":memory:")
            
            # Should skip invalid rows
            count = main.import_csv_data(
                csv_path=csv_path,
                symbol='ADA',
                db=db,
                date_column='Date',
                price_column='Price',
                skip_header=True
            )
            
            # Only 2 valid rows
            self.assertEqual(count, 2)
            db.close()
        finally:
            os.unlink(csv_path)
    
    def test_import_csv_data_handles_different_price_formats(self):
        """Test CSV import handles various price formats."""
        csv_content = """Date,Price
2024-01-01,45,000.00
2024-01-02,46000
2024-01-03,47000.00"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write(csv_content)
            csv_path = f.name
        
        try:
            db = CryptoDatabase(":memory:")
            
            count = main.import_csv_data(
                csv_path=csv_path,
                symbol='LINK',
                db=db,
                date_column='Date',
                price_column='Price',
                skip_header=True
            )
            
            self.assertEqual(count, 3)
            db.close()
        finally:
            os.unlink(csv_path)
    
    def test_default_symbols_constant(self):
        """Test that DEFAULT_SYMBOLS constant is defined."""
        self.assertIsNotNone(main.DEFAULT_SYMBOLS)
        self.assertIsInstance(main.DEFAULT_SYMBOLS, str)
        self.assertIn('BTC', main.DEFAULT_SYMBOLS)


class TestMainModuleIntegration(unittest.TestCase):
    """Integration tests for main module."""
    
    def test_imports_work(self):
        """Test that all imports are available."""
        self.assertTrue(hasattr(main, 'YFinanceCryptoAPI'))
        self.assertTrue(hasattr(main, 'CryptoDatabase'))
        self.assertTrue(hasattr(main, 'StatisticalAnalyzer'))
        self.assertTrue(hasattr(main, 'ExcelReporter'))
    
    def test_import_csv_data_function_exists(self):
        """Test that import_csv_data function is defined."""
        self.assertTrue(callable(main.import_csv_data))


class TestConfigLoading(unittest.TestCase):
    """Tests for configuration loading."""
    
    def test_load_config_returns_configparser(self):
        """Test that load_config returns a ConfigParser instance."""
        config = main.load_config()
        self.assertIsInstance(config, configparser.ConfigParser)
    
    def test_load_config_handles_missing_file(self):
        """Test load_config handles missing config file gracefully."""
        with patch('pathlib.Path.exists', return_value=False):
            config = main.load_config()
            self.assertIsInstance(config, configparser.ConfigParser)


class TestSymbolDetermination(unittest.TestCase):
    """Tests for symbol determination logic."""
    
    def test_determine_symbols_with_explicit_symbols(self):
        """Test determining symbols from explicit argument."""
        args = Mock(all_from_db=False, symbols="BTC,ETH,SOL", all_symbols=False, favorites=False)
        config = configparser.ConfigParser()
        
        symbols = main.determine_symbols(args, config, ":memory:")
        
        self.assertEqual(symbols, ['BTC', 'ETH', 'SOL'])
    
    def test_determine_symbols_with_all_symbols(self):
        """Test determining symbols with all_symbols flag."""
        args = Mock(all_from_db=False, symbols=None, all_symbols=True, favorites=False)
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'all', 'BTC,ETH,ADA')
        
        symbols = main.determine_symbols(args, config, ":memory:")
        
        self.assertEqual(symbols, ['BTC', 'ETH', 'ADA'])
    
    def test_determine_symbols_defaults_to_favorites(self):
        """Test determining symbols defaults to favorites."""
        args = Mock(all_from_db=False, symbols=None, all_symbols=False, favorites=True)
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites', 'BTC,ETH')
        
        symbols = main.determine_symbols(args, config, ":memory:")
        
        self.assertEqual(symbols, ['BTC', 'ETH'])
    
    def test_determine_symbols_from_database(self):
        """Test determining symbols from database."""
        args = Mock(all_from_db=True, symbols=None, all_symbols=False, favorites=False)
        config = configparser.ConfigParser()
        
        # Create temporary database with some cryptos
        db = CryptoDatabase(":memory:")
        db.add_crypto_info('BTC', 'Bitcoin', market_cap=1000000000000)
        db.add_crypto_info('ETH', 'Ethereum', market_cap=500000000000)
        db.close()
        
        # When no data in fresh DB, returns None (prints message)
        symbols = main.determine_symbols(args, config, ":memory:")
        
        self.assertIsNone(symbols)


class TestQuoteOperations(unittest.TestCase):
    """Tests for quote fetching and storing operations."""
    
    def test_store_quotes_with_upsert(self):
        """Test storing quotes with upsert mode."""
        db = CryptoDatabase(":memory:")
        quotes = [
            {'symbol': 'BTC', 'name': 'Bitcoin', 'price_eur': 45000, 'timestamp': datetime.now()},
            {'symbol': 'ETH', 'name': 'Ethereum', 'price_eur': 2500, 'timestamp': datetime.now()}
        ]
        
        count = main.store_quotes(db, quotes, upsert=True, fetch_mode="full")
        
        self.assertEqual(count, 2)
        db.close()
    
    def test_store_quotes_batch_insert(self):
        """Test storing quotes with batch insert."""
        db = CryptoDatabase(":memory:")
        quotes = [
            {'symbol': 'BTC', 'name': 'Bitcoin', 'price_eur': 45000, 'timestamp': datetime.now()}
        ]
        
        count = main.store_quotes(db, quotes, upsert=False, fetch_mode="incremental")
        
        self.assertEqual(count, 1)
        db.close()
    
    def test_fetch_quotes_incremental_mode(self):
        """Test fetching quotes in incremental mode."""
        api = Mock()
        api.fetch_and_parse = Mock(return_value=[])
        
        db = CryptoDatabase(":memory:")
        db.add_cryptocurrency('BTC', 'Bitcoin')
        
        symbols = ['BTC']
        quotes = main.fetch_quotes_incremental(api, symbols, db, "incremental")
        
        api.fetch_and_parse.assert_called_once_with(symbols)
        self.assertEqual(quotes, [])
        db.close()
    
    def test_fetch_quotes_full_mode(self):
        """Test fetching quotes in full mode."""
        api = Mock()
        api.fetch_and_parse = Mock(return_value=[])
        
        db = CryptoDatabase(":memory:")
        symbols = ['BTC', 'ETH']
        
        quotes = main.fetch_quotes_incremental(api, symbols, db, "full")
        
        api.fetch_and_parse.assert_called_once_with(symbols)
        db.close()
    
    @patch('time.sleep')
    def test_fetch_historical_range(self, mock_sleep):
        """Test fetching historical range."""
        api = Mock()
        api.fetch_historical_range = Mock(return_value=[
            {'symbol': 'BTC', 'name': 'Bitcoin', 'price_eur': 45000, 'timestamp': datetime.now()}
        ])
        
        db = CryptoDatabase(":memory:")
        symbols = ['BTC']
        
        count = main.fetch_historical_range(api, symbols, days=30, db=db, 
                                           throttle_seconds=0.1, retries=3)
        
        self.assertEqual(count, 1)
        api.fetch_historical_range.assert_called_once()
        db.close()
    
    @patch('time.sleep')
    def test_fetch_historical_range_with_retry(self, mock_sleep):
        """Test historical range fetch with retry on error."""
        api = Mock()
        api.fetch_historical_range = Mock(side_effect=[
            Exception("Network error"),
            [{'symbol': 'BTC', 'name': 'Bitcoin', 'price_eur': 45000, 'timestamp': datetime.now()}]
        ])
        
        db = CryptoDatabase(":memory:")
        symbols = ['BTC']
        
        count = main.fetch_historical_range(api, symbols, days=30, db=db,
                                           throttle_seconds=0.1, retries=3)
        
        self.assertEqual(count, 1)
        self.assertEqual(api.fetch_historical_range.call_count, 2)
        db.close()


if __name__ == "__main__":
    unittest.main()
