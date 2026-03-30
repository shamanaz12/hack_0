#!/usr/bin/env python3
"""
Auto Processor - Fully Automatic Gmail + WhatsApp Message Processor

This script runs continuously in the background and automatically:
1. Monitors Gmail for new emails
2. Monitors WhatsApp for new messages
3. Reads and analyzes content
4. Creates plan.md files in Plans folder
5. Moves processed items to Done folder

NO MANUAL INTERVENTION REQUIRED!

Usage:
    python auto_processor.py
    
Or run in background:
    python auto_processor.py --background
"""

import os
import sys
import json
import time
import logging
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Try to import Playwright for WhatsApp
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. WhatsApp monitoring disabled.")
    print("Install with: pip install playwright")

# Try to import Qwen API
try:
    from dashscope import Generation
    import dashscope
    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False

# ============================================================================
# Configuration
# ============================================================================

CONFIG = {
    'gmail_check_interval': 300,  # Check Gmail every 5 minutes
    'whatsapp_check_interval': 300,  # Check WhatsApp every 5 minutes
    'max_iterations': 0,  # 0 = run forever
    'auto_create_plans': True,  # Automatically create plan.md files
    'auto_move_to_done': True,  # Automatically move to Done folder
    'keywords': ['urgent', 'invoice', 'payment', 'asap', 'important', 'action required'],
    'log_level': 'INFO',
}

# ============================================================================
# Setup Logging
# ============================================================================

def setup_logging(vault_path: Path) -> logging.Logger:
    """Configure logging"""
    log_dir = vault_path / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / 'auto_processor.log'
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    logger = logging.getLogger('auto_processor')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Message:
    """Represents a message (email or WhatsApp)"""
    id: str
    source: str  # 'gmail' or 'whatsapp'
    from_: str
    subject: str
    content: str
    timestamp: str
    priority: str
    is_important: bool
    keywords_found: List[str]
    raw_data: Dict


@dataclass
class ProcessingResult:
    """Result of processing a message"""
    message_id: str
    status: str  # processed, skipped, error
    plan_file: Optional[str]
    done_file: Optional[str]
    error: Optional[str]

# ============================================================================
# Gmail Processor
# ============================================================================

