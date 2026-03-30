#!/usr/bin/env python3
"""
Odoo MCP Server - Provides tools to interact with Odoo via JSON-RPC.
Run in stdio mode for MCP communication.
"""

import json
import os
import sys
import logging
from typing import Any, Optional
import requests

# Configure logging for stderr (doesn't interfere with stdio MCP protocol)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Odoo configuration from environment variables
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")


class OdooJSONRPCClient:
    """Client for Odoo JSON-RPC API."""
    
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.uid: Optional[int] = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Odoo and get user ID."""
        endpoint = f"{self.url}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self.db,
                "login": self.username,
                "password": self.password
            },
            "id": 1
        }
        
        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if result.get("result", {}).get("uid"):
            self.uid = result["result"]["uid"]
            logger.info(f"Authenticated as user ID: {self.uid}")
        else:
            logger.error("Authentication failed")
            raise ValueError("Failed to authenticate with Odoo")
    
    def _execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute a method on an Odoo model."""
        endpoint = f"{self.url}/web/dataset/call"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": list(args),
                "kwargs": kwargs
            },
            "id": 2
        }
        
        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            error_msg = result["error"].get("message", "Unknown error")
            logger.error(f"Odoo error: {error_msg}")
            raise ValueError(error_msg)
        
        return result.get("result")
    
    def _execute_kw(self, model: str, method: str, args: list = None, kwargs: dict = None) -> Any:
        """Execute using execute_kw (more flexible for Odoo ORM)."""
        endpoint = f"{self.url}/jsonrpc"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [self.db, self.uid, self.password, model, method, args or []],
                "kwargs": kwargs or {}
            },
            "id": 3
        }
        
        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            error_msg = result["error"].get("message", "Unknown error")
            logger.error(f"Odoo error: {error_msg}")
            raise ValueError(error_msg)
        
        return result.get("result")


