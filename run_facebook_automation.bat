@echo off
echo ============================================================
echo   FACEBOOK AUTOMATION - ANTI-CAPTCHA VERSION
echo ============================================================
echo.
echo  This will run Facebook automation with:
echo  - Persistent browser profile (avoids CAPTCHA)
echo  - Session reuse (fast login)
echo  - Human-like timing
echo.
echo  Press Ctrl+C to cancel, or
echo.
pause

python facebook_playwright_anticaptcha.py

echo.
echo ============================================================
echo   AUTOMATION COMPLETE
echo ============================================================
echo.
echo  Your session has been saved.
echo  Next run will be even faster (session reuse).
echo.
pause
