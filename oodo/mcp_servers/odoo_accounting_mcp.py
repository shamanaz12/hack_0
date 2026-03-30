"""
Odoo Accounting MCP Server
Handles all accounting operations without Graph API
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv('odoo_mcp.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/odoo_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OdooAccountingMCP:
    """Odoo Accounting MCP Server for business operations"""
    
    def __init__(self):
        self.odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.odoo_db = os.getenv('ODOO_DB', 'odoo')
        self.odoo_username = os.getenv('ODOO_USERNAME', 'admin')
        self.odoo_password = os.getenv('ODOO_PASSWORD', 'admin')
        self.api_key = os.getenv('ODOO_API_KEY', '')
        
        self.session = requests.Session()
        self.auth = HTTPBasicAuth(self.odoo_username, self.odoo_password)
        
        logger.info(f"Odoo MCP initialized: {self.odoo_url}")
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Odoo API"""
        url = f"{self.odoo_url}/{endpoint}"
        
        try:
            if method == 'GET':
                response = self.session.get(url, auth=self.auth, params=data)
            elif method == 'POST':
                response = self.session.post(url, auth=self.auth, json=data)
            elif method == 'PUT':
                response = self.session.put(url, auth=self.auth, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Odoo API error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Invoice Operations
    def create_invoice(self, partner_id: int, lines: List[Dict], invoice_type: str = 'out_invoice') -> Dict:
        """Create a new invoice in Odoo"""
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'account.move',
                'method': 'create',
                'args': [{
                    'move_type': invoice_type,
                    'partner_id': partner_id,
                    'invoice_line_ids': [
                        (0, 0, {
                            'name': line.get('name', 'Product'),
                            'quantity': line.get('quantity', 1),
                            'price_unit': line.get('price_unit', 0),
                            'account_id': line.get('account_id', None)
                        })
                        for line in lines
                    ],
                    'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                    'invoice_date_due': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                }]
            }
        }
        
        result = self._make_request('jsonrpc', method='POST', data=data)
        logger.info(f"Invoice created: {result}")
        return result
    
    def get_invoices(self, limit: int = 10, offset: int = 0) -> Dict:
        """Get list of invoices"""
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'account.move',
                'method': 'search_read',
                'args': [[('move_type', 'in', ['out_invoice', 'in_invoice'])]],
                'kwargs': {
                    'fields': ['name', 'partner_id', 'amount_total', 'amount_due', 'state', 'invoice_date'],
                    'limit': limit,
                    'offset': offset,
                    'order': 'invoice_date desc'
                }
            }
        }
        
        return self._make_request('jsonrpc', method='POST', data=data)
    
    def confirm_invoice(self, invoice_id: int) -> Dict:
        """Confirm an invoice"""
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'account.move',
                'method': 'action_post',
                'args': [[invoice_id]]
            }
        }
        
        return self._make_request('jsonrpc', method='POST', data=data)
    
    def register_payment(self, invoice_id: int, amount: float, payment_method: str = 'manual') -> Dict:
        """Register payment for an invoice"""
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'account.move',
                'method': 'action_register_payment',
                'args': [[invoice_id]],
                'kwargs': {
                    'amount': amount,
                    'payment_method': payment_method
                }
            }
        }
        
        return self._make_request('jsonrpc', method='POST', data=data)
    
    # Customer Operations
    def get_customers(self, limit: int = 50) -> Dict:
        """Get list of customers"""
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'res.partner',
                'method': 'search_read',
                'args': [[('customer', '=', True)]],
                'kwargs': {
                    'fields': ['name', 'email', 'phone', 'street', 'city', 'country_id'],
                    'limit': limit
                }
            }
        }
        
        return self._make_request('jsonrpc', method='POST', data=data)
    
    def create_customer(self, name: str, email: str = '', phone: str = '', address: Dict = None) -> Dict:
        """Create a new customer"""
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'res.partner',
                'method': 'create',
                'args': [{
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'customer': True,
                    'street': address.get('street', '') if address else '',
                    'city': address.get('city', '') if address else '',
                    'country_id': address.get('country_id', None) if address else None
                }]
            }
        }
        
        return self._make_request('jsonrpc', method='POST', data=data)
    
    # Product Operations
    def get_products(self, limit: int = 50) -> Dict:
        """Get list of products"""
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'product.template',
                'method': 'search_read',
                'args': [[('sale_ok', '=', True)]],
                'kwargs': {
                    'fields': ['name', 'list_price', 'standard_price', 'qty_available'],
                    'limit': limit
                }
            }
        }
        
        return self._make_request('jsonrpc', method='POST', data=data)
    
    def update_inventory(self, product_id: int, quantity: int) -> Dict:
        """Update product inventory"""
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'product.template',
                'method': 'write',
                'args': [[product_id], {'qty_available': quantity}]
            }
        }
        
        return self._make_request('jsonrpc', method='POST', data=data)
    
    # Financial Reports
    def get_financial_summary(self, period: str = 'month') -> Dict:
        """Get financial summary for the period"""
        today = datetime.now()
        
        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        elif period == 'quarter':
            start_date = today - timedelta(days=90)
        elif period == 'year':
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=30)
        
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'account.move',
                'method': 'search_read',
                'args': [[
                    ('move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('state', 'in', ['posted', 'paid']),
                    ('invoice_date', '>=', start_date.strftime('%Y-%m-%d'))
                ]],
                'kwargs': {
                    'fields': ['name', 'amount_total', 'amount_due', 'state', 'invoice_date']
                }
            }
        }
        
        result = self._make_request('jsonrpc', method='POST', data=data)
        
        if result.get('success'):
            invoices = result.get('data', [])
            total_revenue = sum(inv.get('amount_total', 0) for inv in invoices if inv.get('move_type') == 'out_invoice')
            total_expenses = sum(inv.get('amount_total', 0) for inv in invoices if inv.get('move_type') == 'in_invoice')
            
            result['summary'] = {
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'net_profit': total_revenue - total_expenses,
                'invoice_count': len(invoices),
                'period': period,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': today.strftime('%Y-%m-%d')
            }
        
        return result
    
    def get_accounts_receivable(self) -> Dict:
        """Get accounts receivable summary"""
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'account.move',
                'method': 'search_read',
                'args': [[
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('payment_state', '!=', 'paid')
                ]],
                'kwargs': {
                    'fields': ['name', 'partner_id', 'amount_total', 'amount_due', 'invoice_date', 'invoice_date_due']
                }
            }
        }
        
        return self._make_request('jsonrpc', method='POST', data=data)
    
    def get_accounts_payable(self) -> Dict:
        """Get accounts payable summary"""
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'account.move',
                'method': 'search_read',
                'args': [[
                    ('move_type', '=', 'in_invoice'),
                    ('state', '=', 'posted'),
                    ('payment_state', '!=', 'paid')
                ]],
                'kwargs': {
                    'fields': ['name', 'partner_id', 'amount_total', 'amount_due', 'invoice_date', 'invoice_date_due']
                }
            }
        }
        
        return self._make_request('jsonrpc', method='POST', data=data)
    
    # Subscription Operations
    def get_subscriptions(self) -> Dict:
        """Get all subscriptions"""
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'sale.subscription',
                'method': 'search_read',
                'args': [[]],
                'kwargs': {
                    'fields': ['name', 'partner_id', 'recurring_total', 'stage_id', 'next_invoice_date']
                }
            }
        }
        
        return self._make_request('jsonrpc', method='POST', data=data)
    
    # Health Check
    def health_check(self) -> Dict:
        """Check Odoo connection health"""
        try:
            result = self._make_request('web/session/modules')
            return {
                'status': 'healthy' if result.get('success') else 'unhealthy',
                'odoo_url': self.odoo_url,
                'database': self.odoo_db,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# MCP Server instance
mcp_server = OdooAccountingMCP()


# Tool definitions for MCP
TOOLS = [
    {
        'name': 'create_invoice',
        'description': 'Create a new invoice in Odoo',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'partner_id': {'type': 'integer', 'description': 'Customer ID'},
                'lines': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'quantity': {'type': 'number'},
                            'price_unit': {'type': 'number'}
                        }
                    }
                },
                'invoice_type': {'type': 'string', 'default': 'out_invoice'}
            },
            'required': ['partner_id', 'lines']
        }
    },
    {
        'name': 'get_invoices',
        'description': 'Get list of invoices',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'limit': {'type': 'integer', 'default': 10},
                'offset': {'type': 'integer', 'default': 0}
            }
        }
    },
    {
        'name': 'confirm_invoice',
        'description': 'Confirm an invoice',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'invoice_id': {'type': 'integer'}
            },
            'required': ['invoice_id']
        }
    },
    {
        'name': 'register_payment',
        'description': 'Register payment for an invoice',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'invoice_id': {'type': 'integer'},
                'amount': {'type': 'number'},
                'payment_method': {'type': 'string', 'default': 'manual'}
            },
            'required': ['invoice_id', 'amount']
        }
    },
    {
        'name': 'get_customers',
        'description': 'Get list of customers',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'limit': {'type': 'integer', 'default': 50}
            }
        }
    },
    {
        'name': 'create_customer',
        'description': 'Create a new customer',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'email': {'type': 'string'},
                'phone': {'type': 'string'},
                'address': {'type': 'object'}
            },
            'required': ['name']
        }
    },
    {
        'name': 'get_products',
        'description': 'Get list of products',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'limit': {'type': 'integer', 'default': 50}
            }
        }
    },
    {
        'name': 'update_inventory',
        'description': 'Update product inventory',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'product_id': {'type': 'integer'},
                'quantity': {'type': 'integer'}
            },
            'required': ['product_id', 'quantity']
        }
    },
    {
        'name': 'get_financial_summary',
        'description': 'Get financial summary for a period',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'period': {'type': 'string', 'enum': ['week', 'month', 'quarter', 'year'], 'default': 'month'}
            }
        }
    },
    {
        'name': 'get_accounts_receivable',
        'description': 'Get accounts receivable summary'
    },
    {
        'name': 'get_accounts_payable',
        'description': 'Get accounts payable summary'
    },
    {
        'name': 'get_subscriptions',
        'description': 'Get all subscriptions'
    },
    {
        'name': 'health_check',
        'description': 'Check Odoo connection health'
    }
]


