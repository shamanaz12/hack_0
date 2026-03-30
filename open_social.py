"""
Open Facebook & Instagram - Python Script
Opens your profiles in default browser
No login needed if already logged in!
"""

import webbrowser
import time

print("=" * 60)
print("   OPENING YOUR SOCIAL MEDIA")
print("=" * 60)
print()

# Your profile links
FACEBOOK_URL = "https://www.facebook.com/profile.php?id=61578524116357"
INSTAGRAM_URL = "https://www.instagram.com/shamaansari5576/"
META_BUSINESS_URL = "https://business.facebook.com"

print("Opening Facebook...")
webbrowser.open(FACEBOOK_URL)
time.sleep(1)

print("Opening Instagram...")
webbrowser.open(INSTAGRAM_URL)
time.sleep(1)

print("Opening Meta Business Suite...")
webbrowser.open(META_BUSINESS_URL)

print()
print("=" * 60)
print("   DONE! Check your browser")
print("=" * 60)
print()
print("If you're logged in, no login needed!")
print("Browser will use your saved session.")
print()
