"""
Facebook MCP Server with Playwright Automation
No Graph API tokens required - uses browser automation

Replaces mock implementation with real Facebook automation.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Playwright automation
from mcp_servers.facebook_playwright_auto import (
    FacebookAutomation,
    get_automation,
    cleanup,
    FACEBOOK_PAGE_ID
)

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'facebook_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FacebookMCP:
    """
    Facebook MCP Server using Playwright Browser Automation
    No Graph API tokens required!
    """
    
    def __init__(self):
        self.page_id = FACEBOOK_PAGE_ID
        self.auto: Optional[FacebookAutomation] = None
        self.initialized = False
        self.mock_mode = not os.getenv('FACEBOOK_EMAIL') or not os.getenv('FACEBOOK_PASSWORD')
        
        if self.mock_mode:
            logger.info("Facebook MCP running in MOCK MODE (no credentials)")
        else:
            logger.info(f"Facebook MCP initialized for Page: {self.page_id}")
    
    def _ensure_automation(self) -> bool:
        """Ensure automation is initialized"""
        if not self.initialized:
            try:
                self.auto = get_automation()
                self.initialized = True
                logger.info("Automation initialized")
            except Exception as e:
                logger.error(f"Failed to initialize automation: {e}")
                return False
        return True
    
    def health_check(self) -> Dict:
        """Check Facebook connection"""
        if self.mock_mode:
            return {
                'status': 'mock_mode',
                'page_id': self.page_id,
                'message': 'Running in mock mode - add FACEBOOK_EMAIL and FACEBOOK_PASSWORD to .env for real posting',
                'credentials_set': False,
                'timestamp': datetime.now().isoformat()
            }
        
        if not self._ensure_automation():
            return {
                'status': 'error',
                'message': 'Failed to initialize automation',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            health = self.auto.health_check()
            return {
                'status': health.get('status', 'unknown'),
                'page_id': self.page_id,
                'logged_in': health.get('logged_in', False),
                'credentials_set': True,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def create_post(self, message: str, link: str = None) -> Dict:
        """Create Facebook post"""
        logger.info(f"Creating post: {message[:50]}...")
        
        if self.mock_mode:
            post_id = f"{self.page_id}_{int(datetime.now().timestamp())}"
            return {
                'success': True,
                'post_id': post_id,
                'mock': True,
                'message': 'Post created successfully (Mock Mode)',
                'post_data': {
                    'id': post_id,
                    'message': message,
                    'link': link,
                    'created_time': datetime.now().isoformat()
                }
            }
        
        if not self._ensure_automation():
            return {'success': False, 'error': 'Automation not initialized'}
        
        try:
            result = self.auto.create_post(message, link)
            logger.info(f"Post result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_posts(self, limit: int = 5) -> Dict:
        """Get recent posts"""
        logger.info(f"Getting {limit} recent posts...")
        
        if self.mock_mode:
            return {
                'success': True,
                'data': [
                    {
                        'id': f'{self.page_id}_1',
                        'message': 'Welcome to Gold Tier! Our new business management system is now live.',
                        'created_time': '2026-03-25T10:00:00+0000',
                        'likes': {'summary': {'total_count': 45}},
                        'comments': {'summary': {'total_count': 12}},
                        'shares': {'count': 8}
                    },
                    {
                        'id': f'{self.page_id}_2',
                        'message': 'Check out our latest services! Visit our website for more info.',
                        'created_time': '2026-03-24T14:30:00+0000',
                        'likes': {'summary': {'total_count': 32}},
                        'comments': {'summary': {'total_count': 7}},
                        'shares': {'count': 5}
                    }
                ],
                'mock': True
            }
        
        if not self._ensure_automation():
            return {'success': False, 'error': 'Automation not initialized'}
        
        try:
            result = self.auto.get_recent_posts(limit)
            logger.info(f"Posts result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting posts: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_post(self, post_id: str) -> Dict:
        """Delete a Facebook post"""
        logger.info(f"Deleting post: {post_id}")
        
        if self.mock_mode:
            return {
                'success': True,
                'message': 'Post deleted successfully (Mock Mode)',
                'mock': True
            }
        
        if not self._ensure_automation():
            return {'success': False, 'error': 'Automation not initialized'}
        
        try:
            result = self.auto.delete_post(post_id)
            logger.info(f"Delete result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error deleting post: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_messages(self, limit: int = 10) -> Dict:
        """Get page messages/comments"""
        logger.info(f"Getting {limit} messages...")
        
        if self.mock_mode:
            return {
                'success': True,
                'data': [
                    {
                        'id': 'msg_1',
                        'sender': 'John Doe',
                        'preview': 'Thanks for the update!',
                        'timestamp': datetime.now().isoformat(),
                        'mock': True
                    }
                ],
                'mock': True
            }
        
        if not self._ensure_automation():
            return {'success': False, 'error': 'Automation not initialized'}
        
        try:
            result = self.auto.get_page_messages(limit)
            logger.info(f"Messages result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return {'success': False, 'error': str(e)}
    
    def reply_to_message(self, message_id: str, reply_text: str) -> Dict:
        """Reply to a message"""
        logger.info(f"Replying to message: {message_id}")
        
        if self.mock_mode:
            return {
                'success': True,
                'message': 'Reply sent successfully (Mock Mode)',
                'mock': True
            }
        
        if not self._ensure_automation():
            return {'success': False, 'error': 'Automation not initialized'}
        
        try:
            result = self.auto.reply_to_message(message_id, reply_text)
            logger.info(f"Reply result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error replying to message: {e}")
            return {'success': False, 'error': str(e)}
    
    def cleanup(self):
        """Cleanup resources"""
        cleanup()
        self.initialized = False
        logger.info("Cleanup complete")


# Global MCP instance
facebook_mcp = FacebookMCP()


if __name__ == '__main__':
    print("=" * 60)
    print("Facebook MCP Server - Playwright Automation")
    print("=" * 60)
    
    # Test health
    print("\n[1/5] Health Check:")
    health = facebook_mcp.health_check()
    print(json.dumps(health, indent=2))
    
    # Test get posts
    print("\n[2/5] Get Posts:")
    posts = facebook_mcp.get_posts(3)
    print(json.dumps(posts, indent=2))
    
    # Test create post
    print("\n[3/5] Create Post:")
    post_result = facebook_mcp.create_post(f"Test post from MCP {datetime.now().strftime('%H:%M')}")
    print(json.dumps(post_result, indent=2))
    
    # Test get messages
    print("\n[4/5] Get Messages:")
    messages = facebook_mcp.get_messages(5)
    print(json.dumps(messages, indent=2))
    
    # Test reply
    print("\n[5/5] Reply to Message:")
    reply_result = facebook_mcp.reply_to_message('msg_1', 'Test reply')
    print(json.dumps(reply_result, indent=2))
    
    # Cleanup
    facebook_mcp.cleanup()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
