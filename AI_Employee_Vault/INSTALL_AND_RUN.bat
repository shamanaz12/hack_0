@echo off
echo ============================================
echo   AI Employee Vault - Quick Setup
echo ============================================
echo.

cd /d "%~dp0"

echo Step 1: Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)
echo.

echo Step 2: Checking dependencies...
pip install -r requirements.txt -r requirements_gmail.txt -r requirements_mcp.txt --quiet
echo Dependencies installed!
echo.

echo Step 3: Checking credentials.json...
if not exist "credentials.json" (
    echo.
    echo IMPORTANT: You need credentials.json file
    echo.
    echo Follow these steps:
    echo 1. Go to: https://console.cloud.google.com/
    echo 2. Create a NEW PROJECT (name it: AI-Employee-Vault)
    echo 3. Enable Gmail API
    echo 4. Go to: APIs ^& Services ^> Credentials
    echo 5. Click: Create Credentials ^> OAuth 2.0 Client IDs
    echo 6. First configure OAuth Consent Screen:
    echo    - Select: External
    echo    - App name: AI Employee Vault
    echo    - User support email: your-email@gmail.com
    echo    - Developer contact: your-email@gmail.com
    echo    - Click Save and Continue (skip scopes and test users)
    echo 7. Create OAuth 2.0 Client IDs:
    echo    - Application type: Desktop app
    echo    - Name: AI Employee Desktop
    echo    - Click Create
    echo 8. Download the JSON file
    echo 9. Rename it to: credentials.json
    echo 10. Place it in this folder:
    echo     C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault
    echo.
    pause
) else (
    echo credentials.json found!
    echo.
)

echo Step 4: Testing Gmail Authentication...
echo.
echo This will open a browser window for you to sign in to Google.
echo After signing in, you will be asked to allow permissions.
echo Click "Allow" to continue.
echo.
pause
python gmail_auth.py
if errorlevel 1 (
    echo.
    echo Authentication failed. Please check your credentials.json
    pause
    exit /b 1
)
echo.

echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo Next Steps:
echo 1. To receive emails from Gmail, run:
echo    start_gmail_watcher.bat
echo.
echo 2. To send emails via MCP server, you need Gmail App Password
echo    See: GMAIL_APP_PASSWORD_SETUP.md
echo.
echo 3. To start MCP server, run:
echo    start_mcp_with_credentials.bat
echo.
pause
