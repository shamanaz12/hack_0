# Auto Processor - Fully Automatic Gmail + WhatsApp Processor

## Overview (Khulasa)

Ye script **automatically** aapke Gmail aur WhatsApp messages ko process karti hai - **bina manual intervention ke!**

## Features (Khasiyat)

✅ **Automatic Gmail Monitoring** - Har 5 minute baad Gmail check karta hai
✅ **Automatic WhatsApp Monitoring** - Har 5 minute baad WhatsApp check karta hai
✅ **Keyword Detection** - Urgent, invoice, payment, ASAP, important messages detect karta hai
✅ **Auto Plan Creation** - Har message ke liye automatically `plan.md` banata hai
✅ **Auto Move to Done** - Processed messages ko automatically `Done/` folder mein move karta hai
✅ **Continuous Background Running** - Ek baar start karo, chalta rahega
✅ **No Manual Work** - Sab kuch automatic!

## Kaise Kaam Karta Hai (Workflow)

```
┌─────────────────────────────────────────────────────────────┐
│  1. Gmail/WhatsApp se new message aata hai                   │
│         ↓                                                     │
│  2. Auto Processor detect karta hai (keywords check)         │
│         ↓                                                     │
│  3. Automatically plan.md banata hai (Plans folder mein)     │
│         ↓                                                     │
│  4. Automatically Done folder mein move karta hai            │
│         ↓                                                     │
│  5. Processed mark karta hai (duplicate avoid)               │
│         ↓                                                     │
│  6. Wait karta hai next message ke liye                      │
└─────────────────────────────────────────────────────────────┘
```

## Installation (Pehli Baar Setup)

### Step 1: Dependencies Install Karein

```bash
# Playwright install karein (WhatsApp ke liye)
pip install playwright
python -m playwright install chromium

# Optional: Qwen API (AI plans ke liye)
pip install dashscope
```

### Step 2: API Keys Setup (Optional)

```bash
# Gmail API (agar real Gmail integration chahiye)
# credentials.json Dalein AI_Employee_Vault/Silver_Tier/ mein

# Qwen API (AI-generated plans ke liye)
export DASHSCOPE_API_KEY="sk-your-api-key"
```

## Usage (Istemal)

### Method 1: Batch File Se (Aasaan)

```bash
# Double click karein ya run karein:
start_auto_processor.bat
```

### Method 2: Command Line Se

```bash
# Basic run (default settings)
python auto_processor.py

# Custom intervals (Gmail har 3 min, WhatsApp har 5 min)
python auto_processor.py --gmail-interval 180 --whatsapp-interval 300

# Sirf 10 cycles chalana hai (testing ke liye)
python auto_processor.py --max-iterations 10

# Plans automatic nahi chahiye
python auto_processor.py --no-plans

# Done folder mein move nahi karna
python auto_processor.py --no-done
```

### Method 3: Background Mein (Windows Task Scheduler)

```bash
# Task Scheduler mein add karein:
# Program: C:\Python\python.exe
# Arguments: C:\path\to\auto_processor.py
# Start in: C:\path\to\h.p_hack_0
# Trigger: At startup / At log on
```

## Configuration (Settings)

### Default Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Gmail Check Interval | 300s (5 min) | Kitni der baad Gmail check ho |
| WhatsApp Check Interval | 300s (5 min) | Kitni der baad WhatsApp check ho |
| Auto Create Plans | ✅ Yes | Automatically plan.md banega |
| Auto Move to Done | ✅ Yes | Automatically Done folder mein jayega |
| Max Iterations | 0 (forever) | 0 = hamesha chalta rahega |

### Keywords (Detect hone wale words)

Default keywords jo detect honge:
- `urgent`
- `invoice`
- `payment`
- `asap`
- `important`
- `action required`

### Custom Keywords

Script edit karein aur `CONFIG` dictionary mein add karein:

```python
CONFIG = {
    'keywords': ['urgent', 'invoice', 'payment', 'asap', 'important', 'your_keyword']
}
```

## Output (Kya Banega)

### 1. Plans Folder (`Plans/`)

Har message ke liye ek `plan_*.md` file:

```markdown
---
metadata:
  message_id: "Gmail_20260322_123456"
  source: "gmail"
  from: "boss@company.com"
  subject: "Urgent: Meeting Tomorrow"
  priority: "high"
  keywords: ["urgent"]
  created: "2026-03-22T12:35:00"
---

# Action Plan: Urgent: Meeting Tomorrow

## Message Information
| Field | Value |
|-------|-------|
| **Source** | GMAIL |
| **From** | boss@company.com |
| **Priority** | HIGH |
| **Keywords** | urgent |

## Content
[Message content here...]

## Action Items
- [ ] Review message content
- [ ] Identify required actions
- [ ] Respond if needed (gmail)
- [ ] Complete required tasks
- [ ] Verify completion
- [ ] Mark as done
```

### 2. Done Folder (`AI_Employee_Vault/Silver_Tier/Done/`)

