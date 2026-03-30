# Odoo Invoice Creation Skill

## Overview

This skill creates invoices in Odoo ERP using the Odoo MCP server. It automates the invoice creation process and maintains records in your vault.

---

## Invocation

```
/odoo-invoice "customer@email.com" "amount" "description"
```

### Example
```
/odoo-invoice "john@example.com" "1500.00" "Web Development Services - March 2026"
```

---

## Prerequisites

### 1. Odoo MCP Server Must Be Running

The Odoo MCP server must be running in stdio mode. Start it with:

```bash
# Set environment variables (or use odoo_mcp.env)
export ODOO_URL=http://localhost:8069
export ODOO_DB=odoo
export ODOO_USERNAME=admin@example.com
export ODOO_PASSWORD=admin123

# Start the MCP server
python odoo_mcp_server.py
```

### 2. Environment Variables

Ensure these environment variables are set:

| Variable | Description | Default |
|----------|-------------|---------|
| `ODOO_URL` | Odoo server URL | `http://localhost:8069` |
| `ODOO_DB` | Odoo database name | `odoo` |
| `ODOO_USERNAME` | Admin email for login | `admin@example.com` |
| `ODOO_PASSWORD` | Admin password | `admin123` |

### 3. Required Files

- `odoo_mcp_server.py` - MCP server (must exist)
- `Dashboard.md` - Will be updated with invoice records
- `plans/odoo_invoice.json` - State file for tracking

---

## Skill Implementation

