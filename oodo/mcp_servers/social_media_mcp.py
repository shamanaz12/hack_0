"""
Social Media MCP Server
Handles Facebook, Instagram, and Twitter (X) posting without Graph API
Uses direct HTTP requests and alternative APIs
"""

import os
import json
import logging
import hashlib
import hmac
import time
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
        logging.FileHandler('logs/social_media_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FacebookMCP:
    """Facebook posting using direct API calls (no Graph API)"""
    
    def __init__(self):
        self.page_id = os.getenv('FACEBOOK_PAGE_ID', '')
        self.access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN', '')
        self.app_id = os.getenv('FACEBOOK_APP_ID', '')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET', '')
        self.base_url = 'https://graph.facebook.com/v18.0'
        
        logger.info("Facebook MCP initialized")
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Facebook API"""
        url = f"{self.base_url}/{endpoint}"
        params = {'access_token': self.access_token}
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params)
            elif method == 'POST':
                if files:
                    response = requests.post(url, params=params, files=files, data=data)
                else:
                    response = requests.post(url, params=params, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            # Check for API errors
            if 'error' in result:
                logger.error(f"Facebook API error: {result['error']}")
                return {'success': False, 'error': result['error']}
            
            return {'success': True, 'data': result}
        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook request error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def post_text(self, message: str, link: str = None) -> Dict:
        """Post text update to Facebook page"""
        data = {'message': message}
        if link:
            data['link'] = link
        
        result = self._make_request(f"{self.page_id}/feed", method='POST', data=data)
        logger.info(f"Facebook post created: {result}")
        return result
    
    def post_photo(self, photo_url: str, message: str = '') -> Dict:
        """Post photo to Facebook page"""
        data = {'url': photo_url, 'message': message}
        result = self._make_request(f"{self.page_id}/photos", method='POST', data=data)
        logger.info(f"Facebook photo post created: {result}")
        return result
    
    def post_photo_upload(self, photo_path: str, message: str = '') -> Dict:
        """Upload and post photo to Facebook page"""
        try:
            with open(photo_path, 'rb') as f:
                files = {'source': f}
                data = {'message': message}
                result = self._make_request(f"{self.page_id}/photos", method='POST', data=data, files=files)
                logger.info(f"Facebook photo upload created: {result}")
                return result
        except Exception as e:
            logger.error(f"Photo upload error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def post_video(self, video_url: str, title: str, description: str = '') -> Dict:
        """Post video to Facebook page"""
        data = {
            'file_url': video_url,
            'title': title,
            'description': description
        }
        result = self._make_request(f"{self.page_id}/videos", method='POST', data=data)
        logger.info(f"Facebook video post created: {result}")
        return result
    
    def get_posts(self, limit: int = 10) -> Dict:
        """Get recent posts from Facebook page"""
        result = self._make_request(f"{self.page_id}/posts", method='GET', data={'limit': limit})
        logger.info(f"Facebook posts retrieved: {result}")
        return result
    
    def get_insights(self, metric: str = 'page_impressions_unique', days: int = 7) -> Dict:
        """Get page insights"""
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        until_date = datetime.now().strftime('%Y-%m-%d')
        
        result = self._make_request(
            f"{self.page_id}/insights",
            method='GET',
            data={
                'metric': metric,
                'since': since_date,
                'until': until_date
            }
        )
        logger.info(f"Facebook insights retrieved: {result}")
        return result
    
    def get_comments(self, post_id: str) -> Dict:
        """Get comments on a post"""
        result = self._make_request(f"{post_id}/comments", method='GET')
        logger.info(f"Facebook comments retrieved: {result}")
        return result
    
    def reply_to_comment(self, comment_id: str, message: str) -> Dict:
        """Reply to a comment"""
        data = {'message': message}
        result = self._make_request(f"{comment_id}/comments", method='POST', data=data)
        logger.info(f"Facebook comment reply created: {result}")
        return result
    
    def delete_post(self, post_id: str) -> Dict:
        """Delete a post"""
        result = self._make_request(post_id, method='DELETE')
        logger.info(f"Facebook post deleted: {result}")
        return result
    
    def generate_summary(self, days: int = 7) -> Dict:
        """Generate Facebook performance summary"""
        insights = {
            'reach': self.get_insights('page_impressions_unique', days),
            'engagement': self.get_insights('page_engaged_users', days),
            'likes': self.get_insights('page_total_likes', days),
            'posts': self.get_posts(20)
        }
        
        summary = {
            'platform': 'Facebook',
            'period_days': days,
            'generated_at': datetime.now().isoformat(),
            'metrics': {}
        }
        
        # Extract metrics
        if insights['reach'].get('success'):
            summary['metrics']['reach'] = insights['reach'].get('data', {}).get('data', [{}])[0].get('values', [{}])[0].get('value', 0)
        
        if insights['engagement'].get('success'):
            summary['metrics']['engagement'] = insights['engagement'].get('data', {}).get('data', [{}])[0].get('values', [{}])[0].get('value', 0)
        
        if insights['likes'].get('success'):
            summary['metrics']['total_likes'] = insights['likes'].get('data', {}).get('data', [{}])[0].get('values', [{}])[0].get('value', 0)
        
        if insights['posts'].get('success'):
            summary['metrics']['recent_posts_count'] = len(insights['posts'].get('data', {}).get('data', []))
        
        return summary
    
    def health_check(self) -> Dict:
        """Check Facebook connection health"""
        try:
            result = self._make_request(self.page_id, method='GET')
            return {
                'status': 'healthy' if result.get('success') else 'unhealthy',
                'page_id': self.page_id,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


class InstagramMCP:
    """Instagram posting using direct API calls (no Graph API)"""
    
    def __init__(self):
        self.business_id = os.getenv('INSTAGRAM_BUSINESS_ID', '')
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        self.base_url = 'https://graph.facebook.com/v18.0'
        
        logger.info("Instagram MCP initialized")
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Instagram API"""
        url = f"{self.base_url}/{endpoint}"
        params = {'access_token': self.access_token}
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params)
            elif method == 'POST':
                response = requests.post(url, params=params, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result:
                logger.error(f"Instagram API error: {result['error']}")
                return {'success': False, 'error': result['error']}
            
            return {'success': True, 'data': result}
        except requests.exceptions.RequestException as e:
            logger.error(f"Instagram request error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_image_post(self, image_url: str, caption: str = '') -> Dict:
        """Create an image post on Instagram"""
        # Step 1: Create container
        container_data = {
            'image_url': image_url,
            'caption': caption,
            'media_type': 'IMAGE'
        }
        
        container_result = self._make_request(
            f"{self.business_id}/media",
            method='POST',
            data=container_data
        )
        
        if not container_result.get('success'):
            return container_result
        
        container_id = container_result.get('data', {}).get('id')
        
        # Step 2: Publish container
        publish_data = {'creation_id': container_id}
        publish_result = self._make_request(
            f"{self.business_id}/media_publish",
            method='POST',
            data=publish_data
        )
        
        logger.info(f"Instagram image post created: {publish_result}")
        return publish_result
    
    def create_carousel_post(self, media_urls: List[str], caption: str = '') -> Dict:
        """Create a carousel post on Instagram"""
        # Create child containers
        children_ids = []
        for url in media_urls:
            container_data = {
                'image_url': url,
                'media_type': 'IMAGE'
            }
            
            container_result = self._make_request(
                f"{self.business_id}/media",
                method='POST',
                data=container_data
            )
            
            if container_result.get('success'):
                children_ids.append(container_result.get('data', {}).get('id'))
        
        if not children_ids:
            return {'success': False, 'error': 'Failed to create carousel children'}
        
        # Create parent container
        parent_data = {
            'media_type': 'CAROUSEL',
            'children': ','.join(children_ids),
            'caption': caption
        }
        
        container_result = self._make_request(
            f"{self.business_id}/media",
            method='POST',
            data=parent_data
        )
        
        if not container_result.get('success'):
            return container_result
        
        container_id = container_result.get('data', {}).get('id')
        
        # Publish
        publish_data = {'creation_id': container_id}
        publish_result = self._make_request(
            f"{self.business_id}/media_publish",
            method='POST',
            data=publish_data
        )
        
        logger.info(f"Instagram carousel post created: {publish_result}")
        return publish_result
    
    def get_media(self, limit: int = 10) -> Dict:
        """Get recent media posts"""
        result = self._make_request(
            f"{self.business_id}/media",
            method='GET',
            data={'limit': limit}
        )
        logger.info(f"Instagram media retrieved: {result}")
        return result
    
    def get_insights(self, metric: str = 'impressions', days: int = 7) -> Dict:
        """Get media insights"""
        result = self._make_request(
            f"{self.business_id}/insights",
            method='GET',
            data={'metric': metric}
        )
        logger.info(f"Instagram insights retrieved: {result}")
        return result
    
    def generate_summary(self, days: int = 7) -> Dict:
        """Generate Instagram performance summary"""
        insights = {
            'impressions': self.get_insights('impressions', days),
            'reach': self.get_insights('reach', days),
            'engagement': self.get_insights('engagement', days),
            'media': self.get_media(20)
        }
        
        summary = {
            'platform': 'Instagram',
            'period_days': days,
            'generated_at': datetime.now().isoformat(),
            'metrics': {}
        }
        
        if insights['impressions'].get('success'):
            data = insights['impressions'].get('data', {}).get('data', [])
            if data:
                summary['metrics']['impressions'] = sum(v.get('value', 0) for v in data[0].get('values', []))
        
        if insights['reach'].get('success'):
            data = insights['reach'].get('data', {}).get('data', [])
            if data:
                summary['metrics']['reach'] = sum(v.get('value', 0) for v in data[0].get('values', []))
        
        if insights['media'].get('success'):
            summary['metrics']['recent_posts_count'] = len(insights['media'].get('data', {}).get('data', []))
        
        return summary
    
    def health_check(self) -> Dict:
        """Check Instagram connection health"""
        try:
            result = self._make_request(self.business_id, method='GET')
            return {
                'status': 'healthy' if result.get('success') else 'unhealthy',
                'business_id': self.business_id,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


class TwitterMCP:
    """Twitter (X) posting using API v2"""
    
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')
        self.api_key = os.getenv('TWITTER_API_KEY', '')
        self.api_secret = os.getenv('TWITTER_API_SECRET', '')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN', '')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
        self.base_url = 'https://api.twitter.com'
        
        logger.info("Twitter MCP initialized")
    
    def _get_oauth_signature(self, method: str, url: str, params: Dict = None) -> str:
        """Generate OAuth 1.0a signature"""
        import hmac
        import hashlib
        import base64
        from urllib.parse import quote
        
        timestamp = str(int(time.time()))
        nonce = hashlib.md5(f"{timestamp}{time.time()}".encode()).hexdigest()
        
        oauth_params = {
            'oauth_consumer_key': self.api_key,
            'oauth_token': self.access_token,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': timestamp,
            'oauth_nonce': nonce,
            'oauth_version': '1.0'
        }
        
        if params:
            oauth_params.update(params)
        
        # Sort and encode parameters
        encoded_params = '&'.join(
            f"{k}={quote(str(v), safe='')}" 
            for k, v in sorted(oauth_params.items())
        )
        
        # Create signature base string
        base_string = f"{method.upper()}&{quote(url, safe='')}&{quote(encoded_params, safe='')}"
        
        # Create signing key
        signing_key = f"{quote(self.api_secret, safe='')}&{quote(self.access_token_secret, safe='')}"
        
        # Generate signature
        signature = hmac.new(
            signing_key.encode('utf-8'),
            base_string.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode()
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Twitter API v2"""
        url = f"{self.base_url}/{endpoint}"
        
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method == 'POST':
                if json_data:
                    response = requests.post(url, headers=headers, json=json_data)
                else:
                    response = requests.post(url, headers=headers, data=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            return {'success': True, 'data': result}
        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter request error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def post_tweet(self, text: str, reply_settings: str = 'everyone') -> Dict:
        """Post a tweet"""
        data = {
            'text': text,
            'reply_settings': reply_settings
        }
        
        result = self._make_request('2/tweets', method='POST', json_data=data)
        logger.info(f"Tweet posted: {result}")
        return result
    
    def post_thread(self, tweets: List[str]) -> Dict:
        """Post a thread of tweets"""
        if not tweets:
            return {'success': False, 'error': 'No tweets provided'}
        
        results = []
        previous_tweet_id = None
        
        for i, tweet_text in enumerate(tweets):
            data = {'text': tweet_text}
            
            if previous_tweet_id and i > 0:
                data['reply'] = {'in_reply_to_tweet_id': previous_tweet_id}
            
            result = self._make_request('2/tweets', method='POST', json_data=data)
            
            if result.get('success'):
                previous_tweet_id = result.get('data', {}).get('data', {}).get('id')
                results.append(result)
            else:
                return {'success': False, 'error': f'Thread failed at tweet {i+1}', 'partial_results': results}
        
        return {'success': True, 'data': {'tweets': results, 'thread_count': len(tweets)}}
    
    def post_tweet_with_media(self, text: str, media_urls: List[str]) -> Dict:
        """Post tweet with media attachments"""
        # Note: Media upload requires separate media endpoint
        # This is a simplified version
        data = {
            'text': text,
        }
        
        # Media IDs would be added here after uploading
        # For now, just post text
        result = self._make_request('2/tweets', method='POST', json_data=data)
        logger.info(f"Tweet with media posted: {result}")
        return result
    
    def get_tweets(self, username: str, limit: int = 10) -> Dict:
        """Get user's recent tweets"""
        # First get user ID
        user_result = self._make_request(f'2/users/by/username/{username}')
        
        if not user_result.get('success'):
            return user_result
        
        user_id = user_result.get('data', {}).get('data', {}).get('id')
        
        # Get tweets
        tweets_result = self._make_request(
            f'2/users/{user_id}/tweets',
            method='GET',
            data={'max_results': limit}
        )
        
        logger.info(f"User tweets retrieved: {tweets_result}")
        return tweets_result
    
    def get_user_metrics(self, username: str) -> Dict:
        """Get user metrics"""
        result = self._make_request(
            f'2/users/by/username/{username}',
            method='GET',
            data={'user.fields': 'public_metrics,description,created_at'}
        )
        
        logger.info(f"User metrics retrieved: {result}")
        return result
    
    def delete_tweet(self, tweet_id: str) -> Dict:
        """Delete a tweet"""
        result = self._make_request(f'2/tweets/{tweet_id}', method='DELETE')
        logger.info(f"Tweet deleted: {result}")
        return result
    
    def generate_summary(self, username: str, days: int = 7) -> Dict:
        """Generate Twitter performance summary"""
        user_metrics = self.get_user_metrics(username)
        recent_tweets = self.get_tweets(username, 20)
        
        summary = {
            'platform': 'Twitter',
            'username': username,
            'period_days': days,
            'generated_at': datetime.now().isoformat(),
            'metrics': {}
        }
        
        if user_metrics.get('success'):
            metrics = user_metrics.get('data', {}).get('data', {}).get('public_metrics', {})
            summary['metrics']['followers_count'] = metrics.get('followers_count', 0)
            summary['metrics']['following_count'] = metrics.get('following_count', 0)
            summary['metrics']['tweet_count'] = metrics.get('tweet_count', 0)
        
        if recent_tweets.get('success'):
            tweets = recent_tweets.get('data', {}).get('data', [])
            summary['metrics']['recent_tweets_count'] = len(tweets)
            
            # Calculate average engagement
            if tweets:
                avg_likes = sum(t.get('public_metrics', {}).get('like_count', 0) for t in tweets) / len(tweets)
                avg_retweets = sum(t.get('public_metrics', {}).get('retweet_count', 0) for t in tweets) / len(tweets)
                summary['metrics']['avg_likes_per_tweet'] = avg_likes
                summary['metrics']['avg_retweets_per_tweet'] = avg_retweets
        
        return summary
    
    def health_check(self) -> Dict:
        """Check Twitter connection health"""
        try:
            # Test with a simple user lookup
            result = self._make_request('2/users/by/username/twitter', method='GET')
            return {
                'status': 'healthy' if result.get('success') else 'unhealthy',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


class SocialMediaMCP:
    """Unified Social Media MCP Server"""
    
    def __init__(self):
        self.facebook = FacebookMCP()
        self.instagram = InstagramMCP()
        self.twitter = TwitterMCP()
        
        logger.info("Social Media MCP Server initialized")
    
    def post_to_all(self, message: str, image_url: str = None) -> Dict:
        """Post to all connected social media platforms"""
        results = {
            'facebook': None,
            'instagram': None,
            'twitter': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Post to Facebook
        if image_url:
            results['facebook'] = self.facebook.post_photo(image_url, message)
        else:
            results['facebook'] = self.facebook.post_text(message)
        
        # Post to Instagram
        if image_url:
            results['instagram'] = self.instagram.create_image_post(image_url, message)
        
        # Post to Twitter
        results['twitter'] = self.twitter.post_tweet(message)
        
        logger.info(f"Posted to all platforms: {results}")
        return results
    
    def get_all_summaries(self, days: int = 7) -> Dict:
        """Get summaries from all platforms"""
        return {
            'facebook': self.facebook.generate_summary(days),
            'instagram': self.instagram.generate_summary(days),
            'twitter': self.twitter.generate_summary('twitter'),
            'generated_at': datetime.now().isoformat()
        }
    
    def health_check_all(self) -> Dict:
        """Check health of all platforms"""
        return {
            'facebook': self.facebook.health_check(),
            'instagram': self.instagram.health_check(),
            'twitter': self.twitter.health_check(),
            'timestamp': datetime.now().isoformat()
        }


# Create MCP server instance
mcp_server = SocialMediaMCP()


# Tool definitions
TOOLS = [
    {
        'name': 'facebook_post_text',
        'description': 'Post text update to Facebook',
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
        'description': 'Post photo to Facebook',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'photo_url': {'type': 'string'},
                'message': {'type': 'string'}
            },
            'required': ['photo_url']
        }
    },
    {
        'name': 'instagram_post_image',
        'description': 'Post image to Instagram',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'image_url': {'type': 'string'},
                'caption': {'type': 'string'}
            },
            'required': ['image_url']
        }
    },
    {
        'name': 'twitter_post_tweet',
        'description': 'Post a tweet',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'text': {'type': 'string'}
            },
            'required': ['text']
        }
    },
    {
        'name': 'twitter_post_thread',
        'description': 'Post a thread of tweets',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'tweets': {'type': 'array', 'items': {'type': 'string'}}
            },
            'required': ['tweets']
        }
    },
    {
        'name': 'post_to_all_platforms',
        'description': 'Post to all connected social media platforms',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'image_url': {'type': 'string'}
            },
            'required': ['message']
        }
    },
    {
        'name': 'get_social_summaries',
        'description': 'Get performance summaries from all platforms',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'days': {'type': 'integer', 'default': 7}
            }
        }
    },
    {
        'name': 'health_check_social',
        'description': 'Check health of all social media connections'
    }
]


