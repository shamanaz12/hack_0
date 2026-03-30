"""
WhatsApp MCP Skill
Gold Tier - WhatsApp Integration with Workflow

Workflow: needs_action → logs → plans → inbox/approve → done

Usage:
  python whatsapp_skill.py --send "+03202191812" "Hello"
  python whatsapp_skill.py --status
  python whatsapp_skill.py --process
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuration
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_API_URL = 'https://graph.facebook.com/v17.0'

# Base directories
BASE_DIR = Path('AI_Employee_Vault')
BRONZE_DIR = BASE_DIR / 'Bronze_Tier'

# Workflow folders
NEEDS_ACTION = BRONZE_DIR / 'Needs_Action'
LOGS_DIR = BRONZE_DIR / 'Logs'
PLANS_DIR = BRONZE_DIR / 'Plans'
INBOX_DIR = BRONZE_DIR / 'inbox'
DONE_DIR = BRONZE_DIR / 'Done'

# Ensure folders exist
for folder in [NEEDS_ACTION, LOGS_DIR, PLANS_DIR, INBOX_DIR, DONE_DIR]:
    folder.mkdir(exist_ok=True, parents=True)


class WhatsAppSkill:
    """WhatsApp MCP Skill with workflow management"""

    def __init__(self):
        self.phone_number_id = WHATSAPP_PHONE_NUMBER_ID
        self.access_token = WHATSAPP_ACCESS_TOKEN
        self.mock_mode = not self.access_token or self.access_token == 'your_whatsapp_token_here'

    def send_message(self, to: str, message: str) -> dict:
        """Send WhatsApp message"""
        print(f"  Sending message to {to}...")
        
        if self.mock_mode:
            print("  [MOCK MODE] Message not sent (no token configured)")
            return {
                'success': True,
                'message_id': f'mock_{datetime.now().timestamp()}',
                'mock': True,
                'status': 'sent'
            }
        
        try:
            response = requests.post(
                f'{WHATSAPP_API_URL}/{self.phone_number_id}/messages',
                json={
                    'messaging_product': 'whatsapp',
                    'to': to,
                    'type': 'text',
                    'text': {'body': message}
                },
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  [OK] Message sent: {result['messages'][0]['id']}")
                return {
                    'success': True,
                    'message_id': result['messages'][0]['id'],
                    'status': 'sent'
                }
            else:
                error = response.json().get('error', {}).get('message', 'Unknown error')
                print(f"  [ERROR] {error}")
                return {'success': False, 'error': error}
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            return {'success': False, 'error': str(e)}

    def process_request(self, request_file: Path):
        """Process WhatsApp request through workflow"""
        print(f"\nProcessing: {request_file.name}")
        
        # Read request
        content = request_file.read_text(encoding='utf-8')
        
        # Extract phone and message
        phone = self._extract_phone(content)
        message = self._extract_message(content)
        
        if not phone or not message:
            print("  [ERROR] Could not extract phone or message")
            return
        
        # Step 1: Create log
        log_entry = f"""# WhatsApp Log - {request_file.stem}

**Started:** {datetime.now()}
**Phone:** {phone}
**Message:** {message[:100]}...
**Status:** Processing

## Actions:
1. ✅ Request received
2. 🔄 Processing
3. ⏳ Awaiting approval

"""
        log_file = LOGS_DIR / f"{request_file.stem}_log.md"
        log_file.write_text(log_entry, encoding='utf-8')
        print(f"  [OK] Log created: {log_file.name}")
        
        # Step 2: Create plan
        plan_content = f"""# WhatsApp Plan - {request_file.stem}

**Original Request:** {request_file.name}
**Created:** {datetime.now()}

## Plan:
1. ✅ Extract phone and message
2. 🔄 Generate content
3. ⏳ Submit for approval
4. ⏳ Send message
5. ⏳ Mark as done

## Message Details:
- **To:** {phone}
- **Message:** {message}

"""
        plan_file = PLANS_DIR / f"{request_file.stem}_plan.md"
        plan_file.write_text(plan_content, encoding='utf-8')
        print(f"  [OK] Plan created: {plan_file.name}")
        
        # Step 3: Create approval request
        approval_content = f"""# Approval Required - WhatsApp Message

**Type:** WhatsApp Message
**Status:** Awaiting Approval
**Created:** {datetime.now()}

