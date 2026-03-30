"""
Facebook Business Page Auto-Post
Direct page access - Auto post, get posts, delete posts
No login issues - uses saved session
"""

import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from session_manager import SessionManager


class FacebookPageAuto:
    """Direct Facebook Business Page automation."""
    
    def __init__(self, headless=False):
        self.session = SessionManager(headless=headless)
        self.page_url = "https://www.facebook.com/profile.php?id=61578538607212"
        self.page = None
        self.logger = self.session.logger
    
    def start(self):
        """Start browser and load session."""
        self.session.start_browser()
        self.page = self.session.get_page("facebook")
    
    def go_to_page(self):
        """Direct redirect to business page."""
        print("\n[INFO] Navigating to your business page...")
        self.page.goto(self.page_url, wait_until="networkidle")
        time.sleep(3)
        print("[OK] Business page loaded!")
    
    def auto_post(self, text):
        """Auto post to business page."""
        print("\n" + "=" * 50)
        print("  AUTO POSTING TO FACEBOOK PAGE")
        print("=" * 50)
        print(f"\nPost content:\n{text}\n")
        
        try:
            # Go to page
            self.go_to_page()
            
            # Find create post button
            print("[INFO] Finding post creation box...")
            
            # Click on "What's on your mind?" area
            create_btns = [
                "div[role='button'][aria-label*='Create post']",
                "div.x1y1aw1k",
                "span:has-text('What')",
            ]
            
            clicked = False
            for selector in create_btns:
                try:
                    btn = self.page.locator(selector).first
                    if btn.is_visible(timeout=5000):
                        btn.click()
                        clicked = True
                        print(f"[OK] Clicked create post button")
                        time.sleep(2)
                        break
                except:
                    continue
            
            if not clicked:
                print("[ERROR] Could not find create post button")
                return False
            
            # Wait for dialog
            self.page.wait_for_selector("div[role='dialog']", timeout=10000)
            time.sleep(2)
            
            # Find textbox and type
            print("[INFO] Typing post content...")
            textbox = self.page.locator("div[role='textbox'][data-testid='post-creation-textbox']").first
            
            if not textbox.is_visible(timeout=5000):
                textbox = self.page.locator("div[contenteditable='true']").first
            
            textbox.click()
            time.sleep(1)
            textbox.fill(text)
            time.sleep(2)
            
            # Click Post button
            print("[INFO] Publishing post...")
            post_btn = self.page.locator("button[aria-label*='Post'], div[role='button']:has-text('Post')").first
            
            if post_btn.is_visible(timeout=5000):
                post_btn.click()
                self.page.wait_for_load_state("networkidle")
                time.sleep(3)
                print("[OK] POST PUBLISHED SUCCESSFULLY!")
                return True
            else:
                print("[ERROR] Post button not found")
                return False
        
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    def get_posts(self, count=5):
        """Get recent posts from page."""
        print("\n" + "=" * 50)
        print(f"  GETTING RECENT POSTS (Last {count})")
        print("=" * 50)
        
        posts = []
        
        try:
            self.go_to_page()
            time.sleep(3)
            
            # Scroll to load posts
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            
            # Find posts
            post_elements = self.page.locator("div[role='article'], div.x1y1aw1k").all()
            print(f"[INFO] Found {len(post_elements)} post elements")
            
            for i, post in enumerate(post_elements[:count]):
                try:
                    if not post.is_visible():
                        continue
                    
                    text = ""
                    try:
                        text_elem = post.locator("div[dir='auto'], span[dir='auto']").first
                        if text_elem.is_visible():
                            text = text_elem.inner_text()[:200]
                    except:
                        pass
                    
                    if text:
                        posts.append({"id": i+1, "text": text})
                        print(f"\n[POST #{i+1}]\n{text[:100]}...\n")
                except:
                    continue
            
            print(f"[OK] Retrieved {len(posts)} posts")
            return posts
        
        except Exception as e:
            print(f"[ERROR] {e}")
            return posts
    
    def delete_post(self, post_num=1):
        """Delete a post by number."""
        print("\n" + "=" * 50)
        print(f"  DELETING POST #{post_num}")
        print("=" * 50)
        
        try:
            self.go_to_page()
            time.sleep(3)
            
            # Find posts
            post_elements = self.page.locator("div[role='article']").all()
            
            if post_num > len(post_elements):
                print(f"[ERROR] Post #{post_num} not found")
                return False
            
            post = post_elements[post_num - 1]
            
            # Find options button (three dots)
            options_btn = post.locator("div[role='button'][aria-label*='More'], div[role='button'][aria-label*='Options']").first
            
            if options_btn.is_visible(timeout=5000):
                options_btn.click()
                time.sleep(2)
                
                # Find delete option
                delete_btn = self.page.locator("div[role='menuitem']:has-text('Delete'), div[role='menuitem']:has-text('trash')").first
                
                if delete_btn.is_visible(timeout=5000):
                    delete_btn.click()
                    time.sleep(2)
                    
                    # Confirm
                    confirm_btn = self.page.locator("button:has-text('Move to trash'), button:has-text('Delete')").first
                    if confirm_btn.is_visible(timeout=5000):
                        confirm_btn.click()
                        time.sleep(2)
                        print("[OK] Post deleted successfully!")
                        return True
            
            print("[ERROR] Could not delete post")
            return False
        
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    def show_status(self):
        """Show page status."""
        print("\n" + "=" * 50)
        print("  FACEBOOK PAGE STATUS")
        print("=" * 50)
        print(f"\nPage URL: {self.page_url}")
        print(f"Page ID: 61578538607212")
        print(f"Status: Checking...")
        
        try:
            self.go_to_page()
            
            # Check if logged in
            is_logged = self.session.is_logged_in("facebook", self.page)
            
            if is_logged:
                print("[OK] Logged In: YES")
                print("[OK] Page Access: OK")
                print("[OK] Ready for auto posting!")
            else:
                print("[WARNING] Not logged in")
        
        except Exception as e:
            print(f"[ERROR] {e}")
    
    def close(self):
        """Close browser."""
        self.session.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Facebook Page Auto Post")
    parser.add_argument("--post", type=str, help="Post text")
    parser.add_argument("--get", action="store_true", help="Get recent posts")
    parser.add_argument("--delete", type=int, help="Delete post by number")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    
    args = parser.parse_args()
    
    fb = FacebookPageAuto(headless=args.headless)
    
    try:
        fb.start()
        
        if args.post:
            fb.auto_post(args.post)
        elif args.get:
            fb.get_posts()
        elif args.delete:
            fb.delete_post(args.delete)
        elif args.status:
            fb.show_status()
        else:
            # Default: show status
            fb.show_status()
    
    finally:
        time.sleep(2)
        fb.close()


if __name__ == "__main__":
    main()
