@echo off
chcp 65001 >nul
REM Update cryptocurrency quotes automatically from last quote date to today
REM This script fetches quotes from the last recorded date to today for all cryptocurrencies in crypto_info table

echo ========================================
echo Updating Cryptocurrency Quotes
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment and run main.py with --all-from-db and --auto-range
echo Fetching quotes from last recorded date to today for all cryptocurrencies...
echo.

call venv\Scripts\activate.bat
venv\Scripts\python.exe main.py --all-from-db --auto-range

echo.
echo ========================================
echo Update Complete
echo ========================================
REM pause
