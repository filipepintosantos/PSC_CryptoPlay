"""
Module for fetching cryptocurrency prices using yfinance.
Handles EUR quotations for multiple cryptocurrencies.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class YFinanceCryptoAPI:
    """Interface to Yahoo Finance for cryptocurrency price data in EUR."""
    
    # Mapping of symbols to Yahoo Finance tickers (crypto pairs with EUR)
    TICKER_MAP = {
        'BTC': 'BTC-EUR',
        'ETH': 'ETH-EUR',
        'ADA': 'ADA-EUR',
        'SOL': 'SOL-EUR',
        'XRP': 'XRP-EUR',
        'LINK': 'LINK-EUR',
        'ATOM': 'ATOM-EUR',
        'XTZ': 'XTZ-EUR',
        'DOT': 'DOT-EUR',
        'MATIC': 'MATIC-EUR',
        'AVAX': 'AVAX-EUR',
        'UNI': 'UNI-EUR',
        'LTC': 'LTC-EUR',
        'BCH': 'BCH-EUR',
    }
    
    def __init__(self):
        """Initialize the yfinance API client."""
        pass
    
    def get_ticker(self, symbol: str) -> str:
        """
        Get Yahoo Finance ticker for a cryptocurrency symbol.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC')
        
        Returns:
            Yahoo Finance ticker (e.g., 'BTC-EUR')
        """
        return self.TICKER_MAP.get(symbol.upper(), f"{symbol.upper()}-EUR")
    
    def get_latest_quote(self, symbol: str) -> Optional[Dict]:
        """
        Fetch the latest cryptocurrency quote in EUR.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC')
        
        Returns:
            Dictionary with quote data or None on failure
        """
        try:
            ticker = self.get_ticker(symbol)
            crypto = yf.Ticker(ticker)
            
            # Get current price
            info = crypto.info
            
            if not info or 'regularMarketPrice' not in info:
                return None
            
            return {
                'symbol': symbol,
                'name': info.get('shortName', symbol),
                'price_eur': info.get('regularMarketPrice'),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error fetching latest quote for {symbol}: {e}")
            return None
    
    def get_latest_quotes(self, symbols: List[str]) -> List[Dict]:
        """
        Fetch latest quotes for multiple cryptocurrencies.
        
        Args:
            symbols: List of cryptocurrency symbols
        
        Returns:
            List of quote dictionaries
        """
        quotes = []
        for symbol in symbols:
            quote = self.get_latest_quote(symbol)
            if quote:
                quotes.append(quote)
        return quotes
    
    def fetch_historical_range(self, symbols: List[str], days: int = 365) -> List[Dict]:
        """
        Fetch historical close-of-day quotes for the last N days.
        
        Args:
            symbols: List of cryptocurrency symbols
            days: Number of days of historical data (default: 365)
        
        Returns:
            List of quote dictionaries with date and close price
        """
        if days <= 0:
            return []
        
        results = []
        
        # Calculate date range (end = yesterday to avoid partial data)
        end_date = datetime.now().date() - timedelta(days=1)
        start_date = end_date - timedelta(days=days - 1)
        
        for symbol in symbols:
            try:
                ticker = self.get_ticker(symbol)
                crypto = yf.Ticker(ticker)
                
                # Download historical data
                hist = crypto.history(
                    start=start_date.isoformat(),
                    end=(end_date + timedelta(days=1)).isoformat(),  # Include end date
                    interval='1d'
                )
                
                if hist.empty:
                    print(f"No historical data for {symbol}")
                    continue
                
                # Extract close prices
                for date, row in hist.iterrows():
                    results.append({
                        'symbol': symbol,
                        'name': symbol,
                        'price_eur': row['Close'],
                        'timestamp': date.to_pydatetime().date()
                    })
                
                print(f"✓ Fetched {len(hist)} days for {symbol}")
                
            except Exception as e:
                print(f"Error fetching historical data for {symbol}: {e}")
                continue
        
        return results
    
    def fetch_and_parse(self, symbols: List[str], close_of_day: bool = False) -> List[Dict]:
        """
        Fetch quotes and parse them (compatibility method).
        
        Args:
            symbols: List of cryptocurrency symbols
            close_of_day: Not used (yfinance always returns close prices)
        
        Returns:
            List of parsed quote dictionaries
        """
        return self.get_latest_quotes(symbols)
