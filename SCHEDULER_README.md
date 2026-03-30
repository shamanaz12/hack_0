# Task Scheduler - Automatic Time-Based Task Execution

## Overview

The **Scheduler** automatically runs tasks at specific times using Python's `schedule` library.

### Features

- ✅ **Time-based scheduling** - Run tasks at specific times
- ✅ **Daily briefings** - Auto-generate at 8 AM
- ✅ **Weekly reports** - Auto-generate Monday at 9 AM
- ✅ **Continuous monitoring** - Gmail/WhatsApp/Orchestrator checks
- ✅ **Fallback mode** - Works without `schedule` library (simple loop)
- ✅ **Full logging** - All activity logged to `logs/scheduler.log`

---

## Installation

```bash
pip install schedule
```

---

## Quick Start

### Run Scheduler (24/7)

```bash
python scheduler.py
```

### Or use batch file

```bash
start_scheduler.bat
```

---

## Scheduled Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| **Gmail Watcher** | Every 5 min | Check for new emails |
| **WhatsApp Watcher** | Every 5 min | Check for new messages |
| **Orchestrator** | Every 1 min | Process pending files |
| **Daily Briefing** | Daily at 08:00 | Generate daily summary |
| **Weekly Report** | Monday at 09:00 | Generate weekly report |
| **Cleanup** | Daily at 03:00 | Delete old log files |

---

## Commands

### Start Scheduler

```bash
# Continuous run
python scheduler.py

# Or
start_scheduler.bat
```

### Check Status

```bash
python scheduler.py --status
```

### Run All Tasks Once

```bash
python scheduler.py --once
```

### Custom Schedule

```bash
# Custom daily briefing time
python scheduler.py --daily-briefing 09:30

# Custom weekly report (Wednesday 2 PM)
python scheduler.py --weekly-report "wednesday,14:00"

# Custom vault path
python scheduler.py --vault "C:\path\to\vault"
```

---

## Configuration

### Environment Variables

```bash
# Vault base path
set VAULT_PATH=C:\Users\AA\Desktop\h.p_hack_0

# Check intervals (minutes)
set GMAIL_INTERVAL=5
set WHATSAPP_INTERVAL=5
set ORCHESTRATOR_INTERVAL=1

# Daily briefing time (HH:MM)
set DAILY_BRIEFING_TIME=08:00

# Weekly report (day,HH:MM)
set WEEKLY_REPORT_DAY=monday
set WEEKLY_REPORT_TIME=09:00
```

---

## Integration with Orchestrator

The scheduler integrates with `orchestrator.py`:

```
┌─────────────────────────────────────────┐
│           SCHEDULER                     │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Scheduled Tasks                │   │
│  │  - Gmail (every 5 min)          │   │
│  │  - WhatsApp (every 5 min)       │   │
│  │  - Orchestrator (every 1 min)   │   │
│  │  - Daily Briefing (8 AM)        │   │
│  │  - Weekly Report (Mon 9 AM)     │   │
│  └─────────────────────────────────┘   │
│           │                             │
│           ▼                             │
│  ┌─────────────────────────────────┐   │
│  │  orchestrator.py                │   │
│  │  - Process files                │   │
│  │  - Ralph Loop (AI)              │   │
│  │  - Move to Done                 │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## Example Output

### Status Check

```
============================================================
SCHEDULER STATUS
============================================================
Running: True
Schedule Library: True
Tasks Executed: 15

Recent Tasks:
  [OK] gmail_watcher at 2026-03-23T14:55:30
  [OK] whatsapp_watcher at 2026-03-23T14:56:37
  [OK] orchestrator at 2026-03-23T14:58:02
  [OK] daily_briefing at 2026-03-23T14:58:02
============================================================
```

### Running Tasks Once

```
Running all tasks once...

[INFO] Running Gmail watcher...
[INFO] Gmail watcher completed: 1

[INFO] Running WhatsApp watcher...
[INFO] WhatsApp watcher completed: 0

[INFO] Running orchestrator (once)...
[INFO] Orchestrator completed: 1

[INFO] Generating daily briefing...
[INFO] Daily briefing created: plans\daily_briefing_2026-03-23.md

[OK] All tasks completed
```

---

## Generated Files

### Daily Briefing

Location: `plans/daily_briefing_YYYY-MM-DD.md`

```markdown
---
metadata:
  type: "Daily Briefing"
  date: "2026-03-23"
  generated_at: "2026-03-23T08:00:00"
