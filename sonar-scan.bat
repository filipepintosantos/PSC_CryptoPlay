# SonarQube Scanner Configuration for PSC CryptoPlay
# Windows Batch Script to run SonarQube analysis

@echo off
setlocal enabledelayedexpansion

echo.
echo ====================================================
echo PSC CryptoPlay - SonarQube Analysis
echo ====================================================
echo.

REM Check if sonar-scanner is installed
where sonar-scanner >nul 2>&1
if errorlevel 1 (
    echo ERROR: sonar-scanner not found in PATH
    echo.
    echo Please install SonarQube Scanner:
    echo 1. Download from: https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/
    echo 2. Extract to a folder
    echo 3. Add to PATH: setx PATH "%%PATH%%;C:\path\to\sonar-scanner\bin"
    echo.
    pause
    exit /b 1
)

echo [*] SonarQube Scanner version:
sonar-scanner --version
echo.

REM Check if coverage.xml exists
if not exist "coverage.xml" (
    echo [*] Generating code coverage report (required for SonarQube)...
    python -m pytest tests/ --cov=src --cov-report=xml
    if errorlevel 1 (
        echo WARNING: Failed to generate coverage report
        echo Run: pip install -r requirements-dev.txt
    )
    echo.
)

REM Run SonarQube analysis
echo [*] Running SonarQube analysis...
echo.

sonar-scanner

echo.
echo ====================================================
echo SonarQube analysis completed
echo ====================================================
echo.
echo View results on your SonarQube server
echo.
pause
