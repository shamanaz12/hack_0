@echo off
REM ================================================================
REM GOLD TIER - QUICK START SCRIPT
REM ================================================================
REM For: Naz Sheikh - Gold Tier System
REM Last Updated: March 26, 2026
REM ================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║          GOLD TIER - QUICK START MENU                        ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║  Select an option:                                           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo  1. Configure System (Interactive Setup)
echo  2. Install Dependencies
echo  3. Start All Services
echo  4. Stop All Services
echo  5. Check Status
echo  6. Health Check
echo  7. Get Facebook Token (Step-by-Step)
echo  8. Run Weekly Audit
echo  9. Generate Reports
echo  10. Start Facebook MCP Only
echo  11. Start Instagram MCP Only
echo  12. Start Odoo MCP Only
echo  13. View Logs
echo  14. Exit
echo.

set /p choice="Enter your choice (1-14): "

if "%choice%"=="1" goto CONFIGURE
if "%choice%"=="2" goto INSTALL
if "%choice%"=="3" goto START_ALL
if "%choice%"=="4" goto STOP_ALL
if "%choice%"=="5" goto STATUS
if "%choice%"=="6" goto HEALTH
if "%choice%"=="7" goto FB_TOKEN
if "%choice%"=="8" goto AUDIT
if "%choice%"=="9" goto REPORTS
if "%choice%"=="10" goto START_FB
if "%choice%"=="11" goto START_IG
if "%choice%"=="12" goto START_ODOO
if "%choice%"=="13" goto LOGS
if "%choice%"=="14" goto EXIT

echo Invalid choice!
pause
goto END

:CONFIGURE
echo.
echo Starting Configuration Wizard...
python configure_system.py
pause
goto END

:INSTALL
echo.
echo Installing Python Dependencies...
pip install requests python-dotenv watchdog dashscope
echo.
echo Installing Node.js Dependencies...
call npm install express axios dotenv
echo.
echo Installation Complete!
pause
goto END

:START_ALL
echo.
echo Starting All Services...
python master_orchestrator.py start
pause
goto END

:STOP_ALL
echo.
echo Stopping All Services...
python master_orchestrator.py stop
pause
goto END

:STATUS
echo.
echo Checking Service Status...
python master_orchestrator.py status
pause
goto END

:HEALTH
echo.
echo Running Health Check...
python master_orchestrator.py health
pause
goto END

:FB_TOKEN
echo.
echo Starting Facebook Token Helper...
python get_facebook_token.py
pause
goto END

:AUDIT
echo.
echo Running Weekly Audit...
python master_orchestrator.py audit
pause
goto END

:REPORTS
echo.
echo Generating Reports...
python master_orchestrator.py report
pause
goto END

:START_FB
echo.
echo Starting Facebook MCP Server...
node facebook_mcp.js
pause
goto END

:START_IG
echo.
echo Starting Instagram MCP Server...
node instagram_mcp.js
pause
goto END

:START_ODOO
echo.
echo Starting Odoo MCP Server...
python odoo_mcp_server.py
pause
goto END

:LOGS
echo.
echo Opening Logs Folder...
start logs
pause
goto END

:EXIT
echo.
echo Thank you for using Gold Tier System!
echo.
goto END

:END
