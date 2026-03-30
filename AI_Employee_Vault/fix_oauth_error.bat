@echo off
setlocal

echo Fixing OAuth Client Error
echo =========================
echo.
echo The error "Authorization Error: The OAuth client was not found" occurs because
echo the credentials.json file doesn't contain valid OAuth credentials from Google Cloud Console.
echo.
echo Please follow these steps to fix the issue:
echo.
echo 1. Go to https://console.cloud.google.com/
echo 2. Create a new project or select an existing one
echo 3. Enable the Gmail API for your project
echo 4. Create OAuth 2.0 credentials for a Desktop application
echo 5. Download the credentials JSON file and save it as 'credentials.json'
echo 6. Place the file in this folder: C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault
echo.
echo After completing these steps, run the setup_helper.py script again:
echo.
echo python setup_helper.py
echo.
echo This will guide you through the authentication process.
echo.
echo Opening Google Cloud Console in your browser...
start "" "https://console.cloud.google.com/"
echo.
echo Press any key to exit...
pause >nul