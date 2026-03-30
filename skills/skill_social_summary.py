#!/usr/bin/env python3
"""
Skill: Social Summary
Generates and stores summaries of social media posts.

Trigger:
- Run after a successful post on Instagram or Facebook

Function:
1. Receive post data from MCP servers (platform, content, timestamp)
2. Validate input (platform, content, timestamp)
3. Generate summary entry in markdown format
4. Save to AI_Employee_Vault/Reports/social.log.md (append mode)
5. Prevent duplicate entries
6. Log success/errors to logs/system.log and logs/errors.log
7. Call error_recovery on failures (max 1 retry)

Integration:
- Uses existing MCP servers only
- Does not modify Instagram/Facebook posting logic
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import re

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import error recovery
try:
    from .skill_error_recovery import ErrorRecoverySkill, log_error
except ImportError:
    from skill_error_recovery import ErrorRecoverySkill, log_error


@dataclass
class SocialPostSummary:
    """Social post summary record"""
    platform: str  # 'facebook' or 'instagram'
    content: str
    timestamp: str
    summary_id: str
    created_at: str
    content_preview: str = ""
    character_count: int = 0
    hashtag_count: int = 0
    mention_count: int = 0


class SocialSummarySkill:
    """
    Social Summary Skill
    Generates and stores summaries of social media posts
    """

    def __init__(self, vault_path: str = None):
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent

        # Folders
        self.reports_folder = self.vault_path / 'AI_Employee_Vault' / 'Reports'
        self.logs_folder = self.vault_path / 'logs'

        # Create folders
        self.reports_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)

        # Files
        self.social_log = self.reports_folder / 'social.log.md'
        self.system_log = self.logs_folder / 'system.log'
        self.error_log = self.logs_folder / 'errors.log'
        self.state_file = self.reports_folder / 'social_summary_state.json'

        # Error recovery
        self.error_recovery = ErrorRecoverySkill(str(self.vault_path))

        # Valid platforms
        self.valid_platforms = ['facebook', 'instagram']

        # Load state (for duplicate prevention)
        self.loaded_hashes: set = set()
        self.load_state()

    def load_state(self):
        """Load state for duplicate prevention"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.loaded_hashes = set(state.get('posted_hashes', []))
            except Exception as e:
                self._log_error(f"Failed to load state: {e}")
                self.loaded_hashes = set()

    def save_state(self):
        """Save state for duplicate prevention"""
        state = {
            'posted_hashes': list(self.loaded_hashes),
            'last_updated': datetime.now().isoformat()
        }

        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self._log_error(f"Failed to save state: {e}")

    def validate_input(self, platform: str, content: str, timestamp: str) -> Tuple[bool, str]:
        """
        Validate input data

        Args:
            platform: Platform name (facebook/instagram)
            content: Post content/caption
            timestamp: Post timestamp

        Returns:
            (is_valid, error_message) tuple
        """
        # Validate platform
        if not platform or platform.lower() not in self.valid_platforms:
            return False, f"Invalid platform: {platform}. Must be one of: {self.valid_platforms}"

        # Validate content
        if not content or not content.strip():
            return False, "Content cannot be empty"

        # Validate timestamp
        if not timestamp:
            return False, "Timestamp is required"

        # Validate timestamp format (ISO format or parseable)
        try:
            if isinstance(timestamp, str):
                # Try to parse ISO format
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return False, f"Invalid timestamp format: {timestamp}. Use ISO format (YYYY-MM-DDTHH:MM:SS)"

        return True, ""

    def generate_content_preview(self, content: str, max_length: int = 100) -> str:
        """Generate a short preview of content"""
        # Clean content (remove extra whitespace, newlines)
        cleaned = re.sub(r'\s+', ' ', content.strip())

        if len(cleaned) <= max_length:
            return cleaned

        return cleaned[:max_length - 3] + "..."

    def count_hashtags(self, content: str) -> int:
        """Count hashtags in content"""
        return len(re.findall(r'#\w+', content))

    def count_mentions(self, content: str) -> int:
        """Count mentions in content"""
        return len(re.findall(r'@\w+', content))

    def generate_summary_id(self, platform: str, content: str, timestamp: str) -> str:
        """Generate unique summary ID (also used for duplicate detection)"""
        unique_string = f"{platform}:{content}:{timestamp}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:16]

    def is_duplicate(self, summary_id: str) -> bool:
        """Check if this post is a duplicate"""
        return summary_id in self.loaded_hashes

    def create_summary(self, platform: str, content: str, timestamp: str) -> Optional[SocialPostSummary]:
        """
        Create a social post summary

        Args:
            platform: Platform name (facebook/instagram)
            content: Post content/caption
            timestamp: Post timestamp

        Returns:
            SocialPostSummary object or None if duplicate/invalid
        """
        # Validate input
        is_valid, error_message = self.validate_input(platform, content, timestamp)

        if not is_valid:
            task_id = f"social_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            log_error(
                task_name='social_summary_validate',
                task_id=task_id,
                error_message=error_message,
                error_type='ValidationError',
                task_data={
                    'platform': platform,
                    'content_length': len(content) if content else 0,
                    'timestamp': timestamp
                }
            )
            self._log_error(f"Validation failed: {error_message}")
            return None

        # Generate summary ID
        summary_id = self.generate_summary_id(platform, content, timestamp)

        # Check for duplicates
        if self.is_duplicate(summary_id):
            self._log_system(f"Duplicate post detected: {platform} at {timestamp}")
            return None

        # Create summary
        summary = SocialPostSummary(
            platform=platform.lower(),
            content=content,
            timestamp=timestamp,
            summary_id=summary_id,
            created_at=datetime.now().isoformat(),
            content_preview=self.generate_content_preview(content),
            character_count=len(content),
            hashtag_count=self.count_hashtags(content),
            mention_count=self.count_mentions(content)
        )

        return summary

    def save_summary(self, summary: SocialPostSummary) -> bool:
        """
        Save summary to social.log.md (append mode)

        Args:
            summary: SocialPostSummary object

        Returns:
            True if saved successfully
        """
        try:
            # Generate markdown entry
            entry = self._format_summary_entry(summary)

            # Check if file exists
            file_exists = self.social_log.exists()

            # Open in append mode
            with open(self.social_log, 'a', encoding='utf-8') as f:
                # If file is new, add header
                if not file_exists:
                    header = """# Social Media Posts Log

This file contains a log of all social media posts made through the AI Employee System.

---

"""
                    f.write(header)

                f.write(entry)

            # Update state (add hash to prevent duplicates)
            self.loaded_hashes.add(summary.summary_id)
            self.save_state()

            # Log success
            self._log_system(f"Social summary saved: {summary.platform} post at {summary.timestamp}")

            return True

        except Exception as e:
            error_message = f"Failed to save social summary: {e}"
            self._log_error(error_message)

            # Call error recovery
            task_id = f"social_summary_save_{summary.summary_id}"
            log_error(
                task_name='social_summary_save',
                task_id=task_id,
                error_message=error_message,
                error_type='SaveError',
                task_data={'summary': asdict(summary)}
            )

            return False

    def _format_summary_entry(self, summary: SocialPostSummary) -> str:
        """Format summary as markdown entry"""
        platform_icon = "📘" if summary.platform == 'facebook' else "📷"

        entry = f"""## {platform_icon} {summary.platform.title()} Post

**Post ID:** {summary.summary_id}
**Date:** {summary.timestamp}
**Character Count:** {summary.character_count}
**Hashtags:** {summary.hashtag_count}
**Mentions:** {summary.mention_count}

### Content Preview

{summary.content_preview}

### Full Content

```
{summary.content}
```

---

"""
        return entry

    def log_post(self, platform: str, content: str, timestamp: str = None) -> Dict[str, Any]:
        """
        Main entry point - Log a social media post

        Args:
            platform: Platform name (facebook/instagram)
            content: Post content/caption
            timestamp: Post timestamp (defaults to now)

        Returns:
            Dict with status and details
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        # Create summary
        summary = self.create_summary(platform, content, timestamp)

        if summary is None:
            return {
                'success': False,
                'message': 'Invalid input or duplicate post',
                'platform': platform,
                'timestamp': timestamp
            }

        # Save summary
        success = self.save_summary(summary)

        if success:
            return {
                'success': True,
                'message': f'Social summary saved for {platform} post',
                'summary_id': summary.summary_id,
                'platform': summary.platform,
                'timestamp': summary.timestamp,
                'character_count': summary.character_count,
                'hashtag_count': summary.hashtag_count,
                'mention_count': summary.mention_count
            }
        else:
            return {
                'success': False,
                'message': 'Failed to save social summary',
                'platform': platform,
                'timestamp': timestamp
            }

    def _log_system(self, message: str):
        """Log to system.log"""
        log_line = f"[{datetime.now().isoformat()}] [SOCIAL_SUMMARY] [INFO] {message}\n"

        try:
            with open(self.system_log, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except Exception:
            pass

    def _log_error(self, message: str):
        """Log to errors.log"""
        log_line = f"[{datetime.now().isoformat()}] [SOCIAL_SUMMARY] [ERROR] {message}\n"

        try:
            with open(self.error_log, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except Exception:
            pass

    def get_post_count(self, platform: str = None) -> int:
        """Get total post count, optionally filtered by platform"""
        if not self.social_log.exists():
            return 0

        try:
            with open(self.social_log, 'r', encoding='utf-8') as f:
                content = f.read()

            if platform:
                return len(re.findall(f'## {platform.title()} Post', content, re.IGNORECASE))
            else:
                return len(re.findall(r'## .* Post', content))
        except Exception:
            return 0

    def get_recent_posts(self, limit: int = 10) -> List[Dict]:
        """Get recent posts from log"""
        if not self.social_log.exists():
            return []

        posts = []
        try:
            with open(self.social_log, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find all post sections
            pattern = r'## (.*?) Post\n\n\*\*Post ID:\*\* (.*?)\n\*\*Date:\*\* (.*?)\n'
            matches = re.findall(pattern, content, re.IGNORECASE)

            for match in reversed(matches[-limit:]):
                posts.append({
                    'platform': match[0].strip(),
                    'post_id': match[1].strip(),
                    'date': match[2].strip()
                })
        except Exception:
            pass

        return posts


# Global instance
_social_summary = None


def get_skill() -> SocialSummarySkill:
    """Get or create social summary skill instance"""
    global _social_summary
    if _social_summary is None:
        _social_summary = SocialSummarySkill()
    return _social_summary


def log_social_post(platform: str, content: str, timestamp: str = None) -> Dict:
    """
    Log a social media post

    Args:
        platform: Platform name ('facebook' or 'instagram')
        content: Post content/caption
        timestamp: Post timestamp (optional, defaults to now)

    Returns:
        Dict with status and details
    """
    skill = get_skill()
    return skill.log_post(platform, content, timestamp)


def get_social_stats() -> Dict:
    """Get social media posting statistics"""
    skill = get_skill()
    return {
        'total_posts': skill.get_post_count(),
        'facebook_posts': skill.get_post_count('facebook'),
        'instagram_posts': skill.get_post_count('instagram'),
        'recent_posts': skill.get_recent_posts(5)
    }


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Social Summary Skill')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Log post command
    log_parser = subparsers.add_parser('log', help='Log a social media post')
    log_parser.add_argument('platform', type=str, choices=['facebook', 'instagram'], help='Platform')
    log_parser.add_argument('content', type=str, help='Post content/caption')
    log_parser.add_argument('--timestamp', type=str, help='Timestamp (ISO format)')

    # Stats command
    subparsers.add_parser('stats', help='Get social media statistics')

    # Recent command
    recent_parser = subparsers.add_parser('recent', help='Get recent posts')
    recent_parser.add_argument('--limit', type=int, default=10, help='Number of posts to show')

    args = parser.parse_args()

    skill = SocialSummarySkill()

    if args.command == 'log':
        result = skill.log_post(args.platform, args.content, args.timestamp)
        if result['success']:
            print(f"\n[OK] Social summary saved")
            print(f"  Platform: {result['platform']}")
            print(f"  Summary ID: {result['summary_id']}")
            print(f"  Timestamp: {result['timestamp']}")
            print(f"  Characters: {result['character_count']}")
            print(f"  Hashtags: {result['hashtag_count']}")
            print(f"  Mentions: {result['mention_count']}")
        else:
            print(f"\n[ERROR] {result['message']}")

    elif args.command == 'stats':
        stats = get_social_stats()
        print(f"\n=== Social Media Statistics ===")
        print(f"  Total Posts: {stats['total_posts']}")
        print(f"  Facebook Posts: {stats['facebook_posts']}")
        print(f"  Instagram Posts: {stats['instagram_posts']}")

    elif args.command == 'recent':
        posts = skill.get_recent_posts(args.limit)
        print(f"\n=== Recent Posts ({len(posts)}) ===")
        for post in posts:
            icon = "📘" if post['platform'].lower() == 'facebook' else "📷"
            print(f"  {icon} [{post['date']}] {post['post_id']}")

    else:
        parser.print_help()
        print("\nExamples:")
        print('  python skills/social_summary.py log facebook "Hello World!"')
        print('  python skills/social_summary.py log instagram "Nice day #sunset"')
        print('  python skills/social_summary.py stats')
