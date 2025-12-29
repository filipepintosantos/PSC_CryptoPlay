@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo PSC CryptoPlay - Remove stubs and .orig files
echo ==================================================
echo.
echo This script will list and optionally delete:
echo  - known stub scripts in scripts\
echo  - any files matching scripts\*.orig
echo  - any files matching scripts\legacy\*.orig
echo.

echo Files that will be considered for deletion:
if exist "scripts\migrate_to_ohlc_schema.py" echo  - scripts\migrate_to_ohlc_schema.py
if exist "scripts\recreate_price_quotes.py" echo  - scripts\recreate_price_quotes.py
if exist "scripts\migrate_price_quotes_to_symbol.py" echo  - scripts\migrate_price_quotes_to_symbol.py
if exist "scripts\migrate_simplify_price_quotes.py" echo  - scripts\migrate_simplify_price_quotes.py
if exist "scripts\migrate_to_favorite_classes.py" echo  - scripts\migrate_to_favorite_classes.py
if exist "scripts\add_last_quote_date_column.py" echo  - scripts\add_last_quote_date_column.py

for %%F in (scripts\*.orig) do echo  - %%F
for %%F in (scripts\legacy\*.orig) do echo  - %%F

echo.
set /p CONFIRM=Proceed and permanently delete the listed files? (y/N): 
if /i not "%CONFIRM%"=="y" (
    echo Aborting - no files were deleted.
    endlocal
    exit /b 0
)

echo Deleting files...
del /q "scripts\migrate_to_ohlc_schema.py" 2>nul
del /q "scripts\recreate_price_quotes.py" 2>nul
del /q "scripts\migrate_price_quotes_to_symbol.py" 2>nul
del /q "scripts\migrate_simplify_price_quotes.py" 2>nul
del /q "scripts\migrate_to_favorite_classes.py" 2>nul
del /q "scripts\add_last_quote_date_column.py" 2>nul

del /q "scripts\*.orig" 2>nul
del /q "scripts\legacy\*.orig" 2>nul

echo Deletion complete.
endlocal
exit /b 0
