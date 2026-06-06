@echo off
REM Tarea diaria del organizador de Gmail (22:00).
REM Ajusta la ruta si moves la carpeta del proyecto.

cd /d "%~dp0"

REM Si usas un entorno virtual, descomenta la linea siguiente:
REM call .venv\Scripts\activate.bat

REM Corrida diaria automatica: ejecucion real, desde la ultima corrida.
REM El script ya rota logs/cron.log internamente, asi que solo capturamos
REM errores tempranos en logs/startup.log.
python gmail_organizer.py --execute --since-last-run >> logs\startup.log 2>&1
