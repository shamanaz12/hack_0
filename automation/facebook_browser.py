"""
Facebook Browser Automation Module
Handles posting, reading posts, deleting, and comment interactions on Facebook Business Page.
"""

import time
import random
from typing import List, Dict, Any, Optional
from playwright.sync_api import Page
from session_manager import SessionManager


class FacebookAutomation:
    """Facebook Business Page automation using Playwright."""
    
    def __init__(self, session_manager: SessionManager):
        self.session = session_manager
        self.logger = session_manager.logger
        self.page: Optional[Page] = None
    
    def ensure_logged_in(self) -> bool:
        """Ensure we're logged into Facebook."""
        if not self.session.browser:
            self.session.start_browser()
        
        if not self.session.is_logged_in("facebook", self.session.get_page("facebook")):
            return self.session.login_facebook()
        
        return True
    
    def navigate_to_page(self) -> bool:
        """Navigate to the business page."""
        return self.session.navigate_to_facebook_page()
    
    def post(self, text: str, link: Optional[str] = None) -> bool:
        """
        Create a post on the Facebook Business Page.
        Updated with reliable selectors for 2024 UI.
        
        Args:
            text: The post text content
            link: Optional link to include
        
        Returns:
            bool: True if post was successful
        """
        try:
            if not self.ensure_logged_in():
                return False

            self.page = self.session.get_page("facebook")
            self.navigate_to_page()
            self.session.human_delay(3, 5)

            # Find the post creation box
            self.logger.info("Looking for post creation box...")

            # Try clicking "What's on your mind?" section first
            create_post_areas = [
                "div[role='button'][aria-label*='Create post']",
                "div.x1y1aw1k",
                "div[class*='PostCreationDialog']",
                "span:has-text('What')",
                "div[data-testid='post-creation-textbox']"
            ]
            
            clicked = False
            for selector in create_post_areas:
                try:
                    btn = self.page.locator(selector).first
                    if btn.is_visible(timeout=3000):
                        btn.click()
                        clicked = True
                        self.logger.info(f"Clicked create post: {selector}")
                        self.session.human_delay(2, 3)
                        break
                except:
                    continue
            
            if not clicked:
                self.logger.warning("Could not find create post button")
                return False

            # Wait for post dialog to open
            self.page.wait_for_selector("div[role='dialog']", timeout=10000)
            self.session.human_delay(2, 3)

            # Find the textbox in dialog
            post_box = self.page.locator("div[role='textbox'][data-testid='post-creation-textbox']").first
            
            if not post_box.is_visible(timeout=5000):
                # Fallback: any editable div
                post_box = self.page.locator("div[contenteditable='true']").first

            if post_box.is_visible():
                # Click and type
                post_box.click()
                self.session.human_delay(1, 2)
                post_box.fill(text)
                self.session.human_delay(1, 2)

                # Add link if provided
                if link:
                    self.logger.info(f"Adding link: {link}")
                    post_box.press("Enter")
                    self.session.human_delay(1, 2)
                    post_box.type(f" {link}")
                    self.session.human_delay(2, 3)

                # Find and click post button
                post_btn = self.page.locator("button[aria-label*='Post'], div[role='button']:has-text('Post')").first
                
                if post_btn.is_visible(timeout=5000) and post_btn.is_enabled():
                    post_btn.click()
                    self.page.wait_for_load_state("networkidle")
                    self.session.human_delay(3, 5)
                    self.logger.info("Post published successfully!")
                    return True
                else:
                    self.logger.warning("Post button not found or disabled")
                    return False
            else:
                self.logger.error("Post creation box not found")
                return False

        except Exception as e:
            self.logger.error(f"Error creating post: {e}")
            return False

    def get_recent_posts(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent posts from the Facebook Business Page.
        
        Args:
            count: Number of posts to retrieve
        
        Returns:
            List of post dictionaries with id, text, timestamp, likes, comments
        """
        posts = []
        
        try:
            if not self.ensure_logged_in():
                return posts
            
            self.page = self.session.get_page("facebook")
            self.navigate_to_page()
            self.session.human_delay(3, 5)
            
            # Scroll to load posts
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.session.human_delay(2, 3)
            
            # Find posts container
            post_elements = self.page.locator("div[role='article'], div.x1y1aw1k").all()
            
            self.logger.info(f"Found {len(post_elements)} potential post elements")
            
            for i, post in enumerate(post_elements[:count]):
                try:
                    if not post.is_visible():
                        continue
                    
                    post_data = {
                        "id": f"post_{i}",
                        "text": "",
                        "timestamp": "",
                        "likes": 0,
                        "comments": 0,
                        "url": ""
                    }
                    
                    # Extract post text
                    try:
                        text_elem = post.locator("div[dir='auto'], span[dir='auto']").first
                        if text_elem.is_visible():
                            post_data["text"] = text_elem.inner_text()[:500]
                    except:
                        pass
                    
                    # Extract timestamp
                    try:
                        time_elem = post.locator("abbr[data-utime], span[aria-label*='ago']").first
                        if time_elem.is_visible():
                            post_data["timestamp"] = time_elem.get_attribute("data-utime") or time_elem.inner_text()
                    except:
                        pass
                    
                    # Extract likes
                    try:
                        like_elem = post.locator("span[aria-label*='like'], div:has-text(' reactions')").first
                        if like_elem.is_visible():
                            like_text = like_elem.inner_text()
                            # Extract number from text like "123 reactions"
                            import re
                            numbers = re.findall(r'\d+', like_text)
                            if numbers:
                                post_data["likes"] = int(numbers[0])
                    except:
                        pass
                    
                    # Extract comments count
                    try:
                        comment_elem = post.locator("span:has-text(' comment')").first
                        if comment_elem.is_visible():
                            comment_text = comment_elem.inner_text()
                            import re
                            numbers = re.findall(r'\d+', comment_text)
                            if numbers:
                                post_data["comments"] = int(numbers[0])
                    except:
                        pass
                    
                    # Try to get post URL
                    try:
                        link_elem = post.locator("a[href*='/posts/'], a[href*='/permalink/']").first
                        if link_elem.is_visible():
                            post_data["url"] = link_elem.get_attribute("href")
                            if post_data["url"] and not post_data["url"].startswith("http"):
                                post_data["url"] = "https://www.facebook.com" + post_data["url"]
                    except:
                        pass
                    
                    if post_data["text"]:  # Only add if we got some content
                        posts.append(post_data)
                        self.logger.info(f"Retrieved post: {post_data['text'][:50]}...")
                
                except Exception as e:
                    self.logger.debug(f"Error extracting post {i}: {e}")
                    continue
            
            self.logger.info(f"Retrieved {len(posts)} posts")
        
        except Exception as e:
            self.logger.error(f"Error getting posts: {e}")
        
        return posts
    
    def delete_post(self, post_id: str) -> bool:
        """
        Delete a post from the Facebook Business Page.
        
        Args:
            post_id: The post ID or URL
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            if not self.ensure_logged_in():
                return False
            
            self.page = self.session.get_page("facebook")
            
            # Navigate to the post
            if post_id.startswith("http"):
                self.page.goto(post_id, wait_until="networkidle")
            else:
                self.navigate_to_page()
            
            self.session.human_delay(2, 4)
            
            # Find the post options menu (three dots)
            options_btn = self.page.locator("div[role='button'][aria-label*='More'], button[aria-label*='Options']").first
            
            if options_btn.is_visible(timeout=5000):
                options_btn.click()
                self.session.human_delay(1, 2)
                
                # Find delete/trash option
                delete_options = [
                    "Move to trash",
                    "Delete",
                    "Delete post",
                    "Move post to trash"
                ]
                
                for option in delete_options:
                    delete_btn = self.page.locator(f"div[role='menuitem']:has-text('{option}')")
                    if delete_btn.is_visible(timeout=3000):
                        delete_btn.click()
                        self.session.human_delay(1, 2)
                        
                        # Confirm deletion
                        confirm_btn = self.page.locator("button:has-text('Move to trash'), button:has-text('Delete'), button:has-text('OK')")
                        if confirm_btn.is_visible(timeout=3000):
                            confirm_btn.click()
                            self.page.wait_for_load_state("networkidle")
                            self.session.human_delay(2, 3)
                            self.logger.info(f"Post {post_id} deleted successfully")
                            return True
                
                self.logger.warning("Delete option not found")
                return False
            
            self.logger.error("Post options menu not found")
            return False
        
        except Exception as e:
            self.logger.error(f"Error deleting post: {e}")
            return False
    
    def get_post_comments(self, post_url: str) -> List[Dict[str, Any]]:
        """
        Get comments from a specific post.
        
        Args:
            post_url: URL of the post
        
        Returns:
            List of comment dictionaries
        """
        comments = []
        
        try:
            if not self.ensure_logged_in():
                return comments
            
            self.page = self.session.get_page("facebook")
            
            # Navigate to post
            if post_url.startswith("http"):
                self.page.goto(post_url, wait_until="networkidle")
            else:
                self.navigate_to_page()
            
            self.session.human_delay(3, 5)
            
            # Scroll to load comments
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.session.human_delay(2, 3)
            
            # Find comments
            comment_elements = self.page.locator("div[role='article'], div[aria-label*='comment']").all()
            
            for i, comment in enumerate(comment_elements[:20]):
                try:
                    if not comment.is_visible():
                        continue
                    
                    comment_data = {
                        "id": f"comment_{i}",
                        "author": "",
                        "text": "",
                        "timestamp": "",
                        "likes": 0
                    }
                    
                    # Extract author
                    try:
                        author_elem = comment.locator("strong, a[href*='/profile']").first
                        if author_elem.is_visible():
                            comment_data["author"] = author_elem.inner_text()
                    except:
                        pass
                    
                    # Extract text
                    try:
                        text_elem = comment.locator("div[dir='auto'], span[dir='auto'], p").first
                        if text_elem.is_visible():
                            comment_data["text"] = text_elem.inner_text()[:500]
                    except:
                        pass
                    
                    if comment_data["text"]:
                        comments.append(comment_data)
                
                except Exception as e:
                    self.logger.debug(f"Error extracting comment {i}: {e}")
                    continue
            
            self.logger.info(f"Retrieved {len(comments)} comments")
        
        except Exception as e:
            self.logger.error(f"Error getting comments: {e}")
        
        return comments
    
    def reply_to_comment(self, comment_id: str, reply_text: str, post_url: Optional[str] = None) -> bool:
        """
        Reply to a comment on a post.
        
        Args:
            comment_id: The comment ID
            reply_text: The reply text
            post_url: Optional post URL if not on current page
        
        Returns:
            bool: True if reply was successful
        """
        try:
            if not self.ensure_logged_in():
                return False
            
            self.page = self.session.get_page("facebook")
            
            if post_url:
                self.page.goto(post_url, wait_until="networkidle")
                self.session.human_delay(2, 4)
            
            # Find reply button for the comment
            # This is simplified - in practice you'd need to locate the specific comment
            reply_btn = self.page.locator("span:has-text('Reply'), div[role='button']:has-text('Reply')").first
            
            if reply_btn.is_visible(timeout=5000):
                reply_btn.click()
                self.session.human_delay(1, 2)
                
                # Find reply input
                reply_input = self.page.locator("div[role='textbox'][data-testid='comment-input'], input[aria-label*='comment']").first
                
                if reply_input.is_visible(timeout=3000):
                    reply_input.fill(reply_text)
                    self.session.human_delay(1, 2)
                    
                    # Press enter to post
                    reply_input.press("Enter")
                    self.page.wait_for_load_state("networkidle")
                    self.session.human_delay(2, 3)
                    
                    self.logger.info(f"Replied to comment: {reply_text[:50]}...")
                    return True
            
            self.logger.warning("Reply button not found")
            return False
        
        except Exception as e:
            self.logger.error(f"Error replying to comment: {e}")
            return False
    
    def reply_to_post_comment(self, post_url: str, reply_text: str) -> bool:
        """
        Add a comment/reply to a post.
        
        Args:
            post_url: URL of the post
            reply_text: The comment text
        
        Returns:
            bool: True if comment was successful
        """
        try:
            if not self.ensure_logged_in():
                return False
            
            self.page = self.session.get_page("facebook")
            self.page.goto(post_url, wait_until="networkidle")
            self.session.human_delay(2, 4)
            
            # Find comment input
            comment_input = self.page.locator(
                "div[role='textbox'][data-testid='comment-input'], "
                "input[aria-label*='Write a comment'], "
                "div[contenteditable][aria-label*='comment']"
            ).first
            
            if comment_input.is_visible(timeout=5000):
                comment_input.click()
                self.session.human_delay(1, 2)
                comment_input.fill(reply_text)
                self.session.human_delay(1, 2)
                
                # Press enter or click post button
                comment_input.press("Enter")
                self.page.wait_for_load_state("networkidle")
                self.session.human_delay(2, 3)
                
                self.logger.info(f"Comment posted: {reply_text[:50]}...")
                return True
            
            self.logger.warning("Comment input not found")
            return False
        
        except Exception as e:
            self.logger.error(f"Error posting comment: {e}")
            return False


# Convenience functions
def get_facebook_automation(headless: bool = False) -> FacebookAutomation:
    """Get Facebook automation instance."""
    from session_manager import get_session_manager
    session = get_session_manager(headless=headless)
    return FacebookAutomation(session)
