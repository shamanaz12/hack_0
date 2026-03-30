# Orchestrator - Automatic Task Processor

## Overview

The **Orchestrator** automatically watches the `Needs_Action/` folder for new `.md` files and processes them using the **Ralph Wiggum Loop** pattern (iterative AI task execution).

### Workflow

```
Needs_Action/  →  Processing/  →  Done/
                      ↓
                  Error/ (on failure)
                      
Plans/ ← Created during processing
```

## Features

- ✅ **Automatic File Watching** - Uses watchdog (efficient) or polling (fallback)
- ✅ **Duplicate Prevention** - Tracks processed files to avoid re-processing
- ✅ **Error Handling** - Failed files moved to `Error/` folder
- ✅ **State Persistence** - Processing state saved to `orchestrator_state.json`
- ✅ **Logging** - Full logging to `logs/orchestrator.log`
- ✅ **Dashboard Updates** - Auto-updates `Dashboard.md` with status
- ✅ **Plan Generation** - Creates plan files in `plans/` folder
- ✅ **Graceful Shutdown** - Clean stop on Ctrl+C

## Installation

### 1. Install Dependencies

```bash
# Required (minimum)
pip install dashscope

# Recommended (for efficient file watching)
pip install watchdog

# Or install all at once
pip install dashscope watchdog
```

### 2. Configure API Key (Optional but Recommended)

Set the Qwen API key for real AI responses:

```bash
# Windows (Command Prompt)
set DASHSCOPE_API_KEY=sk-your-api-key

# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-your-api-key"

# Linux/Mac
export DASHSCOPE_API_KEY="sk-your-api-key"
```

Without an API key, the orchestrator runs in **simulated mode** (placeholder responses).

### 3. Verify Folder Structure

The orchestrator expects this structure:

```
h.p_hack_0/
├── AI_Employee_Vault/
│   └── Silver_Tier/
│       ├── Needs_Action/    ← Drop new .md files here
│       ├── Processing/      ← Files being processed
│       ├── Done/            ← Completed files
│       └── Error/           ← Failed files
├── plans/                   ← Generated plan files
├── logs/                    ← Logs
│   └── orchestrator.log
└── orchestrator.py          ← This script
```

Folders are created automatically if missing.

## Usage

### Basic Commands

```bash
# Run continuously (watches for new files)
python orchestrator.py

# Run once (process existing files, then exit)
python orchestrator.py --once

# Show current status
python orchestrator.py --status

# Run with custom vault path
python orchestrator.py --vault "C:\path\to\vault"
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--vault PATH` | Vault base path | Current directory |
| `--once` | Run once, then exit | Continuous |
| `--polling` | Force polling mode | Auto-detect |
| `--interval SECONDS` | Polling interval | 5.0 |
| `--max-iterations N` | Max AI iterations | 10 |
| `--status` | Show status and exit | - |
| `--background` | Run in background | Same as default |

### Examples

```bash
# Process files every 10 seconds
python orchestrator.py --interval 10

# Limit AI to 15 iterations per task
python orchestrator.py --max-iterations 15

# Run once on existing files
python orchestrator.py --once

# Check status
python orchestrator.py --status
```

## Running 24/7

### Option 1: Windows Task Scheduler

1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Name: "Orchestrator"
4. Trigger: **When I log on** (or specific time)
5. Action: **Start a program**
6. Program: `python.exe`
7. Arguments: `orchestrator.py --background`
8. Start in: `C:\Users\AA\Desktop\h.p_hack_0`

### Option 2: Windows Batch File + Startup

Create `start_orchestrator.bat`:

```batch
@echo off
cd /d "C:\Users\AA\Desktop\h.p_hack_0"
python orchestrator.py --background
```

Copy the batch file to Windows Startup folder:
- Press `Win + R`
- Type: `shell:startup`
- Paste the batch file

### Option 3: Run as Windows Service (Advanced)

