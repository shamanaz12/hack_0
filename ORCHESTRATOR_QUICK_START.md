# Orchestrator - Fully Automatic Gmail + WhatsApp Processor

## 🚀 Quick Start (Urdu/Hindi)

### Yeh System Kya Karta Hai?

```
Gmail → New Email aaya → Auto Process → Done ✅
WhatsApp → New Message aaya → Auto Process → Done ✅
```

**Sab kuch AUTOMATIC!** Aapko kuch nahi karna, bas system chalana hai.

---

## 📦 Installation (3 Steps)

### Step 1: Dependencies Install karein

```bash
pip install dashscope watchdog playwright
playwright install chromium
```

### Step 2: API Key set karein (Optional)

Real AI responses ke liye:
```bash
set DASHSCOPE_API_KEY=sk-your-api-key
```

**Note:** API key nahi hai to **simulated mode** mein chalega (placeholder responses).

### Step 3: System Start karein

```bash
# Double click karein ya run karein:
start_orchestrator.bat
```

---

## 🎯 Kaise Kaam Karta Hai?

### Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                             │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Gmail        │      │ WhatsApp     │                    │
│  │ Watcher      │      │ Watcher      │                    │
│  │ (5 min)      │      │ (5 min)      │                    │
│  └──────┬───────┘      └──────┬───────┘                    │
│         │                     │                             │
│         └──────────┬──────────┘                             │
│                    │                                        │
│                    ▼                                        │
│         ┌─────────────────────┐                             │
│         │  Needs_Action/      │                             │
│         │  (New .md files)    │                             │
│         └──────────┬──────────┘                             │
│                    │                                        │
│                    ▼                                        │
│         ┌─────────────────────┐                             │
│         │  Ralph Loop (AI)    │                             │
│         │  Auto Process       │                             │
│         └──────────┬──────────┘                             │
│                    │                                        │
│                    ▼                                        │
│         ┌─────────────────────┐                             │
│         │  Done/ Folder       │                             │
│         │  (Completed ✅)     │                             │
│         └─────────────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step Process

1. **Gmail Check** (har 5 minute baad)
   - `gmail_watcher.py` run hota hai
   - Naye emails check hote hain
   - Keywords match hone par `.md` file banti hai
   - File `Needs_Action/` folder mein save hoti hai

2. **WhatsApp Check** (har 5 minute baad)
   - `whatsapp_watcher.py` run hota hai
   - Naye messages check hote hain
   - Keywords match hone par `.md` file banti hai
   - File `Needs_Action/` folder mein save hoti hai

3. **Auto Processing** (continuous)
   - Orchestrator `Needs_Action/` mein nayi files detect karta hai
   - Ralph Loop (AI) se process karta hai
   - Plan file banata hai (`plans/` folder mein)
   - Original file ko `Done/` mein move kar deta hai

4. **Logging & Dashboard**
   - Sab kuch log hota hai: `logs/orchestrator.log`
   - Dashboard update hota hai: `Dashboard.md`

---

## 📝 Commands

### Start karein

```bash
# Continuous run (24/7 chalega)
python orchestrator.py

# Ya batch file use karein
start_orchestrator.bat
```

### Status check karein

```bash
python orchestrator.py --status
```

### Existing files process karein (ek baar)

```bash
python orchestrator.py --once
```

### Custom intervals

```bash
# Gmail har 2 minute, WhatsApp har 10 minute
python orchestrator.py --gmail-interval 120 --whatsapp-interval 600
```

### All options

```bash
python orchestrator.py --help
```

---

## 📁 Folder Structure

```
h.p_hack_0/
├── AI_Employee_Vault/
│   └── Silver_Tier/
│       ├── Needs_Action/     ← New files yahan aate hain
│       ├── Processing/       ← Files jo abhi process ho rahi hain
│       ├── Done/             ✅ Completed files
│       └── Error/            ❌ Failed files
├── plans/                    ← AI generated plans
├── logs/
│   └── orchestrator.log      ← Full logs
├── gmail_watcher.py          ← Gmail checker
├── whatsapp_watcher.py       ← WhatsApp checker
├── orchestrator.py           ← Main controller
└── start_orchestrator.bat    ← Quick start
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# API Key (optional)
set DASHSCOPE_API_KEY=sk-your-api-key

# Check intervals (seconds)
set GMAIL_INTERVAL=300        # Default: 5 minutes
set WHATSAPP_INTERVAL=300     # Default: 5 minutes

# Max AI iterations
set MAX_ITERATIONS=10

# Polling interval
set POLL_INTERVAL=5           # File check interval
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--gmail-interval N` | Gmail check every N seconds | 300 |
| `--whatsapp-interval N` | WhatsApp check every N seconds | 300 |
| `--max-iterations N` | Max AI iterations per task | 10 |
| `--interval N` | File polling interval | 5 |
| `--no-watchers` | Disable auto Gmail/WhatsApp check | - |
| `--once` | Process existing files once | - |
| `--status` | Show status and exit | - |

