@echo off
REM Ativa o venv e inicia a interface gráfica principal
cd /d %~dp0
REM Não é necessário ativar o venv, basta usar o executável correto

REM Set Qt font directory for PyQt6
set QT_QPA_FONTDIR=%~dp0fonts
venv\Scripts\python.exe src\ui_main.py
