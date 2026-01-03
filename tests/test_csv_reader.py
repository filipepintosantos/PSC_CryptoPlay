"""Tests for CSV reader module."""

import unittest
import tempfile
import os
from pathlib import Path
from datetime import datetime

from src.csv_reader import CSVReader, CSVConfig, import_crypto_data


class TestCSVConfig(unittest.TestCase):
    """Tests for CSVConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = CSVConfig()
        self.assertEqual(config.date_column, 0)
        self.assertEqual(config.price_column, 1)
        self.assertTrue(config.has_header)
        self.assertEqual(config.encoding, 'utf-8')
        self.assertEqual(config.delimiter, ',')
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = CSVConfig(
            date_column='Date',
            price_column='Price',
            has_header=True,
            date_format='%d-%m-%Y'
        )
        self.assertEqual(config.date_column, 'Date')
        self.assertEqual(config.price_column, 'Price')
        self.assertEqual(config.date_format, '%d-%m-%Y')


class TestCSVReaderParsing(unittest.TestCase):
    """Tests for CSV parsing functionality."""
    
    def test_parse_date_iso_format(self):
        """Test parsing ISO format date."""
        date = CSVReader._parse_date('2025-01-03')
        self.assertEqual(date.year, 2025)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 3)
    
    def test_parse_date_with_explicit_format(self):
        """Test parsing with explicit format."""
        date = CSVReader._parse_date('03-01-2025', '%d-%m-%Y')
        self.assertEqual(date.year, 2025)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 3)
    
    def test_parse_date_auto_detect(self):
        """Test automatic date format detection."""
        date1 = CSVReader._parse_date('2025-01-03')
        date2 = CSVReader._parse_date('03-01-2025')
        date3 = CSVReader._parse_date('01/03/2025')
        
        self.assertEqual(date1.year, 2025)
        self.assertEqual(date2.year, 2025)
        self.assertEqual(date3.year, 2025)
    
    def test_parse_date_invalid(self):
        """Test invalid date raises ValueError."""
        with self.assertRaises(ValueError):
            CSVReader._parse_date('INVALID_DATE')
    
    def test_parse_price_simple(self):
        """Test simple price parsing."""
        price = CSVReader._parse_price('100.50')
        self.assertEqual(price, 100.50)
    
    def test_parse_price_with_currency(self):
        """Test parsing price with currency symbols."""
        self.assertEqual(CSVReader._parse_price('€100.50'), 100.50)
        self.assertEqual(CSVReader._parse_price('$100.50'), 100.50)
        self.assertEqual(CSVReader._parse_price('£100.50'), 100.50)
        self.assertEqual(CSVReader._parse_price('¥100.50'), 100.50)
    
    def test_parse_price_with_whitespace(self):
        """Test parsing price with whitespace."""
        price = CSVReader._parse_price('  100.50  ')
        self.assertEqual(price, 100.50)
    
    def test_parse_price_with_comma_separator(self):
        """Test parsing price with comma as decimal separator."""
        price = CSVReader._parse_price('100,50')
        self.assertEqual(price, 100.50)
    
    def test_parse_price_invalid(self):
        """Test invalid price raises ValueError."""
        with self.assertRaises(ValueError):
            CSVReader._parse_price('INVALID_PRICE')


class TestCSVReaderFileIO(unittest.TestCase):
    """Tests for CSV file reading."""
    
    def setUp(self):
        """Create temporary files for testing."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_csv_file(self, content: str, filename: str = 'test.csv') -> Path:
        """Helper to create CSV file."""
        path = Path(self.temp_dir) / filename
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    def test_read_simple_csv(self):
        """Test reading simple CSV with header."""
        content = """Date,Price
2025-01-01,100.50
2025-01-02,101.00
2025-01-03,99.75"""
        path = self._create_csv_file(content)
        
        reader = CSVReader(CSVConfig(date_column='Date', price_column='Price'))
        rows = reader.read_file(path)
        
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]['date'].day, 1)
        self.assertEqual(rows[0]['price'], 100.50)
    
    def test_read_csv_numeric_indices(self):
        """Test reading CSV with numeric column indices."""
        content = """2025-01-01,100.50
2025-01-02,101.00"""
        path = self._create_csv_file(content)
        
        config = CSVConfig(has_header=False, date_column=0, price_column=1)
        reader = CSVReader(config)
        rows = reader.read_file(path)
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['price'], 100.50)
    
    def test_read_csv_with_currency(self):
        """Test reading CSV with currency symbols."""
        content = """Date,Price
2025-01-01,€100.50
2025-01-02,$101.00
2025-01-03,£99.75"""
        path = self._create_csv_file(content)
        
        reader = CSVReader(CSVConfig(date_column='Date', price_column='Price'))
        rows = reader.read_file(path)
        
        self.assertEqual(rows[0]['price'], 100.50)
        self.assertEqual(rows[1]['price'], 101.00)
        self.assertEqual(rows[2]['price'], 99.75)
    
    def test_read_csv_skip_rows(self):
        """Test reading CSV with rows to skip."""
        content = """Metadata line 1
Metadata line 2
Date,Price
2025-01-01,100.50
2025-01-02,101.00"""
        path = self._create_csv_file(content)
        
        config = CSVConfig(skip_rows=2, date_column='Date', price_column='Price')
        reader = CSVReader(config)
        rows = reader.read_file(path)
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['date'].day, 1)
    
    def test_read_csv_file_not_found(self):
        """Test reading non-existent file raises error."""
        reader = CSVReader()
        with self.assertRaises(FileNotFoundError):
            reader.read_file('/nonexistent/file.csv')
    
    def test_read_csv_different_delimiters(self):
        """Test reading CSV with different delimiters."""
        content = """Date;Price
2025-01-01;100.50
2025-01-02;101.00"""
        path = self._create_csv_file(content)
        
        config = CSVConfig(delimiter=';', date_column='Date', price_column='Price')
        reader = CSVReader(config)
        rows = reader.read_file(path)
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['price'], 100.50)


class TestImportCryptoData(unittest.TestCase):
    """Tests for import_crypto_data convenience function."""
    
    def setUp(self):
        """Create temporary files for testing."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_csv_file(self, content: str) -> Path:
        """Helper to create CSV file."""
        path = Path(self.temp_dir) / 'test.csv'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    def test_import_crypto_data(self):
        """Test import_crypto_data function."""
        content = """Date,Price
2025-01-01,100.50
2025-01-02,101.00"""
        path = self._create_csv_file(content)
        
        config = CSVConfig(date_column='Date', price_column='Price')
        data = import_crypto_data(path, 'BTC', config)
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['symbol'], 'BTC')
        self.assertEqual(data[0]['close_eur'], 100.50)
        self.assertEqual(data[0]['price_eur'], 100.50)
        self.assertIsInstance(data[0]['timestamp'], datetime)


if __name__ == '__main__':
    unittest.main()
