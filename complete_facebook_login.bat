@echo off
echo ============================================================
echo   FACEBOOK 2FA LOGIN HELPER
echo ============================================================
echo.
echo  This will open Facebook in a browser window.
echo.
echo  YOU NEED TO:
echo  1. Enter your 2FA code when prompted
echo  2. Complete the login manually
echo  3. Once logged in, the session will be saved
echo.
echo  Press Ctrl+C to cancel, or
echo.
pause
python facebook_2fa_handler.py
pause
