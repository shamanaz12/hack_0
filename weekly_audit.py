#!/usr/bin/env python3
"""
Weekly Business Audit System
Generates comprehensive business reports including:
- Financial Summary (from Odoo)
- Social Media Performance (Facebook & Instagram)
- Email Communication Summary
- CEO Briefing Document

Run weekly to get complete business overview.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

# Try to import required libraries
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Installing required: pip install requests")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Installing dotenv: pip install python-dotenv")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/weekly_audit.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class BusinessMetrics:
    """Container for business metrics"""
    week_start: str
    week_end: str
    generated_at: str
    
    # Financial Metrics
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    total_invoices: int = 0
    pending_invoices: int = 0
    paid_invoices: int = 0
    
    # Facebook Metrics
    facebook_followers: int = 0
    facebook_posts: int = 0
    facebook_engagement: int = 0
    facebook_reach: int = 0
    
    # Instagram Metrics
    instagram_followers: int = 0
    instagram_posts: int = 0
    instagram_likes: int = 0
    instagram_comments: int = 0
    instagram_reach: int = 0
    
    # Email Metrics
    emails_received: int = 0
    emails_sent: int = 0
    emails_pending: int = 0
    
    # Summary
    overall_status: str = "unknown"
    key_highlights: List[str] = None
    action_items: List[str] = None
    
    def __post_init__(self):
        if self.key_highlights is None:
            self.key_highlights = []
        if self.action_items is None:
            self.action_items = []
    
    def to_dict(self) -> Dict:
        return asdict(self)


class WeeklyAuditSystem:
    """Weekly Business Audit System"""
    
    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else Path(__file__).parent
        self.logs_folder = self.vault_path / 'logs'
        self.reports_folder = self.vault_path / 'AI_Employee_Vault' / 'Reports'
        self.ceo_briefings_folder = self.vault_path / 'AI_Employee_Vault' / 'CEO_Briefings'
        
        # Create folders
        os.makedirs(self.logs_folder, exist_ok=True)
        os.makedirs(self.reports_folder, exist_ok=True)
        os.makedirs(self.ceo_briefings_folder, exist_ok=True)
        
        # Load configuration
        self.odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.odoo_db = os.getenv('ODOO_DB', 'odoo')
        self.odoo_username = os.getenv('ODOO_USERNAME', 'admin')
        self.odoo_password = os.getenv('ODOO_PASSWORD', 'admin')
        
        self.facebook_page_id = os.getenv('FACEBOOK_PAGE_ID', '')
        self.facebook_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN', '')
        
        self.instagram_id = os.getenv('INSTAGRAM_BUSINESS_ID', '')
        self.instagram_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        
        logger.info("Weekly Audit System initialized")
    
    def get_date_range(self) -> tuple:
        """Get last 7 days date range"""
        today = datetime.now()
        week_end = today
        week_start = today - timedelta(days=7)
        
        return week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')
    
    def fetch_odoo_data(self) -> Dict[str, Any]:
        """Fetch financial data from Odoo"""
        logger.info("Fetching data from Odoo...")
        
        odoo_data = {
            'revenue': 0.0,
            'expenses': 0.0,
            'total_invoices': 0,
            'pending_invoices': 0,
            'paid_invoices': 0
        }
        
        if not REQUESTS_AVAILABLE:
            logger.warning("Requests library not available, skipping Odoo")
            return odoo_data
        
        try:
            # Authenticate with Odoo
            auth_endpoint = f"{self.odoo_url}/web/session/authenticate"
            auth_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "db": self.odoo_db,
                    "login": self.odoo_username,
                    "password": self.odoo_password
                },
                "id": 1
            }
            
            auth_response = requests.post(auth_endpoint, json=auth_payload, timeout=30)
            auth_result = auth_response.json()
            
            if not auth_result.get("result", {}).get("uid"):
                logger.warning("Odoo authentication failed")
                return odoo_data
            
            # Fetch invoices
            week_start, week_end = self.get_date_range()
            
            invoice_endpoint = f"{self.odoo_url}/jsonrpc"
            invoice_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        self.odoo_db,
                        auth_result["result"]["uid"],
                        self.odoo_password,
                        "account.move",
                        "search_read",
                        [[
                            ("move_type", "in", ["out_invoice", "out_refund"]),
                            ("date", ">=", week_start),
                            ("date", "<=", week_end)
                        ]],
                        {"fields": ["id", "name", "state", "amount_total", "amount_residual", "date"]}
                    ]
                },
                "id": 2
            }
            
            invoice_response = requests.post(invoice_endpoint, json=invoice_payload, timeout=30)
            invoices = invoice_response.json().get("result", [])
            
            odoo_data['total_invoices'] = len(invoices)
            
            for invoice in invoices:
                amount = invoice.get('amount_total', 0)
                residual = invoice.get('amount_residual', 0)
                
                odoo_data['revenue'] += amount
                
                if residual == 0:
                    odoo_data['paid_invoices'] += 1
                else:
                    odoo_data['pending_invoices'] += 1
            
            logger.info(f"Odoo data fetched: {odoo_data['total_invoices']} invoices")
            
        except Exception as e:
            logger.error(f"Error fetching Odoo data: {e}")
        
        return odoo_data
    
    def fetch_facebook_data(self) -> Dict[str, Any]:
        """Fetch Facebook page metrics"""
        logger.info("Fetching Facebook data...")
        
        fb_data = {
            'followers': 0,
            'posts': 0,
            'engagement': 0,
            'reach': 0
        }
        
        if not self.facebook_page_id or not self.facebook_token:
            logger.warning("Facebook credentials not configured")
            return fb_data
        
        if not REQUESTS_AVAILABLE:
            return fb_data
        
        try:
            graph_url = f"https://graph.facebook.com/v18.0/{self.facebook_page_id}"
            
            # Get page info
            params = {
                'fields': 'followers_count,likes',
                'access_token': self.facebook_token
            }
            
            response = requests.get(graph_url, params=params, timeout=30)
            if response.status_code == 200:
                page_data = response.json()
                fb_data['followers'] = page_data.get('followers_count', 0)
                fb_data['likes'] = page_data.get('likes', 0)
            
            # Get posts count for the week
            week_start, _ = self.get_date_range()
            posts_params = {
                'fields': 'created_time,message,likes.summary(true),comments.summary(true),shares',
                'since': week_start,
                'access_token': self.facebook_token
            }
            
            posts_response = requests.get(f"{graph_url}/posts", params=posts_params, timeout=30)
            if posts_response.status_code == 200:
                posts_data = posts_response.json().get('data', [])
                fb_data['posts'] = len(posts_data)
                
                # Calculate engagement
                for post in posts_data:
                    likes = post.get('likes', {}).get('summary', {}).get('total_count', 0)
                    comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
                    shares = post.get('shares', {}).get('count', 0)
                    fb_data['engagement'] += likes + comments + shares
            
            logger.info(f"Facebook data fetched: {fb_data['followers']} followers, {fb_data['posts']} posts")
            
        except Exception as e:
            logger.error(f"Error fetching Facebook data: {e}")
        
        return fb_data
    
    def fetch_instagram_data(self) -> Dict[str, Any]:
        """Fetch Instagram business metrics"""
        logger.info("Fetching Instagram data...")
        
        ig_data = {
            'followers': 0,
            'posts': 0,
            'likes': 0,
            'comments': 0,
            'reach': 0
        }
        
        if not self.instagram_id or not self.instagram_token:
            logger.warning("Instagram credentials not configured")
            return ig_data
        
        if not REQUESTS_AVAILABLE:
            return ig_data
        
        try:
            graph_url = f"https://graph.facebook.com/v18.0/{self.instagram_id}"
            
            # Get account info
            params = {
                'fields': 'followers_count,media_count',
                'access_token': self.instagram_token
            }
            
            response = requests.get(graph_url, params=params, timeout=30)
            if response.status_code == 200:
                account_data = response.json()
                ig_data['followers'] = account_data.get('followers_count', 0)
                ig_data['posts'] = account_data.get('media_count', 0)
            
            # Get media with insights
            media_params = {
                'fields': 'like_count,comments_count',
                'limit': 50,
                'access_token': self.instagram_token
            }
            
            media_response = requests.get(f"{graph_url}/media", params=media_params, timeout=30)
            if media_response.status_code == 200:
                media_data = media_response.json().get('data', [])
                
                for media in media_data:
                    ig_data['likes'] += media.get('like_count', 0)
                    ig_data['comments'] += media.get('comments_count', 0)
            
            logger.info(f"Instagram data fetched: {ig_data['followers']} followers")
            
        except Exception as e:
            logger.error(f"Error fetching Instagram data: {e}")
        
        return ig_data
    
    def fetch_email_data(self) -> Dict[str, Any]:
        """Fetch email communication metrics"""
        logger.info("Fetching email data...")
        
        email_data = {
            'received': 0,
            'sent': 0,
            'pending': 0
        }
        
        # Check Gmail watcher logs
        gmail_log = self.vault_path / 'gmail_watcher.log'
        if gmail_log.exists():
            try:
                with open(gmail_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    email_data['received'] = len([l for l in lines if 'Processing email' in l])
            except Exception as e:
                logger.error(f"Error reading Gmail log: {e}")
        
        # Check MCP email status
        mcp_status = self.vault_path / 'mcp_email_status.json'
        if mcp_status.exists():
            try:
                with open(mcp_status, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                    email_data['sent'] = status.get('emails_sent', 0)
                    email_data['pending'] = status.get('emails_pending', 0)
            except Exception as e:
                logger.error(f"Error reading MCP email status: {e}")
        
        logger.info(f"Email data fetched: {email_data['received']} received, {email_data['sent']} sent")
        
        return email_data
    
    def generate_ceo_briefing(self, metrics: BusinessMetrics) -> str:
        """Generate CEO briefing document"""
        
        week_start, week_end = self.get_date_range()
        
        briefing = f"""# CEO Weekly Business Briefing

