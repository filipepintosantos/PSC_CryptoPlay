"""
Module for fetching cryptocurrency prices from CoinMarketCap API.
Handles EUR quotations for multiple cryptocurrencies.
"""

import os
import requests
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Timezone handling: prefer stdlib zoneinfo, fallback to dateutil.tz
try:
    from zoneinfo import ZoneInfo
    def _get_tz(name: str):
        return ZoneInfo(name)
except Exception:
    from dateutil import tz as _dt_tz
    def _get_tz(name: str):
        return _dt_tz.gettz(name)

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

    def get_historical_quote(self, symbol: str, timestamp: datetime) -> Optional[Dict]:
        """
        Attempt to fetch a historical quote for a single symbol at a given timestamp.
        Falls back to latest quote if historical endpoint is unavailable.

        Args:
            symbol: Cryptocurrency symbol
            timestamp: Target timestamp (with tzinfo) — ISO format will be sent to the API

        Returns:
            Parsed quote dict or None on failure
        """
        # Try the historical quotes endpoint; if it's not available, fall back to latest
        url = f"{self.BASE_URL}/cryptocurrency/quotes/historical"
        params = {
            "symbol": symbol,
            "convert": "EUR",
            # Use the same instant for start/end to try to get the nearest datapoint
            "time_start": timestamp.isoformat(),
            "time_end": timestamp.isoformat(),
        }

        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # The structure should be compatible with parse_quotes expectations
            return data
        except requests.exceptions.RequestException:
            # Fallback to latest if historical not supported or request fails
            try:
                latest = self.get_latest_quotes([symbol])
                return latest
            except Exception:
                return None
    
    def parse_quotes(self, data: Dict, symbols: List[str], timestamp_override: Optional[datetime] = None) -> List[Dict]:
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
            
            # Some endpoints (historical) may return a slightly different structure,
            # so we defensively access nested keys and allow a timestamp override
            coin_data = data.get("data", {}).get(symbol) or {}
            eur_data = coin_data.get("quote", {}).get("EUR", {})

            quote_ts = timestamp_override or timestamp

            quote = {
                "symbol": symbol,
                "name": coin_data.get("name", ""),
                "price_eur": eur_data.get("price"),
                "market_cap_eur": eur_data.get("market_cap"),
                "volume_24h_eur": eur_data.get("volume_24h"),
                "percent_change_24h": eur_data.get("percent_change_24h"),
                "percent_change_7d": eur_data.get("percent_change_7d"),
                "percent_change_30d": eur_data.get("percent_change_30d"),
                "timestamp": quote_ts,
            }
            quotes.append(quote)
        
        return quotes
    
    def fetch_and_parse(self, symbols: List[str], close_of_day: bool = False) -> List[Dict]:
        """
        Fetch quotes and parse them in one call.
        
        Args:
            symbols: List of cryptocurrency symbols
        
        Returns:
            List of parsed quote dictionaries
        """
        # If close_of_day is requested, compute target timestamp at 23:59:59 WET (approximated as UTC)
        # and try to retrieve historical quotes for that instant. If the historical endpoint
        # is unavailable, fall back to the latest quote for that symbol.
        if close_of_day:
            # Compute today's 23:59:59 in Europe/Lisbon (handles DST) and use that timestamp.
            local_tz = _get_tz("Europe/Lisbon")
            today_local = datetime.now(local_tz).date()
            target_local = datetime.combine(today_local, time(23, 59, 59))
            # Attach timezone if not already
            if target_local.tzinfo is None:
                try:
                    target_local = target_local.replace(tzinfo=local_tz)
                except Exception:
                    # dateutil tz may require localize-like behavior; fallback to assign
                    target_local = target_local.replace(tzinfo=local_tz)

            quotes = []
            for symbol in symbols:
                raw = self.get_historical_quote(symbol, target_local)
                if raw:
                    parsed = self.parse_quotes(raw, [symbol], timestamp_override=target_local)
                    if parsed:
                        quotes.extend(parsed)
                else:
                    print(f"Warning: could not fetch historical quote for {symbol}; skipping")

            return quotes

        data = self.get_latest_quotes(symbols)
        return self.parse_quotes(data, symbols)

    def fetch_historical_range(self, symbols: List[str], days: int = 30) -> List[Dict]:
        """
        Fetch historical close-of-day quotes for the last `days` days (including today).

        This will query the historical endpoint once per (symbol, day). The method is
        defensive about API response shape: it will look for time-series inside the
        response and pick the last datapoint of the day (closest to end of day).

        Note: This can be slow and is subject to API rate limits. Ensure your API plan
        supports the historical endpoint and adjust request pacing if necessary.
        """
        if days <= 0:
            return []

        quotes = []
        local_tz = _get_tz("Europe/Lisbon")

        for day_offset in range(days):
            # compute target day: today - day_offset
            day = datetime.now(local_tz).date() - timedelta(days=day_offset)
            time_start = datetime.combine(day, time(0, 0, 0)).replace(tzinfo=local_tz)
            time_end = datetime.combine(day, time(23, 59, 59)).replace(tzinfo=local_tz)

            for symbol in symbols:
                url = f"{self.BASE_URL}/cryptocurrency/quotes/historical"
                params = {
                    "symbol": symbol,
                    "convert": "EUR",
                    "time_start": time_start.isoformat(),
                    "time_end": time_end.isoformat(),
                }

                try:
                    resp = self.session.get(url, params=params, timeout=30)
                    resp.raise_for_status()
                    data = resp.json()
                except requests.exceptions.RequestException:
                    # Fallback to latest single point if historical fails
                    try:
                        data = self.get_latest_quotes([symbol])
                    except Exception:
                        print(f"Warning: failed fetching historical for {symbol} on {day}")
                        continue

                # Try to extract time-series points from response
                symbol_block = data.get("data", {}).get(symbol) or {}

                # Some historical responses include a 'quotes' list or 'data' list
                points = []
                if isinstance(symbol_block.get("quotes"), list):
                    points = symbol_block.get("quotes")
                elif isinstance(symbol_block.get("data"), list):
                    points = symbol_block.get("data")
                else:
                    # Try to see if the structure matches latest-quote style
                    eur = symbol_block.get("quote", {}).get("EUR")
                    if eur:
                        points = [{"quote": {"EUR": eur}, "timestamp": time_end.isoformat()}]

                if not points:
                    print(f"No data points for {symbol} on {day}")
                    continue

                # Pick last point (closest to end of day)
                last_point = points[-1]
                eur_data = last_point.get("quote", {}).get("EUR", {})
                ts_raw = last_point.get("timestamp") or last_point.get("time") or time_end.isoformat()

                # Build quote dict
                try:
                    q_ts = datetime.fromisoformat(ts_raw)
                except Exception:
                    q_ts = time_end

                quote = {
                    "symbol": symbol,
                    "name": symbol_block.get("name", ""),
                    "price_eur": eur_data.get("price"),
                    "market_cap_eur": eur_data.get("market_cap"),
                    "volume_24h_eur": eur_data.get("volume_24h"),
                    "percent_change_24h": eur_data.get("percent_change_24h"),
                    "percent_change_7d": eur_data.get("percent_change_7d"),
                    "percent_change_30d": eur_data.get("percent_change_30d"),
                    "timestamp": q_ts,
                }
                quotes.append(quote)

        return quotes
