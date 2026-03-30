# Gmail Watcher Cron Scheduler

This component implements cron-style scheduling to run the Gmail watcher every 5 minutes.

## Components

1. **gmail_cron_scheduler.py**: Main scheduler script that runs the email check every 5 minutes
2. **start_gmail_cron_scheduler.bat**: Windows batch file to start the scheduler
3. **requirements_cron.txt**: Dependencies for the scheduler
4. **schedule_gmail_watcher.bat**: Alternative implementation (deprecated)

## How It Works

The scheduler uses the Python `schedule` library to run the Gmail email checking function every 5 minutes. Rather than running the entire `gmail_poller.py` script (which has its own internal polling), it calls just the email checking function to avoid conflicts.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements_cron.txt
   ```

2. Run the scheduler:
   - On Windows: Double-click `start_gmail_cron_scheduler.bat` or run `python gmail_cron_scheduler.py`

## Features

- Runs email check every 5 minutes as requested
- Proper logging of scheduled tasks
- Error handling for robust operation
- Compatible with Windows systems

## Note

This implementation works alongside the existing `gmail_poller.py` functionality. If you run both simultaneously, you may get duplicate checks. Use either the internal polling of `gmail_poller.py` OR this cron scheduler, not both.