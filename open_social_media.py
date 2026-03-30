"""
Simple Social Media Opener
Opens Facebook and Instagram in your DEFAULT browser
No automation, no CAPTCHA - just direct links!
"""

import os
import sys
import webbrowser
import time
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Get configuration
FACEBOOK_PROFILE_ID = os.getenv('FACEBOOK_PAGE_ID', '61578524116357')
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', 'shamaansari5576')

print("=" * 60)
print("   SOCIAL MEDIA OPENER")
print("=" * 60)
print()
print("Opening in your default browser...")
print()

# URLs
facebook_url = f'https://www.facebook.com/profile.php?id={FACEBOOK_PROFILE_ID}'
instagram_url = f'https://www.instagram.com/{INSTAGRAM_USERNAME}/'
meta_business_url = 'https://business.facebook.com'

print(f"1. Facebook Profile...")
webbrowser.open(facebook_url)
time.sleep(1)

print(f"2. Instagram Profile (@{INSTAGRAM_USERNAME})...")
webbrowser.open(instagram_url)
time.sleep(1)

print(f"3. Meta Business Suite (manage both)...")
webbrowser.open(meta_business_url)

print()
print("=" * 60)
print("   SUCCESS! All platforms opened in your browser!")
print()
print("   - Login manually (no CAPTCHA issues)")
print("   - Use Meta Business Suite to manage both")
print("=" * 60)
print()
print("Press Enter to exit...")
input()
