@echo off
setlocal

echo Starting Gmail Watcher Scheduler...
echo This script will run gmail_poller.py every 5 minutes.
echo Press CTRL+C to stop the scheduler.

:loop
echo [%date% %time%] Running gmail_poller.py...
python "%~dp0gmail_poller.py"

if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] Error running gmail_poller.py
)

echo [%date% %time%] Waiting 5 minutes before next run...
timeout /t 300 /nobreak >nul

goto loop