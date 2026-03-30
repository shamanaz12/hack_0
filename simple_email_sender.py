#!/usr/bin/env python3
"""
Simple Email Sender - Direct SMTP (without MCP)

Quick test email sender using smtplib directly.

Usage:
    python simple_email_sender.py to@example.com "Subject" "Body"
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def load_env():
    """Load environment from .env file"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())


def send_email(to, subject, body, html=False):
    """Send email via SMTP"""
    load_env()
    
    from_email = os.getenv('EMAIL_ADDRESS', '')
    password = os.getenv('EMAIL_PASSWORD', '')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    
    if not from_email or not password:
        return {'success': False, 'error': 'Email not configured. Check .env file.'}
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to
        msg['Subject'] = subject
        
        # Attach body
        msg.attach(MIMEText(body, 'html' if html else 'plain', 'utf-8'))
        
        # Send via SMTP
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
        
        return {
            'success': True,
            'message': f'Email sent to {to}',
            'from': from_email,
            'to': to,
            'subject': subject
        }
        
    except smtplib.SMTPAuthenticationError as e:
        return {
            'success': False,
            'error': f'Authentication failed. Use Gmail App Password, not regular password. {str(e)}'
        }
    except smtplib.SMTPException as e:
        return {
            'success': False,
            'error': f'SMTP error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error: {str(e)}'
        }


if __name__ == '__main__':
    if len(sys.argv) >= 4:
        to = sys.argv[1]
        subject = sys.argv[2]
        body = sys.argv[3]
        html = sys.argv[4].lower() == 'true' if len(sys.argv) > 4 else False
        
        result = send_email(to, subject, body, html)
        
        if result['success']:
            print(f"[OK] {result['message']}")
            print(f"    From: {result['from']}")
            print(f"    Subject: {result['subject']}")
        else:
            print(f"[ERROR] {result['error']}")
    else:
        print("Usage: python simple_email_sender.py <to> <subject> <body> [html]")
        print("\nExample:")
        print('  python simple_email_sender.py test@example.com "Hello" "Test body"')
