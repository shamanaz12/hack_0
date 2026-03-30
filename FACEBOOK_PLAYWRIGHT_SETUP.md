# Facebook Automation with Playwright - Setup Guide

## 🚀 Overview

This system uses **Playwright browser automation** to interact with Facebook **without requiring any Graph API tokens**. It automates a real browser to perform actions exactly like a human would.

### Features:
- ✅ **No API tokens required** - Uses real browser automation
- ✅ **One-time login** - Saves session cookies for 24 hours
- ✅ **Headless mode** - Runs invisibly in background
- ✅ **Human-like behavior** - Random delays, rate limiting
- ✅ **Auto-relogin** - Handles session expiration
- ✅ **Block detection** - Detects captchas and security checks

---

## 📦 Installation

### Step 1: Install Dependencies

```bash
cd C:\Users\AA\Desktop\gold_tier

# Install Python packages
pip install -r requirements_facebook_auto.txt

# Install Playwright browsers
playwright install
```

### Step 2: Configure Credentials

Edit `.env` file and add your Facebook credentials:

```env
# Facebook Login Credentials
FACEBOOK_EMAIL=your_facebook_email@example.com
FACEBOOK_PASSWORD=your_facebook_password

# Facebook Page ID (already configured)
FACEBOOK_PAGE_ID=956241877582673

# Browser Settings
FACEBOOK_HEADLESS=true
FACEBOOK_SLOW_MO=100
```

### Step 3: Test Installation

```bash
python mcp_servers\facebook_playwright_auto.py
```

---

## 🎯 Usage

### Option 1: Direct Python Script

```bash
# Test automation
python mcp_servers\facebook_playwright_auto.py

# Run MCP server
python mcp_servers\facebook_mcp_playwright.py
```

### Option 2: From Web Dashboard

1. Start web server:
```bash
python mcp_servers\social_mcp_web.py
```

2. Open browser: `http://localhost:8080`

3. Use the Facebook tab to:
   - Create posts
   - View recent posts
   - Check messages
   - Reply to comments

### Option 3: From Skills (Command Line)

```bash
# Create post
python skills\facebook_skill.py --post "Hello from automation!"

# Get recent posts
python skills\facebook_skill.py --get 5

# Check status
python skills\facebook_skill.py --check
```

---

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FACEBOOK_EMAIL` | Facebook login email | (required) |
| `FACEBOOK_PASSWORD` | Facebook login password | (required) |
| `FACEBOOK_PAGE_ID` | Page ID to manage | 956241877582673 |
| `FACEBOOK_HEADLESS` | Run browser invisibly | `true` |
| `FACEBOOK_SLOW_MO` | Delay between actions (ms) | `100` |

### Rate Limiting

The system automatically enforces rate limits to avoid detection:

- **Minimum delay**: 3 seconds between actions
- **Maximum delay**: 8 seconds between actions
- **Break after**: 10 actions
- **Break duration**: 5 minutes

You can adjust these in `facebook_playwright_auto.py`:

```python
self.min_delay = 3  # seconds
self.max_delay = 8  # seconds
self.max_actions_before_break = 10
self.break_duration = 300  # 5 minutes
```

---

## 📁 File Structure

```
gold_tier/
├── mcp_servers/
│   ├── facebook_playwright_auto.py    # Core automation module
│   ├── facebook_mcp_playwright.py     # MCP server integration
│   └── social_mcp_web.py              # Web dashboard
├── skills/
│   └── facebook_skill.py              # Command-line skill
├── .env                               # Configuration
├── requirements_facebook_auto.txt     # Dependencies
├── facebook_auth.json                 # Saved session (auto-created)
└── logs/
    └── facebook_auto.log              # Logs
