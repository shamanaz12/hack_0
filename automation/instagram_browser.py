"""
Instagram Browser Automation Module
Handles posting, reading posts, deleting, and comment interactions on Instagram.
"""

import time
import random
from typing import List, Dict, Any, Optional
from pathlib import Path
from playwright.sync_api import Page


class InstagramAutomation:
    """Instagram Business Account automation using Playwright."""
    
    def __init__(self, session_manager):
        self.session = session_manager
        self.logger = session_manager.logger
        self.page: Optional[Page] = None
    
    def ensure_logged_in(self) -> bool:
        """Ensure we're logged into Instagram."""
        if not self.session.browser:
            self.session.start_browser()
        
        if not self.session.is_logged_in("instagram", self.session.get_page("instagram")):
            return self.session.login_instagram()
        
        return True
    
    def post(self, text: str, image_path: Optional[str] = None) -> bool:
        """
        Create a post on Instagram.
        Updated with reliable selectors for 2024 UI.

        Args:
            text: The caption text
            image_path: Optional path to image file

        Returns:
            bool: True if post was successful
        """
        try:
            if not self.ensure_logged_in():
                return False

            self.page = self.session.get_page("instagram")
            self.page.goto("https://www.instagram.com/", wait_until="networkidle")
            self.session.human_delay(3, 5)

            # Handle any startup dialogs
            self._handle_dialogs()

            # Click on create/new post button
            self.logger.info("Looking for create post button...")

            # Instagram 2024 selectors
            create_btn = self.page.locator("div[role='button'][aria-label='New post']").first
            
            if not create_btn.is_visible(timeout=5000):
                # Try alternative - the + icon in top bar
                create_btn = self.page.locator("svg[aria-label='New post']").first
            
            if create_btn.is_visible():
                self.logger.info("Found create post button")
                create_btn.click()
                self.session.human_delay(2, 3)

                # Handle file upload if image provided
                if image_path:
                    self.logger.info(f"Uploading image: {image_path}")

                    file_input = self.page.locator("input[type='file']").first
                    if file_input.is_visible(timeout=5000):
                        file_input.set_input_files(image_path)
                        self.session.human_delay(3, 5)

                        # Click "Next"
                        next_btn = self.page.locator("button:has-text('Next'), div[role='button']:has-text('Next')").first
                        if next_btn.is_visible(timeout=5000):
                            next_btn.click()
                            self.session.human_delay(2, 3)

                            # Click "Next" again for filters
                            try:
                                next_btn.click()
                                self.session.human_delay(2, 3)
                            except:
                                pass  # Sometimes only one Next is needed

                            # Add caption
                            caption_input = self.page.locator("textarea[aria-label*='Write a caption'], textarea[placeholder*='caption']").first
                            if caption_input.is_visible(timeout=5000):
                                caption_input.fill(text)
                                self.session.human_delay(1, 2)

                                # Click "Share"
                                share_btn = self.page.locator("button:has-text('Share'), div[role='button']:has-text('Share')").first
                                if share_btn.is_visible(timeout=5000):
                                    share_btn.click()
                                    self.page.wait_for_load_state("networkidle")
                                    self.session.human_delay(3, 5)

                                    self.logger.info("Instagram post published successfully!")
                                    return True
                                else:
                                    self.logger.warning("Share button not found")
                                    return False
                            else:
                                self.logger.warning("Caption input not found")
                                return False
                        else:
                            self.logger.warning("Next button not found")
                            return False
                    else:
                        self.logger.warning("File input not found")
                        return False
                else:
                    # Instagram requires an image
                    self.logger.warning("Instagram requires an image for posts")
                    return False
            else:
                self.logger.error("Create post button not found")
                return False

        except Exception as e:
            self.logger.error(f"Error creating Instagram post: {e}")
            return False
                                share_btn = self.page.locator("button:has-text('Share'), div[role='button']:has-text('Share')").first
                                if share_btn.is_visible(timeout=5000):
                                    share_btn.click()
                                    self.page.wait_for_load_state("networkidle")
                                    self.session.human_delay(3, 5)
                                    
                                    self.logger.info("Instagram post published successfully!")
                                    return True
                                else:
                                    self.logger.warning("Share button not found")
                                    return False
                            else:
                                self.logger.warning("Caption input not found")
                                return False
                        else:
                            self.logger.warning("Next button not found")
                            return False
                    else:
                        self.logger.warning("File input not found")
                        return False
                else:
                    # Text-only post (Instagram doesn't support text-only posts directly)
                    self.logger.warning("Instagram requires an image for posts")
                    return False
            else:
                self.logger.error("Create post button not found")
                return False
        
        except Exception as e:
            self.logger.error(f"Error creating Instagram post: {e}")
            return False
    
    def get_recent_posts(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent posts from Instagram profile.
        
        Args:
            count: Number of posts to retrieve
        
        Returns:
            List of post dictionaries
        """
        posts = []
        
        try:
            if not self.ensure_logged_in():
                return posts
            
            self.page = self.session.get_page("instagram")
            
            # Navigate to profile
            username = self.session.credentials["instagram"]["username"]
            profile_url = f"https://www.instagram.com/{username}/"
            self.page.goto(profile_url, wait_until="networkidle")
            self.session.human_delay(3, 5)
            
            # Handle "Not now" for notifications
            self._handle_dialogs()
            
            # Find post grid
            post_elements = self.page.locator("a[href*='/p/']").all()
            
            self.logger.info(f"Found {len(post_elements)} post elements")
            
            for i, post_elem in enumerate(post_elements[:count]):
                try:
                    if not post_elem.is_visible():
                        continue
                    
                    post_data = {
                        "id": f"post_{i}",
                        "url": "",
                        "caption": "",
                        "likes": 0,
                        "comments": 0,
                        "timestamp": ""
                    }
                    
                    # Get post URL
                    href = post_elem.get_attribute("href")
                    if href:
                        post_data["url"] = href
                        if not href.startswith("http"):
                            post_data["url"] = "https://www.instagram.com" + href
                    
                    # Click to open post for details
                    post_elem.click()
                    self.session.human_delay(2, 3)
                    
                    # Handle dialogs
                    self._handle_dialogs()
                    
                    # Extract caption
                    try:
                        caption_elem = self.page.locator("span[dir='auto']").first
                        if caption_elem.is_visible():
                            post_data["caption"] = caption_elem.inner_text()[:500]
                    except:
                        pass
                    
                    # Extract likes
                    try:
                        like_elem = self.page.locator("span[aria-label*='like'], span:has-text(' likes')").first
                        if like_elem.is_visible():
                            like_text = like_elem.inner_text()
                            import re
                            numbers = re.findall(r'\d+', like_text)
                            if numbers:
                                post_data["likes"] = int(numbers[0])
                    except:
                        pass
                    
                    # Extract comments
                    try:
                        comment_elem = self.page.locator("span:has-text(' comments'), span:has-text(' comments')").first
                        if comment_elem.is_visible():
                            comment_text = comment_elem.inner_text()
                            import re
                            numbers = re.findall(r'\d+', comment_text)
                            if numbers:
                                post_data["comments"] = int(numbers[0])
                    except:
                        pass
                    
                    # Close modal
                    close_btn = self.page.locator("button[aria-label='Close'], svg[aria-label='Close']").first
                    if close_btn.is_visible(timeout=3000):
                        close_btn.click()
                        self.session.human_delay(1, 2)
                    
                    if post_data["url"]:
                        posts.append(post_data)
                        self.logger.info(f"Retrieved post: {post_data['url']}")
                
                except Exception as e:
                    self.logger.debug(f"Error extracting post {i}: {e}")
                    continue
            
            self.logger.info(f"Retrieved {len(posts)} posts")
        
        except Exception as e:
            self.logger.error(f"Error getting Instagram posts: {e}")
        
        return posts
    
    def delete_post(self, post_url: str) -> bool:
        """
        Delete a post from Instagram.
        
        Args:
            post_url: URL of the post to delete
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            if not self.ensure_logged_in():
                return False
            
            self.page = self.session.get_page("instagram")
            self.page.goto(post_url, wait_until="networkidle")
            self.session.human_delay(3, 5)
            
            # Handle dialogs
            self._handle_dialogs()
            
            # Click on post options (three dots)
            options_btn = self.page.locator("svg[aria-label*='Options'], button[aria-label*='Options']").first
            
            if options_btn.is_visible(timeout=5000):
                options_btn.click()
                self.session.human_delay(1, 2)
                
                # Find delete option
                delete_btn = self.page.locator("div[role='menuitem']:has-text('Delete'), button:has-text('Delete')").first
                
                if delete_btn.is_visible(timeout=3000):
                    delete_btn.click()
                    self.session.human_delay(1, 2)
                    
                    # Confirm deletion
                    confirm_btn = self.page.locator("button:has-text('Delete'), button:has-text('Delete post')").first
                    if confirm_btn.is_visible(timeout=3000):
                        confirm_btn.click()
                        self.page.wait_for_load_state("networkidle")
                        self.session.human_delay(2, 3)
                        
                        self.logger.info(f"Post deleted: {post_url}")
                        return True
                
                self.logger.warning("Delete option not found")
                return False
            
            self.logger.error("Post options not found")
            return False
        
        except Exception as e:
            self.logger.error(f"Error deleting Instagram post: {e}")
            return False
    
    def get_post_comments(self, post_url: str) -> List[Dict[str, Any]]:
        """
        Get comments from an Instagram post.
        
        Args:
            post_url: URL of the post
        
        Returns:
            List of comment dictionaries
        """
        comments = []
        
        try:
            if not self.ensure_logged_in():
                return comments
            
            self.page = self.session.get_page("instagram")
            self.page.goto(post_url, wait_until="networkidle")
            self.session.human_delay(3, 5)
            
            # Handle dialogs
            self._handle_dialogs()
            
            # Click to view all comments
            view_comments = self.page.locator("a[href*='/comments/'], button:has-text('View all comments')").first
            if view_comments.is_visible(timeout=5000):
                view_comments.click()
                self.session.human_delay(2, 3)
            
            # Scroll to load comments
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.session.human_delay(2, 3)
            
            # Find comments
            comment_elements = self.page.locator("ul[aria-label*='comment'], li[aria-label*='comment']").all()
            
            for i, comment in enumerate(comment_elements[:20]):
                try:
                    if not comment.is_visible():
                        continue
                    
                    comment_data = {
                        "id": f"comment_{i}",
                        "author": "",
                        "text": "",
                        "timestamp": ""
                    }
                    
                    # Extract author
                    try:
                        author_elem = comment.locator("a[href*='/profile'], strong").first
                        if author_elem.is_visible():
                            comment_data["author"] = author_elem.inner_text()
                    except:
                        pass
                    
                    # Extract text
                    try:
                        text_elem = comment.locator("span[dir='auto'], div[dir='auto']").first
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
            self.logger.error(f"Error getting Instagram comments: {e}")
        
        return comments
    
    def reply_to_comment(self, post_url: str, reply_text: str) -> bool:
        """
        Reply to a comment on an Instagram post.
        
        Args:
            post_url: URL of the post
            reply_text: The reply text
        
        Returns:
            bool: True if reply was successful
        """
        try:
            if not self.ensure_logged_in():
                return False
            
            self.page = self.session.get_page("instagram")
            self.page.goto(post_url, wait_until="networkidle")
            self.session.human_delay(3, 5)
            
            # Handle dialogs
            self._handle_dialogs()
            
            # Find comment input
            comment_input = self.page.locator(
                "textarea[aria-label*='comment'], "
                "input[placeholder*='comment']"
            ).first
            
            if comment_input.is_visible(timeout=5000):
                comment_input.click()
                self.session.human_delay(1, 2)
                comment_input.fill(reply_text)
                self.session.human_delay(1, 2)
                
                # Click post button
                post_btn = self.page.locator("button:has-text('Post'), div[role='button']:has-text('Post')").first
                if post_btn.is_visible(timeout=3000):
                    post_btn.click()
                    self.page.wait_for_load_state("networkidle")
                    self.session.human_delay(2, 3)
                    
                    self.logger.info(f"Comment posted: {reply_text[:50]}...")
                    return True
            
            self.logger.warning("Comment input not found")
            return False
        
        except Exception as e:
            self.logger.error(f"Error posting Instagram comment: {e}")
            return False
    
    def _handle_dialogs(self):
        """Handle Instagram notification and cookie dialogs."""
        try:
            # "Not now" for notifications
            not_now_btns = [
                "button:has-text('Not now')",
                "button:has-text('Not Now')"
            ]
            
            for selector in not_now_btns:
                try:
                    btn = self.page.locator(selector).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        self.session.human_delay(1, 2)
                        break
                except:
                    continue
            
            # "Allow" cookies
            try:
                allow_btn = self.page.locator("button:has-text('Allow'), button:has-text('Accept')").first
                if allow_btn.is_visible(timeout=2000):
                    allow_btn.click()
                    self.session.human_delay(1, 2)
            except:
                pass
        
        except Exception as e:
            self.logger.debug(f"Dialog handling error: {e}")


# Convenience functions
def get_instagram_automation(headless: bool = False):
    """Get Instagram automation instance."""
    from session_manager import get_session_manager
    session = get_session_manager(headless=headless)
    return InstagramAutomation(session)
