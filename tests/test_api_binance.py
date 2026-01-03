"""Tests for Binance API client."""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import json

from src.api_binance import BinanceAPI, get_price_at_second, get_klines


class TestBinanceAPI(unittest.TestCase):
    """Tests for BinanceAPI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = BinanceAPI()
    
    def test_api_initialization(self):
        """Test API client initialization."""
        self.assertIsNotNone(self.api)
        self.assertEqual(self.api.timeout, 10)
    
    def test_api_custom_timeout(self):
        """Test API with custom timeout."""
        api = BinanceAPI(timeout=30)
        self.assertEqual(api.timeout, 30)
    
    @patch('src.api_binance.requests.get')
    def test_get_price_at_second_success(self, mock_get):
        """Test successful price fetch at exact second."""
        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = [
            [
                1672649400000,  # open_time
                "45000.50",     # open_price
                "45100.00",     # high
                "44900.00",     # low
                "45050.00",     # close
                "10.5",         # volume
                1672649401000,  # close_time
                "472527.50",    # quote_asset_volume
                100,            # number_of_trades
                "5.2",          # taker_buy_base_asset_volume
                "234127.50",    # taker_buy_quote_asset_volume
                "0"             # ignore
            ]
        ]
        mock_get.return_value = mock_response
        
        dt = datetime(2023, 1, 3, 12, 30, 0)
        price, timestamp = self.api.get_price_at_second('BTCEUR', dt)
        
        self.assertEqual(price, 45000.50)
        self.assertEqual(timestamp, 1672649400000)
        mock_get.assert_called_once()
    
    @patch('src.api_binance.requests.get')
    def test_get_price_at_second_no_data(self, mock_get):
        """Test when no data is available for timestamp."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        dt = datetime(2023, 1, 3, 12, 30, 0)
        price, timestamp = self.api.get_price_at_second('BTCEUR', dt)
        
        self.assertIsNone(price)
        self.assertIsNone(timestamp)
    
    @patch('src.api_binance.requests.get')
    def test_get_price_at_second_api_error(self, mock_get):
        """Test API error response handling."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": -1013,
            "msg": "Invalid symbol"
        }
        mock_get.return_value = mock_response
        
        dt = datetime(2023, 1, 3, 12, 30, 0)
        
        with self.assertRaises(Exception) as context:
            self.api.get_price_at_second('INVALID', dt)
        
        self.assertIn("Binance API error", str(context.exception))
    
    @patch('src.api_binance.requests.get')
    def test_get_price_at_second_network_error(self, mock_get):
        """Test network error handling."""
        import requests
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        dt = datetime(2023, 1, 3, 12, 30, 0)
        
        with self.assertRaises(Exception) as context:
            self.api.get_price_at_second('BTCEUR', dt)
        
        self.assertIn("Network error", str(context.exception))
    
    @patch('src.api_binance.requests.get')
    def test_get_klines_success(self, mock_get):
        """Test successful klines fetch."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            [1672649400000, "45000.50", "45100.00", "44900.00", "45050.00", "10.5"],
            [1672649460000, "45050.00", "45150.00", "45000.00", "45100.00", "12.3"]
        ]
        mock_get.return_value = mock_response
        
        klines = self.api.get_klines('BTCEUR', '1m')
        
        self.assertEqual(len(klines), 2)
        self.assertEqual(float(klines[0][1]), 45000.50)
        self.assertEqual(float(klines[1][1]), 45050.00)
    
    @patch('src.api_binance.requests.get')
    def test_get_klines_with_time_range(self, mock_get):
        """Test klines fetch with time range."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        start_time = 1672649400000
        end_time = 1672649460000
        
        self.api.get_klines('BTCEUR', '1m', start_time, end_time)
        
        # Verify parameters
        call_args = mock_get.call_args
        params = call_args[1]['params']
        self.assertEqual(params['startTime'], start_time)
        self.assertEqual(params['endTime'], end_time)
    
    @patch('src.api_binance.requests.get')
    def test_get_klines_limit_capped(self, mock_get):
        """Test that klines limit is capped at 1000."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        self.api.get_klines('BTCEUR', '1m', limit=5000)
        
        call_args = mock_get.call_args
        params = call_args[1]['params']
        self.assertEqual(params['limit'], 1000)


class TestModuleLevelFunctions(unittest.TestCase):
    """Tests for module-level convenience functions."""
    
    @patch('src.api_binance.BinanceAPI.get_price_at_second')
    def test_get_price_at_second_function(self, mock_method):
        """Test module-level get_price_at_second function."""
        mock_method.return_value = (45000.50, 1672649400000)
        
        dt = datetime(2023, 1, 3, 12, 30, 0)
        price, timestamp = get_price_at_second('BTCEUR', dt)
        
        self.assertEqual(price, 45000.50)
        self.assertEqual(timestamp, 1672649400000)
    
    @patch('src.api_binance.BinanceAPI.get_klines')
    def test_get_klines_function(self, mock_method):
        """Test module-level get_klines function."""
        mock_method.return_value = [[1672649400000, "45000.50"]]
        
        klines = get_klines('BTCEUR', '1m')
        
        self.assertEqual(len(klines), 1)
        mock_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()
