@echo off
echo ============================================================
echo   WhatsApp CLI - View Chats in Terminal
echo ============================================================
echo.
cd /d "%~dp0"
python whatsapp_cli.py --chats
echo.
pause
