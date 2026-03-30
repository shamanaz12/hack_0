# Gmail API Setup Guide

## Prerequisites
Before using the Gmail watcher, you need to complete these steps:

### 1. Enable Gmail API
1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Library"
4. Search for "Gmail API"
5. Click on "Gmail API" and then click "Enable"

### 2. Set up OAuth 2.0 Credentials
1. In the Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop Application" as the application type
4. Download the credentials JSON file
5. Rename the file to "credentials.json" and place it in the AI_Employee_Vault folder

### 3. Configure OAuth Consent Screen (if required)
1. In the Google Cloud Console, go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type and click "Create"
3. Fill in the app information (App name, User support email, Authorized domains, Developer contact information)
4. Add the required scopes for Gmail API (typically "..." scopes)
5. Add test users if your app is in testing mode
6. Save and continue

### 4. First-time Authorization
When you first run the gmail_poller.py script, it will:
1. Open a browser window asking you to sign in to your Google account
2. Request permission to access your Gmail data
3. Save the authorization token for future use

## Helper Script
Run the setup_helper.py script to guide you through the process:

```bash
python setup_helper.py
```

## Important Security Notes
- Keep your credentials.json file secure and never share it
- The first time you run the script, you'll need to authenticate through Google's OAuth process
- Tokens will be stored locally for future use
- If you revoke access from your Google account, you'll need to re-authenticate

## Troubleshooting
- If you get "access denied" errors, check that your Google account has 2-step verification enabled
- If you get "invalid_client" errors, verify your credentials.json file is correctly formatted
- If you get "unauthorized" errors, ensure the Gmail API is enabled in your Google Cloud Console