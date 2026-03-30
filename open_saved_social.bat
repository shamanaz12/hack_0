@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    OPEN FACEBOOK & INSTAGRAM - SAVED SESSION
echo    No Password Needed - Browser Auto-Login
echo ============================================================
echo.
echo   Opening with your browser's saved session...
echo   (If logged in before, no login needed!)
echo.

REM Open Facebook Business Page
echo Opening Facebook Business...
start https://business.facebook.com

timeout /t 3 /nobreak >nul

REM Open Facebook Profile
echo Opening Facebook Profile...
start https://www.facebook.com/profile.php?id=61578524116357

timeout /t 2 /nobreak >nul

REM Open Instagram
echo Opening Instagram...
start https://www.instagram.com/shamaansari5576/

timeout /t 2 /nobreak >nul

REM Open Meta Business Suite
echo Opening Meta Business Suite...
start https://business.facebook.com/overview

echo.
echo ============================================================
echo   DONE! All platforms opened
echo ============================================================
echo.
echo   If browser asks for login:
echo   1. Check "Remember me" when logging in
echo   2. Next time it will open automatically!
echo.
pause
