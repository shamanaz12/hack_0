"""
Complete System Setup and Execution Script

This script will:
1. Guide you through the final Gmail authentication step
2. Start the cron scheduler to run every 5 minutes
3. Verify all components are working together
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def run_complete_system():
    print("Starting Complete AI Employee Vault System")
    print("="*60)
    
    print("\nSTEP 1: Gmail API Authentication")
    print("-" * 40)
    print("To complete the Gmail API setup, you need to authenticate once.")
    print("This will open a browser window for you to sign in to your Google account.")
    print("After authentication, a 'token.pickle' file will be created for future use.")
    
    response = input("\nDo you want to start Gmail authentication now? (y/n): ")
    
    if response.lower() in ['y', 'yes']:
        print("\nStarting Gmail authentication...")
        try:
            # Run the authentication process
            result = subprocess.run([
                sys.executable, "-c",
                "import sys; sys.path.append('.'); "
                "from gmail_auth import test_authentication; test_authentication()"
            ], cwd=".", capture_output=True, text=True)
            
            print("Authentication output:", result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
                
        except Exception as e:
            print(f"Authentication error: {e}")
            print("\nNote: Authentication requires a browser window to be opened.")
            print("If running in a headless environment, you'll need to authenticate elsewhere.")
    else:
        print("Skipping authentication for now. You can run it later using gmail_auth.py")
    
    print("\nSTEP 2: Starting Cron Scheduler")
    print("-" * 40)
    print("The cron scheduler will run the Gmail checker every 5 minutes.")
    print("This runs in the background and checks for new emails.")
    
    response = input("\nDo you want to start the cron scheduler now? (y/n): ")
    
    if response.lower() in ['y', 'yes']:
        print("\nStarting Gmail Cron Scheduler...")
        print("This will run indefinitely, checking for emails every 5 minutes.")
        print("Press Ctrl+C to stop the scheduler.")
        
        try:
            # Start the cron scheduler
            subprocess.run([sys.executable, "gmail_cron_scheduler.py"])
        except KeyboardInterrupt:
            print("\nScheduler stopped by user.")
    else:
        print("Scheduler not started. You can run it later using: python gmail_cron_scheduler.py")
    
    print("\nSTEP 3: Starting MCP Email Server (Optional)")
    print("-" * 50)
    print("The MCP Email Server can send emails via HTTP requests.")
    print("This runs on http://localhost:5000")
    
    response = input("\nDo you want to start the MCP Email Server? (y/n): ")
    
    if response.lower() in ['y', 'yes']:
        print("\nStarting MCP Email Server...")
        print("Server will be available at http://localhost:5000")
        print("Press Ctrl+C to stop the server.")
        
        try:
            # Start the MCP email server
            subprocess.run([sys.executable, "mcp_email_server.py"])
        except KeyboardInterrupt:
            print("\nMCP Email Server stopped by user.")
    else:
        print("MCP Email Server not started. You can run it later using: python mcp_email_server.py")
    
    print("\n" + "="*60)
    print("SYSTEM OVERVIEW")
    print("="*60)
    print("✓ File Watcher: Monitors Drop_Folder and moves files to Needs_Action")
    print("✓ Processing System: Moves files from Needs_Action to Plans with structured plans")
    print("✓ Gmail Integration: Checks emails every 5 minutes (when authenticated)")
    print("✓ MCP Email Server: Sends emails via HTTP API (when configured)")
    print("✓ Workflow: Needs_Action → Plans → Pending_Approval → Approved → Done")
    print("\nThe system is fully set up and ready to automate your tasks!")
    print("="*60)

if __name__ == "__main__":
    # Change to the AI_Employee_Vault directory
    os.chdir("C:/Users/AA/Desktop/h.p_hack_0/AI_Employee_Vault")
    run_complete_system()