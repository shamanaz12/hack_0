@echo off
echo ============================================
echo   Bronze Tier - File Watcher
echo ============================================
echo.
echo This watcher monitors Drop_Folder and automatically
echo copies new files to Bronze_Tier/inbox/
echo.
echo Drop Folder: C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Drop_Folder
echo Destination: Bronze_Tier/inbox/
echo.
echo Press Ctrl+C to stop the watcher
echo.
pause

cd /d "%~dp0"
python bronze_tier_watcher.py
