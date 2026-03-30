@echo off
echo ============================================
echo   Bronze Tier - Email Processor
echo ============================================
echo.

cd /d "%~dp0"

echo Current Status:
python bronze_tier_processor.py status

echo.
echo Options:
echo   1. Process inbox (move to Needs_Action)
echo   2. Mark task as done
echo   3. Categorize by skill
echo   4. Refresh status
echo   5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Processing inbox...
    python bronze_tier_processor.py process
    pause
    goto :menu
)

if "%choice%"=="2" (
    echo.
    set /p filename="Enter filename to mark as done: "
    python bronze_tier_processor.py done "%filename%"
    pause
    goto :menu
)

if "%choice%"=="3" (
    echo.
    set /p filename="Enter filename to categorize: "
    echo Categories: email_campaigns, customer_support, meetings, sales, hr, finance, general
    set /p category="Enter category: "
    python bronze_tier_processor.py categorize "%filename%" "%category%"
    pause
    goto :menu
)

if "%choice%"=="4" (
    cls
    goto :start
)

if "%choice%"=="5" (
    exit /b
)

echo Invalid choice!
pause

:menu
cls
goto :start

:start
