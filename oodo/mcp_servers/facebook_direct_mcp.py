"""
Facebook Direct MCP Server
Lightweight Facebook integration without complex token setup
Uses simple HTTP requests to Graph API
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
import requests

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'odoo_mcp.env')
load_dotenv(env_path)

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'facebook_mcp.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FacebookDirectMCP:
    """
    Direct Facebook integration
    Minimal setup - just needs Page ID and Access Token
    
    Mock Mode: If token is 'mock_token', returns sample data for testing
    """

    def __init__(self):
        self.page_id = os.getenv('FACEBOOK_PAGE_ID', '956241877582673')
        # Use mock token by default for testing
        env_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN', '')
        self.access_token = env_token if env_token and env_token != 'test_token_replace_with_actual_token' else 'mock_token'
        self.base_url = 'https://graph.facebook.com/v18.0'
        self.mock_mode = self.access_token == 'mock_token'
        
        logger.info(f"Facebook Direct MCP initialized for Page: {self.page_id} (Mock: {self.mock_mode})")

    def is_configured(self) -> bool:
        """Check if Facebook is properly configured"""
        return bool(self.access_token) and self.access_token not in ['test_token_replace_with_actual_token', '']

    def get_mock_posts(self) -> list:
        """Return mock posts for testing"""
        return [
            {
                'id': f'{self.page_id}_1',
                'message': 'Welcome to Gold Tier! Our new business management system is now live.',
                'created_time': '2026-03-25T10:00:00+0000',
                'likes': {'summary': {'total_count': 45}},
                'comments': {'summary': {'total_count': 12}},
                'shares': {'count': 8}
            },
            {
                'id': f'{self.page_id}_2',
                'message': 'Check out our latest services! Visit our website for more info.',
                'created_time': '2026-03-24T14:30:00+0000',
                'likes': {'summary': {'total_count': 32}},
                'comments': {'summary': {'total_count': 7}},
                'shares': {'count': 5}
            },
            {
                'id': f'{self.page_id}_3',
                'message': 'Thank you for 1000 followers! We appreciate your support.',
                'created_time': '2026-03-23T09:15:00+0000',
                'likes': {'summary': {'total_count': 128}},
                'comments': {'summary': {'total_count': 34}},
                'shares': {'count': 15}
            }
        ]

    def get_mock_page_info(self) -> dict:
        """Return mock page info for testing"""
        return {
            'id': self.page_id,
            'name': 'Gold Tier',
            'about': 'Business Management Solutions',
            'category': 'Business Service',
            'followers_count': 1250,
            'likes': 1180,
            'website': 'https://goldtier.example.com',
            'phone': '+1234567890',
            'email': 'info@goldtier.example.com'
        }

    def health_check(self) -> Dict:
        """Quick health check"""
        if self.mock_mode:
            return {
                'status': 'mock_mode',
                'page_id': self.page_id,
                'message': 'Running in mock mode with sample data',
                'timestamp': datetime.now().isoformat()
            }
        
        if not self.is_configured():
            return {
                'status': 'not_configured',
                'page_id': self.page_id,
                'message': 'Access token not configured. Please update .env file.',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            response = requests.get(
                f'{self.base_url}/{self.page_id}',
                params={'access_token': self.access_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'healthy',
                    'page_id': self.page_id,
                    'page_name': data.get('name', 'Unknown'),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'page_id': self.page_id,
                    'error': response.json().get('error', {}).get('message', 'Unknown error'),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_page_info(self) -> Dict:
        """Get Facebook page information"""
        if self.mock_mode:
            return {'success': True, 'data': self.get_mock_page_info(), 'mock': True}
        
        if not self.is_configured():
            return {'success': False, 'error': 'Facebook not configured'}
        
        try:
            response = requests.get(
                f'{self.base_url}/{self.page_id}',
                params={
                    'access_token': self.access_token,
                    'fields': 'id,name,about,category,followers_count,likes,website,phone,email'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': response.json().get('error', {}).get('message')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_posts(self, limit: int = 10) -> Dict:
        """Get recent posts from page"""
        if self.mock_mode:
            posts = self.get_mock_posts()
            return {'success': True, 'data': posts[:limit], 'mock': True}
        
        if not self.is_configured():
            return {'success': False, 'error': 'Facebook not configured'}
        
        try:
            response = requests.get(
                f'{self.base_url}/{self.page_id}/posts',
                params={
                    'access_token': self.access_token,
                    'limit': limit
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json().get('data', [])}
            else:
                return {'success': False, 'error': response.json().get('error', {}).get('message')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_post(self, message: str, link: Optional[str] = None) -> Dict:
        """Create a new post on page"""
        if self.mock_mode:
            # Return mock success response
            post_id = f"{self.page_id}_{int(datetime.now().timestamp())}"
            return {
                'success': True,
                'post_id': post_id,
                'message': 'Post created successfully (Mock Mode)',
                'mock': True,
                'post_data': {
                    'id': post_id,
                    'message': message,
                    'link': link,
                    'created_time': datetime.now().isoformat()
                }
            }
        
        if not self.is_configured():
            return {'success': False, 'error': 'Facebook not configured'}
        
        try:
            data = {
                'message': message,
                'access_token': self.access_token
            }
            
            if link:
                data['link'] = link
            
            response = requests.post(
                f'{self.base_url}/{self.page_id}/feed',
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'post_id': result.get('id'),
                    'message': 'Post created successfully'
                }
            else:
                return {'success': False, 'error': response.json().get('error', {}).get('message')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def post_photo(self, photo_url: str, caption: str = '') -> Dict:
        """Post photo to page"""
        if not self.is_configured():
            return {'success': False, 'error': 'Facebook not configured'}
        
        try:
            response = requests.post(
                f'{self.base_url}/{self.page_id}/photos',
                data={
                    'url': photo_url,
                    'caption': caption,
                    'access_token': self.access_token
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'photo_id': result.get('id'),
                    'message': 'Photo posted successfully'
                }
            else:
                return {'success': False, 'error': response.json().get('error', {}).get('message')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_insights(self, metric: str = 'page_impressions_unique', days: int = 7) -> Dict:
        """Get page insights/analytics"""
        if not self.is_configured():
            return {'success': False, 'error': 'Facebook not configured'}
        
        from datetime import timedelta
        
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        until_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            response = requests.get(
                f'{self.base_url}/{self.page_id}/insights',
                params={
                    'metric': metric,
                    'since': since_date,
                    'until': until_date,
                    'access_token': self.access_token
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json().get('data', [])}
            else:
                return {'success': False, 'error': response.json().get('error', {}).get('message')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_post(self, post_id: str) -> Dict:
        """Delete a post"""
        if not self.is_configured():
            return {'success': False, 'error': 'Facebook not configured'}
        
        try:
            response = requests.delete(
                f'{self.base_url}/{post_id}',
                params={'access_token': self.access_token},
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'message': 'Post deleted successfully'}
            else:
                return {'success': False, 'error': response.json().get('error', {}).get('message')}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Global MCP instance
mcp_server = FacebookDirectMCP()


# MCP Tools Definition
TOOLS = [
    {
        'name': 'facebook_health_check',
        'description': 'Check Facebook connection status',
        'inputSchema': {'type': 'object', 'properties': {}}
    },
    {
        'name': 'facebook_get_page_info',
        'description': 'Get Facebook page information',
        'inputSchema': {'type': 'object', 'properties': {}}
    },
    {
        'name': 'facebook_get_posts',
        'description': 'Get recent posts from page',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'limit': {'type': 'integer', 'default': 10}
            }
        }
    },
    {
        'name': 'facebook_create_post',
        'description': 'Create a new post',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'link': {'type': 'string'}
            },
            'required': ['message']
        }
    },
    {
        'name': 'facebook_post_photo',
        'description': 'Post a photo',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'photo_url': {'type': 'string'},
                'caption': {'type': 'string'}
            },
            'required': ['photo_url']
        }
    },
    {
        'name': 'facebook_get_insights',
        'description': 'Get page analytics',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'metric': {'type': 'string', 'default': 'page_impressions_unique'},
                'days': {'type': 'integer', 'default': 7}
            }
        }
    },
    {
        'name': 'facebook_delete_post',
        'description': 'Delete a post',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'post_id': {'type': 'string'}
            },
            'required': ['post_id']
        }
    }
]


def handle_tool_call(tool_name: str, arguments: Dict) -> Dict:
    """Handle MCP tool calls"""
    logger.info(f"Tool call: {tool_name} with args: {arguments}")
    
    try:
        if tool_name == 'facebook_health_check':
            return mcp_server.health_check()
        elif tool_name == 'facebook_get_page_info':
            return mcp_server.get_page_info()
        elif tool_name == 'facebook_get_posts':
            return mcp_server.get_posts(arguments.get('limit', 10))
        elif tool_name == 'facebook_create_post':
            return mcp_server.create_post(arguments.get('message'), arguments.get('link'))
        elif tool_name == 'facebook_post_photo':
            return mcp_server.post_photo(arguments.get('photo_url'), arguments.get('caption'))
        elif tool_name == 'facebook_get_insights':
            return mcp_server.get_insights(arguments.get('metric'), arguments.get('days'))
        elif tool_name == 'facebook_delete_post':
            return mcp_server.delete_post(arguments.get('post_id'))
        else:
            return {'success': False, 'error': f'Unknown tool: {tool_name}'}
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return {'success': False, 'error': str(e)}


if __name__ == '__main__':
    print("=" * 60)
    print("FACEBOOK DIRECT MCP SERVER")
    print("=" * 60)
    
    # Health check
    print("\n1. Health Check:")
    health = mcp_server.health_check()
    print(json.dumps(health, indent=2))
    
    # Show configuration status
    print("\n2. Configuration Status:")
    print(f"   Page ID: {mcp_server.page_id}")
    print(f"   Token Configured: {'Yes' if mcp_server.is_configured() else 'No'}")
    
    # Quick test
    if mcp_server.is_configured():
        print("\n3. Testing Page Info:")
        info = mcp_server.get_page_info()
        print(json.dumps(info, indent=2))
    else:
        print("\n⚠️  Facebook not configured yet.")
        print("\n   To configure:")
        print("   1. Get access token from: https://developers.facebook.com/tools/explorer/")
        print("   2. Update .env file:")
        print("      FACEBOOK_PAGE_ACCESS_TOKEN=your_actual_token_here")
        print("   3. Restart server")
    
    print("\n" + "=" * 60)
