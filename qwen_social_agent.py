"""
Qwen AI Autonomous Social Media Agent
Facebook & Instagram - Full Autonomous Operation

Features:
- AI decides what to post
- AI reads and analyzes posts
- AI replies to comments
- AI checks insights/analytics
- No human intervention needed

Uses: Qwen AI (Dashscope) + Playwright Browser Automation
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'qwen_social_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class QwenSocialAgent:
    """
    Autonomous Social Media Agent powered by Qwen AI
    Can post, read, analyze, and reply automatically
    """

    def __init__(self):
        # Configuration
        self.api_key = os.getenv('DASHSCOPE_API_KEY', '')
        self.facebook_email = os.getenv('FACEBOOK_EMAIL', '')
        self.facebook_password = os.getenv('FACEBOOK_PASSWORD', '')
        self.facebook_profile_id = os.getenv('FACEBOOK_PAGE_ID', '61578524116357')
        self.instagram_username = os.getenv('INSTAGRAM_USERNAME', 'shamaansari5576')
        self.instagram_password = os.getenv('INSTAGRAM_PASSWORD', '')
        
        # AI Model
        self.model = 'qwen-plus'
        self.use_ai = bool(self.api_key)
        
        # Browser
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
        # State
        self.last_post_time = None
        self.posts_today = 0
        self.max_posts_per_day = 5
        
        logger.info("Qwen Social Agent initialized")
        logger.info(f"  AI Enabled: {self.use_ai}")
        logger.info(f"  Facebook: {self.facebook_profile_id}")
        logger.info(f"  Instagram: @{self.instagram_username}")

    def start_browser(self):
        """Start Playwright browser"""
        try:
            from playwright.sync_api import sync_playwright
            
            logger.info("Starting browser...")
            self.playwright = sync_playwright().start()
            
            self.browser = self.playwright.chromium.launch(
                headless=False,
                slow_mo=100,
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            self.context.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
            self.page = self.context.new_page()
            
            logger.info("Browser started!")
            return True
        except Exception as e:
            logger.error(f"Browser error: {e}")
            return False

    def ai_decision(self, context: str, options: List[str]) -> str:
        """Ask Qwen AI to make a decision"""
        if not self.use_ai:
            logger.info("AI not configured, using default decision")
            return options[0] if options else "post"
        
        try:
            import dashscope
            from dashscope import Generation
            
            prompt = f"""You are an autonomous social media manager.

Context: {context}

Available actions: {', '.join(options)}

Choose the BEST action based on:
1. Time of day
2. Recent activity
3. Engagement potential
4. Content variety

Respond with ONLY the action name (no explanation).
"""
            
            response = Generation.call(
                model=self.model,
                api_key=self.api_key,
                prompt=prompt,
                max_tokens=50
            )
            
            if response.status_code == 200:
                decision = response.output.text.strip()
                logger.info(f"AI Decision: {decision}")
                return decision
            else:
                logger.warning(f"AI API error: {response.code}")
                return options[0]
                
        except Exception as e:
            logger.error(f"AI decision error: {e}")
            return options[0]

    def ai_generate_post(self, topic: str = None) -> str:
        """Ask Qwen AI to generate a post"""
        if not self.use_ai:
            return self._get_default_post()
        
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
                logger.info(f"AI generated post: {post[:100]}...")
                return post
            else:
                logger.warning(f"AI API error: {response.code}")
                return self._get_default_post()
                
        except Exception as e:
            logger.error(f"AI post generation error: {e}")
            return self._get_default_post()

    def _get_default_post(self) -> str:
        """Default post when AI unavailable"""
        posts = [
            "🌟 Welcome to Gold Tier! We're here to transform your business with innovative solutions. #GoldTier #Business",
            "💼 Success is not final, failure is not fatal: It is the courage to continue that counts. Keep pushing forward! #Motivation",
            "🚀 Exciting updates coming soon! Stay tuned for amazing announcements from Gold Tier. #StayTuned",
            "✨ Thank you for being part of our journey! Your support means everything to us. #Grateful #Community"
        ]
        import random
        return random.choice(posts)

    def ai_analyze_posts(self, posts: List[Dict]) -> Dict:
        """Ask AI to analyze post performance"""
        if not self.use_ai:
            return {'summary': f'Analyzed {len(posts)} posts'}
        
        try:
            import dashscope
            from dashscope import Generation
            
            posts_text = json.dumps(posts[:5], indent=2)  # First 5 posts
            
            prompt = f"""Analyze these social media posts and provide insights:

