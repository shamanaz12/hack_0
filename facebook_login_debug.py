"""
Facebook Login Debug Script
Diagnoses and fixes the #email selector timeout issue

This script will:
1. Debug page load flow
2. Detect current page state
3. Print all available input fields
4. Identify the correct selector strategy
5. Handle edge cases (cookie consent, account picker, checkpoint)

Usage:
    python facebook_login_debug.py
"""

import os
import sys
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple

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
DEBUG_LOG = Path('logs/facebook_login_debug.log')
DEBUG_LOG.parent.mkdir(exist_ok=True)


class FacebookLoginDebugger:
    """
    Facebook Login Debugger - Diagnoses login page issues
    """

    def __init__(self, headless: bool = HEADLESS, slow_mo: int = SLOW_MO):
        self.headless = headless
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.debug_info: Dict = {}

    def log(self, message: str, level: str = "INFO"):
        """Log to console and file"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"{timestamp} - {level} - {message}"
        if level == "ERROR":
            print(f"[ERROR] {message}")
        elif level == "SUCCESS":
            print(f"[OK] {message}")
        elif level == "WARN":
            print(f"[WARN] {message}")
        else:
            print(f"[INFO] {message}")
        try:
            with open(DEBUG_LOG, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
        except:
            pass

    def start_browser(self):
        """Initialize browser with anti-detection"""
        self.log("Starting browser...")
        
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
        
        self.log("Browser started successfully")

    def stop_browser(self):
        """Close browser"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.log("Browser stopped")
        except Exception as e:
            self.log(f"Error stopping browser: {e}", "ERROR")

    def capture_page_state(self, step: str) -> Dict:
        """Capture current page state for debugging"""
        state = {
            'step': step,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'url': self.page.url if self.page else 'N/A',
            'title': self.page.title() if self.page else 'N/A',
            'inputs': [],
            'buttons': [],
            'potential_blocks': [],
            'html_snippet': ''
        }
        
        try:
            # Get all input fields
            inputs = self.page.locator('input').all()
            for i, inp in enumerate(inputs[:20]):  # Limit to first 20
                try:
                    if inp.is_visible(timeout=2000):
                        input_info = {
                            'index': i,
                            'type': inp.get_attribute('type'),
                            'id': inp.get_attribute('id'),
                            'name': inp.get_attribute('name'),
                            'placeholder': inp.get_attribute('placeholder'),
                            'aria_label': inp.get_attribute('aria-label'),
                        }
                        state['inputs'].append(input_info)
                except:
                    continue
            
            # Get all buttons
            buttons = self.page.locator('button').all()
            for i, btn in enumerate(buttons[:20]):
                try:
                    if btn.is_visible(timeout=2000):
                        btn_info = {
                            'index': i,
                            'type': btn.get_attribute('type'),
                            'text': btn.inner_text()[:50],
                            'aria_label': btn.get_attribute('aria-label'),
                        }
                        state['buttons'].append(btn_info)
                except:
                    continue
            
            # Check for block indicators
            page_content = self.page.content()
            block_indicators = [
                'suspicious login',
                'unusual activity',
                'confirm your identity',
                'security check',
                'captcha',
                'temporarily blocked',
                'cookie',
                'consent',
                'saved account',
                'choose account'
            ]
            for indicator in block_indicators:
                if indicator.lower() in page_content.lower():
                    state['potential_blocks'].append(indicator)
            
            # Get HTML snippet for debugging
            try:
                body = self.page.locator('body').first
                state['html_snippet'] = body.inner_html()[:2000]
            except:
                state['html_snippet'] = 'Could not retrieve HTML'
                
        except Exception as e:
            self.log(f"Error capturing page state: {e}", "ERROR")
        
        return state

    def print_debug_state(self, state: Dict):
        """Print debug information in readable format"""
        print("\n" + "=" * 70)
        print(f"  PAGE STATE DEBUG - {state['step']}")
        print("=" * 70)
        print(f"  URL:   {state['url']}")
        print(f"  Title: {state['title']}")
        print("-" * 70)
        
        print("\n  INPUT FIELDS FOUND:")
        if state['inputs']:
            for inp in state['inputs']:
                print(f"    [{inp['index']}] type={inp['type']}, id={inp['id']}, name={inp['name']}")
                if inp['placeholder']:
                    print(f"         placeholder: '{inp['placeholder']}'")
                if inp['aria_label']:
                    print(f"         aria-label: '{inp['aria_label']}'")
        else:
            print("    (No visible input fields found)")
        
        print("\n  BUTTONS FOUND:")
        if state['buttons']:
            for btn in state['buttons']:
                print(f"    [{btn['index']}] type={btn['type']}, text='{btn['text']}'")
        else:
            print("    (No visible buttons found)")
        
        if state['potential_blocks']:
            print("\n  ⚠️  POTENTIAL BLOCKS DETECTED:")
            for block in state['potential_blocks']:
                print(f"    - {block}")
        
        print("=" * 70 + "\n")

    def handle_cookie_consent(self) -> bool:
        """Handle cookie consent popup if present"""
        self.log("Checking for cookie consent...")
        
        cookie_selectors = [
            '[aria-label="Cookie Policy"]',
            '[data-cookiebanner]',
            'button:has-text("Accept All")',
            'button:has-text("Accept")',
            'button:has-text("Allow")',
            'button:has-text("Essential cookies")',
        ]
        
        for selector in cookie_selectors:
            try:
                cookie_btn = self.page.locator(selector).first
                if cookie_btn.is_visible(timeout=3000):
                    self.log(f"Cookie consent found, clicking: {selector}")
                    cookie_btn.click()
                    time.sleep(2)
                    return True
            except:
                continue
        
        self.log("No cookie consent popup detected")
        return False

    def handle_saved_account(self) -> bool:
        """Handle saved account screen if present"""
        self.log("Checking for saved account screen...")
        
        # Check if we're on account picker
        if 'checkpoint' in self.page.url.lower() or 'save-device' in self.page.url.lower():
            self.log("Saved account/checkpoint screen detected")
            
            # Try to click on the saved account
            try:
                saved_account = self.page.locator('[role="button"]').first
                if saved_account.is_visible(timeout=3000):
                    self.log("Clicking on saved account...")
                    saved_account.click()
                    time.sleep(2)
                    return True
            except Exception as e:
                self.log(f"Could not click saved account: {e}", "WARN")
        
        return False

    def handle_checkpoint(self) -> bool:
        """Handle security checkpoint if present"""
        self.log("Checking for security checkpoint...")
        
        if 'checkpoint' in self.page.url.lower():
            self.log("⚠️  SECURITY CHECKPOINT DETECTED", "WARN")
            self.log("Manual intervention may be required", "WARN")
            
            # Try to continue
            continue_selectors = [
                'button:has-text("Continue")',
                'button:has-text("Next")',
                '[type="submit"]'
            ]
            
            for selector in continue_selectors:
                try:
                    btn = self.page.locator(selector).first
                    if btn.is_visible(timeout=3000):
                        self.log(f"Clicking continue button: {selector}")
                        btn.click()
                        time.sleep(3)
                        return True
                except:
                    continue
        
        return False

    def find_email_field(self) -> Tuple[Optional[object], str]:
        """
        Find email/username field with multiple selector strategies
        Returns: (locator, selector_used)
        """
        self.log("Searching for email/username field...")
        
        # Priority-ordered selector strategies
        selector_strategies = [
            # Standard Facebook selectors
            ('#email', 'Standard #email'),
            ('input[type="email"]', 'Email type input'),
            ('input[name="email"]', 'Email name input'),
            ('input[name="login"]', 'Login name input'),
            ('#ident', 'Alternative #ident'),
            
            # Aria-based selectors
            ('[aria-label*="email" i]', 'Aria label with email'),
            ('[aria-label*="phone" i]', 'Aria label with phone'),
            ('[aria-label*="username" i]', 'Aria label with username'),
            
            # Placeholder-based
            ('input[placeholder*="email" i]', 'Placeholder with email'),
            ('input[placeholder*="phone" i]', 'Placeholder with phone'),
            
            # Generic text inputs (fallback)
            ('input[type="text"]', 'Text input (generic)'),
            
            # Facebook mobile selectors
            ('#m_login_email', 'Mobile email selector'),
        ]
        
        for selector, description in selector_strategies:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=3000):
                    self.log(f"✓ Found email field using: {description} ({selector})")
                    return (locator, selector)
            except:
                continue
        
        self.log("✗ Email field NOT FOUND with any selector strategy", "ERROR")
        return (None, None)

    def find_password_field(self) -> Tuple[Optional[object], str]:
        """Find password field with multiple strategies"""
        self.log("Searching for password field...")
        
        selector_strategies = [
            ('#pass', 'Standard #pass'),
            ('input[type="password"]', 'Password type input'),
            ('input[name="pass"]', 'Password name input'),
            ('[aria-label*="password" i]', 'Aria label with password'),
            ('input[placeholder*="password" i]', 'Placeholder with password'),
        ]
        
        for selector, description in selector_strategies:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=3000):
                    self.log(f"✓ Found password field using: {description} ({selector})")
                    return (locator, selector)
            except:
                continue
        
        self.log("✗ Password field NOT FOUND", "ERROR")
        return (None, None)

    def find_login_button(self) -> Tuple[Optional[object], str]:
        """Find login button"""
        self.log("Searching for login button...")
        
        selector_strategies = [
            ('button[type="submit"]', 'Submit button'),
            ('input[type="submit"]', 'Submit input'),
            ('button:has-text("Log In")', 'Log In text button'),
            ('button:has-text("Log in")', 'Log in text button'),
            ('button:has-text("Login")', 'Login text button'),
            ('[value*="Log" i]', 'Value with Log'),
            ('#loginbutton', 'Login button ID'),
        ]
        
        for selector, description in selector_strategies:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=3000):
                    self.log(f"✓ Found login button using: {description} ({selector})")
                    return (locator, selector)
            except:
                continue
        
        self.log("✗ Login button NOT FOUND", "ERROR")
        return (None, None)

    def debug_login_flow(self):
        """Main debug flow"""
        self.log("=" * 60)
        self.log("FACEBOOK LOGIN DEBUG SESSION STARTED")
        self.log("=" * 60)
        
        self.start_browser()
        
        try:
            # Step 1: Navigate to Facebook login
            self.log("\n[STEP 1] Navigating to Facebook login page...")
            self.page.goto('https://www.facebook.com/login', wait_until='networkidle', timeout=30000)
            time.sleep(3)  # Wait for page to fully render
            
            # Capture initial state
            state1 = self.capture_page_state("After Navigation")
            self.print_debug_state(state1)
            
            # Step 2: Handle cookie consent
            self.log("\n[STEP 2] Checking for cookie consent...")
            if self.handle_cookie_consent():
                time.sleep(2)
                state_cookie = self.capture_page_state("After Cookie Consent")
                self.print_debug_state(state_cookie)
            
            # Step 3: Handle saved account
            self.log("\n[STEP 3] Checking for saved account...")
            if self.handle_saved_account():
                time.sleep(2)
                state_saved = self.capture_page_state("After Saved Account")
                self.print_debug_state(state_saved)
            
            # Step 4: Handle checkpoint
            self.log("\n[STEP 4] Checking for checkpoint...")
            if self.handle_checkpoint():
                time.sleep(2)
                state_checkpoint = self.capture_page_state("After Checkpoint")
                self.print_debug_state(state_checkpoint)
            
            # Step 5: Find email field
            self.log("\n[STEP 5] Locating email field...")
            email_field, email_selector = self.find_email_field()
            
            if email_field is None:
                self.log("\n" + "!" * 70)
                self.log("  CRITICAL: Email field not found!")
                self.log("  This is the ROOT CAUSE of your error.")
                self.log("!" * 70)
                
                # Capture final state for analysis
                final_state = self.capture_page_state("Final - Email Not Found")
                self.print_debug_state(final_state)
                
                # Save debug info
                self.save_debug_report(final_state)
                return False
            
            # Step 6: Find password field
            self.log("\n[STEP 6] Locating password field...")
            password_field, password_selector = self.find_password_field()
            
            if password_field is None:
                self.log("CRITICAL: Password field not found!", "ERROR")
                return False
            
            # Step 7: Find login button
            self.log("\n[STEP 7] Locating login button...")
            login_button, login_selector = self.find_login_button()
            
            if login_button is None:
                self.log("CRITICAL: Login button not found!", "ERROR")
                return False
            
            # Step 8: Attempt login
            self.log("\n[STEP 8] Attempting login...")
            self.log(f"  Email: {FACEBOOK_EMAIL[:3]}... (masked)")
            self.log(f"  Password: {'*' * len(FACEBOOK_PASSWORD)}")
            
            try:
                email_field.fill(FACEBOOK_EMAIL)
                time.sleep(1)
                password_field.fill(FACEBOOK_PASSWORD)
                time.sleep(1)
                login_button.click()
                
                self.log("Login credentials submitted, waiting for response...")
                time.sleep(5)
                
                # Check result
                if 'facebook.com' in self.page.url and 'login' not in self.page.url.lower():
                    self.log("✓ LOGIN SUCCESSFUL!", "SUCCESS")
                else:
                    self.log("⚠️  Still on login page - credentials may be incorrect", "WARN")
                
            except Exception as e:
                self.log(f"Error during login attempt: {e}", "ERROR")
            
            # Final state capture
            final_state = self.capture_page_state("After Login Attempt")
            self.print_debug_state(final_state)
            
            # Save debug report
            self.save_debug_report({
                'email_selector': email_selector,
                'password_selector': password_selector,
                'login_selector': login_selector,
                'final_state': final_state
            })
            
            return True
            
        except Exception as e:
            self.log(f"Debug session error: {e}", "ERROR")
            return False
        
        finally:
            self.stop_browser()
            self.log("Debug session complete")

    def save_debug_report(self, data: Dict):
        """Save debug report to file"""
        report_file = Path('logs/facebook_login_debug_report.json')
        report_file.parent.mkdir(exist_ok=True)
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'credentials_used': {
                'email_prefix': FACEBOOK_EMAIL[:3] + '...' if FACEBOOK_EMAIL else 'N/A',
                'password_length': len(FACEBOOK_PASSWORD) if FACEBOOK_PASSWORD else 0
            },
            'browser_config': {
                'headless': self.headless,
                'slow_mo': self.slow_mo
            },
            'debug_data': data
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"Debug report saved to: {report_file}")


def main():
    print("=" * 70)
    print("  FACEBOOK LOGIN DEBUGGER")
    print("  Diagnosing: Page.fill: Timeout 30000ms exceeded waiting for #email")
    print("=" * 70)
    print()
    
    debugger = FacebookLoginDebugger(headless=False)  # Run headed for visibility
    success = debugger.debug_login_flow()
    
    print("\n" + "=" * 70)
    if success:
        print("  DEBUG COMPLETE - Check logs/facebook_login_debug_report.json")
    else:
        print("  DEBUG FAILED - Review error messages above")
    print("=" * 70)
    
    print("\n  NEXT STEPS:")
    print("  1. Review the debug output above")
    print("  2. Check logs/facebook_login_debug_report.json for details")
    print("  3. Update selectors in facebook_playwright_auto.py based on findings")
    print("=" * 70)


if __name__ == '__main__':
    main()
