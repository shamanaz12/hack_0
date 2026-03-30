@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    OPEN FACEBOOK & INSTAGRAM - NO CAPTCHA
echo    Direct Browser Opening
echo ============================================================
echo.
echo   Opening in your DEFAULT browser (no automation = no CAPTCHA)
echo.

REM Open Facebook directly
echo Opening Facebook...
start https://www.facebook.com/profile.php?id=61578524116357

REM Wait 2 seconds
timeout /t 2 /nobreak >nul

REM Open Instagram directly
echo Opening Instagram...
start https://www.instagram.com/shamaansari5576/

REM Wait 2 seconds
timeout /t 2 /nobreak >nul

REM Open Meta Business Suite
echo Opening Meta Business Suite...
start https://business.facebook.com

echo.
echo ============================================================
echo   DONE! All platforms opened in your browser
echo ============================================================
echo.
echo   Login manually (no CAPTCHA issues!)
echo   Then copy posts from: posts\ folder
echo.
pause
