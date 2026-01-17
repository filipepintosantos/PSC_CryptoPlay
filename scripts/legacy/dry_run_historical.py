"""Dry-run for historical fetch: simula o comportamento da API sem chamadas reais.

Usage:
    .\venv\Scripts\python.exe scripts\dry_run_historical.py --days 365 --symbols BTC,ETH
"""

import argparse
import random
from datetime import datetime, timedelta, time as dtime, timezone
import sys
from pathlib import Path

# Ensure `src` is importable when running from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from api import CoinMarketCapAPI


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def make_latest_payload(symbols):
    data = {}
    for s in symbols:
        price = round(1000 + random.random() * 50000, 2)
        data[s] = {
            "name": f"{s}Coin",
            "quote": {
                "EUR": {
                    "price": price,
                    "market_cap": round(price * random.random() * 1e6, 2),
                    "volume_24h": round(random.random() * 1e7, 2),
                    "percent_change_24h": round(random.uniform(-10, 10), 2),
                    "percent_change_7d": round(random.uniform(-20, 20), 2),
                    "percent_change_30d": round(random.uniform(-50, 50), 2),
                }
            }
        }
    return {"data": data}


def make_historical_payload(symbol, time_end_iso):
    # produce a list of a few intraday points and return under 'quotes'
    points = []
    # create 3 sample points across the day
    for i in range(3):
        price = round(1000 + random.random() * 50000, 2)
        ts = datetime.fromisoformat(time_end_iso) - timedelta(hours=2 - i)
        points.append({
            "timestamp": ts.isoformat(),
            "quote": {"EUR": {
                "price": price,
                "market_cap": round(price * random.random() * 1e6, 2),
                "volume_24h": round(random.random() * 1e7, 2),
                "percent_change_24h": round(random.uniform(-10, 10), 2),
            }}
        })
    return {"data": {symbol: {"name": f"{symbol}Coin", "quotes": points}}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--symbols", type=str, default="BTC,ETH,ADA")
    args = parser.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    days = args.days

    api = CoinMarketCapAPI(api_key="DUMMY")

    # Monkeypatch session.get to return fake responses
    def fake_get(url, params=None, timeout=None):
        params = params or {}
        if "historical" in url:
            symbol = params.get("symbol")
            time_end = params.get("time_end") or params.get("time_end")
            if not time_end:
                # fallback to end of today
                time_end = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=0).isoformat()
            payload = make_historical_payload(symbol, time_end)
            return FakeResponse(payload)
        else:
            # latest
            syms = []
            if params and params.get("symbol"):
                syms = [s.strip().upper() for s in params.get("symbol").split(",")]
            else:
                syms = symbols
            payload = make_latest_payload(syms)
            return FakeResponse(payload)

    api.session.get = fake_get

    # Run the historical range fetch
    quotes = api.fetch_historical_range(symbols, days=days)

    print(f"Dry-run fetched {len(quotes)} quote points for {len(symbols)} symbols over {days} days")
    # show first 5 and last 5 samples
    samples = quotes[:5]
    for q in samples:
        print(f"{q['symbol']} {q['timestamp']} €{q['price_eur']}")
    if len(quotes) > 5:
        print("...")
        for q in quotes[-5:]:
            print(f"{q['symbol']} {q['timestamp']} €{q['price_eur']}")


if __name__ == '__main__':
    main()
