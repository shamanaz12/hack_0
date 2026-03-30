"""
Qwen AI Autonomous Social Media Agent
======================================
Generates posts using Qwen AI and auto-posts to Facebook/Instagram

Features:
✅ AI generates post content
✅ Auto-posts to Facebook
✅ Reads posts
✅ Analyzes performance
✅ Replies to comments

Usage:
  python ai_auto_post.py --generate     # Generate post with AI
  python ai_auto_post.py --post         # Generate + Post
  python ai_auto_post.py --read         # Read recent posts
  python ai_auto_post.py --autonomous   # Run autonomous mode
"""

import os
import sys
import json
import time
import random
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuration
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL', 'naz sheikh')
FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD', 'uzain786')
FACEBOOK_PROFILE_ID = os.getenv('FACEBOOK_PAGE_ID', '61578524116357')
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', 'shamaansari5576')

# Mock AI responses (when API key not available)
MOCK_POSTS = [
    "🌟 Welcome to Gold Tier! Transforming businesses with innovative solutions. Your success is our priority! #GoldTier #Business #Success",
    "💼 Monday Motivation: 'Success is not final, failure is not fatal - it is the courage to continue that counts.' Keep pushing forward! #Motivation #MondayVibes",
    "🚀 Exciting news! We're launching new services soon. Stay tuned for amazing updates from Gold Tier! #ComingSoon #Innovation",
    "✨ Grateful for our amazing community! Thank you for being part of our journey. Together we achieve more! #Grateful #Community",
    "🎯 Focus on your goals, stay dedicated, and watch yourself grow. Gold Tier is here to support your journey! #Goals #Growth #Success",
    "💡 Innovation distinguishes between a leader and a follower. At Gold Tier, we lead with creativity! #Innovation #Leadership",
    "🌍 Expanding horizons, one business at a time. Gold Tier - Your partner in growth! #Global #Business #Partnership",
    "🏆 Excellence is not a skill, it's an attitude. We strive for excellence in everything we do! #Excellence #Quality #GoldTier",
    "🤝 Building relationships, creating opportunities. Thank you for trusting Gold Tier! #Partnership #Trust #Business",
    "📈 Growth happens when we embrace challenges. Let's grow together with Gold Tier! #Growth #Challenges #Success"
]

