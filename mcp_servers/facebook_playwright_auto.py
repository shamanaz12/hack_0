"""
Facebook Browser Automation with Playwright
No Graph API tokens required - uses real browser automation

Features:
- One-time login with session persistence
- Headless/headed mode toggle
- Post creation, reading, deletion
- Message/comment reading and replies
- Rate limiting and error handling
- Captcha/block detection

Usage:
    pip install -r requirements_facebook_auto.txt
    playwright install
    python facebook_playwright_auto.py
"""

import os
import sys
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
except ImportError:
    print("ERROR: Playwright not installed. Run: pip install playwright && playwright install")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configuration
FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL', '')
FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD', '')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', '61578538607212')
FACEBOOK_PAGE_URL = os.getenv('FACEBOOK_PAGE_URL', 'https://www.facebook.com/profile.php?id=61578538607212')

# CRITICAL: Use visible browser to avoid CAPTCHA detection
HEADLESS = os.getenv('FACEBOOK_HEADLESS', 'false').lower() == 'true'  # Changed default to False
SLOW_MO = int(os.getenv('FACEBOOK_SLOW_MO', '50'))

# CRITICAL: Persistent browser profile directory
BASE_DIR = Path('facebook_browser_profile')
BASE_DIR.mkdir(exist_ok=True)
USER_DATA_DIR = BASE_DIR / 'Default'  # Chrome uses 'Default' subdirectory
USER_DATA_DIR.mkdir(exist_ok=True)

