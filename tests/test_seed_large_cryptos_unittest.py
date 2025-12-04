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

from scripts.seed_large_cryptos_yfinance import get_large_established_cryptos
from src.database import CryptoDatabase


class TestSeedLargeCryptosYfinance(unittest.TestCase):
    """Test suite for yfinance-based cryptocurrency seeding."""
    
    def test_filters_cryptos_by_criteria(self):
        """Test that filtering logic correctly identifies valid cryptocurrencies."""
        # Date >90 days ago
        past_date = (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()
        
        # Mock CoinGecko response with test data
        mock_cryptos = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "market_cap": 500_000_000_000,  # >100M ✓
                "atl_date": "2015-01-14T00:00:00.000Z"  # Old ✓
            },
            {
                "id": "small-coin",
                "symbol": "small",
                "name": "SmallCoin",
                "market_cap": 50_000_000,  # <100M ✗
                "atl_date": past_date
            },
            {
                "id": "new-coin",
                "symbol": "new",
                "name": "NewCoin",
                "market_cap": 200_000_000,  # >100M ✓
                "atl_date": datetime.now(timezone.utc).isoformat()  # Too new ✗
            }
        ]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_cryptos
        
        with patch("requests.get", return_value=mock_response):
            # Test that it processes the data (actual EUR validation happens in main flow)
            result = get_large_established_cryptos()
            
            # Should return a list
            self.assertIsInstance(result, list)
            
            # Bitcoin should be in results (meets criteria)
            btc_found = any(c["symbol"].upper() == "BTC" for c in result)
            self.assertTrue(btc_found, "Bitcoin should be in results")


if __name__ == "__main__":
    unittest.main()
