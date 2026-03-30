#!/usr/bin/env python3
"""
Social Media CLI - Check Facebook & Instagram Posts
Shows post history from logs

Usage:
  python social_cli.py --facebook    # Show Facebook posts
  python social_cli.py --instagram   # Show Instagram posts
  python social_cli.py --all         # Show all platforms
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def load_json_log(filename):
    """Load JSON log file"""
    filepath = Path('logs') / filename
    if not filepath.exists():
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def parse_log_file(filename):
    """Parse text log file for posts"""
    filepath = Path('logs') / filename
    if not filepath.exists():
        return []
    
    posts = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Look for NEW POST patterns
                if '[NEW POST]' in line or '[NEW IMAGE]' in line or '[NEW CAROUSEL]' in line or '[NEW VIDEO]' in line:
                    # Extract timestamp
                    match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    timestamp = match.group(1) if match else 'Unknown'
                    
                    # Extract post info
                    if '[NEW POST]' in line:
                        post_type = 'POST'
                    elif '[NEW IMAGE]' in line:
                        post_type = 'IMAGE'
                    elif '[NEW CAROUSEL]' in line:
                        post_type = 'CAROUSEL'
                    elif '[NEW VIDEO]' in line:
                        post_type = 'VIDEO'
                    else:
                        post_type = 'UNKNOWN'
                    
                    posts.append({
                        'timestamp': timestamp,
                        'type': post_type,
                        'line': line.strip()
                    })
    except Exception as e:
        print(f"  Error reading log: {e}")
    
    return posts

def show_facebook_posts():
    """Show Facebook posts from log"""
    print_header("FACEBOOK POSTS")
    
    posts = parse_log_file('facebook_watcher.log')
    fb_posts = [p for p in posts if 'POST' in p['type']]
    
    if not fb_posts:
        print("No Facebook posts found in logs.")
        return 0
    
    print(f"Total Facebook Posts: {len(fb_posts)}\n")
    
    for i, post in enumerate(fb_posts[-10:], 1):
        print(f"Post {i}:")
        print(f"  Time: {post['timestamp']}")
        print(f"  Type: {post['type']}")
        # Extract post ID
        if '_' in post['line']:
            parts = post['line'].split('_')
            if len(parts) > 1:
                post_id = parts[1].strip().split()[0]
                print(f"  ID: {post_id}")
        print()
    
    return len(fb_posts)

def show_instagram_posts():
    """Show Instagram posts from log"""
    print_header("INSTAGRAM POSTS")
    
    posts = parse_log_file('facebook_instagram_watcher.log')
    ig_posts = [p for p in posts if p['type'] in ['IMAGE', 'CAROUSEL', 'VIDEO']]
    
    if not ig_posts:
        print("No Instagram posts found in logs.")
        return 0
    
    print(f"Total Instagram Posts: {len(ig_posts)}\n")
    
    for i, post in enumerate(ig_posts[-10:], 1):
        print(f"Post {i}:")
        print(f"  Time: {post['timestamp']}")
        print(f"  Type: {post['type']}")
        print()
    
    return len(ig_posts)

def show_summary():
    """Show summary of all platforms"""
    print_header("SOCIAL MEDIA SUMMARY")
    
    # Parse logs
    fb_posts = parse_log_file('facebook_watcher.log')
    ig_posts = parse_log_file('facebook_instagram_watcher.log')
    
    # Count unique posts
    fb_count = len([p for p in fb_posts if 'POST' in p['type']])
    ig_count = len(ig_posts)
    
    print(f"\nPlatform Summary:")
    print(f"  Facebook:   {fb_count} posts")
    print(f"  Instagram:  {ig_count} posts")
    print(f"\nTotal: {fb_count + ig_count} posts")
    
    # Show recent activity
    print("\n" + "="*50)
    print("Recent Facebook Posts (Last 5)")
    print("="*50)
    
    for post in fb_posts[-5:]:
        print(f"  [{post['timestamp']}] {post['type']}")
    
    print("\n" + "="*50)
    print("Recent Instagram Posts (Last 5)")
    print("="*50)
    
    for post in ig_posts[-5:]:
        print(f"  [{post['timestamp']}] {post['type']}")
    
    print()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Social Media CLI')
    parser.add_argument('--facebook', action='store_true', help='Show Facebook posts')
    parser.add_argument('--instagram', action='store_true', help='Show Instagram posts')
    parser.add_argument('--all', action='store_true', help='Show all platforms')
    args = parser.parse_args()
    
    if args.facebook:
        show_facebook_posts()
    elif args.instagram:
        show_instagram_posts()
    elif args.all:
        show_summary()
    else:
        # Default: show summary
        show_summary()

if __name__ == '__main__':
    main()
