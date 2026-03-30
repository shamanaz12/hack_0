# 🚀 Quick Start Guide for Beginners

## Step 1: Get Gmail API Credentials (5 minutes)

### Go to Google Cloud Console
🔗 https://console.cloud.google.com/

### Create New Project
1. Click the project dropdown at the top
2. Click **"NEW PROJECT"**
3. Enter name: `AI-Employee-Vault`
4. Click **"CREATE"**

### Enable Gmail API
1. Search for **"Gmail API"** in the search bar
2. Click on **"Gmail API"**
3. Click **"ENABLE"**

### Configure OAuth Consent Screen
1. Go to: **APIs & Services** → **OAuth consent screen**
2. Select **"External"** → Click **"CREATE"**
3. Fill in:
   - **App name**: `AI Employee Vault`
   - **User support email**: `your-email@gmail.com`
   - **Developer contact**: `your-email@gmail.com`
4. Click **"SAVE AND CONTINUE"**
5. Skip "Scopes" → Click **"SAVE AND CONTINUE"**
6. Skip "Test users" → Click **"SAVE AND CONTINUE"**

### Create OAuth Credentials
1. Go to: **APIs & Services** → **Credentials**
2. Click **"CREATE CREDENTIALS"** → **"OAuth 2.0 Client IDs"**
3. Application type: **Desktop app**
4. Name: `AI Employee Desktop`
5. Click **"CREATE"**
6. Download the JSON file
7. **Rename it to**: `credentials.json`
8. **Move it to**: `C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\`

---

## Step 2: Get Gmail App Password (3 minutes)

### Enable 2-Step Verification
1. Go to: https://myaccount.google.com/security
2. Under "Signing in to Google" → Click **"2-Step Verification"**
3. Follow steps to enable it

### Generate App Password
1. Go back to: https://myaccount.google.com/security
2. Under "Signing in to Google" → Click **"App passwords"**
3. Select:
   - **App**: Mail
   - **Device**: Other (Custom name) → Enter: `MCP Server`
4. Click **"GENERATE"**
5. **Copy the 16-character password** (example: `abcd efgh ijkl mnop`)

---

## Step 3: Run the Setup (2 minutes)

### Run Installation Script
1. Double-click: `INSTALL_AND_RUN.bat`
2. Follow the prompts
3. Browser will open → Sign in to Google → Click "Allow"

### Start Gmail Watcher (Receive Emails)
```
Double-click: start_gmail_watcher.bat
```

### Start MCP Server (Send Emails)
1. Edit `start_mcp_with_credentials.bat`
2. Replace `your-email@gmail.com` with your email
3. Replace `xxxx xxxx xxxx xxxx` with your App Password
4. Double-click to run

---

## ✅ What Happens After Setup

```
Gmail Inbox → (Every 5 minutes) → Needs_Action Folder
                                           ↓
                                    Process to Plans
                                           ↓
                                      Your Approval
                                           ↓
                                    MCP Sends Email
                                           ↓
                                         Done!
```

---

## 📁 File Locations

| File | Purpose |
|------|---------|
| `credentials.json` | Gmail API OAuth (reading emails) |
| `token.pickle` | Auto-created after first login |
| `start_gmail_watcher.bat` | Receives emails from Gmail |
| `start_mcp_with_credentials.bat` | Sends emails via MCP server |

---

## ❓ Need Help?

1. Check `GMAIL_SETUP_GUIDE.md` for detailed OAuth setup
2. Check `GMAIL_APP_PASSWORD_SETUP.md` for App Password help
3. Check `SYSTEM_STATUS_REPORT.md` for current system status

---

## 🧪 Test It!

1. Send yourself a test email in Gmail
2. Wait 5 minutes (or run `start_gmail_watcher.bat`)
3. Check `Needs_Action/` folder - markdown file should appear!
