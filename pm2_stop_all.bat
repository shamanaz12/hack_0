@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    PM2 - STOP ALL SERVICES
echo ============================================================
echo.

cd /d C:\Users\AA\Desktop\gold_tier

where pm2 >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: PM2 is not installed!
    pause
    exit /b 1
)

echo Stopping all services...
pm2 stop ecosystem.config.js

echo.
echo Done!
pm2 list

pause
