"""
WhatsApp QR Login - Opens WhatsApp Web for QR code scanning.
Run this once to scan QR code with your phone.
"""

import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from session_manager import SessionManager


def main():
    print("\n" + "=" * 60)
    print("  WHATSAPP QR CODE LOGIN")
    print("=" * 60)
    print("\nPhone: +923202191812")
    print("\nInstructions:")
    print("1. Open WhatsApp on your phone")
    print("2. Go to Settings > Linked Devices")
    print("3. Tap 'Link a Device'")
    print("4. Scan the QR code shown in the browser")
    print("\nWaiting for QR code...")
    print("=" * 60 + "\n")
    
    # Create session manager with visible browser
    session = SessionManager(headless=False)
    session.start_browser()
    
    try:
        # Login to WhatsApp (will show QR code)
        success = session.login_whatsapp()
        
        if success:
            print("\n" + "=" * 60)
            print("  WHATSAPP LOGIN SUCCESSFUL!")
            print("=" * 60)
            print(f"\nSession saved to: sessions/whatsapp_auth.json")
            print("You can now run automation in headless mode.")
        else:
            print("\n" + "=" * 60)
            print("  QR CODE NOT SCANNED")
            print("=" * 60)
            print("\nPlease run again and scan the QR code.")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        session.close()
    
    print("\nDone.\n")


if __name__ == "__main__":
    main()
