@echo off
setlocal

:: Set environment variables for MCP Email Server
set SMTP_HOST=smtp.gmail.com
set SMTP_PORT=587
set SMTP_USERNAME=shama20302022@gmail.com
set SMTP_PASSWORD=your_app_password_here
set SMTP_USE_TLS=true

echo Environment variables set:
echo SMTP_HOST=%SMTP_HOST%
echo SMTP_PORT=%SMTP_PORT%
echo SMTP_USERNAME=%SMTP_USERNAME%
echo SMTP_PASSWORD=%SMTP_PASSWORD%
echo SMTP_USE_TLS=%SMTP_USE_TLS%

echo.
echo Note: You need to replace 'your_app_password_here' with your actual Gmail App Password
echo.
echo To generate a Gmail App Password:
echo 1. Go to your Google Account settings
echo 2. Navigate to Security > 2-Step Verification > App passwords
echo 3. Generate a new app password for 'Mail'
echo 4. Replace 'your_app_password_here' with the 16-character app password
echo.

echo Starting MCP Email Server...
cd /d "C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault"
python mcp_email_server.py