```

---

## 🔐 Security & Privacy

### Session Storage
- Login cookies are saved to `facebook_auth.json`
- Session expires after 24 hours
- File is stored locally, not shared

### Credentials
- Stored in `.env` file (not committed to Git)
- Never sent to external servers
- Used only for local browser automation

---

## ⚠️ Important Warnings

### Terms of Service

**Facebook's Terms of Service prohibit automated access.** Use this system responsibly:

1. **Moderate Usage**: Don't post too frequently (max 10 posts per session)
2. **Human Hours**: Run automation during normal business hours
3. **Natural Behavior**: The system includes random delays to mimic humans
4. **Monitor Logs**: Check `logs/facebook_auto.log` for any warnings

### Risks

- ⚠️ Account may be temporarily blocked if detected
- ⚠️ Captchas may appear (system will log and pause)
- ⚠️ Facebook may change UI (selectors may need updates)

### Best Practices

1. **Start with mock mode** - Test without credentials first
2. **Use headed mode initially** - Watch what the browser does
3. **Monitor first few runs** - Check logs for issues
4. **Don't spam** - Keep posting frequency natural
5. **Take breaks** - System auto-pauses after 10 actions

---

## 🐛 Troubleshooting

### Problem: Login fails

**Solution:**
```bash
# Set headless to false to see what's happening
FACEBOOK_HEADLESS=false

# Run with debug output
python mcp_servers\facebook_playwright_auto.py
```

### Problem: "Element not found"

**Solution:** Facebook may have changed their UI. Check logs:
```bash
type logs\facebook_auto.log
```

Update selectors in `facebook_playwright_auto.py` if needed.

### Problem: Captcha / Security Check

**Solution:**
1. System will detect and log the issue
2. Wait 24 hours before trying again
3. Consider using headed mode to solve captcha manually
4. Reduce posting frequency

### Problem: Session expires quickly

**Solution:**
- Session is valid for 24 hours by default
- Increase duration in `load_session()`:
```python
if datetime.now() - saved_at > timedelta(hours=48):  # 48 hours
```

---

## 📊 API Reference

### FacebookAutomation Class

```python
from mcp_servers.facebook_playwright_auto import FacebookAutomation

auto = FacebookAutomation()

# Login
auto.ensure_logged_in()

# Create post
result = auto.create_post("Hello world!", "https://example.com")

# Get posts
posts = auto.get_recent_posts(limit=5)

# Delete post
result = auto.delete_post(post_id="12345")

# Get messages
messages = auto.get_page_messages(limit=10)

# Reply to message
result = auto.reply_to_message("msg_123", "Thanks!")

# Cleanup
auto.stop_browser()
```

### MCP Server Functions

```python
from mcp_servers.facebook_mcp_playwright import facebook_mcp

# Health check
health = facebook_mcp.health_check()

# Create post
post = facebook_mcp.create_post("Message", "https://link.com")

# Get posts
posts = facebook_mcp.get_posts(5)

# Delete post
result = facebook_mcp.delete_post("post_id")

# Get messages
messages = facebook_mcp.get_messages(10)

# Reply
reply = facebook_mcp.reply_to_message("msg_id", "Reply text")
```

---

## 🎓 Example: Automated Daily Posting

Create a script for daily automated posts:

```python
# daily_poster.py
from mcp_servers.facebook_playwright_auto import FacebookAutomation
from datetime import datetime

auto = FacebookAutomation()

try:
    auto.ensure_logged_in()
    
    # Create daily post
    message = f"Good morning! Today is {datetime.now().strftime('%A, %B %d')}"
    result = auto.create_post(message)
    
    print(f"Post created: {result}")
    
finally:
    auto.stop_browser()
```

Schedule with Windows Task Scheduler:
```bash
schtasks /create /tn "Facebook Daily Post" /tr "python C:\Users\AA\Desktop\gold_tier\daily_poster.py" /sc daily /st 09:00
```

---

## 📞 Support

### Logs Location
```
logs/facebook_auto.log
```

### Enable Debug Mode
```python
# In facebook_playwright_auto.py
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Login loop | Check credentials in .env |
| Post not created | Reduce rate limits |
| Browser won't start | Run `playwright install` |
| Session expires | Re-login, check system time |

---

## ✅ Checklist

Before going live:

- [ ] Credentials added to `.env`
- [ ] `playwright install` completed
- [ ] Test run in headed mode (`FACEBOOK_HEADLESS=false`)
- [ ] Logs checked for errors
- [ ] Rate limits configured appropriately
- [ ] First post successful
- [ ] Switched to headless mode

---

**Created for: Gold Tier - Naz Sheikh**
**Date: March 27, 2026**
**Version: 1.0.0**
