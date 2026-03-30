@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    GOLD TIER - RUN ALL PLATFORMS AT ONCE
echo    Gmail + WhatsApp + Facebook + Instagram
echo ============================================================
echo.
echo   Starting ALL automation services...
echo.
echo   This will:
echo   ✓ Check Gmail for new emails
echo   ✓ Check WhatsApp for messages
echo   ✓ Post to Facebook
echo   ✓ Post to Instagram
echo.
echo   Please wait...
echo ============================================================
echo.

cd /d C:\Users\AA\Desktop\gold_tier

REM Create logs folder if not exists
if not exist "logs" mkdir logs
if not exist "posts" mkdir posts

echo [1/6] Starting Gmail Watcher...
echo ─────────────────────────────────────────────────────────────
if exist ".venv\Scripts\python.exe" (
    start "Gmail Watcher" /min .venv\Scripts\python.exe gmail_watcher.py --once
) else (
    start "Gmail Watcher" /min python gmail_watcher.py --once
)
echo ✓ Gmail Watcher started
echo.
timeout /t 2 /nobreak >nul

echo [2/6] Starting WhatsApp Automation...
echo ─────────────────────────────────────────────────────────────
if exist "whatsapp_mcp.js" (
    start "WhatsApp MCP" /min node whatsapp_mcp.js
    echo ✓ WhatsApp MCP started
) else (
    echo ⚠ WhatsApp MCP not found
)
echo.
timeout /t 2 /nobreak >nul

echo [3/6] Opening Facebook & Instagram...
echo ─────────────────────────────────────────────────────────────
if exist ".venv\Scripts\python.exe" (
    start "Social Media" .venv\Scripts\python.exe open_social_media.py
) else (
    start "Social Media" python open_social_media.py
)
echo ✓ Browser opening Facebook & Instagram
echo.
timeout /t 3 /nobreak >nul

echo [4/6] Generating AI Posts...
echo ─────────────────────────────────────────────────────────────
set /a rand=%random% %% 5
if %rand%==0 set "post=Transform your business with Gold Tier automation! 🚀"
if %rand%==1 set "post=Success is the sum of small efforts repeated day in and day out! 💪"
if %rand%==2 set "post=Innovation distinguishes between a leader and a follower! ✨"
if %rand%==3 set "post=Building bridges to success, one step at a time! 🌉"
if %rand%==4 set "post=Your trusted partner in business excellence worldwide! 🌍"

echo Generated Post:
echo %post%
echo.
echo #GoldTier #Business #Success #Automation
echo.

REM Save post
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,4%%dt:~4,2%%dt:~6,2%_%dt:~8,2%%dt:~10,2%"
echo %post% > posts\auto_post_%timestamp%.txt
echo ✓ Post saved to posts\auto_post_%timestamp%.txt
echo.
timeout /t 2 /nobreak >nul

echo [5/6] Starting Facebook Watcher...
echo ─────────────────────────────────────────────────────────────
if exist ".venv\Scripts\python.exe" (
    start "FB Watcher" /min .venv\Scripts\python.exe watcher\facebook_instagram_watcher.py --once
) else (
    start "FB Watcher" /min python watcher\facebook_instagram_watcher.py --once
)
echo ✓ Facebook Watcher started
echo.
timeout /t 2 /nobreak >nul

echo [6/6] Opening Logs Folder...
echo ─────────────────────────────────────────────────────────────
start logs
echo ✓ Logs folder opened
echo.

echo ============================================================
echo    ALL SERVICES STARTED!
echo ============================================================
echo.
echo   Status:
echo   ✓ Gmail Watcher      - Running
echo   ✓ WhatsApp MCP       - Running
echo   ✓ Facebook/Instagram - Opening in browser
echo   ✓ AI Post Generated  - Ready to post
echo   ✓ Facebook Watcher   - Running
echo   ✓ Logs Folder        - Opened
echo.
echo   Next Steps:
echo   1. Copy the generated post from posts\ folder
echo   2. Paste in Facebook & Instagram browser windows
echo   3. Click Post on each platform
echo.
echo   Check logs\ folder for activity logs
echo ============================================================
echo.
pause