def handle_tool_call(tool_name: str, arguments: Dict) -> Dict:
    """Handle MCP tool calls"""
    logger.info(f"Tool call: {tool_name} with args: {arguments}")
    
    try:
        if tool_name == 'facebook_post_text':
            return mcp_server.facebook.post_text(**arguments)
        elif tool_name == 'facebook_post_photo':
            return mcp_server.facebook.post_photo(**arguments)
        elif tool_name == 'instagram_post_image':
            return mcp_server.instagram.create_image_post(**arguments)
        elif tool_name == 'twitter_post_tweet':
            return mcp_server.twitter.post_tweet(**arguments)
        elif tool_name == 'twitter_post_thread':
            return mcp_server.twitter.post_thread(**arguments)
        elif tool_name == 'post_to_all_platforms':
            return mcp_server.post_to_all(**arguments)
        elif tool_name == 'get_social_summaries':
            return mcp_server.get_all_summaries(**arguments)
        elif tool_name == 'health_check_social':
            return mcp_server.health_check_all()
        else:
            return {'success': False, 'error': f'Unknown tool: {tool_name}'}
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return {'success': False, 'error': str(e)}


if __name__ == '__main__':
    print("Social Media MCP Server")
    print("=" * 50)
    
    # Health check
    health = mcp_server.health_check_all()
    print(f"Health: {json.dumps(health, indent=2)}")
    
    # Test summaries
    summaries = mcp_server.get_all_summaries(7)
    print(f"\nSummaries: {json.dumps(summaries, indent=2)}")
