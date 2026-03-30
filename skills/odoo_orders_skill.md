# Odoo Customer Orders Skill

## Overview

This skill fetches customer orders from Odoo ERP using the Odoo MCP server. It retrieves all sales orders for a given customer email and presents them in a readable format.

---

## Invocation

```
/odoo-orders "customer@email.com"
```

### Example
```
/odoo-orders "john@example.com"
```

---

## Prerequisites

### 1. Odoo MCP Server Must Be Running

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

| Variable | Description | Default |
|----------|-------------|---------|
| `ODOO_URL` | Odoo server URL | `http://localhost:8069` |
| `ODOO_DB` | Odoo database name | `odoo` |
| `ODOO_USERNAME` | Admin email for login | `admin@example.com` |
| `ODOO_PASSWORD` | Admin password | `admin123` |

### 3. Required Files

- `odoo_mcp_server.py` - MCP server
- `Plans/` directory - For saving order reports

---

## Skill Implementation

```python
#!/usr/bin/env python3
"""
Odoo Customer Orders Skill
Fetches customer orders from Odoo and saves reports to Plans/.

Usage: python skills/odoo_orders_skill.py "customer@email.com"
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
SKILL_NAME = "odoo_orders"
PLANS_DIR = Path("Plans")
DASHBOARD_FILE = Path("Dashboard.md")

# Odoo configuration from environment
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin@example.com")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin123")


class OdooOrdersSkill:
    """Skill for fetching customer orders from Odoo."""
    
    def __init__(self):
        self.plans_dir = PLANS_DIR
        self.dashboard_file = DASHBOARD_FILE
        
        # Ensure plans directory exists
        self.plans_dir.mkdir(exist_ok=True)
    
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
    
    def get_customer_orders(self, email: str) -> dict:
        """Fetch orders for a customer by email from Odoo."""
        # Authenticate
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
        
        if not partners:
            return {"success": False, "error": f"No customer found with email: {email}"}
        
        partner_id = partners[0]["id"]
        partner_name = partners[0]["name"]
        
        # Fetch sales orders for this partner
        orders_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "sale.order",
                "method": "search_read",
                "args": [[["partner_id", "=", partner_id]]],
                "kwargs": {
                    "fields": ["name", "state", "amount_total", "date_order", "partner_id"],
                    "order": "date_order desc"
                }
            },
            "id": 3
        }
        
        orders_response = session.post(search_url, json=orders_payload, timeout=10)
        orders_result = orders_response.json()
        
        orders = orders_result.get("result", [])
        
        return {
            "success": True,
            "partner_id": partner_id,
            "partner_name": partner_name,
            "email": email,
            "orders": orders,
            "count": len(orders)
        }
    
    def format_orders_markdown(self, result: dict) -> str:
        """Format orders as readable markdown."""
        lines = []
        lines.append(f"# Customer Orders Report")
        lines.append(f"")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Customer:** {result.get('partner_name')} ({result.get('email')})")
        lines.append(f"**Total Orders:** {result.get('count')}")
        lines.append(f"")
        
        orders = result.get('orders', [])
        
        if not orders:
            lines.append(f"*No orders found for this customer.*")
        else:
            lines.append(f"## Orders")
            lines.append(f"")
            lines.append(f"| Order # | Date | Status | Total |")
            lines.append(f"|---------|------|--------|-------|")
            
            total_amount = 0
            
            for order in orders:
                order_name = order.get('name', 'N/A')
                date_order = order.get('date_order', 'N/A')[:10] if order.get('date_order') else 'N/A'
                state = order.get('state', 'N/A')
                amount = order.get('amount_total', 0)
                total_amount += amount
                
                # Status emoji
                status_emoji = {
                    'draft': '📝',
                    'sent': '📤',
                    'sale': '✅',
                    'done': '✔️',
                    'cancel': '❌'
                }.get(state, '')
                
                lines.append(f"| {order_name} | {date_order} | {status_emoji} {state} | ${amount:.2f} |")
            
            lines.append(f"")
            lines.append(f"**Total Revenue:** ${total_amount:.2f}")
        
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"*Report generated by Odoo Orders Skill*")
        
        return '\n'.join(lines)
    
    def save_report(self, email: str, content: str) -> Path:
        """Save order report to Plans/ directory."""
        # Create safe filename from email
        safe_name = email.replace('@', '_at_').replace('.', '_').replace('/', '_')
        filename = f"orders_{safe_name}.md"
        
        filepath = self.plans_dir / filename
        filepath.write_text(content)
        
        return filepath
    
    def update_dashboard(self, email: str, order_count: int, customer_name: str):
        """Update Dashboard.md with order lookup record."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = f"\n- Orders checked for {customer_name} ({email}) - {order_count} orders found - {timestamp}"
        
        if self.dashboard_file.exists():
            content = self.dashboard_file.read_text()
            
            if "## Order History" not in content:
                content += f"\n\n## Order History\n"
            
            content += entry + "\n"
            
            self.dashboard_file.write_text(content)
    
    def execute(self, customer_email: str) -> dict:
        """Execute the orders fetch skill."""
        print(f"\n{'='*60}")
        print(f"ODOO ORDERS SKILL")
        print(f"{'='*60}")
        
        result = {
            "success": False,
            "customer": customer_email,
            "orders": [],
            "report_file": None,
            "error": None
        }
        
        # Step 1: Check Odoo connection
        print(f"\n[1/3] Checking Odoo connection...")
        if not self.check_environment():
            result["error"] = "Environment check failed"
            print("   HINT: Start Odoo with: docker-compose up -d")
            return result
        print("    [OK] Environment OK")
        
        # Step 2: Fetch orders
        print(f"\n[2/3] Fetching orders for: {customer_email}")
        orders_result = self.get_customer_orders(customer_email)
        
        if not orders_result.get("success"):
            error_msg = orders_result.get("error", "Unknown error")
            print(f"    ERROR: {error_msg}")
            result["error"] = error_msg
            
            if "No customer found" in error_msg:
                print(f"\n   TIP: Create the customer in Odoo first:")
                print(f"      1. Go to http://localhost:8069")
                print(f"      2. Navigate to Contacts")
                print(f"      3. Create new contact with email: {customer_email}")
            
            return result
        
        partner_name = orders_result.get("partner_name")
        order_count = orders_result.get("count")
        print(f"    [OK] Found {order_count} orders for {partner_name}")
        
        # Step 3: Save report
        print(f"\n[3/3] Saving report...")
        
        # Format as markdown
        markdown_content = self.format_orders_markdown(orders_result)
        
        # Save to file
        report_file = self.save_report(customer_email, markdown_content)
        print(f"    [OK] Report saved: {report_file}")
        
        # Update dashboard
        self.update_dashboard(customer_email, order_count, partner_name)
        print(f"    [OK] Dashboard updated")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"ORDERS FETCHED SUCCESSFULLY!")
        print(f"   Customer: {partner_name}")
        print(f"   Email: {customer_email}")
        print(f"   Total Orders: {order_count}")
        print(f"   Report: {report_file}")
        print(f"{'='*60}\n")
        
        # Print orders summary
        orders = orders_result.get("orders", [])
        if orders:
            print("Recent Orders:")
            for order in orders[:5]:  # Show last 5
                print(f"  - {order.get('name')}: ${order.get('amount_total', 0):.2f} ({order.get('state')})")
            if len(orders) > 5:
                print(f"  ... and {len(orders) - 5} more")
            print()
        
        result["success"] = True
        result["orders"] = orders
        result["report_file"] = str(report_file)
        
        return result


def main():
    """Main entry point for the skill."""
    if len(sys.argv) < 2:
        print("Usage: python skills/odoo_orders_skill.py \"customer@email.com\"")
        print("Example: python skills/odoo_orders_skill.py \"john@example.com\"")
        sys.exit(1)
    
    customer_email = sys.argv[1]
    
    skill = OdooOrdersSkill()
    result = skill.execute(customer_email)
    
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
python skills/odoo_orders_skill.py "customer@example.com"
```

