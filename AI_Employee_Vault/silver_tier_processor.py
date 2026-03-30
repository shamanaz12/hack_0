"""
Silver Tier Email Processor
Moves emails from inbox → skills → Needs_Action → Done (MCP automated workflow)
"""

import os
import shutil
import json
import requests
from datetime import datetime
from pathlib import Path

class SilverTierProcessor:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.silver_dir = self.base_dir / "Silver_Tier"
        self.inbox_dir = self.silver_dir / "inbox"
        self.skills_dir = self.silver_dir / "skills"
        self.needs_action_dir = self.silver_dir / "Needs_Action"
        self.done_dir = self.silver_dir / "Done"
        
        # MCP Server configuration
        self.mcp_url = os.getenv("MCP_URL", "http://localhost:5000")
        
        # Ensure all directories exist
        for dir_path in [self.inbox_dir, self.skills_dir, self.needs_action_dir, self.done_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def process_inbox(self):
        """Move new emails from inbox to skills for categorization"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processing Silver Tier inbox...")
        
        md_files = list(self.inbox_dir.glob("*.md"))
        
        if not md_files:
            print("  No new emails in inbox.")
            return
        
        for file_path in md_files:
            filename = file_path.name
            category = self.categorize_email(file_path)
            
            category_dir = self.skills_dir / category
            category_dir.mkdir(exist_ok=True)
            
            dest_path = category_dir / filename
            shutil.move(str(file_path), str(dest_path))
            print(f"  Categorized: {filename} → skills/{category}/")
        
        print(f"  Processed {len(md_files)} email(s)")
    
    def categorize_email(self, file_path):
        """AI-powered email categorization into skills"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        
        # Simple keyword-based categorization
        # Can be enhanced with AI/ML models
        categories = {
            'email_campaigns': ['campaign', 'marketing', 'promotional', 'bulk', 'newsletter'],
            'customer_support': ['support', 'help', 'issue', 'problem', 'complaint', 'question'],
            'meetings': ['meeting', 'schedule', 'calendar', 'appointment', 'zoom', 'teams'],
            'sales': ['sale', 'price', 'quote', 'proposal', 'purchase', 'order'],
            'hr': ['hire', 'interview', 'resume', 'employee', 'benefits', 'vacation'],
            'finance': ['invoice', 'payment', 'budget', 'expense', 'billing'],
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in content:
                    return category
        
        return 'general'
    
    def move_to_needs_action(self, filename):
        """Move email from skills to Needs_Action for processing"""
        # Search in all skill categories
        for category_dir in self.skills_dir.iterdir():
            if category_dir.is_dir():
                source = category_dir / filename
                if source.exists():
                    dest = self.needs_action_dir / filename
                    shutil.move(str(source), str(dest))
                    print(f"  Moved: {filename} → Needs_Action/")
                    return True
        
        print(f"  File not found in skills/: {filename}")
        return False
    
    def send_auto_response(self, filename, to_email, subject, body):
        """Send automated response via MCP Server"""
        print(f"  Sending auto-response via MCP Server...")
        
        payload = {
            "to": to_email,
            "subject": f"Re: {subject}",
            "body": body,
            "dry_run": False
        }
        
        try:
            response = requests.post(
                f"{self.mcp_url}/send-email",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=30
            )
            
            result = response.json()
            
            if result.get('status') == 'success':
                print(f"  ✅ Email sent successfully!")
                return True
            else:
                print(f"  ❌ Failed: {result.get('message')}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def move_to_done(self, filename):
        """Move completed task to Done folder"""
        source = self.needs_action_dir / filename
        if not source.exists():
            print(f"  File not found: {filename}")
            return False
        
        dest = self.done_dir / f"COMPLETED_{filename}"
        shutil.move(str(source), str(dest))
        print(f"  ✅ Moved: {filename} → Done/")
        return True
    
    def process_auto_response(self, filename):
        """Complete workflow: send response and move to Done"""
        file_path = self.needs_action_dir / filename
        
        if not file_path.exists():
            print(f"  File not found: {filename}")
            return False
        
        # Read the file to extract recipient and content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract email metadata (simplified - can be enhanced)
        to_email = self.extract_email(content, "from:") or "recipient@example.com"
        subject = self.extract_subject(content) or "No Subject"
        response_body = self.generate_response(content)
        
        # Send via MCP
        success = self.send_auto_response(filename, to_email, subject, response_body)
        
        if success:
            self.move_to_done(filename)
            return True
        
        return False
    
    def extract_email(self, content, marker):
        """Extract email address from content"""
        for line in content.split('\n'):
            if marker.lower() in line.lower():
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()
        return None
    
    def extract_subject(self, content):
        """Extract subject from content"""
        for line in content.split('\n'):
            if 'subject:' in line.lower():
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()
        return None
    
    def generate_response(self, content):
        """Generate auto-response (can be enhanced with AI)"""
        return f"""Thank you for your email.

This is an automated response from our AI Employee system.

We have received your message and will get back to you shortly.

Best regards,
AI Employee Assistant
"""
    
    def show_status(self):
        """Show current status of Silver Tier"""
        print("\n" + "="*50)
        print("  SILVER TIER STATUS (MCP Integrated)")
        print("="*50)
        
        inbox_count = len(list(self.inbox_dir.glob("*.md")))
        needs_action_count = len(list(self.needs_action_dir.glob("*.md")))
        done_count = len(list(self.done_dir.glob("*.md")))
        skills_count = len(list(self.skills_dir.rglob("*.md")))
        
        # Check MCP Server status
        mcp_status = "OFFLINE"
        try:
            response = requests.get(f"{self.mcp_url}/health", timeout=5)
            if response.status_code == 200:
                mcp_status = "ONLINE"
        except:
            pass
        
        print(f"  [INBOX] inbox/           : {inbox_count} emails")
        print(f"  [SKILLS] skills/         : {skills_count} categorized")
        print(f"  [WAITING] Needs_Action/  : {needs_action_count} pending")
        print(f"  [DONE] Done/             : {done_count} completed")
        print(f"  [MCP SERVER]             : {mcp_status}")
        print("="*50 + "\n")

if __name__ == "__main__":
    processor = SilverTierProcessor()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "process":
            processor.process_inbox()
        elif command == "move" and len(sys.argv) > 2:
            processor.move_to_needs_action(sys.argv[2])
        elif command == "respond" and len(sys.argv) > 2:
            processor.process_auto_response(sys.argv[2])
        elif command == "done" and len(sys.argv) > 2:
            processor.move_to_done(sys.argv[2])
        elif command == "status":
            processor.show_status()
        else:
            print("Usage:")
            print("  python silver_tier_processor.py process")
            print("  python silver_tier_processor.py move <filename>")
            print("  python silver_tier_processor.py respond <filename>")
            print("  python silver_tier_processor.py done <filename>")
            print("  python silver_tier_processor.py status")
    else:
        processor.show_status()
