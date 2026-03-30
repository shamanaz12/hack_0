"""
Gmail API Setup Helper
Guides user through the Gmail API setup process
"""

import os
import sys
import json
import webbrowser
from pathlib import Path

def check_credentials_file():
    """Check if credentials.json exists"""
    creds_path = Path("credentials.json")
    return creds_path.exists()

def check_token_file():
    """Check if token.json exists"""
    token_path = Path("token.json")
    return token_path.exists()

def print_status():
    """Print current setup status"""
    print("Gmail API Setup Status:")
    print("="*50)
    
    # Check if credentials exist
    creds_exist = check_credentials_file()
    print(f"Credentials file (credentials.json): {'[FOUND]' if creds_exist else '[MISSING]'}")
    
    # Check if token exists
    token_exists = check_token_file()
    print(f"Token file (token.json): {'[FOUND]' if token_exists else '[MISSING]'}")
    
    # Overall status
    if creds_exist:
        if token_exists:
            print("Overall status: [READY] Ready to use Gmail API")
        else:
            print("Overall status: [NEEDS_AUTH] Credentials ready, need first-time authorization")
    else:
        print("Overall status: [NEEDS_SETUP] Need to set up credentials first")
    
    print("="*50)

def guide_user_through_setup():
    """Guide user through the setup process"""
    print("\nSetting up Gmail API access:")
    print("1. Visit https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Gmail API")
    print("4. Create OAuth 2.0 credentials for a Desktop application")
    print("5. Download the credentials JSON file")
    print("6. Rename it to 'credentials.json' and place it in this folder")
    print("7. Run this script again")
    
    # Ask if user wants to open the browser
    response = input("\nWould you like to open the Google Cloud Console in your browser? (y/n): ")
    if response.lower() in ['y', 'yes']:
        webbrowser.open("https://console.cloud.google.com/")

def main():
    print("Gmail API Setup Helper")
    print("="*30)
    
    # Show current status
    print_status()
    
    # Check if setup is complete
    creds_exist = check_credentials_file()
    
    if not creds_exist:
        guide_user_through_setup()
    else:
        print("\nCredentials file found!")
        print("You can now run the Gmail watcher.")
        print("On first run, you'll need to authorize the application through your browser.")
        
        response = input("\nWould you like to run the Gmail watcher now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            # Try to run the gmail poller
            try:
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                from gmail_poller import run_watcher
                print("\nStarting Gmail Watcher...")
                run_watcher()
            except ImportError as e:
                print(f"Error importing gmail_poller: {e}")
                print("Make sure gmail_poller.py exists in this directory")
            except Exception as e:
                print(f"Error running Gmail Watcher: {e}")

if __name__ == "__main__":
    main()