Processed messages yahan move honge with reference to plan file.

### 3. Logs (`logs/auto_processor.log`)

Detailed logs:
```
2026-03-22 12:35:00 - auto_processor - INFO - Checking Gmail for new emails...
2026-03-22 12:35:01 - auto_processor - INFO - Found 2 new emails
2026-03-22 12:35:02 - auto_processor - INFO - Processing: Gmail_20260322_123456
2026-03-22 12:35:02 - auto_processor - INFO -   From: boss@company.com
2026-03-22 12:35:02 - auto_processor - INFO -   Keywords: ['urgent']
2026-03-22 12:35:03 - auto_processor - INFO - Plan created: plan_Gmail_20260322_123456_20260322_123503.md
2026-03-22 12:35:04 - auto_processor - INFO - Moved to Done: Gmail_20260322_123456.md
2026-03-22 12:35:04 - auto_processor - INFO - [OK] Processed successfully
```

## Examples (Misalein)

### Example 1: Basic Usage

```bash
# Start auto processor
python auto_processor.py

# Output:
# ============================================================
# Auto Processor - Gmail + WhatsApp
# ============================================================
# Vault Path: C:\Users\AA\Desktop\h.p_hack_0
# Gmail Interval: 300s
# WhatsApp Interval: 300s
# Auto Create Plans: True
# Auto Move to Done: True
# Keywords: ['urgent', 'invoice', 'payment', 'asap', 'important', 'action required']
# ============================================================
#
# Press Ctrl+C to stop
```

### Example 2: Testing (Limited Runs)

```bash
# Sirf 5 cycles chalao (testing)
python auto_processor.py --max-iterations 5
```

### Example 3: Fast Checking

```bash
# Har 1 minute baad check karo
python auto_processor.py --gmail-interval 60 --whatsapp-interval 60
```

## Troubleshooting (Masail Ka Hal)

### Problem: "Playwright not installed"

**Solution:**
```bash
pip install playwright
python -m playwright install chromium
```

### Problem: "No modules found"

**Solution:**
```bash
# Required packages install karein
pip install playwright dashscope
```

### Problem: Script start nahi ho rahi

**Solution:**
```bash
# Check Python path
where python

# Full path se chalayein
C:\Python39\python.exe auto_processor.py
```

### Problem: Messages process nahi ho rahe

**Solution:**
1. Check `logs/auto_processor.log`
2. Verify keywords match message content
3. Check file permissions
4. Ensure folders exist

## File Structure (Files Kahan Hain)

```
h.p_hack_0/
├── auto_processor.py              # Main script
├── start_auto_processor.bat       # Windows batch file
├── AUTO_PROCESSOR_README.md       # This file
├── logs/
│   └── auto_processor.log         # Logs
├── Plans/
│   └── plan_*.md                  # Generated plans
└── AI_Employee_Vault/
    └── Silver_Tier/
        ├── Needs_Action/          # Incoming messages
        └── Done/                  # Processed messages
```

## Advanced Usage (Mahir Istemal)

### Integrate with Qwen API (AI Plans)

Agar aap AI-generated plans chahte hain:

```python
# auto_processor.py mein PlanGenerator class edit karein
def _generate_plan_content(self, message: Message) -> str:
    if QWEN_AVAILABLE and os.getenv('DASHSCOPE_API_KEY'):
        # Call Qwen API for AI-generated plan
        response = Generation.call(
            model='qwen-plus',
            prompt=f"Create action plan for: {message.content}"
        )
        return response.output.choices[0].message.content
    else:
        # Use default template
        return self._default_template(message)
```

### Custom Processing Logic

Apna custom logic add karne ke liye `AutoProcessor.process_message()` ko edit karein:

```python
def process_message(self, message: Message):
    # Custom logic here
    if 'invoice' in message.keywords_found:
        # Special handling for invoices
        self._process_invoice(message)
    elif 'urgent' in message.keywords_found:
        # Priority handling
        self._process_urgent(message)
    else:
        # Normal processing
        self._process_normal(message)
```

## Best Practices (Behtareen Tareeqay)

1. **Start with Testing** - Pehle `--max-iterations 5` se test karein
2. **Check Logs Regularly** - `logs/auto_processor.log` monitor karte rahein
3. **Adjust Intervals** - Zaroorat ke mutabiq intervals set karein
4. **Backup Plans** - `Plans/` folder ka regular backup lein
5. **Clean Done Folder** - Periodically `Done/` folder archive karein

## Security Notes (Hifazati Hidayat)

⚠ **Important:**
- API keys ko secure rakhein
- `credentials.json` ko share na karein
- Logs mein sensitive information ho sakti hai
- Regular backups lein

## Support (Madad)

Agar koi masla ho:

1. Check logs: `logs/auto_processor.log`
2. Verify configuration
3. Test with `--max-iterations 1`
4. Check folder permissions

---

**Version:** 1.0.0
**Created:** 2026-03-22
**Author:** AI Employee Vault

*Last Updated: 2026-03-22 23:15*
