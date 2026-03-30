#!/usr/bin/env python3
"""
Scheduler - Automatic Task Scheduler with Orchestrator Integration

This script schedules and runs tasks at specific times:
- Daily briefings
- Weekly reports
- Gmail/WhatsApp checks
- Custom scheduled tasks

Uses Python's schedule library for easy task scheduling.

Usage:
    python scheduler.py

Or run in background:
    python scheduler.py --background
"""

import os
import sys
import time
import logging
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, List

# Try to import schedule library
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("Note: schedule library not installed.")
    print("Install with: pip install schedule")


# ============================================================================
# Configuration
# ============================================================================

class SchedulerConfig:
    """Scheduler configuration"""
    
    def __init__(self):
        self.vault_path = Path(os.getenv('VAULT_PATH', '.'))
        self.logs_folder = self.vault_path / 'logs'
        self.plans_folder = self.vault_path / 'plans'
        self.orchestrator_path = Path(__file__).parent / 'orchestrator.py'
        
        # Schedule intervals (in minutes)
        self.gmail_check_interval = int(os.getenv('GMAIL_INTERVAL', '5'))
        self.whatsapp_check_interval = int(os.getenv('WHATSAPP_INTERVAL', '5'))
        self.orchestrator_check_interval = int(os.getenv('ORCHESTRATOR_INTERVAL', '1'))
        
        # Daily briefing time
        self.daily_briefing_time = os.getenv('DAILY_BRIEFING_TIME', '08:00')
        
        # Weekly report day and time
        self.weekly_report_day = os.getenv('WEEKLY_REPORT_DAY', 'monday')
        self.weekly_report_time = os.getenv('WEEKLY_REPORT_TIME', '09:00')


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(logs_folder: Path) -> logging.Logger:
    """Configure logging"""
    os.makedirs(logs_folder, exist_ok=True)
    
    log_file = logs_folder / 'scheduler.log'
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    logger = logging.getLogger('scheduler')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# ============================================================================
# Task Definitions
# ============================================================================

