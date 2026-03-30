"""
Facebook Browser Automation - Anti-CAPTCHA Version
Implements session reuse and persistent browser profile to avoid reCAPTCHA

Key Features:
- Persistent browser profile (user data directory)
- Session validation before login
- Human-like timing and behavior
- Visible browser for login (headless=False for auth)
- Automatic session reuse
- CAPTCHA detection and human handoff

Usage:
    python facebook_playwright_anticaptcha.py
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

# Browser settings - CRITICAL: Use visible browser for login to avoid CAPTCHA
HEADLESS = os.getenv('FACEBOOK_HEADLESS', 'false').lower() == 'true'  # Default visible
SLOW_MO = int(os.getenv('FACEBOOK_SLOW_MO', '50'))

# Paths - CRITICAL: Persistent user data directory
BASE_DIR = Path('facebook_browser_profile')
BASE_DIR.mkdir(exist_ok=True)
USER_DATA_DIR = BASE_DIR / 'Default'  # Chrome uses 'Default' subdirectory
USER_DATA_DIR.mkdir(exist_ok=True)

AUTH_FILE = Path('facebook_auth.json')
SESSION_FILE = BASE_DIR / 'session_info.json'
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'facebook_anticaptcha.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FacebookAutomationAntiCaptcha:
    """
    Facebook Browser Automation - Anti-CAPTCHA Version
    
    Key Strategies:
    1. Persistent browser profile (avoids fresh login)
    2. Session validation before any login attempt
    3. Human-like timing and behavior
    4. Visible browser during authentication
    5. CAPTCHA detection with human handoff
    """

    def __init__(self, headless: bool = False, slow_mo: int = SLOW_MO):
        # Force visible browser for login (critical for avoiding CAPTCHA)
        self.headless = False  # Always visible during auth
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.logged_in = False
        self.last_action_time = datetime.now() - timedelta(minutes=5)
        
        # Session tracking
        self.session_valid_until = None
        self.last_login_attempt = None
        self.consecutive_failures = 0
        
        # Rate limiting - MORE CONSERVATIVE to avoid detection
        self.min_delay = 5  # Increased from 3
        self.max_delay = 10  # Increased from 8
        self.action_count = 0
        self.max_actions_before_break = 5  # Reduced from 10
        self.break_duration = 600  # 10 minutes (increased from 5)
        
        # Selector cache
        self.selector_cache: Dict[str, str] = {}

    def _log(self, message: str, level: str = "INFO"):
        """Unified logging"""
        timestamp = time.strftime('%H:%M:%S')
        if level == "ERROR":
            logger.error(message)
            print(f"  [ERROR] {message}")
        elif level == "SUCCESS":
            logger.info(message)
            print(f"  [OK] {message}")
        elif level == "WARN":
            logger.warning(message)
            print(f"  [WARN] {message}")
        elif level == "CAPTCHA":
            logger.warning(message)
            print(f"  [!CAPTCHA] {message}")
        else:
            logger.info(message)
            print(f"  [INFO] {message}")

    def _random_delay(self, min_sec: float = None, max_sec: float = None):
        """Add random delay with human-like variation"""
        min_sec = min_sec or self.min_delay
        max_sec = max_sec or self.max_delay
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def _rate_limit_check(self):
        """Conservative rate limiting"""
        self.action_count += 1
        
        if self.action_count >= self.max_actions_before_break:
            self._log(f"Rate limit reached. Taking {self.break_duration}s break...", "WARN")
            time.sleep(self.break_duration)
            self.action_count = 0
        
        self._random_delay()

    def _get_browser_args(self) -> Dict:
        """Get browser launch arguments with anti-detection"""
        return {
            'headless': self.headless,
            'slow_mo': self.slow_mo,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920,1080',
                '--disable-notifications',
                '--disable-popup-blocking',
                '--lang=en-US',
            ]
        }

    def _get_context_args(self) -> Dict:
        """Get browser context arguments with realistic fingerprint"""
        return {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'viewport': {'width': 1920, 'height': 1080},
            'locale': 'en-US',
            'timezone_id': 'Asia/Karachi',  # Match user location
            'permissions': ['geolocation'],
            'geolocation': {'latitude': 24.8607, 'longitude': 67.0011},  # Karachi
            'color_scheme': 'light',
        }

    def start_browser(self, use_persistent: bool = True):
        """
        Start browser with persistent profile
        
        Args:
            use_persistent: If True, use persistent user data directory
        """
        self._log("Starting browser...")
        
        if use_persistent:
            self._log(f"Using persistent profile: {USER_DATA_DIR}", "INFO")
            
            # Use persistent context - CRITICAL for avoiding CAPTCHA
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                **self._get_browser_args()
            )
            self.context = self.browser
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        else:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(**self._get_browser_args())
            self.context = self.browser.new_context(**self._get_context_args())
            self.context.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
            self.page = self.context.new_page()
        
        self._log("Browser started successfully", "SUCCESS")

    def stop_browser(self):
        """Close browser gracefully"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self._log("Browser stopped", "SUCCESS")
        except Exception as e:
            self._log(f"Error stopping browser: {e}", "ERROR")

    def save_session_info(self):
        """Save session metadata"""
        try:
            session_info = {
                'email': FACEBOOK_EMAIL,
                'logged_in_at': datetime.now().isoformat(),
                'valid_until': (datetime.now() + timedelta(hours=24)).isoformat(),
                'browser_profile': str(USER_DATA_DIR),
                'consecutive_failures': 0
            }
            
            with open(SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(session_info, f, indent=2)
            
            # Also save cookies
            if self.context:
                cookies = self.context.cookies()
                with open(AUTH_FILE, 'w', encoding='utf-8') as f:
                    json.dump({
                        'cookies': cookies,
                        'saved_at': datetime.now().isoformat(),
                        'email': FACEBOOK_EMAIL
                    }, f, indent=2)
            
            self._log(f"Session saved to {SESSION_FILE}", "SUCCESS")
            return True
        except Exception as e:
            self._log(f"Error saving session: {e}", "ERROR")
            return False

    def load_session_info(self) -> bool:
        """Load session metadata and check validity"""
        if not SESSION_FILE.exists():
            self._log("No saved session info found")
            return False
        
        try:
            with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                session_info = json.load(f)
            
            # Check if session is still valid
            valid_until = datetime.fromisoformat(session_info.get('valid_until', ''))
            if datetime.now() > valid_until:
                self._log("Session expired", "WARN")
                return False
            
            # Check if email matches
            if session_info.get('email') != FACEBOOK_EMAIL:
                self._log("Session email mismatch", "WARN")
                return False
            
            self.session_valid_until = valid_until
            self._log(f"Session valid until: {valid_until}", "SUCCESS")
            return True
            
        except Exception as e:
            self._log(f"Error loading session: {e}", "ERROR")
            return False

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
                    self._log(f"Blocking CAPTCHA detected: {indicator}", "CAPTCHA")
                    return True
            
            # Check URL for blocking paths
            blocking_urls = [
                '/checkpoint/challenge/',
                '/checkpoint/block/',
                '/captcha/',
            ]
            
            for url_pattern in blocking_urls:
                if url_pattern in self.page.url.lower():
                    self._log(f"Blocking CAPTCHA URL: {self.page.url}", "CAPTCHA")
                    return True
            
            # Non-blocking reCAPTCHA may exist in page but not block automation
            # Only report if it's actually blocking
            return False
            
        except Exception as e:
            self._log(f"Error checking for CAPTCHA: {e}", "ERROR")
            return False

    def _wait_for_human_completion(self, timeout_seconds: int = 300) -> bool:
        """
        Wait for human to complete CAPTCHA/login
        
        Args:
            timeout_seconds: Max time to wait (default 5 minutes)
        
        Returns:
            True if completed successfully, False if timeout
        """
        self._log("=" * 60, "CAPTCHA")
        self._log("SECURITY CHECK DETECTED", "CAPTCHA")
        self._log("=" * 60, "CAPTCHA")
        self._log("Please complete the security check manually in the browser.", "CAPTCHA")
        self._log(f"Waiting {timeout_seconds}s for completion...", "CAPTCHA")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                # Check if we've moved past the security page
                if not self._check_for_captcha():
                    # Verify we're on Facebook
                    if 'facebook.com' in self.page.url and 'login' not in self.page.url.lower():
                        self._log("Security check completed!", "SUCCESS")
                        return True
                
                time.sleep(3)
                
            except Exception as e:
                self._log(f"Error checking status: {e}", "WARN")
                time.sleep(3)
        
        self._log("Timeout waiting for security check completion", "ERROR")
        return False

    def _print_page_info(self, step: str):
        """Print current page information"""
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
            except:
                pass
            
            self._log(f"{'='*60}\n")
            
        except Exception as e:
            self._log(f"Error getting page info: {e}", "WARN")

    def _find_email_field(self) -> Tuple[Optional[object], str]:
        """Find email field with robust fallback"""
        self._log("Searching for email/username field...")
        
        # Check cache
        if 'email' in self.selector_cache:
            try:
                locator = self.page.locator(self.selector_cache['email']).first
                if locator.is_visible(timeout=2000):
                    return (locator, self.selector_cache['email'])
            except:
                pass
        
        selector_strategies = [
            ('input[name="email"]', 'Name=email (PRIMARY)'),
            ('#email', 'Standard #email'),
            ('input[type="email"]', 'Email type'),
            ('[aria-label*="email" i]', 'Aria email'),
            ('input[placeholder*="email" i]', 'Placeholder email'),
        ]
        
        for selector, desc in selector_strategies:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=2000):
                    self._log(f"Found email field: {desc}", "SUCCESS")
                    self.selector_cache['email'] = selector
                    return (locator, selector)
            except:
                continue
        
        self._log("Email field NOT FOUND", "ERROR")
        return (None, None)

    def _find_password_field(self) -> Tuple[Optional[object], str]:
        """Find password field"""
        self._log("Searching for password field...")
        
        if 'password' in self.selector_cache:
            try:
                locator = self.page.locator(self.selector_cache['password']).first
                if locator.is_visible(timeout=2000):
                    return (locator, self.selector_cache['password'])
            except:
                pass
        
        selector_strategies = [
            ('input[name="pass"]', 'Name=pass'),
            ('#pass', 'Standard #pass'),
            ('input[type="password"]', 'Password type'),
        ]
        
        for selector, desc in selector_strategies:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=2000):
                    self._log(f"Found password field: {desc}", "SUCCESS")
                    self.selector_cache['password'] = selector
                    return (locator, selector)
            except:
                continue
        
        return (None, None)

    def _find_login_button(self) -> Tuple[Optional[object], str]:
        """Find login button"""
        self._log("Searching for login button...")
        time.sleep(2)  # Wait for render
        
        selector_strategies = [
            ('button:has-text("Log In")', 'Log In text'),
            ('button[type="submit"]', 'Submit button'),
            ('[aria-label*="Log" i]', 'Aria Log'),
        ]
        
        for selector, desc in selector_strategies:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=3000):
                    self._log(f"Found login button: {desc}", "SUCCESS")
                    return (locator, selector)
            except:
                continue
        
        return (None, None)

    def login(self) -> bool:
        """
        Login with anti-CAPTCHA strategy
        
        Strategy:
        1. Use visible browser (not headless)
        2. Human-like delays
        3. Check for CAPTCHA and wait for human
        4. Save session immediately
        """
        if not self.page:
            self.start_browser(use_persistent=True)
        
        self._log("=" * 60)
        self._log("FACEBOOK LOGIN - ANTI-CAPTCHA VERSION")
        self._log("=" * 60)
        
        try:
            # Navigate to login
            self._log("Navigating to Facebook login...")
            self.page.goto('https://www.facebook.com/login', wait_until='networkidle', timeout=30000)
            time.sleep(5)  # Extra wait for full render
            
            self._print_page_info("After Navigation")
            
            # Check for CAPTCHA immediately
            if self._check_for_captcha():
                if not self._wait_for_human_completion(300):
                    return False
            
            # Find fields
            email_field, email_selector = self._find_email_field()
            if not email_field:
                self._log("Cannot proceed without email field", "ERROR")
                return False
            
            password_field, password_selector = self._find_password_field()
            if not password_field:
                return False
            
            login_button, login_selector = self._find_login_button()
            if not login_button:
                return False
            
            # Enter credentials with human-like timing
            self._log("Entering credentials...")
            email_field.fill(FACEBOOK_EMAIL)
            time.sleep(random.uniform(1.5, 2.5))
            password_field.fill(FACEBOOK_PASSWORD)
            time.sleep(random.uniform(1.5, 2.5))
            
            # Click login
            login_button.click()
            self._log("Login submitted, waiting...")
            time.sleep(5)
            
            # Check for CAPTCHA after login attempt
            if self._check_for_captcha():
                if not self._wait_for_human_completion(300):
                    self.consecutive_failures += 1
                    return False
                else:
                    self.consecutive_failures = 0
            
            # Verify login success
            if 'facebook.com' in self.page.url and 'login' not in self.page.url.lower() and 'checkpoint' not in self.page.url.lower():
                self._log("Login SUCCESSFUL!", "SUCCESS")
                self.logged_in = True
                self.save_session_info()
                self.consecutive_failures = 0
                return True
            else:
                self._log("Still on login/checkpoint page", "WARN")
                self._print_page_info("After Login")
                self.consecutive_failures += 1
                return False
                
        except Exception as e:
            self._log(f"Login error: {e}", "ERROR")
            self.consecutive_failures += 1
            return False

    def ensure_logged_in(self) -> bool:
        """
        Ensure logged in with session reuse
        
        Priority:
        1. Check if browser profile already has session
        2. Load cookies if available
        3. Only login if necessary
        """
        # Check if we should skip login due to failures
        if self.consecutive_failures >= 3:
            self._log("Too many consecutive failures. Manual login required.", "ERROR")
            self._log("Please login manually at: https://www.facebook.com/login", "WARN")
            return False
        
        # Start browser with persistent profile
        if not self.page:
            self.start_browser(use_persistent=True)
        
        # Navigate to Facebook to check session
        self._log("Checking existing session...")
        self.page.goto('https://www.facebook.com', wait_until='networkidle', timeout=30000)
        time.sleep(5)
        
        # Check if already logged in
        if 'login' not in self.page.url.lower() and 'checkpoint' not in self.page.url.lower():
            self._log("Already logged in (session reused)", "SUCCESS")
            self._print_page_info("Session Check")
            self.logged_in = True
            return True
        
        # Check for CAPTCHA on the page
        if self._check_for_captcha():
            self._log("Security check on homepage", "CAPTCHA")
            if not self._wait_for_human_completion(300):
                return False
            # Re-check login status
            if 'login' not in self.page.url.lower():
                self._log("Security check passed", "SUCCESS")
                self.logged_in = True
                return True
        
        # Need to login
        self._log("Session expired, logging in...")
        return self.login()

    def navigate_to_page(self) -> bool:
        """Navigate to Facebook page with rate limiting"""
        if not self.logged_in:
            if not self.ensure_logged_in():
                return False
        
        self._log(f"Navigating to page: {FACEBOOK_PAGE_ID}")
        self._rate_limit_check()
        
        try:
            urls_to_try = [
                f'https://www.facebook.com/{FACEBOOK_PAGE_ID}',
                f'https://www.facebook.com/pages/{FACEBOOK_PAGE_ID}',
            ]
            
            for url in urls_to_try:
                try:
                    self.page.goto(url, wait_until='networkidle', timeout=20000)
                    time.sleep(3)
                    
                    if 'error' not in self.page.url.lower():
                        self._log("Successfully navigated to page", "SUCCESS")
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            self._log(f"Error navigating: {e}", "ERROR")
            return False

    def health_check(self) -> Dict:
        """Check automation health"""
        try:
            if not self.page:
                return {'status': 'not_started', 'message': 'Browser not started'}
            
            self.page.goto('https://www.facebook.com', wait_until='networkidle', timeout=15000)
            time.sleep(3)
            
            is_logged_in = 'login' not in self.page.url.lower() and 'checkpoint' not in self.page.url.lower()
            has_captcha = self._check_for_captcha()
            
            return {
                'status': 'healthy' if is_logged_in and not has_captcha else 'needs_attention',
                'logged_in': is_logged_in,
                'has_captcha': has_captcha,
                'consecutive_failures': self.consecutive_failures,
                'url': self.page.url,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


# Global instance
_auto_instance: Optional[FacebookAutomationAntiCaptcha] = None


def get_automation(headless: bool = False) -> FacebookAutomationAntiCaptcha:
    """Get or create automation instance"""
    global _auto_instance
    if _auto_instance is None:
        _auto_instance = FacebookAutomationAntiCaptcha(headless=headless)
    return _auto_instance


def cleanup():
    """Cleanup"""
    global _auto_instance
    if _auto_instance:
        _auto_instance.stop_browser()
        _auto_instance = None


if __name__ == '__main__':
    print("=" * 70)
    print("  FACEBOOK AUTOMATION - ANTI-CAPTCHA VERSION")
    print("  Using persistent browser profile to avoid reCAPTCHA")
    print("=" * 70)
    
    auto = get_automation(headless=False)
    
    try:
        print("\n[TEST] Login with session reuse:")
        success = auto.ensure_logged_in()
        print(f"  Result: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            print("\n[TEST] Health Check:")
            health = auto.health_check()
            print(f"  Status: {health.get('status')}")
            print(f"  Logged In: {health.get('logged_in')}")
            print(f"  Has CAPTCHA: {health.get('has_captcha')}")
        
        print("\n" + "=" * 70)
        print("  TEST COMPLETE")
        print("=" * 70)
        
    finally:
        cleanup()
