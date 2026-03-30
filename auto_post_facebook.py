"""
Facebook Auto Post - Direct Browser Automation
Posts directly to Facebook using persistent browser session

Usage:
    python auto_post_facebook.py "Your post message here"
"""

import os
import sys
import time
import random
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from facebook_playwright_anticaptcha import get_automation, cleanup

load_dotenv()

def post_to_facebook(message: str) -> bool:
    """Post to Facebook using browser automation"""
    
    print("=" * 70)
    print("  FACEBOOK AUTO POST - DIRECT")
    print("=" * 70)
    print(f"\n  Post: {message[:60]}...\n")
    
    auto = None
    
    try:
        # Get automation
        auto = get_automation(headless=False)
        
        # Login
        print("[1/5] Checking login...")
        if not auto.ensure_logged_in():
            print("  [ERROR] Login failed")
            return False
        print("  [OK] Logged in\n")
        
        page = auto.page
        
        # Go to Facebook home
        print("[2/5] Going to Facebook home...")
        page.goto('https://www.facebook.com/home.php', wait_until='domcontentloaded', timeout=30000)
        time.sleep(8)  # Wait for page to fully load
        print("  [OK] On home page\n")
        
        # Find and click "What's on your mind?" box
        print("[3/5] Finding post creation box...")
        
        # Try multiple approaches
        post_box = None
        
        # Approach 1: Click on "What's on your mind?" text area
        try:
            print("  Trying: 'What's on your mind?' selector...")
            whatsonmind = page.locator('span:has-text("What\'s on your mind?")').first
            if whatsonmind.is_visible(timeout=5000):
                whatsonmind.click()
                time.sleep(3)
                post_box = page.locator('textarea[aria-label*="What\'s on your mind"]').first
                print("  [OK] Found via 'What's on your mind?'")
        except Exception as e:
            print(f"  [WARN] Approach 1 failed: {e}")
        
        # Approach 2: Find textarea by placeholder
        if not post_box:
            try:
                print("  Trying: textarea with placeholder...")
                textareas = page.locator('textarea').all()
                for ta in textareas:
                    try:
                        if ta.is_visible(timeout=2000):
                            placeholder = ta.get_attribute('placeholder') or ''
                            if 'mind' in placeholder.lower() or 'post' in placeholder.lower():
                                post_box = ta
                                post_box.click()
                                time.sleep(2)
                                print(f"  [OK] Found via placeholder: {placeholder[:40]}")
                                break
                    except:
                        continue
            except Exception as e:
                print(f"  [WARN] Approach 2 failed: {e}")
        
        # Approach 3: Click any create post button
        if not post_box:
            try:
                print("  Trying: create post buttons...")
                buttons = page.locator('button[role="button"]').all()
                for btn in buttons:
                    try:
                        if btn.is_visible(timeout=2000):
                            text = btn.inner_text()
                            if 'post' in text.lower() or 'create' in text.lower():
                                btn.click()
                                time.sleep(3)
                                post_box = page.locator('textarea').first
                                if post_box.is_visible(timeout=2000):
                                    print(f"  [OK] Found via button: {text[:40]}")
                                    break
                    except:
                        continue
            except Exception as e:
                print(f"  [WARN] Approach 3 failed: {e}")
        
        # Approach 4: Just find first visible textarea
        if not post_box:
            try:
                print("  Trying: first visible textarea...")
                textareas = page.locator('textarea')
                count = textareas.count()
                print(f"  Found {count} textareas")
                for i in range(min(count, 10)):
                    ta = textareas.nth(i)
                    try:
                        if ta.is_visible(timeout=1000):
                            ta.click()
                            time.sleep(2)
                            post_box = ta
                            print(f"  [OK] Using textarea #{i}")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"  [WARN] Approach 4 failed: {e}")
        
        if not post_box:
            print("  [ERROR] Could not find post creation box")
            print("  [INFO] Facebook may have changed their UI")
            return False
        
        # Fill the post
        print("\n[4/5] Writing post...")
        post_box.fill(message)
        time.sleep(random.uniform(3, 5))
        print("  [OK] Post content filled\n")
        
        # Click Post button
        print("[5/5] Publishing post...")
        
        # Find Post button
        post_btn = None
        try:
            post_btn = page.locator('button:has-text("Post")').first
            if not post_btn.is_visible(timeout=5000):
                post_btn = page.locator('div[role="button"]:has-text("Post")').first
        except:
            pass
        
        if post_btn and post_btn.is_visible(timeout=3000):
            post_btn.click()
            print("  [OK] Post button clicked")
            time.sleep(5)
            
            # Wait for post to publish
            page.wait_for_load_state('networkidle')
            time.sleep(3)
            
            print("  [OK] Post published!\n")
            return True
        else:
            print("  [ERROR] Post button not found")
            return False
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False
    
    finally:
        if auto:
            cleanup()


def main():
    # Get message
    if len(sys.argv) > 1:
        message = ' '.join(sys.argv[1:])
    else:
        # Default message
        messages = [
            "Growing your business takes time, dedication, and the right tools. Gold Tier is here to help you succeed! #BusinessGrowth #Entrepreneur",
            "Thank you for trusting Gold Tier with your business needs. We're committed to your success! #GoldTier #Business",
            "New day, new opportunities! Keep pushing forward. #Motivation #MondayVibes",
        ]
        message = random.choice(messages)
    
    # Post
    success = post_to_facebook(message)
    
    print("=" * 70)
    if success:
        print("  [OK] POST PUBLISHED SUCCESSFULLY!")
    else:
        print("  [ERROR] POST FAILED")
        print("\n  You can post manually:")
        print(f"  1. Go to facebook.com")
        print(f"  2. Copy: {message[:50]}...")
        print(f"  3. Paste and post")
    print("=" * 70)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
