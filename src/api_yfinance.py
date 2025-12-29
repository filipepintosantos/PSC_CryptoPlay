"""
Module for fetching cryptocurrency prices using yfinance.
Handles EUR quotations for multiple cryptocurrencies.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf


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
        # no-op initializer
        return None

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

            price = info.get('regularMarketPrice')
            return {
                'symbol': symbol,
                'name': info.get('shortName', symbol),
                'close_eur': price,
                'price_eur': price,  # Backward compatibility
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

    def fetch_historical_range(self, symbols: List[str], days: int = 365,
                              start_date: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch historical close-of-day quotes for the last N days or from a specific start date.

        Args:
            symbols: List of cryptocurrency symbols
            days: Number of days of historical data (default: 365, ignored if start_date is provided)
            start_date: Optional start date to fetch from (if provided, overrides days parameter)

        Returns:
            List of quote dictionaries with date and close price
        """
        results = []
        end_date = datetime.now().date() - timedelta(days=1)
        if start_date:
            calc_start_date = start_date.date() if hasattr(start_date, 'date') else start_date
        elif days > 0:
            calc_start_date = end_date - timedelta(days=days - 1)
        else:
            return []
        for symbol in symbols:
            symbol_results = self._fetch_symbol_history(symbol, calc_start_date, end_date)
            results.extend(symbol_results)
        return results

    def _fetch_symbol_history(self, symbol: str, calc_start_date, end_date) -> List[Dict]:
        results = []
        try:
            ticker = self.get_ticker(symbol)
            crypto = yf.Ticker(ticker)
            hist = crypto.history(
                start=calc_start_date.isoformat(),
                end=(end_date + timedelta(days=1)).isoformat(),
                interval='1d'
            )
            if hist.empty:
                print(f"No historical data for {symbol}")
                return results
            prev_close = None
            for date, row in hist.iterrows():
                close_price = row['Close']
                daily_return = None
                if prev_close is not None and prev_close > 0:
                    daily_return = ((close_price - prev_close) / prev_close) * 100
                results.append({
                    'symbol': symbol,
                    'name': symbol,
                    'close_eur': close_price,
                    'low_eur': row.get('Low'),
                    'high_eur': row.get('High'),
                    'daily_returns': daily_return,
                    'price_eur': close_price,  # Backward compatibility
                    'timestamp': date.to_pydatetime().date()
                })
                prev_close = close_price
            print(f"✓ Fetched {len(hist)} days for {symbol}")
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
        return results

    def fetch_and_parse(self, symbols: List[str]) -> List[Dict]:
        """
        Fetch quotes and parse them (compatibility method).

        Args:
            symbols: List of cryptocurrency symbols

        Returns:
            List of parsed quote dictionaries
        """
        return self.get_latest_quotes(symbols)
