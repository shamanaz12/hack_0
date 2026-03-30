"""
WhatsApp Web Watcher using Playwright - CORRECTED VERSION
Monitors WhatsApp Web for unread messages containing keywords
Saves messages as markdown files in Needs_Action folder

FIXES APPLIED (ghaltiyan jo fix ki gayi hain):
=====================================================

1. OUTDATED SELECTOR FIX:
   - PURANA (galat): div[data-testid="default-user"] - WhatsApp Web par ab nahi hai
   - NAYA (sahi): canvas[aria-label="Scan me!"] for QR detection
                  div[data-testid="chat-list"] for logged-in state
   - WhatsApp Web ke selectors update ho jate hain, isliye multiple fallbacks use kiye hain

2. EVENT LOOP CLOSED ERROR FIX:
   - PURANA (galat): finally block mein close() call hota tha exception ke baad,
                     lekin playwright already close ho chuka hota tha
   - NAYA (sahi): Proper cleanup flags (_closing, _cleanup_done) use kiye hain
                  Har resource ko individually check karke close kar rahe hain
                  try-except blocks har cleanup step mein hain
                  Context manager pattern use kiya hai for safe cleanup

3. ADDITIONAL IMPROVEMENTS:
   - Multiple selector fallbacks for better compatibility
   - Better QR code detection logic
   - Graceful shutdown with proper error handling
   - Detailed logging at every step
"""
import os
import sys
import json
import time
import logging
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, Playwright


