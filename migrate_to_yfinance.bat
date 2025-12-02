@echo off
echo ===============================================
echo PSC CryptoPlay v2.0.0 - Migration to yfinance
echo ===============================================
echo.

call venv\Scripts\activate.bat

echo [1/3] Installing yfinance...
pip install yfinance
echo.

echo [2/3] Testing API...
python -c "from src.api_yfinance import YFinanceCryptoAPI; api = YFinanceCryptoAPI(); quote = api.get_latest_quote('BTC'); print(f'BTC: {quote[\"price_eur\"]:.2f} EUR' if quote else 'API Error')"
echo.

echo [3/3] Fetching 7 days historical for BTC...
python -c "from src.api_yfinance import YFinanceCryptoAPI; api = YFinanceCryptoAPI(); quotes = api.fetch_historical_range(['BTC'], 7); print(f'Fetched {len(quotes)} days'); [print(f'{q[\"timestamp\"]}: {q[\"price_eur\"]:.2f} EUR') for q in quotes[:3]]"
echo.

echo ===============================================
echo Migration complete! Ready to use yfinance.
echo ===============================================
pause