## Report Period: {week_start} to {week_end}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

**Overall Status:** {metrics.overall_status.upper()}

This week's performance shows:
- **Revenue:** ${metrics.total_revenue:,.2f}
- **Total Invoices:** {metrics.total_invoices} ({metrics.paid_invoices} paid, {metrics.pending_invoices} pending)
- **Facebook Followers:** {metrics.facebook_followers:,}
- **Instagram Followers:** {metrics.instagram_followers:,}
- **Emails Processed:** {metrics.emails_received} received, {metrics.emails_sent} sent

---

## Financial Performance

| Metric | Value |
|--------|-------|
| Total Revenue | ${metrics.total_revenue:,.2f} |
| Total Invoices | {metrics.total_invoices} |
| Paid Invoices | {metrics.paid_invoices} |
| Pending Invoices | {metrics.pending_invoices} |
| Collection Rate | {(metrics.paid_invoices/metrics.total_invoices*100) if metrics.total_invoices > 0 else 0:.1f}% |

---

## Social Media Performance

### Facebook
| Metric | Value |
|--------|-------|
| Followers | {metrics.facebook_followers:,} |
| Posts This Week | {metrics.facebook_posts} |
| Total Engagement | {metrics.facebook_engagement:,} |
| Reach | {metrics.facebook_reach:,} |

