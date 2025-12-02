@echo off
REM Update cryptocurrency quotes with last 3 days of data
REM This script fetches the latest quotes for all cryptocurrencies in crypto_info table

echo ========================================
echo Updating Cryptocurrency Quotes
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment and run main.py with --all-from-db and --days 3
echo Fetching last 3 days of quotes for all cryptocurrencies...
echo.

call venv\Scripts\activate.bat
python main.py --all-from-db --days 3

echo.
echo ========================================
echo Update Complete
echo ========================================
pause
