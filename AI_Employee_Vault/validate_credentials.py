import json
import os
from pathlib import Path

def validate_credentials():
    """Validate the credentials.json file structure"""
    creds_path = Path("credentials.json")
    
    if not creds_path.exists():
        print("[ERROR] credentials.json file not found!")
        print("Please follow the FIX_OAUTH_ERROR.md guide to create it.")
        return False
    
    try:
        with open(creds_path, 'r') as f:
            data = json.load(f)
        
        # Check if it has the expected structure
        if 'installed' in data:
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
            installed_data = data['installed']
            
            print("[OK] credentials.json found with 'installed' structure")
            
            missing_fields = []
            for field in required_fields:
                if field not in installed_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"[ERROR] Missing required fields in credentials.json: {missing_fields}")
                print("Please download the correct credentials file from Google Cloud Console")
                return False
            else:
                print("[OK] All required fields present in credentials.json")
                print(f"   Client ID: {installed_data['client_id'][:20]}...")
                print(f"   Auth URI: {installed_data['auth_uri']}")
                print(f"   Token URI: {installed_data['token_uri']}")
                return True
        else:
            print("[ERROR] Invalid credentials.json structure!")
            print("The file should contain an 'installed' key for desktop applications")
            print("Please download the correct credentials file from Google Cloud Console")
            return False
            
    except json.JSONDecodeError:
        print("[ERROR] Invalid JSON format in credentials.json!")
        print("Please download the correct credentials file from Google Cloud Console")
        return False
    except Exception as e:
        print(f"[ERROR] Error validating credentials: {e}")
        return False

def main():
    print("Validating credentials.json file...")
    print("="*50)
    
    is_valid = validate_credentials()
    
    print("="*50)
    if is_valid:
        print("[OK] Credentials file is valid!")
        print("You can now run the Gmail authentication process.")
    else:
        print("[ERROR] Credentials file is invalid!")
        print("Please follow the instructions in FIX_OAUTH_ERROR.md to fix it.")
    
    print("\nTo run Gmail authentication after fixing credentials:")
    print("python -c \"from gmail_auth import test_authentication; test_authentication()\"")

if __name__ == "__main__":
    main()