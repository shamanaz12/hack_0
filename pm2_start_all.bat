@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    PM2 - START ALL SERVICES
echo    Gold Tier Process Management
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

echo Starting all Gold Tier services...
echo.

REM Start all services
pm2 start ecosystem.config.js

echo.
echo ============================================================
echo   Services Started!
echo ============================================================
echo.
echo View status: pm2 list
echo View logs:   pm2 logs
echo Monitor:     pm2 monit
echo.

REM Show status
pm2 list

echo.
pause
