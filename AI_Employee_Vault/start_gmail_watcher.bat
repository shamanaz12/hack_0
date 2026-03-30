@echo off
echo Starting Gmail Watcher for AI Employee Vault...
echo.
echo Make sure you have set up your Google API credentials!
echo See GMAIL_WATCHER_README.md for setup instructions.
echo.
echo Press Ctrl+C to stop the service.
echo.
python gmail_poller.py
pause