---

## 🔍 Monitoring

### Status Check

```bash
python orchestrator.py --status
```

Output example:
```
============================================================
ORCHESTRATOR STATUS
============================================================
Mode: polling
API Configured: Yes
Running: Yes

Folder Status:
  Needs_Action: 3 files
  Gmail_Files: 2 files
  WhatsApp_Files: 1 files
  Processing: 0 files
  Done: 15 files
  Error: 0 files

Processing History:
  total: 15
  completed: 15
  error: 0
  processing: 0

Watcher Intervals:
  Gmail: Every 300s
  WhatsApp: Every 300s
============================================================
```

### Logs Dekhein

```bash
# Live logs (PowerShell)
Get-Content logs/orchestrator.log -Wait -Tail 50

# Ya simple
type logs/orchestrator.log
```

---

## 🛠️ Troubleshooting

### "Simulated mode" warning

```
WARNING: Qwen API not configured - using simulated mode
```

**Solution:** API key set karein:
```bash
set DASHSCOPE_API_KEY=sk-your-api-key
```

### WhatsApp not working

```
[INFO] playwright not installed - WhatsApp monitoring disabled
```

**Solution:**
```bash
pip install playwright
playwright install chromium
```

### Gmail not working

Check:
1. `gmail_config.json` mein credentials sahi hain
2. App password set hai
3. IMAP enabled hai Gmail mein

### Files stuck in Needs_Action/

Check logs:
```bash
type logs/orchestrator.log
```

Possible issues:
- API key nahi hai (simulated mode slow hai)
- Max iterations kam hain
- File format galat hai

### High CPU usage

Increase intervals:
```bash
python orchestrator.py --gmail-interval 600 --whatsapp-interval 600
```

---

## 📊 24/7 Running (Windows)

### Option 1: Task Scheduler (Recommended)

1. **Task Scheduler** open karein
2. **Create Basic Task** click karein
3. Name: "Orchestrator"
4. Trigger: **When I log on**
5. Action: **Start a program**
6. Program: `C:\path\to\start_orchestrator.bat`
7. Finish click karein

### Option 2: Startup Folder

```bash
# Startup folder open karein
shell:startup

# start_orchestrator.bat ko yahan copy karein
```

### Option 3: Manual Background Run

```bash
# Background mein start karein
start "" python orchestrator.py --background
```

---

## 📋 Example Output

### Start hone par:
```
============================================================
Orchestrator - Fully Automatic Gmail + WhatsApp Processor
============================================================
Vault: C:\Users\AA\Desktop\h.p_hack_0
Mode: polling
Polling Interval: 5s
Gmail Check: Every 300s
WhatsApp Check: Every 300s
Max Iterations: 10
API Key: Configured
Auto-run Watchers: True
============================================================

System will automatically:
  1. Check Gmail for new emails
  2. Check WhatsApp for new messages
  3. Process all files using AI (Ralph Loop)
  4. Move processed files to Done folder
============================================================

Press Ctrl+C to stop
```

### Jab new email aaye:
```
2026-03-23 14:30:00 - orchestrator - INFO - Running Gmail watcher...
2026-03-23 14:30:05 - orchestrator - INFO - Gmail watcher completed
2026-03-23 14:30:06 - orchestrator - INFO - Found 1 new file: Gmail_20260323_143005.md
2026-03-23 14:30:07 - orchestrator - INFO - Processing: Gmail_20260323_143005.md
2026-03-23 14:30:08 - orchestrator - INFO - Ralph Loop - Starting
2026-03-23 14:30:15 - orchestrator - INFO - ✓ Task marked as COMPLETE!
2026-03-23 14:30:16 - orchestrator - INFO - [OK] Completed in 2 iterations
2026-03-23 14:30:17 - orchestrator - INFO - Moved: Gmail_20260323_143005.md -> Done/
```

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] API key set (optional)
- [ ] `start_orchestrator.bat` run kiya
- [ ] Status check kiya (`--status`)
- [ ] Logs check kiye
- [ ] `Done/` folder mein files aa rahi hain

---

## 📞 Support

Agar koi issue ho to:

1. **Logs check karein:** `logs/orchestrator.log`
2. **Status check karein:** `python orchestrator.py --status`
3. **Folders check karein:** `Needs_Action/`, `Done/`, `Error/`

---

## 🎉 That's It!

Ab aapka system fully automatic hai:

- ✉️ **Gmail** → Auto process → ✅ Done
- 💬 **WhatsApp** → Auto process → ✅ Done

**Bas `start_orchestrator.bat` run karte raho!**
