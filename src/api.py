"""
Module for fetching cryptocurrency prices from CoinMarketCap API.
Handles EUR quotations for multiple cryptocurrencies.
"""

import os
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class CoinMarketCapAPI:
    """Interface to CoinMarketCap API for cryptocurrency price data."""
    
    BASE_URL = "https://pro-api.coinmarketcap.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            api_key: CoinMarketCap API key. If None, reads from CMC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("CMC_API_KEY")
        if not self.api_key:
            raise ValueError("CMC_API_KEY not provided and not found in environment variables")
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json",
        })
    
    def get_latest_quotes(self, symbols: List[str]) -> Dict:
        """
        Fetch latest cryptocurrency quotes in EUR.
        
        Args:
            symbols: List of cryptocurrency symbols (e.g., ['BTC', 'ETH', 'ADA'])
        
        Returns:
            Dictionary with cryptocurrency data
        """
        url = f"{self.BASE_URL}/cryptocurrency/quotes/latest"
        
        params = {
            "symbol": ",".join(symbols),
            "convert": "EUR",
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching from CoinMarketCap: {str(e)}")
    
    def parse_quotes(self, data: Dict, symbols: List[str]) -> List[Dict]:
        """
        Parse API response and extract relevant price data.
        
        Args:
            data: API response data
            symbols: List of cryptocurrency symbols
        
        Returns:
            List of dictionaries with parsed quote data
        """
        quotes = []
        timestamp = datetime.now()
        
        for symbol in symbols:
            if symbol not in data.get("data", {}):
                print(f"Warning: {symbol} not found in API response")
                continue
            
            coin_data = data["data"][symbol]
            eur_data = coin_data.get("quote", {}).get("EUR", {})
            
            quote = {
                "symbol": symbol,
                "name": coin_data.get("name", ""),
                "price_eur": eur_data.get("price"),
                "market_cap_eur": eur_data.get("market_cap"),
                "volume_24h_eur": eur_data.get("volume_24h"),
                "percent_change_24h": eur_data.get("percent_change_24h"),
                "percent_change_7d": eur_data.get("percent_change_7d"),
                "percent_change_30d": eur_data.get("percent_change_30d"),
                "timestamp": timestamp,
            }
            quotes.append(quote)
        
        return quotes
    
    def fetch_and_parse(self, symbols: List[str]) -> List[Dict]:
        """
        Fetch quotes and parse them in one call.
        
        Args:
            symbols: List of cryptocurrency symbols
        
        Returns:
            List of parsed quote dictionaries
        """
        data = self.get_latest_quotes(symbols)
        return self.parse_quotes(data, symbols)
