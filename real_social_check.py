#!/usr/bin/env python3
"""
Facebook & Instagram Real Post Checker
Uses Playwright browser automation - NO API TOKEN NEEDED

Usage:
  python real_social_check.py --facebook    # Check Facebook posts
  python real_social_check.py --instagram   # Check Instagram posts
  python real_social_check.py --both        # Check both
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_facebook():
    """Check Facebook posts using browser automation"""
    print_header("FACEBOOK POST CHECKER")
    
    from playwright.sync_api import sync_playwright
    
    email = os.getenv('FACEBOOK_EMAIL', '')
    password = os.getenv('FACEBOOK_PASSWORD', '')
    page_id = os.getenv('FACEBOOK_PAGE_ID', '')
    
    print(f"Page ID: {page_id}")
    print(f"Email: {email}")
    
    if not email or not password:
        print("\n[ERROR] Facebook credentials not set in .env")
        return []
    
    print("\n[INFO] Starting browser...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Login
            print("[INFO] Logging in to Facebook...")
            page.goto('https://facebook.com/login', wait_until='networkidle')
            
            # Fill credentials
            page.fill('#email', email)
            page.fill('#pass', password)
            page.click('button[type="submit"]')
            
            print("[WAIT] Waiting for login... (check browser)")
            time.sleep(5)
            
            # Navigate to page
            print(f"[INFO] Going to page: {page_id}")
            page.goto(f'https://www.facebook.com/{page_id}', wait_until='networkidle')
            time.sleep(3)
            
            # Get posts
            print("[INFO] Extracting posts...")
            
            posts = []
            post_elements = page.query_selector_all('div[role="article"]')
            
            print(f"Found {len(post_elements)} post elements")
            
            for i, post in enumerate(post_elements[:5], 1):
                try:
                    # Get post text
                    text_elem = post.query_selector('div[dir="auto"]')
                    text = text_elem.inner_text().strip() if text_elem else "(no text)"
                    
                    # Get timestamp
                    time_elem = post.query_selector('abbr')
                    timestamp = time_elem.get_attribute('title') if time_elem else "Unknown"
                    
                    posts.append({
                        'index': i,
                        'text': text[:200],
                        'timestamp': timestamp
                    })
                    
                    print(f"\nPost {i}:")
                    print(f"  Time: {timestamp}")
                    if len(text) > 100:
                        print(f"  Text: {text[:100]}...")
                    else:
                        print(f"  Text: {text}")
                        
                except Exception as e:
                    print(f"  [ERROR] Post {i}: {e}")
            
            # Save to log
            log_file = Path('logs/facebook_real_posts.json')
            log_file.parent.mkdir(exist_ok=True)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'checked_at': datetime.now().isoformat(),
                    'page_id': page_id,
                    'posts': posts
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n[OK] Posts saved to: {log_file}")
            
            browser.close()
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return []
    
    return posts

def check_instagram():
    """Check Instagram posts using browser automation"""
    print_header("INSTAGRAM POST CHECKER")
    
    from playwright.sync_api import sync_playwright
    
    username = os.getenv('INSTAGRAM_USERNAME', '')
    password = os.getenv('INSTAGRAM_PASSWORD', '')
    
    print(f"Username: @{username}")
    
    if not username:
        print("\n[ERROR] Instagram username not set in .env")
        return []
    
    print("\n[INFO] Starting browser...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Go to profile
            print(f"[INFO] Going to profile: @{username}")
            page.goto(f'https://www.instagram.com/{username}/', wait_until='networkidle')
            time.sleep(5)
            
            # Check if logged in
            if page.query_selector('button:has-text("Log in")'):
                if password:
                    print("[INFO] Logging in...")
                    page.goto('https://www.instagram.com/accounts/login/')
                    time.sleep(3)
                    
                    # Fill credentials (selectors may vary)
                    try:
                        page.fill('input[name="username"]', username)
                        page.fill('input[name="password"]', password)
                        page.click('button[type="submit"]')
                        time.sleep(5)
                    except Exception as e:
                        print(f"[WARN] Login failed: {e}")
            
            # Get posts
            print("[INFO] Extracting posts...")
            
            posts = []
            
            # Try to get post count
            stats = page.query_selector_all('ul li span')
            if stats:
                try:
                    post_count = stats[0].inner_text() if len(stats) > 0 else "?"
                    followers = stats[1].inner_text() if len(stats) > 1 else "?"
                    following = stats[2].inner_text() if len(stats) > 2 else "?"
                    
                    print(f"\nProfile Stats:")
                    print(f"  Posts: {post_count}")
                    print(f"  Followers: {followers}")
                    print(f"  Following: {following}")
                except:
                    pass
            
            # Get recent posts (grid view)
            post_elements = page.query_selector_all('div[role="button"]')
            
            print(f"\nFound {len(post_elements)} media items")
            
            for i, post in enumerate(post_elements[:6], 1):
                try:
                    # Get image alt text (if available)
                    img = post.query_selector('img')
                    alt = img.get_attribute('alt') if img else ""
                    
                    if alt:
                        posts.append({
                            'index': i,
                            'description': alt
                        })
                        print(f"\nPost {i}: {alt[:100]}")
                        
                except Exception as e:
                    print(f"  [ERROR] Post {i}: {e}")
            
            # Save to log
            log_file = Path('logs/instagram_real_posts.json')
            log_file.parent.mkdir(exist_ok=True)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'checked_at': datetime.now().isoformat(),
                    'username': username,
                    'posts': posts
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n[OK] Posts saved to: {log_file}")
            
            browser.close()
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return []
    
    return posts

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Real Social Media Checker')
    parser.add_argument('--facebook', action='store_true', help='Check Facebook')
    parser.add_argument('--instagram', action='store_true', help='Check Instagram')
    parser.add_argument('--both', action='store_true', help='Check both')
    args = parser.parse_args()
    
    if args.facebook:
        check_facebook()
    elif args.instagram:
        check_instagram()
    elif args.both:
        check_facebook()
        print("\n" + "="*60)
        check_instagram()
    else:
        # Default: check Facebook
        check_facebook()

if __name__ == '__main__':
    main()
