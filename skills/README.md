# Skills Directory

This directory contains agent skills for automating tasks with external systems.

---

## Available Skills

### 1. Accounting Manager Skill (`skill_accounting.py`)

Manages business accounting records - tracks income and expenses, generates weekly summaries and CEO reports.

**Usage:**
```bash
# Log income
python skills/skill_accounting.py income 5000 "Client payment" --category "Sales"

# Log expense
python skills/skill_accounting.py expense 1500 "Office rent" --category "Office"

# View monthly summary
python skills/skill_accounting.py summary

# View weekly summary
python skills/skill_accounting.py weekly-summary

# Generate weekly report
python skills/skill_accounting.py weekly-summary --report

# Generate CEO weekly briefing
python skills/skill_accounting.py ceo-report

# List entries
python skills/skill_accounting.py list

# Export to JSON
python skills/skill_accounting.py export
```

**What it does:**
- Tracks income and expenses with categories
- Maintains monthly accounting records
- Generates weekly summaries with insights
- Creates CEO weekly briefing reports
- Exports data to JSON

**Output Files:**
- `AI_Employee_Vault/Accounting/YYYY-MM.md` - Monthly records
- `AI_Employee_Vault/Accounting/weekly_summary_*.md` - Weekly reports
- `AI_Employee_Vault/Accounting/CEO_Weekly_Briefing_*.md` - CEO briefings

---

### 2. CEO Weekly Briefing Skill (`skill_ceo_weekly_briefing.py`)

Generates comprehensive weekly CEO reports by collecting data from all MCP servers.

**Usage:**
```bash
# Generate CEO weekly briefing
python skills/skill_ceo_weekly_briefing.py

# Generate with custom output
python skills/skill_ceo_weekly_briefing.py --output "C:/path/to/report.md"
```

**What it does:**
- Collects data from Gmail, WhatsApp, Facebook, Instagram MCPs
- Reads system logs for health status
- Gets accounting data from Accounting Skill
- Analyzes pending approvals and completed tasks
- Generates executive summary report

**Data Sources:**
| Source | Data Collected |
|--------|----------------|
| Gmail MCP | Emails sent, received, pending |
| WhatsApp MCP | Messages sent, received |
| Facebook MCP | Posts created, comments, likes |
| Instagram MCP | Posts created, comments, likes |
| Accounting Skill | Income, expenses, balance |
| System Logs | Errors, warnings, recovery actions |

**Output:**
```markdown
# CEO Weekly Briefing

🟢 **Overall Status: EXCELLENT**

**Report Period:** 2026-03-22 to 2026-03-29

## Executive Summary
- Communications: 57 total
- Social Media: 4 posts
- Financial: $3,500.00 balance
- System: 53 errors

## Tasks Completed
## Communications
## Social Media
## Pending Approvals
## Financial Summary
## System Health
## Recommendations
```

---

### 3. Error Recovery Skill (`skill_error_recovery.py`)

Handles failures and recovers tasks automatically.

**Usage:**
```bash
# Log an error
python skills/skill_error_recovery.py log "task_name" "task_id" "Error message"

# Get error summary
python skills/skill_error_recovery.py summary

# List pending errors
python skills/skill_error_recovery.py pending

# Clear old errors
python skills/skill_error_recovery.py clear --days 30
```

**What it does:**
- Monitors MCP tasks and executions
- Detects failed tasks
- Captures error details (task name, timestamp, error message)
- Logs errors to `logs/errors.log` (append mode only)
- Moves failed task data to `AI_Employee_Vault/errors/`
- Retry logic (wait 5 minutes, retry once)
- Tracks status: RECOVERED or FAILED_FINAL
- Max retry: 1 (avoids infinite loops)

**Logging Format:**
```
[Timestamp] | Task | Status | Error Message
```

**Example Log:**
```
[2026-03-29T14:00:00] | send_email | PENDING | Connection timeout
[2026-03-29T14:05:00] | send_email | RECOVERED | Task recovered after 1 retry
[2026-03-29T15:00:00] | post_facebook | FAILED_FINAL | API rate limit exceeded
```

---

### 4. Autonomous Task Loop Skill (`skill_autonomous_task_loop.py`)

Executes tasks autonomously using plan → execute → verify loop.

