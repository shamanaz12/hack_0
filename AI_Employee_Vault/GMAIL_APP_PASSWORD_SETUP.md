# Setting Up Gmail App Password for MCP Email Server

## Why You Need an App Password
Gmail doesn't allow regular passwords for third-party applications. You need to generate a special "App Password".

## Step-by-Step Instructions

### 1. Enable 2-Factor Authentication
- Go to your Google Account: https://myaccount.google.com/
- Click on "Security" from the left sidebar
- Under "Signing in to Google," click on "2-Step Verification"
- Follow the prompts to enable 2-factor authentication if not already enabled

### 2. Generate an App Password
- In your Google Account, go to Security section
- Under "Signing in to Google," find "App passwords"
- Click on "App passwords" (you may need to sign in again)
- Select "Mail" as the app and "Other (Custom name)" and enter a name like "MCP Server"
- Click "Generate"
- A 16-character password will appear (e.g., abcd efgh ijkl mnop)

### 3. Update the Environment Variables
- Open the `setup_and_start_mcp_server.bat` file in a text editor
- Replace `your_app_password_here` with the 16-character app password
- Save the file

### 4. Run the Server
- Double-click `setup_and_start_mcp_server.bat` to run the server with your credentials

## Example of Correct Format
Your app password will look like this when entered:
```
set SMTP_PASSWORD=abcd efgh ijkl mnop
```
(Note: The spaces are automatically included in the generated app password)

## Security Notes
- Keep your app password secure and private
- Never share it or commit it to any public repository
- You can revoke the app password anytime from your Google Account

## Troubleshooting
- If you get authentication errors, double-check your app password
- Make sure 2-factor authentication is enabled on your account
- Ensure you're using the app password, not your regular Gmail password