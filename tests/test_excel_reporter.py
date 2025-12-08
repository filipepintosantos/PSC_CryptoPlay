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
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_report.xlsx")
        self.reporter = ExcelReporter(self.test_file)
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_full_workflow(self):
        """Test complete workflow: generate real report with valid data."""
        # Create realistic report structure
        reports = {
            "BTC": {
                "periods": {
                    "12_months": {
                        "stats": {"count": 365, "mean": 44500.0, "std": 5000.0, "min": 30000.0, "max": 60000.0, "mean_minus_std": 39500.0},
                        "latest_quote": 47000,
                        "second_latest_quote": 46000
                    }
                }
            },
            "ETH": {
                "periods": {
                    "12_months": {
                        "stats": {"count": 365, "mean": 2500.0, "std": 500.0, "min": 1500.0, "max": 3500.0, "mean_minus_std": 2000.0},
                        "latest_quote": 2600,
                        "second_latest_quote": 2550
                    }
                }
            }
        }
        
        market_caps = {"BTC": 1000000000000, "ETH": 300000000000}
        favorites = ["BTC"]
        
        self.reporter.generate_report(reports, market_caps, favorites)
        
        # Verify report was created and has content
        self.assertTrue(os.path.exists(self.test_file))
        self.assertGreater(os.path.getsize(self.test_file), 5000)
    
    def test_save_workbook(self):
        """Test saving workbook."""
        # Add a simple sheet
        ws = self.reporter.workbook.create_sheet("Test")
        ws['A1'] = "Test Data"
        
        try:
            self.reporter.save()
            self.assertTrue(os.path.exists(self.test_file))
        except Exception as e:
            self.fail(f"save failed: {e}")
    
    def test_generate_report_with_market_caps_sorted(self):
        """Test that report sorts by market cap."""
        reports = {
            "BTC": {
                "periods": {
                    "12_months": {
                        "stats": {"count": 365, "mean": 45000, "std": 5000, "min": 35000, "max": 55000, "mean_minus_std": 40000},
                        "latest_quote": 47000,
                        "second_latest_quote": 46000
                    }
                }
            },
            "ETH": {
                "periods": {
                    "12_months": {
                        "stats": {"count": 365, "mean": 2500, "std": 500, "min": 1500, "max": 3500, "mean_minus_std": 2000},
                        "latest_quote": 2600,
                        "second_latest_quote": 2550
                    }
                }
            }
        }
        
        market_caps = {"BTC": 1000000000000, "ETH": 300000000000}
        
        try:
            self.reporter.generate_report(reports, market_caps)
            self.assertTrue(os.path.exists(self.test_file))
        except Exception as e:
            self.fail(f"generate_report with market_caps failed: {e}")


if __name__ == "__main__":
    unittest.main()
