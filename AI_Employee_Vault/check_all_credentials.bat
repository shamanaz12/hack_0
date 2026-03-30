@echo off
echo ============================================
echo   Credentials Setup Checker
echo ============================================
echo.

cd /d "%~dp0"

python check_credentials.py

echo.
echo ============================================
echo   Next Steps:
echo ============================================
echo.
echo If credentials.json is missing:
echo   1. Go to: https://console.cloud.google.com/
echo   2. Create a new project
echo   3. Enable Gmail API
echo   4. Create OAuth 2.0 credentials (Desktop app)
echo   5. Download and save as: credentials.json
echo.
echo If token.pickle is missing:
echo   Run: python gmail_auth.py
echo.
echo If MCP credentials are missing:
echo   Edit: start_mcp_with_credentials.bat
echo   Add your Gmail App Password
echo.
echo ============================================
pause
