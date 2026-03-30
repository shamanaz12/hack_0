"""
Facebook 2FA Handler
Handles Two-Factor Authentication for Facebook login

When 2FA is enabled, Facebook requires a 6-digit code from your phone.
This script helps you either:
1. Manually enter the 2FA code when prompted
2. Use backup codes
3. Approve from a trusted device

Usage:
    python facebook_2fa_handler.py
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

try:
    from playwright.sync_api import sync_playwright, Page, Browser
except ImportError:
    print("ERROR: Playwright not installed. Run: pip install playwright && playwright install")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configuration
FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL', '')
FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD', '')
HEADLESS = os.getenv('FACEBOOK_HEADLESS', 'false').lower() == 'true'


class Facebook2FAHandler:
    """Handle Facebook Two-Factor Authentication"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    def start_browser(self):
        """Start browser"""
        print("[INFO] Starting browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--window-size=1920,1080'
            ]
        )
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.context.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
        self.page = self.context.new_page()
        print("[OK] Browser started")
    
    def stop_browser(self):
        """Stop browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("[OK] Browser stopped")
    
    def wait_for_2fa_code(self, timeout_seconds: int = 120) -> Optional[str]:
        """
        Wait for user to input 2FA code
        
        Returns:
            6-digit code or None if timeout
        """
        print("\n" + "=" * 60)
        print("  TWO-FACTOR AUTHENTICATION REQUIRED")
        print("=" * 60)
        print(f"\n  Facebook account '{FACEBOOK_EMAIL}' has 2FA enabled.")
        print("\n  OPTIONS:")
        print("  1. Get 6-digit code from Facebook app on your phone")
        print("  2. Get SMS code on your phone")
        print("  3. Use a backup code")
        print("\n  IMPORTANT:")
        print("  - Keep this window open")
        print("  - Browser will wait for you to complete 2FA manually")
        print("  - Once approved, automation will continue automatically")
        print("\n" + "=" * 60)
        
        # Navigate to Facebook and let user complete 2FA manually
        print("\n[INFO] Opening Facebook login...")
        self.page.goto('https://www.facebook.com/login', wait_until='networkidle')
        
        # Fill credentials
        print("[INFO] Filling credentials...")
        try:
            email_field = self.page.locator('input[name="email"]').first
            password_field = self.page.locator('input[name="pass"]').first
            
            email_field.fill(FACEBOOK_EMAIL)
            time.sleep(1)
            password_field.fill(FACEBOOK_PASSWORD)
            time.sleep(1)
            
            login_button = self.page.locator('button[type="submit"]').first
            login_button.click()
            
            print("[INFO] Login submitted, waiting for 2FA prompt...")
            time.sleep(5)
        except Exception as e:
            print(f"[WARN] Could not auto-fill: {e}")
            print("[INFO] Please complete login manually in the browser")
        
        print("\n[INFO] Waiting for you to complete 2FA...")
        print(f"[INFO] Timeout: {timeout_seconds} seconds")
        
        # Wait for navigation away from 2FA page
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                current_url = self.page.url
                
                # Check if we've moved past 2FA
                if 'two_step_verification' not in current_url.lower() and \
                   'checkpoint' not in current_url.lower() and \
                   'login' not in current_url.lower():
                    print("\n[OK] 2FA completed successfully!")
                    print(f"[INFO] Now on: {current_url}")
                    
                    # Save session
                    self.save_session()
                    return "browser_session"
                
                # Check for 2FA input field
                try:
                    code_input = self.page.locator('input[type="text"]').first
                    if code_input.is_visible(timeout=1000):
                        # 2FA code input is visible, wait for manual entry
                        pass
                except:
                    pass
                
                time.sleep(2)
                
            except Exception as e:
                print(f"[WARN] Error checking status: {e}")
                time.sleep(2)
        
        print("\n[ERROR] Timeout waiting for 2FA completion")
        return None
    
    def save_session(self):
        """Save session cookies"""
        try:
            import json
            cookies = self.context.cookies()
            auth_file = Path('facebook_auth.json')
            
            with open(auth_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'cookies': cookies,
                    'saved_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'email': FACEBOOK_EMAIL,
                    '2fa_completed': True
                }, f, indent=2)
            
            print(f"[OK] Session saved to {auth_file}")
        except Exception as e:
            print(f"[ERROR] Could not save session: {e}")
    
    def handle_2fa_flow(self) -> bool:
        """
        Complete 2FA flow with user assistance
        
        Returns:
            True if successful, False otherwise
        """
        self.start_browser()
        
        try:
            # Wait for user to complete 2FA
            result = self.wait_for_2fa_code(timeout_seconds=120)
            
            if result:
                print("\n" + "=" * 60)
                print("  2FA COMPLETED SUCCESSFULLY!")
                print("=" * 60)
                print("\n[INFO] Session saved.")
                print("[INFO] Future automations will use saved session.")
                print("[INFO] Session valid for 24 hours.")
                return True
            else:
                print("\n[ERROR] 2FA not completed")
                return False
                
        finally:
            self.stop_browser()


def main():
    print("=" * 60)
    print("  FACEBOOK 2FA HANDLER")
    print("=" * 60)
    print(f"\n  Email: {FACEBOOK_EMAIL}")
    print("\n  This script will:")
    print("  1. Open Facebook login")
    print("  2. Fill your credentials")
    print("  3. Wait for you to complete 2FA")
    print("  4. Save the session for future automation")
    print("\n" + "=" * 60)
    print("\n  [INFO] Starting in 3 seconds...")
    print("  [INFO] Have your phone ready for 2FA code!")
    time.sleep(3)
    
    handler = Facebook2FAHandler(headless=False)
    success = handler.handle_2fa_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("  SUCCESS! You can now use Facebook automation.")
    else:
        print("  FAILED. Please try again.")
    print("=" * 60)


if __name__ == '__main__':
    main()
