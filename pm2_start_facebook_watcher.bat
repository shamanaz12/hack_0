@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    PM2 - START FACEBOOK WATCHER
echo    Force Re-execution Enabled
echo ============================================================
echo.

cd /d C:\Users\AA\Desktop\gold_tier

REM Check if PM2 is installed
where pm2 >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: PM2 is not installed!
    echo.
    echo Install with: npm install -g pm2
    echo.
    pause
    exit /b 1
)

echo Starting Facebook & Instagram Watcher...
echo.

REM Start Facebook watcher with force restart
pm2 restart ecosystem.config.js --only facebook-watcher --force

echo.
echo ============================================================
echo   Facebook Watcher Status
echo ============================================================
echo.

REM Show status
pm2 status facebook-watcher

echo.
echo View logs: pm2 logs facebook-watcher
echo.
pause
