#!/usr/bin/env python3
"""
MCP Email Server - Exposes send_email tool via Model Context Protocol

This server allows AI assistants to send emails via SMTP/Gmail API.

Usage:
    python mcp_email_server.py

Or with credentials:
    python mcp_email_server.py --email your@email.com --password app-password
"""

import os
import sys
import json
import logging
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Any, Dict, Optional

# Try to import MCP
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP package not installed. Install with: pip install mcp")
    sys.exit(1)


# ============================================================================
# Configuration
# ============================================================================

class EmailConfig:
    """Email configuration"""

    def __init__(self):
        # Load from .env file first
        env_file = Path(__file__).parent / '.env'
        if env_file.exists():
            self._load_env_file(env_file)

        # Load from config file or environment
        config_file = Path(__file__).parent / 'email_config.json'

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.smtp_server = config.get('smtp_server', os.getenv('SMTP_SERVER', 'smtp.gmail.com'))
            self.smtp_port = config.get('smtp_port', int(os.getenv('SMTP_PORT', '587')))
            self.email_address = config.get('email', os.getenv('EMAIL_ADDRESS', ''))
            self.app_password = config.get('app_password', os.getenv('EMAIL_PASSWORD', ''))
        else:
            self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
            self.email_address = os.getenv('EMAIL_ADDRESS', '')
            self.app_password = os.getenv('EMAIL_PASSWORD', '')

    def _load_env_file(self, env_file: Path):
        """Load environment variables from .env file"""
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value and not os.getenv(key):
                        os.environ[key] = value

    def is_configured(self) -> bool:
        """Check if email is configured"""
        return bool(self.email_address and self.app_password)


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(logs_folder: Path) -> logging.Logger:
    """Configure logging"""
    os.makedirs(logs_folder, exist_ok=True)
    
    log_file = logs_folder / 'mcp_email_server.log'
    
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
    
    logger = logging.getLogger('mcp_email_server')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# ============================================================================
# Email Sender
# ============================================================================

class EmailSender:
    """Send emails via SMTP"""
    
    def __init__(self, config: EmailConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
    
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> Dict[str, Any]:
        """
        Send email via SMTP
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            html: Whether body is HTML
        
        Returns:
            Dict with success status and message
        """
        if not self.config.is_configured():
            return {
                'success': False,
                'error': 'Email not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.'
            }
        
        try:
            self.logger.info(f"Sending email to: {to}")
            self.logger.info(f"Subject: {subject}")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.email_address
            msg['To'] = to
            
            # Attach body
            content_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, content_type, 'utf-8'))
            
            # Send via SMTP
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.email_address, self.config.app_password)
                server.send_message(msg)
            
            self.logger.info(f"Email sent successfully to {to}")
            
            return {
                'success': True,
                'message': f'Email sent to {to}',
                'subject': subject,
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }
            
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP Authentication failed: {e}")
            return {
                'success': False,
                'error': f'Authentication failed. Check app password. {str(e)}'
            }
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error: {e}")
            return {
                'success': False,
                'error': f'SMTP error: {str(e)}'
            }
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return {
                'success': False,
                'error': f'Error: {str(e)}'
            }


# ============================================================================
# MCP Server
# ============================================================================

