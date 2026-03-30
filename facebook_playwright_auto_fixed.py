"""
Facebook Browser Automation with Playwright - FIXED VERSION
Addresses: Page.fill: Timeout 30000ms exceeded waiting for #email

Fixes Applied:
1. Dynamic selector detection with fallback strategies
2. Cookie consent handling
3. Saved account/checkpoint handling
4. Enhanced CLI debugging visibility
5. Improved page load detection
6. Session reuse optimization

Usage:
    python facebook_playwright_auto_fixed.py
"""

import os
import sys
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeout
except ImportError:
    print("ERROR: Playwright not installed. Run: pip install playwright && playwright install")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configuration
FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL', '')
FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD', '')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', '956241877582673')
HEADLESS = os.getenv('FACEBOOK_HEADLESS', 'false').lower() == 'true'
SLOW_MO = int(os.getenv('FACEBOOK_SLOW_MO', '50'))

# Paths
AUTH_FILE = Path('facebook_auth.json')
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'facebook_auto_fixed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FacebookAutomationFixed:
    """
    Facebook Browser Automation - Fixed Version
    Implements robust selector detection and edge case handling
    """

    def __init__(self, headless: bool = HEADLESS, slow_mo: int = SLOW_MO):
        self.headless = headless
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.logged_in = False
        self.last_action_time = datetime.now() - timedelta(minutes=5)

        # Rate limiting
        self.min_delay = 2
        self.max_delay = 5
        self.action_count = 0
        self.max_actions_before_break = 10
        self.break_duration = 300

        # Selector cache (avoids re-detection)
        self.selector_cache: Dict[str, str] = {}

    def _log(self, message: str, level: str = "INFO"):
        """Unified logging with CLI visibility"""
        timestamp = time.strftime('%H:%M:%S')
        log_line = f"{timestamp} - {level} - {message}"
        if level == "ERROR":
            logger.error(message)
            print(f"  [ERROR] {message}")
        elif level == "SUCCESS":
            logger.info(message)
            print(f"  [OK] {message}")
        elif level == "WARN":
            logger.warning(message)
            print(f"  [WARN] {message}")
        else:
            logger.info(message)
            print(f"  [INFO] {message}")

    def _random_delay(self, min_sec: float = None, max_sec: float = None):
        """Add random delay to mimic human behavior"""
        min_sec = min_sec or self.min_delay
        max_sec = max_sec or self.max_delay
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def _rate_limit_check(self):
        """Check and enforce rate limits"""
        self.action_count += 1
        if self.action_count >= self.max_actions_before_break:
            self._log(f"Rate limit reached. Taking {self.break_duration}s break...", "WARN")
            time.sleep(self.break_duration)
            self.action_count = 0
        self._random_delay()

    def start_browser(self):
        """Initialize browser with anti-detection"""
        self._log("Starting browser...")
        
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
            timezone_id='Asia/Karachi'
        )
        
        self.context.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
        self.page = self.context.new_page()
        
        self._log("Browser started successfully", "SUCCESS")

    def stop_browser(self):
        """Close browser"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self._log("Browser stopped", "SUCCESS")
        except Exception as e:
            self._log(f"Error stopping browser: {e}", "ERROR")

    def save_session(self):
        """Save authentication cookies"""
        if not self.context:
            return False
        try:
            cookies = self.context.cookies()
            with open(AUTH_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'cookies': cookies,
                    'saved_at': datetime.now().isoformat(),
                    'email': FACEBOOK_EMAIL
                }, f, indent=2, ensure_ascii=False)
            self._log(f"Session saved to {AUTH_FILE}", "SUCCESS")
            return True
        except Exception as e:
            self._log(f"Error saving session: {e}", "ERROR")
            return False

    def load_session(self) -> bool:
        """Load saved authentication cookies"""
        if not AUTH_FILE.exists():
            self._log("No saved session found")
            return False
        try:
            with open(AUTH_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            saved_at = datetime.fromisoformat(data['saved_at'])
            if datetime.now() - saved_at > timedelta(hours=24):
                self._log("Session expired (older than 24 hours)")
                return False
            
            if not self.context:
                self.start_browser()
            
            self.context.add_cookies(data['cookies'])
            self._log("Session loaded successfully", "SUCCESS")
            return True
        except Exception as e:
            self._log(f"Error loading session: {e}", "ERROR")
            return False

    def _print_page_info(self, step: str):
        """Print current page information for debugging"""
        if not self.page:
            return
        
        try:
            title = self.page.title()
            url = self.page.url
            
            self._log(f"\n{'='*60}")
            self._log(f"  PAGE INFO - {step}")
            self._log(f"{'='*60}")
            self._log(f"  URL:   {url}")
            self._log(f"  Title: {title}")
            
            # Count input fields
            try:
                inputs = self.page.locator('input').all()
                visible_inputs = [i for i in inputs if i.is_visible(timeout=1000)]
                self._log(f"  Visible input fields: {len(visible_inputs)}")
                
                for i, inp in enumerate(visible_inputs[:5]):
                    inp_type = inp.get_attribute('type')
                    inp_id = inp.get_attribute('id')
                    inp_name = inp.get_attribute('name')
                    inp_placeholder = inp.get_attribute('placeholder')
                    self._log(f"    [{i}] type={inp_type}, id={inp_id}, name={inp_name}")
                    if inp_placeholder:
                        self._log(f"         placeholder: '{inp_placeholder}'")
            except Exception as e:
                self._log(f"  Could not enumerate inputs: {e}", "WARN")
            
            self._log(f"{'='*60}\n")
            
        except Exception as e:
            self._log(f"Error getting page info: {e}", "WARN")

    def _handle_cookie_consent(self) -> bool:
        """Handle cookie consent popup"""
        self._log("Checking for cookie consent...")
        
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
                    self._log(f"Clicking cookie consent: {selector}")
                    cookie_btn.click()
                    time.sleep(2)
                    return True
            except:
                continue
        
        return False

    def _handle_saved_account(self) -> bool:
        """Handle saved account/checkpoint screen"""
        self._log("Checking for saved account screen...")
        
        if 'checkpoint' in self.page.url.lower() or 'save-device' in self.page.url.lower():
            self._log("Saved account/checkpoint detected", "WARN")
            
            try:
                saved_account = self.page.locator('[role="button"]').first
                if saved_account.is_visible(timeout=3000):
                    self._log("Clicking saved account...")
                    saved_account.click()
                    time.sleep(3)
                    return True
            except Exception as e:
                self._log(f"Could not click saved account: {e}", "WARN")
        
        return False

    def _find_email_field(self) -> Tuple[Optional[object], str]:
        """
        Find email field with robust fallback strategy
        Returns: (locator, selector_used)
        """
        self._log("Searching for email/username field...")
        
        # Check cache first
        if 'email' in self.selector_cache:
            cached_selector = self.selector_cache['email']
            try:
                locator = self.page.locator(cached_selector).first
                if locator.is_visible(timeout=2000):
                    self._log(f"Using cached selector: {cached_selector}", "SUCCESS")
                    return (locator, cached_selector)
            except:
                self._log("Cached selector no longer valid, re-detecting...")
        
        # Priority-ordered selector strategies (updated for dynamic IDs)
        selector_strategies = [
            # Primary: name-based (stable across Facebook updates)
            ('input[name="email"]', 'Name=email (PRIMARY)'),
            
            # Standard Facebook selectors (may not work with dynamic IDs)
            ('#email', 'Standard #email'),
            
            # Type-based
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
                    self._log(f"Found email field: {description}", "SUCCESS")
                    self.selector_cache['email'] = selector
                    return (locator, selector)
            except:
                continue
        
        self._log("Email field NOT FOUND with any selector", "ERROR")
        return (None, None)

    def _find_password_field(self) -> Tuple[Optional[object], str]:
        """Find password field with fallback strategy"""
        self._log("Searching for password field...")
        
        if 'password' in self.selector_cache:
            cached_selector = self.selector_cache['password']
            try:
                locator = self.page.locator(cached_selector).first
                if locator.is_visible(timeout=2000):
                    self._log(f"Using cached selector: {cached_selector}", "SUCCESS")
                    return (locator, cached_selector)
            except:
                pass
        
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
                    self._log(f"Found password field: {description}", "SUCCESS")
                    self.selector_cache['password'] = selector
                    return (locator, selector)
            except:
                continue
        
        self._log("Password field NOT FOUND", "ERROR")
        return (None, None)

    def _find_login_button(self) -> Tuple[Optional[object], str]:
        """Find login button"""
        self._log("Searching for login button...")
        
        # Wait a bit for page to fully render
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
                    self._log(f"Found login button: {description}", "SUCCESS")
                    return (locator, selector)
            except:
                continue
        
        # Last resort: find any button near the password field
        self._log("Trying fallback: searching for any submit-like button...", "WARN")
        try:
            buttons = self.page.locator('button').all()
            for btn in buttons:
                try:
                    if btn.is_visible(timeout=1000):
                        btn_text = btn.inner_text().strip().lower()
                        if 'log' in btn_text or 'sign' in btn_text or 'continue' in btn_text:
                            self._log(f"Found login button by text: '{btn_text}'", "SUCCESS")
                            return (btn, f"button:text='{btn_text}'")
                except:
                    continue
        except:
            pass
        
        self._log("Login button NOT FOUND with any selector", "ERROR")
        return (None, None)

    def login(self) -> bool:
        """Login to Facebook with robust error handling"""
        if not self.page:
            self.start_browser()

        self._log("=" * 60)
        self._log("FACEBOOK LOGIN - FIXED VERSION")
        self._log("=" * 60)

        try:
            # Navigate to login page
            self._log("Navigating to Facebook login...")
            self.page.goto('https://www.facebook.com/login', wait_until='networkidle', timeout=30000)
            time.sleep(3)  # Wait for full render
            
            # Print page info for debugging
            self._print_page_info("After Navigation")
            
            # Handle cookie consent
            if self._handle_cookie_consent():
                time.sleep(2)
                self._print_page_info("After Cookie Consent")
            
            # Handle saved account
            if self._handle_saved_account():
                time.sleep(2)
                self._print_page_info("After Saved Account")
            
            # Find email field
            email_field, email_selector = self._find_email_field()
            if email_field is None:
                self._log("CRITICAL: Cannot proceed without email field", "ERROR")
                self._print_page_info("Login Failed - No Email Field")
                return False
            
            # Find password field
            password_field, password_selector = self._find_password_field()
            if password_field is None:
                self._log("CRITICAL: Cannot proceed without password field", "ERROR")
                return False
            
            # Find login button
            login_button, login_selector = self._find_login_button()
            if login_button is None:
                self._log("CRITICAL: Cannot proceed without login button", "ERROR")
                return False
            
            # Enter credentials
            self._log("Entering credentials...")
            email_field.fill(FACEBOOK_EMAIL)
            time.sleep(1)
            password_field.fill(FACEBOOK_PASSWORD)
            time.sleep(1)
            
            # Click login
            login_button.click()
            self._log("Login submitted, waiting...")
            time.sleep(5)
            
            # Check result
            if 'facebook.com' in self.page.url and 'login' not in self.page.url.lower():
                self._log("Login SUCCESSFUL!", "SUCCESS")
                self.logged_in = True
                self.save_session()
                return True
            else:
                self._log("Still on login page - check credentials", "WARN")
                self._print_page_info("After Login Attempt")
                return False

        except Exception as e:
            self._log(f"Login error: {e}", "ERROR")
            return False

    def ensure_logged_in(self) -> bool:
        """Ensure logged in, using session if available"""
        if self.load_session():
            self.page.goto('https://www.facebook.com', wait_until='networkidle')
            time.sleep(3)
            
            if 'login' in self.page.url.lower():
                self._log("Session invalid, re-login required")
                return self.login()
            
            self._log("Session valid, already logged in", "SUCCESS")
            self.logged_in = True
            return True
        else:
            return self.login()

    def navigate_to_page(self) -> bool:
        """Navigate to Facebook page"""
        if not self.logged_in:
            if not self.ensure_logged_in():
                return False

        self._log(f"Navigating to page: {FACEBOOK_PAGE_ID}")

        try:
            urls_to_try = [
                f'https://www.facebook.com/{FACEBOOK_PAGE_ID}',
                f'https://www.facebook.com/pages/{FACEBOOK_PAGE_ID}',
            ]

            for url in urls_to_try:
                try:
                    self.page.goto(url, wait_until='networkidle')
                    time.sleep(2)
                    if 'error' not in self.page.url.lower():
                        self._log("Successfully navigated to page", "SUCCESS")
                        return True
                except:
                    continue

            self._log("Could not navigate to page", "ERROR")
            return False

        except Exception as e:
            self._log(f"Error navigating to page: {e}", "ERROR")
            return False

    def create_post(self, message: str, link: str = None) -> Dict:
        """Create a new post"""
        self._log(f"Creating post: {message[:50]}...")
        self._rate_limit_check()

        if not self.ensure_logged_in():
            return {'success': False, 'error': 'Not logged in'}

        try:
            if not self.navigate_to_page():
                return {'success': False, 'error': 'Could not navigate to page'}

            time.sleep(2)

            post_selectors = [
                '[data-testid="create_post"]',
                'div[role="textbox"]',
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
                compose_btn = self.page.locator('button').filter(has_text='Post').first
                if compose_btn.is_visible(timeout=5000):
                    compose_btn.click()
                    time.sleep(2)
                    post_box = self.page.locator('textarea').first

            if post_box:
                post_box.click()
                time.sleep(1)
                post_box.fill(message)
                time.sleep(1)

                if link:
                    try:
                        link_input = self.page.locator('input[type="url"]').first
                        link_input.fill(link)
                        time.sleep(2)
                    except:
                        post_box.press('Enter')
                        time.sleep(1)
                        post_box.type(f' {link}')

                post_button = self.page.locator('button').filter(has_text='Post').first
                if post_button.is_visible(timeout=5000):
                    post_button.click()
                    time.sleep(3)
                    self.page.wait_for_load_state('networkidle')
                    self._log("Post created successfully!", "SUCCESS")
                    return {
                        'success': True,
                        'message': 'Post created successfully',
                        'post_data': {
                            'message': message,
                            'link': link,
                            'created_at': datetime.now().isoformat()
                        }
                    }

            self._log("Post button not found", "ERROR")
            return {'success': False, 'error': 'Post button not found'}

        except Exception as e:
            self._log(f"Error creating post: {e}", "ERROR")
            return {'success': False, 'error': str(e)}

    def health_check(self) -> Dict:
        """Check automation status"""
        try:
            if not self.page:
                return {'status': 'not_started', 'message': 'Browser not started'}

            self.page.goto('https://www.facebook.com', wait_until='networkidle', timeout=15000)
            time.sleep(2)

            is_logged_in = 'login' not in self.page.url.lower()
            
            return {
                'status': 'healthy' if is_logged_in else 'needs_login',
                'logged_in': is_logged_in,
                'url': self.page.url,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


# Global instance
_auto_instance: Optional[FacebookAutomationFixed] = None


def get_automation(headless: bool = HEADLESS) -> FacebookAutomationFixed:
    """Get or create automation instance"""
    global _auto_instance
    if _auto_instance is None:
        _auto_instance = FacebookAutomationFixed(headless=headless)
    return _auto_instance


def cleanup():
    """Cleanup resources"""
    global _auto_instance
    if _auto_instance:
        _auto_instance.stop_browser()
        _auto_instance = None


if __name__ == '__main__':
    print("=" * 70)
    print("  FACEBOOK AUTOMATION - FIXED VERSION")
    print("  Testing login with improved selector detection")
    print("=" * 70)
    
    auto = get_automation(headless=False)  # Headed for visibility
    
    try:
        # Test login
        print("\n[TEST 1] Login:")
        success = auto.login()
        print(f"  Result: {'SUCCESS' if success else 'FAILED'}\n")
        
        if success:
            # Test health
            print("[TEST 2] Health Check:")
            health = auto.health_check()
            print(f"  Status: {health.get('status')}")
            print(f"  Logged In: {health.get('logged_in')}")
            
            # Test navigation
            print("\n[TEST 3] Navigate to Page:")
            nav_success = auto.navigate_to_page()
            print(f"  Result: {'SUCCESS' if nav_success else 'FAILED'}")
        
        print("\n" + "=" * 70)
        print("  TEST COMPLETE")
        print("=" * 70)
        
    finally:
        cleanup()
