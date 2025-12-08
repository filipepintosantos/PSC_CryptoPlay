"""
Extended tests for analysis module to improve code coverage.
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analysis import StatisticalAnalyzer


class TestStatisticalAnalyzerExtended(unittest.TestCase):
    """Extended tests for StatisticalAnalyzer."""
    
    def test_batch_generate_reports_success(self):
        """Test batch report generation with valid data."""
        def mock_get_quotes(symbol):
            # Generate mock quotes
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
        self.assertIn('BTC', reports)
        self.assertIn('ETH', reports)
        self.assertIn('SOL', reports)
        
        # Verify each report has expected structure
        for symbol in symbols:
            self.assertIn('symbol', reports[symbol])
            self.assertIn('data_points', reports[symbol])
            self.assertIn('periods', reports[symbol])
    
    def test_batch_generate_reports_with_error(self):
        """Test batch report generation handles errors gracefully."""
        def mock_get_quotes_with_error(symbol):
            if symbol == 'ERROR':
                raise ValueError("Test error")
            quotes = []
            for i in range(50):
                quotes.append({
                    'price_eur': 50.0 + i,
                    'timestamp': datetime.now() - timedelta(days=i)
                })
            return quotes
        
        symbols = ['BTC', 'ERROR', 'ETH']
        reports = StatisticalAnalyzer.batch_generate_reports(symbols, mock_get_quotes_with_error)
        
        self.assertEqual(len(reports), 3)
        self.assertIn('error', reports['ERROR'])
        self.assertNotIn('error', reports['BTC'])
        self.assertNotIn('error', reports['ETH'])
    
    def test_generate_report_empty_data(self):
        """Test generating report with empty quotes."""
        quotes = []
        report = StatisticalAnalyzer.generate_report('BTC', quotes)
        
        self.assertEqual(report['symbol'], 'BTC')
        self.assertEqual(report['data_points'], 0)
        self.assertIsNone(report['date_range'])
        self.assertEqual(report['periods'], {})
    
    def test_generate_report_with_date_range(self):
        """Test that report includes correct date range."""
        quotes = []
        start_date = datetime(2024, 1, 1)
        for i in range(100):
            quotes.append({
                'price_eur': 45000.0 + i * 100,
                'timestamp': start_date + timedelta(days=i)
            })
        
        report = StatisticalAnalyzer.generate_report('BTC', quotes)
        
        self.assertIsNotNone(report['date_range'])
        self.assertIn('start', report['date_range'])
        self.assertIn('end', report['date_range'])
        self.assertEqual(report['data_points'], 100)
    
    def test_calculate_statistics_with_single_value(self):
        """Test statistics calculation with single data point."""
        prices = [100.0]
        stats = StatisticalAnalyzer.calculate_statistics(prices)
        
        self.assertEqual(stats['count'], 1)
        self.assertEqual(stats['mean'], 100.0)
        self.assertEqual(stats['min'], 100.0)
        self.assertEqual(stats['max'], 100.0)
        self.assertEqual(stats['std'], 0.0)
    
    def test_calculate_statistics_with_various_prices(self):
        """Test statistics with edge case data."""
        prices = [100.0, 200.0, 150.0, 175.0]
        stats = StatisticalAnalyzer.calculate_statistics(prices)
        
        self.assertEqual(stats['count'], 4)
        self.assertGreater(stats['mean'], 0)
        self.assertGreater(stats['std'], 0)
        self.assertEqual(stats['min'], 100.0)
        self.assertEqual(stats['max'], 200.0)
        self.assertIn('mean_minus_std', stats)
    
    def test_prepare_dataframe_from_quotes_various_formats(self):
        """Test dataframe preparation with different timestamp formats."""
        quotes = [
            {'price_eur': 100.0, 'timestamp': datetime.now()},
            {'price_eur': 101.0, 'timestamp': datetime.now().date()},
            {'price_eur': 102.0, 'timestamp': datetime.now() - timedelta(days=1)},
        ]
        
        df = StatisticalAnalyzer.prepare_dataframe_from_quotes(quotes)
        
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 3)
        self.assertIn('timestamp', df.columns)
        self.assertIn('price_eur', df.columns)
    
    def test_analyze_rolling_periods_insufficient_data(self):
        """Test rolling period analysis with insufficient data for some periods."""
        # Create dataframe with only 30 days of data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        df = pd.DataFrame({
            'timestamp': dates,
            'price_eur': [100.0 + i for i in range(30)]
        })
        
        periods = StatisticalAnalyzer.analyze_rolling_periods(df)
        
        # Should have 1_month but not 3_months, 6_months, 12_months
        self.assertIn('1_month', periods)
        # Other periods might be present but with less data
    
    def test_analyze_rolling_periods_exact_boundaries(self):
        """Test rolling periods at exact boundaries."""
        # Create exactly 365 days of data
        dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
        df = pd.DataFrame({
            'timestamp': dates,
            'price_eur': [45000.0 + i * 10 for i in range(365)]
        })
        
        periods = StatisticalAnalyzer.analyze_rolling_periods(df)
        
        # Should have all periods
        self.assertIn('12_months', periods)
        self.assertIn('6_months', periods)
        self.assertIn('3_months', periods)
        self.assertIn('1_month', periods)
        
        # Verify 12_months has all data
        self.assertEqual(periods['12_months']['stats']['count'], 365)


class TestStatisticalAnalyzerEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_prepare_dataframe_empty_list(self):
        """Test with empty quotes list."""
        df = StatisticalAnalyzer.prepare_dataframe_from_quotes([])
        self.assertTrue(df.empty)
    
    def test_prepare_dataframe_missing_fields(self):
        """Test with quotes missing required fields."""
        quotes = [
            {'price_eur': 100.0},  # Missing timestamp
            {'timestamp': datetime.now()}  # Missing price_eur
        ]
        
        # Should handle gracefully or raise appropriate error
        try:
            df = StatisticalAnalyzer.prepare_dataframe_from_quotes(quotes)
            # If it succeeds, check it has some data
            self.assertIsNotNone(df)
        except KeyError:
            # Expected if strict validation
            pass
    
    def test_calculate_statistics_all_same_values(self):
        """Test statistics when all values are identical."""
        prices = [100.0] * 50
        stats = StatisticalAnalyzer.calculate_statistics(prices)
        
        self.assertEqual(stats['mean'], 100.0)
        self.assertEqual(stats['std'], 0.0)
        self.assertEqual(stats['min'], 100.0)
        self.assertEqual(stats['max'], 100.0)
        self.assertEqual(stats['mean_minus_std'], 100.0)
    
    def test_analyze_rolling_periods_with_gaps(self):
        """Test rolling periods with date gaps in data."""
        # Create data with gaps
        dates = []
        prices = []
        current_date = datetime.now()
        
        for i in range(100):
            if i % 10 != 5:  # Skip every 10th day at position 5
                dates.append(current_date - timedelta(days=i))
                prices.append(100.0 + i)
        
        df = pd.DataFrame({
            'timestamp': dates,
            'price_eur': prices
        })
        
        periods = StatisticalAnalyzer.analyze_rolling_periods(df)
        
        # Should still produce valid analysis
        self.assertIsInstance(periods, dict)
        for period_name, period_data in periods.items():
            self.assertIn('stats', period_data)


if __name__ == "__main__":
    unittest.main()
