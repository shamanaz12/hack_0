"""
Facebook & Instagram Watcher
Monitors Facebook and Instagram pages for new posts, comments, and messages
Uses direct API calls with mock mode support
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

# Setup logging
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

# Create file handler with UTF-8 encoding
file_handler = logging.FileHandler(LOG_DIR / 'facebook_instagram_watcher.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        file_handler,
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FacebookWatcher:
    """Facebook Page Watcher"""

    def __init__(self):
        self.profile_id = os.getenv('FACEBOOK_PAGE_ID', '61578524116357')
        self.profile_url = f'https://www.facebook.com/profile.php?id={self.profile_id}'
        self.access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN', '')
        self.mock_mode = not self.access_token or self.access_token in ['test_token_replace_with_actual_token', 'mock_token', '']
        self.known_posts = set()
        self.stats = {'checks': 0, 'new_posts': 0, 'new_messages': 0}

    def get_posts(self, limit: int = 5) -> dict:
        """Get recent posts"""
        if self.mock_mode:
            logger.info("Running in MOCK MODE")
            return {
                'success': True,
                'mock': True,
                'data': [
                    {
                        'id': f'{self.profile_id}_1',
                        'message': 'Welcome to Gold Tier! Our new business management system is now live.',
                        'created_time': '2026-03-25T10:00:00+0000',
                        'likes': {'summary': {'total_count': 45}},
                        'comments': {'summary': {'total_count': 12}},
                        'shares': {'count': 8}
                    },
                    {
                        'id': f'{self.profile_id}_2',
                        'message': 'Check out our latest services! Visit our website for more info.',
                        'created_time': '2026-03-24T14:30:00+0000',
                        'likes': {'summary': {'total_count': 32}},
                        'comments': {'summary': {'total_count': 7}},
                        'shares': {'count': 5}
                    },
                    {
                        'id': f'{self.profile_id}_3',
                        'message': 'Thank you for 1000 followers! We appreciate your support.',
                        'created_time': '2026-03-23T09:15:00+0000',
                        'likes': {'summary': {'total_count': 128}},
                        'comments': {'summary': {'total_count': 34}},
                        'shares': {'count': 15}
                    }
                ][:limit]
            }

        try:
            import requests
            response = requests.get(
                f'https://graph.facebook.com/v18.0/{self.profile_id}/posts',
                params={'access_token': self.access_token, 'limit': limit},
                timeout=10
            )
            if response.status_code == 200:
                return {'success': True, 'data': response.json().get('data', [])}
            else:
                return {'success': False, 'error': response.json().get('error', {}).get('message')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def check(self):
        """Check for new posts"""
        self.stats['checks'] += 1
        logger.info(f"\n{'='*50}")
        logger.info(f"FACEBOOK CHECK #{self.stats['checks']} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Profile ID: {self.profile_id}")
        logger.info(f"Profile URL: {self.profile_url}")
        logger.info(f"{'='*50}")

        result = self.get_posts(10)

        if not result.get('success'):
            logger.warning(f"Failed to get posts: {result.get('error')}")
            return

        posts = result.get('data', [])
        logger.info(f"Found {len(posts)} posts")

        for post in posts:
            post_id = post.get('id', '')
            message = post.get('message', '')[:100]
            created_time = post.get('created_time', 'N/A')

            if post_id and post_id not in self.known_posts:
                self.known_posts.add(post_id)
                self.stats['new_posts'] += 1
                logger.info(f"  [NEW POST] {post_id}")
                logger.info(f"             {message}")
                logger.info(f"             Time: {created_time}")

                # Show engagement
                likes = post.get('likes', {}).get('summary', {}).get('total_count', 0)
                comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
                shares = post.get('shares', {}).get('count', 0)
                logger.info(f"             Engagement: {likes} likes, {comments} comments, {shares} shares")


class InstagramWatcher:
    """Instagram Business Watcher"""

    def __init__(self):
        self.username = 'shamaansari5576'
        self.profile_url = 'https://www.instagram.com/shamaansari5576'
        self.business_id = os.getenv('INSTAGRAM_BUSINESS_ID', '')
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        self.mock_mode = not self.access_token or self.access_token in ['test_token_replace_with_actual_token', 'mock_token', '']
        self.known_media = set()
        self.stats = {'checks': 0, 'new_posts': 0}

    def get_media(self, limit: int = 5) -> dict:
        """Get recent media"""
        if self.mock_mode:
            logger.info("Running in MOCK MODE")
            return {
                'success': True,
                'mock': True,
                'data': [
                    {
                        'id': 'ig_media_1',
                        'caption': 'Welcome to Gold Tier on Instagram! 📸',
                        'timestamp': '2026-03-25T10:00:00+0000',
                        'media_type': 'IMAGE',
                        'permalink': 'https://instagram.com/p/abc123',
                        'like_count': 89,
                        'comments_count': 23
                    },
                    {
                        'id': 'ig_media_2',
                        'caption': 'Check out our latest products! ✨',
                        'timestamp': '2026-03-24T14:30:00+0000',
                        'media_type': 'CAROUSEL_ALBUM',
                        'permalink': 'https://instagram.com/p/def456',
                        'like_count': 156,
                        'comments_count': 45
                    },
                    {
                        'id': 'ig_media_3',
                        'caption': 'Behind the scenes at Gold Tier HQ 🎬',
                        'timestamp': '2026-03-23T09:15:00+0000',
                        'media_type': 'VIDEO',
                        'permalink': 'https://instagram.com/p/ghi789',
                        'like_count': 234,
                        'comments_count': 67
                    }
                ][:limit]
            }

        try:
            import requests
            response = requests.get(
                f'https://graph.facebook.com/v18.0/{self.business_id}/media',
                params={
                    'access_token': self.access_token,
                    'limit': limit,
                    'fields': 'id,caption,timestamp,media_type,permalink,like_count,comments_count'
                },
                timeout=10
            )
            if response.status_code == 200:
                return {'success': True, 'data': response.json().get('data', [])}
            else:
                return {'success': False, 'error': response.json().get('error', {}).get('message')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def check(self):
        """Check for new media"""
        self.stats['checks'] += 1
        logger.info(f"\n{'='*50}")
        logger.info(f"INSTAGRAM CHECK #{self.stats['checks']} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Account: @{self.username}")
        logger.info(f"Profile: {self.profile_url}")
        logger.info(f"{'='*50}")

        result = self.get_media(10)

        if not result.get('success'):
            logger.warning(f"Failed to get media: {result.get('error')}")
            return

        media_items = result.get('data', [])
        logger.info(f"Found {len(media_items)} media items")

        for item in media_items:
            media_id = item.get('id', '')
            caption = item.get('caption', '')[:100]
            timestamp = item.get('timestamp', 'N/A')
            media_type = item.get('media_type', 'UNKNOWN')

            if media_id and media_id not in self.known_media:
                self.known_media.add(media_id)
                self.stats['new_posts'] += 1
                logger.info(f"  [NEW {media_type}] {media_id}")
                logger.info(f"                {caption}")
                logger.info(f"                Time: {timestamp}")
                logger.info(f"                Engagement: {item.get('like_count', 0)} likes, {item.get('comments_count', 0)} comments")


class CombinedWatcher:
    """Combined Facebook & Instagram Watcher"""

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.facebook = FacebookWatcher()
        self.instagram = InstagramWatcher()
        self.running = False

    def run_once(self):
        """Run a single check cycle"""
        logger.info("=" * 60)
        logger.info("FACEBOOK & INSTAGRAM WATCHER - Single Check")
        logger.info("=" * 60)

        self.facebook.check()
        self.instagram.check()

        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Facebook:  {self.facebook.stats['checks']} checks, {self.facebook.stats['new_posts']} new posts")
        logger.info(f"Instagram: {self.instagram.stats['checks']} checks, {self.instagram.stats['new_posts']} new posts")
        logger.info("=" * 60)

    def run_continuous(self):
        """Run continuous monitoring"""
        logger.info("=" * 60)
        logger.info("FACEBOOK & INSTAGRAM WATCHER - Starting...")
        logger.info(f"Check Interval: {self.check_interval}s")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)

        self.running = True

        try:
            while self.running:
                self.run_once()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("\n\nWatcher stopped by user")
        finally:
            self.running = False


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Facebook & Instagram Watcher')
    parser.add_argument('--interval', '-i', type=int, default=60, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run only once')
    parser.add_argument('--facebook-only', action='store_true', help='Monitor Facebook only')
    parser.add_argument('--instagram-only', action='store_true', help='Monitor Instagram only')

    args = parser.parse_args()

    if args.once:
        # Single check mode
        if args.facebook_only or not args.instagram_only:
            FacebookWatcher().check()
        if args.instagram_only or not args.facebook_only:
            InstagramWatcher().check()
    else:
        # Continuous mode
        watcher = CombinedWatcher(check_interval=args.interval)
        watcher.run_continuous()


if __name__ == '__main__':
    main()
