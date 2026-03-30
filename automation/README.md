# 🤖 Gold Tier Automation Orchestrator

Complete browser automation system for Facebook, Instagram, WhatsApp, and Gmail using Playwright. No API tokens required - all actions performed via browser automation with session persistence.

## 📋 Features

### Facebook Business Page
- ✅ Post text and links
- ✅ Read recent posts
- ✅ Delete posts
- ✅ Reply to comments

### Instagram Business Account
- ✅ Post images with captions
- ✅ Read recent posts
- ✅ Delete posts
- ✅ Reply to comments

### WhatsApp Web
- ✅ Read unread messages
- ✅ Send replies
- ✅ Send new messages

### Gmail
- ✅ Read unread emails
- ✅ Send replies
- ✅ Mark as read
- ✅ Send new emails

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd automation
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Credentials

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Facebook Business Page
FACEBOOK_EMAIL=your_email@example.com
FACEBOOK_PASSWORD=your_password
FACEBOOK_PAGE_ID=956241877582673
FACEBOOK_PAGE_URL=https://www.facebook.com/profile.php?id=956241877582673

# Instagram
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# Gmail
GMAIL_EMAIL=your_gmail@example.com
GMAIL_PASSWORD=your_gmail_password
```

### 3. First-Time Setup (Interactive Mode)

Run the orchestrator in interactive mode to perform initial logins:

```bash
python orchestrator.py --headless=false
```

**First-time login process:**
1. **Facebook/Instagram/Gmail**: Browser will open - login manually if needed
2. **WhatsApp**: Scan QR code with your phone
3. Sessions are saved automatically for future runs

### 4. Run Automation

#### Run Once (Check all platforms)
```bash
python orchestrator.py --once
```

#### Run Continuous (Auto-monitoring)
```bash
python orchestrator.py --interval 60
```

#### Headless Mode (After first login)
```bash
python orchestrator.py --headless --once
```

#### Specific Platforms Only
```bash
python orchestrator.py --platforms facebook whatsapp --once
```

## 📁 Project Structure

```
automation/
├── session_manager.py      # Cookie & session management
├── facebook_browser.py     # Facebook automation
├── instagram_browser.py    # Instagram automation
├── whatsapp_browser.py     # WhatsApp automation
├── gmail_browser.py        # Gmail automation
├── orchestrator.py         # Main controller
├── requirements.txt        # Python dependencies
├── .env                    # Credentials (create from .env.example)
├── .env.example            # Template for credentials
├── sessions/               # Saved authentication cookies
│   ├── facebook_auth.json
│   ├── instagram_auth.json
│   ├── whatsapp_auth.json
│   └── gmail_auth.json
└── logs/                   # Automation logs
    ├── session_manager.log
    └── orchestrator.log
```

## 💡 Usage Examples

### Python API Usage

```python
from orchestrator import AutomationOrchestrator

# Create orchestrator (headless=False for first login)
orchestrator = AutomationOrchestrator(headless=False)
orchestrator.initialize()

# Post to Facebook
orchestrator.post_to_facebook(
    text="Gold Tier - Your partner in business growth! 📈",
    link="https://example.com"
)

# Post to Instagram (requires image)
orchestrator.post_to_instagram(
    text="New product launch! ✨ #GoldTier",
    image_path="path/to/image.jpg"
)

# Send WhatsApp message
orchestrator.send_whatsapp_message(
    contact="+923161129505",
    message="Hello! This is an automated message."
)

# Send email
orchestrator.send_email(
    to="client@example.com",
    subject="Business Update",
    body="Dear Client, here's your update..."
)

# Get unread messages
whatsapp_msgs = orchestrator.get_unread_whatsapp_messages()
emails = orchestrator.get_unread_emails()

# Cleanup
orchestrator.shutdown()
```

### Custom Automation Script

```python
from orchestrator import AutomationOrchestrator

