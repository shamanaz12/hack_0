"""
Quick Status Check - All Platforms
Shows login status and session info
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from session_manager import SessionManager


def print_header():
    print("\n" + "=" * 60)
    print("  GOLD TIER - ALL PLATFORM STATUS")
    print("=" * 60)


def check_facebook():
    print("\n[1] FACEBOOK BUSINESS PAGE")
    print("-" * 50)
    print(f"    Page ID: 61578538607212")
    print(f"    URL: https://www.facebook.com/profile.php?id=61578538607212")
    
    session = SessionManager(headless=True)
    session.start_browser()
    page = session.get_page("facebook")
    
    try:
        page.goto("https://www.facebook.com/profile.php?id=61578538607212", wait_until="networkidle")
        time.sleep(3)
        
        is_logged = session.is_logged_in("facebook", page)
        
        if is_logged:
            print("    Status: [OK] LOGGED IN")
            print("    Auto Post: READY")
        else:
            print("    Status: [WARNING] NOT LOGGED IN")
            print("    Run: python facebook_page_auto.py --status")
    except Exception as e:
        print(f"    Status: [ERROR] {e}")
    
    session.close()


def check_whatsapp():
    print("\n[2] WHATSAPP")
    print("-" * 50)
    print(f"    Phone: +923202191812")
    
    session = SessionManager(headless=True)
    session.start_browser()
    page = session.get_page("whatsapp")
    
    try:
        page.goto("https://web.whatsapp.com/", wait_until="networkidle")
        time.sleep(5)
        
        is_logged = session.is_logged_in("whatsapp", page)
        
        if is_logged:
            print("    Status: [OK] LOGGED IN")
            print("    Session: ACTIVE")
        else:
            print("    Status: [WARNING] QR SCAN REQUIRED")
            print("    Run: python whatsapp_qr_login.py")
    except Exception as e:
        print(f"    Status: [ERROR] {e}")
    
    session.close()


def check_gmail():
    print("\n[3] GMAIL")
    print("-" * 50)
    print(f"    Email: naz.sheikh.business@gmail.com")
    
    session = SessionManager(headless=True)
    session.start_browser()
    page = session.get_page("gmail")
    
    try:
        page.goto("https://mail.google.com/", wait_until="networkidle")
        time.sleep(3)
        
        is_logged = session.is_logged_in("gmail", page)
        
        if is_logged:
            print("    Status: [OK] LOGGED IN")
        else:
            print("    Status: [WARNING] NOT LOGGED IN")
    except Exception as e:
        print(f"    Status: [ERROR] {e}")
    
    session.close()


def check_instagram():
    print("\n[4] INSTAGRAM")
    print("-" * 50)
    print(f"    Username: @shamaansari5576")
    
    session = SessionManager(headless=True)
    session.start_browser()
    page = session.get_page("instagram")
    
    try:
        page.goto("https://www.instagram.com/", wait_until="networkidle")
        time.sleep(3)
        
        is_logged = session.is_logged_in("instagram", page)
        
        if is_logged:
            print("    Status: [OK] LOGGED IN")
        else:
            print("    Status: [WARNING] NOT LOGGED IN")
    except Exception as e:
        print(f"    Status: [ERROR] {e}")
    
    session.close()


def show_commands():
    print("\n" + "=" * 60)
    print("  QUICK COMMANDS")
    print("=" * 60)
    print("""
  Facebook Page Auto Post:
    python facebook_page_auto.py --post "Your message"
    python facebook_page_auto.py --get
    python facebook_page_auto.py --delete 1
    python facebook_page_auto.py --status

  WhatsApp QR Login:
    python whatsapp_qr_login.py

  Full Automation:
    python orchestrator.py --once
    python status_cli.py --quick
  """)


def main():
    print_header()
    
    check_facebook()
    check_whatsapp()
    check_gmail()
    check_instagram()
    
    show_commands()
    
    print("\n" + "=" * 60)
    print("  STATUS CHECK COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
