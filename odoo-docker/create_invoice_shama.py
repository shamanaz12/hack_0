#!/usr/bin/env python3
"""
Create Invoice for Shama Naz - Complete Script
Creates customer if not exists, then creates invoice and verifies it.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo"
ODOO_LOGIN = "admin@example.com"
ODOO_PASSWORD = "admin123"

# Invoice Details
CUSTOMER_NAME = "Shama Naz"
CUSTOMER_EMAIL = "shama.naz@example.com"
INVOICE_AMOUNT = 5000.00
INVOICE_DESCRIPTION = "Professional Services - March 2026"


def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def authenticate(session):
    """Authenticate with Odoo."""
    auth_url = f"{ODOO_URL}/web/session/authenticate"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": ODOO_DB,
            "login": ODOO_LOGIN,
            "password": ODOO_PASSWORD
        },
        "id": 1
    }
    
    response = session.post(auth_url, json=payload, timeout=10)
    result = response.json()
    
    if result.get("result", {}).get("uid"):
        return result["result"]["uid"], None
    return None, "Authentication failed"


def find_or_create_customer(session, uid, name, email):
    """Find existing customer or create new one."""
    # Try to find by email
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
                {"fields": ["id", "name", "email"]}
            ]
        },
        "id": 2
    }
    
    response = session.post(f"{ODOO_URL}/jsonrpc", json=search_payload, timeout=10)
    result = response.json()
    
    if "error" in result:
        print(f"    ERROR: {result['error'].get('message', 'Unknown error')}")
        return None
    
    partners = result.get("result", [])
    
    if partners:
        print(f"    [OK] Customer found: {partners[0]['name']} (ID: {partners[0]['id']})")
        return partners[0]["id"]
    
    # Customer not found, create new one
    print(f"    [INFO] Customer not found. Creating new customer: {name}")
    
    create_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, uid, ODOO_PASSWORD,
                "res.partner",
                "create",
                [{
                    "name": name,
                    "email": email,
                    "customer_rank": 1
                }]
            ]
        },
        "id": 3
    }
    
    response = session.post(f"{ODOO_URL}/jsonrpc", json=create_payload, timeout=10)
    result = response.json()
    
    if "error" in result:
        print(f"    ERROR: Failed to create customer - {result['error'].get('message', 'Unknown error')}")
        return None
    
    customer_id = result.get("result")
    print(f"    [OK] Customer created: {name} (ID: {customer_id})")
    return customer_id


def create_invoice(session, uid, partner_id, amount, description):
    """Create invoice in Odoo."""
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
        "id": 4
    }
    
    response = session.post(f"{ODOO_URL}/jsonrpc", json=create_payload, timeout=10)
    result = response.json()
    
    if "error" in result:
        error_msg = result["error"].get("message", "Unknown error")
        print(f"    ERROR: Failed to create invoice - {error_msg}")
        return None
    
    invoice_id = result.get("result")
    return invoice_id


def verify_invoice(session, uid, invoice_id):
    """Verify invoice was created successfully."""
    read_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, uid, ODOO_PASSWORD,
                "account.move",
                "read",
                [[invoice_id]],
                {"fields": ["id", "name", "partner_id", "amount_total", "state", "invoice_date"]}
            ]
        },
        "id": 5
    }
    
    response = session.post(f"{ODOO_URL}/jsonrpc", json=read_payload, timeout=10)
    result = response.json()
    
    if "error" in result:
        return None, result["error"].get("message", "Unknown error")
    
    invoices = result.get("result", [])
    if invoices:
        return invoices[0], None
    return None, "Invoice not found"


def get_invoice_url(invoice_id):
    """Get direct URL to view invoice in Odoo."""
    return f"{ODOO_URL}/web#id={invoice_id}&cids=1&menu_id=113&action=242&model=account.move&view_type=form"


def main():
    print_header("INVOICE CREATION SCRIPT - SHAMA NAZ")
    
    # Step 1: Authenticate
    print("[1/5] Authenticating with Odoo...")
    session = requests.Session()
    uid, error = authenticate(session)
    
    if not uid:
        print(f"    ERROR: {error}")
        print("    HINT: Check credentials and try again")
        return False
    
    print(f"    [OK] Authenticated as UID: {uid}")
    
    # Step 2: Find or create customer
    print(f"\n[2/5] Finding/Creating customer: {CUSTOMER_NAME}")
    partner_id = find_or_create_customer(session, uid, CUSTOMER_NAME, CUSTOMER_EMAIL)
    
    if not partner_id:
        print("    ERROR: Could not find or create customer")
        return False
    
    # Step 3: Create invoice
    print(f"\n[3/5] Creating invoice...")
    print(f"    Amount: ${INVOICE_AMOUNT:.2f}")
    print(f"    Description: {INVOICE_DESCRIPTION}")
    
    invoice_id = create_invoice(session, uid, partner_id, INVOICE_AMOUNT, INVOICE_DESCRIPTION)
    
    if not invoice_id:
        print("    ERROR: Failed to create invoice")
        return False
    
    print(f"    [OK] Invoice created: #{invoice_id}")
    
    # Step 4: Verify invoice
    print(f"\n[4/5] Verifying invoice #{invoice_id}...")
    invoice_data, error = verify_invoice(session, uid, invoice_id)
    
    if error:
        print(f"    ERROR: {error}")
        return False
    
    print(f"    [OK] Invoice verified!")
    print(f"\n    Invoice Details:")
    print(f"    -------------------------------------")
    print(f"    Invoice Number: {invoice_data.get('name', 'N/A')}")
    print(f"    Invoice ID:     {invoice_data.get('id', 'N/A')}")
    print(f"    Customer:       {CUSTOMER_NAME} (ID: {partner_id})")
    print(f"    Amount:         ${invoice_data.get('amount_total', 0):.2f}")
    print(f"    Status:         {invoice_data.get('state', 'N/A')}")
    print(f"    Date:           {invoice_data.get('invoice_date', 'N/A')}")
    print(f"    -------------------------------------")
    
    # Step 5: Show URL
    invoice_url = get_invoice_url(invoice_id)
    print(f"\n[5/5] Invoice URL:")
    print(f"    {invoice_url}")
    
    # Final confirmation
    print_header("✅ INVOICE CONFIRMED - SUCCESSFULLY CREATED!")
    print(f"  Invoice ID:    #{invoice_id}")
    print(f"  Customer:      {CUSTOMER_NAME}")
    print(f"  Amount:        ${INVOICE_AMOUNT:.2f}")
    print(f"  Status:        {invoice_data.get('state', 'Draft')}")
    print(f"\n  View in Odoo:  {invoice_url}")
    print_header("CONFIRMATION: Invoice ban gayi hai! ✅")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