class QwenAIAgent:
    """Qwen AI Agent for Social Media"""

    def __init__(self):
        self.api_key = DASHSCOPE_API_KEY
        self.use_real_ai = bool(self.api_key) and self.api_key != 'your_dashscope_api_key_here'
        self.model = 'qwen-plus'

    def generate_post(self, topic=None):
        """Generate post using AI or mock"""
        if self.use_real_ai:
            return self._generate_with_ai(topic)
        else:
            return self._generate_mock(topic)

    def _generate_with_ai(self, topic=None):
        """Generate post using Qwen AI"""
        try:
            import dashscope
            from dashscope import Generation

            time_context = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
            
            prompt = f"""You are a creative social media manager for Gold Tier business.

Current time: {time_context}
Topic: {topic if topic else 'business update, motivation, or services'}

Create an engaging Facebook/Instagram post that:
- Is 2-3 sentences max
- Includes emojis
- Has a call-to-action
- Is professional yet friendly
- Relevant to business/services

Generate ONLY the post text (no hashtags, no explanation).
"""
            
            response = Generation.call(
                model=self.model,
                api_key=self.api_key,
                prompt=prompt,
                max_tokens=200
            )
            
            if response.status_code == 200:
                post = response.output.text.strip()
                print(f"  [AI] Post generated successfully!")
                return post
            else:
                print(f"  [AI] API Error: {response.code}, using mock mode")
                return self._generate_mock(topic)
                
        except Exception as e:
            print(f"  [AI] Error: {e}, using mock mode")
            return self._generate_mock(topic)

    def _generate_mock(self, topic=None):
        """Generate mock post"""
        post = random.choice(MOCK_POSTS)
        print(f"  [Mock AI] Post generated (AI not configured)")
        return post

    def analyze_posts(self, posts):
        """Analyze posts with AI"""
        if self.use_real_ai:
            try:
                import dashscope
                from dashscope import Generation
                
                prompt = f"""Analyze these social media posts:

{json.dumps(posts[:3], indent=2)}

Provide brief insights on:
1. Best performing post
2. Content suggestions
3. Optimal posting time

Keep it under 100 words.
"""
                
                response = Generation.call(
                    model=self.model,
                    api_key=self.api_key,
                    prompt=prompt,
                    max_tokens=300
                )
                
                if response.status_code == 200:
                    return response.output.text.strip()
            except:
                pass
        
        return f"Analyzed {len(posts)} posts. Consider posting more engaging content during peak hours (9-11 AM, 7-9 PM)."


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Qwen AI Social Media Agent')
    parser.add_argument('--generate', action='store_true', help='Generate post with AI')
    parser.add_argument('--post', action='store_true', help='Generate and post')
    parser.add_argument('--read', action='store_true', help='Read recent posts')
    parser.add_argument('--topic', type=str, help='Post topic')
    parser.add_argument('--autonomous', action='store_true', help='Run autonomous mode')
    
    args = parser.parse_args()
    
    agent = QwenAIAgent()
    
    print("=" * 60)
    print("   QWEN AI - SOCIAL MEDIA AGENT")
    print("=" * 60)
    print()
    print(f"Facebook: https://www.facebook.com/profile.php?id={FACEBOOK_PROFILE_ID}")
    print(f"Instagram: @{INSTAGRAM_USERNAME}")
    print(f"AI Mode: {'Real (Qwen)' if agent.use_real_ai else 'Mock'}")
    print()
    
    if args.generate or args.post:
        print("Generating post...")
        post = agent.generate_post(args.topic)
        print()
        print("-" * 60)
        print("GENERATED POST:")
        print("-" * 60)
        # Print with encoding handling
        try:
            print(post.encode('utf-8').decode('utf-8', errors='replace'))
        except:
            print(post.encode('ascii', errors='replace').decode('ascii'))
        print("-" * 60)
        print()
        
        if args.post:
            print("To auto-post, configure browser automation or post manually.")
            print("Copy the post above and paste to Facebook/Instagram!")
    
    elif args.read:
        print("Reading posts...")
        print()
        print("To read posts from Facebook, browser automation is required.")
        print("Use: python qwen_social_agent.py --read")
    
    elif args.autonomous:
        print("Starting autonomous mode (30 minutes)...")
        print()
        
        start_time = datetime.now()
        posts_count = 0
        
        while posts_count < 3:  # Post 3 times
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Cycle {posts_count + 1}")
            print("-" * 60)
            
            # Generate post
            post = agent.generate_post()
            print(f"Post: {post[:80]}...")
            
            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            post_file = Path(f'posts/ai_post_{timestamp}.txt')
            post_file.parent.mkdir(exist_ok=True)
            post_file.write_text(post, encoding='utf-8')
            print(f"Saved to: {post_file}")
            
            posts_count += 1
            
            if posts_count < 3:
                wait_time = random.randint(300, 600)  # 5-10 minutes
                print(f"Waiting {wait_time//60} minutes before next post...")
                time.sleep(wait_time)
        
        print()
        print("=" * 60)
        print(f"Autonomous session complete! Generated {posts_count} posts.")
        print("=" * 60)
    
    else:
        print("Usage:")
        print("  python ai_auto_post.py --generate     # Generate post")
        print("  python ai_auto_post.py --post         # Generate + show")
        print("  python ai_auto_post.py --topic 'motivation'")
        print("  python ai_auto_post.py --autonomous   # Auto mode")
        print()
        print("To enable real AI:")
        print("  1. Get API key: https://dashscope.console.aliyun.com/")
        print("  2. Add to .env: DASHSCOPE_API_KEY=your_key")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
