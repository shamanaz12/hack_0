"""
Cron Scheduler for Gmail Watcher
Runs the email checking function every 5 minutes
"""
import time
import schedule
import logging
import sys
import os
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the GmailWatcher class from gmail_poller
from gmail_poller import GmailWatcher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cron_scheduler.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_gmail_check():
    """Run a single check for new emails"""
    logger.info("Starting scheduled email check...")
    try:
        watcher = GmailWatcher()
        watcher.check_new_emails()
        logger.info("Scheduled email check completed")
    except Exception as e:
        logger.error(f"Error during scheduled email check: {e}", exc_info=True)

def main():
    logger.info("Starting Gmail Watcher Cron Scheduler")
    logger.info("Will run email check every 5 minutes")
    
    # Schedule the job to run every 5 minutes
    schedule.every(5).minutes.do(run_gmail_check)
    
    # Run the first check immediately
    run_gmail_check()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()