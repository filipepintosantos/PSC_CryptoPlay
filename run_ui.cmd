@echo off
REM Ativa o venv e inicia a interface gráfica principal
cd /d %~dp0
REM Não é necessário ativar o venv, basta usar o executável correto
venv\Scripts\python.exe src\ui_main.py
