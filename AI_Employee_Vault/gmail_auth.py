"""
Gmail API Authentication Module
Handles OAuth2 authentication for Gmail API access
"""
import os
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes required for reading Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """
    Authenticate and return Gmail API service object
    """
    creds = None
    # Token file stores the user's access and refresh tokens
    token_file = 'token.pickle'
    credentials_file = 'credentials.json'  # This needs to be obtained from Google Cloud Console
    
    # Load existing token if available
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no valid credentials, request authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh the token if expired
            creds.refresh(Request())
        else:
            # Run the OAuth flow if no valid credentials
            if not os.path.exists(credentials_file):
                print(f"Error: {credentials_file} not found.")
                print("Please follow these steps to set up Gmail API access:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select an existing one")
                print("3. Enable the Gmail API")
                print("4. Create credentials (OAuth 2.0 client IDs) for a desktop application")
                print("5. Download the credentials JSON file and save it as 'credentials.json'")
                print("6. Run this script again")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    # Build and return the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    return service

def test_authentication():
    """
    Test function to verify authentication works
    """
    print("Testing Gmail API authentication...")
    service = authenticate_gmail()
    
    if service:
        print("Authentication successful!")
        # Try to fetch basic profile info
        try:
            profile = service.users().getProfile(userId='me').execute()
            print(f"Authenticated as: {profile.get('emailAddress')}")
            return service
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return None
    else:
        print("Authentication failed!")
        return None

if __name__ == '__main__':
    test_authentication()