@echo off
echo ============================================================
echo   Social Media CLI - Check Posts
echo ============================================================
echo.
cd /d "%~dp0"
python social_cli.py --all
echo.
pause