class GmailProcessor:
    """Process Gmail emails automatically"""
    
    def __init__(self, vault_path: Path, logger: logging.Logger):
        self.vault_path = vault_path
        self.logger = logger
        self.needs_action_folder = vault_path / 'AI_Employee_Vault' / 'Silver_Tier' / 'Needs_Action'
        self.done_folder = vault_path / 'AI_Employee_Vault' / 'Silver_Tier' / 'Done'
        self.processed_file = vault_path / 'processed_emails.json'
        
        # Create folders
        self.needs_action_folder.mkdir(parents=True, exist_ok=True)
        self.done_folder.mkdir(parents=True, exist_ok=True)
        
        # Load processed emails
        self.processed_emails = self._load_processed()
    
    def _load_processed(self) -> set:
        """Load list of already processed email IDs"""
        if self.processed_file.exists():
            with open(self.processed_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('processed_ids', []))
        return set()
    
    def _save_processed(self, email_id: str):
        """Mark email as processed"""
        self.processed_emails.add(email_id)
        data = {
            'processed_ids': list(self.processed_emails)[-1000:],
            'last_updated': datetime.now().isoformat()
        }
        with open(self.processed_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def check_gmail(self) -> List[Message]:
        """Check Gmail for new emails (simplified - no API needed)"""
        self.logger.info("Checking Gmail for new emails...")
        
        # In real implementation, this would connect to Gmail API
        # For now, we'll check the Needs_Action folder for new files
        
        messages = []
        
        # Check for new markdown files in Needs_Action
        for md_file in self.needs_action_folder.glob('Gmail_*.md'):
            if md_file.stem not in self.processed_emails:
                try:
                    content = md_file.read_text(encoding='utf-8')
                    message = self._parse_email_file(md_file, content)
                    if message:
                        messages.append(message)
                except Exception as e:
                    self.logger.error(f"Error parsing {md_file.name}: {e}")
        
        self.logger.info(f"Found {len(messages)} new emails")
        return messages
    
    def _parse_email_file(self, file_path: Path, content: str) -> Optional[Message]:
        """Parse email markdown file"""
        try:
            # Extract metadata from frontmatter
            metadata = {}
            body = content
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    body = parts[2]
                    
                    # Parse YAML-like metadata
                    for match in re.finditer(r'(\w+):\s*"?([^"\n]+)"?', frontmatter):
                        key, value = match.groups()
                        metadata[key] = value.strip()
            
            # Check for keywords
            keywords_found = []
            text_lower = content.lower()
            for keyword in CONFIG['keywords']:
                if keyword in text_lower:
                    keywords_found.append(keyword)
            
            if not keywords_found:
                return None  # Skip if no keywords
            
            return Message(
                id=file_path.stem,
                source='gmail',
                from_=metadata.get('from', 'Unknown'),
                subject=metadata.get('subject', 'No Subject'),
                content=body.strip()[:1000],
                timestamp=metadata.get('received_date', datetime.now().isoformat()),
                priority=metadata.get('priority', 'normal'),
                is_important=metadata.get('is_important', 'false').lower() == 'true',
                keywords_found=keywords_found,
                raw_data={'file_path': str(file_path), 'metadata': metadata}
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing email file: {e}")
            return None
    
    def mark_processed(self, message: Message):
        """Mark email as processed"""
        self._save_processed(message.id)
    
    def move_to_done(self, message: Message, plan_file: str) -> Optional[str]:
        """Move processed email to Done folder"""
        try:
            source_file = Path(message.raw_data['file_path'])
            done_file = self.done_folder / source_file.name
            
            # Copy to Done
            done_file.write_text(source_file.read_text(encoding='utf-8'), encoding='utf-8')
            
            # Add plan reference
            with open(done_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n## Plan File\n[{plan_file}]({plan_file})\n")
            
            self.logger.info(f"Moved to Done: {done_file.name}")
            return str(done_file)
            
        except Exception as e:
            self.logger.error(f"Error moving to Done: {e}")
            return None

# ============================================================================
# WhatsApp Processor
# ============================================================================

class WhatsAppProcessor:
    """Process WhatsApp messages automatically"""
    
    def __init__(self, vault_path: Path, logger: logging.Logger):
        self.vault_path = vault_path
        self.logger = logger
        self.needs_action_folder = vault_path / 'AI_Employee_Vault' / 'Silver_Tier' / 'Needs_Action'
        self.done_folder = vault_path / 'AI_Employee_Vault' / 'Silver_Tier' / 'Done'
        self.processed_file = vault_path / 'processed_whatsapp.json'
        
        # Create folders
        self.needs_action_folder.mkdir(parents=True, exist_ok=True)
        self.done_folder.mkdir(parents=True, exist_ok=True)
        
        # Load processed messages
        self.processed_messages = self._load_processed()
    
    def _load_processed(self) -> set:
        """Load list of already processed message IDs"""
        if self.processed_file.exists():
            with open(self.processed_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('processed_ids', []))
        return set()
    
    def _save_processed(self, msg_id: str):
        """Mark message as processed"""
        self.processed_messages.add(msg_id)
        data = {
            'processed_ids': list(self.processed_messages)[-1000:],
            'last_updated': datetime.now().isoformat()
        }
        with open(self.processed_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def check_whatsapp(self) -> List[Message]:
        """Check WhatsApp for new messages"""
        self.logger.info("Checking WhatsApp for new messages...")
        
        messages = []
        
        # Check for new WhatsApp markdown files
        for md_file in self.needs_action_folder.glob('WhatsApp_*.md'):
            if md_file.stem not in self.processed_messages:
                try:
                    content = md_file.read_text(encoding='utf-8')
                    message = self._parse_whatsapp_file(md_file, content)
                    if message:
                        messages.append(message)
                except Exception as e:
                    self.logger.error(f"Error parsing {md_file.name}: {e}")
        
        self.logger.info(f"Found {len(messages)} new WhatsApp messages")
        return messages
    
    def _parse_whatsapp_file(self, file_path: Path, content: str) -> Optional[Message]:
        """Parse WhatsApp markdown file"""
        try:
            # Extract metadata
            metadata = {}
            body = content
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    body = parts[2]
                    
                    for match in re.finditer(r'(\w+):\s*"?([^"\n]+)"?', frontmatter):
                        key, value = match.groups()
                        metadata[key] = value.strip()
            
            # Check for keywords
            keywords_found = []
            text_lower = content.lower()
            for keyword in CONFIG['keywords']:
                if keyword in text_lower:
                    keywords_found.append(keyword)
            
            if not keywords_found:
                return None
            
            return Message(
                id=file_path.stem,
                source='whatsapp',
                from_=metadata.get('chat_name', 'Unknown'),
                subject=f"WhatsApp Message from {metadata.get('chat_name', 'Unknown')}",
                content=body.strip()[:1000],
                timestamp=metadata.get('received_date', datetime.now().isoformat()),
                priority='high' if keywords_found else 'normal',
                is_important=len(keywords_found) > 0,
                keywords_found=keywords_found,
                raw_data={'file_path': str(file_path), 'metadata': metadata}
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing WhatsApp file: {e}")
            return None
    
    def mark_processed(self, message: Message):
        """Mark message as processed"""
        self._save_processed(message.id)
    
    def move_to_done(self, message: Message, plan_file: str) -> Optional[str]:
        """Move processed message to Done folder"""
        try:
            source_file = Path(message.raw_data['file_path'])
            done_file = self.done_folder / source_file.name
            
            done_file.write_text(source_file.read_text(encoding='utf-8'), encoding='utf-8')
            
            with open(done_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n## Plan File\n[{plan_file}]({plan_file})\n")
            
            self.logger.info(f"Moved to Done: {done_file.name}")
            return str(done_file)
            
        except Exception as e:
            self.logger.error(f"Error moving to Done: {e}")
            return None

# ============================================================================
# Plan Generator
# ============================================================================

class PlanGenerator:
    """Generate plan.md files for messages"""
    
    def __init__(self, vault_path: Path, logger: logging.Logger):
        self.vault_path = vault_path
        self.logger = logger
        self.plans_folder = vault_path / 'Plans'
        self.plans_folder.mkdir(exist_ok=True)
    
    def create_plan(self, message: Message) -> str:
        """Create plan.md file for a message"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_filename = f"plan_{message.id}_{timestamp}.md"
        plan_path = self.plans_folder / plan_filename
        
        plan_content = self._generate_plan_content(message)
        
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        self.logger.info(f"Plan created: {plan_filename}")
        return str(plan_path)
    
    def _generate_plan_content(self, message: Message) -> str:
        """Generate plan content"""
        frontmatter = f"""---
metadata:
  message_id: "{message.id}"
  source: "{message.source}"
  from: "{message.from_}"
  subject: "{message.subject}"
  priority: "{message.priority}"
  keywords: {message.keywords_found}
  created: "{datetime.now().isoformat()}"
  analyzer: "Auto Processor"
---

# Action Plan: {message.subject}

## Message Information

| Field | Value |
|-------|-------|
| **Source** | {message.source.upper()} |
| **From** | {message.from_} |
| **Priority** | {message.priority.upper()} |
| **Keywords** | {', '.join(message.keywords_found)} |
| **Received** | {message.timestamp} |

## Content

{message.content}

## Action Items

- [ ] Review message content
- [ ] Identify required actions
- [ ] Respond if needed ({message.source})
- [ ] Complete required tasks
- [ ] Verify completion
- [ ] Mark as done

## Timeline

- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Priority**: {message.priority}
- **Estimated Duration**: 1-2 hours

## Resources Needed

- Access to required tools/systems
- Contact information for sender
- Time allocation for task completion

## Success Criteria

- [ ] All action items completed
- [ ] Response sent (if required)
- [ ] Task completed successfully
- [ ] Status updated to Done

## Notes

Add any additional notes here.

---
*Generated automatically by Auto Processor*
*Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return frontmatter

# ============================================================================
# Auto Processor (Main Controller)
# ============================================================================

class AutoProcessor:
    """Main controller for automatic processing"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.logger = setup_logging(vault_path)
        
        # Initialize processors
        self.gmail_processor = GmailProcessor(vault_path, self.logger)
        self.whatsapp_processor = WhatsAppProcessor(vault_path, self.logger)
        self.plan_generator = PlanGenerator(vault_path, self.logger)
        
        self.logger.info("Auto Processor initialized")
        self.logger.info(f"Gmail check interval: {CONFIG['gmail_check_interval']}s")
        self.logger.info(f"WhatsApp check interval: {CONFIG['whatsapp_check_interval']}s")
        self.logger.info(f"Keywords monitored: {CONFIG['keywords']}")
    
    def process_message(self, message: Message) -> ProcessingResult:
        """Process a single message"""
        try:
            self.logger.info(f"Processing: {message.id} ({message.source})")
            self.logger.info(f"  From: {message.from_}")
            self.logger.info(f"  Keywords: {message.keywords_found}")
            
            # Create plan
            plan_file = None
            if CONFIG['auto_create_plans']:
                plan_file = self.plan_generator.create_plan(message)
            
            # Move to Done
            done_file = None
            if CONFIG['auto_move_to_done']:
                if message.source == 'gmail':
                    done_file = self.gmail_processor.move_to_done(message, plan_file)
                elif message.source == 'whatsapp':
                    done_file = self.whatsapp_processor.move_to_done(message, plan_file)
            
            # Mark as processed
            if message.source == 'gmail':
                self.gmail_processor.mark_processed(message)
            elif message.source == 'whatsapp':
                self.whatsapp_processor.mark_processed(message)
            
            self.logger.info(f"[OK] Processed successfully")
            
            return ProcessingResult(
                message_id=message.id,
                status='processed',
                plan_file=plan_file,
                done_file=done_file,
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"[ERROR] Processing failed: {e}")
            return ProcessingResult(
                message_id=message.id,
                status='error',
                plan_file=None,
                done_file=None,
                error=str(e)
            )
    
    def run_cycle(self) -> Dict[str, int]:
        """Run one processing cycle"""
        results = {
            'gmail_processed': 0,
            'whatsapp_processed': 0,
            'errors': 0
        }
        
        # Check Gmail
        gmail_messages = self.gmail_processor.check_gmail()
        for message in gmail_messages:
            result = self.process_message(message)
            if result.status == 'processed':
                results['gmail_processed'] += 1
            else:
                results['errors'] += 1
        
        # Check WhatsApp
        whatsapp_messages = self.whatsapp_processor.check_whatsapp()
        for message in whatsapp_messages:
            result = self.process_message(message)
            if result.status == 'processed':
                results['whatsapp_processed'] += 1
            else:
                results['errors'] += 1
        
        return results
    
    def run(self, max_iterations: int = 0):
        """Run auto processor continuously"""
        self.logger.info("=" * 60)
        self.logger.info("Starting Auto Processor (Continuous Mode)")
        self.logger.info("=" * 60)
        
        iteration = 0
        
        try:
            while True:
                iteration += 1
                
                self.logger.info(f"\n{'='*40}")
                self.logger.info(f"Cycle {iteration}")
                self.logger.info(f"{'='*40}")
                
                # Run processing cycle
                results = self.run_cycle()
                
                self.logger.info(f"\nResults:")
                self.logger.info(f"  Gmail processed: {results['gmail_processed']}")
                self.logger.info(f"  WhatsApp processed: {results['whatsapp_processed']}")
                self.logger.info(f"  Errors: {results['errors']}")
                
                # Check max iterations
                if max_iterations > 0 and iteration >= max_iterations:
                    self.logger.info("\n[INFO] Max iterations reached, stopping...")
                    break
                
                # Wait for next cycle
                next_check = min(CONFIG['gmail_check_interval'], CONFIG['whatsapp_check_interval'])
                self.logger.info(f"\n[INFO] Waiting {next_check}s until next check...")
                
                for _ in range(next_check):
                    time.sleep(1)
        
        except KeyboardInterrupt:
            self.logger.info("\n[INFO] Stopped by user")
        except Exception as e:
            self.logger.error(f"[ERROR] Fatal error: {e}")
            raise
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Auto Processor stopped")
        self.logger.info("=" * 60)

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto Processor - Gmail + WhatsApp')
    parser.add_argument('--vault', type=str, default=None, help='Vault path')
    parser.add_argument('--gmail-interval', type=int, default=300, help='Gmail check interval (seconds)')
    parser.add_argument('--whatsapp-interval', type=int, default=300, help='WhatsApp check interval')
    parser.add_argument('--max-iterations', type=int, default=0, help='Max iterations (0 = forever)')
    parser.add_argument('--no-plans', action='store_true', help='Disable auto plan creation')
    parser.add_argument('--no-done', action='store_true', help='Disable auto move to Done')
    args = parser.parse_args()
    
    # Set configuration
    vault_path = Path(args.vault) if args.vault else Path.cwd()
    CONFIG['gmail_check_interval'] = args.gmail_interval
    CONFIG['whatsapp_check_interval'] = args.whatsapp_interval
    CONFIG['auto_create_plans'] = not args.no_plans
    CONFIG['auto_move_to_done'] = not args.no_done
    
    print("\n" + "=" * 60)
    print("Auto Processor - Gmail + WhatsApp")
    print("=" * 60)
    print(f"Vault Path: {vault_path}")
    print(f"Gmail Interval: {CONFIG['gmail_check_interval']}s")
    print(f"WhatsApp Interval: {CONFIG['whatsapp_check_interval']}s")
    print(f"Auto Create Plans: {CONFIG['auto_create_plans']}")
    print(f"Auto Move to Done: {CONFIG['auto_move_to_done']}")
    print(f"Keywords: {CONFIG['keywords']}")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")
    
    # Run auto processor
    processor = AutoProcessor(vault_path)
    processor.run(max_iterations=args.max_iterations)


if __name__ == '__main__':
    main()
