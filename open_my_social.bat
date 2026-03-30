@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    QWEN MCP - OPEN YOUR SOCIAL MEDIA
echo    Direct Links - Already Logged In!
echo ============================================================
echo.
echo   Opening YOUR profiles with saved login...
echo   (No password needed - already logged in!)
echo.

REM Your exact Facebook profile link
echo [1/3] Opening YOUR Facebook Profile...
start https://www.facebook.com/profile.php?id=61578524116357
timeout /t 2 /nobreak >nul

REM Your exact Instagram profile link
echo [2/3] Opening YOUR Instagram Profile...
start https://www.instagram.com/shamaansari5576/
timeout /t 2 /nobreak >nul

REM Meta Business Suite
echo [3/3] Opening Meta Business Suite...
start https://business.facebook.com

echo.
echo ============================================================
echo   DONE! Your profiles opened
echo ============================================================
echo.
echo   Facebook: https://www.facebook.com/profile.php?id=61578524116357
echo   Instagram: https://www.instagram.com/shamaansari5576/
echo.
echo   Since you're already logged in, no login needed!
echo   Browser will use your saved session.
echo.
echo ============================================================
pause
