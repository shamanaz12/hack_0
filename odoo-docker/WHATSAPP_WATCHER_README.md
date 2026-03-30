# WhatsApp Web Watcher Setup Guide

Monitor WhatsApp Web for unread messages containing keywords and save them as markdown files.

## Prerequisites

- Python 3.8+
- Google Chrome or Chromium browser

## Installation

### Step 1: Install Playwright

```bash
pip install playwright
```

### Step 2: Install Browser

```bash
python -m playwright install chromium
```

This installs Chromium browser that Playwright will use.

### Step 3: Install Browser Dependencies (Windows)

On Windows, the browser should work out of the box. If you encounter issues:

```bash
python -m playwright install-deps chromium
```

## Usage

### First Run (QR Code Authentication)

The first time you run the watcher, you'll need to scan the QR code. **Do not use `--headless` for the first run:**

```bash
# Run in visible mode (NOT headless) for QR scanning
python whatsapp_watcher.py --once
```

**Steps:**
1. A browser window will open and navigate to WhatsApp Web
2. If not logged in, a QR code will appear
3. Open WhatsApp on your phone:
   - **Android**: Settings → Linked Devices → Link a Device
   - **iPhone**: Settings → Linked Devices → Link a Device
4. Scan the QR code with your phone
5. Session will be saved automatically to `whatsapp_session.json`

### Running the Watcher

```bash
# Continuous monitoring (checks every 5 minutes)
python whatsapp_watcher.py

# Run once and exit
python whatsapp_watcher.py --once

# Custom polling interval (in seconds)
python whatsapp_watcher.py --interval 600

# Custom keywords
python whatsapp_watcher.py --keywords invoice payment urgent asap

# Headless mode (ONLY after session is saved)
python whatsapp_watcher.py --headless --once

# Custom output folder
python whatsapp_watcher.py --output "C:\Path\To\Needs_Action"

# Custom session file
python whatsapp_watcher.py --session "my_session.json"
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--once` | Run once and exit | - |
| `--interval` | Polling interval in seconds | 300 |
| `--keywords` | Keywords to search for | invoice, urgent, payment, asap, important |
| `--output` | Output folder for markdown files | AI_Employee_Vault/Silver_Tier/Needs_Action |
| `--session` | Session file path | whatsapp_session.json |
| `--headless` | Run without visible browser | False |

## Session Management

### Session Files

- **whatsapp_session.json** - Stores authentication cookies
- **message_history.json** - Tracks processed messages to avoid duplicates

### Session Location

Session files are saved in the same directory as the script.

### Reusing Session

After first authentication, the session is saved. Subsequent runs will:
- Automatically load the saved session
- Skip QR code scanning
- Work in headless mode if desired

### Clearing Session

To re-authenticate or switch accounts:

```bash
# Delete session files
del whatsapp_session.json
del message_history.json
```

## Output Format

Messages are saved as markdown files in the Needs_Action folder:

```markdown
---
metadata:
  source: "WhatsApp Web"
  chat_name: "John Doe"
  keywords_matched: ["invoice", "urgent"]
  message_count: 2
  received_date: "2026-03-22 10:30:00"
  processed_at: "2026-03-22T10:30:15"
  tier: "WhatsApp Watcher"
---

# WhatsApp Message Alert

## Chat Information
| Field | Value |
|-------|-------|
| **Chat Name** | John Doe |
| **Keywords Matched** | invoice, urgent |
| **Messages** | 2 |
| **Received** | 2026-03-22 10:30:00 |

## Messages

[Message content here...]

## Action Items
- [ ] Review message content
- [ ] Determine required response
- [ ] Respond on WhatsApp if needed
- [ ] Update status
- [ ] Close when completed
```

## Default Keywords

The watcher monitors for these keywords (case-insensitive):
- invoice
- urgent
- payment
- asap
- important

## Logging

Logs are saved to `logs/whatsapp_watcher.log` with:
- Connection status
- Messages processed
- Errors and warnings

## Troubleshooting

### QR Code Not Showing / Timeout Error

```bash
# Run in visible mode (NOT headless)
python whatsapp_watcher.py --once
```

If you see timeout errors, the script will automatically detect and wait for QR code.

### Session Expired / Not Loading

Delete session files and re-authenticate:
```bash
del whatsapp_session.json
del message_history.json
python whatsapp_watcher.py --once
```

### Browser Not Launching

```bash
# Reinstall browser
python -m playwright install chromium
```

### "Event loop is closed" Error

This was fixed in the corrected version. Make sure you're using the latest script.

### No Messages Detected

- Ensure WhatsApp Web is fully loaded
- Check if messages are actually unread
- Verify keywords match your message content
- Check logs: `logs\whatsapp_watcher.log`

### Selectors Not Working

WhatsApp Web updates frequently. If selectors break:
1. Check logs for which selectors are being tried
2. Open WhatsApp Web manually to inspect current structure
3. Update selectors in `is_authenticated()`, `is_qr_visible()`, `get_unread_chats()` methods

## Integration with AI Employee Vault

The watcher integrates with the Silver Tier system:

1. Messages saved to `AI_Employee_Vault/Silver_Tier/Needs_Action/`
2. File watcher picks up new files
3. Moves through workflow: Needs_Action → Plans → Pending_Approval → Approved → Done

## Running as Background Service (Windows)

Create a batch file `run_whatsapp_watcher.bat`:

```batch
@echo off
cd /d "%~dp0"
python whatsapp_watcher.py --interval 300
```

Run it or add to Task Scheduler for automatic startup.

## Security Notes

- Session files contain authentication cookies - keep them secure
- Do not share session files
- Consider using a dedicated WhatsApp account for automation
- Logs may contain message content - secure log files appropriately
