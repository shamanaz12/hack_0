#!/usr/bin/env python3
"""
MCP Facebook/Instagram Server - Connects to Facebook Graph API

Exposes tools for:
- post_to_facebook(message, image_url=None)
- post_to_instagram(message, image_url=None)
- get_facebook_page_insights()

Usage:
    python facebook_mcp_server.py

Or with credentials:
    python facebook_mcp_server.py --access-token TOKEN --page-id PAGE_ID
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode

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

class FacebookConfig:
    """Facebook/Instagram configuration"""

    def __init__(self):
        # Load from .env file first
        env_file = Path(__file__).parent / '.env'
        if env_file.exists():
            self._load_env_file(env_file)

        # Load from environment variables
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN', '')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID', '')
        self.instagram_account_id = os.getenv('INSTAGRAM_ACCOUNT_ID', '')
        self.app_id = os.getenv('FACEBOOK_APP_ID', '')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET', '')

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
        """Check if Facebook is configured"""
        return bool(self.access_token and self.page_id)


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(logs_folder: Path) -> logging.Logger:
    """Configure logging"""
    os.makedirs(logs_folder, exist_ok=True)

    log_file = logs_folder / 'facebook_mcp_server.log'

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

    logger = logging.getLogger('facebook_mcp_server')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# ============================================================================
# Facebook Graph API Client
# ============================================================================

class FacebookClient:
    """Facebook Graph API client"""

    GRAPH_API_VERSION = 'v18.0'
    GRAPH_API_URL = 'https://graph.facebook.com'

    def __init__(self, config: FacebookConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, 
                      method: str = 'GET', data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make request to Facebook Graph API

        Args:
            endpoint: API endpoint (e.g., '/me/feed')
            params: Query parameters
            method: HTTP method (GET, POST, DELETE)
            data: Request body data for POST

        Returns:
            API response as dict
        """
        url = f"{self.GRAPH_API_URL}/{self.GRAPH_API_VERSION}{endpoint}"
        
        # Add access token to params
        if params is None:
            params = {}
        params['access_token'] = self.config.access_token

        # Build URL with query params for GET requests
        if method == 'GET' and params:
            url += '?' + urlencode(params)

        self.logger.debug(f"{method} {url}")
        if data:
            self.logger.debug(f"Data: {json.dumps(data, indent=2)}")

        try:
            if method == 'POST':
                # For POST, send data as form-urlencoded or JSON
                if data:
                    # Facebook prefers form-urlencoded for most endpoints
                    encoded_data = urlencode(data).encode('utf-8')
                else:
                    encoded_data = b''
                
                req = Request(url, data=encoded_data, method=method)
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            else:
                req = Request(url, method=method)

            with urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                self.logger.debug(f"Response: {json.dumps(result, indent=2)}")
                return result

        except HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ''
            self.logger.error(f"HTTP error {e.code}: {error_body}")
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get('error', {}).get('message', str(e))
            except:
                error_msg = str(e)
            raise Exception(f"Facebook API error ({e.code}): {error_msg}")
        except URLError as e:
            self.logger.error(f"URL error: {e.reason}")
            raise Exception(f"Cannot connect to Facebook: {e.reason}")
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            raise Exception(f"Invalid JSON response: {e}")

    def post_to_facebook(self, message: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Post to Facebook Page

        Args:
            message: Post message/content
            image_url: Optional image URL to include

        Returns:
            Post creation result with post ID
        """
        self.logger.info(f"Posting to Facebook Page {self.config.page_id}")

        try:
            endpoint = f'/{self.config.page_id}/feed'
            
            data = {
                'message': message
            }

            if image_url:
                data['link'] = image_url

            result = self._make_request(endpoint, method='POST', data=data)

            self.logger.info(f"Facebook post created: {result}")

            return {
                'success': True,
                'post_id': result.get('id'),
                'message': message,
                'image_url': image_url,
                'platform': 'facebook',
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error posting to Facebook: {e}")
            return {
                'success': False,
                'error': str(e),
                'platform': 'facebook'
            }

    def post_to_instagram(self, message: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Post to Instagram Business account

        Args:
            message: Caption for the post
            image_url: Image URL (required for Instagram)

        Returns:
            Post creation result with media ID
        """
        self.logger.info(f"Posting to Instagram account {self.config.instagram_account_id}")

        if not self.config.instagram_account_id:
            return {
                'success': False,
                'error': 'Instagram Account ID not configured. Set INSTAGRAM_ACCOUNT_ID environment variable.',
                'platform': 'instagram'
            }

        if not image_url:
            return {
                'success': False,
                'error': 'Image URL is required for Instagram posts',
                'platform': 'instagram'
            }

        try:
            # Step 1: Create media container
            create_endpoint = f'/{self.config.instagram_account_id}/media'
            
            # Determine media type based on URL
            media_type = 'IMAGE'
            if image_url.lower().endswith(('.mp4', '.mov')):
                media_type = 'REELS'

            create_data = {
                'image_url': image_url if media_type == 'IMAGE' else None,
                'video_url': image_url if media_type != 'IMAGE' else None,
                'caption': message,
                'media_type': media_type
            }

            # Remove None values
            create_data = {k: v for k, v in create_data.items() if v is not None}

            self.logger.info(f"Creating Instagram media container: {create_data}")
            create_result = self._make_request(create_endpoint, method='POST', data=create_data)
            
            creation_id = create_result.get('id')
            if not creation_id:
                raise Exception("Failed to create media container")

            self.logger.info(f"Media container created: {creation_id}")

            # Step 2: Publish the media
            publish_endpoint = f'/{self.config.instagram_account_id}/media_publish'
            publish_data = {
                'creation_id': creation_id
            }

            publish_result = self._make_request(publish_endpoint, method='POST', data=publish_data)
            
            media_id = publish_result.get('id')
            self.logger.info(f"Instagram post published: {media_id}")

            return {
                'success': True,
                'media_id': media_id,
                'creation_id': creation_id,
                'caption': message,
                'image_url': image_url,
                'media_type': media_type,
                'platform': 'instagram',
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error posting to Instagram: {e}")
            return {
                'success': False,
                'error': str(e),
                'platform': 'instagram'
            }

    def get_facebook_page_insights(self) -> Dict[str, Any]:
        """
        Get Facebook Page insights/metrics

        Returns:
            Page insights data
        """
        self.logger.info(f"Getting insights for Facebook Page {self.config.page_id}")

        try:
            metrics = [
                'page_impressions',
                'page_reach',
                'page_engaged_users',
                'page_post_engagements',
                'page_likes',
                'page_followers',
                'page_views'
            ]

            endpoint = f'/{self.config.page_id}/insights'
            params = {
                'metric': ','.join(metrics),
                'period': 'day'
            }

            result = self._make_request(endpoint, params=params)

            # Format insights for easier reading
            formatted_insights = {}
            if 'data' in result:
                for metric_data in result['data']:
                    metric_name = metric_data.get('name')
                    values = metric_data.get('values', [])
                    if values:
                        formatted_insights[metric_name] = {
                            'value': values[-1].get('value'),
                            'end_time': values[-1].get('end_time'),
                            'title': metric_data.get('title')
                        }

            return {
                'success': True,
                'page_id': self.config.page_id,
                'insights': formatted_insights,
                'raw_data': result,
                'platform': 'facebook',
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error getting Facebook insights: {e}")
            return {
                'success': False,
                'error': str(e),
                'platform': 'facebook'
            }

    def verify_token(self) -> Dict[str, Any]:
        """
        Verify the access token and get token info

        Returns:
            Token verification result
        """
        self.logger.info("Verifying Facebook access token")

        try:
            endpoint = '/me'
            params = {
                'fields': 'id,name,picture'
            }

            result = self._make_request(endpoint, params=params)

            return {
                'success': True,
                'valid': True,
                'user_id': result.get('id'),
                'name': result.get('name'),
                'page_id': self.config.page_id,
                'instagram_account_id': self.config.instagram_account_id,
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Token verification failed: {e}")
            return {
                'success': False,
                'valid': False,
                'error': str(e)
            }


# ============================================================================
# MCP Server
# ============================================================================

class MCPFacebookServer:
    """MCP Server for Facebook/Instagram operations"""

    def __init__(self, config: FacebookConfig):
        self.config = config
        self.logs_folder = Path(__file__).parent / 'logs'
        self.logger = setup_logging(self.logs_folder)
        self.facebook_client = FacebookClient(config, self.logger)

        # Create MCP server
        self.server = Server("facebook-server")

        # Register tools
        @self.server.list_tools()
        async def list_tools() -> list:
            """List available tools"""
            return [
                Tool(
                    name="post_to_facebook",
                    description="Post a message to a Facebook Page. Optionally include an image URL.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message/content to post"
                            },
                            "image_url": {
                                "type": "string",
                                "description": "Optional image URL to include in the post"
                            }
                        },
                        "required": ["message"]
                    }
                ),
                Tool(
                    name="post_to_instagram",
                    description="Post to Instagram Business account. Requires image URL and caption.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Caption for the Instagram post"
                            },
                            "image_url": {
                                "type": "string",
                                "description": "URL of the image to post (required for Instagram)"
                            }
                        },
                        "required": ["message", "image_url"]
                    }
                ),
                Tool(
                    name="get_facebook_page_insights",
                    description="Get Facebook Page insights including reach, impressions, and engagement metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="verify_facebook_token",
                    description="Verify the Facebook access token and connection",
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

            if name == "post_to_facebook":
                return await self.handle_post_to_facebook(arguments)
            elif name == "post_to_instagram":
                return await self.handle_post_to_instagram(arguments)
            elif name == "get_facebook_page_insights":
                return await self.handle_get_insights(arguments)
            elif name == "verify_facebook_token":
                return await self.handle_verify_token(arguments)
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]

    async def handle_post_to_facebook(self, arguments: Dict[str, Any]) -> list:
        """Handle post_to_facebook tool call"""
        message = arguments.get('message', '')
        image_url = arguments.get('image_url')

        if not message:
            return [TextContent(
                type="text",
                text=json.dumps({'success': False, 'error': 'Missing "message" parameter'})
            )]

        result = self.facebook_client.post_to_facebook(message, image_url)

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    async def handle_post_to_instagram(self, arguments: Dict[str, Any]) -> list:
        """Handle post_to_instagram tool call"""
        message = arguments.get('message', '')
        image_url = arguments.get('image_url')

        if not message:
            return [TextContent(
                type="text",
                text=json.dumps({'success': False, 'error': 'Missing "message" parameter'})
            )]

        if not image_url:
            return [TextContent(
                type="text",
                text=json.dumps({'success': False, 'error': 'Missing "image_url" parameter'})
            )]

        result = self.facebook_client.post_to_instagram(message, image_url)

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    async def handle_get_insights(self, arguments: Dict[str, Any]) -> list:
        """Handle get_facebook_page_insights tool call"""
        result = self.facebook_client.get_facebook_page_insights()

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    async def handle_verify_token(self, arguments: Dict[str, Any]) -> list:
        """Handle verify_facebook_token tool call"""
        result = self.facebook_client.verify_token()

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    async def run(self):
        """Run the MCP server"""
        self.logger.info("Starting MCP Facebook/Instagram Server...")
        self.logger.info(f"Page ID: {self.config.page_id}")
        self.logger.info(f"Instagram Account ID: {self.config.instagram_account_id}")
        self.logger.info(f"Access Token configured: {bool(self.config.access_token)}")
        self.logger.info(f"Configured: {self.config.is_configured()}")

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
        description='MCP Facebook/Instagram Server - Post to social media via Graph API'
    )
    parser.add_argument(
        '--access-token',
        type=str,
        default=None,
        help='Facebook Page Access Token (or set FACEBOOK_ACCESS_TOKEN env var)'
    )
    parser.add_argument(
        '--page-id',
        type=str,
        default=None,
        help='Facebook Page ID (or set FACEBOOK_PAGE_ID env var)'
    )
    parser.add_argument(
        '--instagram-account-id',
        type=str,
        default=None,
        help='Instagram Business Account ID (or set INSTAGRAM_ACCOUNT_ID env var)'
    )
    parser.add_argument(
        '--app-id',
        type=str,
        default=None,
        help='Facebook App ID (or set FACEBOOK_APP_ID env var)'
    )
    parser.add_argument(
        '--app-secret',
        type=str,
        default=None,
        help='Facebook App Secret (or set FACEBOOK_APP_SECRET env var)'
    )

    args = parser.parse_args()

    # Load or create config
    config = FacebookConfig()

    # Apply CLI overrides
    if args.access_token:
        config.access_token = args.access_token
    if args.page_id:
        config.page_id = args.page_id
    if args.instagram_account_id:
        config.instagram_account_id = args.instagram_account_id
    if args.app_id:
        config.app_id = args.app_id
    if args.app_secret:
        config.app_secret = args.app_secret

    # Check configuration
    if not config.is_configured():
        print("\n⚠️  WARNING: Facebook/Instagram not configured!")
        print("\nSet up Facebook credentials:")
        print("\nOption 1: Environment variables")
        print("  set FACEBOOK_ACCESS_TOKEN=your-access-token")
        print("  set FACEBOOK_PAGE_ID=your-page-id")
        print("  set INSTAGRAM_ACCOUNT_ID=your-instagram-account-id")
        print("\nOption 2: Command line")
        print(f"  python {sys.argv[0]} --access-token TOKEN --page-id PAGE_ID")
        print("\nSee FACEBOOK_SETUP.md for instructions to get credentials.\n")

    # Run server
    print("\n" + "=" * 60)
    print("MCP Facebook/Instagram Server")
    print("=" * 60)
    print(f"Page ID: {config.page_id if config.page_id else 'Not configured'}")
    print(f"Instagram Account ID: {config.instagram_account_id if config.instagram_account_id else 'Not configured'}")
    print(f"Access Token: {'Configured' if config.access_token else 'Not configured'}")
    print(f"Status: {'Configured' if config.is_configured() else 'Not configured'}")
    print("=" * 60)
    print("\nStarting MCP server (stdio mode)...")
    print("Press Ctrl+C to stop\n")

    server = MCPFacebookServer(config)

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
