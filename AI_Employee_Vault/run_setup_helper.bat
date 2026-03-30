@echo off
setlocal

echo Running Gmail API Setup Helper...
echo This script will guide you through the Gmail API setup process.
echo.

python "%~dp0setup_helper.py"

echo.
echo Setup helper completed.
pause