### Method 2: As MCP Agent Skill

```
/odoo-orders "customer@example.com"
```

---

## Output Files

### 1. Plans/orders_{customer}.md

Example report file:

```markdown
# Customer Orders Report

**Generated:** 2026-03-24 19:00:00
**Customer:** John Doe (john@example.com)
**Total Orders:** 3

## Orders

| Order # | Date | Status | Total |
|---------|------|--------|-------|
| S00003 | 2026-03-20 | ✅ sale | $1500.00 |
| S00002 | 2026-03-15 | ✔️ done | $2500.00 |
| S00001 | 2026-03-10 | 📝 draft | $500.00 |

**Total Revenue:** $4500.00

---
*Report generated by Odoo Orders Skill*
```

### 2. Dashboard.md Update

```markdown
## Order History
- Orders checked for John Doe (john@example.com) - 3 orders found - 2026-03-24 19:00:00
```

---

## Order Status Meanings

| Status | Description | Emoji |
|--------|-------------|-------|
| `draft` | Order created but not sent | 📝 |
| `sent` | Order sent to customer | 📤 |
| `sale` | Order confirmed | ✅ |
| `done` | Order completed/delivered | ✔️ |
| `cancel` | Order cancelled | ❌ |

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Cannot connect to Odoo` | Odoo not running | Run: `docker ps \| grep odoo` |
| `No customer found` | Email not in Odoo | Create customer in Contacts first |
| `Authentication failed` | Wrong credentials | Check `ODOO_USERNAME` and `ODOO_PASSWORD` |

---

## Quick Start Checklist

- [ ] Odoo running: `docker ps | grep odoo`
- [ ] Environment set: `source odoo_mcp.env`
- [ ] Customer exists in Odoo
- [ ] Run skill: `python skills/odoo_orders_skill.py "email"`

---

## Support

For issues:
1. Check Odoo logs: `docker logs odoo --tail 50`
2. Verify customer exists: Navigate to Contacts in Odoo
3. Test connection: `curl http://localhost:8069`
