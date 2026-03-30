@echo off
setlocal

:: Set environment variables for MCP Email Server
set SMTP_HOST=smtp.gmail.com
set SMTP_PORT=587
set SMTP_USERNAME=shama20302022@gmail.com
:: Replace 'your_actual_app_password' with your real app password
set SMTP_PASSWORD=your_gmail_app_password_here
set SMTP_USE_TLS=true

echo Starting MCP Email Server with your credentials...
echo.

:: Check if the password has been updated from the default
if "%SMTP_PASSWORD%"=="your_gmail_app_password_here" (
    echo ERROR: You need to update the SMTP_PASSWORD in this batch file!
    echo Please edit this file and replace 'your_gmail_app_password_here' with your real Gmail App Password
    echo.
    echo The file is located at: C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\start_mcp_with_credentials.bat
    echo.
    pause
    exit /b 1
)

echo Environment variables set successfully:
echo SMTP_HOST=%SMTP_HOST%
echo SMTP_PORT=%SMTP_PORT%
echo SMTP_USERNAME=%SMTP_USERNAME%
echo SMTP_PASSWORD=**************** (hidden for security)
echo SMTP_USE_TLS=%SMTP_USE_TLS%
echo.

echo Starting MCP Email Server...
cd /d "C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault"
python mcp_email_server.py

pause