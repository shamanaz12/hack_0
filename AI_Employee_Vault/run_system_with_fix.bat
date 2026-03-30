@echo off
setlocal

echo Starting Complete AI Employee Vault System with OAuth Fix
echo ========================================================
echo.

:: Check if credentials.json exists
if not exist "credentials.json" (
    echo [ERROR] credentials.json not found!
    echo.
    echo Please follow these steps to fix the OAuth error:
    echo 1. Go to https://console.cloud.google.com/
    echo 2. Create a new project or select an existing one
    echo 3. Enable the Gmail API for your project
    echo 4. Create OAuth 2.0 credentials for a Desktop application
    echo 5. Download the credentials JSON file and save it as 'credentials.json'
    echo 6. Place the file in this folder
    echo.
    echo Running fix guide...
    start "" "https://console.cloud.google.com/"
    echo.
    echo After setting up credentials, run this script again.
    pause
    exit /b 1
)

echo [OK] credentials.json found. Validating...
python validate_credentials.py

echo.
echo Starting system components...
echo.

:menu
echo Select an option:
echo 1. Run Gmail Authentication (Required for Gmail features)
echo 2. Run Gmail Cron Scheduler (Checks emails every 5 minutes)
echo 3. Run MCP Email Server (Sends emails via HTTP API)
echo 4. Run Complete System Setup
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Running Gmail Authentication...
    python -c "from gmail_auth import test_authentication; test_authentication()"
    echo.
    pause
    goto menu
) else if "%choice%"=="2" (
    echo.
    echo Starting Gmail Cron Scheduler (will run every 5 minutes)...
    echo Press Ctrl+C to stop the scheduler.
    python gmail_cron_scheduler.py
    echo.
    pause
    goto menu
) else if "%choice%"=="3" (
    echo.
    echo Starting MCP Email Server...
    echo Server will be available at http://localhost:5000
    echo Press Ctrl+C to stop the server.
    call setup_and_start_mcp_server.bat
    echo.
    pause
    goto menu
) else if "%choice%"=="4" (
    echo.
    echo Running Complete System Setup...
    python run_complete_system.py
    echo.
    pause
    goto menu
) else if "%choice%"=="5" (
    echo.
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please enter 1-5.
    echo.
    goto menu
)