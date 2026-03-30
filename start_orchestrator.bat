@echo off
REM ============================================================
REM Orchestrator - Fully Automatic Gmail + WhatsApp Processor
REM ============================================================
REM 
REM This script starts the fully automatic system that:
REM 1. Checks Gmail for new emails
REM 2. Checks WhatsApp for new messages
REM 3. Processes everything automatically using AI
REM 4. Moves completed items to Done folder
REM
REM Usage:
REM   start_orchestrator.bat              - Run continuously
REM   start_orchestrator.bat --once       - Process existing files once
REM   start_orchestrator.bat --status     - Show current status
REM   start_orchestrator.bat --help       - Show all options
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo Orchestrator - Fully Automatic Gmail + WhatsApp Processor
echo ============================================================
echo.
echo Starting automatic processing...
echo.
echo System will:
echo   1. Check Gmail for new emails
echo   2. Check WhatsApp for new messages  
echo   3. Process all files using AI (Ralph Loop)
echo   4. Move processed files to Done folder
echo.
echo Press Ctrl+C to stop
echo.
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python or add it to PATH.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Check if dependencies are installed
echo Checking dependencies...

python -c "import dashscope" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] dashscope not installed - Running in SIMULATED MODE
    echo          Install for real AI: pip install dashscope
) else (
    echo [OK] dashscope installed (AI enabled)
)

python -c "import watchdog" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] watchdog not installed - Using polling mode
    echo          Install for better performance: pip install watchdog
) else (
    echo [OK] watchdog installed (efficient file watching)
)

python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo [INFO] playwright not installed - WhatsApp monitoring disabled
    echo          Install for WhatsApp: pip install playwright
    echo          Then run: playwright install chromium
) else (
    echo [OK] playwright installed (WhatsApp enabled)
)

echo.
echo ============================================================
echo Starting Orchestrator...
echo ============================================================
echo.

REM Run orchestrator with all arguments
python orchestrator.py %*

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Orchestrator exited with error
    echo ============================================================
    echo.
    echo Check logs/orchestrator.log for details
    pause
) else (
    echo.
    echo ============================================================
    echo Orchestrator stopped successfully
    echo ============================================================
)