### Instagram
| Metric | Value |
|--------|-------|
| Followers | {metrics.instagram_followers:,} |
| Total Posts | {metrics.instagram_posts} |
| Total Likes | {metrics.instagram_likes:,} |
| Total Comments | {metrics.instagram_comments:,} |
| Reach | {metrics.instagram_reach:,} |

---

## Communication Summary

| Channel | Count |
|---------|-------|
| Emails Received | {metrics.emails_received} |
| Emails Sent | {metrics.emails_sent} |
| Pending Responses | {metrics.emails_pending} |

---

## Key Highlights

"""
        
        for i, highlight in enumerate(metrics.key_highlights, 1):
            briefing += f"{i}. {highlight}\n"
        
        if not metrics.key_highlights:
            briefing += "- No key highlights recorded this week\n"
        
        briefing += """
## Action Items

"""
        
        for i, item in enumerate(metrics.action_items, 1):
            briefing += f"{i}. {item}\n"
        
        if not metrics.action_items:
            briefing += "- No action items identified\n"
        
        briefing += """
---

## Recommendations

Based on this week's performance:

1. **Financial:** """ + ("Focus on collecting pending invoices." if metrics.pending_invoices > 0 else "Maintain current collection practices.") + """

2. **Social Media:** """ + ("Increase posting frequency for better engagement." if metrics.facebook_posts + metrics.instagram_posts < 5 else "Continue current content strategy.") + """

3. **Communication:** """ + ("Reduce response time for pending emails." if metrics.emails_pending > 5 else "Maintain current response times.") + """

---

