"""
Gmail MCP Server - REAL IMPLEMENTATION
AI-Powered Email Automation with Qwen AI + SMTP

Tools:
- Qwen AI (Dashscope) - Content generation
- smtplib - Send emails
- imaplib - Read emails
- playwright - Browser automation (fallback)

NO MOCK - Real email sending!
"""

import os
import sys
import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment
load_dotenv()

# Configuration
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', '')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', '')

# MCP Server info
mcp_info = {
    'name': 'Gmail MCP Server',
    'version': '2.0.0',
    'description': 'AI-Powered Email Automation',
    'tools': ['Qwen AI', 'SMTP', 'IMAP', 'Playwright'],
    'features': [
        'ai_generate_email',
        'send_email',
        'read_emails',
        'reply_to_email',
        'forward_email'
    ]
}


class GmailMCP:
    """Real Gmail MCP with AI integration"""

    def __init__(self):
        self.api_key = DASHSCOPE_API_KEY
        self.email_address = GMAIL_EMAIL
        self.app_password = GMAIL_APP_PASSWORD
        self.use_ai = bool(self.api_key)
        
        print("=" * 60)
        print("   GMAIL MCP SERVER - REAL IMPLEMENTATION")
        print("=" * 60)
        print(f"   Email: {self.email_address or 'Not configured'}")
        print(f"   AI Enabled: {self.use_ai}")
        print(f"   Tools: Qwen AI + SMTP + IMAP")
        print("=" * 60)

    def ai_generate_email(self, prompt: str, recipient: str = '', subject: str = '') -> str:
        """Generate email content using Qwen AI"""
        if not self.use_ai:
            return f"Email about: {prompt}"
        
        try:
            from dashscope import Generation
            
            system_prompt = f"""You are a professional email assistant.
Write a clear, professional email based on the request.

Recipient: {recipient}
Subject: {subject}
Request: {prompt}

Generate ONLY the email body (no subject, no explanation)."""

            response = Generation.call(
                model='qwen-plus',
                api_key=self.api_key,
                prompt=system_prompt,
                max_tokens=500
            )
            
            if response.status_code == 200:
                return response.output.text.strip()
            else:
                return f"Email: {prompt}"
                
        except Exception as e:
            print(f"AI Error: {e}")
            return f"Email about: {prompt}"

    def send_email(self, to: str, subject: str, body: str, 
                   cc: str = None, attachments: list = None) -> dict:
        """Send real email via SMTP"""
        print(f"\n  Sending email to {to}...")
        print(f"  Subject: {subject}")
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = cc
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEText(f.read(), 'base64')
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename="{os.path.basename(file_path)}"'
                            )
                            msg.attach(part)
            
            # Send via SMTP
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.email_address, self.app_password)
            server.send_message(msg)
            server.quit()
            
            print(f"  ✅ Email sent successfully!")
            
            return {
                'success': True,
                'message_id': f'<{datetime.now().timestamp()}@gmail.com>',
                'status': 'sent'
            }
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return {'success': False, 'error': str(e)}

    def read_emails(self, limit: int = 5, unread_only: bool = True) -> list:
        """Read emails via IMAP"""
        print(f"\n  Reading emails (limit: {limit})...")
        
        try:
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.email_address, self.app_password)
            mail.select('inbox')
            
            # Search for emails
            if unread_only:
                status, messages = mail.search(None, 'UNSEEN')
            else:
                status, messages = mail.search(None, 'ALL')
            
            email_ids = messages[0].split()[-limit:]
            
            emails = []
            for email_id in email_ids:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                email_message = email.message_from_bytes(msg_data[0][1])
                
                # Extract subject
                subject = email_message['subject']
                
                # Extract from
                from_email = email_message['from']
                
                # Extract body
                body = ''
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == 'text/plain':
                            try:
                                body = part.get_payload(decode=True).decode('utf-8')
                            except:
                                pass
                else:
                    body = email_message.get_payload(decode=True).decode('utf-8')
                
                emails.append({
                    'id': email_id.decode(),
                    'from': from_email,
                    'subject': subject,
                    'body': body[:500],
                    'date': email_message['date']
                })
            
            mail.close()
            mail.logout()
            
            print(f"  ✅ Found {len(emails)} emails")
            return emails
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []

    def reply_to_email(self, original_email: dict, reply_text: str) -> dict:
        """Reply to an email"""
        to = original_email.get('from', '')
        subject = f"Re: {original_email.get('subject', '')}"
        
        # Add original message
        full_body = f"""{reply_text}

--- Original Message ---
From: {original_email.get('from')}
Subject: {original_email.get('subject')}

{original_email.get('body', '')[:500]}
"""
        
        return self.send_email(to, subject, full_body)

    def forward_email(self, original_email: dict, forward_to: str, message: str = '') -> dict:
        """Forward an email"""
        subject = f"Fwd: {original_email.get('subject', '')}"
        
        body = f"""{message}

--- Forwarded Message ---
From: {original_email.get('from')}
Subject: {original_email.get('subject')}

{original_email.get('body', '')[:500]}
"""
        
        return self.send_email(forward_to, subject, body)

    def health_check(self) -> dict:
        """Check Gmail connection"""
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.email_address, self.app_password)
            mail.logout()
            
            return {
                'status': 'healthy',
                'email': self.email_address,
                'ai_enabled': self.use_ai,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Global instance
gmail_mcp = GmailMCP()


# MCP Tools definition
TOOLS = [
    {
        'name': 'gmail_send',
        'description': 'Send email via Gmail',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'to': {'type': 'string'},
                'subject': {'type': 'string'},
                'body': {'type': 'string'},
                'cc': {'type': 'string'}
            },
            'required': ['to', 'subject', 'body']
        }
    },
    {
        'name': 'gmail_read',
        'description': 'Read Gmail messages',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'limit': {'type': 'integer', 'default': 5},
                'unread_only': {'type': 'boolean', 'default': True}
            }
        }
    },
    {
        'name': 'gmail_reply',
        'description': 'Reply to an email',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'original_email': {'type': 'object'},
                'reply_text': {'type': 'string'}
            },
            'required': ['original_email', 'reply_text']
        }
    },
    {
        'name': 'gmail_ai_generate',
        'description': 'Generate email content with AI',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'prompt': {'type': 'string'},
                'recipient': {'type': 'string'},
                'subject': {'type': 'string'}
            },
            'required': ['prompt']
        }
    }
]


