#!/usr/bin/env python3
"""
Skill: CEO Weekly Briefing
Generates comprehensive weekly CEO report for AI Employee System

Collects data from:
- Gmail MCP (emails sent/received)
- WhatsApp MCP (messages sent)
- Facebook MCP (posts created)
- Instagram MCP (posts created)
- Accounting Skill (income/expenses)
- System logs (errors, health status)
- Pending approvals (inbox folder)

Generates markdown report saved to: AI_Employee_Vault/Reports/ceo_weekly_report_YYYY-MM-DD.md
"""

import os
import sys
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class CEOWeeklyBriefingSkill:
    """
    CEO Weekly Briefing Skill
    Generates comprehensive weekly report for Gold Tier AI Employee System
    """

    def __init__(self, vault_path: str = None):
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent

        self.reports_folder = self.vault_path / 'AI_Employee_Vault' / 'Reports'
        self.logs_folder = self.vault_path / 'logs'
        self.inbox_folder = self.vault_path / 'AI_Employee_Vault' / 'inbox'
        self.accounting_folder = self.vault_path / 'AI_Employee_Vault' / 'Accounting'

        # Create folders
        self.reports_folder.mkdir(parents=True, exist_ok=True)

        self.week_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        self.week_end = datetime.now().strftime('%Y-%m-%d')

    def _get_week_timestamp(self) -> str:
        """Get timestamp for this week's report"""
        return datetime.now().strftime('%Y-%m-%d')

    def _get_unique_filename(self, base_name: str) -> Path:
        """Generate unique filename if report already exists"""
        base_path = self.reports_folder / base_name
        if not base_path.exists():
            return base_path

        # Add timestamp to make unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name_parts = base_name.rsplit('.', 1)
        new_name = f"{name_parts[0]}_{timestamp}.{name_parts[1] if len(name_parts) > 1 else 'md'}"
        return self.reports_folder / new_name

    def collect_gmail_data(self) -> Dict[str, int]:
        """Collect Gmail MCP data"""
        data = {
            'emails_sent': 0,
            'emails_received': 0,
            'emails_pending': 0
        }

        # Check Gmail watcher log
        gmail_log = self.vault_path / 'gmail_watcher.log'
        if gmail_log.exists():
            try:
                with open(gmail_log, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    data['emails_received'] = len(re.findall(r'Processing email', content, re.IGNORECASE))
            except Exception as e:
                pass

        # Check MCP email status
        mcp_status = self.vault_path / 'mcp_email_status.json'
        if mcp_status.exists():
            try:
                with open(mcp_status, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                    data['emails_sent'] = status.get('emails_sent', 0)
                    data['emails_pending'] = status.get('emails_pending', 0)
            except Exception:
                pass

        # Check MCP email server log
        email_log = self.vault_path / 'email_server.log'
        if email_log.exists():
            try:
                with open(email_log, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    sent_count = len(re.findall(r'Email sent', content, re.IGNORECASE))
                    if sent_count > data['emails_sent']:
                        data['emails_sent'] = sent_count
            except Exception:
                pass

        return data

    def collect_whatsapp_data(self) -> Dict[str, int]:
        """Collect WhatsApp MCP data"""
        data = {
            'messages_sent': 0,
            'messages_received': 0
        }

        # Check WhatsApp session
        whatsapp_session = self.vault_path / 'whatsapp_session.json'
        if whatsapp_session.exists():
            try:
                with open(whatsapp_session, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    data['messages_sent'] = session.get('messages_sent', 0)
            except Exception:
                pass

        # Check WhatsApp watcher log
        whatsapp_log = self.vault_path / 'logs' / 'whatsapp_watcher.log'
        if whatsapp_log.exists():
            try:
                with open(whatsapp_log, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    data['messages_received'] = len(re.findall(r'message', content, re.IGNORECASE))
            except Exception:
                pass

        return data

    def collect_facebook_data(self) -> Dict[str, int]:
        """Collect Facebook MCP data"""
        data = {
            'posts_created': 0,
            'comments': 0,
            'likes': 0
        }

        # Check Facebook watcher log
        fb_log = self.vault_path / 'logs' / 'facebook_watcher.log'
        if fb_log.exists():
            try:
                with open(fb_log, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    data['posts_created'] = len(re.findall(r'post', content, re.IGNORECASE))
            except Exception:
                pass

        # Check unified social MCP log
        social_log = self.vault_path / 'logs' / 'unified_social_mcp.log'
        if social_log.exists():
            try:
                with open(social_log, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Count Facebook-related activities
                    fb_mentions = len(re.findall(r'facebook|Facebook', content))
                    if fb_mentions > data['posts_created']:
                        data['posts_created'] = fb_mentions
            except Exception:
                pass

        return data

    def collect_instagram_data(self) -> Dict[str, int]:
        """Collect Instagram MCP data"""
        data = {
            'posts_created': 0,
            'comments': 0,
            'likes': 0
        }

        # Check unified social MCP log for Instagram
        social_log = self.vault_path / 'logs' / 'unified_social_mcp.log'
        if social_log.exists():
            try:
                with open(social_log, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Count Instagram-related activities
                    data['posts_created'] = len(re.findall(r'instagram|Instagram', content))
            except Exception:
                pass

        return data

    def collect_accounting_data(self) -> Dict[str, float]:
        """Collect accounting data from Accounting Skill"""
        data = {
            'income': 0.0,
            'expenses': 0.0,
            'balance': 0.0
        }

        try:
            # Import accounting skill
            sys.path.insert(0, str(self.vault_path / 'skills'))
            from skill_accounting import AccountingSkill

            skill = AccountingSkill(str(self.vault_path))
            summary = skill.get_summary()

            data['income'] = summary.get('total_income', 0.0)
            data['expenses'] = summary.get('total_expenses', 0.0)
            data['balance'] = summary.get('balance', 0.0)
        except Exception as e:
            pass

        return data

    def collect_pending_approvals(self) -> List[Dict[str, str]]:
        """Collect pending approvals from inbox folder"""
        approvals = []

        if not self.inbox_folder.exists():
            return approvals

        try:
            for item in self.inbox_folder.iterdir():
                if item.is_file():
                    approvals.append({
                        'file': item.name,
                        'date': datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d'),
                        'type': 'approval'
                    })
        except Exception:
            pass

        return approvals

    def collect_system_health(self) -> Dict[str, Any]:
        """Collect system health data from logs"""
        health = {
            'errors': 0,
            'warnings': 0,
            'recovery_actions': 0,
            'services_running': 0,
            'services_failed': 0
        }

        # Scan all log files
        log_files = list(self.logs_folder.glob('*.log'))

        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    health['errors'] += len(re.findall(r'ERROR|error|Error', content))
                    health['warnings'] += len(re.findall(r'WARN|warning|Warning', content))
                    health['recovery_actions'] += len(re.findall(r'recover|Recover', content))
            except Exception:
                pass

        # Check orchestrator state
        orchestrator_state = self.vault_path / 'master_orchestrator_state.json'
        if orchestrator_state.exists():
            try:
                with open(orchestrator_state, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    services = state.get('services', [])
                    health['services_running'] = len([s for s in services if s.get('status') == 'running'])
                    health['services_failed'] = len([s for s in services if s.get('status') == 'error'])
            except Exception:
                pass

        return health

    def collect_tasks_completed(self) -> List[Dict[str, str]]:
        """Collect completed tasks from Done folder"""
        tasks = []

        done_folder = self.vault_path / 'AI_Employee_Vault' / 'Done'
        if not done_folder.exists():
            return tasks

        try:
            for item in done_folder.iterdir():
                if item.is_file():
                    tasks.append({
                        'file': item.name,
                        'date': datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d'),
                        'type': 'completed_task'
                    })
        except Exception:
            pass

        return tasks

    def generate_report(self) -> str:
        """Generate complete CEO weekly briefing report"""

        # Collect all data
        gmail_data = self.collect_gmail_data()
        whatsapp_data = self.collect_whatsapp_data()
        facebook_data = self.collect_facebook_data()
        instagram_data = self.collect_instagram_data()
        accounting_data = self.collect_accounting_data()
        pending_approvals = self.collect_pending_approvals()
        system_health = self.collect_system_health()
        tasks_completed = self.collect_tasks_completed()

        # Calculate totals
        total_communications = (
            gmail_data['emails_sent'] +
            gmail_data['emails_received'] +
            whatsapp_data['messages_sent'] +
            whatsapp_data['messages_received']
        )

        total_social_posts = facebook_data['posts_created'] + instagram_data['posts_created']

        # Determine overall status
        if system_health['errors'] == 0 and accounting_data['balance'] >= 0:
            overall_status = "EXCELLENT"
            status_icon = "🟢"
        elif system_health['errors'] <= 5 and accounting_data['balance'] >= 0:
            overall_status = "GOOD"
            status_icon = "🟡"
        else:
            overall_status = "NEEDS ATTENTION"
            status_icon = "🔴"

        report = f"""# CEO Weekly Briefing

{status_icon} **Overall Status: {overall_status}**

**Report Period:** {self.week_start} to {self.week_end}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Prepared by:** AI Employee System - CEO Weekly Briefing Skill

---

## Executive Summary

This week, the AI Employee System processed **{total_communications} communications**, created **{total_social_posts} social media posts**, and maintained a financial balance of **${accounting_data['balance']:,.2f}**.

| Category | Metric | Count/Amount |
|----------|--------|--------------|
| Communications | Total | {total_communications} |
| Social Media | Posts | {total_social_posts} |
| Financial | Balance | ${accounting_data['balance']:,.2f} |
| Tasks | Completed | {len(tasks_completed)} |
| System | Errors | {system_health['errors']} |

---

## Summary

The AI Employee System operated at **{overall_status.lower()}** capacity this week.

**Key Achievements:**
- Processed {gmail_data['emails_received']} incoming emails
- Sent {gmail_data['emails_sent']} outgoing emails
- Created {facebook_data['posts_created']} Facebook posts
- Created {instagram_data['posts_created']} Instagram posts
- Generated ${accounting_data['income']:,.2f} in income

**Areas Requiring Attention:**
"""

        # Add attention items based on data
        attention_items = []
        if system_health['errors'] > 0:
            attention_items.append(f"- {system_health['errors']} system errors detected")
        if len(pending_approvals) > 0:
            attention_items.append(f"- {len(pending_approvals)} items pending approval")
        if accounting_data['balance'] < 0:
            attention_items.append(f"- Negative cash balance: ${accounting_data['balance']:,.2f}")
        if gmail_data['emails_pending'] > 0:
            attention_items.append(f"- {gmail_data['emails_pending']} emails pending response")

        if attention_items:
            for item in attention_items:
                report += f"{item}\n"
        else:
            report += "- No critical issues identified\n"

        report += f"""
---

## Tasks Completed

**Total:** {len(tasks_completed)} tasks

"""

        if tasks_completed:
            report += "| Date | Task |\n|------|------|\n"
            for task in tasks_completed[:10]:
                report += f"| {task['date']} | {task['file']} |\n"
            if len(tasks_completed) > 10:
                report += f"| ... | and {len(tasks_completed) - 10} more |\n"
        else:
            report += "*No tasks recorded in Done folder this week.*\n"

        report += f"""
---

## Communications

### Gmail
| Metric | Count |
|--------|-------|
| Emails Sent | {gmail_data['emails_sent']} |
| Emails Received | {gmail_data['emails_received']} |
| Emails Pending | {gmail_data['emails_pending']} |

### WhatsApp
| Metric | Count |
|--------|-------|
| Messages Sent | {whatsapp_data['messages_sent']} |
| Messages Received | {whatsapp_data['messages_received']} |

---

## Social Media

### Facebook
| Metric | Count |
|--------|-------|
| Posts Created | {facebook_data['posts_created']} |
| Comments | {facebook_data['comments']} |
| Likes | {facebook_data['likes']} |

### Instagram
| Metric | Count |
|--------|-------|
| Posts Created | {instagram_data['posts_created']} |
| Comments | {instagram_data['comments']} |
| Likes | {instagram_data['likes']} |

---

## Pending Approvals

**Total:** {len(pending_approvals)} items

"""

        if pending_approvals:
            report += "| Date | Item | Status |\n|------|------|--------|\n"
            for approval in pending_approvals[:10]:
                report += f"| {approval['date']} | {approval['file']} | Pending |\n"
        else:
            report += "*No pending approvals.*\n"

        report += f"""
---

## Financial Summary

| Metric | Amount |
|--------|--------|
| Total Income | ${accounting_data['income']:,.2f} |
| Total Expenses | ${accounting_data['expenses']:,.2f} |
| **Net Balance** | **${accounting_data['balance']:,.2f}** |

---

## System Health

| Metric | Count | Status |
|--------|-------|--------|
| Errors | {system_health['errors']} | {'⚠️' if system_health['errors'] > 0 else '✅'} |
| Warnings | {system_health['warnings']} | {'⚠️' if system_health['warnings'] > 0 else '✅'} |
| Recovery Actions | {system_health['recovery_actions']} | ℹ️ |
| Services Running | {system_health['services_running']} | ✅ |
| Services Failed | {system_health['services_failed']} | {'⚠️' if system_health['services_failed'] > 0 else '✅'} |

"""

        if system_health['errors'] > 5:
            report += """
**⚠️ System Alert:** High error count detected. Review logs for details.

"""

        report += f"""---

## Recommendations

Based on this week's performance:

1. **Communications:** {"Maintain current response times." if gmail_data['emails_pending'] < 5 else "Reduce email response time."}
2. **Social Media:** {"Increase posting frequency." if total_social_posts < 5 else "Continue current content strategy."}
3. **Financial:** {"Focus on revenue generation." if accounting_data['income'] == 0 else "Maintain current financial practices."}
4. **System:** {"Review and address system errors." if system_health['errors'] > 0 else "System operating normally."}

---

## Next Week Priorities

- [ ] Review and approve pending items
- [ ] Address system errors and warnings
- [ ] Continue social media engagement
- [ ] Monitor financial performance
- [ ] Complete outstanding tasks

---

*This report was automatically generated by the AI Employee System.*  
*For questions or clarifications, contact the System Administrator.*

**Confidentiality:** This document contains sensitive business information.  
**Distribution:** CEO, Executive Team Only
"""

        return report

    def save_report(self, output_path: str = None) -> str:
        """Save report to file"""
        report_content = self.generate_report()

        if output_path is None:
            base_filename = f"ceo_weekly_report_{self._get_week_timestamp()}.md"
            output_path = self._get_unique_filename(base_filename)
        else:
            output_path = Path(output_path)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return str(output_path)


# MCP-compatible functions
_briefing_skill = None


def get_skill() -> CEOWeeklyBriefingSkill:
    """Get or create briefing skill instance"""
    global _briefing_skill
    if _briefing_skill is None:
        _briefing_skill = CEOWeeklyBriefingSkill()
    return _briefing_skill


def generate_ceo_weekly_briefing(output_path: str = None) -> str:
    """
    Generate CEO weekly briefing report

    Args:
        output_path: Optional custom output path

    Returns:
        Path to generated report
    """
    skill = get_skill()
    return skill.save_report(output_path)


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='CEO Weekly Briefing Skill')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--vault', type=str, help='Vault path')
    args = parser.parse_args()

    skill = CEOWeeklyBriefingSkill(args.vault)
    report_path = skill.save_report(args.output)

    print(f"\n[CEO BRIEFING] Report generated: {report_path}")
    print(f"\nPreview:")
    print("=" * 60)

    # Show first 30 lines as preview
    with open(report_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 30:
                print("...")
                break
            # Remove emojis for console compatibility
            line_clean = line.replace('🟢', '[OK]').replace('🟡', '[WARN]').replace('🔴', '[ERROR]')
            line_clean = line_clean.replace('⚠️', '[!]').replace('✅', '[OK]').replace('ℹ️', '[i]')
            print(line_clean.rstrip())
