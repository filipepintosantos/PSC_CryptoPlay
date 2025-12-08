"""
Extended tests for YFinance API module to improve coverage.
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api_yfinance import YFinanceCryptoAPI


class TestYFinanceAPIExtended(unittest.TestCase):
    """Extended tests for YFinance API."""
    
    def setUp(self):
        """Set up test environment."""
        self.api = YFinanceCryptoAPI()
    
    def test_fetch_and_parse_compatibility(self):
        """Test fetch_and_parse compatibility method."""
        quotes = self.api.fetch_and_parse(['BTC'])
        
        # Should behave like get_latest_quotes
        self.assertIsInstance(quotes, list)
    
    def test_get_ticker_format(self):
        """Test ticker format conversion."""
        ticker = self.api.get_ticker('BTC')
        self.assertEqual(ticker, 'BTC-EUR')
        
        ticker = self.api.get_ticker('ETH')
        self.assertEqual(ticker, 'ETH-EUR')
        
        ticker = self.api.get_ticker('SOL')
        self.assertEqual(ticker, 'SOL-EUR')
    
    def test_get_latest_quotes_empty_list(self):
        """Test get_latest_quotes with empty symbol list."""
        quotes = self.api.get_latest_quotes([])
        self.assertEqual(quotes, [])
    
    def test_get_latest_quotes_structure(self):
        """Test that latest quotes return proper structure."""
        quotes = self.api.get_latest_quotes(['BTC'])
        
        if quotes:
            quote = quotes[0]
            # Verify structure
            self.assertIn('symbol', quote)
            self.assertIn('name', quote)
            self.assertIn('price_eur', quote)
            self.assertIn('timestamp', quote)
            
            # Verify types
            self.assertIsInstance(quote['symbol'], str)
            self.assertIsInstance(quote['name'], str)
            self.assertTrue(isinstance(quote['price_eur'], (int, float)))
    
    def test_get_latest_quote_single(self):
        """Test getting latest quote for single symbol."""
        quote = self.api.get_latest_quote('BTC')
        
        if quote:
            self.assertIn('symbol', quote)
            self.assertEqual(quote['symbol'], 'BTC')
            self.assertIn('price_eur', quote)


class TestYFinanceAPIErrorHandling(unittest.TestCase):
    """Test error handling in YFinance API."""
    
    def setUp(self):
        """Set up test environment."""
        self.api = YFinanceCryptoAPI()
    
    def test_get_latest_quotes_with_mixed_valid_invalid(self):
        """Test getting quotes with mix of valid and invalid symbols."""
        symbols = ['BTC', 'INVALID_XYZ', 'ETH']
        quotes = self.api.get_latest_quotes(symbols)
        
        # Should return quotes for valid symbols, skip invalid
        self.assertIsInstance(quotes, list)
        
        if quotes:
            symbols_returned = [q['symbol'] for q in quotes]
            # Invalid symbol should not be in results
            self.assertNotIn('INVALID_XYZ', symbols_returned)
    
    def test_api_resilience(self):
        """Test that API handles multiple rapid calls."""
        # Make several quick calls
        for i in range(3):
            quotes = self.api.get_latest_quotes(['BTC'])
            self.assertIsInstance(quotes, list)


if __name__ == "__main__":
    unittest.main()
