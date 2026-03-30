"""
Automation Orchestrator
Main controller for multi-platform social media automation.
Coordinates Facebook, Instagram, WhatsApp, and Gmail automation tasks.
"""

import time
import random
import signal
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from session_manager import SessionManager
from facebook_browser import FacebookAutomation
from instagram_browser import InstagramAutomation
from whatsapp_browser import WhatsAppAutomation
from gmail_browser import GmailAutomation


class AutomationOrchestrator:
    """
    Main orchestrator for social media automation.
    Runs scheduled tasks across all platforms with error handling and logging.
    """
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.running = False
        self.session: Optional[SessionManager] = None
        self.facebook: Optional[FacebookAutomation] = None
        self.instagram: Optional[InstagramAutomation] = None
        self.whatsapp: Optional[WhatsAppAutomation] = None
        self.gmail: Optional[GmailAutomation] = None
        
        # Setup logging
        self.logger = self._setup_logger()
        
        # Task schedule (in seconds)
        self.task_intervals = {
            "facebook_check": 300,      # Check Facebook every 5 minutes
            "instagram_check": 600,     # Check Instagram every 10 minutes
            "whatsapp_check": 120,      # Check WhatsApp every 2 minutes
            "gmail_check": 180,         # Check Gmail every 3 minutes
            "facebook_post": 3600,      # Post to Facebook every hour
            "instagram_post": 7200,     # Post to Instagram every 2 hours
        }
        
        # Last run times
        self.last_run: Dict[str, float] = {key: 0 for key in self.task_intervals}
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logger(self):
        """Setup logging for orchestrator."""
        import logging
        
        log_path = Path(__file__).parent / "logs"
        log_path.mkdir(exist_ok=True)
        
        logger = logging.getLogger("orchestrator")
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler
        fh = logging.FileHandler(log_path / "orchestrator.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info("Shutdown signal received. Stopping orchestrator...")
        self.running = False
    
    def initialize(self) -> bool:
        """
        Initialize all platform automations.
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            self.logger.info("Initializing Automation Orchestrator...")
            
            # Create session manager
            self.session = SessionManager(headless=self.headless)
            self.session.start_browser()
            
            # Create platform automations
            self.facebook = FacebookAutomation(self.session)
            self.instagram = InstagramAutomation(self.session)
            self.whatsapp = WhatsAppAutomation(self.session)
            self.gmail = GmailAutomation(self.session)
            
            self.logger.info("Orchestrator initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            return False
    
    def shutdown(self):
        """Cleanup resources and shutdown."""
        self.logger.info("Shutting down orchestrator...")
        
        if self.session:
            self.session.close()
        
        self.running = False
        self.logger.info("Orchestrator shutdown complete")
    
    def run_once(self, platforms: Optional[list] = None):
        """
        Run automation tasks once for specified platforms.
        
        Args:
            platforms: List of platforms to check. If None, checks all.
        """
        if platforms is None:
            platforms = ["facebook", "instagram", "whatsapp", "gmail"]
        
        self.logger.info(f"Running automation tasks for: {', '.join(platforms)}")
        
        for platform in platforms:
            try:
                if platform == "facebook":
                    self._run_facebook_tasks()
                elif platform == "instagram":
                    self._run_instagram_tasks()
                elif platform == "whatsapp":
                    self._run_whatsapp_tasks()
                elif platform == "gmail":
                    self._run_gmail_tasks()
            except Exception as e:
                self.logger.error(f"Error running {platform} tasks: {e}")
    
    def run_continuous(self, interval: int = 60):
        """
        Run automation tasks continuously in a loop.
        
        Args:
            interval: Base check interval in seconds
        """
        self.logger.info("Starting continuous automation loop...")
        self.running = True
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check Facebook
                if current_time - self.last_run["facebook_check"] >= self.task_intervals["facebook_check"]:
                    self._run_facebook_tasks()
                    self.last_run["facebook_check"] = current_time
                
                # Check Instagram
                if current_time - self.last_run["instagram_check"] >= self.task_intervals["instagram_check"]:
                    self._run_instagram_tasks()
                    self.last_run["instagram_check"] = current_time
                
                # Check WhatsApp
                if current_time - self.last_run["whatsapp_check"] >= self.task_intervals["whatsapp_check"]:
                    self._run_whatsapp_tasks()
                    self.last_run["whatsapp_check"] = current_time
                
                # Check Gmail
                if current_time - self.last_run["gmail_check"] >= self.task_intervals["gmail_check"]:
                    self._run_gmail_tasks()
                    self.last_run["gmail_check"] = current_time
                
                # Sleep before next check
                self.session.human_delay(interval / 2, interval)
            
            except KeyboardInterrupt:
                self.logger.info("Interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Error in automation loop: {e}")
                time.sleep(30)  # Wait before retrying
        
        self.shutdown()
    
    def _run_facebook_tasks(self):
        """Run Facebook automation tasks."""
        self.logger.info("Running Facebook tasks...")
        
        try:
            # Ensure logged in
            if not self.facebook.ensure_logged_in():
                self.logger.warning("Facebook login failed")
                return
            
            # Navigate to business page
            self.facebook.navigate_to_page()
            
            # Get recent posts
            posts = self.facebook.get_recent_posts(count=3)
            self.logger.info(f"Facebook: Found {len(posts)} recent posts")
            
            for post in posts:
                self.logger.info(f"  - Post: {post.get('text', '')[:50]}...")
        
        except Exception as e:
            self.logger.error(f"Facebook tasks error: {e}")
    
    def _run_instagram_tasks(self):
        """Run Instagram automation tasks."""
        self.logger.info("Running Instagram tasks...")
        
        try:
            # Ensure logged in
            if not self.instagram.ensure_logged_in():
                self.logger.warning("Instagram login failed")
                return
            
            # Get recent posts
            posts = self.instagram.get_recent_posts(count=3)
            self.logger.info(f"Instagram: Found {len(posts)} recent posts")
            
            for post in posts:
                self.logger.info(f"  - Post: {post.get('caption', '')[:50]}...")
        
        except Exception as e:
            self.logger.error(f"Instagram tasks error: {e}")
    
    def _run_whatsapp_tasks(self):
        """Run WhatsApp automation tasks."""
        self.logger.info("Running WhatsApp tasks...")
        
        try:
            # Ensure logged in
            if not self.whatsapp.ensure_logged_in():
                self.logger.warning("WhatsApp login failed")
                return
            
            # Get unread messages
            messages = self.whatsapp.read_unread_messages(count=5)
            self.logger.info(f"WhatsApp: Found {len(messages)} unread messages")
            
            for msg in messages:
                self.logger.info(f"  - From {msg.get('sender', 'Unknown')}: {msg.get('text', '')[:50]}...")
                
                # Auto-reply to messages (optional - customize logic here)
                # if "urgent" in msg.get('text', '').lower():
                #     self.whatsapp.send_reply("Thank you for your message. We'll get back to you soon!")
        
        except Exception as e:
            self.logger.error(f"WhatsApp tasks error: {e}")
    
    def _run_gmail_tasks(self):
        """Run Gmail automation tasks."""
        self.logger.info("Running Gmail tasks...")
        
        try:
            # Ensure logged in
            if not self.gmail.ensure_logged_in():
                self.logger.warning("Gmail login failed")
                return
            
            # Get unread count
            count_info = self.gmail.get_email_count()
            self.logger.info(f"Gmail: {count_info.get('unread', 0)} unread emails")
            
            # Get unread emails
            emails = self.gmail.read_unread_emails(count=5)
            self.logger.info(f"Gmail: Found {len(emails)} emails")
            
            for email in emails:
                self.logger.info(f"  - From {email.get('sender', 'Unknown')}: {email.get('subject', '')[:50]}...")
                
                # Auto-reply to emails (optional - customize logic here)
                # if "urgent" in email.get('subject', '').lower():
                #     self.gmail.send_reply("Thank you for your email. We'll respond shortly.")
                #     self.gmail.mark_as_read([email.get('id')])
        
        except Exception as e:
            self.logger.error(f"Gmail tasks error: {e}")
    
    # === Public API Methods ===
    
    def post_to_facebook(self, text: str, link: Optional[str] = None) -> bool:
        """Post to Facebook Business Page."""
        return self.facebook.post(text, link)
    
    def post_to_instagram(self, text: str, image_path: Optional[str] = None) -> bool:
        """Post to Instagram."""
        return self.instagram.post(text, image_path)
    
    def send_whatsapp_message(self, contact: str, message: str) -> bool:
        """Send WhatsApp message."""
        return self.whatsapp.send_message(contact, message)
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send Gmail email."""
        return self.gmail.send_email(to, subject, body)
    
    def get_facebook_posts(self, count: int = 5) -> list:
        """Get recent Facebook posts."""
        return self.facebook.get_recent_posts(count)
    
    def get_instagram_posts(self, count: int = 5) -> list:
        """Get recent Instagram posts."""
        return self.instagram.get_recent_posts(count)
    
    def get_unread_whatsapp_messages(self, count: int = 10) -> list:
        """Get unread WhatsApp messages."""
        return self.whatsapp.read_unread_messages(count)
    
    def get_unread_emails(self, count: int = 10) -> list:
        """Get unread Gmail emails."""
        return self.gmail.read_unread_emails(count)


def main():
    """Main entry point for the orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Social Media Automation Orchestrator")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (no GUI)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run tasks once and exit"
    )
    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=["facebook", "instagram", "whatsapp", "gmail"],
        default=["facebook", "instagram", "whatsapp", "gmail"],
        help="Platforms to automate"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (for continuous mode)"
    )
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = AutomationOrchestrator(headless=args.headless)
    
    # Initialize
    if not orchestrator.initialize():
        print("Failed to initialize orchestrator. Check logs for details.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("  GOLD TIER AUTOMATION ORCHESTRATOR")
    print("=" * 60)
    print(f"Mode: {'Headless' if args.headless else 'Interactive'}")
    print(f"Platforms: {', '.join(args.platforms)}")
    print("=" * 60 + "\n")
    
    try:
        if args.once:
            # Run once and exit
            orchestrator.run_once(platforms=args.platforms)
        else:
            # Run continuously
            print("Press Ctrl+C to stop...\n")
            orchestrator.run_continuous(interval=args.interval)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        orchestrator.shutdown()
    
    print("\nOrchestrator stopped.")


if __name__ == "__main__":
    main()
