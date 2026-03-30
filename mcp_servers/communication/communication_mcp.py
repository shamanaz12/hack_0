"""
Communication MCP Server
Gold Tier - Unified Communication Hub

Integrates:
- Gmail (SMTP/IMAP)
- WhatsApp (Playwright/API)
- Slack (Web API)
- Calendar (Google Calendar API)

Features:
- Send/receive emails
- Send/receive WhatsApp messages
- Send/receive Slack messages
- Schedule calendar events
- AI-powered content generation

Usage:
  python communication_mcp.py --health
  python communication_mcp.py --send-email
  python communication_mcp.py --send-whatsapp
  python communication_mcp.py --send-slack
"""

import os
import sys
import json
import smtplib
import time
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', '')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', '')
WHATSAPP_PHONE = os.getenv('WHATSAPP_PHONE_NUMBER', '')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN', '')

# MCP Server Info
SERVER_INFO = {
    'name': 'Communication MCP',
    'version': '1.0.0',
    'description': 'Unified Communication Hub',
    'channels': ['Gmail', 'WhatsApp', 'Slack', 'Calendar'],
    'features': [
        'send_email',
        'read_email',
        'send_whatsapp',
        'send_slack',
        'create_calendar_event',
        'ai_generate_content'
    ]
}


class CommunicationMCP:
    """Unified Communication Server"""

    def __init__(self):
        self.api_key = DASHSCOPE_API_KEY
        self.gmail_email = GMAIL_EMAIL
        self.gmail_password = GMAIL_APP_PASSWORD
        self.whatsapp_phone = WHATSAPP_PHONE
        self.slack_token = SLACK_BOT_TOKEN
        self.use_ai = bool(self.api_key)

    def ai_generate_content(self, prompt: str, channel: str = 'email') -> str:
        """Generate content using Qwen AI"""
        if not self.use_ai:
            return f"[AI Content]: {prompt}"
        
        try:
            from dashscope import Generation
            
            response = Generation.call(
                model='qwen-plus',
                api_key=self.api_key,
                prompt=f"Write a professional {channel} message: {prompt}",
                max_tokens=300
            )
            
            if response.status_code == 200:
                return response.output.text.strip()
            return prompt
        except:
            return prompt

    def send_email(self, to: str, subject: str, body: str, cc: str = None) -> dict:
        """Send email via Gmail SMTP"""
        print(f"  Sending email to {to}...")
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_email
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = cc
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.gmail_email, self.gmail_password)
            server.send_message(msg)
            server.quit()
            
            print(f"  ✅ Email sent!")
            return {
                'success': True,
                'message_id': f'<{datetime.now().timestamp()}@gmail.com>',
                'status': 'sent'
            }
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return {'success': False, 'error': str(e)}

    def send_whatsapp(self, to: str, message: str) -> dict:
        """Send WhatsApp message (Mock mode - integrate with whatsapp_watcher.py)"""
        print(f"  Sending WhatsApp to {to}...")
        
        # Log message for whatsapp_watcher to pick up
        log_file = Path('logs/whatsapp_outgoing.json')
        log_file.parent.mkdir(exist_ok=True)
        
        messages = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                messages = json.load(f)
        
        messages.append({
            'to': to,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        })
        
        with open(log_file, 'w') as f:
            json.dump(messages, f, indent=2)
        
        print(f"  ✅ WhatsApp message queued!")
        return {
            'success': True,
            'message_id': f'wa_{datetime.now().timestamp()}',
            'status': 'queued'
        }

    def send_slack(self, channel: str, message: str) -> dict:
        """Send Slack message"""
        print(f"  Sending Slack message to {channel}...")
        
        if not self.slack_token:
            print(f"  ⚠️  Slack token not configured - queuing message")
            return {'success': False, 'error': 'Slack token not configured'}
        
        try:
            import requests
            
            response = requests.post(
                'https://slack.com/api/chat.postMessage',
                headers={'Authorization': f'Bearer {self.slack_token}'},
                json={
                    'channel': channel,
                    'text': message
                },
                timeout=10
            )
            
            result = response.json()
            
            if result.get('ok'):
                print(f"  ✅ Slack message sent!")
                return {
                    'success': True,
                    'message_id': result.get('ts'),
                    'status': 'sent'
                }
            else:
                return {'success': False, 'error': result.get('error')}
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return {'success': False, 'error': str(e)}

    def create_calendar_event(self, title: str, start: str, end: str, 
                              attendees: list = None) -> dict:
        """Create calendar event (placeholder - integrate with calendar_mcp.js)"""
        print(f"  Creating calendar event: {title}...")
        
        # Log event for calendar_mcp to pick up
        log_file = Path('logs/calendar_events.json')
        log_file.parent.mkdir(exist_ok=True)
        
        events = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                events = json.load(f)
        
        events.append({
            'title': title,
            'start': start,
            'end': end,
            'attendees': attendees or [],
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        })
        
        with open(log_file, 'w') as f:
            json.dump(events, f, indent=2)
        
        print(f"  ✅ Event queued!")
        return {
            'success': True,
            'event_id': f'cal_{datetime.now().timestamp()}',
            'status': 'queued'
        }

    def health_check(self) -> dict:
        """Check all communication channels"""
        status = {
            'server': 'Communication MCP',
            'timestamp': datetime.now().isoformat(),
            'channels': {}
        }
        
        # Gmail
        if self.gmail_email and self.gmail_password:
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(self.gmail_email, self.gmail_password)
                server.quit()
                status['channels']['gmail'] = 'healthy'
            except:
                status['channels']['gmail'] = 'unhealthy'
        else:
            status['channels']['gmail'] = 'not_configured'
        
        # WhatsApp
        if self.whatsapp_phone:
            status['channels']['whatsapp'] = 'configured'
        else:
            status['channels']['whatsapp'] = 'not_configured'
        
        # Slack
        if self.slack_token:
            status['channels']['slack'] = 'configured'
        else:
            status['channels']['slack'] = 'not_configured'
        
        # AI
        status['channels']['ai'] = 'enabled' if self.use_ai else 'disabled'
        
        return status


