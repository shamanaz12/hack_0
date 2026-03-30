"""
Final verification script for the complete system
"""
import os
import sys
from pathlib import Path

def check_system_setup():
    print("Verifying complete system setup...")
    print("="*50)
    
    # Check for credentials file
    creds_path = Path("credentials.json")
    print(f"1. Credentials file: {'[FOUND]' if creds_path.exists() else '[MISSING]'}")
    
    # Check for required Python modules
    try:
        import schedule
        print("2. Schedule module: [AVAILABLE]")
    except ImportError:
        print("2. Schedule module: [MISSING]")
    
    try:
        import google.auth
        print("3. Google Auth module: [AVAILABLE]")
    except ImportError:
        print("3. Google Auth module: [MISSING]")
    
    # Check for main scripts
    scripts = [
        "gmail_poller.py",
        "gmail_cron_scheduler.py",
        "mcp_email_server.py",
        "file_watcher.py"
    ]
    
    print("\n4. Main scripts:")
    for script in scripts:
        script_path = Path(script)
        print(f"   {script}: {'[FOUND]' if script_path.exists() else '[MISSING]'}")
    
    # Check for folder structure
    folders = [
        "Needs_Action",
        "Plans",
        "Approved",
        "Done",
        "Drop_Folder"
    ]
    
    print("\n5. Required folders:")
    for folder in folders:
        folder_path = Path(folder)
        print(f"   {folder}: {'[EXISTS]' if folder_path.exists() else '[MISSING]'}")
    
    print("\n" + "="*50)
    if creds_path.exists():
        print("SYSTEM READY STATUS: Most components are in place!")
        print("Next step: Run the Gmail authentication to create token.pickle")
        print("Then start the cron scheduler to run every 5 minutes")
    else:
        print("SYSTEM READY STATUS: Almost complete!")
        print("Missing: Valid credentials.json file")
        print("Action: Follow the Gmail setup guide to get credentials.json")
    
    print("="*50)

if __name__ == "__main__":
    # Change to the AI_Employee_Vault directory
    os.chdir("C:/Users/AA/Desktop/h.p_hack_0/AI_Employee_Vault")
    check_system_setup()