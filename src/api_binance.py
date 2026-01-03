"""
Binance API client for cryptocurrency data retrieval.

Provides functionality to fetch price data from Binance API endpoints,
including historical klines (candlestick) data.
"""

import requests
from datetime import datetime
from typing import Optional, Tuple

# Binance API endpoints
BINANCE_URL = "https://api.binance.com/api/v3/klines"

# Configuration
REQUEST_TIMEOUT = 10  # seconds


class BinanceAPI:
    """Client for Binance API interactions."""
    
    def __init__(self, base_url: str = BINANCE_URL, timeout: int = REQUEST_TIMEOUT):
        """
        Initialize Binance API client.
        
        Args:
            base_url: Base URL for Binance API (default: klines endpoint)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
    
    def get_price_at_second(self, symbol: str, dt_utc: datetime) -> Tuple[Optional[float], Optional[int]]:
        """
        Fetch price for a trading pair at the exact second.
        
        Uses 1-second klines from Binance API.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCEUR', 'ETHUSDT')
            dt_utc: Datetime object in UTC timezone
            
        Returns:
            Tuple of (open_price, open_time_ms) or (None, None) if no data
            
        Raises:
            Exception: If Binance API returns an error
            requests.RequestException: If network request fails
            
        Example:
            >>> api = BinanceAPI()
            >>> price, ts = api.get_price_at_second('BTCEUR', datetime(2025, 1, 3, 12, 30, 0))
            >>> if price:
            ...     print(f"BTC price at that second: €{price}")
        """
        # Convert datetime to timestamp in milliseconds
        ts = int(dt_utc.timestamp() * 1000)
        
        params = {
            "symbol": symbol,
            "interval": "1s",
            "startTime": ts,
            "endTime": ts + 1000
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise Exception(f"Network error accessing Binance API: {e}")
        
        # Check for API error responses
        if isinstance(data, dict) and "code" in data:
            raise Exception(f"Binance API error: {data.get('msg', data)}")
        
        # No data available for this timestamp
        if not data:
            return None, None
        
        # Extract price data from kline
        kline = data[0]
        open_time = kline[0]  # Opening time in milliseconds
        open_price = float(kline[1])  # Opening price
        
        return open_price, open_time
    
    def get_klines(self, symbol: str, interval: str, start_time: Optional[int] = None,
                   end_time: Optional[int] = None, limit: int = 500) -> list:
        """
        Fetch klines (candlestick data) for a trading pair.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCEUR')
            interval: Kline interval ('1s', '1m', '5m', '1h', '1d', etc.)
            start_time: Start time in milliseconds (optional)
            end_time: End time in milliseconds (optional)
            limit: Maximum number of klines to return (max 1000)
            
        Returns:
            List of klines, each containing [open_time, open, high, low, close, ...]
            
        Raises:
            Exception: If API returns an error
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": min(limit, 1000)  # Binance API limit is 1000
        }
        
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        try:
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise Exception(f"Network error accessing Binance API: {e}")
        
        if isinstance(data, dict) and "code" in data:
            raise Exception(f"Binance API error: {data.get('msg', data)}")
        
        return data or []


# Module-level convenience functions
def get_price_at_second(symbol: str, dt_utc: datetime) -> Tuple[Optional[float], Optional[int]]:
    """
    Convenience function to fetch price at exact second.
    
    Args:
        symbol: Trading pair symbol
        dt_utc: Datetime in UTC
        
    Returns:
        Tuple of (price, timestamp) or (None, None)
    """
    api = BinanceAPI()
    return api.get_price_at_second(symbol, dt_utc)


def get_klines(symbol: str, interval: str, start_time: Optional[int] = None,
               end_time: Optional[int] = None, limit: int = 500) -> list:
    """
    Convenience function to fetch klines.
    
    Args:
        symbol: Trading pair symbol
        interval: Kline interval
        start_time: Start time in ms (optional)
        end_time: End time in ms (optional)
        limit: Maximum klines to return
        
    Returns:
        List of klines
    """
    api = BinanceAPI()
    return api.get_klines(symbol, interval, start_time, end_time, limit)
