"""
Facebook & Instagram MCP Server - Localhost Dashboard
Opens both platforms in browser with auto-login
No tokens required - uses Playwright browser automation
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import threading

# Load environment
load_dotenv()

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'social_localhost.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SocialMediaServer:
    """Facebook & Instagram Browser Automation"""

    def __init__(self):
        self.facebook_email = os.getenv('FACEBOOK_EMAIL', 'naz sheikh')
        self.facebook_password = os.getenv('FACEBOOK_PASSWORD', 'uzain786')
        self.facebook_profile_id = os.getenv('FACEBOOK_PAGE_ID', '61578524116357')
        self.instagram_username = os.getenv('INSTAGRAM_USERNAME', 'shamaansari5576')
        self.instagram_password = os.getenv('INSTAGRAM_PASSWORD', '')
        
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
        self.fb_logged_in = False
        self.ig_logged_in = False

    def start_browser(self):
        """Start Playwright browser"""
        try:
            from playwright.sync_api import sync_playwright
            
            logger.info("Starting browser...")
            self.playwright = sync_playwright().start()
            
            self.browser = self.playwright.chromium.launch(
                headless=False,
                slow_mo=100,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--window-size=1920,1080'
                ]
            )
            
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            self.context.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
            
            self.page = self.context.new_page()
            logger.info("Browser started!")
            return True
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return False

    def open_facebook(self):
        """Open Facebook in browser"""
        if not self.page:
            self.start_browser()
        
        try:
            logger.info("Opening Facebook...")
            self.page.goto(f'https://www.facebook.com/profile.php?id={self.facebook_profile_id}', 
                          wait_until='networkidle', timeout=30000)
            
            # Check if login needed
            if 'login' in self.page.url.lower():
                logger.info("Login required - entering credentials...")
                self.page.fill('#email', self.facebook_email)
                time.sleep(1)
                self.page.fill('#pass', self.facebook_password)
                time.sleep(1)
                self.page.click('button[type="submit"]')
                time.sleep(5)
            
            self.fb_logged_in = True
            logger.info("Facebook opened successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Facebook error: {e}")
            return False

    def open_instagram(self):
        """Open Instagram in new tab"""
        if not self.page:
            self.start_browser()
        
        try:
            logger.info("Opening Instagram...")
            
            # Open new tab for Instagram
            ig_page = self.context.new_page()
            ig_page.goto(f'https://www.instagram.com/{self.instagram_username}/', 
                        wait_until='networkidle', timeout=30000)
            
            # Check if login needed
            if 'login' in ig_page.url.lower():
                logger.info("Instagram login required...")
                ig_page.fill('input[name="username"]', self.instagram_username)
                time.sleep(1)
                ig_page.fill('input[name="password"]', self.instagram_password)
                time.sleep(1)
                ig_page.click('button[type="submit"]')
                time.sleep(5)
            
            self.ig_logged_in = True
            logger.info("Instagram opened successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Instagram error: {e}")
            return False

    def open_both(self):
        """Open both Facebook and Instagram"""
        logger.info("=" * 60)
        logger.info("OPENING FACEBOOK & INSTAGRAM")
        logger.info("=" * 60)
        
        if not self.start_browser():
            return False
        
        # Open Facebook
        self.open_facebook()
        time.sleep(2)
        
        # Open Instagram in new tab
        self.open_instagram()
        
        logger.info("=" * 60)
        logger.info("BOTH PLATFORMS OPEN!")
        logger.info(f"Facebook: https://www.facebook.com/profile.php?id={self.facebook_profile_id}")
        logger.info(f"Instagram: https://www.instagram.com/{self.instagram_username}/")
        logger.info("=" * 60)
        
        return True

    def cleanup(self):
        """Cleanup"""
        try:
            if self.browser:
                time.sleep(5)  # Keep browser open for user
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Cleanup complete")
        except:
            pass


# Global instance
social_server = SocialMediaServer()


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP Server for localhost dashboard"""

    def do_GET(self):
        if self.path == '/':
            self.send_html(self.get_dashboard())
        elif self.path == '/facebook':
            self.send_json({'status': 'opening', 'platform': 'Facebook'})
            threading.Thread(target=social_server.open_facebook).start()
        elif self.path == '/instagram':
            self.send_json({'status': 'opening', 'platform': 'Instagram'})
            threading.Thread(target=social_server.open_instagram).start()
        elif self.path == '/both':
            self.send_json({'status': 'opening', 'platform': 'Both'})
            threading.Thread(target=social_server.open_both).start()
        elif self.path == '/health':
            self.send_json(social_server.get_status() if hasattr(social_server, 'get_status') else {'status': 'ready'})
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
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Media Dashboard - localhost</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .card h2 {{
            color: #667eea;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .btn {{
            display: inline-block;
            padding: 15px 30px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-size: 1.1em;
            font-weight: bold;
            transition: all 0.3s;
            margin: 10px 5px;
            border: none;
            cursor: pointer;
        }}
        .btn:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }}
        .btn-facebook {{ background: #1877f2; }}
        .btn-facebook:hover {{ background: #166fe5; }}
        .btn-instagram {{ background: #e4405f; }}
        .btn-instagram:hover {{ background: #c13550; }}
        .btn-both {{ background: linear-gradient(135deg, #1877f2, #e4405f); }}
        .info {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
        }}
        .info p {{
            margin: 5px 0;
            color: #555;
        }}
        .status {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .status-ready {{ background: #27ae60; color: white; }}
        .status-busy {{ background: #f39c12; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📱 Social Media Dashboard</h1>

        <div class="card">
            <h2>📘 Facebook</h2>
            <p>Profile ID: {social_server.facebook_profile_id}</p>
            <p>Email: {social_server.facebook_email}</p>
            <a href="/facebook" class="btn btn-facebook" onclick="openPlatform(event, '/facebook')">Open Facebook</a>
            <a href="https://www.facebook.com/profile.php?id={social_server.facebook_profile_id}" target="_blank" class="btn btn-facebook">Direct Link</a>
        </div>

        <div class="card">
            <h2>📸 Instagram</h2>
            <p>Username: @{social_server.instagram_username}</p>
            <a href="/instagram" class="btn btn-instagram" onclick="openPlatform(event, '/instagram')">Open Instagram</a>
            <a href="https://www.instagram.com/{social_server.instagram_username}/" target="_blank" class="btn btn-instagram">Direct Link</a>
        </div>

        <div class="card">
            <h2>🚀 Open Both</h2>
            <p>Open Facebook and Instagram together</p>
            <a href="/both" class="btn btn-both" onclick="openPlatform(event, '/both')">Open Both Platforms</a>
        </div>

        <div class="info">
            <h3>ℹ️ Information</h3>
            <p><strong>Server:</strong> http://localhost:8080</p>
            <p><strong>Mode:</strong> Browser Automation (Playwright)</p>
            <p><strong>Tokens:</strong> Not Required</p>
            <p><strong>Status:</strong> <span class="status status-ready">Ready</span></p>
        </div>
    </div>

    <script>
        async function openPlatform(event, url) {{
            event.preventDefault();
            try {{
                const res = await fetch(url);
                const data = await res.json();
                alert('Opening ' + data.platform + '...');
            }} catch(e) {{
                alert('Error: ' + e.message);
            }}
        }}
    </script>
</body>
</html>'''

    def log_message(self, format, *args):
        logger.info(f"{self.log_date_time_string()} - {args[0]}")


def run_server(port=8080):
    """Run HTTP server"""
    server = HTTPServer(('127.0.0.1', port), DashboardHandler)
    logger.info(f"Server starting on http://localhost:{port}")
    
    # Open browser automatically
    webbrowser.open(f'http://localhost:{port}')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")
        server.shutdown()


if __name__ == '__main__':
    print("=" * 60)
    print("SOCIAL MEDIA MCP SERVER - LOCALHOST")
    print("=" * 60)
    print()
    print("Configuration:")
    print(f"  Facebook Profile: {social_server.facebook_profile_id}")
    print(f"  Facebook Email: {social_server.facebook_email}")
    print(f"  Instagram: @{social_server.instagram_username}")
    print()
    print("=" * 60)
    print("Starting server on: http://localhost:8080")
    print("Dashboard will open in your browser...")
    print("=" * 60)
    print()
    
    # Run server
    run_server(8080)