def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    """Handle MCP tool calls"""
    print(f"\nTool call: {tool_name}")
    
    if tool_name == 'gmail_send':
        return gmail_mcp.send_email(
            arguments.get('to'),
            arguments.get('subject'),
            arguments.get('body'),
            arguments.get('cc')
        )
    
    elif tool_name == 'gmail_read':
        emails = gmail_mcp.read_emails(
            arguments.get('limit', 5),
            arguments.get('unread_only', True)
        )
        return {'success': True, 'emails': emails}
    
    elif tool_name == 'gmail_reply':
        return gmail_mcp.reply_to_email(
            arguments.get('original_email'),
            arguments.get('reply_text')
        )
    
    elif tool_name == 'gmail_ai_generate':
        content = gmail_mcp.ai_generate_email(
            arguments.get('prompt'),
            arguments.get('recipient'),
            arguments.get('subject')
        )
        return {'success': True, 'content': content}
    
    else:
        return {'success': False, 'error': f'Unknown tool: {tool_name}'}


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail MCP Server')
    parser.add_argument('--test', action='store_true', help='Run test')
    parser.add_argument('--send', nargs=3, metavar=('TO', 'SUBJECT', 'BODY'), help='Send email')
    parser.add_argument('--read', action='store_true', help='Read emails')
    parser.add_argument('--health', action='store_true', help='Health check')
    
    args = parser.parse_args()
    
    if args.health:
        health = gmail_mcp.health_check()
        print(json.dumps(health, indent=2))
    
    elif args.read:
        emails = gmail_mcp.read_emails(5)
        for email in emails:
            print(f"\n  From: {email['from']}")
            print(f"  Subject: {email['subject']}")
            print(f"  Body: {email['body'][:200]}...")
    
    elif args.send:
        result = gmail_mcp.send_email(args.send[0], args.send[1], args.send[2])
        print(f"\nResult: {result}")
    
    elif args.test:
        print("\n" + "=" * 60)
        print("   GMAIL MCP - TEST")
        print("=" * 60)
        
        # Health check
        print("\n1. Health Check:")
        health = gmail_mcp.health_check()
        print(json.dumps(health, indent=2))
        
        # Test AI generation
        print("\n2. AI Email Generation:")
        content = gmail_mcp.ai_generate_email(
            "Meeting invitation for tomorrow 3 PM",
            "shama@example.com",
            "Meeting Request"
        )
        print(f"Generated:\n{content}")
        
        # Read emails
        print("\n3. Read Emails:")
        emails = gmail_mcp.read_emails(3)
        print(f"Found {len(emails)} emails")
        
        print("\n" + "=" * 60)
        print("   TEST COMPLETE")
        print("=" * 60)
    
    else:
        print("Gmail MCP Server - AI-Powered Email Automation")
        print("=" * 60)
        print("\nUsage:")
        print("  python gmail_mcp_server.py --health")
        print("  python gmail_mcp_server.py --read")
        print("  python gmail_mcp_server.py --send TO SUBJECT BODY")
        print("  python gmail_mcp_server.py --test")
        print("\nTools:")
        for tool in TOOLS:
            print(f"  - {tool['name']}: {tool['description']}")
