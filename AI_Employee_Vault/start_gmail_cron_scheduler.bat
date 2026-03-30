@echo off
setlocal

echo Installing required packages...
pip install -r "%~dp0requirements_cron.txt"

echo Starting Gmail Watcher Cron Scheduler...
echo This script will run gmail_poller check every 5 minutes.
echo Press CTRL+C to stop the scheduler.

python "%~dp0gmail_cron_scheduler.py"

pause