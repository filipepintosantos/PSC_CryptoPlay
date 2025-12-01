@echo off
echo ===============================================
echo Testing and Cleaning Database
echo ===============================================
echo.

call venv\Scripts\activate.bat

echo [1/3] Running unit tests...
python -m unittest discover -s tests -p "test_*.py" -v
if errorlevel 1 (
    echo.
    echo ERROR: Tests failed!
    pause
    exit /b 1
)

echo.
echo [2/3] Recreating price_quotes table...
python scripts\recreate_price_quotes.py

echo.
echo [3/3] Verifying empty table...
python -c "from src.database import CryptoDatabase; db=CryptoDatabase('data/crypto_prices.db'); quotes=db.get_quotes('BTC'); print(f'BTC quotes in DB: {len(quotes)}'); db.close()"

echo.
echo ===============================================
echo Done! Database is clean and ready.
echo ===============================================
pause
