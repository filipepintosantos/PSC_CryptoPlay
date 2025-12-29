@echo off
REM Create environment helper
cd /d %~dp0
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Virtual environment not found. Run tools_setup.cmd first.
    exit /b 1
)

REM Run create_env.ps1 if present
if exist scripts\create_env.ps1 (
    powershell -ExecutionPolicy Bypass -File scripts\create_env.ps1
) else (
    echo No create_env.ps1 found in scripts\
)
