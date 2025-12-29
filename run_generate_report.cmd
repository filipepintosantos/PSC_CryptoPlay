@echo off
REM ========================================
REM Generate Cryptocurrency Analysis Report
REM ========================================
REM This script generates an Excel report from existing data without fetching new quotes

echo ========================================
echo Generating Cryptocurrency Report
echo ========================================
echo.
echo [1/2] Updating favorites from config...
venv\Scripts\python.exe scripts\mark_favorites.py
echo.
echo [2/2] Generating report from existing data...
echo.

venv\Scripts\python.exe main.py --all-from-db --days 0

echo.
echo ========================================
echo Report generation complete!
echo ========================================
rem pause
