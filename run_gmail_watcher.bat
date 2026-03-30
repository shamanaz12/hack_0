@echo off
echo ================================================
echo Silver Tier Gmail Watcher
echo ================================================
echo.
echo Starting Gmail watcher...
echo.
python "%~dp0gmail_watcher.py" --once
echo.
echo ================================================
echo Done! Check AI_Employee_Vault\Silver_Tier\Needs_Action\ folder
echo ================================================
pause
