"""
Unit tests for volatility_analysis module.
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from volatility_analysis import VolatilityAnalyzer
from database import CryptoDatabase


class TestVolatilityAnalyzer(unittest.TestCase):
    """Test the VolatilityAnalyzer class."""
    
    def setUp(self):
        """Set up test database with sample data."""
        self.db = CryptoDatabase(":memory:")
        self.analyzer = VolatilityAnalyzer(self.db)
        
        # Add sample crypto
        self.db.add_crypto_info("TEST", "Test Coin", 1000000)
        
        # Add sample price data with various oscillations
        base_price = 100.0
        for i in range(30):
            # Create some oscillations
            if i % 10 == 0:
                price = base_price * 1.15  # +15% spike
            elif i % 7 == 0:
                price = base_price * 0.90  # -10% dip
            elif i % 5 == 0:
                price = base_price * 1.06  # +6% rise
            else:
                price = base_price
            
            timestamp = datetime.now() - timedelta(days=30-i)
            quote_data = {
                'timestamp': timestamp,
                'price_eur': price
            }
            self.db.insert_or_update_quote("TEST", quote_data)
    
    def test_calculate_oscillations_returns_dict(self):
        """Test that calculate_oscillations returns proper structure."""
        result = self.analyzer.calculate_oscillations("TEST", days=30)
        
        self.assertIsInstance(result, dict)
        self.assertIn("24h", result)
        self.assertIn("72h", result)
        self.assertIn("7d", result)
    
    def test_oscillations_have_all_thresholds(self):
        """Test that all threshold counts are present."""
        result = self.analyzer.calculate_oscillations("TEST", days=30)
        
        for window in result.values():
            for threshold in [5, 10, 15, 20]:
                self.assertIn(f'positive_{threshold}', window)
                self.assertIn(f'negative_{threshold}', window)
    
    def test_empty_result_for_missing_symbol(self):
        """Test that missing symbol returns empty result."""
        result = self.analyzer.calculate_oscillations("MISSING", days=30)
        
        for window in result.values():
            for threshold in [5, 10, 15, 20]:
                self.assertEqual(window[f'positive_{threshold}'], 0)
                self.assertEqual(window[f'negative_{threshold}'], 0)
    
    def test_get_summary_stats_structure(self):
        """Test summary stats returns correct keys."""
        summary = self.analyzer.get_summary_stats("TEST", days=30)
        
        self.assertIn('volatility_positive_5', summary)
        self.assertIn('volatility_positive_10', summary)
        self.assertIn('volatility_positive_15', summary)
        self.assertIn('volatility_positive_20', summary)
        self.assertIn('volatility_negative_5', summary)
        self.assertIn('volatility_negative_10', summary)
        self.assertIn('volatility_negative_15', summary)
        self.assertIn('volatility_negative_20', summary)
        self.assertIn('volatility_score', summary)
    
    def test_weighted_score_calculation(self):
        """Test that volatility score is weighted correctly (5*1, 10*2, 15*3, 20*4)."""
        summary = self.analyzer.get_summary_stats("TEST", days=30)
        
        # Calculate expected weighted score
        expected_score = (
            (summary['volatility_positive_5'] + summary['volatility_negative_5']) * 1 +
            (summary['volatility_positive_10'] + summary['volatility_negative_10']) * 2 +
            (summary['volatility_positive_15'] + summary['volatility_negative_15']) * 3 +
            (summary['volatility_positive_20'] + summary['volatility_negative_20']) * 4
        )
        
        self.assertEqual(summary['volatility_score'], expected_score)
    
    def test_analyze_all_symbols(self):
        """Test batch analysis of multiple symbols."""
        # Add another symbol
        self.db.add_crypto_info("TEST2", "Test Coin 2", 500000)
        
        result = self.analyzer.analyze_all_symbols(["TEST", "TEST2"], days=30)
        
        self.assertEqual(len(result), 2)
        self.assertIn("TEST", result)
        self.assertIn("TEST2", result)
    
    def test_export_to_csv_creates_file(self):
        """Test CSV export functionality."""
        import os
        import tempfile
        
        result = self.analyzer.analyze_all_symbols(["TEST"], days=30)
        
        # Use temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_path = f.name
        
        try:
            df = self.analyzer.export_to_csv(result, temp_path)
            
            # Check file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Check DataFrame structure
            self.assertIn('Symbol', df.columns)
            self.assertIn('Window', df.columns)
            self.assertIn('+5%', df.columns)
            self.assertIn('-10%', df.columns)
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_get_period_stats_all_periods(self):
        """Test get_period_stats for all period durations"""
        periods = [30, 90, 180, 365]
        
        for days in periods:
            stats = self.analyzer.get_period_stats("TEST", days)
            
            # Verify structure
            self.assertIn('volatility_positive_5', stats)
            self.assertIn('volatility_negative_5', stats)
            self.assertIn('volatility_positive_10', stats)
            self.assertIn('volatility_negative_10', stats)
            self.assertIn('volatility_positive_15', stats)
            self.assertIn('volatility_negative_15', stats)
            self.assertIn('volatility_positive_20', stats)
            self.assertIn('volatility_negative_20', stats)
            self.assertIn('volatility_score', stats)
            
            # Verify score calculation (weighted)
            score_calc = (
                (stats['volatility_positive_5'] + stats['volatility_negative_5']) * 1 +
                (stats['volatility_positive_10'] + stats['volatility_negative_10']) * 2 +
                (stats['volatility_positive_15'] + stats['volatility_negative_15']) * 3 +
                (stats['volatility_positive_20'] + stats['volatility_negative_20']) * 4
            )
            self.assertEqual(stats['volatility_score'], score_calc)
    
    def test_empty_oscillations_handling(self):
        """Test handling of empty oscillations data"""
        # Symbol with no data
        stats = self.analyzer.get_period_stats("NONEXISTENT", 30)
        
        # Should return zeros
        self.assertEqual(stats['volatility_positive_5'], 0)
        self.assertEqual(stats['volatility_negative_5'], 0)
        self.assertEqual(stats['volatility_score'], 0)
    
    def tearDown(self):
        """Clean up database."""
        self.db.close()


if __name__ == '__main__':
    unittest.main()
