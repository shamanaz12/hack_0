"""
Facebook & Instagram MCP Web Server
Beautiful UI with Auto-Token Management
No manual token configuration needed!
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_servers.social_mcp_auto import (
    facebook_mcp, instagram_mcp, token_manager,
    FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_PAGE_ID
)

PORT = 8080


class MCPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_json(facebook_mcp.health_check())
        elif self.path == '/instagram/health':
            self.send_json(instagram_mcp.health_check())
        elif self.path.startswith('/facebook/posts'):
            self.send_json(facebook_mcp.get_posts(5))
        elif self.path == '/config':
            self.send_json({
                'facebook_app_id': FACEBOOK_APP_ID,
                'facebook_page_id': FACEBOOK_PAGE_ID,
                'has_app_secret': bool(FACEBOOK_APP_SECRET),
                'token_valid': token_manager.is_token_valid()
            })
        elif self.path == '/':
            self.send_html(self.get_dashboard())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/facebook/post':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode())
            result = facebook_mcp.create_post(data.get('message'), data.get('link'))
            self.send_json(result)
        elif self.path == '/facebook/photo':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode())
            result = facebook_mcp.post_photo(data.get('photo_url'), data.get('caption'))
            self.send_json(result)
        elif self.path == '/instagram/post':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode())
            result = instagram_mcp.create_post(data.get('image_url'), data.get('caption'))
            self.send_json(result)
        elif self.path == '/token/exchange':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode())
            short_token = data.get('token')
            if short_token:
                long_token = token_manager.exchange_long_lived_token(short_token)
                if long_token:
                    self.send_json({'success': True, 'message': 'Token refreshed (60 days)'})
                else:
                    self.send_json({'success': False, 'error': 'Token exchange failed'})
            else:
                self.send_json({'success': False, 'error': 'No token provided'})
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def get_dashboard(self):
        fb_health = facebook_mcp.health_check()
        ig_health = instagram_mcp.health_check()
        config = {
            'facebook_app_id': FACEBOOK_APP_ID,
            'facebook_page_id': FACEBOOK_PAGE_ID,
            'has_app_secret': bool(FACEBOOK_APP_SECRET),
            'token_valid': token_manager.is_token_valid()
        }
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Media MCP Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .card h2 {{
            color: #667eea;
            margin-bottom: 15px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .status {{
            display: inline-block;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-healthy, .status-mock_mode {{ background: #27ae60; color: white; }}
        .status-unhealthy, .status-error {{ background: #e74c3c; color: white; }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }}
        .info-item {{
            background: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .info-item label {{
            font-weight: bold;
            color: #555;
            display: block;
            margin-bottom: 5px;
            font-size: 0.85em;
        }}
        .info-item span {{ color: #333; font-size: 1em; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{
            display: block;
            font-weight: bold;
            color: #555;
            margin-bottom: 5px;
        }}
        .form-group input, .form-group textarea {{
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }}
        .form-group input:focus, .form-group textarea:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            margin: 5px;
        }}
        .btn:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }}
        .btn-success {{ background: #27ae60; }}
        .btn-success:hover {{ background: #219a52; }}
        .btn-facebook {{ background: #1877f2; }}
        .btn-facebook:hover {{ background: #166fe5; }}
        .btn-instagram {{ background: #e4405f; }}
        .btn-instagram:hover {{ background: #c13550; }}
        #result {{
            background: #1a1a1a;
            color: #00ff00;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
            white-space: pre-wrap;
            display: none;
            font-family: 'Courier New', monospace;
            max-height: 300px;
            overflow-y: auto;
        }}
        .posts-container {{ max-height: 400px; overflow-y: auto; }}
        .post {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }}
        .post-message {{ color: #333; margin-bottom: 8px; }}
        .post-meta {{ color: #888; font-size: 0.9em; }}
        .post-stats {{
            display: flex;
            gap: 15px;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
            font-size: 0.9em;
        }}
        .alert {{
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }}
        .alert-warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            color: #856404;
        }}
        .alert-success {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            color: #155724;
        }}
        .setup-steps {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 15px;
        }}
        .setup-steps ol {{
            margin-left: 20px;
            line-height: 2;
        }}
        .setup-steps code {{
            background: #e9ecef;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }}
        .tab-container {{ margin-bottom: 20px; }}
        .tab {{
            display: inline-block;
            padding: 10px 20px;
            background: #e9ecef;
            border: none;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            margin-right: 5px;
            font-weight: bold;
        }}
        .tab.active {{
            background: white;
            color: #667eea;
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📱 Social Media MCP Dashboard</h1>
        
        <!-- Setup Alert -->
        {self._get_setup_alert(config)}
        
        <!-- Status Cards -->
        <div class="grid">
            <!-- Facebook Status -->
            <div class="card">
                <h2>📘 Facebook</h2>
                <span class="status status-{fb_health.get('status')}">{fb_health.get('status')}</span>
                <div class="info-grid">
                    <div class="info-item">
                        <label>Page ID</label>
                        <span>{fb_health.get('page_id', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <label>Page Name</label>
                        <span>{fb_health.get('page_name', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <label>Token Valid</label>
                        <span>{"✅ Yes" if config['token_valid'] else "❌ No"}</span>
                    </div>
                </div>
                <button class="btn" onclick="testEndpoint('/health')">Refresh Status</button>
            </div>
            
            <!-- Instagram Status -->
            <div class="card">
                <h2>📸 Instagram</h2>
                <span class="status status-{ig_health.get('status')}">{ig_health.get('status')}</span>
                <div class="info-grid">
                    <div class="info-item">
                        <label>Business ID</label>
                        <span>{ig_health.get('business_id', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <label>Token Valid</label>
                        <span>{"✅ Yes" if ig_health.get('token_valid') else "❌ No"}</span>
                    </div>
                </div>
                <button class="btn" onclick="testEndpoint('/instagram/health')">Refresh Status</button>
            </div>
        </div>
        
        <!-- Tabs -->
        <div class="tab-container">
            <button class="tab active" onclick="switchTab('facebook')">Facebook</button>
            <button class="tab" onclick="switchTab('instagram')">Instagram</button>
            <button class="tab" onclick="switchTab('setup')">Setup Guide</button>
        </div>
        
        <!-- Facebook Tab -->
        <div id="facebook" class="tab-content active">
            <div class="grid">
                <!-- Create Post -->
                <div class="card">
                    <h2>📝 Create Facebook Post</h2>
                    <div class="form-group">
                        <label>Message</label>
                        <textarea id="fb-message" rows="4" placeholder="What's on your mind?"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Link (optional)</label>
                        <input type="text" id="fb-link" placeholder="https://example.com">
                    </div>
                    <button class="btn btn-facebook" onclick="createFacebookPost()">Post to Facebook</button>
                </div>
                
                <!-- Recent Posts -->
                <div class="card">
                    <h2>📰 Recent Posts</h2>
                    <div class="posts-container" id="fb-posts">Loading...</div>
                    <button class="btn" onclick="loadFacebookPosts()">Refresh Posts</button>
                </div>
            </div>
        </div>
        
        <!-- Instagram Tab -->
        <div id="instagram" class="tab-content">
            <div class="card">
                <h2>📝 Create Instagram Post</h2>
                <div class="form-group">
                    <label>Image URL</label>
                    <input type="text" id="ig-image" placeholder="https://example.com/image.jpg">
                </div>
                <div class="form-group">
                    <label>Caption</label>
                    <textarea id="ig-caption" rows="3" placeholder="Add a caption..."></textarea>
                </div>
                <button class="btn btn-instagram" onclick="createInstagramPost()">Post to Instagram</button>
            </div>
        </div>
        
        <!-- Setup Tab -->
        <div id="setup" class="tab-content">
            <div class="card">
                <h2>🔧 Setup Instructions</h2>
                {self._get_setup_guide()}
            </div>
        </div>
        
        <!-- Result Box -->
        <div id="result"></div>
    </div>
    
    <script>
        // Load initial data
        loadFacebookPosts();
        
        // Tab switching
        function switchTab(tabName) {{
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }}
        
        // Test endpoint
        async function testEndpoint(url) {{
            const result = document.getElementById('result');
            result.style.display = 'block';
            result.textContent = 'Loading...';
            try {{
                const res = await fetch(url);
                const data = await res.json();
                result.textContent = JSON.stringify(data, null, 2);
            }} catch(e) {{
                result.textContent = 'Error: ' + e.message;
            }}
        }}
        
        // Load Facebook posts
        async function loadFacebookPosts() {{
            const container = document.getElementById('fb-posts');
            try {{
                const res = await fetch('/facebook/posts');
                const data = await res.json();
                if(data.success && data.data && data.data.length > 0) {{
                    let html = '';
                    data.data.forEach(post => {{
                        const likes = post.likes?.summary?.total_count || 0;
                        const comments = post.comments?.summary?.total_count || 0;
                        html += `
                        <div class="post">
                            <div class="post-message">${{post.message || 'No message'}}</div>
                            <div class="post-meta">📅 ${{new Date(post.created_time).toLocaleString()}}</div>
                            <div class="post-stats">
                                <span>👍 ${{likes}} likes</span>
                                <span>💬 ${{comments}} comments</span>
                            </div>
                        </div>`;
                    }});
                    container.innerHTML = html;
                }} else {{
                    container.innerHTML = '<p>No posts found</p>';
                }}
            }} catch(e) {{
                container.innerHTML = '<p>Error loading posts</p>';
            }}
        }}
        
        // Create Facebook post
        async function createFacebookPost() {{
            const message = document.getElementById('fb-message').value;
            const link = document.getElementById('fb-link').value;
            const result = document.getElementById('result');
            
            if(!message) {{ alert('Please enter a message'); return; }}
            
            result.style.display = 'block';
            result.textContent = 'Creating post...';
            
            try {{
                const res = await fetch('/facebook/post', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{message, link}})
                }});
                const data = await res.json();
                result.textContent = JSON.stringify(data, null, 2);
                
                if(data.success) {{
                    document.getElementById('fb-message').value = '';
                    document.getElementById('fb-link').value = '';
                    setTimeout(() => loadFacebookPosts(), 2000);
                }}
            }} catch(e) {{
                result.textContent = 'Error: ' + e.message;
            }}
        }}
        
        // Create Instagram post
        async function createInstagramPost() {{
            const image_url = document.getElementById('ig-image').value;
            const caption = document.getElementById('ig-caption').value;
            const result = document.getElementById('result');
            
            if(!image_url) {{ alert('Please enter an image URL'); return; }}
            
            result.style.display = 'block';
            result.textContent = 'Creating post...';
            
            try {{
                const res = await fetch('/instagram/post', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{image_url, caption}})
                }});
                const data = await res.json();
                result.textContent = JSON.stringify(data, null, 2);
            }} catch(e) {{
                result.textContent = 'Error: ' + e.message;
            }}
        }}
    </script>
</body>
</html>'''
    
    def _get_setup_alert(self, config):
        if not config['token_valid']:
            return '''
            <div class="alert alert-warning">
                <strong>⚠️ Token Not Configured</strong> - Running in mock mode. 
                <button class="btn" onclick="switchTab('setup')" style="margin-left: 10px; padding: 5px 15px;">Setup Now</button>
            </div>
            '''
        return '''
        <div class="alert alert-success">
            <strong>✅ All Set!</strong> - Facebook and Instagram are configured and ready.
        </div>
        '''
    
    def _get_setup_guide(self):
        return f'''
        <div class="setup-steps">
            <h3>Quick Setup (5 minutes)</h3>
            <ol>
                <li><strong>Get Facebook App Credentials:</strong>
                    <ul>
                        <li>Go to <a href="https://developers.facebook.com" target="_blank">developers.facebook.com</a></li>
                        <li>Create a new app or select existing</li>
                        <li>Copy <strong>App ID</strong> and <strong>App Secret</strong></li>
                    </ul>
                </li>
                <li><strong>Get Page Access Token:</strong>
                    <ul>
                        <li>Go to <a href="https://developers.facebook.com/tools/explorer/" target="_blank">Graph API Explorer</a></li>
                        <li>Select your app</li>
                        <li>Click "Generate Access Token"</li>
                        <li>Select permissions: <code>pages_manage_posts</code>, <code>pages_read_engagement</code></li>
                        <li>Run query: <code>GET /me/accounts</code></li>
                        <li>Copy the <strong>access_token</strong> from response</li>
                    </ul>
                </li>
                <li><strong>Update .env file:</strong>
                    <pre style="background: #1a1a1a; color: #00ff00; padding: 15px; border-radius: 8px; overflow-x: auto;">
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_PAGE_ID=your_page_id_here
FACEBOOK_PAGE_ACCESS_TOKEN=your_access_token_here</pre>
                </li>
                <li><strong>Restart server and refresh this page</strong></li>
            </ol>
            <p style="margin-top: 20px;"><strong>Note:</strong> Token will auto-refresh for 60 days validity!</p>
        </div>
        '''
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")


if __name__ == '__main__':
    print("=" * 60)
    print("Social Media MCP Web Server")
    print("=" * 60)
    print(f"URL: http://localhost:{PORT}")
    print(f"Dashboard: http://localhost:{PORT}/")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        server = HTTPServer(("127.0.0.1", PORT), MCPHandler)
        print("Server started successfully!")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error: {e}")