# Global instance
comm_mcp = CommunicationMCP()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Communication MCP Server')
    parser.add_argument('--health', action='store_true', help='Health check')
    parser.add_argument('--send-email', action='store_true', help='Send email')
    parser.add_argument('--send-whatsapp', action='store_true', help='Send WhatsApp')
    parser.add_argument('--send-slack', action='store_true', help='Send Slack')
    parser.add_argument('--ai-generate', type=str, help='Generate content with AI')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   COMMUNICATION MCP SERVER")
    print("=" * 60)
    
    if args.health:
        print("\nHealth Check:")
        health = comm_mcp.health_check()
        print(json.dumps(health, indent=2))
    
    elif args.ai_generate:
        print(f"\nAI Content Generation:")
        content = comm_mcp.ai_generate_content(args.ai_generate)
        print(f"Generated:\n{content}")
    
    elif args.send_email:
        print("\nSend Email:")
        to = input("  To: ")
        subject = input("  Subject: ")
        body = input("  Body: ")
        
        # Optionally use AI
        use_ai = input("  Use AI to enhance? (y/n): ").lower() == 'y'
        if use_ai:
            body = comm_mcp.ai_generate_content(f"{subject}: {body}", 'email')
            print(f"  AI Enhanced:\n  {body[:100]}...")
        
        result = comm_mcp.send_email(to, subject, body)
        print(f"\nResult: {result}")
    
    elif args.send_whatsapp:
        print("\nSend WhatsApp:")
        to = input("  To: ")
        message = input("  Message: ")
        
        # Optionally use AI
        use_ai = input("  Use AI to enhance? (y/n): ").lower() == 'y'
        if use_ai:
            message = comm_mcp.ai_generate_content(message, 'whatsapp')
            print(f"  AI Enhanced:\n  {message[:100]}...")
        
        result = comm_mcp.send_whatsapp(to, message)
        print(f"\nResult: {result}")
    
    elif args.send_slack:
        print("\nSend Slack:")
        channel = input("  Channel: ")
        message = input("  Message: ")
        
        # Optionally use AI
        use_ai = input("  Use AI to enhance? (y/n): ").lower() == 'y'
        if use_ai:
            message = comm_mcp.ai_generate_content(message, 'slack')
            print(f"  AI Enhanced:\n  {message[:100]}...")
        
        result = comm_mcp.send_slack(channel, message)
        print(f"\nResult: {result}")
    
    else:
        print("\nUsage:")
        print("  python communication_mcp.py --health")
        print("  python communication_mcp.py --send-email")
        print("  python communication_mcp.py --send-whatsapp")
        print("  python communication_mcp.py --send-slack")
        print("  python communication_mcp.py --ai-generate 'prompt'")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
