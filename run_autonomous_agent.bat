@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    QWEN AI - AUTONOMOUS SOCIAL MEDIA AGENT
echo    Auto Post Generation + Auto Posting
echo ============================================================
echo.
echo   This agent will:
echo   1. Generate posts using AI (or mock AI if no API key)
echo   2. Post to Facebook automatically
echo   3. Read and analyze posts
echo   4. Reply to comments
echo.
echo   Running in autonomous mode...
echo.

cd /d C:\Users\AA\Desktop\gold_tier

REM Activate venv
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe qwen_social_agent.py --run --duration 30
) else (
    python qwen_social_agent.py --run --duration 30
)

echo.
echo ============================================================
echo   Session Complete!
echo ============================================================
pause
