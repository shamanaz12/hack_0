# Accounting Manager Skill

**Location:** `skills/skill_accounting.py`  
**Vault Path:** `AI_Employee_Vault/Accounting/`

---

## Overview

The Accounting Manager Skill is an autonomous accounting agent that maintains monthly and weekly financial records for your Gold Tier business. It tracks income and expenses, generates summaries, and provides financial insights.

---

## Features

- **Log Income** - Record income entries with date, amount, description, and category
- **Log Expenses** - Record expense entries with date, amount, description, and category
- **Monthly Summary** - Get current month financial summary
- **Weekly Summary** - Get last 7 days financial summary with insights
- **Weekly Report** - Generate formatted markdown reports
- **Export to JSON** - Export data for external analysis
- **Auto-categorization** - Track expenses by category

---

## File Structure

```
AI_Employee_Vault/Accounting/
├── 2026-03.md                              # Current month records
├── weekly_summary_2026-03-22_to_2026-03-29.md  # Weekly reports
└── 2026-03.json                            # JSON exports
```

---

## Usage

### Command Line Interface

```bash
# View monthly summary
python skills/skill_accounting.py summary

# View weekly summary
python skills/skill_accounting.py weekly-summary

# Generate weekly report file
python skills/skill_accounting.py weekly-summary --report

# Log income
python skills/skill_accounting.py income <amount> "<description>" --category "<category>"

# Log expense
python skills/skill_accounting.py expense <amount> "<description>" --category "<category>"

# List all entries
python skills/skill_accounting.py list

# List only income entries
python skills/skill_accounting.py list --type income

# List only expense entries
python skills/skill_accounting.py list --type expense

# Export to JSON
python skills/skill_accounting.py export
```

### Examples

```bash
# Log income of $5000 from client payment
python skills/skill_accounting.py income 5000 "Client payment - Web development project" --category "Sales"

# Log expense of $1500 for office rent
python skills/skill_accounting.py expense 1500 "Office rent payment" --category "Office"

# Get weekly summary with full report
python skills/skill_accounting.py weekly-summary --report
```

---

## Python API

```python
from skills.skill_accounting import AccountingSkill

# Initialize skill
skill = AccountingSkill(vault_path="C:/Users/AA/Desktop/gold_tier")

# Log income
result = skill.add_income(
    amount=5000.0,
    description="Client payment",
    date="2026-03-29",  # Optional, defaults to today
    category="Sales",
    notes="Project completed"
)

# Log expense
result = skill.add_expense(
    amount=1500.0,
    description="Office rent",
    date="2026-03-29",
    category="Office"
)

# Get monthly summary
summary = skill.get_summary()
print(f"Balance: ${summary['balance']:,.2f}")

# Get weekly summary
weekly = skill.get_weekly_summary()
print(f"Weekly Balance: ${weekly['weekly_balance']:,.2f}")
print("Insights:")
for insight in weekly['insights']:
    print(f"  - {insight}")

# Generate weekly report
report_path = skill.generate_weekly_report()
print(f"Report saved to: {report_path}")
```

---

## Weekly Summary Output

The weekly summary includes:

| Section | Description |
|---------|-------------|
| **Week at a Glance** | Total income, expenses, balance, transaction count |
| **Month to Date** | Cumulative monthly totals |
| **Top Transactions** | Highest income and expense entries |
| **Financial Insights** | AI-generated insights about financial health |
| **Recent Transactions** | Last 5 income and expense entries |

### Sample Insights

- "Positive cash flow this week - good financial health"
- "Negative cash flow this week - review expenses"
- "Expenses are high relative to income - consider cost reduction"
- "No income recorded this week - follow up on receivables"
- "Top expense category: Office ($1,500.00)"

---

## MCP Integration

The skill can be called from MCP servers:

```python
from skills.skill_accounting import log_income, log_expense, get_accounting_summary

# Log income via MCP
result = log_income(5000, "Client payment", category="Sales")

# Log expense via MCP
result = log_expense(1500, "Office rent", category="Office")

# Get summary via MCP
summary = get_accounting_summary()
```

---

## Data Format

### Monthly Records (Markdown)

```markdown
# Accounting Records - 2026-03

## Summary
| Metric | Amount |
|--------|--------|
| Total Income | $5,000.00 |
| Total Expenses | $1,500.00 |
| Balance | $3,500.00 |

## Income
| Date | Amount | Description | Category | Notes |
|------|--------|-------------|----------|-------|
| 2026-03-29 | $5,000.00 | Client payment | Sales | |

## Expenses
| Date | Amount | Description | Category | Notes |
|------|--------|-------------|----------|-------|
| 2026-03-29 | $1,500.00 | Office rent | Office | |
```

---

## Best Practices

1. **Log transactions daily** - Keep records up to date
2. **Use categories** - Helps with expense analysis
3. **Add notes** - Provide context for unusual transactions
4. **Review weekly** - Use weekly summary to track financial health
5. **Export monthly** - Keep JSON backups for external analysis

---

## Integration with Weekly Audit

The Accounting Manager integrates with the Weekly Audit System:

```bash
# Run weekly audit (includes accounting data)
python weekly_audit.py
```

The audit system pulls data from:
- `AI_Employee_Vault/Accounting/*.md` - Accounting records
- Odoo (if configured) - Invoice data
- Facebook/Instagram - Social media metrics
- Gmail - Email communication summary

---

## Troubleshooting

### Issue: Unicode encoding errors
**Solution:** The skill uses ASCII-safe characters for Windows console compatibility

### Issue: File not found
**Solution:** Ensure `AI_Employee_Vault/Accounting/` folder exists

### Issue: Date parsing errors
**Solution:** Use YYYY-MM-DD format for all dates

---

**Created for:** Gold Tier - Autonomous Employee System  
**Author:** AI Employee Vault  
**Last Updated:** 2026-03-29
