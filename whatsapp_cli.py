#!/usr/bin/env python3
"""
WhatsApp CLI - Pure Terminal Based Chat Viewer
No browser automation issues - direct Playwright CLI

Usage:
  python whatsapp_cli.py --chats     # List all chats
  python whatsapp_cli.py --messages  # Show messages from each chat
"""

import sys
import time
from playwright.sync_api import sync_playwright

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_chat_info(name, last_message, unread):
    print(f"\nChat: {name}")
    print(f"Messages found: 1")
    if len(last_message) > 50:
        print(f'Sample: "{last_message[:50]}..."')
    else:
        print(f'Sample: "{last_message}"')
    print(f"Unread: {unread}")

def list_chats(page):
    """List all chats with last message"""
    print_header("WHATSAPP RECENT CHATS")
    
    # Wait for chat list
    time.sleep(3)
    
    try:
        page.wait_for_selector('div[data-testid="chat-list"]', timeout=10000)
        print("\n[OK] Chat list loaded")
    except:
        print("\n[WARN] Chat list selector not found, trying anyway...")
    
    # Get chats
    chat_selectors = [
        'div[data-testid="chat-list"] > div',
        '#pane-side > div > div > div > div',
    ]
    
    chat_elements = []
    for selector in chat_selectors:
        chat_elements = page.query_selector_all(selector)
        if chat_elements:
            print(f"[OK] Found {len(chat_elements)} chats")
            break
    
    if not chat_elements:
        print("[ERROR] No chats found")
        return 0
    
    print(f"\n{'='*50}")
    print(f"TOTAL CHATS: {len(chat_elements)}")
    print(f"{'='*50}")
    
    # Show each chat
    count = 0
    for chat in chat_elements[:10]:
        try:
            # Name
            name_elem = chat.query_selector('span[data-testid="meta-title"]')
            name = name_elem.inner_text().strip() if name_elem else "Unknown"
            
            # Last message
            msg_elem = chat.query_selector('span[data-testid="last-message-snippet"]')
            msg = msg_elem.inner_text().strip() if msg_elem else "(no preview)"
            
            # Unread
            unread_elem = chat.query_selector('span[data-testid="unread-msg-count"]')
            unread = unread_elem.inner_text().strip() if unread_elem else "0"
            
            print_chat_info(name, msg, unread)
            count += 1
            
        except Exception as e:
            print(f"[ERROR] {e}")
            continue
    
    return count

def show_messages(page):
    """Show messages from each chat"""
    print_header("WHATSAPP CHATS WITH MESSAGES")
    
    time.sleep(3)
    
    # Get chats
    chat_selectors = [
        'div[data-testid="chat-list"] > div',
        '#pane-side > div > div > div > div',
    ]
    
    chat_elements = []
    for selector in chat_selectors:
        chat_elements = page.query_selector_all(selector)
        if chat_elements:
            print(f"[OK] Found {len(chat_elements)} chats")
            break
    
    if not chat_elements:
        print("[ERROR] No chats found")
        return 0
    
    print(f"\n{'='*50}")
    print(f"TOTAL CHATS: {len(chat_elements)}")
    print(f"{'='*50}")
    
    # Process first 5 chats
    count = 0
    for i, chat in enumerate(chat_elements[:5], 1):
        try:
            name_elem = chat.query_selector('span[data-testid="meta-title"]')
            name = name_elem.inner_text().strip() if name_elem else "Unknown"
            
            print(f"\n{'='*50}")
            print(f"Chat: {name}")
            print(f"{'='*50}")
            
            # Click to open
            chat.click()
            time.sleep(2)
            
            # Wait for messages
            try:
                page.wait_for_selector('div[data-testid="msg-container"]', timeout=5000)
                print("[OK] Messages loaded")
            except:
                print("[WARN] Messages not loaded")
            
            # Get messages
            msg_containers = page.query_selector_all('div[data-testid="msg-container"]')
            
            if msg_containers:
                print(f"Messages found: {len(msg_containers)}")
                print("\nRecent messages:")
                
                for msg in msg_containers[-5:]:
                    # Check direction
                    incoming = msg.query_selector('div[data-testid="msg-in"]')
                    outgoing = msg.query_selector('div[data-testid="msg-out"]')
                    icon = "→" if outgoing else "←"
                    
                    # Get text
                    text_elem = msg.query_selector('span[data-testid="message-text"]')
                    text = text_elem.inner_text().strip() if text_elem else "(empty)"
                    
                    # Get time
                    time_elem = msg.query_selector('span[data-testid="msg-time"]')
                    msg_time = time_elem.inner_text().strip() if time_elem else "??:??"
                    
                    sample = text[:50] + "..." if len(text) > 50 else text
                    print(f"  {icon} [{msg_time}] {sample}")
                
                count += 1
            else:
                print("Messages found: 0")
            
            # Go back
            back_btn = page.query_selector('button[aria-label="Back"]')
            if back_btn:
                back_btn.click()
                time.sleep(1)
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            continue
    
    return count

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp CLI')
    parser.add_argument('--chats', action='store_true', help='List all chats')
    parser.add_argument('--messages', action='store_true', help='Show messages')
    args = parser.parse_args()
    
    print("\n[INFO] Starting WhatsApp CLI...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            page.set_default_timeout(30000)
            
            # Load session if exists
            try:
                context.storage_state(path='whatsapp_session.json')
                print("[OK] Session loaded")
            except:
                print("[INFO] No saved session")
            
            print("[INFO] Navigating to WhatsApp Web...")
            page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=60000)
            
            print("\n[WAIT] Waiting for authentication (scan QR if needed)...")
            print("Check browser window - scan QR code with WhatsApp phone app")
            print("Timeout: 60 seconds\n")
            
            # Wait for auth with better error handling
            authenticated = False
            for i in range(60):  # 60 seconds
                try:
                    if page.query_selector('div[data-testid="chat-list"]'):
                        authenticated = True
                        print("[OK] Authenticated!")
                        break
                except Exception as e:
                    if i % 10 == 0:
                        print(f"[INFO] Still waiting... ({i}s)")
                time.sleep(1)
            
            if not authenticated:
                print("\n[ERROR] Authentication timeout")
                browser.close()
                return
            
            try:
                if args.chats:
                    list_chats(page)
                elif args.messages:
                    show_messages(page)
                else:
                    list_chats(page)
            except Exception as e:
                print(f"[ERROR] {e}")
            finally:
                # Save session
                try:
                    context.storage_state(path='whatsapp_session.json')
                    print("\n[OK] Session saved")
                except:
                    pass
                browser.close()
                print("[OK] Done!")
                
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        print("\nTroubleshooting:")
        print("1. Close any open Chrome/Chromium windows")
        print("2. Try: python whatsapp_cli.py --chats")
        print("3. Make sure internet is connected")

if __name__ == '__main__':
    main()
