@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    OPEN SOCIAL MEDIA PROFILES
echo ============================================================
echo.
echo   Opening Facebook and Instagram in your browser...
echo.

REM Open Facebook
echo Opening Facebook...
start https://www.facebook.com/profile.php?id=61578524116357

REM Wait 2 seconds
timeout /t 2 /nobreak >nul

REM Open Instagram
echo Opening Instagram...
start https://www.instagram.com/shamaansari5576

REM Wait 2 seconds
timeout /t 2 /nobreak >nul

REM Open Meta Business Suite (for managing both)
echo Opening Meta Business Suite...
start https://business.facebook.com

echo.
echo ============================================================
echo   All profiles opened in your browser!
echo ============================================================
echo.
pause