*This report was automatically generated by the AI Employee Vault Weekly Audit System.*
"""
        
        return briefing
    
    def run_audit(self) -> BusinessMetrics:
        """Run complete weekly audit"""
        logger.info("=" * 60)
        logger.info("Starting Weekly Business Audit")
        logger.info("=" * 60)
        
        week_start, week_end = self.get_date_range()
        
        metrics = BusinessMetrics(
            week_start=week_start,
            week_end=week_end,
            generated_at=datetime.now().isoformat()
        )
        
        # Fetch Odoo data
        odoo_data = self.fetch_odoo_data()
        metrics.total_revenue = odoo_data['revenue']
        metrics.total_invoices = odoo_data['total_invoices']
        metrics.paid_invoices = odoo_data['paid_invoices']
        metrics.pending_invoices = odoo_data['pending_invoices']
        
        # Fetch Facebook data
        fb_data = self.fetch_facebook_data()
        metrics.facebook_followers = fb_data['followers']
        metrics.facebook_posts = fb_data['posts']
        metrics.facebook_engagement = fb_data['engagement']
        metrics.facebook_reach = fb_data['reach']
        
        # Fetch Instagram data
        ig_data = self.fetch_instagram_data()
        metrics.instagram_followers = ig_data['followers']
        metrics.instagram_posts = ig_data['posts']
        metrics.instagram_likes = ig_data['likes']
        metrics.instagram_comments = ig_data['comments']
        metrics.instagram_reach = ig_data['reach']
        
        # Fetch email data
        email_data = self.fetch_email_data()
        metrics.emails_received = email_data['received']
        metrics.emails_sent = email_data['sent']
        metrics.emails_pending = email_data['pending']
        
        # Determine overall status
        if metrics.total_revenue > 0 and metrics.paid_invoices > metrics.pending_invoices:
            metrics.overall_status = "excellent"
        elif metrics.total_revenue > 0:
            metrics.overall_status = "good"
        elif metrics.pending_invoices > metrics.paid_invoices:
            metrics.overall_status = "needs_attention"
        else:
            metrics.overall_status = "normal"
        
        # Generate key highlights
        if metrics.total_revenue > 0:
            metrics.key_highlights.append(f"Generated ${metrics.total_revenue:,.2f} in revenue")
        if metrics.facebook_followers > 0:
            metrics.key_highlights.append(f"Facebook community grew to {metrics.facebook_followers:,} followers")
        if metrics.instagram_followers > 0:
            metrics.key_highlights.append(f"Instagram reached {metrics.instagram_followers:,} followers")
        
        # Generate action items
        if metrics.pending_invoices > 0:
            metrics.action_items.append(f"Follow up on {metrics.pending_invoices} pending invoices")
        if metrics.emails_pending > 0:
            metrics.action_items.append(f"Respond to {metrics.emails_pending} pending emails")
        if metrics.facebook_posts < 3:
            metrics.action_items.append("Increase Facebook posting frequency")
        
        # Save metrics
        metrics_file = self.reports_folder / f"weekly_audit_{week_start}_{week_end}.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics.to_dict(), f, indent=2)
        
        # Generate CEO briefing
        briefing = self.generate_ceo_briefing(metrics)
        briefing_file = self.ceo_briefings_folder / f"ceo_briefing_{week_start}_{week_end}.md"
        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write(briefing)
        
        logger.info(f"Weekly audit completed!")
        logger.info(f"Metrics saved to: {metrics_file}")
        logger.info(f"CEO briefing saved to: {briefing_file}")
        logger.info("=" * 60)
        
        return metrics


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Weekly Business Audit System')
    parser.add_argument('--vault', type=str, help='Path to vault folder')
    parser.add_argument('--output', type=str, help='Output folder for reports')
    args = parser.parse_args()
    
    audit = WeeklyAuditSystem(vault_path=args.vault)
    metrics = audit.run_audit()
    
    print("\n" + "=" * 60)
    print("Weekly Audit Summary")
    print("=" * 60)
    print(f"Period: {metrics.week_start} to {metrics.week_end}")
    print(f"Status: {metrics.overall_status.upper()}")
    print(f"Revenue: ${metrics.total_revenue:,.2f}")
    print(f"Invoices: {metrics.total_invoices} ({metrics.paid_invoices} paid)")
    print(f"Facebook Followers: {metrics.facebook_followers:,}")
    print(f"Instagram Followers: {metrics.instagram_followers:,}")
    print(f"Emails: {metrics.emails_received} received, {metrics.emails_sent} sent")
    print("=" * 60)


if __name__ == '__main__':
    main()
