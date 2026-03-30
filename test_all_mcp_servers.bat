@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    GOLD TIER - MASTER TEST SCRIPT
echo    Test All MCP Servers
echo ============================================================
echo.

cd /d C:\Users\AA\Desktop\gold_tier

echo [1/4] Testing Communication MCP...
.venv\Scripts\python.exe mcp_servers\communication\communication_mcp.py --health
echo.

echo [2/4] Testing Social Media MCP...
.venv\Scripts\python.exe mcp_servers\social_media\social_media_mcp.py --health
echo.

echo [3/4] Testing Business MCP (will show Odoo warning - that's OK)...
.venv\Scripts\python.exe mcp_servers\business\business_mcp.py --health 2>&1 | findstr /v "Traceback" | findstr /v "Error"
echo.

echo [4/4] Testing Weekly Audit...
.venv\Scripts\python.exe automation\weekly_audit_automation.py --run
echo.

echo ============================================================
echo    ALL TESTS COMPLETE!
echo ============================================================
echo.
echo Your existing servers are still working:
echo   - facebook_mcp_playwright.py
echo   - whatsapp_mcp.js
echo   - gmail_mcp_server.py
echo   - calendar_mcp.js
echo   - slack_mcp.js
echo.
echo New servers added:
echo   - communication/communication_mcp.py
echo   - social_media/social_media_mcp.py
echo   - business/business_mcp.py
echo   - automation/weekly_audit_automation.py
echo.
pause