orchestrator = AutomationOrchestrator(headless=False)
orchestrator.initialize()

# Check all platforms
orchestrator.run_once()

# Post to Facebook
orchestrator.post_to_facebook("Business update from Gold Tier!")

# Read WhatsApp messages and auto-reply
messages = orchestrator.get_unread_whatsapp_messages()
for msg in messages:
    if "urgent" in msg.get('text', '').lower():
        orchestrator.send_whatsapp_message(
            msg['sender'],
            "Thank you! We'll respond shortly."
        )

orchestrator.shutdown()
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FACEBOOK_EMAIL` | Facebook login email | Yes |
| `FACEBOOK_PASSWORD` | Facebook password | Yes |
| `FACEBOOK_PAGE_ID` | Business Page ID | Yes |
| `FACEBOOK_PAGE_URL` | Business Page URL | Yes |
| `INSTAGRAM_USERNAME` | Instagram username | Yes |
| `INSTAGRAM_PASSWORD` | Instagram password | Yes |
| `GMAIL_EMAIL` | Gmail address | Yes |
| `GMAIL_PASSWORD` | Gmail password | Yes |
| `HEADLESS_MODE` | Run browser headless | No (default: false) |
| `LOG_LEVEL` | Logging level | No (default: INFO) |

### Task Intervals (in orchestrator.py)

```python
self.task_intervals = {
    "facebook_check": 300,      # 5 minutes
    "instagram_check": 600,     # 10 minutes
    "whatsapp_check": 120,      # 2 minutes
    "gmail_check": 180,         # 3 minutes
    "facebook_post": 3600,      # 1 hour
    "instagram_post": 7200,     # 2 hours
}
```

## 🔐 Security Notes

1. **Never commit `.env`** - Contains sensitive credentials
2. **Session files** - Stored in `sessions/` folder, keep secure
3. **Gmail App Password** - If using 2FA, generate an app password
4. **WhatsApp** - QR code only needed once, session is saved

## 🛠️ Troubleshooting

### Session Not Persisting
- Ensure `sessions/` folder has write permissions
- Check that cookies are being saved after login

### CAPTCHA Challenges
- Use persistent sessions (already implemented)
- Add delays between actions (already implemented)
- Manual login may be required occasionally

### WhatsApp QR Code Not Appearing
- Clear `sessions/whatsapp_auth.json`
- Restart orchestrator
- Ensure stable internet connection

### Gmail Login Issues
- Enable "Less secure app access" (if available)
- Use App Password if 2FA is enabled
- Clear `sessions/gmail_auth.json` and re-login

## 📊 Logs

Check logs in the `logs/` folder:
- `orchestrator.log` - Main automation logs
- `session_manager.log` - Login and session logs

## 🎯 Best Practices

1. **First Run**: Always run with `--headless=false` first
2. **Session Reuse**: After first login, use `--headless` for automation
3. **Rate Limiting**: Built-in random delays prevent detection
4. **Error Handling**: All operations have try/catch with logging
5. **Graceful Shutdown**: Press Ctrl+C to stop safely

## 📝 Command Reference

```bash
# Check status (quick - no live tests)
python status_cli.py --quick

# Check status with live tests
python status_cli.py

# Check specific platform
python status_cli.py --platform whatsapp

# Run once, all platforms
python orchestrator.py --once

# Run once, specific platforms
python orchestrator.py --once --platforms facebook gmail

# Continuous monitoring
python orchestrator.py --interval 60

# Headless mode (after first login)
python orchestrator.py --headless --once

# Full help
python orchestrator.py --help
```

## 📄 License

Internal use for Gold Tier Business Automation.

## 🆘 Support

For issues, check:
1. Logs in `logs/` folder
2. Session files in `sessions/` folder
3. Credentials in `.env` file

---

**Created:** March 30, 2026  
**Version:** 1.0  
**Maintained by:** Gold Tier Automation System
