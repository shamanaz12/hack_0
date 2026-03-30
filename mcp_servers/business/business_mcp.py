"""
Business MCP Server
Gold Tier - Odoo & Accounting Integration

Integrates:
- Odoo Community (JSON-RPC API)
- Accounting operations
- Invoice generation
- Financial reports

Features:
- Create invoices
- Read accounting data
- Generate financial reports
- Customer management
- CEO briefing generation

Usage:
  python business_mcp.py --health
  python business_mcp.py --create-invoice
  python business_mcp.py --generate-report
  python business_mcp.py --ceo-briefing
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'odoo')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'admin')

# MCP Server Info
SERVER_INFO = {
    'name': 'Business MCP',
    'version': '1.0.0',
    'description': 'Odoo & Accounting Integration',
    'modules': ['Odoo', 'Accounting', 'Invoicing', 'Reports'],
    'features': [
        'create_invoice',
        'read_invoices',
        'generate_financial_report',
        'create_ceo_briefing',
        'customer_management'
    ]
}


class BusinessMCP:
    """Business & Accounting Server"""

    def __init__(self):
        self.api_key = DASHSCOPE_API_KEY
        self.odoo_url = ODOO_URL.rstrip('/')
        self.odoo_db = ODOO_DB
        self.odoo_username = ODOO_USERNAME
        self.odoo_password = ODOO_PASSWORD
        self.use_ai = bool(self.api_key)
        self.uid = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Odoo"""
        try:
            endpoint = f"{self.odoo_url}/web/session/authenticate"
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "db": self.odoo_db,
                    "login": self.odoo_username,
                    "password": self.odoo_password
                }
            }
            
            response = requests.post(endpoint, json=payload, timeout=10)
            result = response.json()

            if result.get('result', {}).get('uid'):
                self.uid = result['result']['uid']
                print(f"  [OK] Odoo authenticated (UID: {self.uid})")
            else:
                print(f"  [WARN] Odoo authentication failed")
        except Exception as e:
            print(f"  [WARN] Odoo connection error: {e}")

    def ai_generate_briefing(self, data: dict) -> str:
        """Generate CEO briefing using Qwen AI"""
        if not self.use_ai:
            return self._generate_simple_briefing(data)
        
        try:
            from dashscope import Generation
            
            prompt = f"""Generate a CEO briefing report from this business data:

{json.dumps(data, indent=2)}

Include:
1. Executive Summary
2. Key Highlights
3. Areas of Concern
4. Recommendations

Keep it concise and professional."""

            response = Generation.call(
                model='qwen-plus',
                api_key=self.api_key,
                prompt=prompt,
                max_tokens=500
            )
            
            if response.status_code == 200:
                return response.output.text.strip()
            return self._generate_simple_briefing(data)
        except:
            return self._generate_simple_briefing(data)

    def _generate_simple_briefing(self, data: dict) -> str:
        """Simple briefing without AI"""
        briefing = "CEO BRIEFING REPORT\n"
        briefing += "=" * 60 + "\n\n"
        briefing += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if 'invoices' in data:
            briefing += f"Total Invoices: {len(data['invoices'])}\n"
        
        if 'revenue' in data:
            briefing += f"Revenue: ${data['revenue']}\n"
        
        briefing += "\n" + "=" * 60
        return briefing

    def create_invoice(self, customer_name: str, amount: float, 
                       items: list = None) -> dict:
        """Create invoice in Odoo"""
        print(f"  Creating invoice for {customer_name}...")
        print(f"  Amount: ${amount}")
        
        if not self.uid:
            # Log for later processing
            return self._queue_invoice(customer_name, amount, items)
        
        try:
            # Create invoice via Odoo API
            endpoint = f"{self.odoo_url}/web/dataset/call_kw"
            
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': self._get_or_create_partner(customer_name),
                'invoice_line_ids': []
            }
            
            if items:
                for item in items:
                    invoice_vals['invoice_line_ids'].append((0, 0, {
                        'name': item.get('name', 'Product'),
                        'quantity': item.get('quantity', 1),
                        'price_unit': item.get('price', 0)
                    }))
            
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": "account.move",
                    "method": "create",
                    "args": [invoice_vals]
                }
            }
            
            response = requests.post(endpoint, json=payload, timeout=10)
            result = response.json()
            
            if 'result' in result:
                invoice_id = result['result']
                print(f"  ✅ Invoice created: {invoice_id}")
                return {
                    'success': True,
                    'invoice_id': invoice_id,
                    'status': 'created'
                }
            else:
                return self._queue_invoice(customer_name, amount, items)
                
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            return self._queue_invoice(customer_name, amount, items)

    def _get_or_create_partner(self, name: str) -> int:
        """Get or create partner in Odoo"""
        # Simplified - in production would search/create partner
        return 1  # Default partner

    def _queue_invoice(self, customer_name: str, amount: float, 
                       items: list = None) -> dict:
        """Queue invoice for later processing"""
        log_file = Path('logs/pending_invoices.json')
        log_file.parent.mkdir(exist_ok=True)
        
        invoices = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                invoices = json.load(f)
        
        invoices.append({
            'customer': customer_name,
            'amount': amount,
            'items': items or [],
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        })
        
        with open(log_file, 'w') as f:
            json.dump(invoices, f, indent=2)
        
        print(f"  ✅ Invoice queued!")
        return {
            'success': True,
            'invoice_id': f'inv_{datetime.now().timestamp()}',
            'status': 'queued'
        }

    def read_invoices(self, limit: int = 10) -> list:
        """Read recent invoices"""
        print(f"  Reading recent invoices...")
        
        invoices = []
        
        # Read from Odoo
        if self.uid:
            try:
                endpoint = f"{self.odoo_url}/web/dataset/call_kw"
                payload = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "model": "account.move",
                        "method": "search_read",
                        "kwargs": {
                            "domain": [('move_type', '=', 'out_invoice')],
                            "limit": limit
                        }
                    }
                }
                
                response = requests.post(endpoint, json=payload, timeout=10)
                result = response.json()
                
                if 'result' in result:
                    invoices = result['result']
            except:
                pass
        
        # Also read pending invoices
        log_file = Path('logs/pending_invoices.json')
        if log_file.exists():
            with open(log_file, 'r') as f:
                pending = json.load(f)
                invoices.extend(pending[-5:])
        
        print(f"  ✅ Found {len(invoices)} invoices")
        return invoices

    def generate_financial_report(self, period_days: int = 30) -> dict:
        """Generate financial report"""
        print(f"  Generating {period_days}-day financial report...")
        
        report = {
            'type': 'financial_report',
            'period_days': period_days,
            'generated_at': datetime.now().isoformat(),
            'summary': {}
        }
        
        # Get invoices
        invoices = self.read_invoices(100)
        
        # Calculate totals
        total_amount = sum(inv.get('amount', 0) for inv in invoices if isinstance(inv, dict))
        pending_count = len([inv for inv in invoices if isinstance(inv, dict) and inv.get('status') == 'pending'])
        
        report['summary'] = {
            'total_invoices': len(invoices),
            'total_amount': total_amount,
            'pending_invoices': pending_count,
            'period': f"Last {period_days} days"
        }
        
        print(f"  ✅ Report generated!")
        return report

    def generate_ceo_briefing(self) -> dict:
        """Generate CEO briefing report"""
        print(f"  Generating CEO briefing...")
        
        # Collect data
        data = {
            'invoices': self.read_invoices(50),
            'report': self.generate_financial_report(30),
            'generated_at': datetime.now().isoformat()
        }
        
        # Generate briefing
        briefing_text = self.ai_generate_briefing(data)
        
        # Save briefing
        briefing_file = Path('reports/ceo_briefing.md')
        briefing_file.parent.mkdir(exist_ok=True)
        
        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write("# CEO Briefing Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("---\n\n")
            f.write(briefing_text)
        
        print(f"  ✅ CEO briefing saved to: {briefing_file}")
        
        return {
            'success': True,
            'briefing_file': str(briefing_file),
            'generated_at': datetime.now().isoformat()
        }

    def health_check(self) -> dict:
        """Check business server health"""
        status = {
            'server': 'Business MCP',
            'timestamp': datetime.now().isoformat(),
            'odoo': {
                'url': self.odoo_url,
                'connected': bool(self.uid),
                'database': self.odoo_db
            },
            'ai': 'enabled' if self.use_ai else 'disabled'
        }
        
        return status


# Global instance
business_mcp = BusinessMCP()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Business MCP Server')
    parser.add_argument('--health', action='store_true', help='Health check')
    parser.add_argument('--create-invoice', nargs=2, metavar=('CUSTOMER', 'AMOUNT'), help='Create invoice')
    parser.add_argument('--read-invoices', action='store_true', help='Read invoices')
    parser.add_argument('--report', type=int, help='Generate financial report')
    parser.add_argument('--ceo-briefing', action='store_true', help='Generate CEO briefing')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   BUSINESS MCP SERVER")
    print("=" * 60)
    
    if args.health:
        print("\nHealth Check:")
        health = business_mcp.health_check()
        print(json.dumps(health, indent=2))
    
    elif args.create_invoice:
        customer = args.create_invoice[0]
        amount = float(args.create_invoice[1])
        result = business_mcp.create_invoice(customer, amount)
        print(f"\nResult: {result}")
    
    elif args.read_invoices:
        invoices = business_mcp.read_invoices(10)
        print(f"\nFound {len(invoices)} invoices:")
        for inv in invoices:
            if isinstance(inv, dict):
                print(f"  - {inv.get('customer', 'Unknown')}: ${inv.get('amount', 0)}")
    
    elif args.report:
        report = business_mcp.generate_financial_report(args.report)
        print("\nFinancial Report:")
        print(json.dumps(report, indent=2))
    
    elif args.ceo_briefing:
        result = business_mcp.generate_ceo_briefing()
        print(f"\nResult: {result}")
    
    else:
        print("\nUsage:")
        print("  python business_mcp.py --health")
        print("  python business_mcp.py --create-invoice 'Customer' 1000")
        print("  python business_mcp.py --read-invoices")
        print("  python business_mcp.py --report 30")
        print("  python business_mcp.py --ceo-briefing")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