**Usage:**
```bash
# Create a new task
python skills/skill_autonomous_task_loop.py create "Task Name" "Description" "Objective" --type log_income --risk low

# Execute a task
python skills/skill_autonomous_task_loop.py execute <task_id>

# Get task status
python skills/skill_autonomous_task_loop.py status <task_id>

# List pending tasks
python skills/skill_autonomous_task_loop.py pending

# Approve a high-risk task
python skills/skill_autonomous_task_loop.py approve <task_id>
```

**What it does:**
- Detects new tasks from scheduler or task queue
- Analyzes task objectives and identifies required tools
- Creates step-by-step plans (saved to `AI_Employee_Vault/Plans/{task_id}.md`)
- Executes steps using MCP tools
- Verifies each step's success
- Calls error_recovery on failures
- Moves completed tasks to `AI_Employee_Vault/Done/`
- Max iterations limit (10 steps) to prevent infinite loops
- Human approval for risky tasks (high risk level)
- Memory of past task results for optimization
- Skips already completed steps
- Reports completed tasks to CEO briefing

**Task Types:**
| Type | Description |
|------|-------------|
| `file_copy` | Copy files |
| `file_move` | Move files |
| `send_email` | Send emails |
| `post_facebook` | Post to Facebook |
| `post_instagram` | Post to Instagram |
| `log_income` | Log accounting income |
| `log_expense` | Log accounting expense |

**Risk Levels:**
| Level | Behavior |
|-------|----------|
| `low` | No approval needed |
| `medium` | Notify only |
| `high` | Approval required before execution |

**Example Task Flow:**
```
1. CREATE task: "Post to Facebook"
   - Type: post_facebook
   - Risk: low
   - Generated ID: post_facebook_20260329_120000_abc123

2. ANALYZE and PLAN
   - Step 1: Prepare post content
   - Step 2: Post to Facebook
   - Step 3: Verify post published

3. EXECUTE
   - Run each step using MCP tools
   - Verify each step

4. COMPLETE
   - Move to Done folder
   - Report to CEO briefing
```

**Output Files:**
- `AI_Employee_Vault/Plans/{task_id}.md` - Task plan
- `AI_Employee_Vault/Done/{task_id}.json` - Completed task record
- `AI_Employee_Vault/Memory/task_memory.json` - Task memory for optimization

---

### 5. Social Summary Skill (`skill_social_summary.py`)

Generates and stores summaries of social media posts.

**Usage:**
```bash
# Log a Facebook post
python skills/social_summary.py log facebook "Hello World! #Business"

# Log an Instagram post
python skills/social_summary.py log instagram "Beautiful sunset 🌅 #photography"

# Get statistics
python skills/social_summary.py stats

# Get recent posts
python skills/social_summary.py recent --limit 10
```

**What it does:**
- Receives post data from MCP servers (platform, content, timestamp)
- Validates input (platform must be facebook/instagram, content not empty, timestamp exists)
- Generates summary entry with content preview, character count, hashtag count, mention count
- Saves to `AI_Employee_Vault/Reports/social.log.md` (append mode only)
- Prevents duplicate entries (same content + timestamp)
- Logs success to `logs/system.log`
- Logs errors to `logs/errors.log`
- Calls error_recovery on failures (max 1 retry)

**Trigger:**
- Run after a successful post on Instagram or Facebook

**Integration Example:**
```python
# In facebook_mcp.py or instagram_mcp.py
from skills.skill_social_summary import log_social_post

# After successful post
result = post_to_facebook(content)
if result['success']:
    log_social_post(
        platform='facebook',
        content=content,
        timestamp=datetime.now().isoformat()
    )
```

**Output File Format:**
```markdown
# Social Media Posts Log

## 📘 Facebook Post

**Post ID:** 840b8972a8e66a3e
**Date:** 2026-03-29T17:54:53.596684
**Character Count:** 56
**Hashtags:** 2
**Mentions:** 0

### Content Preview

Hello World! This is our first post. #GoldTier #Business

### Full Content

```
Hello World! This is our first post. #GoldTier #Business
```

---

## 📷 Instagram Post

**Post ID:** d7eeb59be9835a72
**Date:** 2026-03-29T17:55:12.020981
**Character Count:** 59
**Hashtags:** 2
**Mentions:** 1

### Content Preview

Beautiful sunset 🌅 #photography #nature @photographer

### Full Content

```
Beautiful sunset 🌅 #photography #nature @photographer
```

---
```

