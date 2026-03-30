@echo off
REM Auto Processor - Start Gmail + WhatsApp Automatic Processor
REM This script starts the auto processor in the background

echo ============================================================
echo Auto Processor - Starting...
echo ============================================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Start auto processor
echo Starting Auto Processor...
echo Logs: logs\auto_processor.log
echo.
echo Press Ctrl+C to stop
echo ============================================================
echo.

python auto_processor.py

pause
