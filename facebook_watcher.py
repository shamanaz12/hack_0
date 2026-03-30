"""
Facebook Watcher
Monitors Facebook page for new posts, comments, and messages
Uses Playwright browser automation
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Facebook automation
from mcp_servers.facebook_playwright_auto import FacebookAutomation, FACEBOOK_PAGE_ID

# Setup logging
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'facebook_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FacebookWatcher:
    """
    Facebook Watcher - Monitors page activity
    """

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval  # seconds between checks
        self.auto: FacebookAutomation = None
        self.last_check = None
        self.known_posts = set()
        self.known_messages = set()
        self.stats = {
            'checks': 0,
            'new_posts': 0,
            'new_messages': 0,
            'started_at': datetime.now().isoformat()
        }

    def start(self):
        """Start the watcher"""
        logger.info("=" * 60)
        logger.info("FACEBOOK WATCHER - Starting...")
        logger.info(f"Page ID: {FACEBOOK_PAGE_ID}")
        logger.info(f"Check Interval: {self.check_interval}s")
        logger.info("=" * 60)

        # Initialize automation
        self.auto = FacebookAutomation(headless=False)  # Show browser for debugging

        try:
            # Login
            logger.info("\n[1/3] Logging in to Facebook...")
            if not self.auto.ensure_logged_in():
                logger.error("Failed to login!")
                return

            logger.info("    [OK] Logged in successfully")

            # Initial check
            logger.info("\n[2/3] Initial page check...")
            self._check_posts()
            self._check_messages()

            # Continuous monitoring
            logger.info("\n[3/3] Starting continuous monitoring...")
            logger.info(f"Press Ctrl+C to stop\n")

            while True:
                time.sleep(self.check_interval)
                self._run_check()

        except KeyboardInterrupt:
            logger.info("\n\nWatcher stopped by user")
        except Exception as e:
            logger.error(f"Watcher error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the watcher"""
        logger.info("\nStopping Facebook Watcher...")

        if self.auto:
            self.auto.stop_browser()

        # Save stats
        self.stats['stopped_at'] = datetime.now().isoformat()
        stats_file = Path('facebook_watcher_stats.json')
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

        logger.info(f"Stats saved to {stats_file}")
        logger.info("=" * 60)
        logger.info("FACEBOOK WATCHER - Stopped")
        logger.info("=" * 60)

    def _run_check(self):
        """Run a single check cycle"""
        self.stats['checks'] += 1
        self.last_check = datetime.now()

        logger.info(f"\n{'='*40}")
        logger.info(f"Check #{self.stats['checks']} - {self.last_check.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*40}")

        self._check_posts()
        self._check_messages()

        logger.info(f"\nStats: {self.stats['checks']} checks, "
                   f"{self.stats['new_posts']} new posts, "
                   f"{self.stats['new_messages']} new messages")

    def _check_posts(self):
        """Check for new posts"""
        logger.info("\n[Checking Posts]")

        result = self.auto.get_recent_posts(limit=10)

        if not result.get('success'):
            logger.warning(f"Failed to get posts: {result.get('error')}")
            return

        posts = result.get('data', [])
        logger.info(f"Found {len(posts)} posts")

        for post in posts:
            post_id = post.get('id', str(post.get('index', '')))
            message = post.get('message', '')[:100]

            if post_id and post_id not in self.known_posts:
                self.known_posts.add(post_id)
                self.stats['new_posts'] += 1
                logger.info(f"  [NEW POST] {post_id}")
                logger.info(f"             {message}")
                logger.info(f"             Time: {post.get('timestamp', 'N/A')}")

    def _check_messages(self):
        """Check for new messages"""
        logger.info("\n[Checking Messages]")

        result = self.auto.get_page_messages(limit=10)

        if not result.get('success'):
            logger.warning(f"Failed to get messages: {result.get('error')}")
            return

        messages = result.get('data', [])
        logger.info(f"Found {len(messages)} messages")

        for msg in messages:
            msg_id = f"{msg.get('sender', '')}_{msg.get('timestamp', '')}"
            sender = msg.get('sender', 'Unknown')
            preview = msg.get('preview', '')[:100]

            if msg_id and msg_id not in self.known_messages:
                self.known_messages.add(msg_id)
                self.stats['new_messages'] += 1
                logger.info(f"  [NEW MESSAGE] From: {sender}")
                logger.info(f"                {preview}")
                logger.info(f"                Time: {msg.get('timestamp', 'N/A')}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Facebook Watcher - Monitor page activity')
    parser.add_argument('--interval', '-i', type=int, default=60,
                       help='Check interval in seconds (default: 60)')
    parser.add_argument('--once', action='store_true',
                       help='Run only once (no continuous monitoring)')

    args = parser.parse_args()

    watcher = FacebookWatcher(check_interval=args.interval)

    if args.once:
        # Single check mode
        logger.info("FACEBOOK WATCHER - Single check mode")
        watcher.auto = FacebookAutomation(headless=False)

        try:
            if watcher.auto.ensure_logged_in():
                watcher._check_posts()
                watcher._check_messages()
                logger.info(f"\nFinal Stats: {watcher.stats}")
            else:
                logger.error("Failed to login")
        finally:
            watcher.stop()
    else:
        # Continuous monitoring
        watcher.start()


if __name__ == '__main__':
    main()
