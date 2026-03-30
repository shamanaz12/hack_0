"""
Unified Social Media MCP Server
Facebook + Instagram - NO TOKENS REQUIRED!
Uses browser automation with Playwright

Features:
- No API tokens needed
- Real browser automation
- Session persistence (login once)
- Works with both Facebook & Instagram
- Multiple MCP servers in one
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'unified_social_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class UnifiedSocialMCP:
    """
    Unified Social Media MCP - Facebook + Instagram
    No tokens required - uses browser automation
    """

    def __init__(self):
        self.facebook_page_id = os.getenv('FACEBOOK_PAGE_ID', '956241877582673')
        self.facebook_email = os.getenv('FACEBOOK_EMAIL', '')
        self.facebook_password = os.getenv('FACEBOOK_PASSWORD', '')
        self.instagram_username = os.getenv('INSTAGRAM_USERNAME', 'shamaansari5576')
        self.instagram_password = os.getenv('INSTAGRAM_PASSWORD', '')
        
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.logged_in_fb = False
        self.logged_in_ig = False
        
        # Session storage
        self.session_file = Path('social_session.json')
        
        logger.info("Unified Social MCP initialized")
        logger.info(f"  Facebook Page: {self.facebook_page_id}")
        logger.info(f"  Instagram: @{self.instagram_username}")

    def start_browser(self, headless: bool = False):
        """Start Playwright browser"""
        try:
            from playwright.sync_api import sync_playwright
            
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            self.context.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
            
            self.page = self.context.new_page()
            logger.info("Browser started")
            return True
        except Exception as e:
            logger.error(f"Error starting browser: {e}")
            return False

    def stop_browser(self):
        """Stop browser"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Browser stopped")
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")

    def save_session(self):
        """Save browser session cookies"""
        if not self.context:
            return
        
        try:
            cookies = self.context.cookies()
            with open(self.session_file, 'w') as f:
                json.dump({
                    'cookies': cookies,
                    'saved_at': datetime.now().isoformat(),
                    'facebook_logged_in': self.logged_in_fb,
                    'instagram_logged_in': self.logged_in_ig
                }, f, indent=2)
            logger.info("Session saved")
        except Exception as e:
            logger.error(f"Error saving session: {e}")

    def load_session(self) -> bool:
        """Load saved session"""
        if not self.session_file.exists():
            logger.info("No saved session found")
            return False
        
        try:
            with open(self.session_file, 'r') as f:
                data = json.load(f)
            
            # Check if session is expired (24 hours)
            saved_at = datetime.fromisoformat(data['saved_at'])
            if datetime.now() - saved_at > timedelta(hours=24):
                logger.info("Session expired")
                return False
            
            if self.context:
                self.context.add_cookies(data['cookies'])
                self.logged_in_fb = data.get('facebook_logged_in', False)
                self.logged_in_ig = data.get('instagram_logged_in', False)
                logger.info("Session loaded")
                return True
        except Exception as e:
            logger.error(f"Error loading session: {e}")
        
        return False

    def facebook_login(self) -> bool:
        """Login to Facebook"""
        if not self.page:
            if not self.start_browser():
                return False
        
        if self.logged_in_fb:
            logger.info("Already logged in to Facebook")
            return True
        
        if self.load_session() and self.logged_in_fb:
            logger.info("Restored Facebook session")
            return True
        
        if not self.facebook_email or not self.facebook_password:
            logger.warning("Facebook credentials not configured")
            return False
        
        try:
            logger.info("Logging in to Facebook...")
            
            self.page.goto('https://www.facebook.com/login', wait_until='networkidle')
            self.page.wait_for_selector('#email', timeout=10000)
            
            self.page.fill('#email', self.facebook_email)
            self.page.fill('#pass', self.facebook_password)
            self.page.click('button[type="submit"]')
            
            self.page.wait_for_load_state('networkidle')
            
            if 'facebook.com' in self.page.url and 'login' not in self.page.url.lower():
                logger.info("Facebook login successful")
                self.logged_in_fb = True
                self.save_session()
                return True
            else:
                logger.error("Facebook login failed")
                return False
                
        except Exception as e:
            logger.error(f"Facebook login error: {e}")
            return False

    def instagram_login(self) -> bool:
        """Login to Instagram"""
        if not self.page:
            if not self.start_browser():
                return False
        
        if self.logged_in_ig:
            logger.info("Already logged in to Instagram")
            return True
        
        if self.load_session() and self.logged_in_ig:
            logger.info("Restored Instagram session")
            return True
        
        if not self.instagram_username or not self.instagram_password:
            logger.warning("Instagram credentials not configured")
            return False
        
        try:
            logger.info("Logging in to Instagram...")
            
            self.page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle')
            self.page.wait_for_selector('input[name="username"]', timeout=10000)
            
            self.page.fill('input[name="username"]', self.instagram_username)
            self.page.fill('input[name="password"]', self.instagram_password)
            self.page.click('button[type="submit"]')
            
            self.page.wait_for_load_state('networkidle')
            
            if 'instagram.com' in self.page.url and 'login' not in self.page.url.lower():
                logger.info("Instagram login successful")
                self.logged_in_ig = True
                self.save_session()
                return True
            else:
                logger.error("Instagram login failed")
                return False
                
        except Exception as e:
            logger.error(f"Instagram login error: {e}")
            return False

    def facebook_create_post(self, message: str, link: str = None) -> Dict:
        """Create Facebook post"""
        logger.info(f"Creating Facebook post: {message[:50]}...")
        
        if not self.facebook_login():
            return {'success': False, 'error': 'Not logged in to Facebook'}
        
        try:
            self.page.goto(f'https://www.facebook.com/{self.facebook_page_id}', wait_until='networkidle')
            self.page.wait_for_timeout(3000)
            
            # Find post box
            post_box = self.page.locator('[data-testid="create_post"]').first
            if not post_box.is_visible():
                post_box = self.page.locator('div[role="textbox"]').first
            
            post_box.click()
            self.page.wait_for_timeout(1000)
            post_box.fill(message)
            self.page.wait_for_timeout(1000)
            
            if link:
                post_box.press('Enter')
                self.page.wait_for_timeout(1000)
                post_box.type(f' {link}')
            
            # Click Post button
            post_button = self.page.locator('button').filter(has_text='Post').first
            if post_button.is_visible():
                post_button.click()
                self.page.wait_for_load_state('networkidle')
                
                logger.info("Facebook post created")
                return {
                    'success': True,
                    'message': 'Post created successfully',
                    'post_data': {
                        'message': message,
                        'link': link,
                        'created_at': datetime.now().isoformat()
                    }
                }
            else:
                return {'success': False, 'error': 'Post button not found'}
                
        except Exception as e:
            logger.error(f"Error creating Facebook post: {e}")
            return {'success': False, 'error': str(e)}

    def facebook_get_posts(self, limit: int = 5) -> Dict:
        """Get recent Facebook posts"""
        logger.info(f"Getting {limit} recent Facebook posts...")
        
        if not self.facebook_login():
            return {'success': False, 'error': 'Not logged in to Facebook'}
        
        try:
            self.page.goto(f'https://www.facebook.com/{self.facebook_page_id}', wait_until='networkidle')
            self.page.wait_for_timeout(3000)
            
            # Scroll to load posts
            for _ in range(3):
                self.page.evaluate('window.scrollBy(0, 1000)')
                self.page.wait_for_timeout(1000)
            
            posts = []
            post_elements = self.page.locator('[role="article"]')
            count = min(post_elements.count(), limit)
            
            for i in range(count):
                try:
                    post_el = post_elements.nth(i)
                    if not post_el.is_visible():
                        continue
                    
                    post_data = {'index': i}
                    
                    # Get message
                    try:
                        message_el = post_el.locator('[dir="auto"]').first
                        if message_el.is_visible():
                            post_data['message'] = message_el.inner_text()[:500]
                    except:
                        post_data['message'] = ''
                    
                    # Get timestamp
                    try:
                        time_el = post_el.locator('abbr').first
                        if time_el.is_visible():
                            post_data['timestamp'] = time_el.get_attribute('title')
                    except:
                        post_data['timestamp'] = ''
                    
                    posts.append(post_data)
                except Exception as e:
                    logger.error(f"Error extracting post {i}: {e}")
            
            logger.info(f"Retrieved {len(posts)} Facebook posts")
            return {'success': True, 'data': posts, 'count': len(posts)}
            
        except Exception as e:
            logger.error(f"Error getting Facebook posts: {e}")
            return {'success': False, 'error': str(e)}

    def instagram_create_post(self, image_url: str, caption: str = '') -> Dict:
        """Create Instagram post"""
        logger.info(f"Creating Instagram post: {image_url}")
        
        if not self.instagram_login():
            return {'success': False, 'error': 'Not logged in to Instagram'}
        
        try:
            self.page.goto('https://www.instagram.com/', wait_until='networkidle')
            self.page.wait_for_timeout(3000)
            
            # Click create button
            create_btn = self.page.locator('svg[aria-label="New post"]').first
            create_btn.click()
            self.page.wait_for_timeout(2000)
            
            # Upload from URL (simplified - in production would need file upload)
            logger.info("Instagram post creation initiated")
            return {
                'success': True,
                'message': 'Post creation initiated (manual completion may be required)',
                'post_data': {
                    'image_url': image_url,
                    'caption': caption,
                    'created_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating Instagram post: {e}")
            return {'success': False, 'error': str(e)}

    def instagram_get_posts(self, limit: int = 5) -> Dict:
        """Get recent Instagram posts"""
        logger.info(f"Getting {limit} recent Instagram posts...")
        
        if not self.instagram_login():
            return {'success': False, 'error': 'Not logged in to Instagram'}
        
        try:
            self.page.goto(f'https://www.instagram.com/{self.instagram_username}/', wait_until='networkidle')
            self.page.wait_for_timeout(3000)
            
            posts = []
            post_elements = self.page.locator('article')
            count = min(post_elements.count(), limit)
            
            for i in range(count):
                try:
                    post_el = post_elements.nth(i)
                    if not post_el.is_visible():
                        continue
                    
                    post_data = {'index': i}
                    
                    # Get caption
                    try:
                        caption_el = post_el.locator('ul li span').first
                        if caption_el.is_visible():
                            post_data['caption'] = caption_el.inner_text()[:300]
                    except:
                        post_data['caption'] = ''
                    
                    # Get likes
                    try:
                        likes_el = post_el.locator('span[aria-label*="like"]').first
                        if likes_el.is_visible():
                            post_data['likes'] = likes_el.inner_text()
                    except:
                        post_data['likes'] = ''
                    
                    posts.append(post_data)
                except Exception as e:
                    logger.error(f"Error extracting Instagram post {i}: {e}")
            
            logger.info(f"Retrieved {len(posts)} Instagram posts")
            return {'success': True, 'data': posts, 'count': len(posts)}
            
        except Exception as e:
            logger.error(f"Error getting Instagram posts: {e}")
            return {'success': False, 'error': str(e)}

    def health_check(self) -> Dict:
        """Check health of all platforms"""
        return {
            'status': 'healthy',
            'facebook': {
                'logged_in': self.logged_in_fb,
                'page_id': self.facebook_page_id,
                'credentials_set': bool(self.facebook_email and self.facebook_password)
            },
            'instagram': {
                'logged_in': self.logged_in_ig,
                'username': self.instagram_username,
                'credentials_set': bool(self.instagram_username and self.instagram_password)
            },
            'mock_mode': False,
            'timestamp': datetime.now().isoformat()
        }

    def cleanup(self):
        """Cleanup resources"""
        self.save_session()
        self.stop_browser()


# Global MCP instance
unified_mcp = UnifiedSocialMCP()


if __name__ == '__main__':
    print("=" * 60)
    print("UNIFIED SOCIAL MEDIA MCP SERVER")
    print("Facebook + Instagram - NO TOKENS REQUIRED!")
    print("=" * 60)
    
    print("\nConfiguration:")
    print(f"  Facebook Page: {unified_mcp.facebook_page_id}")
    print(f"  Instagram: @{unified_mcp.instagram_username}")
    print(f"  Facebook Email: {'Set' if unified_mcp.facebook_email else 'Not Set'}")
    print(f"  Instagram Password: {'Set' if unified_mcp.instagram_password else 'Not Set'}")
    
    print("\n" + "=" * 60)
    print("Testing Health Check...")
    health = unified_mcp.health_check()
    print(json.dumps(health, indent=2))
    
    print("\n" + "=" * 60)
    print("To configure credentials, update .env file:")
    print("  FACEBOOK_EMAIL=your@email.com")
    print("  FACEBOOK_PASSWORD=your_password")
    print("  INSTAGRAM_USERNAME=shamaansari5576")
    print("  INSTAGRAM_PASSWORD=your_password")
    print("=" * 60)
