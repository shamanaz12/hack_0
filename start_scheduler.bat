@echo off
REM ============================================================
REM Task Scheduler Starter
REM ============================================================
REM 
REM This script starts the task scheduler that:
REM 1. Runs Gmail watcher at scheduled intervals
REM 2. Runs WhatsApp watcher at scheduled intervals
REM 3. Runs orchestrator to process files
REM 4. Generates daily briefings (8 AM)
REM 5. Generates weekly reports (Monday 9 AM)
REM
REM Usage:
REM   start_scheduler.bat              - Run continuously
REM   start_scheduler.bat --status     - Show current status
REM   start_scheduler.bat --once       - Run all tasks once
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo Task Scheduler - Automatic Scheduling
echo ============================================================
echo.
echo Starting scheduler...
echo.
echo Scheduled Tasks:
echo   - Gmail Watcher (every 5 min)
echo   - WhatsApp Watcher (every 5 min)
echo   - Orchestrator (every 1 min)
echo   - Daily Briefing (8:00 AM)
echo   - Weekly Report (Monday 9:00 AM)
echo   - Cleanup (3:00 AM)
echo.
echo Press Ctrl+C to stop
echo.
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python or add it to PATH.
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Check if schedule library is installed
python -c "import schedule" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing schedule library...
    pip install schedule
) else (
    echo [OK] schedule library installed
)

echo.
echo ============================================================
echo Starting Scheduler...
echo ============================================================
echo.

REM Run scheduler
python scheduler.py %*

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Scheduler exited with error
    echo ============================================================
    echo.
    echo Check logs/scheduler.log for details
    pause
) else (
    echo.
    echo ============================================================
    echo Scheduler stopped successfully
    echo ============================================================
)
