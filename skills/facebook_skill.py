#!/usr/bin/env python3
"""
Facebook Auto-Post Skill
Creates posts on Facebook via Graph API.

Usage: 
  python skills/facebook_skill.py "post message"
  python skills/facebook_skill.py --post "Your message here"
  python skills/facebook_skill.py --get 5
  python skills/facebook_skill.py --check
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Run: pip install requests")
    sys.exit(1)

# Configuration
SKILL_NAME = "facebook_auto_post"
STATE_DIR = Path("plans")
STATE_FILE = STATE_DIR / "facebook_skill.json"
DASHBOARD_FILE = Path("Dashboard.md")
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "facebook_skill.log"

# Facebook configuration from environment
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "956241877582673")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
GRAPH_API_VERSION = "v18.0"
GRAPH_API_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class FacebookSkill:
    """Skill for Facebook auto-posting and management."""

    def __init__(self):
        self.state_dir = STATE_DIR
        self.state_file = STATE_FILE
        self.dashboard_file = DASHBOARD_FILE
        self.log_dir = LOG_DIR
        self.log_file = LOG_FILE
        self.state_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        self.mock_mode = not FACEBOOK_ACCESS_TOKEN or FACEBOOK_ACCESS_TOKEN == "test_token_replace_with_actual_token" or FACEBOOK_ACCESS_TOKEN == "mock_token"

    def log(self, message: str):
        """Log message to file and console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except:
            pass

    def check_connection(self) -> bool:
        """Check Facebook API connection."""
        if self.mock_mode:
            self.log("Running in MOCK MODE - no real Facebook API calls")
            return True
        
        try:
            response = requests.get(
                f"{GRAPH_API_URL}/{FACEBOOK_PAGE_ID}",
                params={"access_token": FACEBOOK_ACCESS_TOKEN},
                timeout=10
            )
            if response.status_code == 200:
                self.log("Facebook connection OK")
                return True
            else:
                error = response.json().get("error", {}).get("message", "Unknown error")
                self.log(f"Facebook API error: {error}")
                return False
        except Exception as e:
            self.log(f"Connection error: {str(e)}")
            return False

    def get_page_info(self) -> dict:
        """Get Facebook page information."""
        if self.mock_mode:
            return {
                "success": True,
                "mock": True,
                "data": {
                    "id": FACEBOOK_PAGE_ID,
                    "name": "Gold Tier",
                    "about": "Business Management Solutions",
                    "category": "Business Service",
                    "followers_count": 1250,
                    "likes": 1180
                }
            }
        
        try:
            response = requests.get(
                f"{GRAPH_API_URL}/{FACEBOOK_PAGE_ID}",
                params={
                    "access_token": FACEBOOK_ACCESS_TOKEN,
                    "fields": "id,name,about,category,followers_count,likes"
                },
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json().get("error", {}).get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_post(self, message: str, link: str = None) -> dict:
        """Create a new post on Facebook."""
        self.log(f"Creating post: {message[:50]}...")
        
        if self.mock_mode:
            post_id = f"{FACEBOOK_PAGE_ID}_{int(datetime.now().timestamp())}"
            result = {
                "success": True,
                "post_id": post_id,
                "mock": True,
                "message": "Post created successfully (Mock Mode)",
                "post_data": {
                    "id": post_id,
                    "message": message,
                    "link": link,
                    "created_time": datetime.now().isoformat()
                }
            }
            self.log(f"Mock post created: {post_id}")
            return result
        
        try:
            data = {"message": message, "access_token": FACEBOOK_ACCESS_TOKEN}
            if link:
                data["link"] = link
            
            response = requests.post(
                f"{GRAPH_API_URL}/{FACEBOOK_PAGE_ID}/feed",
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get("id")
                self.log(f"Post created: {post_id}")
                return {
                    "success": True,
                    "post_id": post_id,
                    "message": "Post created successfully"
                }
            else:
                error = response.json().get("error", {}).get("message", "Unknown error")
                self.log(f"Post creation failed: {error}")
                return {"success": False, "error": error}
        except Exception as e:
            self.log(f"Post creation error: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_posts(self, limit: int = 5) -> dict:
        """Get recent posts from Facebook page."""
        if self.mock_mode:
            mock_posts = [
                {
                    "id": f"{FACEBOOK_PAGE_ID}_1",
                    "message": "Welcome to Gold Tier! Our new business management system is now live.",
                    "created_time": "2026-03-25T10:00:00+0000",
                    "likes": {"summary": {"total_count": 45}},
                    "comments": {"summary": {"total_count": 12}},
                    "shares": {"count": 8}
                },
                {
                    "id": f"{FACEBOOK_PAGE_ID}_2",
                    "message": "Check out our latest services! Visit our website for more info.",
                    "created_time": "2026-03-24T14:30:00+0000",
                    "likes": {"summary": {"total_count": 32}},
                    "comments": {"summary": {"total_count": 7}},
                    "shares": {"count": 5}
                }
            ]
            return {"success": True, "data": mock_posts[:limit], "mock": True}
        
        try:
            response = requests.get(
                f"{GRAPH_API_URL}/{FACEBOOK_PAGE_ID}/posts",
                params={
                    "access_token": FACEBOOK_ACCESS_TOKEN,
                    "limit": limit,
                    "fields": "id,message,created_time,likes.summary(true),comments.summary(true),shares"
                },
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json().get("data", [])}
            else:
                return {"success": False, "error": response.json().get("error", {}).get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def post_photo(self, photo_url: str, caption: str = "") -> dict:
        """Post photo to Facebook."""
        self.log(f"Posting photo: {photo_url}")
        
        if self.mock_mode:
            photo_id = f"{FACEBOOK_PAGE_ID}_photo_{int(datetime.now().timestamp())}"
            return {
                "success": True,
                "photo_id": photo_id,
                "mock": True,
                "message": "Photo posted successfully (Mock Mode)"
            }
        
        try:
            response = requests.post(
                f"{GRAPH_API_URL}/{FACEBOOK_PAGE_ID}/photos",
                data={
                    "url": photo_url,
                    "caption": caption,
                    "access_token": FACEBOOK_ACCESS_TOKEN
                },
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                return {"success": True, "photo_id": result.get("id")}
            else:
                return {"success": False, "error": response.json().get("error", {}).get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_post(self, post_id: str) -> dict:
        """Delete a Facebook post."""
        self.log(f"Deleting post: {post_id}")
        
        if self.mock_mode:
            return {"success": True, "message": "Post deleted successfully (Mock Mode)", "mock": True}
        
        try:
            response = requests.delete(
                f"{GRAPH_API_URL}/{post_id}",
                params={"access_token": FACEBOOK_ACCESS_TOKEN},
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "message": "Post deleted successfully"}
            else:
                return {"success": False, "error": response.json().get("error", {}).get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_dashboard(self, action: str, post_id: str, message: str, status: str):
        """Update Dashboard.md with Facebook activity."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n- [{timestamp}] {action}: {post_id} - {message[:50]}... - Status: {status}"

        if self.dashboard_file.exists():
            content = self.dashboard_file.read_text()
            if "## Facebook Posts" in content:
                lines = content.split('\n')
                new_lines = []
                inserted = False
                for line in lines:
                    new_lines.append(line)
                    if line.startswith("## Facebook Posts") and not inserted:
                        new_lines.append(entry)
                        inserted = True
                content = '\n'.join(new_lines)
            else:
                content += f"\n\n## Facebook Posts\n{entry}"
        else:
            content = f"# Dashboard\n\n## Facebook Posts\n{entry}\n"

        self.dashboard_file.write_text(content)
        self.log(f"Dashboard updated: {self.dashboard_file}")

    def save_state(self, action: str, post_id: str, message: str, status: str):
        """Save Facebook action state."""
        state = {
            "skill": SKILL_NAME,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "post_id": post_id,
            "message": message,
            "status": status,
            "mock_mode": self.mock_mode
        }

        states = []
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    states = json.load(f)
            except:
                states = []

        states.append(state)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(states, f, indent=2, ensure_ascii=False)
        self.log(f"State saved: {self.state_file}")

    def execute(self, action: str = "post", **kwargs) -> dict:
        """Execute Facebook skill."""
        self.log(f"\n{'='*60}")
        self.log(f"FACEBOOK SKILL - Action: {action}")
        self.log(f"{'='*60}")

        result = {"success": False, "action": action, "error": None}

        # Check connection
        self.log(f"\n[1/2] Checking Facebook connection...")
        if not self.check_connection():
            result["error"] = "Connection check failed"
            return result
        self.log("    [OK] Connection OK")

        # Execute action
        self.log(f"\n[2/2] Executing: {action}")
        
        if action == "post":
            message = kwargs.get("message", "")
            link = kwargs.get("link")
            if not message:
                result["error"] = "Message is required"
                self.log("    ERROR: No message provided")
                return result
            
            post_result = self.create_post(message, link)
            
            if post_result.get("success"):
                post_id = post_result.get("post_id")
                self.log(f"    [OK] Post created: {post_id}")
                self.update_dashboard("POST", post_id, message, "Success")
                self.save_state("POST", post_id, message, "Success")
                result["success"] = True
                result["post_id"] = post_id
                result["data"] = post_result
            else:
                result["error"] = post_result.get("error")
                self.log(f"    ERROR: {result['error']}")
        
        elif action == "get":
            limit = kwargs.get("limit", 5)
            posts_result = self.get_posts(limit)
            
            if posts_result.get("success"):
                self.log(f"    [OK] Retrieved {len(posts_result.get('data', []))} posts")
                result["success"] = True
                result["data"] = posts_result
            else:
                result["error"] = posts_result.get("error")
                self.log(f"    ERROR: {result['error']}")
        
        elif action == "check":
            page_info = self.get_page_info()
            
            if page_info.get("success"):
                data = page_info.get("data", {})
                self.log(f"    [OK] Page: {data.get('name')}")
                self.log(f"         Followers: {data.get('followers_count', 'N/A'):,}")
                self.log(f"         Likes: {data.get('likes', 'N/A'):,}")
                result["success"] = True
                result["data"] = page_info
            else:
                result["error"] = page_info.get("error")
                self.log(f"    ERROR: {result['error']}")
        
        elif action == "photo":
            photo_url = kwargs.get("photo_url", "")
            caption = kwargs.get("caption", "")
            if not photo_url:
                result["error"] = "Photo URL is required"
                self.log("    ERROR: No photo URL provided")
                return result
            
            photo_result = self.post_photo(photo_url, caption)
            
            if photo_result.get("success"):
                photo_id = photo_result.get("photo_id")
                self.log(f"    [OK] Photo posted: {photo_id}")
                result["success"] = True
                result["photo_id"] = photo_id
                result["data"] = photo_result
            else:
                result["error"] = photo_result.get("error")
                self.log(f"    ERROR: {result['error']}")
        
        elif action == "delete":
            post_id = kwargs.get("post_id", "")
            if not post_id:
                result["error"] = "Post ID is required"
                self.log("    ERROR: No post ID provided")
                return result
            
            delete_result = self.delete_post(post_id)
            
            if delete_result.get("success"):
                self.log(f"    [OK] Post deleted: {post_id}")
                result["success"] = True
                result["data"] = delete_result
            else:
                result["error"] = delete_result.get("error")
                self.log(f"    ERROR: {result['error']}")
        
        else:
            result["error"] = f"Unknown action: {action}"
            self.log(f"    ERROR: {result['error']}")

        self.log(f"\n{'='*60}")
        if result["success"]:
            self.log("FACEBOOK SKILL COMPLETED SUCCESSFULLY!")
        else:
            self.log(f"FACEBOOK SKILL FAILED: {result['error']}")
        self.log(f"{'='*60}\n")

        return result


def main():
    parser = argparse.ArgumentParser(description="Facebook Auto-Post Skill")
    parser.add_argument("message", nargs="?", help="Post message")
    parser.add_argument("--post", "-p", help="Create a new post")
    parser.add_argument("--get", "-g", type=int, nargs="?", const=5, help="Get recent posts (default: 5)")
    parser.add_argument("--check", "-c", action="store_true", help="Check Facebook connection")
    parser.add_argument("--photo", help="Post a photo (provide URL)")
    parser.add_argument("--caption", default="", help="Photo caption")
    parser.add_argument("--delete", help="Delete post by ID")
    parser.add_argument("--link", "-l", help="Link to include with post")

    args = parser.parse_args()

    skill = FacebookSkill()
    result = None

    if args.check:
        result = skill.execute("check")
    elif args.get is not None:
        result = skill.execute("get", limit=args.get)
    elif args.delete:
        result = skill.execute("delete", post_id=args.delete)
    elif args.photo:
        result = skill.execute("photo", photo_url=args.photo, caption=args.caption)
    elif args.post:
        result = skill.execute("post", message=args.post, link=args.link)
    elif args.message:
        result = skill.execute("post", message=args.message, link=args.link)
    else:
        print("Facebook Auto-Post Skill")
        print("=" * 60)
        print("\nUsage:")
        print("  python skills/facebook_skill.py \"Your message here\"")
        print("  python skills/facebook_skill.py --post \"Your message\"")
        print("  python skills/facebook_skill.py --get 5")
        print("  python skills/facebook_skill.py --check")
        print("  python skills/facebook_skill.py --photo \"https://example.com/image.jpg\" --caption \"Nice photo\"")
        print("  python skills/facebook_skill.py --delete \"post_id\"")
        print("\nExamples:")
        print('  python skills/facebook_skill.py "Hello from Gold Tier!"')
        print('  python skills/facebook_skill.py --post "New product launch!" --link "https://goldtier.example.com"')
        print("  python skills/facebook_skill.py --get 10")
        print("  python skills/facebook_skill.py --check")
        print("=" * 60)
        sys.exit(0)

    sys.exit(0 if result and result.get("success") else 1)


if __name__ == "__main__":
    main()
