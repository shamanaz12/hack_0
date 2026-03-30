#!/usr/bin/env python3
"""
Simple test client for Odoo MCP Server.
Tests all available tools by communicating via stdio.
"""

import json
import subprocess
import sys
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv("odoo_mcp.env")

SERVER_SCRIPT = "odoo_mcp_server.py"


class MCPTestClient:
    """Test client for MCP server communication."""
    
    def __init__(self):
        self.process = None
        self.request_id = 0
    
    def start(self):
        """Start the MCP server process."""
        self.process = subprocess.Popen(
            [sys.executable, SERVER_SCRIPT],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        print("MCP Server started")
    
    def stop(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            print("MCP Server stopped")
    
    def send_request(self, method: str, params: dict = None) -> dict:
        """Send a request to the MCP server."""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request) + "\n"
        print(f"\n>>> Sending: {request_json.strip()}")
        
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        response_line = self.process.stdout.readline()
        response = json.loads(response_line)
        print(f"<<< Response: {json.dumps(response, indent=2)}")
        
        return response
    
    def initialize(self):
        """Initialize the MCP session."""
        print("\n=== Initializing ===")
        return self.send_request("initialize")
    
    def list_tools(self):
        """List available tools."""
        print("\n=== Listing Tools ===")
        return self.send_request("tools/list")
    
    def call_tool(self, name: str, arguments: dict):
        """Call a tool with arguments."""
        print(f"\n=== Calling Tool: {name} ===")
        return self.send_request("tools/call", {"name": name, "arguments": arguments})


def main():
    """Run test scenarios."""
    client = MCPTestClient()
    
    try:
        client.start()
        
        # Initialize
        client.initialize()
        
        # List available tools
        client.list_tools()
        
        # Test 1: Get customer orders
        print("\n" + "="*50)
        print("TEST 1: Get Customer Orders")
        print("="*50)
        email = input("Enter customer email (or press Enter for test@example.com): ").strip()
        email = email or "test@example.com"
        result = client.call_tool("get_customer_orders", {"email": email})
        
        # Test 2: Get subscriptions
        print("\n" + "="*50)
        print("TEST 2: Get Subscriptions")
        print("="*50)
        result = client.call_tool("get_subscriptions", {})
        
        # Test 3: Create invoice
        print("\n" + "="*50)
        print("TEST 3: Create Invoice")
        print("="*50)
        try:
            partner_id = int(input("Enter partner ID (or press Enter for 1): ").strip() or "1")
            amount = float(input("Enter amount (or press Enter for 100.0): ").strip() or "100.0")
            description = input("Enter description (or press Enter for 'Test Invoice'): ").strip() or "Test Invoice"
            result = client.call_tool("create_invoice", {
                "partner_id": partner_id,
                "amount": amount,
                "description": description
            })
        except ValueError as e:
            print(f"Invalid input: {e}")
        
        # Test 4: Update inventory
        print("\n" + "="*50)
        print("TEST 4: Update Inventory")
        print("="*50)
        try:
            product_id = int(input("Enter product ID (or press Enter for 1): ").strip() or "1")
            quantity = int(input("Enter quantity (or press Enter for 10): ").strip() or "10")
            result = client.call_tool("update_inventory", {
                "product_id": product_id,
                "quantity": quantity
            })
        except ValueError as e:
            print(f"Invalid input: {e}")
        
        print("\n" + "="*50)
        print("All tests completed!")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.stop()


if __name__ == "__main__":
    main()
