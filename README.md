# 🏆 GOLD TIER - Business Automation System

**Complete social media automation for Facebook, Instagram, WhatsApp, and Gmail**

---

## 📋 Features

### Facebook Business Page Automation
- ✅ Auto Post to Business Page
- ✅ Get Recent Posts
- ✅ Delete Posts
- ✅ Reply to Comments
- ✅ Direct Page Redirect (No login issues)

### Instagram Automation
- ✅ Post Images with Captions
- ✅ Get Recent Posts
- ✅ Delete Posts
- ✅ Reply to Comments

### WhatsApp Web Automation
- ✅ Read Unread Messages
- ✅ Send Replies
- ✅ Send New Messages
- ✅ Session Persistence

### Gmail Automation
- ✅ Read Unread Emails
- ✅ Send Replies
- ✅ Mark as Read
- ✅ Send New Emails

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd automation
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Credentials
Edit `automation/.env`:
```env
FACEBOOK_EMAIL=your_email@example.com
FACEBOOK_PASSWORD=your_password
FACEBOOK_PAGE_ID=61578538607212
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
GMAIL_EMAIL=your_gmail@example.com
WHATSAPP_PHONE=+923202191812
```

### 3. First Login
```bash
cd automation
python orchestrator.py
```

### 4. Auto Post to Facebook
```bash
python facebook_page_auto.py --post "Your post message here"
```

---

## 📁 Project Structure

```
gold_tier/
├── automation/
│   ├── session_manager.py      # Session & cookie management
│   ├── facebook_browser.py     # Facebook automation
│   ├── instagram_browser.py    # Instagram automation
│   ├── whatsapp_browser.py     # WhatsApp automation
│   ├── gmail_browser.py        # Gmail automation
│   ├── orchestrator.py         # Main controller
│   ├── facebook_page_auto.py   # Facebook page auto-post
│   ├── status_cli.py           # Status checker
│   ├── check_all_status.py     # All platforms status
│   ├── whatsapp_qr_login.py    # WhatsApp QR login
│   ├── requirements.txt        # Dependencies
│   ├── .env                    # Credentials
│   └── README.md               # Documentation
├── mcp_servers/
│   ├── facebook_mcp_playwright.py      # Facebook MCP server
│   ├── facebook_playwright_auto.py     # Facebook automation
│   ├── gmail_mcp_server.py             # Gmail MCP server
│   ├── social_localhost_mcp.py         # Social MCP localhost
│   └── unified_social_mcp.py           # Unified social MCP
├── dashboard.md                  # Live status dashboard
├── .env                          # Main credentials
└── README.md                     # This file
```

---

## 💡 Quick Commands

### Facebook Page
```bash
# Auto post
python automation/facebook_page_auto.py --post "Gold Tier Update!"

# Get posts
python automation/facebook_page_auto.py --get

# Delete post
python automation/facebook_page_auto.py --delete 1

# Check status
python automation/facebook_page_auto.py --status
```

### All Platforms
```bash
# Run automation
python automation/orchestrator.py --once

# Continuous monitoring
python automation/orchestrator.py --interval 60

# Status check
python automation/status_cli.py --quick
python automation/check_all_status.py
```

### WhatsApp
```bash
# QR Login (first time)
python automation/whatsapp_qr_login.py
```

---

## 🔐 Configuration

### Environment Variables (.env)
| Variable | Description | Required |
|----------|-------------|----------|
| `FACEBOOK_EMAIL` | Facebook login email | Yes |
| `FACEBOOK_PASSWORD` | Facebook password | Yes |
| `FACEBOOK_PAGE_ID` | Business Page ID | Yes |
| `INSTAGRAM_USERNAME` | Instagram username | Yes |
| `INSTAGRAM_PASSWORD` | Instagram password | Yes |
| `GMAIL_EMAIL` | Gmail address | Yes |
| `GMAIL_PASSWORD` | Gmail password | Yes |
| `WHATSAPP_PHONE` | WhatsApp phone | Yes |

---

## 📊 Current Status

| Platform | Status |
|----------|--------|
| Facebook Page | ✅ Configured (61578538607212) |
| Instagram | ✅ Configured (@shamaansari5576) |
| WhatsApp | ✅ Logged In (+923202191812) |
| Gmail | ✅ Configured |
| MCP Server | ✅ Direct Redirect |

---

## 🛠️ Troubleshooting

### Session Not Persisting
```bash
# Clear sessions and re-login
rm automation/sessions/*.json
python automation/orchestrator.py
```

### WhatsApp QR Code
```bash
# Re-scan QR code
python automation/whatsapp_qr_login.py
```

### Facebook Login Issues
```bash
# Check status
python automation/facebook_page_auto.py --status
```

---

## 📝 MCP Server Integration

The system includes MCP servers for integration with other tools:

```bash
# Test Facebook MCP
python mcp_servers/facebook_mcp_playwright.py

# Test Social MCP
python mcp_servers/social_localhost_mcp.py
```

---

## 🎯 Key Features

1. **No API Tokens Required** - Uses browser automation
2. **Session Persistence** - Login once, reuse sessions
3. **Anti-Detection** - Human-like delays and behavior
4. **Error Handling** - Comprehensive logging and recovery
5. **MCP Server Support** - Easy integration with other systems

---

## 📄 License

Internal use for Gold Tier Business Automation

---

## 👤 Owner

**Naz Sheikh**
- Facebook: https://www.facebook.com/profile.php?id=61578538607212
- Instagram: @shamaansari5576
- WhatsApp: +923202191812

---

**Created:** March 31, 2026
**Version:** 1.0
**Status:** ✅ Production Ready
