@echo off
call venv\Scripts\activate.bat
python scripts\import_coinmarketcap_csv.py
pause
