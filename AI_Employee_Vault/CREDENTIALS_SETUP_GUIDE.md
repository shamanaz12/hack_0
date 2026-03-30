# 🔐 Complete Credentials Setup Guide

## Overview

Is project mein **2 types ki credentials** chahiye:

| # | Credential | Purpose | Tier | Status |
|---|------------|---------|------|--------|
| 1 | **Google OAuth (credentials.json)** | Gmail se emails **read** karne ke liye | Bronze + Silver | ⚠️ Setup Needed |
| 2 | **Gmail App Password** | Gmail se emails **send** karne ke liye (MCP) | Silver Only | ⚠️ Setup Needed |

---

## 📋 Part 1: Google OAuth Credentials (credentials.json)

### Step-by-Step Setup:

#### 1. Google Cloud Console mein jayein
🔗 https://console.cloud.google.com/

#### 2. New Project Create Karein
```
1. Top par project dropdown click karein
2. "NEW PROJECT" click karein
3. Project name: AI-Employee-Vault
4. "CREATE" click karein
```

#### 3. Gmail API Enable Karein
```
1. Search bar mein "Gmail API" search karein
2. "Gmail API" par click karein
3. "ENABLE" button click karein
```

#### 4. OAuth Consent Screen Setup (Bronze Tier - Testing)
```
1. Left menu: APIs & Services → OAuth consent screen
2. "External" select karein → "CREATE"
3. Fill karein:
   - App name: AI Employee Vault
   - User support email: your-email@gmail.com
   - Developer contact: your-email@gmail.com
4. "SAVE AND CONTINUE" click karein
5. Scopes skip karein → "SAVE AND CONTINUE"
6. Test users skip karein → "SAVE AND CONTINUE"
```

#### 5. OAuth 2.0 Credentials Create Karein
```
1. Left menu: APIs & Services → Credentials
2. "CREATE CREDENTIALS" → "OAuth 2.0 Client IDs"
3. Application type: "Desktop app"
4. Name: "AI Employee Desktop"
5. "CREATE" click karein
6. JSON file download hoga
7. File ko rename karein: `credentials.json`
```

#### 6. File Ko Sahi Jagah Rakhein
```
credentials.json ko yahan place karein:
C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\credentials.json
```

---

### ✅ Current credentials.json Status:

**Existing File:**
```json
{
  "installed": {
    "client_id": "1086031784666-7m1k1jvg1qrv5jjovjc1jf6o9g9dsq5v.apps.googleusercontent.com",
    "project_id": "quickstart-123456789",
    ...
  }
}
```

⚠️ **Issue:** Ye ek **placeholder/test** credentials hai. 
**Real credentials** Google Cloud Console se download karni hongi.

---

### 🔧 First-Time Authentication:

Jab aap pehli baar run karenge:

```bash
cd C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault
python gmail_auth.py
```

**Kya hoga:**
1. Browser automatically open hoga
2. Google sign-in page aayega
3. Apne Gmail account se sign in karein
4. "Allow" click karein permissions ke liye
5. `token.pickle` file automatically create hogi

---

## 📋 Part 2: Gmail App Password (MCP Server ke liye)

### Step-by-Step Setup:

#### 1. Google Account Security Settings
🔗 https://myaccount.google.com/security

#### 2. 2-Step Verification Enable Karein
```
1. "Signing in to Google" section mein
2. "2-Step Verification" par click karein
3. "GET STARTED" click karein
4. Phone number enter karein
5. Code enter karein (SMS se aayega)
6. "ON" click karein
```

#### 3. App Password Generate Karein
```
1. Wapis Security page par jayein
2. "2-Step Verification" ke neeche
3. "App passwords" par click karein
4. Sign in karna pade (agar prompt aaye)
5. App select karein: "Mail"
6. Device select karein: "Other (Custom name)"
7. Name enter karein: "MCP Server"
8. "GENERATE" click karein
```

#### 4. Password Copy Karein
```
16-character password dikhega:
abcd efgh ijkl mnop

Isko copy karlein (spaces ke saath)
```

#### 5. MCP Server Configuration

**File edit karein:** `start_mcp_with_credentials.bat`

```batch
set SMTP_HOST=smtp.gmail.com
set SMTP_PORT=587
set SMTP_USERNAME=your-email@gmail.com
set SMTP_PASSWORD=abcd efgh ijkl mnop    ← Yahan paste karein
set SMTP_USE_TLS=true
```

---

## 🎯 Quick Setup Commands

### Bronze Tier (Testing - Read Only):

```bash
cd C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault

# 1. Check credentials
python validate_credentials.py

# 2. Authenticate (browser open hoga)
python gmail_auth.py

# 3. Start Gmail watcher
python gmail_poller.py

# 4. Check Bronze Tier status
python bronze_tier_processor.py status
```

### Silver Tier (Production - Read + Send):

```bash
cd C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault

# 1. Setup App Password in batch file
# Edit: start_mcp_with_credentials.bat

# 2. Start MCP Server
start_mcp_with_credentials.bat

# 3. Start Gmail watcher
python gmail_poller.py

# 4. Check Silver Tier status
python silver_tier_processor.py status
```

---

## 📁 Credentials Files Location

| File | Location | Purpose |
|------|----------|---------|
| `credentials.json` | `AI_Employee_Vault/` | OAuth credentials (download from Google) |
| `token.pickle` | `AI_Employee_Vault/` | Auto-created after first login |
| `start_mcp_with_credentials.bat` | `AI_Employee_Vault/` | MCP server with App Password |

---

## ✅ Verification Checklist

### Before Running:

- [ ] Google Cloud project created
- [ ] Gmail API enabled
- [ ] OAuth consent screen configured
- [ ] `credentials.json` downloaded and placed in correct folder
- [ ] 2-Step Verification enabled on Gmail
- [ ] App Password generated (for Silver Tier)
- [ ] App Password saved in batch file

### After First Run:

- [ ] Browser opened for authentication
- [ ] Successfully signed in to Google
- [ ] `token.pickle` file created
- [ ] No errors in console

---

## ❓ Troubleshooting

### Error: "The OAuth client was not found"
**Solution:** `credentials.json` file galat hai. Dobara download karein Google Cloud se.

### Error: "invalid_client"
**Solution:** `credentials.json` file corrupted hai. Dobara download karein.

### Error: "Access denied" / "User not found"
**Solution:** Gmail account mein 2-Step Verification enable nahi hai. Enable karein.

### Error: "App password option not available"
**Solution:** Pehle 2-Step Verification enable karein, phir App Password option aayega.

### Error: "Token expired"
**Solution:** `token.pickle` file delete karein aur dobara `gmail_auth.py` run karein.

---

## 🔒 Security Notes

⚠️ **IMPORTANT:**
- `credentials.json` ko **public repository** mein commit na karein
- `token.pickle` ko **secure** rakhein
- App Password ko **share na karein**
- Agar credentials leak ho jayein, toh Google Cloud se **revoke** karein

---

## 📞 Need Help?

1. Check: `GMAIL_SETUP_GUIDE.md` - OAuth setup details
2. Check: `GMAIL_APP_PASSWORD_SETUP.md` - App Password details
3. Check: `FIX_OAUTH_ERROR.md` - Common OAuth errors
4. Run: `python setup_helper.py` - Interactive setup helper

---

## 🚀 Quick Start After Credentials

```bash
# 1. Validate credentials
python validate_credentials.py

# 2. Authenticate
python gmail_auth.py

# 3. Start Bronze Tier
start_bronze_tier_watcher.bat

# 4. Check status
python bronze_tier_processor.py status
```
