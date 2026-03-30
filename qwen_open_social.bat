@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    QWEN MCP - SOCIAL MEDIA OPENER
echo    Saved Session - No Password Needed!
echo ============================================================
echo.
echo   Opening Facebook & Instagram with saved browser session...
echo.
echo   If you logged in before, no login needed!
echo   Browser will auto-login with saved credentials.
echo.

REM Open Facebook Business
echo [1/4] Opening Facebook Business...
start https://business.facebook.com
timeout /t 2 /nobreak >nul

REM Open Facebook Profile
echo [2/4] Opening Facebook Profile...
start https://www.facebook.com/profile.php?id=61578524116357
timeout /t 2 /nobreak >nul

REM Open Instagram
echo [3/4] Opening Instagram...
start https://www.instagram.com/shamaansari5576/
timeout /t 2 /nobreak >nul

REM Open Meta Business Suite
echo [4/4] Opening Meta Business Suite...
start https://business.facebook.com/overview

echo.
echo ============================================================
echo   DONE! All platforms opened in your browser
echo ============================================================
echo.
echo   AUTO-LOGIN TIPS:
echo   ================
echo   1. If already logged in - Perfect! No action needed.
echo.
echo   2. If asked to login:
echo      - Login once
echo      - Check "Keep me logged in"
echo      - Next time: Auto-login!
echo.
echo   3. Browser saves your session for 30 days
echo.
echo ============================================================
pause
