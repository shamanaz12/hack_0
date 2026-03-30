@echo off
echo ============================================
echo   WSL Installation Script
echo ============================================
echo.
echo This script will install everything in WSL (Linux)
echo.
echo Step 1: Check if WSL is enabled...
wsl --version >nul 2>&1
if errorlevel 1 (
    echo WSL is not enabled!
    echo.
    echo To enable WSL, run this in PowerShell as Administrator:
    echo   wsl --install
    echo.
    pause
    exit /b 1
)
echo WSL is available!
echo.

echo Step 2: Running installation in WSL...
echo.
wsl bash -c "
echo 'Updating packages...'
sudo apt update -y

echo 'Installing Python3 and pip...'
sudo apt install -y python3 python3-pip

echo 'Installing dependencies...'
cd /mnt/c/Users/AA/Desktop/h.p_hack_0/AI_Employee_Vault
pip3 install -r requirements.txt
pip3 install -r requirements_gmail.txt
pip3 install -r requirements_mcp.txt

echo ''
echo 'Setup Complete!'
"

echo.
echo ============================================
echo   WSL Installation Complete!
echo ============================================
echo.
echo Next: Run the setup script in WSL:
echo   wsl bash /mnt/c/Users/AA/Desktop/h.p_hack_0/AI_Employee_Vault/install_wsl.sh
echo.
pause
