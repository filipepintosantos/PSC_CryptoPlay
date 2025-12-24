@echo off
REM Script para atualizar a versão do projeto

set PYTHON_EXEC=venv\Scripts\python.exe
if not exist %PYTHON_EXEC% set PYTHON_EXEC=python

%PYTHON_EXEC% scripts\update_version.py %*
