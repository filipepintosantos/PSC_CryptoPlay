"""
Tests for seed_large_cryptos_yfinance script.
Tests the yfinance-based cryptocurrency seeding functionality.
"""
import os
import tempfile
import shutil
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import pandas as pd

from scripts.seed_large_cryptos_yfinance import get_large_established_cryptos
from src.database import CryptoDatabase


class TestSeedLargeCryptosYfinance(unittest.TestCase):
    """Test suite for yfinance-based cryptocurrency seeding."""
    
    @patch('scripts.seed_large_cryptos_yfinance.get_all_cryptos_from_coingecko')
    def test_filters_cryptos_by_criteria(self, mock_get_cryptos):
        """Test that filtering logic correctly identifies valid cryptocurrencies."""
        # Mock the CoinGecko API call to return test data directly
        mock_get_cryptos.return_value = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "market_cap": 500_000_000_000  # >100M ✓
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "market_cap": 200_000_000_000  # >100M ✓
            }
        ]
        
        # Create proper pandas DataFrame for yfinance history
        old_date = datetime.now(timezone.utc) - timedelta(days=365)
        mock_hist = pd.DataFrame(
            {'Close': [50000.0]},
            index=pd.DatetimeIndex([old_date])
        )
        
        # Mock yfinance Ticker
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_hist
        
        with patch('yfinance.Ticker', return_value=mock_ticker):
            result = get_large_established_cryptos()
            
            # Should return a list with our test cryptos
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0, "Should return at least one crypto")
            
            # Bitcoin should be in results
            btc_found = any(c["code"] == "BTC" for c in result)
            self.assertTrue(btc_found, "Bitcoin should be in results")


if __name__ == "__main__":
    unittest.main()
