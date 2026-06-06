@echo off
REM Tarea diaria del organizador de Gmail (22:00).
REM Ajusta la ruta si moves la carpeta del proyecto.

cd /d "%~dp0"

REM Si usas un entorno virtual, descomenta la linea siguiente:
REM call .venv\Scripts\activate.bat

REM Corrida diaria automatica: ejecucion real, solo lo nuevo del ultimo dia.
python gmail_organizer.py --execute --since 1d >> logs\cron.log 2>&1
