# MCP Servers - Organized Structure

## 📁 Folder Organization

### **Root Level (Existing Servers - UNTOUCHED)**
These are your original working servers - **DO NOT DELETE**:
- `facebook_mcp_playwright.py` - Facebook automation
- `whatsapp_mcp.js` - WhatsApp messaging
- `gmail_mcp_server.py` - Gmail automation
- `calendar_mcp.js` - Google Calendar
- `slack_mcp.js` - Slack integration
- `social_mcp_*.py` - Social media tools

### **communication/ (NEW)**
Email and messaging servers:
- `gmail_mcp_v2.py` - Enhanced Gmail (optional upgrade)
- `whatsapp_mcp_v2.py` - Enhanced WhatsApp (optional upgrade)
- `slack_mcp_v2.py` - Enhanced Slack (optional upgrade)
- `calendar_mcp_v2.py` - Enhanced Calendar (optional upgrade)

### **social_media/ (NEW)**
Social media management:
- `facebook_posting.py` - Facebook posting with AI
- `instagram_posting.py` - Instagram posting with AI
- `twitter_mcp.py` - Twitter integration (NEW)
- `social_summary.py` - Generate social media summaries

### **business/ (NEW)**
Business and accounting:
- `odoo_mcp_v2.py` - Enhanced Odoo integration
- `accounting_mcp.py` - Accounting operations (NEW)
- `invoice_mcp.py` - Invoice generation (NEW)

---

## 🔄 Migration Plan

### **Phase 1: Parallel Running (CURRENT)**
- Old servers: Running ✅
- New servers: Being added
- Both work independently

### **Phase 2: Testing**
- Test new servers in isolation
- Compare with old servers
- No changes to production

### **Phase 3: Optional Migration**
- If new server is better → switch
- If old server is fine → keep using
- Your choice!

---

## 🛡️ Safety Rules

1. **NEVER** delete files from root level
2. **ALWAYS** test in subfolders first
3. **KEEP** backup folder intact
4. **TEST** before switching to new servers

---

## 📋 Current Status

| Folder | Status | Files |
|--------|--------|-------|
| Root | ✅ Working | 10 servers |
| communication/ | 🆕 Empty | Ready for new |
| social_media/ | 🆕 Empty | Ready for new |
| business/ | 🆕 Empty | Ready for new |

---

**Last Updated:** 2026-03-28  
**Backup Location:** `backup/mcp_servers_backup/`
