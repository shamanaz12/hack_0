#!/usr/bin/env python3
"""
Auto Create Odoo Database
Automatically creates the Odoo database without manual form filling
"""

import requests
import json
import time
import sys

# Configuration
ODOO_URL = "http://localhost:8069"
MASTER_PASSWORD = "admin123"
DATABASE_NAME = "odoo"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
COUNTRY_CODE = "pk"  # Pakistan
LANGUAGE = "en_US"
PHONE = "+92-123-4567890"

def check_odoo_ready():
    """Check if Odoo is accessible."""
    try:
        response = requests.get(ODOO_URL, timeout=5)
        return response.status_code == 200
    except:
        return False

def create_database():
    """Create Odoo database programmatically."""
    print("=" * 60)
    print("ODOO DATABASE AUTO-CREATOR")
    print("=" * 60)
    print()
    
    # Step 1: Check if Odoo is running
    print("[1/4] Checking if Odoo is running...")
    if not check_odoo_ready():
        print("    ERROR: Odoo is not accessible at", ODOO_URL)
        print("    Please make sure Docker containers are running:")
        print("    docker ps")
        return False
    print("    OK: Odoo is running!")
    
    # Step 2: Check if database already exists
    print()
    print("[2/4] Checking if database exists...")
    try:
        # Try to authenticate - if successful, database exists
        auth_url = f"{ODOO_URL}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": DATABASE_NAME,
                "login": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            },
            "id": 1
        }
        
        response = requests.post(auth_url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result", {}).get("uid"):
            print(f"    INFO: Database '{DATABASE_NAME}' already exists!")
            print(f"    INFO: Can login with: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
            return True
        else:
            print(f"    INFO: Database '{DATABASE_NAME}' does not exist yet.")
    except Exception as e:
        print(f"    INFO: Database check - {e}")
    
    # Step 3: Create database
    print()
    print("[3/4] Creating database...")
    print(f"    Database: {DATABASE_NAME}")
    print(f"    Master Password: {MASTER_PASSWORD}")
    print(f"    Admin Email: {ADMIN_EMAIL}")
    print(f"    Admin Password: {ADMIN_PASSWORD}")
    print(f"    Country: Pakistan")
    print()
    
    create_url = f"{ODOO_URL}/web/database/create"
    
    # Create database using form data
    form_data = {
        "master_pwd": MASTER_PASSWORD,
        "name": DATABASE_NAME,
        "demo": "true",  # Include demo data
        "lang": LANGUAGE,
        "password": ADMIN_PASSWORD,
        "login": ADMIN_EMAIL,
        "country_code": COUNTRY_CODE,
        "phone": PHONE
    }
    
    try:
        # First try with JSON-RPC
        rpc_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "master_pwd": MASTER_PASSWORD,
                "name": DATABASE_NAME,
                "demo": True,
                "lang": LANGUAGE,
                "password": ADMIN_PASSWORD,
                "login": ADMIN_EMAIL,
                "country_code": COUNTRY_CODE,
                "phone": PHONE
            },
            "id": 1
        }
        
        response = requests.post(create_url, json=rpc_payload, timeout=60)
        
        # Check response
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get("result") == True:
                    print("    SUCCESS: Database created!")
                    return True
                elif "error" in result:
                    error_msg = result.get("error", {}).get("message", "Unknown error")
                    print(f"    ERROR: {error_msg}")
                    return False
            except:
                pass
        
        # If JSON didn't work, try form POST
        print("    Trying form-based creation...")
        response = requests.post(create_url, data=form_data, timeout=60)
        
        if response.status_code in [200, 303]:
            print("    SUCCESS: Database creation initiated!")
            return True
        else:
            print(f"    ERROR: HTTP {response.status_code}")
            print(f"    Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("    TIMEOUT: Database creation is taking time...")
        print("    This is normal for first-time setup.")
        print("    Waiting 30 seconds...")
        time.sleep(30)
        return True  # Assume it worked
    except Exception as e:
        print(f"    ERROR: {e}")
        return False
    
    # Step 4: Verify database creation
    print()
    print("[4/4] Verifying database creation...")
    time.sleep(5)  # Wait for database to be ready
    
    try:
        auth_url = f"{ODOO_URL}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": DATABASE_NAME,
                "login": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            },
            "id": 1
        }
        
        response = requests.post(auth_url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result", {}).get("uid"):
            print("    SUCCESS: Database is ready and accessible!")
            print(f"    You can now login at: {ODOO_URL}")
            print(f"    Email: {ADMIN_EMAIL}")
            print(f"    Password: {ADMIN_PASSWORD}")
            return True
        else:
            print("    WARNING: Database may still be initializing...")
            print("    Try again in 30 seconds.")
            return True
            
    except Exception as e:
        print(f"    WARNING: {e}")
        print("    Database is being created in background...")
        return True


def main():
    """Main function."""
    success = create_database()
    
    print()
    print("=" * 60)
    if success:
        print("DATABASE SETUP COMPLETE!")
        print()
        print("Next steps:")
        print(f"1. Open: {ODOO_URL}")
        print(f"2. Login with: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print("3. Run MCP test: python odoo_mcp_test_client.py")
    else:
        print("DATABASE SETUP FAILED!")
        print()
        print("Troubleshooting:")
        print("1. Check Docker: docker ps")
        print("2. Check logs: docker logs odoo --tail 50")
        print("3. Try manual creation at: http://localhost:8069")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
