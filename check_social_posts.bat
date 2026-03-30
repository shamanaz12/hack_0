@echo off
echo ============================================================
echo   Facebook & Instagram - Post Status
echo ============================================================
echo.
echo Checking logs for recent activity...
echo.
cd /d "%~dp0"

echo ============================================================
echo FACEBOOK ACTIVITY (from logs)
echo ============================================================
type logs\facebook_watcher.log 2>nul | findstr /C:"[OK]" /C:"[NEW" /C:"Post" | more +0
echo.

echo ============================================================
echo INSTAGRAM ACTIVITY (from logs)
echo ============================================================
type logs\facebook_instagram_watcher.log 2>nul | findstr /C:"[OK]" /C:"[NEW" /C:"Media" | more +0
echo.

echo ============================================================
echo SOCIAL MCP ACTIVITY
echo ============================================================
type logs\social_mcp.log 2>nul | findstr /C:"[OK]" /C:"Posted" /C:"Post" | more +0
echo.

pause
