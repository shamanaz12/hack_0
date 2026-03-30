@echo off
echo ============================================
echo   Silver Tier - Email Processor (MCP)
echo ============================================
echo.

cd /d "%~dp0"

echo Checking MCP Server status...
python -c "import requests; r=requests.get('http://localhost:5000/health', timeout=3); print('MCP Server: Online' if r.status_code==200 else 'MCP Server: Offline')" 2>nul || echo MCP Server: Offline

echo.
echo Current Status:
python silver_tier_processor.py status

echo.
echo Options:
echo   1. Process inbox (categorize into skills)
echo   2. Move from skills to Needs_Action
echo   3. Send auto-response (via MCP) + Move to Done
echo   4. Mark task as done (manual)
echo   5. Refresh status
echo   6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Processing inbox...
    python silver_tier_processor.py process
    pause
    goto :menu
)

if "%choice%"=="2" (
    echo.
    set /p filename="Enter filename to move to Needs_Action: "
    python silver_tier_processor.py move "%filename%"
    pause
    goto :menu
)

if "%choice%"=="3" (
    echo.
    set /p filename="Enter filename to send auto-response: "
    python silver_tier_processor.py respond "%filename%"
    pause
    goto :menu
)

if "%choice%"=="4" (
    echo.
    set /p filename="Enter filename to mark as done: "
    python silver_tier_processor.py done "%filename%"
    pause
    goto :menu
)

if "%choice%"=="5" (
    cls
    goto :start
)

if "%choice%"=="6" (
    exit /b
)

echo Invalid choice!
pause

:menu
cls
goto :start

:start