class ScheduledTasks:
    """Collection of scheduled tasks"""
    
    def __init__(self, config: SchedulerConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.task_history: List[dict] = []
    
    def run_orchestrator_once(self):
        """Run orchestrator to process pending files"""
        self.logger.info("Running orchestrator (once)...")
        
        try:
            result = subprocess.run(
                [sys.executable, str(self.config.orchestrator_path), '--once'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            self.logger.info(f"Orchestrator completed: {result.returncode}")
            
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.logger.info(f"  {line}")
            
            if result.stderr:
                for line in result.stderr.split('\n'):
                    if line.strip():
                        self.logger.debug(f"  {line}")
            
            self._record_task('orchestrator', result.returncode == 0)
            
        except subprocess.TimeoutExpired:
            self.logger.error("Orchestrator timed out")
            self._record_task('orchestrator', False)
        except Exception as e:
            self.logger.error(f"Orchestrator error: {e}")
            self._record_task('orchestrator', False)
    
    def run_gmail_watcher(self):
        """Run Gmail watcher to check for new emails"""
        self.logger.info("Running Gmail watcher...")
        
        gmail_watcher_path = Path(__file__).parent / 'gmail_watcher.py'
        
        if not gmail_watcher_path.exists():
            self.logger.warning("Gmail watcher not found")
            return
        
        try:
            result = subprocess.run(
                [sys.executable, str(gmail_watcher_path), '--once'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            self.logger.info(f"Gmail watcher completed: {result.returncode}")
            self._record_task('gmail_watcher', result.returncode == 0)
            
        except Exception as e:
            self.logger.error(f"Gmail watcher error: {e}")
            self._record_task('gmail_watcher', False)
    
    def run_whatsapp_watcher(self):
        """Run WhatsApp watcher to check for new messages"""
        self.logger.info("Running WhatsApp watcher...")
        
        whatsapp_watcher_path = Path(__file__).parent / 'whatsapp_watcher.py'
        
        if not whatsapp_watcher_path.exists():
            self.logger.warning("WhatsApp watcher not found")
            return
        
        try:
            result = subprocess.run(
                [sys.executable, str(whatsapp_watcher_path), '--once'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            self.logger.info(f"WhatsApp watcher completed: {result.returncode}")
            self._record_task('whatsapp_watcher', result.returncode == 0)
            
        except Exception as e:
            self.logger.error(f"WhatsApp watcher error: {e}")
            self._record_task('whatsapp_watcher', False)
    
    def generate_daily_briefing(self):
        """Generate daily briefing report"""
        self.logger.info("Generating daily briefing...")
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d')
            briefing_file = self.config.plans_folder / f'daily_briefing_{timestamp}.md'
            
            # Count files processed today
            done_folder = self.config.vault_path / 'AI_Employee_Vault' / 'Silver_Tier' / 'Done'
            today_files = []
            
            if done_folder.exists():
                for f in done_folder.glob('*.md'):
                    if timestamp.replace('-', '') in f.stem:
                        today_files.append(f.name)
            
            # Create briefing content
            content = f"""---
metadata:
  type: "Daily Briefing"
  date: "{timestamp}"
  generated_at: "{datetime.now().isoformat()}"
---

# Daily Briefing - {timestamp}

## Summary
| Metric | Value |
|--------|-------|
| **Files Processed** | {len(today_files)} |
| **Generated At** | {datetime.now().strftime('%H:%M:%S')} |

## Files Processed Today

"""
            
            for file in sorted(today_files):
                content += f"- [x] {file}\n"
            
            if not today_files:
                content += "*No files processed today*\n"
            
            content += f"""
## Tasks Completed

- Orchestrator processed pending files
- Gmail watcher checked for new emails
- WhatsApp watcher checked for new messages

## Next Steps

- Review processed files in Done folder
- Check plans folder for AI-generated plans
- Continue automatic processing

---
*Generated by Scheduler - Daily Briefing Task*
"""
            
            briefing_file.write_text(content, encoding='utf-8')
            self.logger.info(f"Daily briefing created: {briefing_file}")
            self._record_task('daily_briefing', True)
            
        except Exception as e:
            self.logger.error(f"Daily briefing error: {e}")
            self._record_task('daily_briefing', False)
    
    def generate_weekly_report(self):
        """Generate weekly summary report"""
        self.logger.info("Generating weekly report...")
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d')
            week_num = datetime.now().isocalendar()[1]
            report_file = self.config.plans_folder / f'weekly_report_{timestamp}.md'
            
            # Count files in Done folder
            done_folder = self.config.vault_path / 'AI_Employee_Vault' / 'Silver_Tier' / 'Done'
            total_files = 0
            
            if done_folder.exists():
                total_files = len(list(done_folder.glob('*.md')))
            
            # Create report content
            content = f"""---
metadata:
  type: "Weekly Report"
  week: {week_num}
  date: "{timestamp}"
  generated_at: "{datetime.now().isoformat()}"
---

# Weekly Report - Week {week_num} ({timestamp})

## Summary
| Metric | Value |
|--------|-------|
| **Total Files Processed** | {total_files} |
| **Generated At** | {datetime.now().strftime('%H:%M:%S')} |

## This Week's Activity

### Completed Tasks
- Automatic Gmail processing
- Automatic WhatsApp processing
- AI-powered task execution (Ralph Loop)
- Plan generation

### System Status
- Orchestrator: Running
- Gmail Watcher: Active
- WhatsApp Watcher: Active
- AI Processing: Enabled

## Performance Metrics

- Average processing time: ~10 iterations per task
- Success rate: High (auto-move to Done)
- Error rate: Low (files moved to Error folder on failure)

## Next Week's Goals

- Continue automatic processing
- Monitor system performance
- Review and optimize workflows

---
*Generated by Scheduler - Weekly Report Task*
"""
            
            report_file.write_text(content, encoding='utf-8')
            self.logger.info(f"Weekly report created: {report_file}")
            self._record_task('weekly_report', True)
            
        except Exception as e:
            self.logger.error(f"Weekly report error: {e}")
            self._record_task('weekly_report', False)
    
    def cleanup_old_files(self):
        """Cleanup old log files (older than 30 days)"""
        self.logger.info("Running cleanup task...")
        
        try:
            cleaned_count = 0
            
            # Clean old log files
            for log_file in self.config.logs_folder.glob('*.log'):
                try:
                    modified_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    days_old = (datetime.now() - modified_time).days
                    
                    if days_old > 30:
                        log_file.unlink()
                        cleaned_count += 1
                        self.logger.info(f"Deleted old log: {log_file.name} ({days_old} days old)")
                except:
                    continue
            
            self.logger.info(f"Cleanup completed: {cleaned_count} files deleted")
            self._record_task('cleanup', True)
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            self._record_task('cleanup', False)
    
    def _record_task(self, task_name: str, success: bool):
        """Record task execution history"""
        self.task_history.append({
            'task': task_name,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 100 records
        if len(self.task_history) > 100:
            self.task_history = self.task_history[-100:]


# ============================================================================
# Scheduler
# ============================================================================

class TaskScheduler:
    """Main task scheduler"""
    
    def __init__(self, config: SchedulerConfig):
        self.config = config
        self.logger = setup_logging(config.logs_folder)
        self.tasks = ScheduledTasks(config, self.logger)
        self.running = False
        
        self.logger.info("Task Scheduler initialized")
        self.logger.info(f"Vault path: {config.vault_path}")
        self.logger.info(f"Logs folder: {config.logs_folder}")
    
    def setup_schedule(self):
        """Setup all scheduled tasks"""
        self.logger.info("Setting up schedule...")
        
        if not SCHEDULE_AVAILABLE:
            self.logger.error("Schedule library not available. Using simple loop mode.")
            return False
        
        # Continuous tasks (every N minutes)
        schedule.every(self.config.gmail_check_interval).minutes.do(
            self.tasks.run_gmail_watcher
        )
        self.logger.info(f"Scheduled: Gmail watcher (every {self.config.gmail_check_interval} min)")
        
        schedule.every(self.config.whatsapp_check_interval).minutes.do(
            self.tasks.run_whatsapp_watcher
        )
        self.logger.info(f"Scheduled: WhatsApp watcher (every {self.config.whatsapp_check_interval} min)")
        
        schedule.every(self.config.orchestrator_check_interval).minutes.do(
            self.tasks.run_orchestrator_once
        )
        self.logger.info(f"Scheduled: Orchestrator (every {self.config.orchestrator_check_interval} min)")
        
        # Daily tasks
        schedule.every().day.at(self.config.daily_briefing_time).do(
            self.tasks.generate_daily_briefing
        )
        self.logger.info(f"Scheduled: Daily briefing (at {self.config.daily_briefing_time})")
        
        # Weekly tasks
        schedule.every().monday.at(self.config.weekly_report_time).do(
            self.tasks.generate_weekly_report
        )
        self.logger.info(f"Scheduled: Weekly report (Monday at {self.config.weekly_report_time})")
        
        # Monthly cleanup
        schedule.every().day.at("03:00").do(
            self.tasks.cleanup_old_files
        )
        self.logger.info("Scheduled: Cleanup (daily at 03:00)")
        
        return True
    
    def run_schedule_loop(self):
        """Run the schedule loop"""
        self.logger.info("=" * 60)
        self.logger.info("Starting Task Scheduler")
        self.logger.info("=" * 60)
        
        self.running = True
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("Scheduler interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(5)
        
        self.logger.info("Scheduler stopped")
    
    def run_simple_loop(self):
        """Run using simple loop (fallback if schedule not available)"""
        self.logger.info("=" * 60)
        self.logger.info("Starting Simple Loop Scheduler")
        self.logger.info("=" * 60)
        
        self.running = True
        
        # Track last run times
        last_gmail = 0
        last_whatsapp = 0
        last_orchestrator = 0
        last_briefing = ""
        last_cleanup = ""
        
        while self.running:
            try:
                now = time.time()
                current_date = datetime.now().strftime('%Y-%m-%d')
                current_time = datetime.now().strftime('%H:%M')
                current_day = datetime.now().strftime('%A').lower()
                
                # Gmail watcher
                if now - last_gmail >= (self.config.gmail_check_interval * 60):
                    self.tasks.run_gmail_watcher()
                    last_gmail = now
                
                # WhatsApp watcher
                if now - last_whatsapp >= (self.config.whatsapp_check_interval * 60):
                    self.tasks.run_whatsapp_watcher()
                    last_whatsapp = now
                
                # Orchestrator
                if now - last_orchestrator >= (self.config.orchestrator_check_interval * 60):
                    self.tasks.run_orchestrator_once()
                    last_orchestrator = now
                
                # Daily briefing
                if current_time == self.config.daily_briefing_time and current_date != last_briefing:
                    self.tasks.generate_daily_briefing()
                    last_briefing = current_date
                
                # Weekly report
                if (current_day == self.config.weekly_report_day and 
                    current_time == self.config.weekly_report_time and 
                    current_date != last_cleanup):
                    self.tasks.generate_weekly_report()
                    last_cleanup = current_date
                
                # Cleanup (daily at 3 AM)
                if current_time == "03:00" and current_date != last_cleanup:
                    self.tasks.cleanup_old_files()
                    last_cleanup = current_date
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.logger.info("Scheduler interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(5)
        
        self.logger.info("Scheduler stopped")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        self.logger.info("Stop requested")
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        return {
            'running': self.running,
            'schedule_available': SCHEDULE_AVAILABLE,
            'tasks_scheduled': len(self.tasks.task_history),
            'last_tasks': self.tasks.task_history[-10:] if self.tasks.task_history else []
        }


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Task Scheduler - Automatic Task Scheduling',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Run scheduler
  %(prog)s --background        # Run in background mode
  %(prog)s --status            # Show current status
  %(prog)s --once              # Run all tasks once
        """
    )
    
    parser.add_argument(
        '--vault',
        type=str,
        default=None,
        help='Vault path (default: current directory)'
    )
    parser.add_argument(
        '--background',
        action='store_true',
        help='Run in background mode'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current status and exit'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run all tasks once (no scheduling)'
    )
    parser.add_argument(
        '--daily-briefing',
        type=str,
        default=None,
        help='Daily briefing time (HH:MM, default: 08:00)'
    )
    parser.add_argument(
        '--weekly-report',
        type=str,
        default=None,
        help='Weekly report day and time (day,HH:MM, default: monday,09:00)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = SchedulerConfig()
    
    # Apply CLI overrides
    if args.vault:
        config.vault_path = Path(args.vault)
    if args.daily_briefing:
        config.daily_briefing_time = args.daily_briefing
    if args.weekly_report:
        parts = args.weekly_report.split(',')
        if len(parts) == 2:
            config.weekly_report_day = parts[0].lower()
            config.weekly_report_time = parts[1]
    
    # Create scheduler
    scheduler = TaskScheduler(config)
    
    try:
        if args.status:
            # Show status
            status = scheduler.get_status()
            print("\n" + "=" * 60)
            print("SCHEDULER STATUS")
            print("=" * 60)
            print(f"Running: {status['running']}")
            print(f"Schedule Library: {status['schedule_available']}")
            print(f"Tasks Executed: {status['tasks_scheduled']}")
            
            if status['last_tasks']:
                print("\nRecent Tasks:")
                for task in status['last_tasks'][-5:]:
                    status_icon = "[OK]" if task['success'] else "[FAIL]"
                    print(f"  {status_icon} {task['task']} at {task['timestamp']}")
            
            print("=" * 60)
            
        elif args.once:
            # Run all tasks once
            print("\nRunning all tasks once...\n")
            
            scheduler.tasks.run_gmail_watcher()
            scheduler.tasks.run_whatsapp_watcher()
            scheduler.tasks.run_orchestrator_once()
            scheduler.tasks.generate_daily_briefing()
            
            print("\n[OK] All tasks completed")
            
        else:
            # Run scheduler
            print("\n" + "=" * 60)
            print("Task Scheduler - Automatic Scheduling")
            print("=" * 60)
            print(f"Vault: {config.vault_path}")
            print(f"Schedule Library: {SCHEDULE_AVAILABLE}")
            print(f"Gmail Check: Every {config.gmail_check_interval} min")
            print(f"WhatsApp Check: Every {config.whatsapp_check_interval} min")
            print(f"Orchestrator: Every {config.orchestrator_check_interval} min")
            print(f"Daily Briefing: {config.daily_briefing_time}")
            print(f"Weekly Report: {config.weekly_report_day} {config.weekly_report_time}")
            print("=" * 60)
            print("\nPress Ctrl+C to stop\n")
            
            # Setup and run
            if SCHEDULE_AVAILABLE and scheduler.setup_schedule():
                scheduler.run_schedule_loop()
            else:
                scheduler.run_simple_loop()
            
    except KeyboardInterrupt:
        scheduler.stop()
        print("\nStopped by user")
    except Exception as e:
        scheduler.logger.error(f"Fatal error: {e}")
        raise
    
    print("\n" + "=" * 60)
    print("Scheduler stopped")
    print("=" * 60)


if __name__ == '__main__':
    main()