```python
#!/usr/bin/env python3
"""
Odoo Invoice Creation Skill
Creates invoices in Odoo via MCP server and updates vault records.

Usage: python skills/odoo_invoice_skill.py "customer@email.com" "amount" "description"
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Run: pip install requests")
    sys.exit(1)

# Configuration
SKILL_NAME = "odoo_invoice"
STATE_DIR = Path("plans")
STATE_FILE = STATE_DIR / "odoo_invoice.json"
DASHBOARD_FILE = Path("Dashboard.md")
MCP_SERVER_SCRIPT = Path("odoo_mcp_server.py")

# Odoo configuration from environment
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin@example.com")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin123")


class OdooInvoiceSkill:
    """Skill for creating invoices in Odoo."""
    
    def __init__(self):
        self.state_dir = STATE_DIR
        self.state_file = STATE_FILE
        self.dashboard_file = DASHBOARD_FILE
        self.mcp_server = MCP_SERVER_SCRIPT
        
        # Ensure state directory exists
        self.state_dir.mkdir(exist_ok=True)
    
    def check_mcp_server(self) -> bool:
        """Check if MCP server script exists."""
        if not self.mcp_server.exists():
            print(f"ERROR: MCP server not found at {self.mcp_server}")
            print("   Please ensure odoo_mcp_server.py exists in the project root.")
            print("   Start it with: python odoo_mcp_server.py")
            return False
        return True
    
    def check_environment(self) -> bool:
        """Check if Odoo is accessible."""
        try:
            response = requests.get(ODOO_URL, timeout=5)
            if response.status_code != 200:
                print(f"WARNING: Odoo server at {ODOO_URL} returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"ERROR: Cannot connect to Odoo at {ODOO_URL}")
            print("   Please ensure Odoo is running:")
            print("   docker ps | grep odoo")
            return False
        
        return True
    
    def find_partner_by_email(self, email: str) -> dict:
        """Find partner (customer) by email in Odoo."""
        auth_url = f"{ODOO_URL}/web/session/authenticate"
        auth_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": ODOO_DB,
                "login": ODOO_USERNAME,
                "password": ODOO_PASSWORD
            },
            "id": 1
        }
        
        session = requests.Session()
        auth_response = session.post(auth_url, json=auth_payload, timeout=10)
        auth_result = auth_response.json()
        
        if not auth_result.get("result", {}).get("uid"):
            return {"success": False, "error": "Authentication failed"}
        
        # Search for partner by email
        search_url = f"{ODOO_URL}/web/dataset/call"
        search_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "res.partner",
                "method": "search_read",
                "args": [[["email", "=", email]]],
                "kwargs": {"fields": ["id", "name", "email"]}
            },
            "id": 2
        }
        
        search_response = session.post(search_url, json=search_payload, timeout=10)
        search_result = search_response.json()
        
        partners = search_result.get("result", [])
        
        if partners:
            return {
                "success": True,
                "partner_id": partners[0]["id"],
                "partner_name": partners[0]["name"],
                "email": email
            }
        else:
            return {"success": False, "error": f"No customer found with email: {email}"}
    
    def create_invoice(self, partner_id: int, amount: float, description: str) -> dict:
        """Create invoice in Odoo via JSON-RPC."""
        auth_url = f"{ODOO_URL}/web/session/authenticate"
        auth_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": ODOO_DB,
                "login": ODOO_USERNAME,
                "password": ODOO_PASSWORD
            },
            "id": 1
        }
        
        session = requests.Session()
        auth_response = session.post(auth_url, json=auth_payload, timeout=10)
        auth_result = auth_response.json()
        
        if not auth_result.get("result", {}).get("uid"):
            return {"success": False, "error": "Authentication failed"}
        
        # Create invoice
        create_url = f"{ODOO_URL}/web/dataset/call"
        create_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "account.move",
                "method": "create",
                "args": [{
                    "move_type": "out_invoice",
                    "partner_id": partner_id,
                    "invoice_line_ids": [[0, 0, {
                        "name": description,
                        "price_unit": amount,
                        "quantity": 1
                    }]]
                }],
                "kwargs": {}
            },
            "id": 3
        }
        
        create_response = session.post(create_url, json=create_payload, timeout=10)
        create_result = create_response.json()
        
        invoice_id = create_result.get("result")
        
        if invoice_id:
            return {
                "success": True,
                "invoice_id": invoice_id,
                "partner_id": partner_id,
                "amount": amount,
                "description": description
            }
        else:
            return {"success": False, "error": "Failed to create invoice"}
    
    def update_dashboard(self, customer_email: str, amount: float, invoice_id: int, status: str):
        """Update Dashboard.md with invoice record."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create dashboard entry
        entry = f"\n- Invoice #{invoice_id} created for {customer_email} - Amount: ${amount:.2f} - Status: {status} - {timestamp}"
        
        # Read existing dashboard
        if self.dashboard_file.exists():
            content = self.dashboard_file.read_text()
            
            # Check if Invoice section exists
            if "## Invoices" in content:
                # Find the invoice section and append
                lines = content.split('\n')
                new_lines = []
                inserted = False
                
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    if line.startswith("## Invoices") and not inserted:
                        new_lines.append(entry)
                        inserted = True
                
                content = '\n'.join(new_lines)
            else:
                # Add new Invoice section
                content += f"\n\n## Invoices\n{entry}"
        else:
            # Create new dashboard
            content = f"# Dashboard\n\n## Invoices\n{entry}\n"
        
        self.dashboard_file.write_text(content)
        print(f"   [OK] Dashboard updated: {self.dashboard_file}")
    
    def save_state(self, customer_email: str, amount: float, description: str, invoice_id: int, status: str):
        """Save invoice state to plans/odoo_invoice.json."""
        state = {
            "skill": SKILL_NAME,
            "timestamp": datetime.now().isoformat(),
            "invoice": {
                "invoice_id": invoice_id,
                "customer_email": customer_email,
                "amount": amount,
                "description": description,
                "status": status
            },
            "odoo_config": {
                "url": ODOO_URL,
                "database": ODOO_DB
            }
        }
        
        # Append to existing state file or create new
        states = []
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    states = json.load(f)
            except:
                states = []
        
        states.append(state)
        
        with open(self.state_file, 'w') as f:
            json.dump(states, f, indent=2)
        
        print(f"   [OK] State saved: {self.state_file}")
    
    def execute(self, customer_email: str, amount: str, description: str) -> dict:
        """Execute the invoice creation skill."""
        print(f"\n{'='*60}")
        print(f"ODOO INVOICE SKILL")
        print(f"{'='*60}")
        
        result = {
            "success": False,
            "invoice_id": None,
            "customer": customer_email,
            "amount": amount,
            "description": description,
            "error": None
        }
        
        # Step 1: Check MCP server exists
        print(f"\n[1/5] Checking MCP server...")
        if not self.check_mcp_server():
            result["error"] = "MCP server not found"
            print("   HINT: Start MCP server with: python odoo_mcp_server.py")
            return result
        print("    [OK] MCP server found")
        
        # Step 2: Check Odoo connection
        print(f"\n[2/5] Checking Odoo connection...")
        if not self.check_environment():
            result["error"] = "Environment check failed"
            print("   HINT: Start Odoo with: docker-compose up -d")
            return result
        print("    [OK] Environment OK")
        
        # Step 3: Find customer by email
        print(f"\n[3/5] Finding customer: {customer_email}")
        customer_result = self.find_partner_by_email(customer_email)
        
        if not customer_result.get("success"):
            error_msg = customer_result.get("error", "Customer not found")
            print(f"    ERROR: {error_msg}")
            result["error"] = f"Customer not found: {customer_email}"
            print(f"\n   TIP: Create the customer in Odoo first:")
            print(f"      1. Go to http://localhost:8069")
            print(f"      2. Navigate to Contacts")
            print(f"      3. Create new contact with email: {customer_email}")
            return result
        
        partner_id = customer_result.get("partner_id")
        partner_name = customer_result.get("partner_name", customer_email)
        print(f"    [OK] Customer found: {partner_name} (ID: {partner_id})")
        
        # Step 4: Create invoice
        print(f"\n[4/5] Creating invoice...")
        print(f"    Amount: ${amount}")
        print(f"    Description: {description}")
        
        try:
            amount_float = float(amount)
        except ValueError:
            result["error"] = f"Invalid amount: {amount}"
            print(f"    ERROR: Invalid amount format")
            return result
        
        invoice_result = self.create_invoice(partner_id, amount_float, description)
        
        if not invoice_result.get("success"):
            error_msg = invoice_result.get("error", "Unknown error")
            print(f"    ERROR: {error_msg}")
            result["error"] = error_msg
            return result
        
        invoice_id = invoice_result.get("invoice_id")
        print(f"    [OK] Invoice created: #{invoice_id}")
        
        # Step 5: Update records
        print(f"\n[5/5] Updating records...")
        self.update_dashboard(customer_email, amount_float, invoice_id, "Created")
        self.save_state(customer_email, amount_float, description, invoice_id, "Created")
        
        # Success
        result["success"] = True
        result["invoice_id"] = invoice_id
        
        print(f"\n{'='*60}")
        print(f"INVOICE CREATED SUCCESSFULLY!")
        print(f"   Invoice ID: #{invoice_id}")
        print(f"   Customer: {partner_name}")
        print(f"   Amount: ${amount_float:.2f}")
        print(f"{'='*60}\n")
        
        return result


def main():
    """Main entry point for the skill."""
    if len(sys.argv) < 4:
        print("Usage: python skills/odoo_invoice_skill.py \"customer@email.com\" \"amount\" \"description\"")
        print("Example: python skills/odoo_invoice_skill.py \"john@example.com\" \"1500.00\" \"Consulting Services\"")
        sys.exit(1)
    
    customer_email = sys.argv[1]
    amount = sys.argv[2]
    description = sys.argv[3]
    
    skill = OdooInvoiceSkill()
    result = skill.execute(customer_email, amount, description)
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
```

