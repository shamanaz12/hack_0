# WhatsApp Watcher - Quick Start Guide

## Fixes Summary (Ghaltiyan aur Unka Hal)

### ❌ Problem 1: Outdated Selector
**Error:** `div[data-testid="default-user"]` timeout
**Fix:** Multiple fallback selectors for QR code and chat list
- QR: `canvas[aria-label="Scan me!"]`, `img[alt="Scan me!"]`, etc.
- Auth: `div[data-testid="chat-list"]`, `div[role="main"]`, etc.

### ❌ Problem 2: Event Loop Closed Error
**Error:** Browser close fails after exception
**Fix:** Proper cleanup with flags (`_closing`, `_cleanup_done`)
- Each resource closed individually with try-except
- Prevents double-close errors

---

## Quick Commands

### First Time Setup
```bash
# Install
pip install playwright
python -m playwright install chromium

# First run (QR scan required - NOT headless!)
python whatsapp_watcher.py --once
```

### Daily Usage
```bash
# Continuous monitoring (every 5 min)
python whatsapp_watcher.py

# Run once
python whatsapp_watcher.py --once

# Headless mode (after session saved)
python whatsapp_watcher.py --headless --once

# Custom keywords
python whatsapp_watcher.py --keywords urgent invoice payment
```

---

## File Structure

```
h.p_hack_0/
├── whatsapp_watcher.py          # Main script
├── WHATSAPP_WATCHER_README.md   # Full documentation
├── whatsapp_session.json        # Saved login session (auto-created)
├── message_history.json         # Processed messages log (auto-created)
├── logs/
│   └── whatsapp_watcher.log     # Detailed logs
└── AI_Employee_Vault/
    └── Silver_Tier/
        └── Needs_Action/        # Output markdown files
```

---

## Keywords

Default keywords (case-insensitive):
- invoice
- urgent
- payment
- asap
- important

Change with: `--keywords word1 word2 word3`

---

## Output Example

When a message matches keywords, creates:
`AI_Employee_Vault/Silver_Tier/Needs_Action/WhatsApp_20260322_143022_John.md`

With metadata, message content, and action items.

---

## Common Issues

| Issue | Solution |
|-------|----------|
| QR timeout | Run without `--headless`, wait for scan |
| Session expired | Delete `whatsapp_session.json`, re-run |
| No messages | Check keywords, verify unread messages exist |
| Browser won't start | `python -m playwright install chromium` |

---

## Logs

Check `logs/whatsapp_watcher.log` for:
- Authentication status
- Messages processed
- Errors and debugging info

---

## Stop Watcher

Press `Ctrl+C` to stop gracefully (saves session before exit)
