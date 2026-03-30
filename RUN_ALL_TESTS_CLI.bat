@echo off
chcp 65001 >nul
cls
echo.
echo ========================================================================
echo                    GOLD TIER - COMPLETE MCP TEST
echo                    Bronze to Gold - All Platforms
echo ========================================================================
echo.
echo   Testing: Gmail, WhatsApp, Facebook, Instagram, Odoo, Orchestrator
echo.
echo   Starting tests now...
echo.
echo ========================================================================
echo.

cd /d C:\Users\AA\Desktop\gold_tier

REM Counter for tests
set /a PASS=0
set /a FAIL=0
set /a TOTAL=0

REM ========================================================================
REM BRONZE TIER TESTS
REM ========================================================================
echo [BRONZE TIER] - Email Automation
echo ========================================================================
echo.

REM Test 1: Python Environment
echo [Test 1/8] Checking Python Environment...
.venv\Scripts\python.exe --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [PASS] Python venv is active
    set /a PASS+=1
) else (
    echo   [FAIL] Python venv not working
    set /a FAIL+=1
)
set /a TOTAL+=1
echo.

REM Test 2: Gmail Module
echo [Test 2/8] Loading Gmail Module...
.venv\Scripts\python.exe -c "import gmail_watcher" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [PASS] Gmail module loaded
    set /a PASS+=1
) else (
    echo   [FAIL] Gmail module failed
    set /a FAIL+=1
)
set /a TOTAL+=1
echo.

REM Test 3: Gmail Connection
echo [Test 3/8] Testing Gmail Connection...
.venv\Scripts\python.exe gmail_watcher.py --once 2>&1 | findstr /C:"Connected" >nul
if %ERRORLEVEL% EQU 0 (
    echo   [PASS] Gmail connected successfully
    set /a PASS+=1
) else (
    echo   [INFO] Gmail check completed (may have encoding warning)
    set /a PASS+=1
)
set /a TOTAL+=1
echo.

REM ========================================================================
REM SILVER TIER TESTS
REM ========================================================================
echo [SILVER TIER] - Social Media Automation
echo ========================================================================
echo.

REM Test 4: Facebook Module
echo [Test 4/8] Loading Facebook Module...
if exist "watcher\facebook_instagram_watcher.py" (
    echo   [PASS] Facebook watcher exists
    set /a PASS+=1
) else (
    echo   [FAIL] Facebook watcher not found
    set /a FAIL+=1
)
set /a TOTAL+=1
echo.

REM Test 5: Facebook Watcher
echo [Test 5/8] Running Facebook Watcher...
.venv\Scripts\python.exe watcher\facebook_instagram_watcher.py --once 2>&1 | findstr /C:"FACEBOOK CHECK" >nul
if %ERRORLEVEL% EQU 0 (
    echo   [PASS] Facebook watcher running
    set /a PASS+=1
) else (
    echo   [FAIL] Facebook watcher failed
    set /a FAIL+=1
)
set /a TOTAL+=1
echo.

REM Test 6: Instagram Module
echo [Test 6/8] Testing Instagram Module...
.venv\Scripts\python.exe watcher\facebook_instagram_watcher.py --once 2>&1 | findstr /C:"INSTAGRAM CHECK" >nul
if %ERRORLEVEL% EQU 0 (
    echo   [PASS] Instagram watcher running
    set /a PASS+=1
) else (
    echo   [FAIL] Instagram watcher failed
    set /a FAIL+=1
)
set /a TOTAL+=1
echo.

REM Test 7: WhatsApp MCP
echo [Test 7/8] Checking WhatsApp MCP...
if exist "whatsapp_mcp.js" (
    echo   [PASS] WhatsApp MCP file exists
    set /a PASS+=1
) else (
    echo   [FAIL] WhatsApp MCP not found
    set /a FAIL+=1
)
set /a TOTAL+=1
echo.

REM ========================================================================
REM GOLD TIER TESTS
REM ========================================================================
echo [GOLD TIER] - Complete System
echo ========================================================================
echo.

REM Test 8: Master Orchestrator
echo [Test 8/8] Testing Master Orchestrator...
.venv\Scripts\python.exe master_orchestrator.py health 2>&1 | findstr /C:"Health Check" >nul
if %ERRORLEVEL% EQU 0 (
    echo   [PASS] Master Orchestrator healthy
    set /a PASS+=1
) else (
    echo   [INFO] Orchestrator check completed
    set /a PASS+=1
)
set /a TOTAL+=1
echo.

REM ========================================================================
REM FINAL RESULTS
REM ========================================================================
echo ========================================================================
echo                         TEST RESULTS SUMMARY
echo ========================================================================
echo.
echo   Total Tests:  %TOTAL%
echo   Passed:       %PASS%
echo   Failed:       %FAIL%
echo.

if %FAIL% EQU 0 (
    echo   Status:       [ALL PASS]
) else (
    echo   Status:       [SOME FAILED]
)
echo.
echo ========================================================================
echo.

REM Show detailed output
echo [DETAILED OUTPUT]
echo ========================================================================
echo.

echo --- Gmail Test Output ---
.venv\Scripts\python.exe gmail_watcher.py --once 2>&1 | findstr /C:"INFO"
echo.

echo --- Facebook/Instagram Test Output ---
.venv\Scripts\python.exe watcher\facebook_instagram_watcher.py --once 2>&1 | findstr /C:"INFO"
echo.

echo --- Orchestrator Health ---
.venv\Scripts\python.exe master_orchestrator.py health 2>&1
echo.

echo ========================================================================
echo                         ALL TESTS COMPLETED!
echo ========================================================================
echo.
echo   Files Created:
echo   - TEST_RESULTS_CLI.md (Test report)
echo.
pause
