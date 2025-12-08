@echo off
REM Create or update .env interactively (Windows CMD)
REM Usage: run this script from project root: scripts\create_env.bat

setlocal

if exist "%~dp0..\.env" (
    echo .env already exists at %~dp0..\.env
    echo If you want to overwrite it, delete the file and run this script again.
    pause
    exit /b 0
)

echo Creating .env for PSC CryptoPlay
echo.
set /p KEY=Enter CoinMarketCap API key (leave empty to create from .env.example): 

if "%KEY%"=="" (
    if exist "%~dp0..\.env.example" (
        copy "%~dp0..\.env.example" "%~dp0..\.env" >nul
        echo Created .env from .env.example
    ) else (
        echo CMC_API_KEY= > "%~dp0..\.env"
        echo COINMARKETCAP_API_KEY= >> "%~dp0..\.env"
        echo Created empty .env (no .env.example found)
    )
) else (
    (echo CMC_API_KEY=%KEY%) > "%~dp0..\.env"
    (echo COINMARKETCAP_API_KEY=%KEY%) >> "%~dp0..\.env"
    echo .env created successfully (wrote CMC_API_KEY and COINMARKETCAP_API_KEY)
)

endlocal
pause