class OdooMCPHandler:
    """Handle MCP protocol messages for Odoo tools."""
    
    def __init__(self):
        self.odoo: Optional[OdooJSONRPCClient] = None
        self.connection_error: Optional[str] = None
        self._try_connect_odoo()
    
    def _try_connect_odoo(self) -> None:
        """Try to initialize Odoo connection (non-blocking)."""
        try:
            self.odoo = OdooJSONRPCClient(
                url=ODOO_URL,
                db=ODOO_DB,
                username=ODOO_USERNAME,
                password=ODOO_PASSWORD
            )
            logger.info(f"Connected to Odoo at {ODOO_URL}")
            self.connection_error = None
        except Exception as e:
            self.odoo = None
            self.connection_error = str(e)
            logger.warning(f"Odoo connection pending: {e}")
    
    def _check_connection(self) -> bool:
        """Check if Odoo is connected."""
        if self.odoo is None:
            return False
        return True
    
    def create_invoice(self, partner_id: int, amount: float, description: str) -> dict:
        """Create an invoice in Odoo."""
        if not self._check_connection():
            return {"success": False, "error": f"Odoo not connected: {self.connection_error}"}
        try:
            invoice_data = {
                "move_type": "out_invoice",
                "partner_id": partner_id,
                "invoice_line_ids": [[0, 0, {
                    "name": description,
                    "price_unit": amount,
                    "quantity": 1
                }]]
            }
            
            invoice_id = self.odoo._execute_kw(
                "account.move",
                "create",
                [invoice_data]
            )
            
            return {
                "success": True,
                "invoice_id": invoice_id,
                "message": f"Invoice {invoice_id} created successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_customer_orders(self, email: str) -> dict:
        """Get orders for a customer by email."""
        if not self._check_connection():
            return {"success": False, "error": f"Odoo not connected: {self.connection_error}"}
        try:
            # Find partner by email
            partner_ids = self.odoo._execute_kw(
                "res.partner",
                "search",
                [[["email", "=", email]]]
            )
            
            if not partner_ids:
                return {"success": False, "error": f"No customer found with email: {email}"}
            
            partner_id = partner_ids[0]
            
            # Get sales orders for this partner
            orders = self.odoo._execute_kw(
                "sale.order",
                "search_read",
                [[["partner_id", "=", partner_id]]],
                {"fields": ["name", "state", "amount_total", "date_order", "partner_id"]}
            )
            
            return {
                "success": True,
                "partner_id": partner_id,
                "orders": orders,
                "count": len(orders)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_subscriptions(self) -> dict:
        """Get all subscriptions (requires Odoo Subscription module)."""
        if not self._check_connection():
            return {"success": False, "error": f"Odoo not connected: {self.connection_error}"}
        try:
            # Try Odoo 17+ subscription model
            subscriptions = self.odoo._execute_kw(
                "sale.subscription",
                "search_read",
                [],
                {"fields": ["__all__"]}
            )
            
            return {
                "success": True,
                "subscriptions": subscriptions,
                "count": len(subscriptions)
            }
        except Exception as e:
            logger.warning(f"Subscription module may not be installed: {e}")
            return {"success": False, "error": f"Subscription module not available: {str(e)}"}
    
    def update_inventory(self, product_id: int, quantity: int) -> dict:
        """Update product inventory quantity."""
        if not self._check_connection():
            return {"success": False, "error": f"Odoo not connected: {self.connection_error}"}
        try:
            # Get product to find its default location
            product = self.odoo._execute_kw(
                "product.product",
                "read",
                [[product_id]],
                {"fields": ["name", "default_code"]}
            )
            
            if not product:
                return {"success": False, "error": f"Product {product_id} not found"}
            
            # Create stock quant update (Odoo 17+ approach)
            # Find stock quant for this product
            quant_ids = self.odoo._execute_kw(
                "stock.quant",
                "search",
                [[["product_id", "=", product_id]]]
            )
            
            if quant_ids:
                # Update existing quant
                self.odoo._execute_kw(
                    "stock.quant",
                    "write",
                    [[quant_ids[0]], {"quantity": quantity}]
                )
            else:
                # Create new quant - need location_id
                location_id = self.odoo._execute_kw(
                    "stock.location",
                    "search",
                    [[[("usage", "=", "internal")]]],
                    {"limit": 1}
                )
                
                if location_id:
                    self.odoo._execute_kw(
                        "stock.quant",
                        "create",
                        [{
                            "product_id": product_id,
                            "location_id": location_id[0],
                            "quantity": quantity
                        }]
                    )
            
            return {
                "success": True,
                "product_id": product_id,
                "product_name": product[0].get("name"),
                "new_quantity": quantity,
                "message": f"Inventory updated for {product[0].get('name')} to {quantity} units"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_request(self, request: dict) -> dict:
        """Handle incoming MCP request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"Handling request: {method}")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "odoo-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "create_invoice",
                                "description": "Create a new invoice in Odoo",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "partner_id": {"type": "integer", "description": "Customer/partner ID"},
                                        "amount": {"type": "number", "description": "Invoice amount"},
                                        "description": {"type": "string", "description": "Invoice line description"}
                                    },
                                    "required": ["partner_id", "amount", "description"]
                                }
                            },
                            {
                                "name": "get_customer_orders",
                                "description": "Get all orders for a customer by email",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string", "description": "Customer email address"}
                                    },
                                    "required": ["email"]
                                }
                            },
                            {
                                "name": "get_subscriptions",
                                "description": "Get all active subscriptions",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {}
                                }
                            },
                            {
                                "name": "update_inventory",
                                "description": "Update product inventory quantity",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "product_id": {"type": "integer", "description": "Product ID"},
                                        "quantity": {"type": "integer", "description": "New quantity"}
                                    },
                                    "required": ["product_id", "quantity"]
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "create_invoice":
                    result = self.create_invoice(
                        partner_id=arguments.get("partner_id"),
                        amount=arguments.get("amount"),
                        description=arguments.get("description")
                    )
                elif tool_name == "get_customer_orders":
                    result = self.get_customer_orders(
                        email=arguments.get("email")
                    )
                elif tool_name == "get_subscriptions":
                    result = self.get_subscriptions()
                elif tool_name == "update_inventory":
                    result = self.update_inventory(
                        product_id=arguments.get("product_id"),
                        quantity=arguments.get("quantity")
                    )
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                        "isError": not result.get("success", True)
                    }
                }
            
            elif method == "notifications/initialized":
                return None  # No response needed for notifications
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
        
        except Exception as e:
            logger.exception(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": str(e)}
            }


def main():
    """Main entry point - run MCP server in stdio mode."""
    logger.info("Starting Odoo MCP Server...")
    
    try:
        handler = OdooMCPHandler()
        logger.info("Odoo MCP Server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        sys.exit(1)
    
    # Read from stdin, process, write to stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            request = json.loads(line)
            logger.debug(f"Received: {request}")
            
            response = handler.handle_request(request)
            
            if response is not None:
                print(json.dumps(response), flush=True)
                logger.debug(f"Sent: {response}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error: Invalid JSON"}
            }
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
