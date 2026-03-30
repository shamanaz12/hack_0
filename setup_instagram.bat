@echo off
chcp 65001 >nul
cls
echo ============================================================
echo      INSTAGRAM TOKEN SETUP - @shamaansari5576
echo ============================================================
echo   Yeh script aap ko Instagram API Token lene mein madad
echo   karegi step-by-step
echo.
echo   INSTAGRAM: @shamaansari5576
echo   PROFILE: https://www.instagram.com/shamaansari5576
echo ============================================================
echo.
pause
echo.
echo ============================================================
echo   STEP 1: Facebook Graph API Explorer Open Karein
echo ============================================================
echo.
echo   Opening browser...
start https://developers.facebook.com/tools/explorer/
echo.
echo   Graph API Explorer khul gaya hoga!
echo.
echo   Ab ye karein:
echo   1. Facebook login karein
echo   2. Application select karein
echo.
pause

echo.
echo ============================================================
echo   STEP 2: Permissions Select Karein
echo ============================================================
echo.
echo   "Get Token" -^> "Get User Access Token" click karein
echo.
echo   Ye sab permissions SELECT karein:
echo     [x] instagram_basic
echo     [x] instagram_content_publish  
echo     [x] pages_read_engagement
echo     [x] pages_manage_engagement
echo     [x] pages_show_list
echo.
pause

echo.
echo ============================================================
echo   STEP 3: Token Generate Karein
echo ============================================================
echo.
echo   1. "Generate Access Token" button click karein
echo   2. Facebook permission dialog aayega
echo   3. "Continue" click karein
echo   4. Saare permissions allow karein
echo.
pause

echo.
echo ============================================================
echo   STEP 4: Token Copy Karein ^(IMPORTANT!^)
echo ============================================================
echo.
echo   Access Token box mein ek lamba code hoga.
echo   Example: EAAGm0P4ZCqo0BOxxxxx...
echo.
echo   Us ko SELECT kar ke COPY kar lein!
echo.
pause

echo.
echo ============================================================
echo   STEP 5: Instagram Business ID Nikalein
echo ============================================================
echo.
echo   Graph API Explorer mein ye query chalayein:
echo.
echo   GET /me/accounts?fields=instagram_business_account
echo.
echo   "Submit" dabayein
echo.
echo   Response mein dikhega:
echo   {
echo     "data": [{
echo       "name": "Gold Tier",
echo       "id": "956241877582673",
echo       "instagram_business_account": {
echo         "id": "178414XXXXXXXXXX"  -- YE HAI BUSINESS ID
echo         "name": "shamaansari5576"
echo       }
echo     }]
echo   }
echo.
echo   Instagram Business ID COPY kar lein!
echo.
pause

echo.
echo ============================================================
echo   STEP 6: .env File Update Karein
echo ============================================================
echo.
echo   .env file edit karein:
echo     File: C:\Users\AA\Desktop\gold_tier\.env
echo.
echo   Ye lines dhundhein:
echo     INSTAGRAM_BUSINESS_ID=
echo     INSTAGRAM_ACCESS_TOKEN=
echo.
echo   Replace karein:
echo     INSTAGRAM_BUSINESS_ID=178414XXXXXXXXXX
echo     INSTAGRAM_ACCESS_TOKEN=EAAGm0P4ZCqo0BOxxxx...
echo.
echo   SAVE kar dein!
echo.
pause

echo.
echo ============================================================
echo   STEP 7: Test Karein
echo ============================================================
echo.
echo   Command prompt mein ye chalayein:
echo.
echo   python watcher\facebook_instagram_watcher.py --once --instagram-only
echo.
echo   Agar real posts dikhein toh SUCCESS!
echo.
pause

echo.
echo ============================================================
echo            SETUP COMPLETE!
echo ============================================================
echo.
echo   Instagram @shamaansari5576 ab ready hai!
echo.
echo   Quick Commands:
echo     python watcher\facebook_instagram_watcher.py --once
echo     python watcher\facebook_instagram_watcher.py
echo.
echo   Logs: logs\facebook_instagram_watcher.log
echo.
echo ============================================================
echo.
echo   Shukriya! Instagram integration complete ho gaya.
echo.
pause
