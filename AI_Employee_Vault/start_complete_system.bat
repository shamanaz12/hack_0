@echo off
setlocal

echo Starting Complete AI Employee Vault System...
echo.

cd /d "C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault"

echo Checking for required files...
if not exist "credentials.json" (
    echo Warning: credentials.json not found. Gmail API will not work until you set this up.
    echo Please follow the instructions in GMAIL_SETUP_GUIDE.md
    pause
    exit /b 1
)

echo All required files found.
echo.

echo Starting the complete system setup...
python "run_complete_system.py"

echo.
echo System setup completed.
pause