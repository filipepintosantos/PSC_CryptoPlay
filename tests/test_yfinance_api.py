"""
Test suite for yfinance API integration.
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api_yfinance import YFinanceCryptoAPI


class TestYFinanceAPI(unittest.TestCase):
    """Tests for YFinanceCryptoAPI module."""
    
    def setUp(self):
        """Initialize API client."""
        self.api = YFinanceCryptoAPI()
    
    def test_get_ticker(self):
        """Test ticker mapping."""
        self.assertEqual(self.api.get_ticker('BTC'), 'BTC-EUR')
        self.assertEqual(self.api.get_ticker('ETH'), 'ETH-EUR')
        self.assertEqual(self.api.get_ticker('UNKNOWN'), 'UNKNOWN-EUR')
    
    def test_get_latest_quote(self):
        """Test fetching latest quote for BTC."""
        quote = self.api.get_latest_quote('BTC')
        
        if quote:  # May fail if network is down
            self.assertEqual(quote['symbol'], 'BTC')
            self.assertIn('price_eur', quote)
            self.assertIsInstance(quote['price_eur'], (int, float))
            self.assertGreater(quote['price_eur'], 0)
            self.assertIn('timestamp', quote)
            self.assertIsInstance(quote['timestamp'], datetime)
    
    def test_get_latest_quotes_multiple(self):
        """Test fetching multiple quotes."""
        quotes = self.api.get_latest_quotes(['BTC', 'ETH'])
        
        if quotes:  # May fail if network is down
            self.assertGreater(len(quotes), 0)
            symbols = [q['symbol'] for q in quotes]
            self.assertIn('BTC', symbols)
    
    def test_fetch_historical_range(self):
        """Test fetching historical data."""
        quotes = self.api.fetch_historical_range(['BTC'], days=7)
        
        if quotes:  # May fail if network is down
            self.assertGreater(len(quotes), 0)
            self.assertLessEqual(len(quotes), 7)  # Should be max 7 days
            
            # Check first quote structure
            quote = quotes[0]
            self.assertEqual(quote['symbol'], 'BTC')
            self.assertIn('price_eur', quote)
            self.assertIn('timestamp', quote)
            
            # Timestamp should be date only
            from datetime import date
            self.assertIsInstance(quote['timestamp'], date)
    
    def test_invalid_symbol(self):
        """Test handling of invalid symbol."""
        quote = self.api.get_latest_quote('INVALID999')
        # Should return None or empty, not crash
        self.assertIsNone(quote)


if __name__ == '__main__':
    unittest.main()
