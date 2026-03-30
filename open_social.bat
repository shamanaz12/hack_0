@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    OPEN SOCIAL MEDIA
echo    Facebook + Instagram + Meta Business Suite
echo ============================================================
echo.
echo   Opening in your default browser...
echo.

cd /d C:\Users\AA\Desktop\gold_tier

REM Activate venv if exists
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe open_social_media.py
) else (
    python open_social_media.py
)

echo.
echo ============================================================
echo   Done!
echo ============================================================
pause
