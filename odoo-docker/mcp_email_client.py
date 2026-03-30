#!/usr/bin/env python3
"""
MCP Email Client - Client library for MCP Email Server

This module provides a client to communicate with the MCP email server.
Used by orchestrator to send emails when files are approved.

Usage:
    from mcp_email_client import MCPEmailClient
    
    client = MCPEmailClient()
    result = client.send_email("to@example.com", "Subject", "Body")
"""

import os
import sys
import json
import logging
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Try to import MCP client
try:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class MCPEmailClient:
    """Client for MCP Email Server"""
    
    def __init__(self, server_path: Optional[str] = None):
        self.server_path = server_path or Path(__file__).parent / 'email_mcp.js'
        self.logger = logging.getLogger('mcp_email_client')
        
        # Check if server exists
        if not self.server_path.exists():
            # Try Python version
            self.server_path = Path(__file__).parent / 'mcp_email_server.py'
        
        self.server_process = None
    
    async def send_email(self, to: str, subject: str, body: str, html: bool = False) -> Dict[str, Any]:
        """
        Send email via MCP server
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            html: Whether body is HTML
        
        Returns:
            Dict with success status
        """
        if not MCP_AVAILABLE:
            return {
                'success': False,
                'error': 'MCP client not installed. Install with: pip install mcp'
            }
        
        try:
            # Start MCP server
            cmd = ['node', str(self.server_path)] if self.server_path.suffix == '.js' else ['python', str(self.server_path)]
            
            self.server_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            async with stdio_client(self.server_process.stdin, self.server_process.stdout) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize
                    await session.initialize()
                    
                    # Call send_email tool
                    result = await session.call_tool(
                        'send_email',
                        {
                            'to': to,
                            'subject': subject,
                            'body': body,
                            'html': html
                        }
                    )
                    
                    # Parse result
                    if result.content:
                        response_text = result.content[0].text
                        return json.loads(response_text)
                    
                    return {'success': False, 'error': 'No response from server'}
                    
        except Exception as e:
            self.logger.error(f"MCP email error: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if self.server_process:
                self.server_process.terminate()
    
    async def check_config(self) -> Dict[str, Any]:
        """Check email configuration"""
        if not MCP_AVAILABLE:
            return {'configured': False, 'error': 'MCP not available'}
        
        try:
            cmd = ['node', str(self.server_path)] if self.server_path.suffix == '.js' else ['python', str(self.server_path)]
            
            self.server_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            async with stdio_client(self.server_process.stdin, self.server_process.stdout) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    result = await session.call_tool('check_email_config', {})
                    
                    if result.content:
                        response_text = result.content[0].text
                        return json.loads(response_text)
                    
                    return {'configured': False}
                    
        except Exception as e:
            return {'configured': False, 'error': str(e)}
        finally:
            if self.server_process:
                self.server_process.terminate()


def send_email_sync(to: str, subject: str, body: str, html: bool = False) -> Dict[str, Any]:
    """Synchronous wrapper for send_email"""
    client = MCPEmailClient()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(client.send_email(to, subject, body, html))


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) >= 4:
        to = sys.argv[1]
        subject = sys.argv[2]
        body = sys.argv[3]
        
        result = send_email_sync(to, subject, body)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python mcp_email_client.py <to> <subject> <body>")
