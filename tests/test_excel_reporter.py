"""
Test suite for Excel Reporter module.
Tests actual report generation to catch runtime errors.
"""

import unittest
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from excel_reporter import ExcelReporter
from database import CryptoDatabase


class TestExcelReporter(unittest.TestCase):
    """Tests for ExcelReporter module."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_report.xlsx")
        self.reporter = ExcelReporter(self.test_file)
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
    
    def test_class_constants_exist(self):
        """Test that required class constants are defined."""
        self.assertTrue(hasattr(ExcelReporter, 'NUMBER_FORMAT_DECIMAL'))
        self.assertTrue(hasattr(ExcelReporter, 'PERIODS'))
        self.assertTrue(hasattr(ExcelReporter, 'PERIOD_DISPLAY'))
        
        # Test constant values
        self.assertEqual(ExcelReporter.NUMBER_FORMAT_DECIMAL, '#,##0.00')
        self.assertIsInstance(ExcelReporter.PERIODS, list)
        self.assertIsInstance(ExcelReporter.PERIOD_DISPLAY, dict)
    
    def test_required_methods_exist(self):
        """Test that all required methods exist with correct names."""
        self.assertTrue(hasattr(self.reporter, 'create_summary_sheet'))
        self.assertTrue(hasattr(self.reporter, 'create_detail_sheet'))
        self.assertTrue(hasattr(self.reporter, 'generate_report'))
        self.assertTrue(hasattr(self.reporter, 'save'))
        
        # Verify no typos in method names
        self.assertFalse(hasattr(self.reporter, 'create_detailed_sheet'), 
                        "Method should be 'create_detail_sheet' not 'create_detailed_sheet'")
    
    def test_generate_empty_report(self):
        """Test generating report with empty data."""
        reports = {}
        try:
            self.reporter.generate_report(reports)
            # Should create file even with empty data
            self.assertTrue(os.path.exists(self.test_file))
        except Exception as e:
            self.fail(f"generate_report() raised {type(e).__name__} unexpectedly: {e}")
    
    def test_generate_simple_report(self):
        """Test generating report with minimal valid data."""
        now = datetime.now()
        reports = {
            "BTC": {
                "12_months": {
                    "count": 365,
                    "mean": 45000.0,
                    "std": 5000.0,
                    "min": 35000.0,
                    "max": 55000.0,
                    "median": 45000.0,
                    "range": 20000.0,
                    "coefficient_variation": 11.11
                },
                "6_months": {
                    "count": 180,
                    "mean": 46000.0,
                    "std": 4000.0,
                    "min": 38000.0,
                    "max": 54000.0,
                    "median": 46000.0,
                    "range": 16000.0,
                    "coefficient_variation": 8.70
                },
                "3_months": {
                    "count": 90,
                    "mean": 47000.0,
                    "std": 3000.0,
                    "min": 40000.0,
                    "max": 52000.0,
                    "median": 47000.0,
                    "range": 12000.0,
                    "coefficient_variation": 6.38
                },
                "1_month": {
                    "count": 30,
                    "mean": 48000.0,
                    "std": 2000.0,
                    "min": 44000.0,
                    "max": 51000.0,
                    "median": 48000.0,
                    "range": 7000.0,
                    "coefficient_variation": 4.17
                }
            }
        }
        
        try:
            self.reporter.generate_report(reports)
            self.assertTrue(os.path.exists(self.test_file))
            
            # Verify file is not empty
            self.assertGreater(os.path.getsize(self.test_file), 0)
        except Exception as e:
            self.fail(f"generate_report() raised {type(e).__name__} unexpectedly: {e}")
    
    def test_generate_with_favorites(self):
        """Test generating report with favorites list."""
        reports = {
            "BTC": {
                "12_months": {
                    "count": 365,
                    "mean": 45000.0,
                    "std": 5000.0,
                    "min": 35000.0,
                    "max": 55000.0,
                    "median": 45000.0,
                    "range": 20000.0,
                    "coefficient_variation": 11.11
                }
            }
        }
        
        favorites = ["BTC"]
        market_caps = {"BTC": 1000000000000}
        
        try:
            self.reporter.generate_report(reports, market_caps, favorites)
            self.assertTrue(os.path.exists(self.test_file))
        except Exception as e:
            self.fail(f"generate_report() with favorites raised {type(e).__name__}: {e}")
    
    def test_create_detail_sheet(self):
        """Test creating detail sheet for a single cryptocurrency."""
        report = {
            "12_months": {
                "count": 365,
                "mean": 45000.0,
                "std": 5000.0,
                "min": 35000.0,
                "max": 55000.0,
                "median": 45000.0,
                "range": 20000.0,
                "coefficient_variation": 11.11
            }
        }
        
        try:
            self.reporter.create_detail_sheet("BTC", report)
            # Should not raise any AttributeError
        except AttributeError as e:
            self.fail(f"create_detail_sheet() raised AttributeError: {e}")


class TestExcelReporterIntegration(unittest.TestCase):
    """Integration tests with database."""
    
    def test_full_workflow(self):
        """Test complete workflow: generate real report with valid data."""
        # Create temporary report file
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, "integration_test.xlsx")
        
        try:
            reporter = ExcelReporter(test_file)
            
            # Create realistic report structure
            reports = {
                "BTC": {
                    "12_months": {
                        "count": 365,
                        "mean": 44500.0,
                        "std": 5000.0,
                        "min": 30000.0,
                        "max": 60000.0,
                        "median": 44500.0,
                        "range": 30000.0,
                        "coefficient_variation": 11.24
                    },
                    "6_months": {
                        "count": 180,
                        "mean": 45000.0,
                        "std": 4000.0,
                        "min": 35000.0,
                        "max": 55000.0,
                        "median": 45000.0,
                        "range": 20000.0,
                        "coefficient_variation": 8.89
                    },
                    "3_months": {
                        "count": 90,
                        "mean": 46000.0,
                        "std": 3000.0,
                        "min": 40000.0,
                        "max": 52000.0,
                        "median": 46000.0,
                        "range": 12000.0,
                        "coefficient_variation": 6.52
                    },
                    "1_month": {
                        "count": 30,
                        "mean": 47000.0,
                        "std": 2000.0,
                        "min": 43000.0,
                        "max": 51000.0,
                        "median": 47000.0,
                        "range": 8000.0,
                        "coefficient_variation": 4.26
                    }
                },
                "ETH": {
                    "12_months": {
                        "count": 365,
                        "mean": 2500.0,
                        "std": 500.0,
                        "min": 1500.0,
                        "max": 3500.0,
                        "median": 2500.0,
                        "range": 2000.0,
                        "coefficient_variation": 20.0
                    },
                    "6_months": {
                        "count": 180,
                        "mean": 2600.0,
                        "std": 400.0,
                        "min": 1800.0,
                        "max": 3400.0,
                        "median": 2600.0,
                        "range": 1600.0,
                        "coefficient_variation": 15.38
                    },
                    "3_months": {
                        "count": 90,
                        "mean": 2700.0,
                        "std": 300.0,
                        "min": 2100.0,
                        "max": 3300.0,
                        "median": 2700.0,
                        "range": 1200.0,
                        "coefficient_variation": 11.11
                    },
                    "1_month": {
                        "count": 30,
                        "mean": 2800.0,
                        "std": 200.0,
                        "min": 2400.0,
                        "max": 3200.0,
                        "median": 2800.0,
                        "range": 800.0,
                        "coefficient_variation": 7.14
                    }
                }
            }
            
            market_caps = {"BTC": 1000000000000, "ETH": 300000000000}
            favorites = ["BTC"]
            
            reporter.generate_report(reports, market_caps, favorites)
            
            # Verify report was created and has content
            self.assertTrue(os.path.exists(test_file))
            self.assertGreater(os.path.getsize(test_file), 5000)  # Excel file should be substantial
            
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)
            os.rmdir(temp_dir)


if __name__ == "__main__":
    unittest.main()