# Paths
AUTH_FILE = Path('facebook_auth.json')
SESSION_FILE = BASE_DIR / 'session_info.json'
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'facebook_auto.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FacebookAutomation:
    """
    Facebook Browser Automation using Playwright
    Implements human-like behavior to avoid detection
    """
    
    def __init__(self, headless: bool = HEADLESS, slow_mo: int = SLOW_MO):
        self.headless = headless
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.logged_in = False
        self.last_action_time = datetime.now() - timedelta(minutes=5)  # Start with cooldown
        
        # Rate limiting
        self.min_delay = 3  # Minimum seconds between actions
        self.max_delay = 8  # Maximum seconds between actions
        self.action_count = 0
        self.max_actions_before_break = 10
        self.break_duration = 300  # 5 minutes break after max actions
        
    def _random_delay(self, min_sec: float = None, max_sec: float = None):
        """Add random delay to mimic human behavior"""
        min_sec = min_sec or self.min_delay
        max_sec = max_sec or self.max_delay
        delay = random.uniform(min_sec, max_sec)
        logger.debug(f"Waiting {delay:.1f}s...")
        time.sleep(delay)
    
    def _rate_limit_check(self):
        """Check and enforce rate limits"""
        self.action_count += 1
        
        if self.action_count >= self.max_actions_before_break:
            logger.info(f"Rate limit reached. Taking {self.break_duration}s break...")
            time.sleep(self.break_duration)
            self.action_count = 0
        
        # Random delay between actions
        self._random_delay()
    
    def _check_for_blocks(self, page: Page) -> bool:
        """Check if Facebook has blocked or shown captcha"""
        try:
            # Check for common block indicators
            page_content = page.content()
            
            block_indicators = [
                'suspicious login attempt',
                'unusual activity',
                'confirm your identity',
                'security check',
                'captcha',
                'temporarily blocked'
            ]
            
            for indicator in block_indicators:
                if indicator.lower() in page_content.lower():
                    logger.warning(f"Potential block detected: {indicator}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking for blocks: {e}")
            return False
    
    def start_browser(self, use_persistent: bool = True):
        """
        Initialize browser with persistent profile option
        
        Args:
            use_persistent: If True, use persistent user data directory (avoids CAPTCHA)
        """
        logger.info(f"Starting browser (headless={self.headless}, persistent={use_persistent})...")

        if use_persistent:
            # CRITICAL: Use persistent context to reuse browser profile
            # This avoids CAPTCHA by maintaining browser fingerprints
            logger.info(f"Using persistent profile: {USER_DATA_DIR}")
            
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=self.headless,
                slow_mo=self.slow_mo,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--window-size=1920,1080',
                    '--disable-notifications',
                    '--lang=en-US',
                ]
            )
            self.context = self.browser
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        else:
            # Fallback to non-persistent (for testing)
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--window-size=1920,1080'
                ]
            )

            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='Asia/Karachi',  # Match user location
            )
            self.context.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
            self.page = self.context.new_page()
        
        logger.info("Browser started successfully")
    
    def stop_browser(self):
        """Close browser"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Browser stopped")
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")
    
    def save_session(self):
        """Save authentication cookies and session metadata"""
        if not self.context:
            return False

        try:
            cookies = self.context.cookies()
            with open(AUTH_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'cookies': cookies,
                    'saved_at': datetime.now().isoformat(),
                    'email': FACEBOOK_EMAIL
                }, f, indent=2)
            
            # Also save session metadata
            session_info = {
                'email': FACEBOOK_EMAIL,
                'logged_in_at': datetime.now().isoformat(),
                'valid_until': (datetime.now() + timedelta(hours=24)).isoformat(),
                'browser_profile': str(USER_DATA_DIR),
                'consecutive_failures': 0
            }
            with open(SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(session_info, f, indent=2)
            
            logger.info(f"Session saved to {AUTH_FILE} and {SESSION_FILE}")
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False

    def load_session_info(self) -> bool:
        """Load session metadata and check validity"""
        if not SESSION_FILE.exists():
            logger.info("No saved session info found")
            return False
        
        try:
            with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                session_info = json.load(f)
            
            # Check if session is still valid
            valid_until = datetime.fromisoformat(session_info.get('valid_until', ''))
            if datetime.now() > valid_until:
                logger.info("Session expired (older than 24 hours)")
                return False
            
            # Check if email matches
            if session_info.get('email') != FACEBOOK_EMAIL:
                logger.info("Session email mismatch")
                return False
            
            logger.info(f"Session valid until: {valid_until}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return False

    def load_session(self) -> bool:
        """Load saved authentication cookies"""
        if not AUTH_FILE.exists():
            logger.info("No saved session found")
            return False

        try:
            with open(AUTH_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check if session is expired (24 hours)
            saved_at = datetime.fromisoformat(data['saved_at'])
            if datetime.now() - saved_at > timedelta(hours=24):
                logger.info("Session expired (older than 24 hours)")
                return False

            if not self.context:
                self.start_browser()

            self.context.add_cookies(data['cookies'])
            logger.info("Session loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return False
    
    def _print_page_info(self, step: str):
        """Print current page information for debugging"""
        if not self.page:
            return
        
        try:
            title = self.page.title()
            url = self.page.url
            
            logger.info(f"\n{'='*60}")
            logger.info(f"  PAGE INFO - {step}")
            logger.info(f"{'='*60}")
            logger.info(f"  URL:   {url}")
            logger.info(f"  Title: {title}")
            
            # Count input fields
            try:
                inputs = self.page.locator('input').all()
                visible_inputs = [i for i in inputs if i.is_visible(timeout=1000)]
                logger.info(f"  Visible input fields: {len(visible_inputs)}")
                
                for i, inp in enumerate(visible_inputs[:5]):
                    inp_type = inp.get_attribute('type')
                    inp_id = inp.get_attribute('id')
                    inp_name = inp.get_attribute('name')
                    inp_placeholder = inp.get_attribute('placeholder')
                    logger.info(f"    [{i}] type={inp_type}, id={inp_id}, name={inp_name}")
                    if inp_placeholder:
                        logger.info(f"         placeholder: '{inp_placeholder}'")
            except Exception as e:
                logger.warning(f"  Could not enumerate inputs: {e}")
            
            logger.info(f"{'='*60}\n")
            
        except Exception as e:
            logger.warning(f"Error getting page info: {e}")

    def _handle_cookie_consent(self) -> bool:
        """Handle cookie consent popup"""
        logger.info("Checking for cookie consent...")
        
        cookie_selectors = [
            '[aria-label="Cookie Policy"]',
            '[data-cookiebanner]',
            'button:has-text("Accept All")',
            'button:has-text("Accept")',
            'button:has-text("Allow")',
        ]
        
        for selector in cookie_selectors:
            try:
                cookie_btn = self.page.locator(selector).first
                if cookie_btn.is_visible(timeout=2000):
                    logger.info(f"Clicking cookie consent: {selector}")
                    cookie_btn.click()
                    time.sleep(2)
                    return True
            except:
                continue
        
        return False

    def _handle_saved_account(self) -> bool:
        """Handle saved account/checkpoint screen"""
        logger.info("Checking for saved account screen...")
        
        if 'checkpoint' in self.page.url.lower() or 'save-device' in self.page.url.lower():
            logger.warning("Saved account/checkpoint detected")
            
            try:
                saved_account = self.page.locator('[role="button"]').first
                if saved_account.is_visible(timeout=3000):
                    logger.info("Clicking saved account...")
                    saved_account.click()
                    time.sleep(3)
                    return True
            except Exception as e:
                logger.warning(f"Could not click saved account: {e}")
        
        return False

    def _find_email_field(self) -> tuple:
        """Find email field with robust fallback strategy"""
        logger.info("Searching for email/username field...")

        # Priority-ordered selector strategies (updated for dynamic IDs)
        selector_strategies = [
            # Primary: name-based (stable across Facebook updates)
            ('input[name="email"]', 'Name=email (PRIMARY)'),
            
            # Standard Facebook selectors (may not work with dynamic IDs)
            ('#email', 'Standard #email'),
            
            # Type-based (but text is too generic)
            ('input[type="email"]', 'Email type input'),
            
            # Alternative names
            ('input[name="login"]', 'Login name input'),
            ('input[name="ident"]', 'Ident name input'),
            
            # Aria-based selectors
            ('[aria-label*="email" i]', 'Aria label with email'),
            ('[aria-label*="phone" i]', 'Aria label with phone'),
            
            # Placeholder-based
            ('input[placeholder*="email" i]', 'Placeholder with email'),
            ('input[placeholder*="phone" i]', 'Placeholder with phone'),
            ('input[placeholder*="Log in" i]', 'Placeholder with Log in'),
            
            # Mobile selectors
            ('#m_login_email', 'Mobile email selector'),
            
            # Fallback: text input with name=email (handles dynamic IDs)
            ('input[type="text"][name="email"]', 'Text+name=email (FALLBACK)'),
        ]

        for selector, description in selector_strategies:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=2000):
                    logger.info(f"Found email field: {description}")
                    return (locator, selector)
            except:
                continue

        logger.error("Email field NOT FOUND with any selector")
        return (None, None)

    def _find_password_field(self) -> tuple:
        """Find password field with fallback strategy"""
        logger.info("Searching for password field...")
        
        selector_strategies = [
            ('#pass', 'Standard #pass'),
            ('input[type="password"]', 'Password type input'),
            ('input[name="pass"]', 'Password name input'),
            ('[aria-label*="password" i]', 'Aria label with password'),
        ]
        
        for selector, description in selector_strategies:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=2000):
                    logger.info(f"Found password field: {description}")
                    return (locator, selector)
            except:
                continue
        
        logger.error("Password field NOT FOUND")
        return (None, None)

    def _find_login_button(self) -> tuple:
        """Find login button"""
        logger.info("Searching for login button...")
        
        # Wait for page to fully render
        time.sleep(2)
        
        selector_strategies = [
            # Text-based (most reliable)
            ('button:has-text("Log In")', 'Log In text'),
            ('button:has-text("Log in")', 'Log in text'),
            ('button:has-text("Login")', 'Login text'),
            
            # Type-based
            ('button[type="submit"]', 'Submit button'),
            ('input[type="submit"]', 'Submit input'),
            
            # Value-based
            ('[value*="Log" i]', 'Value with Log'),
            ('[value*="log" i]', 'Value with log'),
            
            # Aria-based
            ('[aria-label*="Log" i]', 'Aria label with Log'),
            
            # Role-based
            ('button[role="button"]', 'Button role'),
        ]
        
        for selector, description in selector_strategies:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=3000):
                    logger.info(f"Found login button: {description}")
                    return (locator, selector)
            except:
                continue
        
        # Last resort: find any button with login-like text
        logger.warning("Trying fallback: searching for any button...")
        try:
            buttons = self.page.locator('button').all()
            for btn in buttons:
                try:
                    if btn.is_visible(timeout=1000):
                        btn_text = btn.inner_text().strip().lower()
                        if 'log' in btn_text or 'sign' in btn_text or 'continue' in btn_text:
                            logger.info(f"Found login button by text: '{btn_text}'")
                            return (btn, f"button:text='{btn_text}'")
                except:
                    continue
        except:
            pass
        
        logger.error("Login button NOT FOUND")
        return (None, None)

    def _check_for_captcha(self) -> bool:
        """
        Detect if BLOCKING CAPTCHA or security check is present
        
        Returns True only if CAPTCHA is blocking automation
        """
        try:
            # Blocking CAPTCHA indicators (must solve to proceed)
            blocking_indicators = [
                'recaptcha-checkbox',  # Actual reCAPTCHA widget
                'captcha-form',
                'security check required',
                'unusual activity detected',
                'suspicious login attempt',
                'confirm your identity to continue',
                'checkpoint/challenge/',
            ]
            
            page_content = self.page.content().lower()
            
            for indicator in blocking_indicators:
                if indicator in page_content:
                    logger.warning(f"Blocking CAPTCHA detected: {indicator}")
                    return True
            
            # Check URL for blocking paths
            blocking_urls = [
                '/checkpoint/challenge/',
                '/checkpoint/block/',
                '/captcha/',
            ]
            
            for url_pattern in blocking_urls:
                if url_pattern in self.page.url.lower():
                    logger.warning(f"Blocking CAPTCHA URL: {self.page.url}")
                    return True
            
            # Non-blocking reCAPTCHA may exist in page but not block automation
            # Only report if it's actually blocking
            return False
            
        except Exception as e:
            logger.error(f"Error checking for CAPTCHA: {e}")
            return False

    def _wait_for_human_completion(self, timeout_seconds: int = 300) -> bool:
        """
        Wait for human to complete CAPTCHA/login
        
        Args:
            timeout_seconds: Max time to wait (default 5 minutes)
        
        Returns:
            True if completed successfully, False if timeout
        """
        logger.warning("=" * 60)
        logger.warning("SECURITY CHECK DETECTED")
        logger.warning("=" * 60)
        logger.warning("Please complete the security check manually in the browser.")
        logger.warning(f"Waiting {timeout_seconds}s for completion...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                # Check if we've moved past the security page
                if not self._check_for_captcha():
                    # Verify we're on Facebook
                    if 'facebook.com' in self.page.url and 'login' not in self.page.url.lower():
                        logger.info("Security check completed!")
                        return True
                
                time.sleep(3)
                
            except Exception as e:
                logger.warning(f"Error checking status: {e}")
                time.sleep(3)
        
        logger.error("Timeout waiting for security check completion")
        return False

    def login(self) -> bool:
        """
        Login to Facebook with anti-CAPTCHA strategy
        
        Strategy:
        1. Use persistent browser profile (avoids fresh login detection)
        2. Use visible browser (not headless)
        3. Human-like delays
        4. Check for CAPTCHA and wait for human completion
        5. Save session immediately after success
        """
        if not self.page:
            self.start_browser(use_persistent=True)  # CRITICAL: Use persistent profile

        logger.info("=" * 60)
        logger.info("FACEBOOK LOGIN - ANTI-CAPTCHA VERSION")
        logger.info("=" * 60)

        try:
            # Navigate to login page
            logger.info("Navigating to Facebook login...")
            self.page.goto('https://www.facebook.com/login', wait_until='networkidle', timeout=30000)
            time.sleep(5)  # Extra wait for full render (human-like)

            # Print page info for debugging
            self._print_page_info("After Navigation")
            
            # CRITICAL: Check for CAPTCHA immediately
            if self._check_for_captcha():
                logger.warning("CAPTCHA detected before login")
                if not self._wait_for_human_completion(300):
                    logger.error("CAPTCHA completion failed")
                    return False

            # Handle cookie consent
            if self._handle_cookie_consent():
                time.sleep(2)
                self._print_page_info("After Cookie Consent")

            # Handle saved account
            if self._handle_saved_account():
                time.sleep(2)
                self._print_page_info("After Saved Account")

            # Find email field with fallback strategy
            email_field, email_selector = self._find_email_field()
            if email_field is None:
                logger.error("CRITICAL: Cannot proceed without email field")
                self._print_page_info("Login Failed - No Email Field")
                return False

            # Find password field
            password_field, password_selector = self._find_password_field()
            if password_field is None:
                logger.error("CRITICAL: Cannot proceed without password field")
                return False

            # Find login button
            login_button, login_selector = self._find_login_button()
            if login_button is None:
                logger.error("CRITICAL: Cannot proceed without login button")
                return False

            # Enter credentials with HUMAN-LIKE timing
            logger.info("Entering credentials...")
            email_field.fill(FACEBOOK_EMAIL)
            time.sleep(random.uniform(1.5, 2.5))  # Human-like delay
            password_field.fill(FACEBOOK_PASSWORD)
            time.sleep(random.uniform(1.5, 2.5))  # Human-like delay

            # Click login
            login_button.click()
            logger.info("Login submitted, waiting...")
            time.sleep(5)

            # CRITICAL: Check for CAPTCHA after login attempt
            if self._check_for_captcha():
                logger.warning("CAPTCHA detected after login")
                if not self._wait_for_human_completion(300):
                    logger.error("Post-login CAPTCHA completion failed")
                    return False
                logger.info("CAPTCHA completed successfully")

            # Check result
            if 'facebook.com' in self.page.url and 'login' not in self.page.url.lower() and 'checkpoint' not in self.page.url.lower():
                logger.info("Login SUCCESSFUL!")
                self.logged_in = True
                self.save_session()  # Save immediately
                return True
            else:
                logger.warning("Still on login/checkpoint page - check credentials")
                self._print_page_info("After Login Attempt")
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def ensure_logged_in(self) -> bool:
        """
        Ensure logged in with session reuse
        
        Priority:
        1. Check if persistent browser profile already has session
        2. Load cookies if available
        3. Only login if necessary
        """
        # Start browser with persistent profile FIRST
        if not self.page:
            self.start_browser(use_persistent=True)
        
        # Navigate to Facebook to check if already logged in
        logger.info("Checking existing session...")
        self.page.goto('https://www.facebook.com', wait_until='networkidle', timeout=30000)
        time.sleep(5)
        
        # Check if already logged in (session reused from persistent profile)
        if 'login' not in self.page.url.lower() and 'checkpoint' not in self.page.url.lower():
            logger.info("Already logged in (persistent session reused)")
            self._print_page_info("Session Check")
            self.logged_in = True
            return True
        
        # Check for CAPTCHA on the page
        if self._check_for_captcha():
            logger.warning("Security check detected on homepage")
            if not self._wait_for_human_completion(300):
                return False
            # Re-check login status after CAPTCHA
            if 'login' not in self.page.url.lower():
                logger.info("Security check passed, now logged in")
                self.logged_in = True
                return True
        
        # Need to login
        logger.info("Session expired, logging in...")
        return self.login()
    
    def navigate_to_page(self) -> bool:
        """Navigate to Facebook Business Page - Direct Redirect"""
        if not self.logged_in:
            if not self.ensure_logged_in():
                return False

        logger.info(f"Navigating to business page: {FACEBOOK_PAGE_URL}")

        try:
            # Direct redirect to business page
            self.page.goto(FACEBOOK_PAGE_URL, wait_until='networkidle')
            self._random_delay(3, 5)

            logger.info(f"Successfully navigated to business page: {FACEBOOK_PAGE_ID}")
            return True

        except Exception as e:
            logger.error(f"Error navigating to page: {e}")
            return False
    
    def create_post(self, message: str, link: str = None) -> Dict:
        """Create a new post on Facebook page"""
        logger.info(f"Creating post: {message[:50]}...")
        
        self._rate_limit_check()
        
        if not self.ensure_logged_in():
            return {'success': False, 'error': 'Not logged in'}
        
        try:
            # Navigate to page
            if not self.navigate_to_page():
                return {'success': False, 'error': 'Could not navigate to page'}
            
            # Find the post creation box
            self._random_delay(2, 3)
            
            # Try to find "What's on your mind?" box
            post_selectors = [
                '[data-testid="create_post"]',
                'div[role="textbox"]',
                '.mbs._6m2._6m3',
                'textarea[name="xh8qjy"]',
            ]
            
            post_box = None
            for selector in post_selectors:
                try:
                    post_box = self.page.locator(selector).first
                    if post_box.is_visible(timeout=5000):
                        break
                    post_box = None
                except:
                    continue
            
            if not post_box:
                # Fallback: try to click on any compose button first
                logger.info("Trying to find compose button...")
                compose_btn = self.page.locator('button').filter(has_text='Post').first
                if compose_btn.is_visible(timeout=5000):
                    compose_btn.click()
                    self._random_delay(2, 3)
                    post_box = self.page.locator('textarea').first
            
            if post_box:
                post_box.click()
                self._random_delay(1, 2)
                post_box.fill(message)
                self._random_delay(1, 2)
                
                # Add link if provided
                if link:
                    logger.info(f"Adding link: {link}")
                    # Try to find link input
                    try:
                        link_input = self.page.locator('input[type="url"]').first
                        link_input.fill(link)
                        self._random_delay(2, 3)
                    except:
                        # If no link input found, append to message
                        post_box.press('Enter')
                        self._random_delay(1, 2)
                        post_box.type(f' {link}')
                
                # Click Post button
                post_button = self.page.locator('button').filter(has_text='Post').first
                if post_button.is_visible(timeout=5000):
                    post_button.click()
                    self._random_delay(3, 5)
                    
                    # Wait for post to be published
                    self.page.wait_for_load_state('networkidle')
                    
                    logger.info("Post created successfully!")
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
                    logger.error("Post button not found")
                    return {'success': False, 'error': 'Post button not found'}
            else:
                logger.error("Post creation box not found")
                return {'success': False, 'error': 'Post box not found'}
                
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_recent_posts(self, limit: int = 5) -> Dict:
        """Get recent posts from Facebook page"""
        logger.info(f"Getting recent posts (limit: {limit})...")
        
        self._rate_limit_check()
        
        if not self.ensure_logged_in():
            return {'success': False, 'error': 'Not logged in'}
        
        try:
            if not self.navigate_to_page():
                return {'success': False, 'error': 'Could not navigate to page'}
            
            self._random_delay(3, 5)
            
            # Scroll to load posts
            for _ in range(3):
                self.page.evaluate('window.scrollBy(0, 1000)')
                self._random_delay(1, 2)
            
            # Find posts
            posts = []
            
            # Try different post selectors
            post_selectors = [
                '[role="article"]',
                '.ecm0bbzt',
                '[data-pagelet="MainFeed"] > div > div',
            ]
            
            post_elements = None
            for selector in post_selectors:
                try:
                    post_elements = self.page.locator(selector)
                    count = post_elements.count()
                    if count > 0:
                        logger.info(f"Found {count} posts with selector: {selector}")
                        break
                    post_elements = None
                except:
                    continue
            
            if post_elements:
                count = min(post_elements.count(), limit)
                
                for i in range(count):
                    try:
                        post_el = post_elements.nth(i)
                        if not post_el.is_visible():
                            continue
                        
                        # Extract post data
                        post_data = {
                            'index': i,
                            'extracted_at': datetime.now().isoformat()
                        }
                        
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
                                post_data['timestamp'] = time_el.get_attribute('title') or time_el.inner_text()
                        except:
                            post_data['timestamp'] = ''
                        
                        # Get likes/comments
                        try:
                            stats_el = post_el.locator('[data-pagelet="UFI2"]').first
                            if stats_el.is_visible():
                                post_data['stats'] = stats_el.inner_text()[:200]
                        except:
                            post_data['stats'] = ''
                        
                        posts.append(post_data)
                        
                    except Exception as e:
                        logger.error(f"Error extracting post {i}: {e}")
                        continue
            
            logger.info(f"Extracted {len(posts)} posts")
            
            return {
                'success': True,
                'data': posts,
                'count': len(posts)
            }
            
        except Exception as e:
            logger.error(f"Error getting posts: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_post(self, post_id: str = None, post_url: str = None) -> Dict:
        """Delete a Facebook post"""
        logger.info(f"Deleting post: {post_id or post_url}")
        
        self._rate_limit_check()
        
        if not self.ensure_logged_in():
            return {'success': False, 'error': 'Not logged in'}
        
        try:
            # Navigate to post
            if post_url:
                self.page.goto(post_url, wait_until='networkidle')
            elif post_id:
                self.page.goto(f'https://www.facebook.com/{post_id}', wait_until='networkidle')
            else:
                return {'success': False, 'error': 'Post ID or URL required'}
            
            self._random_delay(2, 3)
            
            # Find post options menu (three dots)
            options_btn = self.page.locator('[aria-label="More options"]').first
            
            if not options_btn.is_visible(timeout=5000):
                options_btn = self.page.locator('div[role="button"]').filter(has_text='···').first
            
            if options_btn.is_visible():
                options_btn.click()
                self._random_delay(1, 2)
                
                # Find delete/trash option
                delete_btn = self.page.locator('div[role="menuitem"]').filter(has_text='Delete')
                
                if delete_btn.is_visible(timeout=5000):
                    delete_btn.click()
                    self._random_delay(1, 2)
                    
                    # Confirm deletion
                    confirm_btn = self.page.locator('button').filter(has_text='Delete')
                    if confirm_btn.is_visible(timeout=5000):
                        confirm_btn.click()
                        self._random_delay(2, 3)
                        
                        logger.info("Post deleted successfully")
                        return {
                            'success': True,
                            'message': 'Post deleted successfully',
                            'post_id': post_id
                        }
            
            logger.error("Could not find delete option")
            return {'success': False, 'error': 'Delete option not found'}
            
        except Exception as e:
            logger.error(f"Error deleting post: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_page_messages(self, limit: int = 10) -> Dict:
        """Get messages/comments from page inbox"""
        logger.info(f"Getting page messages (limit: {limit})...")
        
        self._rate_limit_check()
        
        if not self.ensure_logged_in():
            return {'success': False, 'error': 'Not logged in'}
        
        try:
            # Navigate to Meta Business Suite inbox
            self.page.goto('https://business.facebook.com/latest/inbox', wait_until='networkidle')
            self._random_delay(3, 5)
            
            messages = []
            
            # Find message threads
            message_threads = self.page.locator('[role="row"]')
            count = min(message_threads.count(), limit)
            
            for i in range(count):
                try:
                    thread = message_threads.nth(i)
                    if not thread.is_visible():
                        continue
                    
                    message_data = {
                        'index': i,
                        'extracted_at': datetime.now().isoformat()
                    }
                    
                    # Extract sender
                    try:
                        sender_el = thread.locator('[dir="auto"]').first
                        message_data['sender'] = sender_el.inner_text()[:100]
                    except:
                        message_data['sender'] = ''
                    
                    # Extract message preview
                    try:
                        preview_el = thread.locator('[dir="auto"]').nth(1)
                        message_data['preview'] = preview_el.inner_text()[:200]
                    except:
                        message_data['preview'] = ''
                    
                    # Extract timestamp
                    try:
                        time_el = thread.locator('time').first
                        message_data['timestamp'] = time_el.get_attribute('datetime') or time_el.inner_text()
                    except:
                        message_data['timestamp'] = ''
                    
                    messages.append(message_data)
                    
                except Exception as e:
                    logger.error(f"Error extracting message {i}: {e}")
                    continue
            
            logger.info(f"Extracted {len(messages)} messages")
            
            return {
                'success': True,
                'data': messages,
                'count': len(messages)
            }
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return {'success': False, 'error': str(e)}
    
    def reply_to_message(self, message_id: str, reply_text: str) -> Dict:
        """Reply to a message in inbox"""
        logger.info(f"Replying to message: {message_id}")
        
        self._rate_limit_check()
        
        if not self.ensure_logged_in():
            return {'success': False, 'error': 'Not logged in'}
        
        try:
            # Navigate to inbox
            self.page.goto('https://business.facebook.com/latest/inbox', wait_until='networkidle')
            self._random_delay(3, 5)
            
            # Click on the message thread
            # This is simplified - in production you'd need to match message_id
            message_thread = self.page.locator('[role="row"]').first
            message_thread.click()
            self._random_delay(2, 3)
            
            # Find reply input
            reply_input = self.page.locator('[contenteditable="true"]').first
            reply_input.click()
            self._random_delay(1, 2)
            reply_input.fill(reply_text)
            self._random_delay(1, 2)
            
            # Send reply
            send_btn = self.page.locator('button').filter(has_text='Send')
            if send_btn.is_visible(timeout=5000):
                send_btn.click()
                self._random_delay(2, 3)
                
                logger.info("Reply sent successfully")
                return {
                    'success': True,
                    'message': 'Reply sent successfully',
                    'reply_text': reply_text
                }
            else:
                logger.error("Send button not found")
                return {'success': False, 'error': 'Send button not found'}
            
        except Exception as e:
            logger.error(f"Error replying to message: {e}")
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> Dict:
        """Check if automation is working"""
        try:
            if not self.page:
                return {
                    'status': 'not_started',
                    'message': 'Browser not started'
                }
            
            # Try to navigate to Facebook
            self.page.goto('https://www.facebook.com', wait_until='networkidle', timeout=10000)
            
            # Check if logged in
            is_logged_in = 'login' not in self.page.url.lower()
            
            return {
                'status': 'healthy' if is_logged_in else 'needs_login',
                'logged_in': is_logged_in,
                'url': self.page.url,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Global automation instance
fb_auto = None


def get_automation() -> FacebookAutomation:
    """Get or create automation instance"""
    global fb_auto
    if fb_auto is None:
        fb_auto = FacebookAutomation()
    return fb_auto


def cleanup():
    """Cleanup automation instance"""
    global fb_auto
    if fb_auto:
        fb_auto.stop_browser()
        fb_auto = None


# For testing
if __name__ == '__main__':
    print("=" * 60)
    print("Facebook Playwright Automation Test")
    print("=" * 60)
    
    # Check credentials
    if not FACEBOOK_EMAIL or not FACEBOOK_PASSWORD:
        print("\n⚠️  WARNING: Facebook credentials not set!")
        print("Please set FACEBOOK_EMAIL and FACEBOOK_PASSWORD in .env file")
        print("\nRunning in demo mode...")
    else:
        print(f"\n✓ Email configured: {FACEBOOK_EMAIL}")
        print(f"✓ Page ID: {FACEBOOK_PAGE_ID}")
    
    # Test automation
    auto = get_automation()
    
    try:
        # Health check
        print("\n[1/4] Health Check...")
        health = auto.health_check()
        print(f"Status: {health}")
        
        if FACEBOOK_EMAIL and FACEBOOK_PASSWORD:
            # Login
            print("\n[2/4] Logging in...")
            logged_in = auto.ensure_logged_in()
            print(f"Logged in: {logged_in}")
            
            if logged_in:
                # Get posts
                print("\n[3/4] Getting recent posts...")
                posts = auto.get_recent_posts(3)
                print(f"Posts found: {posts.get('count', 0)}")
                
                # Create post
                print("\n[4/4] Creating test post...")
                result = auto.create_post(f"Test post from automation {datetime.now().strftime('%H:%M')}")
                print(f"Post result: {result}")
        else:
            print("\n⊠ Skipping login tests (no credentials)")
    
    finally:
        cleanup()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
