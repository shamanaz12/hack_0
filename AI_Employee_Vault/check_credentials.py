"""
Credentials Validation Script
Checks if all required credentials are properly configured
"""

import os
import json
from pathlib import Path

def check_credentials_json():
    """Check if credentials.json exists and is valid"""
    print("\n" + "="*50)
    print("  Checking credentials.json")
    print("="*50)
    
    cred_file = Path("credentials.json")
    
    if not cred_file.exists():
        print("  [ERROR] credentials.json not found!")
        print("  Download from: https://console.cloud.google.com/")
        return False
    
    try:
        with open(cred_file, 'r') as f:
            creds = json.load(f)
        
        # Check required fields
        required_fields = ['client_id', 'client_secret', 'project_id']
        
        if 'installed' not in creds:
            print("  [ERROR] Invalid format - 'installed' key missing!")
            return False
        
        installed = creds['installed']
        
        all_valid = True
        for field in required_fields:
            if field not in installed:
                print(f"  [ERROR] Required field '{field}' missing!")
                all_valid = False
            else:
                value = installed[field]
                if len(value) < 10:
                    print(f"  [WARNING] '{field}' looks invalid (too short)")
                else:
                    print(f"  [OK] {field}: {value[:20]}...")
        
        return all_valid
        
    except json.JSONDecodeError:
        print("  [ERROR] credentials.json is not valid JSON!")
        return False
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

def check_token_pickle():
    """Check if token.pickle exists (created after first auth)"""
    print("\n" + "="*50)
    print("  Checking token.pickle")
    print("="*50)
    
    token_file = Path("token.pickle")
    
    if token_file.exists():
        print("  [OK] token.pickle found (already authenticated)")
        return True
    else:
        print("  [INFO] token.pickle not found")
        print("  Run 'python gmail_auth.py' to authenticate")
        return False

def check_mcp_credentials():
    """Check MCP server environment variables"""
    print("\n" + "="*50)
    print("  Checking MCP Server Credentials")
    print("="*50)
    
    env_vars = {
        'SMTP_HOST': 'SMTP Host',
        'SMTP_PORT': 'SMTP Port',
        'SMTP_USERNAME': 'SMTP Username',
        'SMTP_PASSWORD': 'SMTP Password'
    }
    
    all_set = True
    for var, name in env_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'SMTP_PASSWORD':
                print(f"  [OK] {name}: {'*' * 8}")
            else:
                print(f"  [OK] {name}: {value}")
        else:
            print(f"  [WARNING] {name}: Not set")
            all_set = False
    
    if not all_set:
        print("\n  To set MCP credentials, edit:")
        print("  start_mcp_with_credentials.bat")
    
    return all_set

def check_gmail_api_enabled():
    """Try to import Gmail API libraries"""
    print("\n" + "="*50)
    print("  Checking Gmail API Libraries")
    print("="*50)
    
    try:
        from googleapiclient.discovery import build
        print("  [OK] Gmail API libraries installed")
        return True
    except ImportError:
        print("  [ERROR] Gmail API libraries not installed!")
        print("  Run: pip install -r requirements_gmail.txt")
        return False

def main():
    print("\n" + "="*60)
    print("  CREDENTIALS VALIDATION CHECKER")
    print("="*60)
    
    results = {
        'credentials.json': check_credentials_json(),
        'token.pickle': check_token_pickle(),
        'MCP Credentials': check_mcp_credentials(),
        'Gmail API Libraries': check_gmail_api_enabled()
    }
    
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    
    for check, result in results.items():
        status = "[OK]" if result else "[NEEDS ATTENTION]"
        print(f"  {status} {check}")
    
    print("="*60)
    
    # Overall status
    ok_count = sum(results.values())
    total_count = len(results)
    
    if ok_count == total_count:
        print("\n  [SUCCESS] All credentials are properly configured!")
        print("  You can now run the system.")
    else:
        print(f"\n  [WARNING] {total_count - ok_count} issue(s) found.")
        print("  Please fix the issues above before running the system.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
