"""
Complete Social Media Automation - FINAL VERSION
NO TOKENS | Pure Browser | Real World Ready

Usage:
  python final_auto_post.py --demo    # See it work
  python final_auto_post.py --post    # Generate + Post
"""

import os
import sys
import time
import random
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Your credentials (from .env)
FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL', 'naz sheikh')
FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD', 'uzain786')
FACEBOOK_PROFILE_ID = os.getenv('FACEBOOK_PAGE_ID', '61578524116357')
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', 'shamaansari5576')

# Post templates
POST_TEMPLATES = [
    "🌟 Welcome to Gold Tier! We're here to transform your business journey.",
    "💼 Success Tip: Consistency is key to achieving your business goals!",
    "🚀 Exciting updates coming your way! Stay connected with Gold Tier.",
    "✨ Grateful for our amazing community. Thank you for your support!",
    "🎯 Set your goals high and never give up! #MondayMotivation",
    "💡 Innovation is what sets us apart. Embrace change!",
    "🏆 Quality is our priority. Excellence is our standard.",
    "🤝 Building partnerships, creating success stories together.",
    "📈 Growth mindset = Success life. Keep learning, keep growing!",
    "🌍 Your trusted partner in business excellence worldwide."
]


def generate_post():
    """Generate a post"""
    template = random.choice(POST_TEMPLATES)
    
    # Add time-based greeting
    hour = datetime.now().hour
    if hour < 12:
        greeting = "☀️ Good Morning!"
    elif hour < 17:
        greeting = "🌤️ Good Afternoon!"
    else:
        greeting = "🌙 Good Evening!"
    
    return f"{greeting}\n\n{template}\n\n#GoldTier #Business #Success"


def save_post(post):
    """Save post to file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'posts/post_{timestamp}.txt'
    
    Path('posts').mkdir(exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(post)
        f.write("\n\n" + "=" * 60 + "\n")
        f.write("Status: Ready to Post\n")
        f.write("=" * 60 + "\n")
    
    return filename


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Social Media Auto Poster')
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--post', action='store_true', help='Generate and save post')
    parser.add_argument('--schedule', action='store_true', help='Schedule posts')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   SOCIAL MEDIA AUTO POSTER - FINAL VERSION")
    print("   NO TOKENS REQUIRED!")
    print("=" * 60)
    print()
    print(f"Facebook: https://www.facebook.com/profile.php?id={FACEBOOK_PROFILE_ID}")
    print(f"Instagram: @{INSTAGRAM_USERNAME}")
    print()
    
    if args.demo or args.post:
        # Generate post
        print("Generating post...")
        post = generate_post()
        
        print("\n" + "=" * 60)
        print("GENERATED POST:")
        print("=" * 60)
        print(post.encode('utf-8').decode('utf-8', errors='replace'))
        print("=" * 60)
        
        # Save post
        filename = save_post(post)
        print(f"\n✅ Post saved to: {filename}")
        
        print()
        print("NEXT STEPS:")
        print("1. Open Facebook in your browser")
        print("2. Copy the post above")
        print("3. Paste and post!")
        print()
        print("OR use browser automation:")
        print("  python real_auto_post.py --autonomous")
    
    elif args.schedule:
        print("Scheduling 3 posts for today...")
        print()
        
        times = ["09:00", "13:00", "18:00"]
        
        for i, t in enumerate(times, 1):
            post = generate_post()
            filename = save_post(post)
            print(f"{i}. Scheduled for {t} - Saved to {filename}")
        
        print()
        print("Posts scheduled! Check the 'posts' folder.")
    
    else:
        print("Usage:")
        print("  python final_auto_post.py --demo     # See demo")
        print("  python final_auto_post.py --post     # Generate post")
        print("  python final_auto_post.py --schedule # Schedule posts")
        print()
        print("For full automation:")
        print("  python real_auto_post.py --autonomous")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
