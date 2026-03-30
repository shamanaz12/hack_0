@echo off
echo ============================================
echo   Silver Tier - File Watcher (MCP)
echo ============================================
echo.
echo This watcher monitors Drop_Folder and automatically
echo copies new files to Silver_Tier/inbox/
echo.
echo Drop Folder: C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Drop_Folder
echo Destination: Silver_Tier/inbox/
echo.
echo Press Ctrl+C to stop the watcher
echo.
pause

cd /d "%~dp0"
python silver_tier_watcher.py
