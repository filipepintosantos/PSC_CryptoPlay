@echo off
REM Wrapper script to run PSC CryptoPlay
REM This script uses the system PATH to find Python

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Try to find Python
for /f "delims=" %%i in ('where python 2^>nul') do (
    set "PYTHON_PATH=%%i"
    goto :found
)

REM If not found, try common locations
if exist "C:\Python311\python.exe" (
    set "PYTHON_PATH=C:\Python311\python.exe"
    goto :found
)

if exist "C:\Python310\python.exe" (
    set "PYTHON_PATH=C:\Python310\python.exe"
    goto :found
)

if exist "C:\Python39\python.exe" (
    set "PYTHON_PATH=C:\Python39\python.exe"
    goto :found
)

echo ERROR: Python not found in PATH or common locations
echo Please install Python 3.8+ from https://www.python.org/
pause
exit /b 1

:found
echo Found Python: !PYTHON_PATH!

REM Check if venv exists, if not create it
if not exist "venv" (
    echo Creating virtual environment...
    "!PYTHON_PATH!" -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Run main.py with arguments
"!PYTHON_PATH!" main.py %*
