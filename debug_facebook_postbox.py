"""Debug Facebook post creation box"""
import os
import sys
import time
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from facebook_playwright_anticaptcha import get_automation, cleanup

try:
    auto = get_automation(headless=False)
    auto.ensure_logged_in()
    
    page = auto.page
    print("Navigating to Facebook home...")
    page.goto('https://www.facebook.com', wait_until='domcontentloaded')
    time.sleep(8)
    
    print("\n=== ALL TEXTAREAS ===")
    textareas = page.locator('textarea').all()
    print(f"Found {len(textareas)} textareas:")
    for i, ta in enumerate(textareas[:10]):
        try:
            if ta.is_visible(timeout=1000):
                placeholder = ta.get_attribute('placeholder') or 'N/A'
                aria_label = ta.get_attribute('aria-label') or 'N/A'
                name = ta.get_attribute('name') or 'N/A'
                print(f"  [{i}] placeholder='{placeholder[:50]}', aria-label='{aria_label[:50]}', name='{name}'")
        except Exception as e:
            print(f"  [{i}] Error: {e}")
    
    print("\n=== ALL BUTTONS ===")
    buttons = page.locator('button').all()
    print(f"Found {len(buttons)} buttons:")
    for i, btn in enumerate(buttons[:20]):
        try:
            if btn.is_visible(timeout=1000):
                text = btn.inner_text()[:50] or 'N/A'
                aria_label = btn.get_attribute('aria-label') or 'N/A'
                print(f"  [{i}] text='{text}', aria-label='{aria_label[:50]}'")
        except Exception as e:
            print(f"  [{i}] Error: {e}")
    
    print("\n=== ALL DIVS WITH POST/CREATE ===")
    divs = page.locator('div').all()
    for i, div in enumerate(divs[:100]):
        try:
            if div.is_visible(timeout=500):
                text = div.inner_text()[:100]
                if 'post' in text.lower() or 'create' in text.lower() or 'mind' in text.lower():
                    print(f"  [{i}] '{text[:80]}...'")
        except:
            continue
    
    print("\n=== PAGE INFO ===")
    print(f"URL: {page.url}")
    print(f"Title: {page.title()}")
    
    input("\nPress ENTER to exit...")
    
finally:
    cleanup()
