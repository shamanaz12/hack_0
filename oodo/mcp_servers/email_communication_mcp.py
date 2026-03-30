"""
Email & Communication MCP Server
Handles Gmail, WhatsApp, and general email operations
"""

import os
import json
import logging
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import requests
import base64

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/email_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GmailMCP:
    """Gmail operations using SMTP/IMAP"""
    
    def __init__(self):
        self.email_address = os.getenv('GMAIL_ADDRESS', '')
        self.app_password = os.getenv('GMAIL_APP_PASSWORD', '')
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.imap_server = 'imap.gmail.com'
        self.imap_port = 993
        
        logger.info("Gmail MCP initialized")
    
    def send_email(self, to: str, subject: str, body: str, html: bool = False, 
                   cc: List[str] = None, bcc: List[str] = None, 
                   attachments: List[str] = None) -> Dict:
        """Send email via Gmail SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = ', '.join([to] + (cc or []) + (bcc or []))
            msg['Subject'] = subject
            
            # Add body
            msg_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, msg_type))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename="{os.path.basename(file_path)}"'
                            )
                            msg.attach(part)
                    except Exception as e:
                        logger.error(f"Attachment error for {file_path}: {str(e)}")
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.app_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent to {to}")
            return {'success': True, 'message': 'Email sent successfully'}
        except Exception as e:
            logger.error(f"Send email error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_emails(self, limit: int = 10, unread_only: bool = False, 
                   from_address: str = None, subject_contains: str = None) -> Dict:
        """Get emails from Gmail IMAP"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.app_password)
            mail.select('inbox')
            
            # Search criteria
            search_criteria = 'UNSEEN' if unread_only else 'ALL'
            
            status, messages = mail.search(None, search_criteria)
            email_ids = messages[0].split()
            
            emails = []
            for email_id in email_ids[-limit:]:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Filter by from address
                        if from_address and from_address not in msg.get('From', ''):
                            continue
                        
                        # Filter by subject
                        if subject_contains and subject_contains not in msg.get('Subject', ''):
                            continue
                        
                        # Get email body
                        body = ''
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get('Content-Disposition'))
                                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                                    try:
                                        body = part.get_payload(decode=True).decode()
                                    except:
                                        body = part.get_payload(decode=True).decode('latin-1')
                                    break
                        else:
                            try:
                                body = msg.get_payload(decode=True).decode()
                            except:
                                body = msg.get_payload(decode=True).decode('latin-1')
                        
                        emails.append({
                            'id': email_id.decode(),
                            'from': msg.get('From'),
                            'to': msg.get('To'),
                            'subject': msg.get('Subject'),
                            'date': msg.get('Date'),
                            'body': body[:500] if len(body) > 500 else body,
                            'is_read': '\\Seen' in str(msg.get('Flags', ''))
                        })
            
            mail.close()
            mail.logout()
            
            logger.info(f"Retrieved {len(emails)} emails")
            return {'success': True, 'data': emails, 'count': len(emails)}
        except Exception as e:
            logger.error(f"Get emails error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def mark_as_read(self, email_ids: List[str]) -> Dict:
        """Mark emails as read"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.app_password)
            mail.select('inbox')
            
            for email_id in email_ids:
                mail.store(email_id, '+FLAGS', '\\Seen')
            
            mail.close()
            mail.logout()
            
            logger.info(f"Marked {len(email_ids)} emails as read")
            return {'success': True, 'message': f'Marked {len(email_ids)} emails as read'}
        except Exception as e:
            logger.error(f"Mark as read error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def search_emails(self, query: str, limit: int = 20) -> Dict:
        """Search emails by query"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.app_password)
            mail.select('inbox')
            
            # Gmail search syntax
            status, messages = mail.search(None, 'X-GM-RAW', query)
            email_ids = messages[0].split()
            
            emails = []
            for email_id in email_ids[-limit:]:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        emails.append({
                            'id': email_id.decode(),
                            'from': msg.get('From'),
                            'subject': msg.get('Subject'),
                            'date': msg.get('Date')
                        })
            
            mail.close()
            mail.logout()
            
            logger.info(f"Search found {len(emails)} emails")
            return {'success': True, 'data': emails, 'count': len(emails)}
        except Exception as e:
            logger.error(f"Search emails error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_email_stats(self, days: int = 7) -> Dict:
        """Get email statistics"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.app_password)
            mail.select('inbox')
            
            # Get all emails
            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            
            total_emails = len(email_ids)
            unread_count = 0
            today_count = 0
            week_count = 0
            
            today = datetime.now().date()
            week_ago = today - timedelta(days=days)
            
            for email_id in email_ids:
                status, msg_data = mail.fetch(email_id, '(RFC822 FLAGS)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Check if unread
                        if '\\Seen' not in str(msg.get('Flags', '')):
                            unread_count += 1
                        
                        # Check date
                        email_date = email.utils.parsedate_to_datetime(msg.get('Date', ''))
                        if email_date.date() == today:
                            today_count += 1
                        elif email_date.date() >= week_ago:
                            week_count += 1
            
            mail.close()
            mail.logout()
            
            return {
                'success': True,
                'stats': {
                    'total_emails': total_emails,
                    'unread_count': unread_count,
                    'today_count': today_count,
                    'week_count': week_count,
                    'period_days': days
                }
            }
        except Exception as e:
            logger.error(f"Get email stats error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> Dict:
        """Check Gmail connection health"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.app_password)
            mail.select('inbox')
            mail.close()
            mail.logout()
            
            return {
                'status': 'healthy',
                'email': self.email_address,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


class WhatsAppMCP:
    """WhatsApp operations using Twilio API or WhatsApp Business API"""
    
    def __init__(self):
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
        self.base_url = 'https://graph.facebook.com/v17.0'
        
        logger.info("WhatsApp MCP initialized")
    
    def send_message(self, to: str, message: str, message_type: str = 'text') -> Dict:
        """Send WhatsApp message"""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': message_type
        }
        
        if message_type == 'text':
            data['text'] = {'body': message}
        elif message_type == 'template':
            data['template'] = {
                'name': message,
                'language': {'code': 'en'}
            }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"WhatsApp message sent to {to}")
            return {'success': True, 'data': result}
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp send error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_template(self, to: str, template_name: str, components: List[Dict] = None) -> Dict:
        """Send WhatsApp template message"""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': 'en'}
            }
        }
        
        if components:
            data['template']['components'] = components
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"WhatsApp template sent to {to}")
            return {'success': True, 'data': result}
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp template send error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_messages(self, limit: int = 10) -> Dict:
        """Get recent messages (requires webhook storage)"""
        # This would typically read from a database where webhook messages are stored
        # For now, return placeholder
        return {
            'success': True,
            'data': [],
            'message': 'Messages retrieved from webhook storage',
            'count': 0
        }
    
    def get_message_stats(self, days: int = 7) -> Dict:
        """Get message statistics"""
        # Get insights from WhatsApp API
        url = f"{self.base_url}/{self.phone_number_id}/message_insights"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        until_date = datetime.now().strftime('%Y-%m-%d')
        
        params = {
            'metric': ['sent', 'delivered', 'read', 'failed'],
            'since': since_date,
            'until': until_date
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            
            return {'success': True, 'data': result, 'period_days': days}
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp stats error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> Dict:
        """Check WhatsApp connection health"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}"
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return {
                'status': 'healthy',
                'phone_number_id': self.phone_number_id,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


class EmailCommunicationMCP:
    """Unified Email & Communication MCP Server"""
    
    def __init__(self):
        self.gmail = GmailMCP()
        self.whatsapp = WhatsAppMCP()
        
        logger.info("Email Communication MCP Server initialized")
    
    def send_notification(self, channel: str, to: str, subject: str, message: str) -> Dict:
        """Send notification via specified channel"""
        if channel == 'email':
            return self.gmail.send_email(to, subject, message)
        elif channel == 'whatsapp':
            return self.whatsapp.send_message(to, message)
        else:
            return {'success': False, 'error': f'Unknown channel: {channel}'}
    
    def get_all_stats(self, days: int = 7) -> Dict:
        """Get stats from all communication channels"""
        return {
            'gmail': self.gmail.get_email_stats(days),
            'whatsapp': self.whatsapp.get_message_stats(days),
            'generated_at': datetime.now().isoformat()
        }
    
    def health_check_all(self) -> Dict:
        """Check health of all communication channels"""
        return {
            'gmail': self.gmail.health_check(),
            'whatsapp': self.whatsapp.health_check(),
            'timestamp': datetime.now().isoformat()
        }


# Create MCP server instance
mcp_server = EmailCommunicationMCP()


# Tool definitions
TOOLS = [
    {
        'name': 'send_email',
        'description': 'Send email via Gmail',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'to': {'type': 'string'},
                'subject': {'type': 'string'},
                'body': {'type': 'string'},
                'html': {'type': 'boolean', 'default': False},
                'cc': {'type': 'array', 'items': {'type': 'string'}},
                'attachments': {'type': 'array', 'items': {'type': 'string'}}
            },
            'required': ['to', 'subject', 'body']
        }
    },
    {
        'name': 'get_emails',
        'description': 'Get emails from Gmail',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'limit': {'type': 'integer', 'default': 10},
                'unread_only': {'type': 'boolean', 'default': False},
                'from_address': {'type': 'string'},
                'subject_contains': {'type': 'string'}
            }
        }
    },
    {
        'name': 'send_whatsapp_message',
        'description': 'Send WhatsApp message',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'to': {'type': 'string'},
                'message': {'type': 'string'},
                'message_type': {'type': 'string', 'default': 'text'}
            },
            'required': ['to', 'message']
        }
    },
    {
        'name': 'send_notification',
        'description': 'Send notification via email or WhatsApp',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'channel': {'type': 'string', 'enum': ['email', 'whatsapp']},
                'to': {'type': 'string'},
                'subject': {'type': 'string'},
                'message': {'type': 'string'}
            },
            'required': ['channel', 'to', 'message']
        }
    },
    {
        'name': 'get_communication_stats',
        'description': 'Get stats from all communication channels',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'days': {'type': 'integer', 'default': 7}
            }
        }
    },
    {
        'name': 'health_check_communication',
        'description': 'Check health of all communication channels'
    }
]


def handle_tool_call(tool_name: str, arguments: Dict) -> Dict:
    """Handle MCP tool calls"""
    logger.info(f"Tool call: {tool_name} with args: {arguments}")
    
    try:
        if tool_name == 'send_email':
            return mcp_server.gmail.send_email(**arguments)
        elif tool_name == 'get_emails':
            return mcp_server.gmail.get_emails(**arguments)
        elif tool_name == 'send_whatsapp_message':
            return mcp_server.whatsapp.send_message(**arguments)
        elif tool_name == 'send_notification':
            return mcp_server.send_notification(**arguments)
        elif tool_name == 'get_communication_stats':
            return mcp_server.get_all_stats(**arguments)
        elif tool_name == 'health_check_communication':
            return mcp_server.health_check_all()
        else:
            return {'success': False, 'error': f'Unknown tool: {tool_name}'}
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return {'success': False, 'error': str(e)}


if __name__ == '__main__':
    print("Email Communication MCP Server")
    print("=" * 50)
    
    # Health check
    health = mcp_server.health_check_all()
    print(f"Health: {json.dumps(health, indent=2)}")
    
    # Test stats
    stats = mcp_server.get_all_stats(7)
    print(f"\nStats: {json.dumps(stats, indent=2)}")
