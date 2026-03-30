# Odoo MCP Server

A Model Context Protocol (MCP) server that provides tools to interact with a self-hosted Odoo instance via JSON-RPC.

## Features

- **create_invoice**: Create customer invoices
- **get_customer_orders**: Retrieve orders by customer email
- **get_subscriptions**: List all subscriptions (requires Odoo Subscription module)
- **update_inventory**: Update product stock quantities

## Prerequisites

- Python 3.8+
- Odoo 17.0+ running at `http://localhost:8069`
- requests library

## Installation

```bash
pip install -r odoo_mcp_requirements.txt
pip install python-dotenv  # For test client
```

## Configuration

Copy `odoo_mcp.env` and update with your Odoo credentials:

```env
ODOO_URL=http://localhost:8069
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password
```

## Running the MCP Server

The server runs in **stdio mode** for MCP communication:

```bash
# Set environment variables
export ODOO_URL=http://localhost:8069
export ODOO_DB=odoo
export ODOO_USERNAME=admin
export ODOO_PASSWORD=admin

# Run the server
python odoo_mcp_server.py
```

## Testing with the Test Client

```bash
# Install dotenv for the test client
pip install python-dotenv

# Run the interactive test client
python odoo_mcp_test_client.py
```

## Testing with curl (Manual JSON-RPC)

```bash
# List tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python odoo_mcp_server.py

# Call a tool
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_subscriptions","arguments":{}}}' | python odoo_mcp_server.py
```

## MCP Client Configuration

Add to your MCP client config (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "odoo": {
      "command": "python",
      "args": ["C:/Users/AA/Desktop/gold_tier/odoo_mcp_server.py"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "odoo",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "admin"
      }
    }
  }
}
```

## Tool Reference

### create_invoice
Create a new customer invoice.
```json
{
  "partner_id": 1,
  "amount": 100.0,
  "description": "Consulting services"
}
```

### get_customer_orders
Get all orders for a customer by email.
```json
{
  "email": "customer@example.com"
}
```

### get_subscriptions
Get all active subscriptions (no parameters).

### update_inventory
Update product inventory quantity.
```json
{
  "product_id": 1,
  "quantity": 50
}
```

## Troubleshooting

1. **Authentication failed**: Check your Odoo credentials in environment variables
2. **Connection refused**: Ensure Odoo is running at the configured URL
3. **Module not found**: Some tools require specific Odoo modules (e.g., subscriptions)

## Logs

Server logs are written to stderr and don't interfere with the stdio MCP protocol.
