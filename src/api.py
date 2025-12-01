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
        # Accept both env var names for compatibility
        self.api_key = api_key or os.getenv("CMC_API_KEY") or os.getenv("COINMARKETCAP_API_KEY")
        if not self.api_key:
            raise ValueError("API key not provided. Set CMC_API_KEY or COINMARKETCAP_API_KEY in environment/.env or pass --api-key")
        
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
        Fetch historical close-of-day quotes for the last `days` days using a single
        between-dates API call per symbol (OHLCV daily). Uses Europe/Lisbon day bounds
        and stores the EUR close price as the quote value for each day.

        Returns a list of quote dicts with `price_eur` set to OHLC close.
        """
        if days <= 0:
            return []

        results: List[Dict] = []
        local_tz = _get_tz("Europe/Lisbon")

        # Compute date window in Europe/Lisbon with date-only bounds.
        # End date is capped to yesterday to avoid partial "today" data.
        today_local = datetime.now(local_tz).date()
        end_date_local = today_local - timedelta(days=1)
        start_date_local = end_date_local - timedelta(days=days - 1)

        # Date-only ISO strings (YYYY-MM-DD) as required by the API call
        time_start_iso = start_date_local.isoformat()
        time_end_iso = end_date_local.isoformat()

        for symbol in symbols:
            url = f"{self.BASE_URL}/cryptocurrency/ohlcv/historical"
            params = {
                "symbol": symbol,
                "convert": "EUR",
                "time_start": time_start_iso,
                "time_end": time_end_iso,
                "interval": "daily",
            }

            try:
                resp = self.session.get(url, params=params, timeout=45)
                resp.raise_for_status()
                data = resp.json()
            except requests.exceptions.RequestException as e:
                print(f"Warning: OHLCV fetch failed for {symbol}: {e}. Falling back to quotes/historical.")
                # Fallback to quotes/historical with interval=daily
                url_q = f"{self.BASE_URL}/cryptocurrency/quotes/historical"
                params_q = {
                    "symbol": symbol,
                    "convert": "EUR",
                    "time_start": time_start_iso,
                    "time_end": time_end_iso,
                    "interval": "daily",
                }
                try:
                    resp = self.session.get(url_q, params=params_q, timeout=45)
                    resp.raise_for_status()
                    data = resp.json()
                except requests.exceptions.RequestException as e2:
                    print(f"Warning: quotes/historical fallback also failed for {symbol}: {e2}")
                    continue

            sym_block = (data.get("data") or {}).get(symbol) or {}
            name = sym_block.get("name", "")

            # Prefer OHLCV structure: list under 'quotes' with quote.EUR.close
            points = []
            if isinstance(sym_block.get("quotes"), list):
                points = sym_block.get("quotes")
            elif isinstance(sym_block.get("data"), list):
                # alternative historical payloads
                points = sym_block.get("data")

            if not points:
                print(f"No historical points returned for {symbol} in range {start_date_local}..{end_date_local}")
                continue

            for p in points:
                # Try OHLCV close first
                eur_q = ((p.get("quote") or {}).get("EUR") or {})
                close_val = eur_q.get("close")
                price_val = eur_q.get("price")
                price_eur = close_val if close_val is not None else price_val

                ts = p.get("time_close") or p.get("timestamp") or p.get("time")
                try:
                    # Parse timestamp if provided; otherwise synthesize as end-of-day UTC for the date
                    ts_dt = datetime.fromisoformat(ts) if isinstance(ts, str) else datetime.combine(end_date_local, time(23, 59, 59))
                except Exception:
                    ts_dt = datetime.combine(end_date_local, time(23, 59, 59))

                results.append({
                    "symbol": symbol,
                    "name": name,
                    "price_eur": price_eur,
                    "market_cap_eur": None,
                    "volume_24h_eur": None,
                    "percent_change_24h": None,
                    "percent_change_7d": None,
                    "percent_change_30d": None,
                    "timestamp": ts_dt,
                })

        return results
