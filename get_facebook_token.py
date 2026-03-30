#!/usr/bin/env python3
"""
Facebook Token Helper - Guides you through getting Facebook Access Token
Opens browser and walks you through the process
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

print("""
╔══════════════════════════════════════════════════════════════╗
║         FACEBOOK ACCESS TOKEN - STEP BY STEP GUIDE          ║
╠══════════════════════════════════════════════════════════════╣
║  Yeh script aap ko step-by-step guide karegi                ║
║  Facebook Access Token lene ke liye                         ║
╚══════════════════════════════════════════════════════════════╝

STEP 1: Browser Open Ho Raha Hai...
""")

# Wait for user
input("Press Enter to open Facebook in your browser...")

# Open Facebook
print("\nOpening Facebook.com...")
webbrowser.open('https://www.facebook.com')

print("""
✅ Facebook khul gaya hoga!

Ab ye karein:

1. ✅ Agar login nahi hain, toh login karein
   - Email: [Your Facebook Email]
   - Password: [Your Facebook Password]

2. ✅ Login ke baad, address bar mein type karein:
   
   business.facebook.com

3. ✅ Enter dabayein

─────────────────────────────────────────────────────────────

Press Enter jab Business Suite khul jaaye...
""")

input()

print("""
STEP 2: Business Suite Mein

Ab ye karein:

1. ✅ Left side mein "Settings" (⚙️ gear icon) dhundhein
2. ✅ Click karein
3. ✅ "Business Settings" select karein

─────────────────────────────────────────────────────────────

Press Enter jab Business Settings khul jaaye...
""")

input()

print("""
STEP 3: System User Banayein

1. ✅ Left menu mein "Users" → "System Users" pe jaayein
2. ✅ "Add" button click karein
3. ✅ Name mein likhein: "Gold Tier MCP"
4. ✅ "Create System User" dabayein

─────────────────────────────────────────────────────────────

Press Enter jab System User ban jaaye...
""")

input()

print("""
STEP 4: Assets Assign Karein

1. ✅ Naya banaya hua "Gold Tier MCP" user select karein
2. ✅ "Add Assets" button click karein
3. ✅ "Pages" select karein
4. ✅ "Gold Tier" page select karein
5. ✅ Permissions: "Full Control" select karein
6. ✅ "Save Changes" dabayein

─────────────────────────────────────────────────────────────

Press Enter jab assets assign ho jaayein...
""")

input()

print("""
STEP 5: Token Generate Karein (IMPORTANT!)

1. ✅ System User abhi bhi select ho
2. ✅ "Generate New Token" button click karein
3. ✅ "Select Asset" → "Pages" choose karein
4. ✅ Page: "Gold Tier" select karein
5. ✅ Ye permissions select karein (ALL):
   
   ☑ manage_pages
   ☑ pages_show_list
   ☑ pages_read_engagement
   ☑ pages_manage_posts
   ☑ pages_manage_engagement
   ☑ read_insights

6. ✅ "Generate Token" dabayein

─────────────────────────────────────────────────────────────

⚠️  TOKEN COPY KAR LEIN! ⚠️

Jab token generate ho, toh woh ek lamba code hoga.
Us ko COPY kar lein aur kahin save kar lein.

Press Enter jab token copy kar lein...
""")

input()

print("""
STEP 6: .env File Update Karein

Ab apni .env file edit karein:

1. File kholain: C:\\Users\\AA\\Desktop\\gold_tier\\.env

2. Ye line dhundhein:
   FACEBOOK_PAGE_ACCESS_TOKEN=test_token

3. Replace karein apne token se:
   FACEBOOK_PAGE_ACCESS_TOKEN=YOUR_COPIED_TOKEN_HERE

4. Save kar dein

─────────────────────────────────────────────────────────────

Press Enter jab .env update ho jaaye...
""")

input()

print("""
╔══════════════════════════════════════════════════════════════╗
║                    ✅ COMPLETE!                              ║
╠══════════════════════════════════════════════════════════════╣
║  Facebook Access Token configure ho gaya hai!               ║
║                                                              ║
║  Ab ye command chalayein:                                    ║
║                                                              ║
║  node facebook_mcp.js                                        ║
║                                                              ║
║  Ya phir:                                                    ║
║  python master_orchestrator.py start                         ║
╚══════════════════════════════════════════════════════════════╝
""")

print("\nShukriya! System ab ready hai.")
print("\nKoi masla ho toh GET_TOKEN_EASY.md file parhein.")

# Save completion marker
with open('token_setup_complete.txt', 'w') as f:
    f.write(f"Token setup completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

print("\nPress Enter to exit...")
input()
