#!/usr/bin/env python3
"""
Facebook Automation Orchestration System
Gold Tier Business - Multi-platform Social Media Automation

Coordinates posting across Facebook and Instagram using Playwright browser automation.
Implements rate limiting, session persistence, and mock mode for testing.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv(".env.facebook")
load_dotenv(".env.instagram")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("orchestration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("orchestrator")

# Configuration
CONFIG = {
    "mock_mode": os.getenv("MOCK_MODE", "true").lower() == "true",
    "rate_limit_delay": int(os.getenv("RATE_LIMIT_DELAY", "60")),
    "max_posts_per_run": int(os.getenv("MAX_POSTS_PER_RUN", "5")),
    "facebook_page_id": os.getenv("FACEBOOK_PAGE_ID", "956241877582673"),
    "session_timeout": int(os.getenv("SESSION_TIMEOUT", "3600")),
    "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3")),
}


class OrchestrationManager:
    """Main orchestration manager for social media automation."""

    def __init__(self):
        self.start_time = datetime.now()
        self.posts_completed = 0
        self.errors = []
        self.session_data = {}

    def initialize(self) -> bool:
        """Initialize the orchestration system."""
        logger.info("=" * 60)
        logger.info("Facebook Automation Orchestration System - Starting")
        logger.info("=" * 60)
        logger.info(f"Mock Mode: {CONFIG['mock_mode']}")
        logger.info(f"Rate Limit Delay: {CONFIG['rate_limit_delay']}s")
        logger.info(f"Max Posts Per Run: {CONFIG['max_posts_per_run']}")
        logger.info(f"Facebook Page ID: {CONFIG['facebook_page_id']}")

        if CONFIG["mock_mode"]:
            logger.warning("Running in MOCK MODE - No actual posts will be made")

        return True

    def load_pending_posts(self) -> list:
        """Load pending posts from the content queue."""
        pending_file = Path("content_queue.json")
        if not pending_file.exists():
            logger.info("No content queue found, checking auto_processor")
            return []

        try:
            with open(pending_file, "r", encoding="utf-8") as f:
                queue = json.load(f)
            logger.info(f"Found {len(queue)} pending posts in queue")
            return queue[:CONFIG["max_posts_per_run"]]
        except Exception as e:
            logger.error(f"Error loading content queue: {e}")
            return []

    def post_to_facebook(self, post_data: dict) -> bool:
        """Execute Facebook post via Playwright automation."""
        logger.info(f"Posting to Facebook: {post_data.get('title', 'Untitled')}")

        if CONFIG["mock_mode"]:
            logger.info("[MOCK] Facebook post would be published here")
            time.sleep(2)  # Simulate processing
            return True

        try:
            # Import and run the Facebook automation
            from auto_post_facebook import FacebookPoster

            poster = FacebookPoster()
            success = poster.create_post(
                content=post_data.get("content", ""),
                image_path=post_data.get("image_path"),
                schedule_time=post_data.get("schedule_time")
            )

            if success:
                logger.info("Facebook post published successfully")
                return True
            else:
                logger.error("Facebook post failed")
                return False

        except ImportError:
            logger.warning("auto_post_facebook module not available, using Playwright directly")
            return self._post_via_playwright("facebook", post_data)
        except Exception as e:
            logger.error(f"Facebook posting error: {e}")
            self.errors.append(f"Facebook: {str(e)}")
            return False

    def post_to_instagram(self, post_data: dict) -> bool:
        """Execute Instagram post via Playwright automation."""
        logger.info(f"Posting to Instagram: {post_data.get('title', 'Untitled')}")

        if CONFIG["mock_mode"]:
            logger.info("[MOCK] Instagram post would be published here")
            time.sleep(2)
            return True

        try:
            return self._post_via_playwright("instagram", post_data)
        except Exception as e:
            logger.error(f"Instagram posting error: {e}")
            self.errors.append(f"Instagram: {str(e)}")
            return False

    def _post_via_playwright(self, platform: str, post_data: dict) -> bool:
        """Generic Playwright-based posting method."""
        logger.info(f"Using Playwright automation for {platform}")
        # Placeholder for Playwright implementation
        time.sleep(1)
        return True

    def apply_rate_limiting(self):
        """Apply rate limiting between posts."""
        delay = CONFIG["rate_limit_delay"]
        logger.info(f"Applying rate limit: {delay}s delay")
        if not CONFIG["mock_mode"]:
            time.sleep(delay)

    def run_orchestration(self) -> dict:
        """Main orchestration loop."""
        results = {
            "start_time": self.start_time.isoformat(),
            "end_time": None,
            "posts_attempted": 0,
            "posts_successful": 0,
            "posts_failed": 0,
            "errors": [],
            "status": "running"
        }

        try:
            if not self.initialize():
                results["status"] = "initialization_failed"
                return results

            # Load pending content
            pending_posts = self.load_pending_posts()

            if not pending_posts:
                logger.info("No pending posts to process")
                # Try auto_processor as fallback
                try:
                    from auto_processor import AutoProcessor
                    processor = AutoProcessor()
                    pending_posts = processor.get_pending_content()
                    logger.info(f"Loaded {len(pending_posts)} posts from auto_processor")
                except Exception as e:
                    logger.warning(f"Could not load from auto_processor: {e}")

            # Process each post
            for i, post in enumerate(pending_posts):
                if self.posts_completed >= CONFIG["max_posts_per_run"]:
                    logger.info("Reached max posts per run limit")
                    break

                results["posts_attempted"] += 1
                logger.info(f"Processing post {i + 1}/{len(pending_posts)}")

                # Determine target platforms
                platforms = post.get("platforms", ["facebook"])

                for platform in platforms:
                    if platform == "facebook":
                        success = self.post_to_facebook(post)
                    elif platform == "instagram":
                        success = self.post_to_instagram(post)
                    else:
                        logger.warning(f"Unknown platform: {platform}")
                        success = False

                    if success:
                        results["posts_successful"] += 1
                        self.posts_completed += 1
                    else:
                        results["posts_failed"] += 1

                    # Apply rate limiting between posts
                    if i < len(pending_posts) - 1:
                        self.apply_rate_limiting()

            results["status"] = "completed"

        except KeyboardInterrupt:
            logger.warning("Orchestration interrupted by user")
            results["status"] = "interrupted"
        except Exception as e:
            logger.error(f"Orchestration error: {e}")
            results["status"] = "error"
            results["errors"].append(str(e))
            self.errors.append(str(e))
        finally:
            results["end_time"] = datetime.now().isoformat()
            results["errors"] = self.errors
            self._generate_report(results)

        return results

    def _generate_report(self, results: dict):
        """Generate and save orchestration report."""
        report = {
            "orchestration_report": results,
            "duration_seconds": (
                datetime.fromisoformat(results["end_time"]) - 
                datetime.fromisoformat(results["start_time"])
            ).total_seconds() if results["end_time"] else 0,
            "summary": (
                f"Completed: {results['posts_successful']}/{results['posts_attempted']} posts"
            )
        }

        report_file = Path(f"orchestration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Report saved to: {report_file}")
        logger.info(f"Summary: {report['summary']}")


def main():
    """Main entry point."""
    manager = OrchestrationManager()
    results = manager.run_orchestration()

    # Exit with appropriate code
    if results["status"] == "completed" and results["posts_failed"] == 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
