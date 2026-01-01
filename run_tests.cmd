@echo off
REM Script to run tests for PSC CryptoPlay
REM Usage: run_tests.bat [options]
REM Options: -v (verbose), -c (coverage), -u (unittest only)

setlocal enabledelayedexpansion

echo.
echo ====================================================
echo PSC CryptoPlay - Test Runner
echo ====================================================
echo.

REM Ensure virtual environment is activated; if not, activate it automatically
if not defined VIRTUAL_ENV (
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    ) else (
        echo ERROR: Virtual environment not found.
        echo Create it first: python -m venv venv
        exit /b 1
    )
)

REM Parse arguments
set TEST_MODE=pytest
set COVERAGE=false
set VERBOSE=

for %%A in (%*) do (
    if "%%A"=="-u" set TEST_MODE=unittest
    if "%%A"=="-c" set COVERAGE=true
    if "%%A"=="-v" set VERBOSE=-v
)

REM Run tests based on mode
if "%TEST_MODE%"=="unittest" (
    echo [*] Running tests with unittest...
    echo.
    venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" %VERBOSE%
) else (
    echo [*] Running tests with pytest...
    echo.
    
    REM Check if pytest is installed
    venv\Scripts\python.exe -c "import pytest" >nul 2>&1
    if errorlevel 1 (
        echo ERROR: pytest not found
        echo Please install with: pip install -r requirements-dev.txt
        exit /b 1
    )
    
    REM Run with or without coverage
    if "%COVERAGE%"=="true" (
        echo [*] Generating coverage report...
        venv\Scripts\python.exe -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term
        if errorlevel 0 (
            echo.
            echo Coverage report generated: htmlcov\index.html
        )
    ) else (
        venv\Scripts\python.exe -m pytest tests/ %VERBOSE%
    )
)

echo.
echo ====================================================
echo Test run completed
echo ====================================================
echo.
REM Automatic cleanup: remove test database files created during tests
echo Cleaning test database files...
if exist "data\test*.db*" (
    del /q "data\test*.db*"
    echo Removed test database files matching data\test*.db*
) else (
    echo No test database files found (data\test*.db*)
)

rem pause
echo Cleanup complete.
