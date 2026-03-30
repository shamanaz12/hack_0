"""
Gmail Watcher for Silver Tier - IMAP Version with Status Tracking
Monitors Gmail inbox for unread important emails
Tracks status, avoids duplicates, creates daily reports
"""
import os
import sys
import time
import json
import logging
import email
import imaplib
import hashlib
from datetime import datetime
from pathlib import Path

# Configure logging
log_dir = Path(__file__).parent / 'logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'gmail_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StatusTracker:
    """Tracks watcher status and processed emails"""
    
    def __init__(self, status_file):
        self.status_file = status_file
        self.status = self.load_status()
    
    def load_status(self):
        """Load status from file"""
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'total_runs': 0,
            'total_emails_processed': 0,
            'last_run': None,
            'processed_email_ids': [],
            'daily_stats': {}
        }
    
    def save_status(self):
        """Save status to file"""
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(self.status, f, indent=2, ensure_ascii=False)
    
    def add_run(self, emails_processed):
        """Add a run to status"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        self.status['total_runs'] += 1
        self.status['total_emails_processed'] += len(emails_processed)
        self.status['last_run'] = datetime.now().isoformat()
        
        # Add to daily stats
        if today not in self.status['daily_stats']:
            self.status['daily_stats'][today] = {
                'runs': 0,
                'emails_processed': 0
            }
        self.status['daily_stats'][today]['runs'] += 1
        self.status['daily_stats'][today]['emails_processed'] += len(emails_processed)
        
        # Track processed email IDs
        for email_id in emails_processed:
            if email_id not in self.status['processed_email_ids']:
                self.status['processed_email_ids'].append(email_id)
        
        # Keep only last 1000 email IDs to avoid huge file
        self.status['processed_email_ids'] = self.status['processed_email_ids'][-1000:]
        
        self.save_status()
    
    def is_email_processed(self, email_id):
        """Check if email was already processed"""
        return email_id in self.status['processed_email_ids']
    
    def get_summary(self):
        """Get status summary"""
        return f"""
╔══════════════════════════════════════════════════╗
║  GMAIL WATCHER STATUS                            ║
╠══════════════════════════════════════════════════╣
║  Total Runs: {self.status['total_runs']:<35}║
║  Total Emails Processed: {self.status['total_emails_processed']:<27}║
║  Last Run: {self.status['last_run'] or 'Never':<35}║
╠══════════════════════════════════════════════════╣
║  DAILY STATISTICS:                               ║
╚══════════════════════════════════════════════════╝
"""


class GmailWatcher:
    """Base Gmail Watcher class using IMAP with status tracking"""
    
    def __init__(self, email_address, app_password, status_file='watcher_status.json'):
        self.email_address = email_address
        self.app_password = app_password
        self.mail = None
        self.status_tracker = StatusTracker(status_file)
    
    def connect(self):
        """Connect to Gmail IMAP server"""
        try:
            self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
            password_clean = self.app_password.replace(' ', '')
            self.mail.login(self.email_address, password_clean)
            self.mail.select('INBOX')
            logger.info("Connected to Gmail")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def get_unread_emails(self, max_results=20):
        """Fetch unread emails"""
        if not self.mail:
            if not self.connect():
                return []
        
        try:
            status, messages = self.mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            
            if not email_ids:
                return []
            
            return email_ids[-max_results:]
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def get_email_details(self, msg_id):
        """Get email details"""
        try:
            status, msg_data = self.mail.fetch(msg_id, '(RFC822)')
            email_message = email.message_from_bytes(msg_data[0][1])
            
            email_data = {
                'id': msg_id.decode(),
                'from': email_message.get('From', 'Unknown'),
                'subject': email_message.get('Subject', 'No Subject'),
                'date': email_message.get('Date', ''),
                'snippet': '',
                'priority': 'normal',
                'is_important': False
            }
            
            # Get email body snippet
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == 'text/plain':
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            email_data['snippet'] = body[:200]
                        except:
                            pass
                        break
            else:
                try:
                    body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                    email_data['snippet'] = body[:200]
                except:
                    pass
            
            # Check priority
            subject_lower = email_data['subject'].lower()
            if any(kw in subject_lower for kw in ['urgent', 'asap', 'important', 'priority']):
                email_data['priority'] = 'high'
                email_data['is_important'] = True
            
            return email_data
        except Exception as e:
            logger.error(f"Error getting email details: {e}")
            return None
    
    def create_markdown_file(self, email_data, output_folder):
        """Create markdown file with metadata"""
        sanitized_subject = "".join(
            c for c in email_data['subject'] if c.isalnum() or c in (' ', '-', '_')
        ).rstrip()[:50] or "untitled"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Gmail_{timestamp}_{sanitized_subject}.md"
        filepath = os.path.join(output_folder, filename)
        
        content = f"""---
metadata:
  from: "{email_data['from']}"
  subject: "{email_data['subject']}"
  snippet: "{email_data['snippet'][:200]}"
  priority: "{email_data['priority']}"
  is_important: {email_data['is_important']}
  email_id: "{email_data['id']}"
  received_date: "{email_data['date']}"
  processed_at: "{datetime.now().isoformat()}"
  tier: "Silver"
---