{posts_text}

Provide:
1. Best performing post and why
2. Suggested improvements
3. Optimal posting time recommendation
4. Content strategy suggestion

Keep it concise (100 words max).
"""
            
            response = Generation.call(
                model=self.model,
                api_key=self.api_key,
                prompt=prompt,
                max_tokens=300
            )
            
            if response.status_code == 200:
                analysis = response.output.text.strip()
                logger.info(f"AI Analysis: {analysis[:100]}...")
                return {'summary': analysis}
            else:
                return {'summary': 'Analysis unavailable'}
                
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {'summary': 'Analysis error'}

    def ai_reply_to_comment(self, comment: str) -> str:
        """Ask AI to generate reply to comment"""
        if not self.use_ai:
            return "Thank you for your comment! We appreciate your feedback. 😊"
        
        try:
            import dashscope
            from dashscope import Generation
            
            prompt = f"""You are a friendly social media manager.

Comment: {comment}

Generate a polite, professional, and friendly reply (1-2 sentences max).
Include an emoji if appropriate.
Generate ONLY the reply text.
"""
            
            response = Generation.call(
                model=self.model,
                api_key=self.api_key,
                prompt=prompt,
                max_tokens=100
            )
            
            if response.status_code == 200:
                reply = response.output.text.strip()
                logger.info(f"AI reply: {reply}")
                return reply
            else:
                return "Thank you for your comment! 😊"
                
        except Exception as e:
            logger.error(f"AI reply error: {e}")
            return "Thank you!"

    def post_to_facebook(self, message: str) -> Dict:
        """Post to Facebook"""
        logger.info(f"Posting to Facebook: {message[:50]}...")
        
        if not self.page:
            self.start_browser()
        
        try:
            # Login if needed
            self._facebook_login()
            
            # Navigate to profile
            self.page.goto(f'https://www.facebook.com/profile.php?id={self.facebook_profile_id}', 
                          wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            # Find post box and post
            try:
                post_box = self.page.locator('[data-testid="create_post"]').first
                post_box.click()
                time.sleep(1)
                post_box.fill(message)
                time.sleep(1)
                
                post_btn = self.page.locator('button').filter(has_text='Post').first
                if post_btn.is_visible():
                    post_btn.click()
                    time.sleep(3)
                    
                    self.posts_today += 1
                    self.last_post_time = datetime.now()
                    
                    logger.info("Facebook post created!")
                    return {'success': True, 'message': 'Post created'}
                else:
                    return {'success': False, 'error': 'Post button not found'}
                    
            except Exception as e:
                logger.error(f"Post error: {e}")
                return {'success': False, 'error': str(e)}
                
        except Exception as e:
            logger.error(f"Facebook post error: {e}")
            return {'success': False, 'error': str(e)}

    def _facebook_login(self):
        """Login to Facebook"""
        try:
            self.page.goto('https://www.facebook.com/login', wait_until='networkidle', timeout=30000)
            
            if 'login' in self.page.url.lower():
                if self.facebook_email and self.facebook_password:
                    logger.info("Logging in to Facebook...")
                    self.page.fill('#email', self.facebook_email)
                    time.sleep(1)
                    self.page.fill('#pass', self.facebook_password)
                    time.sleep(1)
                    self.page.click('button[type="submit"]')
                    time.sleep(5)
        except:
            pass

    def get_facebook_posts(self, limit: int = 5) -> List[Dict]:
        """Get recent Facebook posts"""
        logger.info(f"Getting {limit} recent posts...")
        
        if not self.page:
            self.start_browser()
        
        try:
            self._facebook_login()
            
            self.page.goto(f'https://www.facebook.com/profile.php?id={self.facebook_profile_id}', 
                          wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            posts = []
            post_elements = self.page.locator('[role="article"]')
            count = min(post_elements.count(), limit)
            
            for i in range(count):
                try:
                    post_el = post_elements.nth(i)
                    if post_el.is_visible():
                        message = ''
                        try:
                            msg_el = post_el.locator('[dir="auto"]').first
                            message = msg_el.inner_text()[:500]
                        except:
                            pass
                        
                        posts.append({
                            'index': i,
                            'message': message,
                            'timestamp': datetime.now().isoformat()
                        })
                except:
                    continue
            
            logger.info(f"Retrieved {len(posts)} posts")
            return posts
            
        except Exception as e:
            logger.error(f"Get posts error: {e}")
            return []

    def autonomous_run(self, duration_minutes: int = 60):
        """Run autonomous agent for specified duration"""
        logger.info("=" * 60)
        logger.info("QWEN AUTONOMOUS SOCIAL AGENT - STARTING")
        logger.info(f"Duration: {duration_minutes} minutes")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            try:
                # Decision cycle
                context = f"""
                Current time: {datetime.now().strftime('%I:%M %p')}
                Posts today: {self.posts_today}/{self.max_posts_per_day}
                Last post: {self.last_post_time.strftime('%I:%M %p') if self.last_post_time else 'None'}
                """
                
                options = ['post', 'read', 'analyze', 'wait']
                decision = self.ai_decision(context, options)
                
                logger.info(f"\nAI Decision: {decision}")
                
                if decision == 'post' and self.posts_today < self.max_posts_per_day:
                    # Generate and post
                    post_content = self.ai_generate_post()
                    result = self.post_to_facebook(post_content)
                    logger.info(f"Post result: {result}")
                    
                elif decision == 'read':
                    # Get and read posts
                    posts = self.get_facebook_posts(5)
                    logger.info(f"Read {len(posts)} posts")
                    
                elif decision == 'analyze':
                    # Analyze performance
                    posts = self.get_facebook_posts(5)
                    analysis = self.ai_analyze_posts(posts)
                    logger.info(f"Analysis: {analysis['summary'][:100]}...")
                    
                else:
                    # Wait
                    logger.info("Waiting 5 minutes before next action...")
                    time.sleep(300)
                    
            except Exception as e:
                logger.error(f"Autonomous cycle error: {e}")
                time.sleep(60)
        
        logger.info("\n" + "=" * 60)
        logger.info("AUTONOMOUS SESSION COMPLETE")
        logger.info(f"Total posts: {self.posts_today}")
        logger.info("=" * 60)

    def cleanup(self):
        """Cleanup"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Cleanup complete")
        except:
            pass


