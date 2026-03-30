# CEO Weekly Briefing Skill

**Location:** `skills/skill_ceo_weekly_briefing.py`  
**Reports Saved:** `AI_Employee_Vault/Reports/ceo_weekly_report_YYYY-MM-DD.md`

---

## Overview

The CEO Weekly Briefing Skill is an autonomous reporting agent that generates comprehensive weekly executive reports for your Gold Tier AI Employee System. It collects data from all MCP servers, analyzes performance, and creates professional markdown reports.

---

## Features

- **Multi-Source Data Collection** - Gathers data from all MCP servers
- **Automated Analysis** - Analyzes performance and identifies issues
- **Executive Summary** - High-level overview for quick decision-making
- **Detailed Sections** - Communications, Social Media, Financial, System Health
- **Smart Recommendations** - AI-generated action items based on data
- **Safe File Handling** - Never overwrites existing reports

---

## Data Sources

| Source | Data Collected |
|--------|----------------|
| **Gmail MCP** | Emails sent, received, pending |
| **WhatsApp MCP** | Messages sent, received |
| **Facebook MCP** | Posts created, comments, likes |
| **Instagram MCP** | Posts created, comments, likes |
| **Accounting Skill** | Income, expenses, balance |
| **System Logs** | Errors, warnings, recovery actions |
| **Inbox Folder** | Pending approvals |
| **Done Folder** | Completed tasks |

---

## Usage

### Command Line

```bash
# Generate CEO weekly briefing
python skills/skill_ceo_weekly_briefing.py

# Generate with custom output path
python skills/skill_ceo_weekly_briefing.py --output "C:/path/to/report.md"

# Generate with custom vault path
python skills/skill_ceo_weekly_briefing.py --vault "C:/Users/AA/Desktop/gold_tier"
```

### Python API

```python
from skills.skill_ceo_weekly_briefing import CEOWeeklyBriefingSkill, generate_ceo_weekly_briefing

# Quick generation
report_path = generate_ceo_weekly_briefing()
print(f"Report saved to: {report_path}")

# Custom instance
skill = CEOWeeklyBriefingSkill(vault_path="C:/Users/AA/Desktop/gold_tier")
report_path = skill.save_report()
```

### MCP Integration

```python
from skills.skill_ceo_weekly_briefing import generate_ceo_weekly_briefing

# Call from MCP server
report_path = generate_ceo_weekly_briefing()
```

---

## Report Format

```markdown
# CEO Weekly Briefing

🔴/🟡/🟢 **Overall Status: [STATUS]**

**Report Period:** YYYY-MM-DD to YYYY-MM-DD
**Generated:** YYYY-MM-DD HH:MM:SS

---

## Executive Summary
(Quick overview with key metrics table)

## Summary
(Key achievements and areas requiring attention)

## Tasks Completed
(List of completed tasks from Done folder)

## Communications
- Gmail (sent, received, pending)
- WhatsApp (sent, received)

## Social Media
- Facebook (posts, comments, likes)
- Instagram (posts, comments, likes)

## Pending Approvals
(Items in inbox folder)

## Financial Summary
(Income, expenses, balance from Accounting Skill)

## System Health
(Errors, warnings, recovery actions, services status)

## Recommendations
(Al-generated action items based on data)

## Next Week Priorities
(Checklist for upcoming week)
```

---

## Example Report

### Executive Summary Table

| Category | Metric | Count/Amount |
|----------|--------|--------------|
| Communications | Total | 57 |
| Social Media | Posts | 4 |
| Financial | Balance | $3,500.00 |
| Tasks | Completed | 0 |
| System | Errors | 53 |

### Status Indicators

| Status | Icon | Meaning |
|--------|------|---------|
| EXCELLENT | 🟢 | No errors, positive balance |
| GOOD | 🟡 | Minor issues, positive balance |
| NEEDS ATTENTION | 🔴 | Errors or negative balance |

---

## Safety Features

