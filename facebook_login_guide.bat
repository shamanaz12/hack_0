@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    FACEBOOK LOGIN GUIDE
echo    Step-by-Step Instructions
echo ============================================================
echo.
echo   STEP 1: Opening Facebook Login Page...
echo.

start https://www.facebook.com/login

echo   Facebook login page khul gaya hai
echo.
echo   ============================================================
echo   STEP 2: Login Karein
echo   ============================================================
echo.
echo   1. Email/Phone mein likhein: naz sheikh
echo.
echo   2. Password mein likhein: uzain786
echo.
echo   3. "Log In" button click karein
echo.
echo   4. IMPORTANT: "Keep me logged in" CHECKBOX check karein!
echo.
echo   ============================================================
echo   STEP 3: Save Password
echo   ============================================================
echo.
echo   Agar browser puche "Save Password?":
echo   - "Save" ya "Yes" click karein
echo.
echo   ============================================================
echo   STEP 4: Verify Login
echo   ============================================================
echo.
echo   Jab aapki profile khul jaye:
echo   - Aap successfully logged in hain!
echo   - Browser ne session save kar liya hai
echo.
echo   ============================================================
echo.
echo   NEXT TIME:
echo   ============
echo   Jab bhi aap ye script chalayenge:
echo   - Facebook automatically login ho jayega
echo   - No password needed!
echo.
echo   ============================================================
echo.
echo   Press any key to continue...
pause >nul

REM Wait 10 seconds for user to login
echo.
echo   Waiting 10 seconds for you to login...
timeout /t 10 /nobreak >nul

REM Open Instagram after login
echo.
echo   Opening Instagram...
start https://www.instagram.com/shamaansari5576/

echo.
echo   Done! Both platforms opened.
echo.
pause
