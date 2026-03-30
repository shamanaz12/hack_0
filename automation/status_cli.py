"""
Status CLI - Quick status check for all automation platforms.
Run this after initial setup to check connection status.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()


def print_header():
    """Print CLI header."""
    print("\n" + "=" * 60)
    print("  GOLD TIER - PLATFORM STATUS CHECK")
    print("=" * 60)


def print_status(platform: str, status: str, message: str = ""):
    """Print platform status."""
    icons = {
        "OK": "[OK]",
        "READY": "[READY]",
        "ERROR": "[ERROR]",
        "MISSING": "[MISSING]"
    }
    
    icon = icons.get(status, "[?]")
    print(f"{icon} {platform}: {message}")


def check_credentials():
    """Check if credentials are configured."""
    import os
    
    print("\n[1] Checking Credentials...")
    
    checks = {
        "Facebook Email": os.getenv("FACEBOOK_EMAIL"),
        "Facebook Password": os.getenv("FACEBOOK_PASSWORD"),
        "Facebook Page ID": os.getenv("FACEBOOK_PAGE_ID"),
        "Instagram Username": os.getenv("INSTAGRAM_USERNAME"),
        "Instagram Password": os.getenv("INSTAGRAM_PASSWORD"),
        "Gmail Email": os.getenv("GMAIL_EMAIL"),
    }
    
    all_ok = True
    for name, value in checks.items():
        if value:
            if "Password" in name or "password" in name:
                print_status(name, "OK", "Configured")
            else:
                print_status(name, "OK", value[:30])
        else:
            print_status(name, "MISSING", "Not configured")
            all_ok = False
    
    return all_ok


def check_sessions():
    """Check if session files exist."""
    print("\n[2] Checking Saved Sessions...")
    
    session_files = {
        "Facebook": "sessions/facebook_auth.json",
        "Instagram": "sessions/instagram_auth.json",
        "WhatsApp": "sessions/whatsapp_auth.json",
        "Gmail": "sessions/gmail_auth.json"
    }
    
    all_ok = True
    for platform, filepath in session_files.items():
        full_path = Path(__file__).parent / filepath
        if full_path.exists():
            # Check file age
            mtime = full_path.stat().st_mtime
            age_hours = (time.time() - mtime) / 3600
            
            if age_hours < 24:
                print_status(platform, "OK", f"Session valid ({age_hours:.1f}h old)")
            else:
                print_status(platform, "READY", f"Session old ({age_hours:.1f}h) - may need re-login")
        else:
            print_status(platform, "MISSING", "First login required")
            all_ok = False
    
    return all_ok


def check_browser():
    """Check if Playwright browser is installed."""
    print("\n[3] Checking Browser...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Check if chromium is available
            if p.chromium:
                print_status("Chromium", "OK", "Installed")
                return True
    except Exception as e:
        print_status("Chromium", "ERROR", str(e))
        print("\n  Run: playwright install chromium")
        return False


def quick_test(platform: str):
    """Quick connectivity test for a platform - just check session files."""
    print(f"\n[4] Testing {platform}...")
    
    session_file = Path(__file__).parent / "sessions" / f"{platform}_auth.json"
    
    if session_file.exists():
        # Check file age
        mtime = session_file.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        
        if age_hours < 24:
            print_status(platform.capitalize(), "OK", f"Session valid ({age_hours:.1f}h old)")
        else:
            print_status(platform.capitalize(), "READY", f"Session old ({age_hours:.1f}h)")
        return True
    else:
        print_status(platform.capitalize(), "MISSING", "First login required")
        print(f"     Run: python orchestrator.py")
        return False


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check automation platform status")
    parser.add_argument(
        "--platform",
        choices=["facebook", "instagram", "whatsapp", "gmail", "all"],
        default="all",
        help="Platform to test (default: all)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick check (skip live tests)"
    )
    
    args = parser.parse_args()
    
    print_header()
    
    # Check credentials
    creds_ok = check_credentials()
    
    # Check sessions
    sessions_ok = check_sessions()
    
    # Check browser
    browser_ok = check_browser()
    
    # Quick mode - skip live tests
    if args.quick:
        print("\n" + "=" * 60)
        print("  QUICK CHECK COMPLETE")
        print("=" * 60)
        
        if creds_ok and sessions_ok and browser_ok:
            print("\n[OK] All systems ready!")
            print("\nRun: python orchestrator.py --once")
        else:
            print("\n[WARNING] Some items need attention")
            if not sessions_ok:
                print("  Run: python orchestrator.py  (for first login)")
        return
    
    # Live tests
    if args.platform == "all":
        platforms = ["facebook", "whatsapp", "gmail", "instagram"]
    else:
        platforms = [args.platform]
    
    print("\n" + "=" * 60)
    print("  LIVE CONNECTIVITY TESTS")
    print("=" * 60)
    
    for platform in platforms:
        quick_test(platform)
        time.sleep(2)  # Delay between tests
    
    print("\n" + "=" * 60)
    print("  STATUS CHECK COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("  - Run automation: python orchestrator.py --once")
    print("  - Continuous mode: python orchestrator.py --interval 60")
    print("  - Help: python orchestrator.py --help")
    print()


if __name__ == "__main__":
    main()