# Global agent instance
agent = QwenSocialAgent()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Qwen Autonomous Social Media Agent')
    parser.add_argument('--run', action='store_true', help='Run autonomous agent')
    parser.add_argument('--duration', type=int, default=60, help='Duration in minutes')
    parser.add_argument('--post', action='store_true', help='Create single post')
    parser.add_argument('--read', action='store_true', help='Read recent posts')
    parser.add_argument('--topic', type=str, help='Post topic')
    
    args = parser.parse_args()
    
    if args.run:
        agent.autonomous_run(args.duration)
    elif args.post:
        agent.start_browser()
        post = agent.ai_generate_post(args.topic)
        result = agent.post_to_facebook(post)
        print(f"Post result: {result}")
    elif args.read:
        agent.start_browser()
        posts = agent.get_facebook_posts(5)
        print(f"Found {len(posts)} posts")
        for i, post in enumerate(posts, 1):
            print(f"\n{i}. {post['message'][:100]}...")
    else:
        print("=" * 60)
        print("QWEN AUTONOMOUS SOCIAL MEDIA AGENT")
        print("=" * 60)
        print()
        print("Usage:")
        print("  python qwen_social_agent.py --run --duration 60")
        print("  python qwen_social_agent.py --post")
        print("  python qwen_social_agent.py --read")
        print("  python qwen_social_agent.py --post --topic 'business update'")
        print()
        print("Configuration:")
        print(f"  AI Enabled: {agent.use_ai}")
        print(f"  Facebook: {agent.facebook_profile_id}")
        print(f"  Instagram: @{agent.instagram_username}")
        print()
        print("To enable AI, set DASHSCOPE_API_KEY in .env")
        print("=" * 60)
    
    agent.cleanup()
