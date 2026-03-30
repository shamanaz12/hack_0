# Fixing the OAuth Client Error

## Problem
The error "The OAuth client was not found. Error 401: invalid_client" occurs because the credentials.json file doesn't contain valid OAuth credentials from Google Cloud Console.

## Solution Steps

### Step 1: Create a New Project in Google Cloud Console
1. Go to https://console.cloud.google.com/
2. Click the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "AI-Employee-Vault")
5. Click "Create"

### Step 2: Enable Gmail API for Your Project
1. In the Google Cloud Console, search for "Gmail API"
2. Click on "Gmail API" in the search results
3. Click "Enable"

### Step 3: Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials" in the left sidebar
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. If prompted about the OAuth consent screen, click "Configure consent screen"
4. Select "External" and click "Create"
5. Fill in the required fields:
   - App name: "AI Employee Vault"
   - User support email: your email address
   - Authorized domains: your domain (or leave default)
   - Developer contact information: your email
6. Click "Save and Continue"
7. Skip adding scopes for now and click "Save and Continue"
8. Skip adding test users and click "Save and Continue"
9. Click "Back to Dashboard"
10. Go back to "Credentials" and click "Create Credentials" > "OAuth 2.0 Client IDs" again
11. Select "Desktop application" as the application type
12. Give it a name (e.g., "AI Employee Desktop App")
13. Click "Create"
14. Download the JSON file that appears
15. Rename the downloaded file to "credentials.json"
16. Place it in the folder: C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault

### Step 4: Update Your credentials.json
Replace the current credentials.json file with the one you downloaded from Google Cloud Console.

### Step 5: Run the Setup Again
1. Run the setup_helper.py script again:
   ```
   python setup_helper.py
   ```
2. This time it should work properly and guide you through the authentication process

## Important Notes
- Make sure to use the exact filename "credentials.json"
- The credentials file contains sensitive information - keep it secure
- After the first successful authentication, a "token.pickle" file will be created for future use
- If you get an error about the app not being verified, that's normal for development apps

## Troubleshooting
- If you still get errors, make sure you selected "Desktop application" when creating the OAuth client
- Ensure the Gmail API is enabled for your project
- Check that the credentials.json file is in the correct location