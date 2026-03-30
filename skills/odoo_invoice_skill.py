#!/usr/bin/env python3
"""
Odoo Invoice Creation Skill
Creates invoices in Odoo via direct JSON-RPC API.

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
        self.state_dir.mkdir(exist_ok=True)
    
    def check_environment(self) -> bool:
        """Check if Odoo is accessible."""
        try:
            response = requests.get(ODOO_URL, timeout=5)
            if response.status_code != 200:
                print(f"WARNING: Odoo server returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"ERROR: Cannot connect to Odoo at {ODOO_URL}")
            print("   Please ensure Odoo is running: docker ps | grep odoo")
            return False
        return True
    
    def authenticate(self, session):
        """Authenticate with Odoo and return user ID."""
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
        
        response = session.post(auth_url, json=auth_payload, timeout=10)
        if response.status_code != 200:
            return None, f"HTTP {response.status_code}"
        
        result = response.json()
        uid = result.get("result", {}).get("uid")
        return uid, None
    
    def find_partner_by_email(self, session, uid, email: str) -> dict:
        """Find partner (customer) by email in Odoo."""
        search_url = f"{ODOO_URL}/jsonrpc"
        search_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, uid, ODOO_PASSWORD,
                    "res.partner",
                    "search_read",
                    [[["email", "=", email]]],
                    {"fields": ["id", "name", "email"], "limit": 1}
                ]
            },
            "id": 2
        }
        
        response = session.post(search_url, json=search_payload, timeout=10)
        if response.status_code != 200:
            return {"success": False, "error": f"HTTP {response.status_code}"}
        
        result = response.json()
        if "error" in result:
            return {"success": False, "error": result["error"].get("message", "Unknown error")}
        
        partners = result.get("result", [])
        if partners:
            return {
                "success": True,
                "partner_id": partners[0]["id"],
                "partner_name": partners[0]["name"],
                "email": email
            }
        return {"success": False, "error": f"No customer found with email: {email}"}
    
    def create_invoice(self, session, uid, partner_id: int, amount: float, description: str) -> dict:
        """Create invoice in Odoo."""
        create_url = f"{ODOO_URL}/jsonrpc"
        create_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, uid, ODOO_PASSWORD,
                    "account.move",
                    "create",
                    [{
                        "move_type": "out_invoice",
                        "partner_id": partner_id,
                        "invoice_line_ids": [[0, 0, {
                            "name": description,
                            "price_unit": amount,
                            "quantity": 1
                        }]]
                    }]
                ]
            },
            "id": 3
        }
        
        response = session.post(create_url, json=create_payload, timeout=10)
        if response.status_code != 200:
            return {"success": False, "error": f"HTTP {response.status_code}"}
        
        result = response.json()
        if "error" in result:
            return {"success": False, "error": result["error"].get("message", "Unknown error")}
        
        invoice_id = result.get("result")
        if invoice_id:
            return {
                "success": True,
                "invoice_id": invoice_id,
                "partner_id": partner_id,
                "amount": amount,
                "description": description
            }
        return {"success": False, "error": "Failed to create invoice"}
    
    def update_dashboard(self, customer_email: str, amount: float, invoice_id: int, status: str):
        """Update Dashboard.md with invoice record."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n- Invoice #{invoice_id} created for {customer_email} - Amount: ${amount:.2f} - Status: {status} - {timestamp}"
        
        if self.dashboard_file.exists():
            content = self.dashboard_file.read_text()
            if "## Invoices" in content:
                lines = content.split('\n')
                new_lines = []
                inserted = False
                for line in lines:
                    new_lines.append(line)
                    if line.startswith("## Invoices") and not inserted:
                        new_lines.append(entry)
                        inserted = True
                content = '\n'.join(new_lines)
            else:
                content += f"\n\n## Invoices\n{entry}"
        else:
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
            "odoo_config": {"url": ODOO_URL, "database": ODOO_DB}
        }
        
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
        
        result = {"success": False, "invoice_id": None, "customer": customer_email, "amount": amount, "description": description, "error": None}
        
        # Step 1: Check environment
        print(f"\n[1/4] Checking Odoo connection...")
        if not self.check_environment():
            result["error"] = "Environment check failed"
            print("   HINT: Start Odoo with: docker-compose up -d")
            return result
        print("    [OK] Environment OK")
        
        # Step 2: Authenticate
        print(f"\n[2/4] Authenticating...")
        session = requests.Session()
        uid, error = self.authenticate(session)
        if not uid:
            result["error"] = f"Authentication failed: {error}"
            print(f"    ERROR: {error}")
            print("   HINT: Check credentials in odoo_mcp.env")
            return result
        print(f"    [OK] Authenticated as UID: {uid}")
        
        # Step 3: Find customer
        print(f"\n[3/4] Finding customer: {customer_email}")
        customer_result = self.find_partner_by_email(session, uid, customer_email)
        
        if not customer_result.get("success"):
            result["error"] = customer_result.get("error")
            print(f"    ERROR: {result['error']}")
            print(f"\n   TIP: Create customer in Odoo first:")
            print(f"      1. Go to {ODOO_URL}")
            print(f"      2. Navigate to Contacts")
            print(f"      3. Create contact with email: {customer_email}")
            return result
        
        partner_id = customer_result["partner_id"]
        partner_name = customer_result["partner_name"]
        print(f"    [OK] Customer found: {partner_name} (ID: {partner_id})")
        
        # Step 4: Create invoice
        print(f"\n[4/4] Creating invoice...")
        print(f"    Amount: ${amount}")
        print(f"    Description: {description}")
        
        try:
            amount_float = float(amount)
        except ValueError:
            result["error"] = f"Invalid amount: {amount}"
            print(f"    ERROR: Invalid amount format")
            return result
        
        invoice_result = self.create_invoice(session, uid, partner_id, amount_float, description)
        
        if not invoice_result.get("success"):
            result["error"] = invoice_result.get("error")
            print(f"    ERROR: {result['error']}")
            return result
        
        invoice_id = invoice_result["invoice_id"]
        print(f"    [OK] Invoice created: #{invoice_id}")
        
        # Update records
        print(f"\nUpdating records...")
        self.update_dashboard(customer_email, amount_float, invoice_id, "Created")
        self.save_state(customer_email, amount_float, description, invoice_id, "Created")
        
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
