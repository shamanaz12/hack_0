# 🚀 Quick Start Guide - Odoo MCP Server

## ✅ Setup Complete!

### What's Ready:
- ✅ Odoo running at http://localhost:8069
- ✅ MCP server created: `odoo_mcp_server.py`
- ✅ Test client ready: `odoo_mcp_test_client.py`
- ✅ Config file: `mcp_config.json`

---

## 📝 Step 1: Create Database in Odoo

1. Open browser: **http://localhost:8069**
2. Click **"Create Database"**
3. Fill this form:
   ```
   Master Password:  admin123
   Database Name:    odoo
   Email:            admin@example.com
   Password:         admin123
   Country:          Pakistan
   Demo Data:        ✓ (tick it)
   ```
4. Click **"Create Database"**

---

## 🧪 Step 2: Test MCP Server

### Option A: Quick Test
```bash
python test_mcp_quick.py
```

### Option B: Interactive Test
```bash
python odoo_mcp_test_client.py
```

---

## 🔧 Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_invoice` | Create customer invoice | partner_id, amount, description |
| `get_customer_orders` | Get orders by email | email |
| `get_subscriptions` | Get all subscriptions | (none) |
| `update_inventory` | Update product stock | product_id, quantity |

---

## 📌 Environment Variables

Edit `.env` or set before running:
```env
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin@example.com
ODOO_PASSWORD=admin123
```

---

## 🎯 Example Usage

### Create Invoice:
```python
result = call_tool("create_invoice", {
    "partner_id": 1,
    "amount": 100.0,
    "description": "Consulting Services"
})
```

### Get Customer Orders:
```python
result = call_tool("get_customer_orders", {
    "email": "customer@example.com"
})
```

---

## ❓ Troubleshooting

### "Access Denied" Error
- Check master password: `admin123`
- Verify database name: `odoo`

### "Connection Refused" Error
- Make sure Odoo is running: `docker ps`
- Check URL: http://localhost:8069

### Login Failed
- Use the email/password you set during database creation
- Default: `admin@example.com` / `admin123`

---

## 📞 Need Help?

Run the setup script:
```bash
setup_odoo_mcp.bat
```

Or check logs:
```bash
docker logs odoo --tail 50
```
