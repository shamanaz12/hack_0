@echo off
REM =============================================
REM Odoo MCP Server - Complete Setup Script
REM =============================================

echo.
echo =============================================
echo   ODOO MCP SERVER - SETUP
echo =============================================
echo.

REM Step 1: Check if Docker is running
echo [1/5] Checking Docker...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo Docker is running OK.

REM Step 2: Install Python dependencies
echo.
echo [2/5] Installing Python dependencies...
pip install requests python-dotenv -q
echo Dependencies installed.

REM Step 3: Check Odoo status
echo.
echo [3/5] Checking Odoo containers...
docker ps --filter "name=odoo" --format "{{.Names}}" | findstr "odoo" >nul
if errorlevel 1 (
    echo WARNING: Odoo containers not found!
    echo Starting Odoo with docker-compose...
    cd /d "%~dp0odoo-docker"
    docker-compose up -d
    cd /d "%~dp0"
) else (
    echo Odoo containers found.
)

REM Step 4: Wait for Odoo to be ready
echo.
echo [4/5] Waiting for Odoo to start (30 seconds)...
timeout /t 30 /nobreak >nul

REM Step 5: Test MCP server
echo.
echo [5/5] Testing MCP server...
python test_mcp_quick.py

echo.
echo =============================================
echo   SETUP COMPLETE!
echo =============================================
echo.
echo Next steps:
echo 1. Make sure Odoo is accessible at http://localhost:8069
echo 2. Create database if not already done
echo 3. Run: python odoo_mcp_test_client.py
echo.
pause
