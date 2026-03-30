#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Token Setup - Easy Step by Step Guide
For @shamaansari5576 account
"""

import os
import sys
import webbrowser
import time
from pathlib import Path
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

print("=" * 60)
print("     INSTAGRAM TOKEN SETUP - @shamaansari5576")
print("=" * 60)
print("  Yeh script aap ko Instagram API Token lene mein")
print("  madad karegi step-by-step")
print()
print("  INSTAGRAM: @shamaansari5576")
print("  PROFILE: https://www.instagram.com/shamaansari5576")
print("=" * 60)
print()

input("Press Enter to start setup...")

print()
print("=" * 60)
print("  STEP 1: Facebook Graph API Explorer Open Karein")
print("=" * 60)
print()

input("Press Enter to open browser...")
webbrowser.open('https://developers.facebook.com/tools/explorer/')

print("""
Graph API Explorer khul gaya hoga!

Ab ye karein:
1. Facebook login karein (if not logged in)
2. Application select karein (ya new banayein)

------------------------------------------------------------
""")

input("Press Enter jab app select ho jaaye...")

print()
print("=" * 60)
print("  STEP 2: Permissions Select Karein")
print("=" * 60)
print("""
"Get Token" -> "Get User Access Token" click karein

Ye sab permissions SELECT karein:
  [x] instagram_basic
  [x] instagram_content_publish  
  [x] pages_read_engagement
  [x] pages_manage_engagement
  [x] pages_show_list

------------------------------------------------------------
""")

input("Press Enter jab permissions select ho jaayein...")

print()
print("=" * 60)
print("  STEP 3: Token Generate Karein")
print("=" * 60)
print("""
1. "Generate Access Token" button click karein
2. Facebook permission dialog aayega
3. "Continue" click karein
4. Saare permissions allow karein

------------------------------------------------------------
""")

input("Press Enter jab token generate ho jaaye...")

print()
print("=" * 60)
print("  STEP 4: Token Copy Karein (IMPORTANT!)")
print("=" * 60)
print("""
Access Token box mein ek lamba code hoga.
Example: EAAGm0P4ZCqo0BOxxxxx...

Us ko SELECT kar ke COPY kar lein!

------------------------------------------------------------
""")

input("Press Enter jab token copy kar lein...")

print()
print("=" * 60)
print("  STEP 5: Instagram Business ID Nikalein")
print("=" * 60)
print("""
Graph API Explorer mein ye query chalayein:

GET /me/accounts?fields=instagram_business_account

"Submit" dabayein

Response mein dikhega:
{
  "data": [{
    "name": "Gold Tier",
    "id": "956241877582673",
    "instagram_business_account": {
      "id": "178414XXXXXXXXXX"  <-- YE HAI BUSINESS ID
      "name": "shamaansari5576"
    }
  }]
}

Instagram Business ID COPY kar lein!

------------------------------------------------------------
""")

input("Press Enter jab Business ID copy ho jaaye...")

print()
print("=" * 60)
print("  STEP 6: .env File Update Karein")
print("=" * 60)
print("""
.env file edit karein:
  File: C:\\Users\\AA\\Desktop\\gold_tier\\.env

Ye lines dhundhein:
  INSTAGRAM_BUSINESS_ID=
  INSTAGRAM_ACCESS_TOKEN=

Replace karein:
  INSTAGRAM_BUSINESS_ID=178414XXXXXXXXXX
  INSTAGRAM_ACCESS_TOKEN=EAAGm0P4ZCqo0BOxxxx...

SAVE kar dein!

------------------------------------------------------------
""")

input("Press Enter jab .env update ho jaaye...")

print()
print("=" * 60)
print("  STEP 7: Test Karein")
print("=" * 60)
print("""
Command prompt mein ye chalayein:

python watcher\\facebook_instagram_watcher.py --once --instagram-only

Agar real posts dikhein toh SUCCESS!

------------------------------------------------------------
""")

input("Press Enter to complete...")

print()
print("=" * 60)
print("           SETUP COMPLETE!")
print("=" * 60)
print("""
Instagram @shamaansari5576 ab ready hai!

Quick Commands:
  python watcher\\facebook_instagram_watcher.py --once
  python watcher\\facebook_instagram_watcher.py

Logs: logs\\facebook_instagram_watcher.log
""")
print("=" * 60)

# Save completion marker
with open('instagram_setup_complete.txt', 'w', encoding='utf-8') as f:
    f.write(f"Instagram setup completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Instagram: @shamaansari5576\n")

print("\nShukriya! Instagram integration complete ho gaya.\n")
print("Press Enter to exit...")
input()