class MCPEmailServer:
    """MCP Server for email operations"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.logs_folder = Path(__file__).parent / 'logs'
        self.logger = setup_logging(self.logs_folder)
        self.email_sender = EmailSender(config, self.logger)
        
        # Create MCP server
        self.server = Server("email-server")
        
        # Register tools
        @self.server.list_tools()
        async def list_tools() -> list:
            """List available tools"""
            return [
                Tool(
                    name="send_email",
                    description="Send an email via SMTP/Gmail. Requires recipient, subject, and body.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "Recipient email address"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject line"
                            },
                            "body": {
                                "type": "string",
                                "description": "Email body content"
                            },
                            "html": {
                                "type": "boolean",
                                "description": "Whether body is HTML format (default: false)",
                                "default": False
                            }
                        },
                        "required": ["to", "subject", "body"]
                    }
                ),
                Tool(
                    name="check_email_config",
                    description="Check if email server is configured properly",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> list:
            """Handle tool calls"""
            self.logger.info(f"Tool called: {name}")
            self.logger.info(f"Arguments: {arguments}")
            
            if name == "send_email":
                return await self.handle_send_email(arguments)
            elif name == "check_email_config":
                return await self.handle_check_config()
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
    
    async def handle_send_email(self, arguments: Dict[str, Any]) -> list:
        """Handle send_email tool call"""
        to = arguments.get('to', '')
        subject = arguments.get('subject', '')
        body = arguments.get('body', '')
        html = arguments.get('html', False)
        
        if not to:
            return [TextContent(
                type="text",
                text=json.dumps({'success': False, 'error': 'Missing "to" parameter'})
            )]
        
        if not subject:
            return [TextContent(
                type="text",
                text=json.dumps({'success': False, 'error': 'Missing "subject" parameter'})
            )]
        
        if not body:
            return [TextContent(
                type="text",
                text=json.dumps({'success': False, 'error': 'Missing "body" parameter'})
            )]
        
        # Send email
        result = self.email_sender.send_email(to, subject, body, html)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    async def handle_check_config(self) -> list:
        """Handle check_email_config tool call"""
        is_configured = self.config.is_configured()
        
        return [TextContent(
            type="text",
            text=json.dumps({
                'configured': is_configured,
                'email': self.config.email_address if is_configured else 'Not configured',
                'smtp_server': self.config.smtp_server,
                'smtp_port': self.config.smtp_port
            }, indent=2)
        )]
    
    async def run(self):
        """Run the MCP server"""
        self.logger.info("Starting MCP Email Server...")
        self.logger.info(f"Email configured: {self.config.is_configured()}")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='MCP Email Server - Send emails via MCP protocol'
    )
    parser.add_argument(
        '--email',
        type=str,
        default=None,
        help='Email address (or set EMAIL_ADDRESS env var)'
    )
    parser.add_argument(
        '--password',
        type=str,
        default=None,
        help='App password (or set EMAIL_PASSWORD env var)'
    )
    parser.add_argument(
        '--smtp-server',
        type=str,
        default='smtp.gmail.com',
        help='SMTP server (default: smtp.gmail.com)'
    )
    parser.add_argument(
        '--smtp-port',
        type=int,
        default=587,
        help='SMTP port (default: 587)'
    )
    parser.add_argument(
        '--save-config',
        action='store_true',
        help='Save configuration to email_config.json'
    )
    
    args = parser.parse_args()
    
    # Load or create config
    config = EmailConfig()
    
    # Apply CLI overrides
    if args.email:
        config.email_address = args.email
    if args.password:
        config.app_password = args.password
    if args.smtp_server:
        config.smtp_server = args.smtp_server
    if args.smtp_port:
        config.smtp_port = args.smtp_port
    
    # Save config if requested
    if args.save_config:
        config_data = {
            'smtp_server': config.smtp_server,
            'smtp_port': config.smtp_port,
            'email': config.email_address,
            'app_password': config.app_password
        }
        config_file = Path(__file__).parent / 'email_config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
        print(f"Configuration saved to: {config_file}")
    
    # Check configuration
    if not config.is_configured():
        print("\n⚠️  WARNING: Email not configured!")
        print("\nSet up email credentials:")
        print("\nOption 1: Command line")
        print(f"  python {sys.argv[0]} --email your@email.com --password app-password --save-config")
        print("\nOption 2: Environment variables")
        print("  set EMAIL_ADDRESS=your@email.com")
        print("  set EMAIL_PASSWORD=your-app-password")
        print("\nOption 3: Create email_config.json")
        print('  {"email": "your@email.com", "app_password": "your-password"}')
        print("\nFor Gmail, use an App Password:")
        print("  https://support.google.com/accounts/answer/185833")
        print("\nServer will start but email sending will fail until configured.\n")
    
    # Run server
    print("\n" + "=" * 60)
    print("MCP Email Server")
    print("=" * 60)
    print(f"Email: {config.email_address if config.email_address else 'Not configured'}")
    print(f"SMTP: {config.smtp_server}:{config.smtp_port}")
    print(f"Status: {'Configured' if config.is_configured() else 'Not configured'}")
    print("=" * 60)
    print("\nStarting MCP server (stdio mode)...")
    print("Press Ctrl+C to stop\n")
    
    server = MCPEmailServer(config)
    
    try:
        import asyncio
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == '__main__':
    main()