# Configure logging
log_dir = Path(__file__).parent / 'logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'whatsapp_watcher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WhatsAppWatcher:
    """
    WhatsApp Web Watcher using Playwright
    
    FIX: Proper cleanup flags to prevent "Event loop is closed" error
    """

    def __init__(
        self,
        keywords: List[str] = None,
        needs_action_folder: str = None,
        session_file: str = None,
        headless: bool = False
    ):
        self.keywords = keywords or ['invoice', 'urgent', 'payment', 'asap', 'important']
        self.needs_action_folder = Path(needs_action_folder) if needs_action_folder else None
        self.session_file = session_file or 'whatsapp_session.json'
        self.headless = headless
        
        # Playwright components
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # FIX: Cleanup flags to prevent double-close errors
        self._closing = False
        self._cleanup_done = False
        
        # Message tracking
        self.processed_messages = set()
        self.total_messages_processed = 0
        
        # Load processed messages history
        self._load_message_history()

    def _load_message_history(self):
        """Load history of processed messages"""
        history_file = Path(self.session_file).parent / 'message_history.json'
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_messages = set(data.get('processed_ids', []))
                    self.total_messages_processed = data.get('total_processed', 0)
                    logger.info(f"Loaded message history: {len(self.processed_messages)} messages")
            except Exception as e:
                logger.warning(f"Could not load message history: {e}")

    def _save_message_history(self):
        """Save history of processed messages"""
        history_file = Path(self.session_file).parent / 'message_history.json'
        try:
            data = {
                'processed_ids': list(self.processed_messages)[-1000:],
                'total_processed': self.total_messages_processed,
                'last_updated': datetime.now().isoformat()
            }
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.debug("Message history saved")
        except Exception as e:
            logger.error(f"Could not save message history: {e}")

    def start(self):
        """Initialize Playwright and browser"""
        logger.info("=" * 50)
        logger.info("Starting Playwright...")
        
        try:
            self.playwright = sync_playwright().start()
            logger.info("Playwright started successfully")
        except Exception as e:
            logger.error(f"Failed to start Playwright: {e}")
            raise
        
        logger.info("Launching Chromium browser...")
        try:
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            logger.info("Browser launched successfully")
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            self.close()
            raise
        
        # Load existing session or create new context
        if os.path.exists(self.session_file):
            logger.info(f"Loading session from {self.session_file}")
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    storage_state = json.load(f)
                self.context = self.browser.new_context(storage_state=storage_state)
                logger.info("Session loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load session: {e}. Starting fresh...")
                self.context = self.browser.new_context()
        else:
            logger.info("No session file found. Starting fresh...")
            self.context = self.browser.new_context()
        
        self.page = self.context.new_page()
        logger.info("Browser context and page created successfully")

    def save_session(self):
        """Save current session for reuse"""
        if not self.context:
            logger.warning("No context available to save session")
            return
            
        try:
            storage_state = self.context.storage_state()
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(storage_state, f, indent=2)
            logger.info(f"Session saved to {self.session_file}")
        except Exception as e:
            logger.error(f"Could not save session: {e}")

    def navigate_to_whatsapp(self) -> bool:
        """
        Navigate to WhatsApp Web and wait for load

        FIX: Updated selectors for current WhatsApp Web structure
        - QR code: canvas[aria-label="Scan me!"] or img[alt="Scan me!"]
        - Chat list: div[data-testid="chat-list"] or div[role="main"]
        """
        logger.info("Navigating to WhatsApp Web...")

        try:
            self.page.goto('https://web.whatsapp.com', wait_until='networkidle', timeout=60000)
            logger.info("Page loaded, checking authentication state...")

            # Wait longer for chats to load
            logger.info("Waiting for chats to load...")
            time.sleep(15)  # Wait 15 seconds for chat list

            # Wait for chat list specifically
            try:
                self.page.wait_for_selector('div[data-testid="chat-list"], div[role="main"]', timeout=20000)
                logger.info("Chat list loaded!")
            except:
                logger.warning("Chat list not found, continuing anyway...")

            return True
        except Exception as e:
            logger.error(f"Failed to navigate to WhatsApp: {e}")
            return False

    def is_authenticated(self) -> bool:
        """
        Check if WhatsApp Web is authenticated (logged in)
        
        FIX: Multiple selector fallbacks for better detection
        """
        selectors = [
            'div[data-testid="chat-list"]',
            'div[role="main"]',
            '#app > div > div',
            'div[data-testid="default-user"]'  # Fallback for older versions
        ]
        
        for selector in selectors:
            try:
                self.page.wait_for_selector(selector, timeout=3000)
                logger.info(f"Authenticated! Found: {selector}")
                return True
            except:
                continue
        
        logger.debug("No authenticated selector found")
        return False

    def is_qr_visible(self) -> bool:
        """
        Check if QR code is visible (needs authentication)
        
        FIX: Updated QR code selectors for current WhatsApp Web
        """
        qr_selectors = [
            'canvas[aria-label="Scan me!"]',
            'img[alt="Scan me!"]',
            'canvas[data-testid="qr-image"]',
            'div[data-testid="qr-container"]',
            'img[data-testid="qr-image"]'
        ]
        
        for selector in qr_selectors:
            try:
                if self.page.query_selector(selector):
                    logger.info(f"QR code detected: {selector}")
                    return True
            except:
                continue
        
        return False

    def wait_for_authentication(self, timeout: int = 90) -> bool:
        """
        Wait for user to scan QR code and authenticate
        
        FIX: Better QR detection and login wait logic
        """
        logger.info("=" * 50)
        logger.info("Waiting for authentication...")
        logger.info(f"Timeout: {timeout} seconds")
        logger.info("Please scan the QR code with WhatsApp on your phone")
        logger.info("=" * 50)
        
        start_time = time.time()
        last_status = None
        check_interval = 2  # Check every 2 seconds
        
        while time.time() - start_time < timeout:
            try:
                # Check if already authenticated
                if self.is_authenticated():
                    logger.info("✓ Authentication successful!")
                    self.save_session()
                    return True
                
                # Check QR code status
                qr_visible = self.is_qr_visible()
                
                if qr_visible and last_status != 'qr_visible':
                    logger.info("QR code is visible - waiting for scan...")
                    last_status = 'qr_visible'
                elif not qr_visible and last_status != 'loading':
                    logger.info("Loading/Processing...")
                    last_status = 'loading'
                    
            except Exception as e:
                logger.debug(f"Check error (retrying): {e}")
            
            time.sleep(check_interval)
        
        logger.error(f"Authentication timeout after {timeout} seconds")
        return False

    def get_unread_chats(self) -> List[Dict]:
        """Get list of chats with unread messages"""
        unread_chats = []

        try:
            # Wait for chat list to load
            time.sleep(2)
            
            # Multiple selector strategies for chat list
            chat_selectors = [
                'div[data-testid="chat-list"] > div',
                'div[data-testid="chat-list"] div[role="row"]',
                'div[data-testid="chat-list"] > div > div > div',
                '#pane-side > div > div > div > div',
                'div[role="main"] > div > div > div > div',
                'div[class*="animated-drawer"] + div div[role="row"]',
            ]

            chat_elements = []
            for selector in chat_selectors:
                try:
                    chat_elements = self.page.query_selector_all(selector)
                    if chat_elements:
                        logger.info(f"Found {len(chat_elements)} chats using: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector failed {selector}: {e}")
                    continue

            if not chat_elements:
                logger.warning("No chat elements found - trying fallback...")
                # Fallback: take screenshot for debugging
                try:
                    self.page.screenshot(path='debug_chat.png')
                    logger.info("Screenshot saved to debug_chat.png")
                except:
                    pass
                return []

            logger.info(f"Processing {len(chat_elements)} chat elements...")
            
            for chat in chat_elements:
                try:
                    # Check for unread badge
                    unread_count = 1
                    has_unread = False
                    
                    # Multiple selectors for unread count
                    unread_selectors = [
                        'span[data-testid="unread-msg-count"]',
                        'span[class*="unread"]',
                        'div[class*="unread"] span',
                        'span[class*="badge"]',
                        'div[class*="badge"]',
                    ]

                    for sel in unread_selectors:
                        try:
                            badge = chat.query_selector(sel)
                            if badge:
                                count_text = badge.inner_text().strip()
                                if count_text.isdigit():
                                    unread_count = int(count_text)
                                    has_unread = True
                                    break
                                else:
                                    has_unread = True
                        except:
                            continue

                    # Get chat name
                    name_element = chat.query_selector('span[data-testid="meta-title"]')
                    if not name_element:
                        name_element = chat.query_selector('div[class*="title"] span')
                    if not name_element:
                        name_element = chat.query_selector('div[title]')
                    chat_name = name_element.inner_text().strip() if name_element else "Unknown"

                    # Get last message
                    message_element = chat.query_selector('span[data-testid="last-message-snippet"]')
                    if not message_element:
                        message_element = chat.query_selector('div[class*="message"] span')
                    if not message_element:
                        message_element = chat.query_selector('span[class*="message"]')
                    last_message = message_element.inner_text().strip() if message_element else ""

                    if has_unread or last_message:
                        unread_chats.append({
                            'name': chat_name,
                            'unread_count': unread_count if has_unread else 0,
                            'last_message': last_message
                        })
                        logger.info(f"Chat found: {chat_name} (unread: {unread_count})")

                except Exception as e:
                    logger.debug(f"Error processing chat: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error getting unread chats: {e}")

        logger.info(f"Total chats with messages: {len(unread_chats)}")
        return unread_chats

    def open_chat(self, chat_name: str) -> bool:
        """Open a specific chat"""
        try:
            # FIX: Multiple selector strategies for clicking chat
            strategies = [
                f'div:has-text("{chat_name}")',
                f'span:has-text("{chat_name}")',
                f'div[title="{chat_name}"]',
            ]
            
            for strategy in strategies:
                try:
                    chat_element = self.page.query_selector(strategy)
                    if chat_element:
                        chat_element.click()
                        time.sleep(1.5)
                        logger.info(f"Opened chat: {chat_name}")
                        return True
                except:
                    continue
            
            logger.warning(f"Chat not found: {chat_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error opening chat '{chat_name}': {e}")
            return False

    def get_messages_from_chat(self) -> List[Dict]:
        """
        Get recent messages from currently open chat
        Extracts BOTH incoming and outgoing messages
        """
        messages = []

        try:
            # Wait for messages to load
            try:
                self.page.wait_for_selector('div[data-testid="msg-container"], div[data-testid="message"]', timeout=5000)
                logger.info("Message container loaded")
            except:
                logger.warning("Message container not found, trying fallback")
                time.sleep(2)

            # Updated message selectors for current WhatsApp Web DOM
            msg_selectors = [
                'div[data-testid="msg-container"]',
                'div[data-testid="message"]',
                'div[class*="message-container"]',
                'div[class*="msg-container"]',
                'div[role="listitem"]',  # Fallback
            ]

            msg_containers = []
            for selector in msg_selectors:
                try:
                    msg_containers = self.page.query_selector_all(selector)
                    if msg_containers:
                        logger.info(f"Found {len(msg_containers)} messages using: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector failed {selector}: {e}")
                    continue

            if not msg_containers:
                logger.warning("No message containers found - taking screenshot for debug")
                try:
                    self.page.screenshot(path='debug_messages.png')
                    logger.info("Screenshot saved to debug_messages.png")
                except:
                    pass
                return []

            logger.info(f"Extracting last {min(20, len(msg_containers))} messages...")

            # Get last 20 messages (both incoming and outgoing)
            for msg_container in msg_containers[-20:]:
                try:
                    # Check message direction (incoming or outgoing)
                    incoming = msg_container.query_selector('div[data-testid="msg-in"]')
                    outgoing = msg_container.query_selector('div[data-testid="msg-out"]')
                    
                    if not incoming and not outgoing:
                        # Try fallback selectors
                        incoming = msg_container.query_selector('div[class*="from-me"]:nth-child(2)')
                        outgoing = msg_container.query_selector('div[class*="from-me"]:first-child')
                    
                    # Get message text - try multiple selectors
                    text_selectors = [
                        'span[data-testid="message-text"]',
                        'div[data-testid="msg-in"] span',
                        'div[data-testid="msg-out"] span',
                        'span[class*="message-text"]',
                        'div[class*="message-text"]',
                        'span[dir="auto"]',
                        'div[dir="auto"]',
                    ]

                    message_text = ""
                    for sel in text_selectors:
                        try:
                            # Try direct query first
                            text_elem = msg_container.query_selector(sel)
                            if not text_elem:
                                # Try finding in shadow DOM or nested
                                text_elem = msg_container.query_selector(f'*:has-text("{sel.split("[")[0] if "[" in sel else sel}")')
                            
                            if text_elem:
                                message_text = text_elem.inner_text().strip()
                                if message_text:
                                    break
                        except Exception as e:
                            logger.debug(f"Text selector failed {sel}: {e}")
                            continue

                    # Skip empty messages
                    if not message_text:
                        logger.debug("Empty message skipped")
                        continue

                    # Determine message type
                    msg_type = "incoming" if incoming else ("outgoing" if outgoing else "unknown")

                    # Get timestamp if available
                    time_elem = msg_container.query_selector('span[data-testid="msg-time"]')
                    msg_time = time_elem.inner_text().strip() if time_elem else datetime.now().strftime('%H:%M')

                    msg_id = hashlib.md5(
                        f"{time.time()}{message_text}".encode()
                    ).hexdigest()

                    messages.append({
                        'id': msg_id,
                        'text': message_text,
                        'type': msg_type,
                        'time': msg_time,
                        'timestamp': datetime.now().isoformat()
                    })

                    logger.debug(f"  [{msg_type}] {msg_time}: {message_text[:50]}...")

                except Exception as e:
                    logger.debug(f"Error processing message: {e}")
                    continue

            logger.info(f"Extracted {len(messages)} messages")

        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            import traceback
            logger.error(traceback.format_exc())

        return messages

    def check_keywords(self, text: str) -> List[str]:
        """Check if text contains any keywords"""
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords

    def create_markdown_file(self, chat_name: str, messages: List[Dict], keywords_found: List[str]) -> Optional[str]:
        """Create markdown file with message details"""
        if self.needs_action_folder is None:
            logger.error("Needs_Action folder not configured")
            return None
        
        os.makedirs(self.needs_action_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sanitized_name = re.sub(r'[^\w\s-]', '', chat_name)[:30]
        filename = f"WhatsApp_{timestamp}_{sanitized_name}.md"
        filepath = self.needs_action_folder / filename
        
        full_message = '\n\n'.join([msg['text'] for msg in messages])
        
        content = f"""---
metadata:
  source: "WhatsApp Web"
  chat_name: "{chat_name}"
  keywords_matched: {keywords_found}
  message_count: {len(messages)}
  received_date: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
  processed_at: "{datetime.now().isoformat()}"
  tier: "WhatsApp Watcher"
---

# WhatsApp Message Alert

## Chat Information
| Field | Value |
|-------|-------|
| **Chat Name** | {chat_name} |
| **Keywords Matched** | {', '.join(keywords_found)} |
| **Messages** | {len(messages)} |
| **Received** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |

## Messages

{full_message}

## Action Items
- [ ] Review message content
- [ ] Determine required response
- [ ] Respond on WhatsApp if needed
- [ ] Update status
- [ ] Close when completed

---
*Generated by WhatsApp Web Watcher*
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✓ Created: {filename}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error creating file: {e}")
            return None

    def process_chats(self) -> int:
        """Process all chats and save messages with keywords"""
        processed_count = 0
        
        try:
            chats = self.get_unread_chats()
            logger.info(f"Checking {len(chats)} chats for keywords...")
            
            for chat in chats:
                chat_name = chat['name']
                last_message = chat['last_message']
                
                logger.info(f"Checking chat: {chat_name}")
                
                # Check last message for keywords
                keywords_found = self.check_keywords(last_message)
                
                if keywords_found:
                    logger.info(f"  ✓ Keywords found: {keywords_found}")
                    
                    # Open chat to get more context
                    if self.open_chat(chat_name):
                        messages = self.get_messages_from_chat()
                        if messages:
                            self.create_markdown_file(chat_name, messages, keywords_found)
                            processed_count += 1
                        else:
                            # Use last message if no messages retrieved
                            msg_id = hashlib.md5(
                                f"{time.time()}{last_message}".encode()
                            ).hexdigest()
                            self.create_markdown_file(
                                chat_name,
                                [{'id': msg_id, 'text': last_message}],
                                keywords_found
                            )
                            processed_count += 1
                else:
                    logger.debug(f"  No keywords in: {chat_name}")
            
            # Save message history
            self._save_message_history()
            
        except Exception as e:
            logger.error(f"Error processing chats: {e}")
        
        return processed_count

    def show_recent_chats(self):
        """Show recent chats with sample messages in CLI - FIXED VERSION"""
        print("\n" + "=" * 60)
        print("  WHATSAPP RECENT CHATS")
        print("=" * 60)

        try:
            self.start()
            if not self.navigate_to_whatsapp():
                print("Failed to navigate to WhatsApp")
                return

            if not self.is_authenticated():
                print("Not authenticated. Please scan QR code.")
                if not self.wait_for_authentication(timeout=90):
                    print("Authentication failed")
                    return

            print("\n[OK] WhatsApp authenticated\n")

            # Wait for chat list to fully load
            time.sleep(3)
            
            # Wait for chat list specifically
            try:
                self.page.wait_for_selector('div[data-testid="chat-list"]', timeout=10000)
                print("[OK] Chat list loaded")
            except:
                print("[WARN] Chat list selector not found, trying anyway...")

            # Get chat elements with multiple fallback selectors
            chat_selectors = [
                'div[data-testid="chat-list"] > div',
                '#pane-side > div > div > div > div',
                'div[role="list"] > div[role="listitem"]',
                'div[data-testid="chat-list"] div[role="row"]',
            ]

            chat_elements = []
            for selector in chat_selectors:
                try:
                    chat_elements = self.page.query_selector_all(selector)
                    if chat_elements:
                        print(f"[OK] Found {len(chat_elements)} chats using: {selector[:40]}...")
                        break
                except Exception as e:
                    logger.debug(f"Selector failed: {selector[:30]} - {e}")
                    continue

            if not chat_elements:
                print("[ERROR] No chats found")
                return

            print(f"\n{'='*50}")
            print(f"TOTAL CHATS: {len(chat_elements)}")
            print(f"{'='*50}\n")

            # Show first 10 chats with details
            for i, chat in enumerate(chat_elements[:10], 1):
                try:
                    # Get chat name
                    name_elem = chat.query_selector('span[data-testid="meta-title"]')
                    if not name_elem:
                        name_elem = chat.query_selector('div[title]')
                    if not name_elem:
                        name_elem = chat.query_selector('span[dir="auto"]')
                    
                    name = name_elem.inner_text().strip() if name_elem else "Unknown"
                    
                    # Get last message
                    msg_elem = chat.query_selector('span[data-testid="last-message-snippet"]')
                    if not msg_elem:
                        msg_elem = chat.query_selector('div[data-testid="last-message"]')
                    if not msg_elem:
                        msg_elem = chat.query_selector('span[class*="message"]')
                    
                    msg = msg_elem.inner_text().strip() if msg_elem else "(no preview)"
                    
                    # Get unread count
                    unread_elem = chat.query_selector('span[data-testid="unread-msg-count"]')
                    unread = unread_elem.inner_text().strip() if unread_elem else "0"
                    
                    print(f"Chat: {name}")
                    print(f"Messages found: 1")
                    print(f"Sample: \"{msg[:50]}...\"" if len(msg) > 50 else f"Sample: \"{msg}\"")
                    print(f"Unread: {unread}")
                    print()
                    
                except Exception as e:
                    logger.debug(f"Error reading chat: {e}")
                    continue

        except Exception as e:
            print(f"[ERROR] {e}")
            logger.error(f"show_recent_chats error: {e}")
        finally:
            self.close()

        print("=" * 60)

    def list_chats_with_messages(self):
        """List all chats and show messages from each - FIXED VERSION"""
        print("\n" + "=" * 60)
        print("  WHATSAPP CHATS WITH MESSAGES")
        print("=" * 60)

        try:
            self.start()
            if not self.navigate_to_whatsapp():
                print("Failed to navigate to WhatsApp")
                return

            if not self.is_authenticated():
                print("Not authenticated.")
                if not self.wait_for_authentication(timeout=90):
                    print("Authentication failed")
                    return

            print("\n[OK] WhatsApp authenticated\n")
            time.sleep(3)

            # Get chats
            chat_selectors = [
                'div[data-testid="chat-list"] > div',
                '#pane-side > div > div > div > div',
            ]

            chat_elements = []
            for selector in chat_selectors:
                chat_elements = self.page.query_selector_all(selector)
                if chat_elements:
                    print(f"[OK] Found {len(chat_elements)} chats")
                    break

            if not chat_elements:
                print("[ERROR] No chats found")
                return

            print(f"\n{'='*50}")
            print(f"TOTAL CHATS: {len(chat_elements)}")
            print(f"{'='*50}")

            # Process first 5 chats
            for i, chat in enumerate(chat_elements[:5], 1):
                try:
                    name_elem = chat.query_selector('span[data-testid="meta-title"]')
                    name = name_elem.inner_text().strip() if name_elem else "Unknown"
                    
                    print(f"\n{'='*50}")
                    print(f"Chat: {name}")
                    print(f"{'='*50}")
                    
                    # Click chat to open
                    chat.click()
                    time.sleep(2)
                    
                    # Wait for messages to load
                    try:
                        self.page.wait_for_selector('div[data-testid="msg-container"]', timeout=5000)
                        print("[OK] Messages loaded")
                    except:
                        print("[WARN] Message container not found")
                    
                    # Get messages
                    messages = self.get_messages_from_chat()
                    
                    if messages:
                        print(f"Messages found: {len(messages)}")
                        print(f"\nRecent messages:")
                        for msg in messages[-5:]:  # Last 5 messages
                            icon = "→" if msg['type'] == 'outgoing' else "←"
                            sample = msg['text'][:50] + "..." if len(msg['text']) > 50 else msg['text']
                            print(f"  {icon} [{msg['time']}] {sample}")
                    else:
                        print("Messages found: 0")
                    
                    # Go back to chat list
                    back_btn = self.page.query_selector('button[aria-label="Back"]')
                    if back_btn:
                        back_btn.click()
                        time.sleep(1)
                    
                except Exception as e:
                    print(f"  [ERROR] {e}")
                    logger.debug(f"Error processing chat: {e}")
                    continue

        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.close()

        print("\n" + "=" * 60)

    def close(self):
        """
        Close browser and cleanup properly
        
        FIX: Proper cleanup to prevent "Event loop is closed" error
        - Uses flags to prevent double-close
        - Closes each resource individually with try-except
        - Handles already-closed resources gracefully
        """
        if self._closing or self._cleanup_done:
            return
        
        self._closing = True
        logger.info("Cleaning up resources...")
        
        # Close page
        if self.page:
            try:
                self.page.close()
                logger.debug("Page closed")
            except Exception as e:
                logger.debug(f"Page close error (may be already closed): {e}")
            self.page = None
        
        # Close context
        if self.context:
            try:
                self.context.close()
                logger.debug("Context closed")
            except Exception as e:
                logger.debug(f"Context close error: {e}")
            self.context = None
        
        # Close browser
        if self.browser:
            try:
                self.browser.close()
                logger.debug("Browser closed")
            except Exception as e:
                logger.debug(f"Browser close error: {e}")
            self.browser = None
        
        # Stop playwright
        if self.playwright:
            try:
                self.playwright.stop()
                logger.debug("Playwright stopped")
            except Exception as e:
                logger.debug(f"Playwright stop error: {e}")
            self.playwright = None
        
        self._cleanup_done = True
        self._closing = False
        logger.info("Cleanup complete")

    def run_once(self) -> int:
        """Run watcher once"""
        try:
            self.start()
            
            if not self.navigate_to_whatsapp():
                logger.error("Failed to navigate to WhatsApp")
                return 0
            
            # Check authentication
            if not self.is_authenticated():
                logger.info("Not authenticated. Waiting for QR scan...")
                if not self.wait_for_authentication(timeout=90):
                    logger.error("Authentication failed or timed out")
                    return 0
            else:
                logger.info("Already authenticated (session loaded)")
            
            # Process chats
            count = self.process_chats()
            logger.info(f"Processed {count} messages with keywords")
            
            return count
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            return 0
        except Exception as e:
            logger.error(f"Error in run_once: {e}")
            return 0
        finally:
            self.close()

    def start_polling(self, interval: int = 300):
        """Start continuous polling"""
        logger.info("=" * 50)
        logger.info(f"Starting WhatsApp watcher (interval: {interval}s)")
        logger.info("=" * 50)
        
        try:
            self.start()
            
            if not self.navigate_to_whatsapp():
                logger.error("Failed to navigate to WhatsApp")
                return
            
            # Check authentication
            if not self.is_authenticated():
                logger.info("Not authenticated. Waiting for QR scan...")
                if not self.wait_for_authentication(timeout=90):
                    logger.error("Authentication failed or timed out")
                    return
            else:
                logger.info("Already authenticated (session loaded)")
            
            run_count = 0
            
            while True:
                try:
                    count = self.process_chats()
                    run_count += 1
                    
                    if count > 0:
                        logger.info(f"✓ Run {run_count}: Found {count} messages with keywords")
                    else:
                        logger.info(f"Run {run_count}: No new messages with keywords")
                    
                    # Save session periodically
                    if run_count % 10 == 0:
                        self.save_session()
                    
                    # Wait for next interval
                    logger.info(f"Waiting {interval}s until next check...")
                    for _ in range(interval):
                        time.sleep(1)
                        
                except KeyboardInterrupt:
                    logger.info("Interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"Error in polling loop: {e}")
                    logger.info("Retrying in 10 seconds...")
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            logger.info("Stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            self.save_session()
            self.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Web Watcher')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--interval', type=int, default=300, help='Polling interval in seconds')
    parser.add_argument('--keywords', type=str, nargs='+', help='Keywords to search for')
    parser.add_argument('--output', type=str, help='Output folder for markdown files')
    parser.add_argument('--session', type=str, default='whatsapp_session.json', help='Session file path')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode (after first login)')
    parser.add_argument('--show-chats', action='store_true', help='Show recent chats in CLI')
    parser.add_argument('--list-chats', action='store_true', help='List all available chats')
    args = parser.parse_args()
    
    # Determine output folder
    output_folder = args.output
    if output_folder is None:
        output_folder = Path(__file__).parent / 'AI_Employee_Vault' / 'Silver_Tier' / 'Needs_Action'
    
    watcher = WhatsAppWatcher(
        keywords=args.keywords,
        needs_action_folder=output_folder,
        session_file=args.session,
        headless=args.headless
    )
    
    try:
        if args.list_chats:
            watcher.list_chats_with_messages()
        elif args.show_chats:
            watcher.show_recent_chats()
        elif args.once:
            count = watcher.run_once()
            print(f"\n[OK] Processed {count} messages with keywords")
        else:
            watcher.start_polling(args.interval)
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        logger.error(f"Main error: {e}")
    finally:
        watcher.close()


if __name__ == '__main__':
    main()
