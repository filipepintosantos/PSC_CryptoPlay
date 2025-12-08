"""
Tests for main.py module.
"""

import unittest
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime
from io import StringIO

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


if __name__ == "__main__":
    unittest.main()
