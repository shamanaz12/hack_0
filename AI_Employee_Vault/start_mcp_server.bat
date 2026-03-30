@echo off
set SMTP_HOST=localhost
set SMTP_PORT=587
set SMTP_USERNAME=testuser
set SMTP_PASSWORD=testpass
set SMTP_USE_TLS=false

echo Environment variables set for testing:
echo SMTP_HOST=%SMTP_HOST%
echo SMTP_PORT=%SMTP_PORT%
echo SMTP_USERNAME=%SMTP_USERNAME%
echo SMTP_PASSWORD=%SMTP_PASSWORD%
echo SMTP_USE_TLS=%SMTP_USE_TLS%

echo.
echo Starting MCP Email Server...
python mcp_email_server.py