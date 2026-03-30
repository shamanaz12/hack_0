@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    GOLD TIER - RUN ALL PLATFORMS
echo    Gmail + WhatsApp + Facebook + Instagram
echo ============================================================
echo.

cd /d C:\Users\AA\Desktop\gold_tier

REM Create folders
if not exist "logs" mkdir logs
if not exist "posts" mkdir posts

echo [1/4] Starting Gmail Watcher...
if exist ".venv\Scripts\python.exe" (
    start "Gmail" .venv\Scripts\python.exe gmail_watcher.py --once
) else (
    start "Gmail" python gmail_watcher.py --once
)
timeout /t 2 /nobreak >nul

echo [2/4] Opening Facebook and Instagram...
if exist ".venv\Scripts\python.exe" (
    start "Social" .venv\Scripts\python.exe open_social_media.py
) else (
    start "Social" python open_social_media.py
)
timeout /t 3 /nobreak >nul

echo [3/4] Generating Post...
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%%a"
echo Transform your business with Gold Tier automation! > posts\post_%date:~-4,4%%date:~-7,2%%date:~-10,2%.txt
echo Post created in posts\ folder
timeout /t 2 /nobreak >nul

echo [4/4] Opening Logs...
start logs

echo.
echo ============================================================
echo    ALL SERVICES STARTED!
echo ============================================================
echo    - Gmail Watcher running
echo    - Facebook/Instagram opening in browser
echo    - Post ready in posts\ folder
echo    - Logs folder opened
echo ============================================================
pause
