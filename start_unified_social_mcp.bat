@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    UNIFIED SOCIAL MEDIA MCP SERVER
echo    Facebook + Instagram - NO TOKENS REQUIRED!
echo ============================================================
echo.
echo   This server uses browser automation instead of API tokens
echo.
echo   Features:
echo     - No API tokens needed
echo     - Real browser automation (Playwright)
echo     - Session persistence (login once)
echo     - Works with Facebook AND Instagram
echo     - Multiple MCP servers in one
echo.
echo ============================================================
echo.

REM Check if .venv exists
if exist ".venv\Scripts\python.exe" (
    echo Using virtual environment...
    .venv\Scripts\python.exe mcp_servers\unified_social_mcp.py
) else (
    echo Using system Python...
    python mcp_servers\unified_social_mcp.py
)

echo.
echo ============================================================
echo   Server stopped
echo ============================================================
pause
