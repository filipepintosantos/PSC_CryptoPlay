# SonarQube Scanner Configuration for PSC CryptoPlay
# Windows Batch Script to run SonarQube analysis

@echo off
setlocal enabledelayedexpansion

echo.
echo ====================================================
echo PSC CryptoPlay - SonarCloud Analysis
echo ====================================================
echo.

REM Load environment variables from .env file
if exist ".env" (
    echo [*] Loading environment variables from .env...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" (
            set "%%a=%%b"
        )
    )
)

REM Check if SONAR_TOKEN is set
if not defined SONAR_TOKEN (
    echo ERROR: SONAR_TOKEN not found
    echo.
    echo Please add your SonarCloud token to .env file:
    echo SONAR_TOKEN=your_token_here
    echo.
    pause
    exit /b 1
)

REM Check if sonar-scanner is installed
where sonar-scanner >nul 2>&1
if errorlevel 1 (
    echo ERROR: sonar-scanner not found in PATH
    echo.
    echo Please install SonarQube Scanner:
    echo 1. Download from: https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/
    echo 2. Extract to a folder (e.g., C:\Tools\sonar-scanner)
    echo 3. Add to PATH: setx PATH "%%PATH%%;C:\Tools\sonar-scanner\bin"
    echo.
    pause
    exit /b 1
)

echo [*] SonarQube Scanner version:
sonar-scanner --version
echo.

REM Check if coverage.xml exists
if not exist "coverage.xml" (
    echo [*] Generating code coverage report...
    venv\Scripts\python.exe -m pytest tests/ --cov=src --cov-report=xml
    if errorlevel 1 (
        echo WARNING: Failed to generate coverage report
        echo Continuing without coverage...
    )
    echo.
)

REM Run SonarCloud analysis
echo [*] Running SonarCloud analysis...
echo.

sonar-scanner -Dsonar.host.url=https://sonarcloud.io -Dsonar.token=%SONAR_TOKEN%

echo.
echo ====================================================
echo SonarCloud analysis completed
echo ====================================================
echo.
echo View results at:
echo https://sonarcloud.io/dashboard?id=filipepintosantos_PSC_CryptoPlay
echo.
pause