Use [NSSM](https://nssm.cc/):

```bash
# Download nssm.exe and run:
nssm install Orchestrator

# Configure:
#   Path: C:\Python39\python.exe
#   Arguments: orchestrator.py
#   Startup: C:\Users\AA\Desktop\h.p_hack_0

nssm start Orchestrator
```

### Option 4: Linux/Mac (systemd)

Create `/etc/systemd/system/orchestrator.service`:

```ini
[Unit]
Description=Orchestrator Auto Processor
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/h.p_hack_0
ExecStart=/usr/bin/python3 orchestrator.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable orchestrator
sudo systemctl start orchestrator
sudo systemctl status orchestrator
```

### Option 5: Screen/Tmux (Linux/Mac)

```bash
# Using screen
screen -S orchestrator
python orchestrator.py
# Ctrl+A, D to detach

# Using tmux
tmux new -s orchestrator
python orchestrator.py
# Ctrl+B, D to detach
```

## How It Works

### 1. File Detection

- **Watchdog mode**: Listens for file system events (efficient)
- **Polling mode**: Checks folder every N seconds (fallback)

### 2. Processing Flow

```
1. New .md file detected in Needs_Action/
2. Check if already processed (via hash)
3. Move to Processing/ folder
4. Extract task prompt from file content
5. Run Ralph Loop (iterative AI)
6. Create plan file in plans/
7. Move to Done/ (or Error/ on failure)
8. Update state and dashboard
```

### 3. Ralph Loop

The reasoning loop:
1. Builds prompt with task + previous iterations
2. Calls Qwen API
3. Parses response for `<promise>COMPLETE</promise>`
4. Repeats until complete or max iterations

### 4. State Management

State saved to `orchestrator_state.json`:
- File hashes (prevents duplicates)
- Processing status
- Iteration counts
- Error messages

## Logging

All activity logged to `logs/orchestrator.log`:

```
2026-03-23 10:30:00 - orchestrator - INFO - File Orchestrator initialized
2026-03-23 10:30:01 - orchestrator - INFO - Starting polling mode (interval: 5.0s)
2026-03-23 10:30:15 - orchestrator - INFO - New file detected: Gmail_20260323_103010.md
2026-03-23 10:30:16 - orchestrator - INFO - Processing: Gmail_20260323_103010.md
2026-03-23 10:30:17 - orchestrator - INFO - Ralph Loop - Starting
2026-03-23 10:30:18 - orchestrator - INFO - Iteration 1 / 10
2026-03-23 10:30:25 - orchestrator - INFO - ✓ Task marked as COMPLETE!
2026-03-23 10:30:26 - orchestrator - INFO - [OK] Completed in 3 iterations
```

## Dashboard

The orchestrator updates `AI_Employee_Vault/Dashboard.md` with:

- Current status (running/stopped)
- Folder file counts
- Processing history (total, completed, errors)
- Last update timestamp

## Troubleshooting

### "No files being processed"

- Ensure files are `.md` extension
- Check files are in `AI_Employee_Vault/Silver_Tier/Needs_Action/`
- Run `--status` to verify folder paths

### "Simulated mode" warning

```
WARNING: Qwen API not configured - using simulated mode
```

**Solution**: Set `DASHSCOPE_API_KEY` environment variable

### "watchdog not installed"

```
Note: watchdog not installed. Using polling mode.
```

**Solution**: Install watchdog: `pip install watchdog`

### Files stuck in Processing/

- Check `logs/orchestrator.log` for errors
- Manually move files back to `Needs_Action/`
- Restart orchestrator

### API errors

```
ERROR: API call failed after 5 attempts
```

**Solutions**:
1. Verify API key: `echo %DASHSCOPE_API_KEY%`
2. Check network connection
3. Review API quota/limits

### High CPU usage

- Increase polling interval: `--interval 10`
- Ensure watchdog is installed (more efficient)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VAULT_PATH` | Current dir | Base vault path |
| `DASHSCOPE_API_KEY` | (none) | Qwen API key |
| `MODEL_NAME` | qwen-plus | Qwen model |
| `MAX_ITERATIONS` | 10 | Max loop iterations |
| `POLL_INTERVAL` | 5.0 | Polling interval (seconds) |
| `BACKOFF_BASE` | 2.0 | Retry backoff base |
| `BACKOFF_MAX` | 60.0 | Max retry delay |

## File Formats

### Input File (Needs_Action/)

```markdown
---
metadata:
  from: "sender@example.com"
  subject: "Urgent: Review document"
  priority: "high"
---

# Email: Review document

Please review the attached document and provide feedback by EOD.

Action items:
- Review content
- Provide feedback
- Send response
```

### Output Plan (plans/)

```markdown
---
metadata:
  source_file: "Gmail_20260323_103010.md"
  created: "2026-03-23T10:30:26"
  status: "completed"
  iterations: 3
---

# Plan: Gmail_20260323_103010.md

## Processing Summary
| Field | Value |
|-------|-------|
| **Status** | completed |
| **Iterations** | 3 |

## Iteration History

### Iteration 1
**Action:** Analyze task requirements
**Result:** Requirements documented
...
```

## Best Practices

1. **Set API Key** - Real AI responses are much better than simulated
2. **Monitor Logs** - Check `logs/orchestrator.log` regularly
3. **Review Error Folder** - Check `Error/` for failed files
4. **Adjust Max Iterations** - Complex tasks may need more iterations
5. **Run as Service** - Use Task Scheduler for 24/7 operation
6. **Backup State** - Keep `orchestrator_state.json` backed up

## Integration

### With Gmail Watcher

Gmail watcher creates files → Orchestrator processes them:

```
gmail_watcher.py → Needs_Action/ → orchestrator.py → Done/
```

### With WhatsApp Watcher

Same flow:

```
whatsapp_watcher.py → Needs_Action/ → orchestrator.py → Done/
```

### Manual File Drop

Just drop `.md` files into `Needs_Action/`:

```
1. Create task.md
2. Drop into AI_Employee_Vault/Silver_Tier/Needs_Action/
3. Orchestrator auto-processes
4. Check Done/ for result
```

## Status Commands

```bash
# Quick status
python orchestrator.py --status

# View logs (last 50 lines)
tail -50 logs/orchestrator.log

# Check processed files
cat orchestrator_state.json | python -m json.tool
```

## Support

For issues:
1. Check `logs/orchestrator.log`
2. Verify folder structure
3. Confirm API key (if using real AI)
4. Run `--status` for diagnostics
