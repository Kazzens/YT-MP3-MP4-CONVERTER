@echo off
cd /d "%~dp0"
title YouTube to MP3/MP4 Converter by KAZZEN

REM ─────────────── CREATE VENV IF NOT EXISTS ───────────────
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM ─────────────── ACTIVATE VENV ───────────────
call venv\Scripts\activate

REM ─────────────── CHECK AND INSTALL DEPENDENCIES ───────────────
echo Installing required packages...
pip install --disable-pip-version-check --no-warn-script-location -r requirements.txt >nul 2>&1

REM ─────────────── RUN APP ───────────────
echo Launching converter...
python main.py

pause
