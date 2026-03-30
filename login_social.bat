@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    LOGIN TO FACEBOOK & INSTAGRAM
echo ============================================================
echo.
echo   Opening login pages...
echo.
echo   IMPORTANT: Login to BOTH accounts to enable auto-posting
echo.

REM Open Facebook Login
echo Opening Facebook Login...
start https://www.facebook.com/login

echo.
echo   Facebook Login Instructions:
echo   1. Enter your email/phone
echo   2. Enter your password
echo   3. Click Login
echo.

timeout /t 5 /nobreak >nul

REM Open Instagram Login
echo Opening Instagram Login...
start https://www.instagram.com/accounts/login/

echo.
echo   Instagram Login Instructions:
echo   1. Username: shamaansari5576
echo   2. Enter your password
echo   3. Click Log In
echo.

timeout /t 5 /nobreak >nul

echo.
echo ============================================================
echo   NEXT STEP: Configure Credentials in .env
echo ============================================================
echo.
echo   After logging in successfully:
echo.
echo   1. Open: C:\Users\AA\Desktop\gold_tier\.env
echo.
echo   2. Add your credentials:
echo      FACEBOOK_EMAIL=your_facebook_email
echo      FACEBOOK_PASSWORD=your_facebook_password
echo      INSTAGRAM_PASSWORD=your_instagram_password
echo.
echo   3. Save the file
echo.
echo   4. Run: start_watcher.bat
echo.
echo ============================================================
echo.
pause