# Email: {email_data['subject']}

## Metadata
| Field | Value |
|-------|-------|
| **From** | {email_data['from']} |
| **Priority** | {email_data['priority'].upper()} |
| **Important** | {"Yes" if email_data['is_important'] else "No"} |
| **Received** | {email_data['date']} |

## Snippet
{email_data['snippet']}

## Action Items
- [ ] Review email content
- [ ] Determine required response
- [ ] Take necessary action
- [ ] Update status
- [ ] Close when completed

---
*Generated by Silver Tier Gmail Watcher*
"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Created: {filename}")
            return filepath
        except Exception as e:
            logger.error(f"Error creating file: {e}")
            return None
    
    def process_emails(self, output_folder):
        """Process unread emails with duplicate check"""
        messages = self.get_unread_emails(max_results=20)
        
        if not messages:
            logger.info("No unread emails found")
            return []
        
        processed = []
        skipped = 0
        
        for msg_id in messages:
            email_id = msg_id.decode()
            
            # Skip if already processed
            if self.status_tracker.is_email_processed(email_id):
                skipped += 1
                continue
            
            email_data = self.get_email_details(msg_id)
            if email_data:
                logger.info(f"Processing: {email_data['from']} - {email_data['subject']}")
                logger.info(f"  Priority: {email_data['priority']}, Important: {email_data['is_important']}")
                
                filepath = self.create_markdown_file(email_data, output_folder)
                if filepath:
                    processed.append(email_id)
        
        # Update status
        self.status_tracker.add_run(processed)
        
        logger.info(f"Processed: {len(processed)}, Skipped (duplicates): {skipped}")
        return processed
    
    def print_status(self):
        """Print current status"""
        print(self.status_tracker.get_summary())
    
    def create_daily_report(self, output_folder):
        """Create daily summary report"""
        today = datetime.now().strftime('%Y-%m-%d')
        report_file = os.path.join(output_folder, f'Daily_Report_{today}.md')
        
        stats = self.status_tracker.status['daily_stats'].get(today, {'runs': 0, 'emails_processed': 0})
        
        content = f"""# Daily Report - {today}

## Summary
| Metric | Value |
|--------|-------|
| **Total Runs** | {stats['runs']} |
| **Emails Processed** | {stats['emails_processed']} |
| **Status** | Active |

## Files Created Today
"""
        # List today's files
        today_files = []
        for f in os.listdir(output_folder):
            if f.startswith(f'Gmail_{today.replace("-", "")}'):
                today_files.append(f)
        
        for f in sorted(today_files):
            content += f"- [ ] {f}\n"
        
        content += f"""
## Notes
- All emails automatically processed from Gmail
- Files saved in Needs_Action folder for review
- Status tracked in watcher_status.json

---
*Generated by Silver Tier Gmail Watcher*
"""
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Daily report created: {report_file}")
            return report_file
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            return None


class SilverTierGmailWatcher(GmailWatcher):
    """Silver Tier specific watcher"""
    
    def __init__(self):
        silver_tier_path = Path(__file__).parent / 'AI_Employee_Vault' / 'Silver_Tier'
        config_path = silver_tier_path / 'gmail_config.json'
        status_path = silver_tier_path / 'watcher_status.json'
        self.needs_action_folder = silver_tier_path / 'Needs_Action'
        
        os.makedirs(self.needs_action_folder, exist_ok=True)
        
        # Load config
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            email_address = config.get('email', '')
            app_password = config.get('app_password', '')
        else:
            logger.error("Config file not found!")
            email_address = ''
            app_password = ''
        
        super().__init__(email_address, app_password, str(status_path))
    
    def run_once(self):
        """Single run"""
        logger.info("Running Silver Tier Gmail Watcher")
        return self.process_emails(str(self.needs_action_folder))
    
    def start_polling(self, interval=300):
        """Continuous polling with status saves"""
        self.running = True
        logger.info(f"Started polling (interval: {interval}s)")
        logger.info(f"Status saved to: AI_Employee_Vault/Silver_Tier/watcher_status.json")
        
        run_count = 0
        while self.running:
            self.process_emails(str(self.needs_action_folder))
            run_count += 1
            
            # Create daily report every 12 runs (about every hour)
            if run_count % 12 == 0:
                self.create_daily_report(str(self.needs_action_folder))
            
            for _ in range(interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def stop(self):
        self.running = False
        logger.info("Watcher stopped")
        self.print_status()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Silver Tier Gmail Watcher')
    parser.add_argument('--once', action='store_true', help='Run once')
    parser.add_argument('--interval', type=int, default=300, help='Polling interval')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--report', action='store_true', help='Create daily report')
    args = parser.parse_args()
    
    watcher = SilverTierGmailWatcher()
    
    try:
        if args.status:
            watcher.print_status()
        elif args.report:
            watcher.create_daily_report(str(watcher.needs_action_folder))
        elif args.once:
            results = watcher.run_once()
            print(f"\n[OK] Processed {len(results)} emails")
            watcher.print_status()
        else:
            watcher.start_polling(args.interval)
    except KeyboardInterrupt:
        watcher.stop()
        print("\n⏹️  Stopped by user")
        watcher.print_status()


if __name__ == '__main__':
    main()