---

# Daily Briefing - 2026-03-23

## Summary
| Metric | Value |
|--------|-------|
| **Files Processed** | 5 |
| **Generated At** | 08:00:00 |

## Files Processed Today
- [x] Gmail_20260323_012819.md
- [x] Gmail_20260323_012820.md
...
```

### Weekly Report

Location: `plans/weekly_report_YYYY-MM-DD.md`

```markdown
---
metadata:
  type: "Weekly Report"
  week: 13
  date: "2026-03-23"
---

# Weekly Report - Week 13

## Summary
| Metric | Value |
|--------|-------|
| **Total Files Processed** | 25 |
...
```

---

## Running 24/7

### Option 1: Task Scheduler (Windows)

1. Open **Task Scheduler**
2. Create **Basic Task**
3. Name: "Task Scheduler"
4. Trigger: **When I log on**
5. Action: **Start a program**
6. Program: `C:\path\to\start_scheduler.bat`
7. Finish

### Option 2: Startup Folder

```bash
# Open startup folder
shell:startup

# Copy start_scheduler.bat here
```

### Option 3: Background Run

```bash
start "" python scheduler.py --background
```

---

## Logs

All activity logged to: `logs/scheduler.log`

```
2026-03-23 14:55:00 - scheduler - INFO - Task Scheduler initialized
2026-03-23 14:55:00 - scheduler - INFO - Setting up schedule...
2026-03-23 14:55:00 - scheduler - INFO - Scheduled: Gmail watcher (every 5 min)
2026-03-23 14:55:00 - scheduler - INFO - Scheduled: WhatsApp watcher (every 5 min)
2026-03-23 14:55:00 - scheduler - INFO - Scheduled: Orchestrator (every 1 min)
2026-03-23 14:55:00 - scheduler - INFO - Scheduled: Daily briefing (at 08:00)
2026-03-23 14:55:00 - scheduler - INFO - Scheduled: Weekly report (Monday at 09:00)
2026-03-23 14:55:00 - scheduler - INFO - Starting Task Scheduler
```

---

## Custom Tasks

Add your own scheduled tasks:

```python
# In scheduler.py, add to ScheduledTasks class

def my_custom_task(self):
    """My custom scheduled task"""
    self.logger.info("Running custom task...")
    
    # Your code here
    
    self._record_task('my_custom_task', True)

# In setup_schedule method, add:
schedule.every().day.at("10:00").do(
    self.tasks.my_custom_task
)
```

---

## Troubleshooting

### "schedule library not installed"

```bash
pip install schedule
```

### Tasks not running

Check logs:
```bash
type logs\scheduler.log
```

### High CPU usage

Increase intervals:
```bash
set GMAIL_INTERVAL=10
set WHATSAPP_INTERVAL=10
set ORCHESTRATOR_INTERVAL=5
```

---

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETE SYSTEM                          │
│                                                             │
│  ┌──────────────┐     ┌──────────────┐                    │
│  │  scheduler.py│────▶│  gmail_      │                    │
│  │  (Time-based)│     │  watcher.py  │                    │
│  │              │     └──────────────┘                    │
│  │              │           │                             │
│  │              │     ┌──────────────┐                    │
│  │              │────▶│  whatsapp_   │                    │
│  │              │     │  watcher.py  │                    │
│  │              │     └──────────────┘                    │
│  │              │           │                             │
│  │              │     ┌──────────────┐                    │
│  │              │────▶│  orchestrator│                    │
│  │              │     │  .py         │                    │
│  │              │     └──────────────┘                    │
│  │              │           │                             │
│  │              │           ▼                             │
│  │              │     ┌──────────────┐                    │
│  └──────────────┘     │  Done/       │                    │
│                       │  (Completed) │                    │
│                       └──────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Best Practices

1. **Run scheduler 24/7** - Use Task Scheduler or startup
2. **Monitor logs** - Check `logs/scheduler.log` regularly
3. **Adjust intervals** - Based on your needs
4. **Review briefings** - Check daily/weekly reports
5. **Backup state** - Keep scheduler state backed up

---

## Summary

| Component | Purpose |
|-----------|---------|
| `scheduler.py` | Time-based task scheduling |
| `orchestrator.py` | File processing with AI |
| `gmail_watcher.py` | Email monitoring |
| `whatsapp_watcher.py` | WhatsApp monitoring |

**All working together for fully automatic processing!** ✅
