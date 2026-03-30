#!/usr/bin/env python3
"""
Gold Tier Configuration Script
Interactive setup for all tokens and credentials
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Colors for terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_section(text):
    print(f"\n{Colors.OKCYAN}{Colors.BOLD}--- {text} ---{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def get_input(prompt, default=None, hide=False):
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def load_current_env(env_path):
    """Load current .env values"""
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def save_env(env_path, env_vars):
    """Save environment variables to .env file"""
    with open(env_path, 'w', encoding='utf-8') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    print_success(f".env file saved: {env_path}")

def test_facebook_token(token, page_id):
    """Test Facebook access token"""
    try:
        import requests
        url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {
            'fields': 'id,name',
            'access_token': token
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return True, f"Connected to: {data.get('name', 'Unknown')}"
        else:
            return False, f"Error: {response.json().get('error', {}).get('message', 'Unknown error')}"
    except ImportError:
        return None, "Requests library not installed"
    except Exception as e:
        return False, str(e)

def test_odoo_connection(url, db, username, password):
    """Test Odoo connection"""
    try:
        import requests
        endpoint = f"{url}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": db,
                "login": username,
                "password": password
            },
            "id": 1
        }
        response = requests.post(endpoint, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("result", {}).get("uid"):
                return True, f"Authenticated as user ID: {result['result']['uid']}"
            else:
                return False, "Authentication failed"
        else:
            return False, f"HTTP Error: {response.status_code}"
    except ImportError:
        return None, "Requests library not installed"
    except Exception as e:
        return False, str(e)

def setup_facebook(env_vars):
    """Setup Facebook configuration"""
    print_section("FACEBOOK CONFIGURATION")
    
    page_id = env_vars.get('FACEBOOK_PAGE_ID', '956241877582673')
    print_info(f"Facebook Page ID: {page_id}")
    print_info(f"Page URL: https://www.facebook.com/{page_id}")
    
    print("\nHow to get Facebook Access Token:")
    print("1. Run: python get_facebook_token.py")
    print("2. Or visit: https://developers.facebook.com/tools/explorer/")
    print("3. Generate token with permissions: pages_show_list, pages_manage_posts")
    
    token = get_input("\nEnter Facebook Access Token", env_vars.get('FACEBOOK_PAGE_ACCESS_TOKEN', ''))
    
    if token and token != 'test_token_replace_with_actual_token':
        print_info("Testing token...")
        success, message = test_facebook_token(token, page_id)
        if success:
            print_success(message)
        elif success is False:
            print_error(message)
            print_info("You can still save it and fix later")
    
    env_vars['FACEBOOK_PAGE_ACCESS_TOKEN'] = token if token else 'test_token_replace_with_actual_token'
    env_vars['FACEBOOK_PAGE_ID'] = page_id
    env_vars['FACEBOOK_PORT'] = '3000'

def setup_instagram(env_vars):
    """Setup Instagram configuration"""
    print_section("INSTAGRAM CONFIGURATION")
    
    print_info("Instagram must be a Business Account connected to Facebook Page")
    
    ig_id = get_input(
        "Enter Instagram Business ID",
        env_vars.get('INSTAGRAM_BUSINESS_ID', 'test_instagram_id_replace_with_actual')
    )
    
    ig_token = get_input(
        "Enter Instagram Access Token (or same as Facebook)",
        env_vars.get('INSTAGRAM_ACCESS_TOKEN', 'test_token_replace_with_actual_token')
    )
    
    # If same as Facebook
    if ig_token == 'fb' or ig_token == 'facebook':
        ig_token = env_vars.get('FACEBOOK_PAGE_ACCESS_TOKEN', '')
        print_success(f"Using Facebook token for Instagram")
    
    env_vars['INSTAGRAM_BUSINESS_ID'] = ig_id if ig_id else 'test_instagram_id_replace_with_actual'
    env_vars['INSTAGRAM_ACCESS_TOKEN'] = ig_token if ig_token else 'test_token_replace_with_actual_token'
    env_vars['INSTAGRAM_PORT'] = '3001'

def setup_odoo(env_vars):
    """Setup Odoo configuration"""
    print_section("ODOO ACCOUNTING CONFIGURATION")
    
    url = get_input(
        "Enter Odoo URL",
        env_vars.get('ODOO_URL', 'http://localhost:8069')
    )
    
    db = get_input(
        "Enter Odoo Database Name",
        env_vars.get('ODOO_DB', 'odoo')
    )
    
    username = get_input(
        "Enter Odoo Username",
        env_vars.get('ODOO_USERNAME', 'admin')
    )
    
    password = get_input(
        "Enter Odoo Password",
        env_vars.get('ODOO_PASSWORD', 'admin')
    )
    
    if url and db and username and password:
        print_info("Testing Odoo connection...")
        success, message = test_odoo_connection(url, db, username, password)
        if success:
            print_success(message)
        elif success is False:
            print_error(message)
            print_info("Make sure Odoo is running at", url)
            print_info("You can still save and fix later")
    
    env_vars['ODOO_URL'] = url
    env_vars['ODOO_DB'] = db
    env_vars['ODOO_USERNAME'] = username
    env_vars['ODOO_PASSWORD'] = password

def setup_email(env_vars):
    """Setup Email configuration"""
    print_section("GMAIL EMAIL CONFIGURATION")
    
    print_info("Generate Gmail App Password:")
    print("1. Visit: https://myaccount.google.com/apppasswords")
    print("2. Select 'Mail' and 'Windows Computer'")
    print("3. Copy the 16-character password")
    
    email = get_input(
        "Enter Gmail Address",
        env_vars.get('GMAIL_EMAIL', 'naz.sheikh.business@gmail.com')
    )
    
    app_password = get_input(
        "Enter Gmail App Password (16 characters)",
        env_vars.get('GMAIL_APP_PASSWORD', 'your_gmail_app_password_here')
    )
    
    env_vars['GMAIL_EMAIL'] = email
    env_vars['GMAIL_APP_PASSWORD'] = app_password
    env_vars['GMAIL_SMTP_HOST'] = 'smtp.gmail.com'
    env_vars['GMAIL_SMTP_PORT'] = '587'

def setup_qwen(env_vars):
    """Setup Qwen AI configuration"""
    print_section("QWEN AI CONFIGURATION (For Ralph Loop)")
    
    print_info("Get API Key from: https://dashscope.console.aliyun.com/")
    
    api_key = get_input(
        "Enter Dashscope API Key",
        env_vars.get('DASHSCOPE_API_KEY', 'your_dashscope_api_key_here')
    )
    
    env_vars['DASHSCOPE_API_KEY'] = api_key if api_key else 'your_dashscope_api_key_here'
    env_vars['MODEL_NAME'] = 'qwen-plus'
    env_vars['MAX_ITERATIONS'] = '10'

def main():
    """Main configuration function"""
    print_header("GOLD TIER CONFIGURATION WIZARD")
    
    env_path = Path(__file__).parent / '.env'
    
    # Load current configuration
    print_info("Loading current configuration...")
    env_vars = load_current_env(env_path)
    
    # Menu
    while True:
        print_header("CONFIGURATION MENU")
        print("1. Facebook Configuration")
        print("2. Instagram Configuration")
        print("3. Odoo Accounting Configuration")
        print("4. Gmail Email Configuration")
        print("5. Qwen AI Configuration")
        print("6. Quick Setup (All)")
        print("7. Save & Exit")
        print("8. Exit without Saving")
        
        choice = get_input("\nSelect option (1-8)", "6")
        
        if choice == '1':
            setup_facebook(env_vars)
        elif choice == '2':
            setup_instagram(env_vars)
        elif choice == '3':
            setup_odoo(env_vars)
        elif choice == '4':
            setup_email(env_vars)
        elif choice == '5':
            setup_qwen(env_vars)
        elif choice == '6':
            print_info("Running quick setup for all services...")
            setup_facebook(env_vars)
            setup_instagram(env_vars)
            setup_odoo(env_vars)
            setup_email(env_vars)
            setup_qwen(env_vars)
        elif choice == '7':
            print_section("SAVING CONFIGURATION")
            save_env(env_path, env_vars)
            print_success("Configuration saved successfully!")
            
            print("\n" + "="*70)
            print("NEXT STEPS:")
            print("="*70)
            print("1. Install dependencies: pip install requests python-dotenv")
            print("2. Start services: python master_orchestrator.py start")
            print("3. Check status: python master_orchestrator.py status")
            print("4. Get Facebook token: python get_facebook_token.py")
            print("="*70)
            break
        elif choice == '8':
            print_info("Exiting without saving...")
            break
        else:
            print_error("Invalid option. Please select 1-8")

if __name__ == '__main__':
    main()
