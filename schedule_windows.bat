@echo off
REM Script de exemplo para agendamento no Windows Task Scheduler
REM Copie este ficheiro para a pasta raiz do projeto

REM Definir diretório de trabalho
cd /d %~dp0

REM Ativar ambiente virtual (se usar)
call venv\Scripts\activate.bat

REM Executar comando principal com timestamps
echo [%date% %time%] Iniciando recolha de dados... >> logs\sync.log

REM Modo incremental - coleta dados novos
python main.py --favorites --fetch-mode incremental --fetch-only >> logs\sync.log 2>&1

REM Verificar se houve erro
if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] ERRO ao recolher dados >> logs\error.log
) else (
    echo [%date% %time%] Recolha concluída com sucesso >> logs\sync.log
)

REM Gerar relatório apenas nos fins de semana
REM (pode ser adaptado para outra lógica)

echo [%date% %time%] Fim >> logs\sync.log
