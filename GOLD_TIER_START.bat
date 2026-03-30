@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    GOLD TIER - QUICK START MENU
echo    Facebook + Instagram + All Services
echo ============================================================
echo.
echo  SOCIAL MEDIA (NEW):
echo  1. Generate AI Post
echo  2. Open Facebook & Instagram (No CAPTCHA)
echo  3. Run Social Media Watcher
echo  4. Run Autonomous Agent
echo.
echo  MAIN SERVICES:
echo  5. Start All Services
echo  6. Stop All Services
echo  7. Check Status
echo  8. Health Check
echo.
echo  INDIVIDUAL SERVICES:
echo  9. Start Facebook MCP
echo  10. Start Instagram MCP
echo  11. Start Odoo MCP
echo  12. Start Unified Social MCP
echo.
echo  UTILITIES:
echo  13. View Logs
echo  14. Open Posts Folder
echo  15. Exit
echo.

set /p choice="Enter your choice (1-15): "

if "%choice%"=="1" goto GENERATE_POST
if "%choice%"=="2" goto OPEN_SOCIAL
if "%choice%"=="3" goto WATCHER
if "%choice%"=="4" goto AUTONOMOUS
if "%choice%"=="5" goto START_ALL
if "%choice%"=="6" goto STOP_ALL
if "%choice%"=="7" goto STATUS
if "%choice%"=="8" goto HEALTH
if "%choice%"=="9" goto START_FB
if "%choice%"=="10" goto START_IG
if "%choice%"=="11" goto START_ODOO
if "%choice%"=="12" goto START_UNIFIED
if "%choice%"=="13" goto LOGS
if "%choice%"=="14" goto POSTS
if "%choice%"=="15" goto EXIT

echo Invalid choice!
pause
goto END

:GENERATE_POST
echo.
echo Generating AI Post...
call generate_post.bat
goto END

:OPEN_SOCIAL
echo.
echo Opening Facebook & Instagram...
call open_facebook_direct.bat
goto END

:WATCHER
echo.
echo Running Social Media Watcher...
call run_watcher_once.bat
goto END

:AUTONOMOUS
echo.
echo Starting Autonomous Agent...
call run_autonomous_agent.bat
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

:START_UNIFIED
echo.
echo Starting Unified Social MCP...
python mcp_servers\social_localhost_mcp.py
pause
goto END

:LOGS
echo.
echo Opening Logs Folder...
start logs
pause
goto END

:POSTS
echo.
echo Opening Posts Folder...
if not exist "posts" mkdir posts
start posts
pause
goto END

:EXIT
echo.
echo Thank you for using Gold Tier System!
echo.
goto END

:END