---

## Usage Instructions

### Method 1: Direct Python Execution

```bash
cd C:\Users\AA\Desktop\gold_tier

# Run the skill
python skills/odoo_invoice_skill.py "customer@example.com" "1500.00" "Service Description"
```

### Method 2: As MCP Agent Skill

If your MCP client supports skill invocation:

```
/odoo-invoice "customer@example.com" "1500.00" "Web Development Services"
```

---

## Output Files

### 1. Dashboard.md Update

After successful execution, `Dashboard.md` will contain:

```markdown
# Dashboard

## Invoices
- Invoice #42 created for customer@example.com - Amount: $1500.00 - Status: Created - 2026-03-24 19:00:00
```

### 2. plans/odoo_invoice.json

State file content:

```json
[
  {
    "skill": "odoo_invoice",
    "timestamp": "2026-03-24T19:00:00",
    "invoice": {
      "invoice_id": 42,
      "customer_email": "customer@example.com",
      "amount": 1500.00,
      "description": "Web Development Services",
      "status": "Created"
    },
    "odoo_config": {
      "url": "http://localhost:8069",
      "database": "odoo"
    }
  }
]
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `MCP server not found` | `odoo_mcp_server.py` missing | Ensure file exists in project root |
| `Cannot connect to Odoo` | Odoo not running | Run: `docker ps \| grep odoo` |
| `Customer not found` | Email not in Odoo | Create customer in Odoo first |
| `Authentication failed` | Wrong credentials | Check `ODOO_USERNAME` and `ODOO_PASSWORD` |
| `Invalid amount format` | Non-numeric amount | Use format: `1500.00` |

---

## Quick Start Checklist

- [ ] Odoo running: `docker ps | grep odoo`
- [ ] Database created: Visit http://localhost:8069
- [ ] Environment set: `source odoo_mcp.env`
- [ ] MCP server exists: `ls odoo_mcp_server.py`
- [ ] Run skill: `python skills/odoo_invoice_skill.py "email" "amount" "desc"`

---

## Support

For issues:
1. Check logs: `docker logs odoo --tail 50`
2. Verify connection: `curl http://localhost:8069`
3. Test MCP server: `python test_mcp_quick.py`
