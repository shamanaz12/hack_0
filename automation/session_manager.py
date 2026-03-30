"""
Session Manager for Social Media Automation
Handles login, cookie persistence, and session reuse for all platforms.
"""

import json
import os
import time
import random
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SessionManager:
    """Manages browser sessions and authentication for all platforms."""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        
        # Session storage paths
        self.base_path = Path(__file__).parent / "sessions"
        self.base_path.mkdir(exist_ok=True)
        
        # Platform URLs
        self.platform_urls = {
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "whatsapp": "https://web.whatsapp.com",
            "gmail": "https://mail.google.com"
        }
        
        # Credentials from environment
        self.credentials = {
            "facebook": {
                "email": os.getenv("FACEBOOK_EMAIL", ""),
                "password": os.getenv("FACEBOOK_PASSWORD", ""),
                "page_id": os.getenv("FACEBOOK_PAGE_ID", ""),
                "page_url": os.getenv("FACEBOOK_PAGE_URL", "")
            },
            "instagram": {
                "username": os.getenv("INSTAGRAM_USERNAME", ""),
                "password": os.getenv("INSTAGRAM_PASSWORD", "")
            },
            "gmail": {
                "email": os.getenv("GMAIL_EMAIL", ""),
                "password": os.getenv("GMAIL_PASSWORD", "")
            }
        }
        
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup logging for session management."""
        import logging
        log_path = Path(__file__).parent / "logs"
        log_path.mkdir(exist_ok=True)
        
        logger = logging.getLogger("session_manager")
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_path / "session_manager.log")
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
    
    def start_browser(self):
        """Start the Playwright browser."""
        if self.playwright is None:
            self.playwright = sync_playwright().start()
        
        if self.browser is None or not self.browser.is_connected():
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            self.logger.info("Browser launched successfully")
    
    def stop_browser(self):
        """Stop the browser and cleanup."""
        if self.browser:
            self.browser.close()
            self.browser = None
        
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
        
        self.contexts.clear()
        self.pages.clear()
        self.logger.info("Browser stopped")
    
    def get_context(self, platform: str) -> BrowserContext:
        """Get or create a browser context for a platform."""
        if platform not in self.contexts:
            self.contexts[platform] = self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            self.logger.info(f"Created new context for {platform}")
        
        return self.contexts[platform]
    
    def get_page(self, platform: str) -> Page:
        """Get or create a page for a platform."""
        if platform not in self.pages:
            context = self.get_context(platform)
            self.pages[platform] = context.new_page()
            self.logger.info(f"Created new page for {platform}")
        
        return self.pages[platform]
    
    def save_cookies(self, platform: str, context: BrowserContext):
        """Save cookies for a platform."""
        cookie_path = self.base_path / f"{platform}_auth.json"
        cookies = context.cookies()
        
        with open(cookie_path, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        self.logger.info(f"Saved cookies for {platform} to {cookie_path}")
    
    def load_cookies(self, platform: str, context: BrowserContext) -> bool:
        """Load cookies for a platform if they exist."""
        cookie_path = self.base_path / f"{platform}_auth.json"
        
        if cookie_path.exists():
            try:
                with open(cookie_path, 'r') as f:
                    cookies = json.load(f)
                
                context.add_cookies(cookies)
                self.logger.info(f"Loaded cookies for {platform}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to load cookies for {platform}: {e}")
        
        return False
    
    def human_delay(self, min_sec: float = 2.0, max_sec: float = 5.0):
        """Add random human-like delay."""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def is_logged_in(self, platform: str, page: Page) -> bool:
        """Check if logged in to a platform."""
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
            
            if platform == "facebook":
                # Check for Facebook profile icon or menu
                return page.is_visible("img[alt='Profile picture']") or \
                       page.is_visible("[aria-label='Menu']")
            
            elif platform == "instagram":
                # Check for Instagram profile icon
                return page.is_visible("img[alt*='Profile']") or \
                       page.is_visible("[role='button'][aria-label*='Profile']")
            
            elif platform == "whatsapp":
                # Check for chat list (logged in) vs QR code (not logged in)
                return page.is_visible("div[data-testid='default-user']") or \
                       not page.is_visible("[data-testid='qr']")
            
            elif platform == "gmail":
                # Check for Gmail profile icon
                return page.is_visible("img[alt*='Profile']") or \
                       page.is_visible("[data-g-ba='true']")
            
            return False
        
        except Exception as e:
            self.logger.debug(f"Login check for {platform} failed: {e}")
            return False
    
    def login_facebook(self) -> bool:
        """Login to Facebook - Updated with reliable selectors."""
        page = self.get_page("facebook")
        context = self.get_context("facebook")

        # Try to load existing session
        if self.load_cookies("facebook", context):
            page.goto(self.platform_urls["facebook"], wait_until="networkidle")
            self.human_delay(3, 5)

            if self.is_logged_in("facebook", page):
                self.logger.info("Facebook session restored from cookies")
                self.save_cookies("facebook", context)
                return True

        # Fresh login
        self.logger.info("Performing fresh Facebook login")
        page.goto("https://www.facebook.com/login.php", wait_until="networkidle")
        self.human_delay(3, 5)

        try:
            # Handle cookie consent first
            self._handle_cookie_consent(page)
            
            # Wait for login form to be ready
            page.wait_for_selector("#email", timeout=10000)

            # Find and fill login form - Facebook's standard selectors
            email_input = page.locator("#email")
            password_input = page.locator("#pass")

            if email_input.is_visible() and password_input.is_visible():
                self.logger.info("Facebook login form found")
                email_input.fill(self.credentials["facebook"]["email"])
                self.human_delay(1, 2)
                password_input.fill(self.credentials["facebook"]["password"])
                self.human_delay(1, 2)

                # Click login button
                login_btn = page.locator("button[name='login']")
                login_btn.click()
                
                # Wait for navigation after login
                page.wait_for_load_state("networkidle", timeout=30000)
                self.human_delay(4, 6)
                
                # Handle any "save password" or security check dialogs
                self._handle_save_login_dialog(page)

                # Check for login success - multiple indicators
                if self.is_logged_in("facebook", page):
                    self.logger.info("Facebook login successful")
                    self.save_cookies("facebook", context)
                    return True
                else:
                    # Double check - maybe we're already on homepage
                    current_url = page.url
                    if "facebook.com" in current_url and "login" not in current_url.lower():
                        self.logger.info("Facebook login successful (on homepage)")
                        self.save_cookies("facebook", context)
                        return True
                    self.logger.error("Facebook login failed - credentials may be incorrect")
                    return False

            self.logger.error("Facebook login form not found")
            return False

        except Exception as e:
            self.logger.error(f"Facebook login error: {e}")
            return False
    
    def login_instagram(self) -> bool:
        """Login to Instagram - Updated with reliable selectors."""
        page = self.get_page("instagram")
        context = self.get_context("instagram")

        # Try to load existing session
        if self.load_cookies("instagram", context):
            page.goto(self.platform_urls["instagram"], wait_until="networkidle")
            self.human_delay(3, 5)

            if self.is_logged_in("instagram", page):
                self.logger.info("Instagram session restored from cookies")
                self.save_cookies("instagram", context)
                return True

        # Fresh login
        self.logger.info("Performing fresh Instagram login")
        page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
        self.human_delay(4, 6)

        try:
            # Handle cookie consent
            self._handle_cookie_consent(page)
            
            # Wait for login form
            page.wait_for_selector("input[name='username']", timeout=10000)

            # Check if already logged in
            if self.is_logged_in("instagram", page):
                self.save_cookies("instagram", context)
                return True

            # Find and fill login form - Instagram's standard selectors
            username_input = page.locator("input[name='username']")
            password_input = page.locator("input[name='password']")

            if username_input.is_visible() and password_input.is_visible():
                self.logger.info("Instagram login form found")
                username_input.fill(self.credentials["instagram"]["username"])
                self.human_delay(1, 2)
                password_input.fill(self.credentials["instagram"]["password"])
                self.human_delay(1, 2)

                # Click login button
                login_btn = page.locator("button[type='submit']")
                login_btn.click()
                
                # Wait for navigation
                page.wait_for_load_state("networkidle", timeout=30000)
                self.human_delay(4, 6)
                
                # Handle "Save login info" dialog
                self._handle_save_login_dialog(page)
                
                # Handle "Turn on notifications" dialog
                self._handle_notification_dialog(page)

                # Check for login success
                if self.is_logged_in("instagram", page):
                    self.logger.info("Instagram login successful")
                    self.save_cookies("instagram", context)
                    return True
                else:
                    # Double check - maybe we're on homepage
                    current_url = page.url
                    if "instagram.com" in current_url and "login" not in current_url.lower():
                        self.logger.info("Instagram login successful (on homepage)")
                        self.save_cookies("instagram", context)
                        return True
                    self.logger.error("Instagram login failed")
                    return False

            self.logger.error("Instagram login form not found")
            return False

        except Exception as e:
            self.logger.error(f"Instagram login error: {e}")
            return False
    
    def login_whatsapp(self) -> bool:
        """Login to WhatsApp Web (QR code scan required for first time)."""
        page = self.get_page("whatsapp")
        context = self.get_context("whatsapp")
        
        # Try to load existing session
        if self.load_cookies("whatsapp", context):
            page.goto(self.platform_urls["whatsapp"], wait_until="networkidle")
            self.human_delay(5, 8)
            
            if self.is_logged_in("whatsapp", page):
                self.logger.info("WhatsApp session restored from cookies")
                self.save_cookies("whatsapp", context)
                return True
        
        # Fresh login - QR code scan required
        self.logger.info("WhatsApp login - QR code scan required")
        page.goto(self.platform_urls["whatsapp"], wait_until="networkidle")
        self.human_delay(3, 5)
        
        try:
            # Wait for QR code or chat list
            self.logger.info("Please scan QR code with WhatsApp mobile app...")
            
            # Wait up to 60 seconds for QR scan
            for _ in range(12):  # 12 * 5 = 60 seconds
                self.human_delay(4, 6)
                
                if self.is_logged_in("whatsapp", page):
                    self.logger.info("WhatsApp login successful")
                    self.save_cookies("whatsapp", context)
                    return True
            
            self.logger.warning("WhatsApp login timeout - QR code not scanned")
            return False
        
        except Exception as e:
            self.logger.error(f"WhatsApp login error: {e}")
            return False
    
    def login_gmail(self) -> bool:
        """Login to Gmail."""
        page = self.get_page("gmail")
        context = self.get_context("gmail")
        
        # Try to load existing session
        if self.load_cookies("gmail", context):
            page.goto(self.platform_urls["gmail"], wait_until="networkidle")
            self.human_delay(2, 4)
            
            if self.is_logged_in("gmail", page):
                self.logger.info("Gmail session restored from cookies")
                self.save_cookies("gmail", context)
                return True
        
        # Fresh login
        self.logger.info("Performing fresh Gmail login")
        page.goto(self.platform_urls["gmail"], wait_until="networkidle")
        self.human_delay(3, 5)
        
        try:
            # Handle cookie consent
            self._handle_cookie_consent(page)
            
            # Check if already logged in
            if self.is_logged_in("gmail", page):
                self.save_cookies("gmail", context)
                return True
            
            # Find email input
            email_input = page.locator("input[type='email']")
            
            if email_input.is_visible():
                email_input.fill(self.credentials["gmail"]["email"])
                self.human_delay(1, 2)
                
                # Click Next
                next_btn = page.locator("button[type='button']:has-text('Next')")
                if next_btn.is_visible():
                    next_btn.click()
                    page.wait_for_load_state("networkidle")
                    self.human_delay(2, 4)
                    
                    # Enter password if prompted
                    password_input = page.locator("input[type='password']")
                    if password_input.is_visible():
                        password_input.fill(self.credentials["gmail"]["password"])
                        self.human_delay(1, 2)
                        
                        # Click Next
                        next_btn.click()
                        page.wait_for_load_state("networkidle")
                        self.human_delay(3, 5)
                        
                        # Handle security check if needed
                        self._handle_security_check(page)
                        
                        if self.is_logged_in("gmail", page):
                            self.logger.info("Gmail login successful")
                            self.save_cookies("gmail", context)
                            return True
            
            self.logger.error("Gmail login form not found")
            return False
        
        except Exception as e:
            self.logger.error(f"Gmail login error: {e}")
            return False
    
    def _handle_cookie_consent(self, page: Page):
        """Handle cookie consent dialogs."""
        try:
            # Facebook cookie consent
            cookie_btn = page.locator("button:has-text('Allow'), button:has-text('Accept')")
            if cookie_btn.is_visible(timeout=3000):
                cookie_btn.click()
                page.wait_for_load_state("networkidle")
                self.human_delay(1, 2)
        except:
            pass
    
    def _handle_save_login_dialog(self, page: Page):
        """Handle Instagram save login dialog."""
        try:
            save_btn = page.locator("button:has-text('Save'), button:has-text('Not Now')")
            if save_btn.is_visible(timeout=3000):
                save_btn.click()
                self.human_delay(1, 2)
        except:
            pass
    
    def _handle_notification_dialog(self, page: Page):
        """Handle notification permission dialog."""
        try:
            allow_btn = page.locator("button:has-text('Allow'), button:has-text('Not Now')")
            if allow_btn.is_visible(timeout=3000):
                allow_btn.click()
                self.human_delay(1, 2)
        except:
            pass
    
    def _handle_security_check(self, page: Page):
        """Handle Google security check if needed."""
        try:
            # Look for security verification
            verify_btn = page.locator("button:has-text('Verify'), button:has-text('Got it')")
            if verify_btn.is_visible(timeout=3000):
                verify_btn.click()
                page.wait_for_load_state("networkidle")
                self.human_delay(2, 4)
        except:
            pass
    
    def navigate_to_facebook_page(self) -> bool:
        """Navigate to the business page (not personal profile)."""
        page = self.get_page("facebook")
        page_url = self.credentials["facebook"].get("page_url", "")
        
        if not page_url:
            page_id = self.credentials["facebook"].get("page_id", "")
            page_url = f"https://www.facebook.com/profile.php?id={page_id}"
        
        try:
            page.goto(page_url, wait_until="networkidle")
            self.human_delay(2, 4)
            self.logger.info(f"Navigated to Facebook page: {page_url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to Facebook page: {e}")
            return False
    
    def close(self):
        """Cleanup all resources."""
        self.stop_browser()


# Singleton instance
_session_manager: Optional[SessionManager] = None


def get_session_manager(headless: bool = False) -> SessionManager:
    """Get or create the session manager singleton."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(headless=headless)
    return _session_manager
