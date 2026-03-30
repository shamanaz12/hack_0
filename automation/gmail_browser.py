"""
Gmail Browser Automation Module
Handles reading emails, sending replies, and marking as read.
"""

import time
import random
from typing import List, Dict, Any, Optional
from playwright.sync_api import Page


class GmailAutomation:
    """Gmail web automation using Playwright."""
    
    def __init__(self, session_manager):
        self.session = session_manager
        self.logger = session_manager.logger
        self.page: Optional[Page] = None
    
    def ensure_logged_in(self) -> bool:
        """Ensure we're logged into Gmail."""
        if not self.session.browser:
            self.session.start_browser()
        
        if not self.session.is_logged_in("gmail", self.session.get_page("gmail")):
            return self.session.login_gmail()
        
        return True
    
    def read_unread_emails(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Read unread emails from Gmail inbox.
        
        Args:
            count: Maximum number of emails to retrieve
        
        Returns:
            List of email dictionaries
        """
        emails = []
        
        try:
            if not self.ensure_logged_in():
                return emails
            
            self.page = self.session.get_page("gmail")
            self.page.goto("https://mail.google.com/mail/u/0/#inbox", wait_until="networkidle")
            self.session.human_delay(3, 5)
            
            # Wait for inbox to load
            self.logger.info("Waiting for inbox to load...")
            self.page.wait_for_selector("div[role='listitem']", timeout=10000)
            self.session.human_delay(2, 3)
            
            # Find unread emails (bold text indicates unread)
            email_elements = self.page.locator("div[role='listitem']").all()
            
            self.logger.info(f"Found {len(email_elements)} email elements")
            
            for i, email_elem in enumerate(email_elements[:count]):
                try:
                    # Check if unread (bold font)
                    is_unread = False
                    try:
                        sender_elem = email_elem.locator("span[aria-label], div.y6").first
                        if sender_elem.is_visible():
                            # Unread emails have bold font-weight
                            font_weight = sender_elem.evaluate("el => window.getComputedStyle(el).fontWeight")
                            is_unread = font_weight and int(font_weight) > 400
                    except:
                        pass
                    
                    if not is_unread and i > 0:
                        # Skip read emails after finding first few
                        continue
                    
                    email_data = {
                        "id": f"email_{i}",
                        "sender": "",
                        "subject": "",
                        "snippet": "",
                        "timestamp": "",
                        "is_unread": is_unread
                    }
                    
                    # Extract sender
                    try:
                        sender_elem = email_elem.locator("span[aria-label], div.y6").first
                        if sender_elem.is_visible():
                            email_data["sender"] = sender_elem.inner_text()
                    except:
                        pass
                    
                    # Extract subject
                    try:
                        subject_elem = email_elem.locator("span[aria-label*='subject'], div.yP").first
                        if subject_elem.is_visible():
                            email_data["subject"] = subject_elem.inner_text()
                    except:
                        pass
                    
                    # Extract snippet/preview
                    try:
                        snippet_elem = email_elem.locator("div.y2, span.aoP").first
                        if snippet_elem.is_visible():
                            email_data["snippet"] = snippet_elem.inner_text()[:200]
                    except:
                        pass
                    
                    # Extract timestamp
                    try:
                        time_elem = email_elem.locator("span[aria-label*='time'], div.yW").first
                        if time_elem.is_visible():
                            email_data["timestamp"] = time_elem.get_attribute("aria-label") or time_elem.inner_text()
                    except:
                        pass
                    
                    if email_data["sender"] or email_data["subject"]:
                        emails.append(email_data)
                        self.logger.info(f"Found email from {email_data['sender']}: {email_data['subject'][:50]}...")
                    
                    # Stop if we have enough unread emails
                    if len([e for e in emails if e["is_unread"]]) >= count:
                        break
                
                except Exception as e:
                    self.logger.debug(f"Error extracting email {i}: {e}")
                    continue
            
            self.logger.info(f"Retrieved {len(emails)} emails")
        
        except Exception as e:
            self.logger.error(f"Error reading Gmail emails: {e}")
        
        return emails
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send a new email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
        
        Returns:
            bool: True if email was sent successfully
        """
        try:
            if not self.ensure_logged_in():
                return False
            
            self.page = self.session.get_page("gmail")
            self.page.goto("https://mail.google.com/mail/u/0/#inbox", wait_until="networkidle")
            self.session.human_delay(3, 5)
            
            # Click on Compose button
            self.logger.info("Looking for compose button...")
            
            compose_btn = self.page.locator("div[aria-label='Compose'], button[aria-label='Compose']").first
            
            if compose_btn.is_visible(timeout=5000):
                compose_btn.click()
                self.session.human_delay(2, 3)
                
                # Wait for compose window
                self.page.wait_for_selector("textarea[name='to']", timeout=10000)
                self.session.human_delay(1, 2)
                
                # Fill in recipient
                to_input = self.page.locator("textarea[name='to'], input[name='to']").first
                if to_input.is_visible(timeout=5000):
                    to_input.fill(to)
                    self.session.human_delay(1, 2)
                    
                    # Press enter to confirm recipient
                    to_input.press("Enter")
                    self.session.human_delay(1, 2)
                    
                    # Fill in subject
                    subject_input = self.page.locator("input[name='subject'], input[aria-label='Subject']").first
                    if subject_input.is_visible(timeout=5000):
                        subject_input.fill(subject)
                        self.session.human_delay(1, 2)
                        
                        # Fill in body
                        body_input = self.page.locator("div[aria-label='Message body'], div[contenteditable='true']").first
                        if body_input.is_visible(timeout=5000):
                            body_input.click()
                            self.session.human_delay(1, 2)
                            body_input.fill(body)
                            self.session.human_delay(2, 3)
                            
                            # Click Send button
                            send_btn = self.page.locator("button[aria-label='Send'], div[aria-label='Send']").first
                            if send_btn.is_visible(timeout=5000):
                                send_btn.click()
                                self.page.wait_for_load_state("networkidle")
                                self.session.human_delay(2, 3)
                                
                                self.logger.info(f"Email sent to {to}: {subject}")
                                return True
                            else:
                                self.logger.warning("Send button not found")
                                return False
                        else:
                            self.logger.warning("Body input not found")
                            return False
                    else:
                        self.logger.warning("Subject input not found")
                        return False
                else:
                    self.logger.warning("To input not found")
                    return False
            else:
                self.logger.error("Compose button not found")
                return False
        
        except Exception as e:
            self.logger.error(f"Error sending Gmail email: {e}")
            return False
    
    def send_reply(self, reply_text: str) -> bool:
        """
        Send a reply to the currently open email.
        
        Args:
            reply_text: The reply message
        
        Returns:
            bool: True if reply was sent successfully
        """
        try:
            if not self.ensure_logged_in():
                return False
            
            self.page = self.session.get_page("gmail")
            
            # Find reply box
            reply_box = self.page.locator(
                "div[aria-label='Message body'], "
                "div[role='textbox'][aria-label*='reply'], "
                "div[contenteditable='true']"
            ).last  # Use last as reply box is usually at the bottom
            
            if reply_box.is_visible(timeout=5000):
                reply_box.click()
                self.session.human_delay(1, 2)
                reply_box.fill(reply_text)
                self.session.human_delay(1, 2)
                
                # Click Send button
                send_btn = self.page.locator("button[aria-label='Send'], div[aria-label='Send']").first
                if send_btn.is_visible(timeout=5000):
                    send_btn.click()
                    self.page.wait_for_load_state("networkidle")
                    self.session.human_delay(2, 3)
                    
                    self.logger.info(f"Reply sent: {reply_text[:50]}...")
                    return True
                else:
                    self.logger.warning("Send button not found")
                    return False
            else:
                self.logger.warning("Reply box not found - no email open?")
                return False
        
        except Exception as e:
            self.logger.error(f"Error sending Gmail reply: {e}")
            return False
    
    def mark_as_read(self, email_ids: Optional[List[str]] = None) -> bool:
        """
        Mark emails as read.
        
        Args:
            email_ids: List of email IDs to mark as read. If None, marks all unread in view.
        
        Returns:
            bool: True if operation was successful
        """
        try:
            if not self.ensure_logged_in():
                return False
            
            self.page = self.session.get_page("gmail")
            self.page.goto("https://mail.google.com/mail/u/0/#inbox", wait_until="networkidle")
            self.session.human_delay(3, 5)
            
            if email_ids:
                # Mark specific emails
                for email_id in email_ids:
                    try:
                        # Find and click the email to select
                        email_elem = self.page.locator(f"div[data-legacy-message-id='{email_id}']")
                        if email_elem.is_visible(timeout=3000):
                            email_elem.click()
                            self.session.human_delay(1, 2)
                            
                            # Click "Mark as read" button
                            mark_read_btn = self.page.locator("button[aria-label='Mark as read'], div[aria-label='Mark as read']").first
                            if mark_read_btn.is_visible(timeout=3000):
                                mark_read_btn.click()
                                self.session.human_delay(1, 2)
                                self.logger.info(f"Marked {email_id} as read")
                    except Exception as e:
                        self.logger.debug(f"Error marking {email_id} as read: {e}")
                        continue
            else:
                # Mark all visible as read
                select_all = self.page.locator("div[role='checkbox'][aria-label='Select'], input[type='checkbox']").first
                if select_all.is_visible(timeout=5000):
                    select_all.click()
                    self.session.human_delay(1, 2)
                    
                    mark_read_btn = self.page.locator("button[aria-label='Mark as read'], div[aria-label='Mark as read']").first
                    if mark_read_btn.is_visible(timeout=3000):
                        mark_read_btn.click()
                        self.session.human_delay(1, 2)
                        self.logger.info("Marked all visible emails as read")
                        return True
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error marking emails as read: {e}")
            return False
    
    def get_email_count(self) -> Dict[str, int]:
        """
        Get count of unread emails.
        
        Returns:
            Dictionary with unread count
        """
        try:
            if not self.ensure_logged_in():
                return {"unread": 0}
            
            self.page = self.session.get_page("gmail")
            self.page.goto("https://mail.google.com/mail/u/0/#inbox", wait_until="networkidle")
            self.session.human_delay(3, 5)
            
            # Look for unread count badge
            unread_elem = self.page.locator("div[aria-label='Inbox'], a[href*='#inbox'] span.aim").first
            
            if unread_elem.is_visible(timeout=5000):
                unread_text = unread_elem.inner_text()
                import re
                numbers = re.findall(r'\d+', unread_text)
                if numbers:
                    count = int(numbers[0])
                    self.logger.info(f"Unread emails: {count}")
                    return {"unread": count}
            
            return {"unread": 0}
        
        except Exception as e:
            self.logger.error(f"Error getting email count: {e}")
            return {"unread": 0}


# Convenience functions
def get_gmail_automation(headless: bool = False):
    """Get Gmail automation instance."""
    from session_manager import get_session_manager
    session = get_session_manager(headless=headless)
    return GmailAutomation(session)