## Message Details:
- **To:** {phone}
- **Message:** {message}

## Actions:
- [ ] Approve
- [ ] Edit
- [ ] Reject

## Approval:
**Approved by:** ________________
**Date:** ________________
**Comments:** ________________

"""
        approval_file = INBOX_DIR / f"{request_file.stem}_approval.md"
        approval_file.write_text(approval_content, encoding='utf-8')
        print(f"  [OK] Approval request created: {approval_file.name}")
        
        # Step 4: Move to processed
        processed_file = NEEDS_ACTION / f"processed_{request_file.name}"
        request_file.rename(processed_file)
        print(f"  [OK] Moved to processed")

    def approve_and_send(self, approval_file: Path):
        """Approve and send message"""
        print(f"\nProcessing approval: {approval_file.name}")
        
        # Read approval file
        content = approval_file.read_text(encoding='utf-8')
        
        # Check if approved
        if 'Approved by:' not in content or content.split('Approved by:')[1].strip().startswith('_'):
            print("  [SKIP] Not approved yet")
            return
        
        # Extract phone and message
        phone = self._extract_phone(content)
        message = self._extract_message(content)
        
        if not phone or not message:
            print("  [ERROR] Could not extract phone or message")
            return
        
        # Send message
        result = self.send_message(phone, message)
        
        if result['success']:
            # Mark as done
            done_content = f"""# WhatsApp Message - COMPLETED

**Original Request:** {approval_file.name}
**Completed:** {datetime.now()}

## Message Details:
- **To:** {phone}
- **Message:** {message}

## Result:
- **Status:** ✅ Sent
- **Message ID:** {result.get('message_id', 'N/A')}

"""
            done_file = DONE_DIR / f"{approval_file.stem}_done.md"
            done_file.write_text(done_content, encoding='utf-8')
            print(f"  [OK] Marked as done: {done_file.name}")
            
            # Delete approval file
            approval_file.unlink()
            print(f"  [OK] Approval file removed")
        else:
            print(f"  [ERROR] Failed to send: {result.get('error')}")

    def _extract_phone(self, content: str) -> str:
        """Extract phone number from content"""
        import re
        # Look for phone pattern
        match = re.search(r'(\+?\d{10,15})', content)
        return match.group(1) if match else ''

    def _extract_message(self, content: str) -> str:
        """Extract message from content"""
        # Look for message section
        if 'Message:' in content:
            return content.split('Message:')[1].split('\n')[0].strip()
        return content[:200]

    def status(self):
        """Show workflow status"""
        print("\n" + "=" * 60)
        print("   WHATSAPP SKILL - WORKFLOW STATUS")
        print("=" * 60)
        
        for folder, name in [(NEEDS_ACTION, 'Needs Action'), (LOGS_DIR, 'Logs'), 
                             (PLANS_DIR, 'Plans'), (INBOX_DIR, 'Inbox/Approval'), 
                             (DONE_DIR, 'Done')]:
            if folder.exists():
                count = len(list(folder.glob('*.md')))
                print(f"  {name:20} : {count} items")
        
        print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Skill')
    parser.add_argument('--send', nargs=2, metavar=('PHONE', 'MESSAGE'), help='Send message')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--process', action='store_true', help='Process requests')
    parser.add_argument('--approve', action='store_true', help='Approve and send')
    
    args = parser.parse_args()
    
    skill = WhatsAppSkill()
    
    if args.send:
        result = skill.send_message(args.send[0], args.send[1])
        print(f"\nResult: {result}")
    
    elif args.status:
        skill.status()
    
    elif args.process:
        print("Processing WhatsApp requests...")
        for file in NEEDS_ACTION.glob('*.md'):
            if 'whatsapp' in file.name.lower() or 'whatsapp' in file.read_text().lower():
                skill.process_request(file)
    
    elif args.approve:
        print("Processing approvals...")
        for file in INBOX_DIR.glob('*.md'):
            if 'whatsapp' in file.name.lower():
                skill.approve_and_send(file)
    
    else:
        print("Usage:")
        print("  python whatsapp_skill.py --send '+923161129505' 'Hello'")
        print("  python whatsapp_skill.py --status")
        print("  python whatsapp_skill.py --process")
        print("  python whatsapp_skill.py --approve")


if __name__ == '__main__':
    main()
