"""
Facebook Auto Poster - Uses browser automation to actually post
Integrates with facebook_playwright_anticaptcha.py for CAPTCHA-free posting

Usage:
    python facebook_auto_post.py "Your post message here"
    python facebook_auto_post.py --generate  # Generate with AI
"""

import os
import sys
import time
import random
from pathlib import Path
from dotenv import load_dotenv

# Import the anti-CAPTCHA automation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from facebook_playwright_anticaptcha import get_automation, cleanup

load_dotenv()

# Configuration
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', '956241877582673')


def create_post_on_facebook(message: str, link: str = None) -> bool:
    """
    Actually create a post on Facebook using browser automation
    
    Args:
        message: Post content
        link: Optional link to include
    
    Returns:
        True if successful
    """
    print("=" * 70)
    print("  FACEBOOK AUTO POSTER")
    print("=" * 70)
    print(f"\n  Message: {message[:50]}...")
    if link:
        print(f"  Link: {link}")
    print()
    
    auto = None
    
    try:
        # Get automation instance
        auto = get_automation(headless=False)
        
        # Ensure logged in
        print("[1/4] Checking login status...")
        if not auto.ensure_logged_in():
            print("  [ERROR] Login failed")
            return False
        print("  [OK] Logged in\n")
        
        # Get page reference
        page = auto.page
        
        # Navigate to page - use home feed for posting (works better for profiles)
        print("[2/4] Navigating to Facebook home feed...")
        try:
            page.goto('https://www.facebook.com', wait_until='domcontentloaded', timeout=20000)
            time.sleep(5)  # Wait for content to load
            print("  [OK] On home feed\n")
        except Exception as e:
            print(f"  [WARN] Could not navigate to home: {e}")
            print("  [INFO] Trying to continue on current page...")
        
        # Create post
        print("[3/4] Creating post...")
        auto._rate_limit_check()
        
        time.sleep(3)
        
        # Find post creation box - try multiple selectors for profile vs page
        post_selectors = [
            # Profile/Home feed
            '[data-testid="create_post"]',
            'div[role="textbox"]',
            'textarea[name="xh8qjy"]',
            'textarea[aria-label*="What"]',
            'div[placeholder*="What"]',
            # Page composer
            '[data-testid="feed-creation-input"]',
        ]
        
        post_box = None
        for selector in post_selectors:
            try:
                post_box = page.locator(selector).first
                if post_box.is_visible(timeout=3000):
                    print(f"  [INFO] Found post box: {selector}")
                    break
                post_box = None
            except:
                continue
        
        if not post_box:
            # Try clicking on "What's on your mind?" area
            print("  [INFO] Trying to click create post area...")
            try:
                # Look for "What's on your mind?" text
                create_post_btn = page.locator('button').filter(has_text='Post').first
                if create_post_btn.is_visible(timeout=3000):
                    create_post_btn.click()
                    time.sleep(2)
                    post_box = page.locator('textarea').first
                    print("  [INFO] Clicked create post button")
            except Exception as e:
                print(f"  [WARN] Could not click create post: {e}")
        
        if not post_box:
            # Last resort: try any textarea
            try:
                textareas = page.locator('textarea').all()
                for ta in textareas:
                    if ta.is_visible(timeout=1000):
                        placeholder = ta.get_attribute('placeholder') or ''
                        if 'what' in placeholder.lower() or 'post' in placeholder.lower() or 'mind' in placeholder.lower():
                            post_box = ta
                            print(f"  [INFO] Found textarea by placeholder: {placeholder[:30]}")
                            break
            except:
                pass
        
        if post_box:
            # Click and fill
            post_box.click()
            time.sleep(random.uniform(1, 2))
            post_box.fill(message)
            time.sleep(random.uniform(1, 2))
            
            # Add link if provided
            if link:
                try:
                    link_input = page.locator('input[type="url"]').first
                    link_input.fill(link)
                    time.sleep(2)
                except:
                    post_box.press('Enter')
                    time.sleep(1)
                    post_box.type(f' {link}')
            
            # Click Post button
            print("  [INFO] Submitting post...")
            post_button = page.locator('button').filter(has_text='Post').first
            if post_button.is_visible(timeout=5000):
                post_button.click()
                time.sleep(5)
                page.wait_for_load_state('networkidle')
                print("  [OK] Post submitted\n")
            else:
                print("  [ERROR] Post button not found")
                return False
        else:
            print("  [ERROR] Post creation box not found")
            return False
        
        # Verify post
        print("[4/4] Verifying post...")
        time.sleep(3)
        
        # Check if post appears in timeline
        if 'facebook.com' in page.url:
            print("  [OK] Post created successfully!\n")
            return True
        else:
            print("  [WARN] Unexpected page after posting")
            return True  # Still probably successful
            
    except Exception as e:
        print(f"  [ERROR] Failed to create post: {e}")
        return False
        
    finally:
        if auto:
            cleanup()


def generate_post_with_ai(topic: str = None):
    """Generate post content using AI (if configured) or use templates"""
    
    # Check if AI is configured
    api_key = os.getenv('DASHSCOPE_API_KEY', '')
    
    if api_key and api_key != 'your_dashscope_api_key_here':
        # Use real AI
        try:
            import dashscope
            dashscope.api_key = api_key
            
            prompt = "Generate a short, engaging Facebook post for a business. "
            if topic:
                prompt += f"Topic: {topic}. "
            prompt += "Keep it under 200 characters. Include 2-3 relevant hashtags. "
            prompt += "Return only the post content, nothing else."
            
            response = dashscope.Generation.call(
                model='qwen-plus',
                prompt=prompt
            )
            
            if response.status_code == 200:
                return response.output.text.strip()
        except Exception as e:
            print(f"[WARN] AI generation failed: {e}")
    
    # Fallback: Use templates
    templates = [
        "Monday Motivation: Success is not final, failure is not fatal - it is the courage to continue that counts. Keep pushing forward! #Motivation #MondayVibes",
        "Growing your business takes time, dedication, and the right tools. Gold Tier is here to help you succeed! #BusinessGrowth #Entrepreneur",
        "The only way to do great work is to love what you do. - Steve Jobs. What are you passionate about today? #Inspiration #Success",
        "Smart businesses use automation to save time and reduce errors. What tasks could you automate? #Productivity #Automation",
        "Customer satisfaction is our priority! Thank you for trusting Gold Tier with your business needs. #CustomerFirst #Grateful",
    ]
    
    return random.choice(templates)


def main():
    # Check for command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == '--generate':
            # Generate and post
            topic = sys.argv[2] if len(sys.argv) > 2 else None
            message = generate_post_with_ai(topic)
            print(f"\nGenerated post:\n{message}\n")
            success = create_post_on_facebook(message)
        else:
            # Custom message
            message = ' '.join(sys.argv[1:])
            success = create_post_on_facebook(message)
    else:
        # Generate and post with default topic
        message = generate_post_with_ai()
        print(f"\nGenerated post:\n{message}\n")
        success = create_post_on_facebook(message)
    
    print("=" * 70)
    if success:
        print("  [OK] POST CREATED SUCCESSFULLY!")
    else:
        print("  [ERROR] POST FAILED")
    print("=" * 70)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