---

### 6. Odoo Invoice Skill (`odoo_invoice_skill.py`)

Creates invoices in Odoo ERP automatically.

**Usage:**
```bash
python skills/odoo_invoice_skill.py "customer@email.com" "amount" "description"
```

**Example:**
```bash
python skills/odoo_invoice_skill.py "john@example.com" "1500.00" "Web Development - March 2026"
```

---

### 6. Odoo Orders Skill (`odoo_orders_skill.py`)

Fetches customer orders from Odoo ERP and generates reports.

**Usage:**
```bash
python skills/odoo_orders_skill.py "customer@email.com"
```

---

### 7. Facebook Skill (`facebook_skill.py`)

Facebook automation skill for posting and monitoring.

---

### 8. Ralph Loop Runner (`ralph_loop_runner.py`)

Autonomous reasoning loop for multi-step task execution.

---

## Prerequisites

### For All Skills

1. **Python 3.8+** installed
2. **Required packages** installed:
   ```bash
   pip install requests python-dotenv
   ```

3. **Environment variables** set (or use `.env` file):
   ```bash
   source .env
   ```

### For Odoo Skills Specifically

1. **Odoo running** in Docker:
   ```bash
   docker ps | grep odoo
   ```

2. **Database created** at http://localhost:8069

3. **Customer exists** in Odoo Contacts

---

## Creating New Skills

To create a new skill:

1. Create a new `.py` file in this directory
2. Follow the pattern:
   - Check prerequisites
   - Validate inputs
   - Execute main logic
   - Update Dashboard.md
   - Save state to `Plans/`

3. Update this README with the new skill

---

## State Files

All skills save their state to the `Plans/` directory:

- `plans/odoo_invoice.json` - Invoice creation history
- `plans/orders_{customer}.md` - Order reports by customer
- `AI_Employee_Vault/Accounting/*.md` - Accounting records
- `AI_Employee_Vault/Reports/*.md` - CEO briefings

---

## Dashboard Integration

Skills automatically update `Dashboard.md` with their activities:

- **## Invoices** - Invoice creation records
- **## Order History** - Order lookup records
- **## Accounting** - Financial summaries
- **## Reports** - CEO briefings

---

## Quick Reference

| Skill | Command | Output |
|-------|---------|--------|
| Log Income | `python skills/skill_accounting.py income 5000 "Desc"` | Accounting record |
| Log Expense | `python skills/skill_accounting.py expense 1500 "Desc"` | Accounting record |
| Weekly Summary | `python skills/skill_accounting.py weekly-summary` | Weekly report |
| CEO Report | `python skills/skill_ceo_weekly_briefing.py` | CEO briefing |
| Log Error | `python skills/skill_error_recovery.py log "name" "id" "msg"` | Error record |
| Create Task | `python skills/skill_autonomous_task_loop.py create "name" "desc" "obj"` | Task created |
| Execute Task | `python skills/skill_autonomous_task_loop.py execute <task_id>` | Task result |
| Log Social Post | `python skills/social_summary.py log facebook "content"` | Summary saved |
| Social Stats | `python skills/social_summary.py stats` | Posting statistics |
| Create Invoice | `python skills/odoo_invoice_skill.py "email" "amt" "desc"` | Invoice ID |
| Get Orders | `python skills/odoo_orders_skill.py "email"` | Order report |

---

## Troubleshooting

### "MCP server not found"
Ensure the required MCP server exists in the project root.

### "Cannot connect to Odoo"
```bash
docker ps | grep odoo
# If not running:
cd odoo-docker && docker-compose up -d
```

### "Customer not found"
Create the customer in Odoo first:
1. Go to http://localhost:8069
2. Navigate to Contacts/Customers
3. Create new contact with the email

### "Authentication failed"
Check your credentials in `.env` or `odoo_mcp.env`.

### "No data in report"
Ensure MCP servers have been running and generating logs.

---

## MCP Agent Invocation

If your MCP client supports skill invocation:

```
/accounting-income 5000 "Client payment" --category "Sales"
/accounting-expense 1500 "Office rent" --category "Office"
/ceo-weekly-briefing
/odoo-invoice "customer@example.com" "1500.00" "Service"
/odoo-orders "customer@example.com"
```

---

## Support

For issues:
1. Check logs in `logs/` folder
2. Verify `.env` configuration
3. Test MCP servers individually
