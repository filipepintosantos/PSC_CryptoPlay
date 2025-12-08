@echo off
REM Setup script for PSC CryptoPlay - Windows
REM This script creates a virtual environment and installs dependencies

setlocal enabledelayedexpansion

echo.
echo ====================================================
echo PSC CryptoPlay - Virtual Environment Setup (Windows)
echo ====================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/4] Python version:
python --version
echo.

REM Create virtual environment
echo [2/4] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping creation
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)
echo.

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo.

REM Install dependencies
echo [4/4] Installing dependencies...
pip install --upgrade pip setuptools wheel >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Create .env from template if it doesn't exist
if not exist ".env" (
    echo Creating .env from template...
    copy .env.example .env
    echo .env created - please edit with your CMC_API_KEY
)
echo.

REM Create necessary directories
echo Creating necessary directories...
if not exist "data" mkdir data
if not exist "reports" mkdir reports
if not exist "logs" mkdir logs
echo.

REM Initialize database
echo Initializing database...
python init_db.py
if errorlevel 1 (
    echo WARNING: Failed to initialize database, but setup will continue
    echo You can try again with: python init_db.py
)
echo.

echo ====================================================
echo Setup completed successfully!
echo ====================================================
echo.
echo Virtual environment is activated. You can now run:
echo   python main.py
echo.
echo Optional: Install development tools (pytest, pylint, black, etc):
echo   pip install -r requirements-dev.txt
echo.
echo Then run tests with:
echo   run_tests.bat
echo   python -m unittest discover -s tests -p "test_*.py" -v
echo.
echo To deactivate the environment later, type:
echo   deactivate
echo.
echo To activate it again, run:
echo   venv\Scripts\activate.bat
echo.
pause