### File Safety
- **Never overwrites** existing reports
- **Auto-generates unique filename** with timestamp if file exists
- **Creates reports folder** if it doesn't exist

### Data Safety
- **Read-only access** to log files
- **Error handling** for all data sources
- **Graceful degradation** if source unavailable

### System Safety
- **No modifications** to MCP servers
- **No external API calls** (local data only)
- **No credentials** stored or transmitted

---

## Scheduling

### Weekly Automatic Generation

Add to your scheduler or cron:

```bash
# Windows Task Scheduler
# Run every Monday at 8:00 AM
python C:\Users\AA\Desktop\gold_tier\skills\skill_ceo_weekly_briefing.py

# Linux/Mac cron
# Run every Monday at 8:00 AM
0 8 * * 1 cd /path/to/gold_tier && python skills/skill_ceo_weekly_briefing.py
```

### Integration with Master Orchestrator

```python
# In master_orchestrator.py
from skills.skill_ceo_weekly_briefing import generate_ceo_weekly_briefing

# Run weekly audit (includes CEO briefing)
def run_weekly_audit():
    generate_ceo_weekly_briefing()
```

---

## Troubleshooting

### Issue: Report shows 0 for all metrics
**Solution:** Ensure MCP servers have been running and generating logs

### Issue: File not found error
**Solution:** Check that vault path is correct and folders exist

### Issue: Console encoding errors
**Solution:** Skill automatically handles emoji encoding for Windows console

### Issue: Accounting data not showing
**Solution:** Ensure `skill_accounting.py` exists and has data entries

---

## Integration with Other Skills

### Accounting Manager Skill

The CEO Briefing Skill automatically pulls financial data from the Accounting Manager Skill:

```python
# Both skills work together
from skills.skill_accounting import AccountingSkill
from skills.skill_ceo_weekly_briefing import CEOWeeklyBriefingSkill

# Accounting data is automatically included in CEO report
```

### Weekly Audit System

The CEO Briefing complements the Weekly Audit System:

| Feature | Weekly Audit | CEO Briefing |
|---------|--------------|--------------|
| Focus | Financial + Social | Comprehensive |
| Audience | CFO/Finance | CEO/Executive |
| Detail Level | Detailed | Executive Summary |
| Frequency | Weekly | Weekly |

---

## Customization

### Modify Report Sections

Edit the `generate_report()` method in `skill_ceo_weekly_briefing.py`:

```python
def generate_report(self) -> str:
    # Add custom sections
    custom_data = self.collect_custom_data()

    report = f"""
## Custom Section

{custom_data['info']}
"""
    return report
```

### Add New Data Sources

```python
def collect_custom_data(self) -> Dict:
    """Collect data from custom source"""
    data = {'info': 0}

    # Add your data source
    custom_log = self.vault_path / 'custom.log'
    if custom_log.exists():
        with open(custom_log, 'r') as f:
            data['info'] = len(f.readlines())

    return data
```

---

## Best Practices

1. **Run weekly** - Generate report same day each week
2. **Review with team** - Share with executive team
3. **Track trends** - Compare reports week-over-week
4. **Act on recommendations** - Complete suggested action items
5. **Archive reports** - Keep historical reports for analysis

---

## Report Distribution

### Email Distribution

```python
from skills.skill_ceo_weekly_briefing import generate_ceo_weekly_briefing
from skills.skill_email import send_email

# Generate report
report_path = generate_ceo_weekly_briefing()

# Email to CEO
send_email(
    to='ceo@company.com',
    subject=f'CEO Weekly Briefing - {datetime.now().strftime("%Y-%m-%d")}',
    body='Please find attached the weekly briefing.',
    attachments=[report_path]
)
```

### Save to Shared Drive

```python
import shutil

# Copy to shared drive
shutil.copy(report_path, 'D:/Shared/CEO_Reports/')
```

---

**Created for:** Gold Tier - Autonomous Employee System  
**Author:** AI Employee Vault  
**Last Updated:** 2026-03-29