def handle_tool_call(tool_name: str, arguments: Dict) -> Dict:
    """Handle MCP tool calls"""
    logger.info(f"Tool call: {tool_name} with args: {arguments}")
    
    try:
        if tool_name == 'create_invoice':
            return mcp_server.create_invoice(**arguments)
        elif tool_name == 'get_invoices':
            return mcp_server.get_invoices(**arguments)
        elif tool_name == 'confirm_invoice':
            return mcp_server.confirm_invoice(**arguments)
        elif tool_name == 'register_payment':
            return mcp_server.register_payment(**arguments)
        elif tool_name == 'get_customers':
            return mcp_server.get_customers(**arguments)
        elif tool_name == 'create_customer':
            return mcp_server.create_customer(**arguments)
        elif tool_name == 'get_products':
            return mcp_server.get_products(**arguments)
        elif tool_name == 'update_inventory':
            return mcp_server.update_inventory(**arguments)
        elif tool_name == 'get_financial_summary':
            return mcp_server.get_financial_summary(**arguments)
        elif tool_name == 'get_accounts_receivable':
            return mcp_server.get_accounts_receivable()
        elif tool_name == 'get_accounts_payable':
            return mcp_server.get_accounts_payable()
        elif tool_name == 'get_subscriptions':
            return mcp_server.get_subscriptions()
        elif tool_name == 'health_check':
            return mcp_server.health_check()
        else:
            return {'success': False, 'error': f'Unknown tool: {tool_name}'}
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return {'success': False, 'error': str(e)}


if __name__ == '__main__':
    # Test the MCP server
    print("Odoo Accounting MCP Server")
    print("=" * 50)
    
    # Health check
    health = mcp_server.health_check()
    print(f"Health: {json.dumps(health, indent=2)}")
    
    # Test financial summary
    summary = mcp_server.get_financial_summary('month')
    print(f"\nFinancial Summary: {json.dumps(summary, indent=2)}")
