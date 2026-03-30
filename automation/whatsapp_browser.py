"""
WhatsApp Web Browser Automation Module
Handles reading messages, sending replies, and sending new messages.
"""

import time
import random
from typing import List, Dict, Any, Optional
from playwright.sync_api import Page


class WhatsAppAutomation:
    """WhatsApp Web automation using Playwright."""
    
    def __init__(self, session_manager):
        self.session = session_manager
        self.logger = session_manager.logger
        self.page: Optional[Page] = None
    
    def ensure_logged_in(self) -> bool:
        """Ensure we're logged into WhatsApp Web."""
        if not self.session.browser:
            self.session.start_browser()
        
        if not self.session.is_logged_in("whatsapp", self.session.get_page("whatsapp")):
            return self.session.login_whatsapp()
        
        return True
    
    def read_unread_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Read unread messages from WhatsApp Web.
        
        Args:
            count: Maximum number of messages to retrieve
        
        Returns:
            List of message dictionaries
        """
        messages = []
        
        try:
            if not self.ensure_logged_in():
                return messages
            
            self.page = self.session.get_page("whatsapp")
            self.page.goto("https://web.whatsapp.com/", wait_until="networkidle")
            self.session.human_delay(3, 5)
            
            # Wait for chat list to load
            self.logger.info("Waiting for chat list...")
            
            # Find unread chat indicators
            unread_chats = self.page.locator(
                "div[aria-label*='unread'], "
                "span[title*='unread'], "
                "div[data-testid='unread']"
            ).all()
            
            self.logger.info(f"Found {len(unread_chats)} unread chats")
            
            for i, chat in enumerate(unread_chats[:count]):
                try:
                    if not chat.is_visible():
                        continue
                    
                    # Click on the chat
                    chat.click()
                    self.session.human_delay(2, 3)
                    
                    # Get chat info
                    message_data = {
                        "id": f"msg_{i}",
                        "sender": "",
                        "text": "",
                        "timestamp": "",
                        "is_group": False
                    }
                    
                    # Extract sender name
                    try:
                        sender_elem = self.page.locator("span[title], div[data-testid='conversation-info-header-chat-title']").first
                        if sender_elem.is_visible():
                            message_data["sender"] = sender_elem.inner_text()
                            # Check if it's a group
                            message_data["is_group"] = "group" in sender_elem.inner_text().lower()
                    except:
                        pass
                    
                    # Extract last message
                    try:
                        msg_elem = self.page.locator(
                            "div[data-testid='message-container'] span[dir='auto'], "
                            "div.message-in span[dir='auto'], "
                            "span[dir='auto']:not([aria-label])"
                        ).last
                        if msg_elem.is_visible():
                            message_data["text"] = msg_elem.inner_text()[:500]
                    except:
                        pass
                    
                    # Extract timestamp
                    try:
                        time_elem = self.page.locator("span[data-testid='message-meta-block'], span[title]").last
                        if time_elem.is_visible():
                            message_data["timestamp"] = time_elem.get_attribute("title") or time_elem.inner_text()
                    except:
                        pass
                    
                    if message_data["text"]:
                        messages.append(message_data)
                        self.logger.info(f"Read message from {message_data['sender']}: {message_data['text'][:50]}...")
                    
                    # Go back to chat list
                    back_btn = self.page.locator("button[aria-label='Back'], button[data-testid='back']").first
                    if back_btn.is_visible(timeout=3000):
                        back_btn.click()
                        self.session.human_delay(1, 2)
                
                except Exception as e:
                    self.logger.debug(f"Error reading message {i}: {e}")
                    continue
            
            self.logger.info(f"Retrieved {len(messages)} unread messages")
        
        except Exception as e:
            self.logger.error(f"Error reading WhatsApp messages: {e}")
        
        return messages
    
    def send_message(self, phone_or_contact: str, message: str) -> bool:
        """
        Send a new message to a contact or phone number.
        
        Args:
            phone_or_contact: Phone number (with country code) or contact name
            message: The message text
        
        Returns:
            bool: True if message was sent successfully
        """
        try:
            if not self.ensure_logged_in():
                return False
            
            self.page = self.session.get_page("whatsapp")
            self.page.goto("https://web.whatsapp.com/", wait_until="networkidle")
            self.session.human_delay(3, 5)
            
            # Click on new chat / compose button
            self.logger.info("Looking for new chat button...")
            
            new_chat_btn = self.page.locator(
                "button[aria-label='New chat'], "
                "button[aria-label='Start new conversation'], "
                "div[role='button'][aria-label*='New chat']"
            ).first
            
            if new_chat_btn.is_visible(timeout=5000):
                new_chat_btn.click()
                self.session.human_delay(2, 3)
                
                # Search for contact/number
                search_input = self.page.locator(
                    "input[aria-label='Search'], "
                    "input[placeholder*='Search']"
                ).first
                
                if search_input.is_visible(timeout=5000):
                    search_input.fill(phone_or_contact)
                    self.session.human_delay(2, 3)
                    
                    # Click on the contact from search results
                    contact_result = self.page.locator("div[role='listitem'], span[dir='auto']").first
                    
                    if contact_result.is_visible(timeout=5000):
                        contact_result.click()
                        self.session.human_delay(2, 3)
                        
                        # Type message
                        message_input = self.page.locator(
                            "div[contenteditable][data-tab='10'], "
                            "div[aria-label='Message input']"
                        ).first
                        
                        if message_input.is_visible(timeout=5000):
                            message_input.click()
                            self.session.human_delay(1, 2)
                            message_input.fill(message)
                            self.session.human_delay(1, 2)
                            
                            # Click send button
                            send_btn = self.page.locator(
                                "button[aria-label='Send'], "
                                "button[data-testid='compose-btn-send']"
                            ).first
                            
                            if send_btn.is_visible(timeout=3000):
                                send_btn.click()
                                self.page.wait_for_load_state("networkidle")
                                self.session.human_delay(2, 3)
                                
                                self.logger.info(f"Message sent to {phone_or_contact}: {message[:50]}...")
                                return True
                            else:
                                self.logger.warning("Send button not found")
                                return False
                        else:
                            self.logger.warning("Message input not found")
                            return False
                    else:
                        self.logger.warning(f"Contact not found: {phone_or_contact}")
                        return False
                else:
                    self.logger.warning("Search input not found")
                    return False
            else:
                self.logger.error("New chat button not found")
                return False
        
        except Exception as e:
            self.logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    def send_reply(self, reply_text: str) -> bool:
        """
        Send a reply in the currently open chat.
        
        Args:
            reply_text: The reply message
        
        Returns:
            bool: True if reply was sent successfully
        """
        try:
            if not self.ensure_logged_in():
                return False
            
            self.page = self.session.get_page("whatsapp")
            
            # Find message input in current chat
            message_input = self.page.locator(
                "div[contenteditable][data-tab='10'], "
                "div[aria-label='Message input']"
            ).first
            
            if message_input.is_visible(timeout=5000):
                message_input.click()
                self.session.human_delay(1, 2)
                message_input.fill(reply_text)
                self.session.human_delay(1, 2)
                
                # Click send button
                send_btn = self.page.locator(
                    "button[aria-label='Send'], "
                    "button[data-testid='compose-btn-send']"
                ).first
                
                if send_btn.is_visible(timeout=3000):
                    send_btn.click()
                    self.page.wait_for_load_state("networkidle")
                    self.session.human_delay(2, 3)
                    
                    self.logger.info(f"Reply sent: {reply_text[:50]}...")
                    return True
                else:
                    self.logger.warning("Send button not found")
                    return False
            else:
                self.logger.warning("Message input not found - no chat open?")
                return False
        
        except Exception as e:
            self.logger.error(f"Error sending WhatsApp reply: {e}")
            return False
    
    def get_recent_chats(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get list of recent chats.
        
        Args:
            count: Number of chats to retrieve
        
        Returns:
            List of chat dictionaries
        """
        chats = []
        
        try:
            if not self.ensure_logged_in():
                return chats
            
            self.page = self.session.get_page("whatsapp")
            self.page.goto("https://web.whatsapp.com/", wait_until="networkidle")
            self.session.human_delay(3, 5)
            
            # Find chat list items
            chat_elements = self.page.locator(
                "div[role='listitem'], "
                "div[data-testid='chat-list'] > div"
            ).all()
            
            self.logger.info(f"Found {len(chat_elements)} chat elements")
            
            for i, chat in enumerate(chat_elements[:count]):
                try:
                    if not chat.is_visible():
                        continue
                    
                    chat_data = {
                        "id": f"chat_{i}",
                        "name": "",
                        "last_message": "",
                        "timestamp": "",
                        "unread_count": 0
                    }
                    
                    # Extract name
                    try:
                        name_elem = chat.locator("span[dir='auto'][title]").first
                        if name_elem.is_visible():
                            chat_data["name"] = name_elem.inner_text()
                    except:
                        pass
                    
                    # Extract last message
                    try:
                        msg_elem = chat.locator("span[dir='auto']:not([title])").last
                        if msg_elem.is_visible():
                            chat_data["last_message"] = msg_elem.inner_text()[:100]
                    except:
                        pass
                    
                    # Extract unread count
                    try:
                        unread_elem = chat.locator("span[aria-label*='unread'], div[data-testid='unread']")
                        if unread_elem.is_visible():
                            unread_text = unread_elem.inner_text()
                            import re
                            numbers = re.findall(r'\d+', unread_text)
                            if numbers:
                                chat_data["unread_count"] = int(numbers[0])
                            else:
                                chat_data["unread_count"] = 1
                    except:
                        pass
                    
                    if chat_data["name"]:
                        chats.append(chat_data)
                        self.logger.info(f"Found chat: {chat_data['name']}")
                
                except Exception as e:
                    self.logger.debug(f"Error extracting chat {i}: {e}")
                    continue
            
            self.logger.info(f"Retrieved {len(chats)} recent chats")
        
        except Exception as e:
            self.logger.error(f"Error getting WhatsApp chats: {e}")
        
        return chats


# Convenience functions
def get_whatsapp_automation(headless: bool = False):
    """Get WhatsApp automation instance."""
    from session_manager import get_session_manager
    session = get_session_manager(headless=headless)
    return WhatsAppAutomation(session)
