#!/usr/bin/env python3
"""
Skill: Accounting Manager
Maintains monthly accounting records in AI Employee Vault

Features:
- Log income entries with date, amount, description
- Log expense entries with date, amount, description
- Generate monthly summary reports
- Track running balance
- Store records in: AI_Employee_Vault/Accounting/current_month.md
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class AccountingEntry:
    """Single accounting entry"""
    date: str
    type: str  # "income" or "expense"
    amount: float
    description: str
    category: str = ""
    notes: str = ""


class AccountingSkill:
    """
    Accounting Manager Skill
    Maintains monthly accounting records for Gold Tier business
    """

    def __init__(self, vault_path: str = None):
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent

        self.accounting_folder = self.vault_path / 'AI_Employee_Vault' / 'Accounting'
        self.accounting_folder.mkdir(parents=True, exist_ok=True)

        self.current_month_file = self.accounting_folder / 'current_month.md'
        self.entries: List[AccountingEntry] = []
        self.current_month = datetime.now().strftime('%Y-%m')

        self.load_entries()

    def get_current_month_filename(self) -> Path:
        """Get filename for current month"""
        month_str = datetime.now().strftime('%Y-%m')
        return self.accounting_folder / f'{month_str}.md'

    def load_entries(self):
        """Load existing entries from current month file"""
        self.current_month_file = self.get_current_month_filename()

        if not self.current_month_file.exists():
            self.entries = []
            return

        try:
            with open(self.current_month_file, 'r', encoding='utf-8') as f:
                content = f.read()

            self.entries = []
            current_type = None

            for line in content.split('\n'):
                line = line.strip()

                if line.startswith('### Income') or line.startswith('## Income'):
                    current_type = 'income'
                elif line.startswith('### Expenses') or line.startswith('## Expenses'):
                    current_type = 'expense'
                elif line.startswith('|') and current_type and '|' in line[1:]:
                    parts = line.split('|')
                    if len(parts) >= 5:
                        try:
                            date_str = parts[1].strip()
                            amount_str = parts[2].strip().replace('$', '').replace(',', '')
                            description = parts[3].strip()

                            if date_str and date_str != 'Date' and amount_str:
                                entry = AccountingEntry(
                                    date=date_str,
                                    type=current_type,
                                    amount=float(amount_str),
                                    description=description
                                )
                                self.entries.append(entry)
                        except (ValueError, IndexError):
                            pass
        except Exception as e:
            print(f"[WARN] Error loading entries: {e}")
            self.entries = []

    def add_income(self, amount: float, description: str, date: str = None, category: str = "", notes: str = "") -> Dict:
        """
        Add income entry

        Args:
            amount: Income amount
            description: Description of income source
            date: Date (defaults to today)
            category: Category (e.g., "Sales", "Service", "Investment")
            notes: Additional notes

        Returns:
            Dict with status and entry details
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        entry = AccountingEntry(
            date=date,
            type='income',
            amount=amount,
            description=description,
            category=category,
            notes=notes
        )

        self.entries.append(entry)
        self.save()

        return {
            'status': 'success',
            'message': f'Income of ${amount:,.2f} recorded: {description}',
            'entry': asdict(entry)
        }

    def add_expense(self, amount: float, description: str, date: str = None, category: str = "", notes: str = "") -> Dict:
        """
        Add expense entry

        Args:
            amount: Expense amount
            description: Description of expense
            date: Date (defaults to today)
            category: Category (e.g., "Office", "Software", "Marketing")
            notes: Additional notes

        Returns:
            Dict with status and entry details
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        entry = AccountingEntry(
            date=date,
            type='expense',
            amount=amount,
            description=description,
            category=category,
            notes=notes
        )

        self.entries.append(entry)
        self.save()

        return {
            'status': 'success',
            'message': f'Expense of ${amount:,.2f} recorded: {description}',
            'entry': asdict(entry)
        }

    def get_summary(self) -> Dict:
        """Get current month summary"""
        total_income = sum(e.amount for e in self.entries if e.type == 'income')
        total_expenses = sum(e.amount for e in self.entries if e.type == 'expense')
        balance = total_income - total_expenses

        return {
            'month': self.current_month,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': balance,
            'entry_count': len(self.entries),
            'income_count': len([e for e in self.entries if e.type == 'income']),
            'expense_count': len([e for e in self.entries if e.type == 'expense'])
        }

    def get_weekly_summary(self) -> Dict:
        """
        Get weekly accounting summary
        Returns summary for the last 7 days
        """
        from datetime import timedelta
        
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        weekly_entries = [
            e for e in self.entries 
            if datetime.strptime(e.date, '%Y-%m-%d').date() >= week_ago.date()
        ]
        
        weekly_income = sum(e.amount for e in weekly_entries if e.type == 'income')
        weekly_expenses = sum(e.amount for e in weekly_entries if e.type == 'expense')
        weekly_balance = weekly_income - weekly_expenses
        
        # Get top income sources
        income_entries = [e for e in weekly_entries if e.type == 'income']
        expense_entries = [e for e in weekly_entries if e.type == 'expense']
        
        # Generate insights
        insights = []
        if weekly_balance > 0:
            insights.append("Positive cash flow this week - good financial health")
        elif weekly_balance < 0:
            insights.append("Negative cash flow this week - review expenses")
        
        if weekly_expenses > weekly_income * 0.8:
            insights.append("Expenses are high relative to income - consider cost reduction")
        
        if len(income_entries) == 0:
            insights.append("No income recorded this week - follow up on receivables")
        
        # Top expense category
        if expense_entries:
            category_totals = {}
            for e in expense_entries:
                cat = e.category or 'Uncategorized'
                category_totals[cat] = category_totals.get(cat, 0) + e.amount
            top_category = max(category_totals.items(), key=lambda x: x[1])
            insights.append(f"Top expense category: {top_category[0]} (${top_category[1]:,.2f})")
        
        return {
            'period_start': week_ago.strftime('%Y-%m-%d'),
            'period_end': today.strftime('%Y-%m-%d'),
            'weekly_income': weekly_income,
            'weekly_expenses': weekly_expenses,
            'weekly_balance': weekly_balance,
            'income_transactions': len(income_entries),
            'expense_transactions': len(expense_entries),
            'insights': insights,
            'top_income': asdict(max(income_entries, key=lambda x: x.amount)) if income_entries else None,
            'top_expense': asdict(max(expense_entries, key=lambda x: x.amount)) if expense_entries else None
        }

    def generate_weekly_report(self, output_path: str = None) -> str:
        """
        Generate formatted weekly report markdown file
        """
        weekly = self.get_weekly_summary()
        month_summary = self.get_summary()
        
        if output_path is None:
            output_path = self.accounting_folder / f'weekly_summary_{weekly["period_start"]}_to_{weekly["period_end"]}.md'
        else:
            output_path = Path(output_path)
        
        report = f"""# Weekly Accounting Summary

**Period:** {weekly['period_start']} to {weekly['period_end']}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Week at a Glance

| Metric | Amount |
|--------|--------|
| Total Income | ${weekly['weekly_income']:,.2f} |
| Total Expenses | ${weekly['weekly_expenses']:,.2f} |
| **Net Balance** | **${weekly['weekly_balance']:,.2f}** |
| Income Transactions | {weekly['income_transactions']} |
| Expense Transactions | {weekly['expense_transactions']} |

---

## Month to Date Summary

| Metric | Amount |
|--------|--------|
| Monthly Income | ${month_summary['total_income']:,.2f} |
| Monthly Expenses | ${month_summary['total_expenses']:,.2f} |
| **Monthly Balance** | **${month_summary['balance']:,.2f}** |

---

## Top Transactions This Week

### Highest Income
"""
        
        if weekly['top_income']:
            t = weekly['top_income']
            report += f"\n- **${t['amount']:,.2f}** - {t['description']} ({t['date']})\n"
        else:
            report += "\n- No income recorded this week\n"
        
        report += "\n### Highest Expense\n"
        
        if weekly['top_expense']:
            t = weekly['top_expense']
            report += f"\n- **${t['amount']:,.2f}** - {t['description']} ({t['date']})\n"
        else:
            report += "\n- No expenses recorded this week\n"
        
        report += "\n---\n\n## Financial Insights\n\n"
        
        for i, insight in enumerate(weekly['insights'], 1):
            report += f"{i}. {insight}\n"
        
        report += f"""
---

## Recent Transactions

### Income
| Date | Amount | Description |
|------|--------|-------------|
"""
        
        income_entries = [e for e in self.entries if e.type == 'income'][:5]
        for e in income_entries:
            report += f"| {e.date} | ${e.amount:,.2f} | {e.description} |\n"
        
        if not income_entries:
            report += "| - | - | No recent income |\n"
        
        report += """
### Expenses
| Date | Amount | Description |
|------|--------|-------------|
"""
        
        expense_entries = [e for e in self.entries if e.type == 'expense'][:5]
        for e in expense_entries:
            report += f"| {e.date} | ${e.amount:,.2f} | {e.description} |\n"
        
        if not expense_entries:
            report += "| - | - | No recent expenses |\n"
        
        report += f"""
---

*Report generated by Accounting Manager Skill*
*File: {output_path.name}*
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        return str(output_path)

    def generate_ceo_weekly_report(self, output_path: str = None) -> str:
        """
        Generate CEO Weekly Briefing Report
        Executive-level summary with recommendations
        """
        weekly = self.get_weekly_summary()
        month_summary = self.get_summary()
        
        if output_path is None:
            output_path = self.accounting_folder / f'CEO_Weekly_Briefing_{weekly["period_end"]}.md'
        else:
            output_path = Path(output_path)
        
        # Determine overall status
        if weekly['weekly_balance'] > 0:
            status = "POSITIVE"
            status_color = "🟢"
        elif weekly['weekly_balance'] < 0:
            status = "NEGATIVE"
            status_color = "🔴"
        else:
            status = "NEUTRAL"
            status_color = "🟡"
        
        # Calculate key ratios
        expense_ratio = (weekly['weekly_expenses'] / weekly['weekly_income'] * 100) if weekly['weekly_income'] > 0 else 0
        profit_margin = ((weekly['weekly_income'] - weekly['weekly_expenses']) / weekly['weekly_income'] * 100) if weekly['weekly_income'] > 0 else 0
        
        # Generate recommendations based on data
        recommendations = []
        
        if weekly['weekly_balance'] > 0:
            recommendations.append("Consider reinvesting surplus into growth opportunities")
            if weekly['weekly_balance'] > weekly['weekly_income'] * 0.3:
                recommendations.append("Strong cash position - evaluate expansion options")
        else:
            recommendations.append("Review and reduce non-essential expenses")
            recommendations.append("Prioritize accounts receivable collection")
        
        if expense_ratio > 70:
            recommendations.append(f"Expense ratio is high ({expense_ratio:.1f}%) - implement cost control measures")
        elif expense_ratio < 40:
            recommendations.append(f"Excellent expense management ({expense_ratio:.1f}%) - maintain current practices")
        
        if profit_margin > 50:
            recommendations.append(f"Strong profit margin ({profit_margin:.1f}%) - consider price optimization")
        elif profit_margin > 0:
            recommendations.append(f"Healthy profit margin ({profit_margin:.1f}%) - focus on volume growth")
        
        # Get top 3 expenses for CEO attention
        expense_entries = [e for e in self.entries if e.type == 'expense']
        top_expenses = sorted(expense_entries, key=lambda x: x.amount, reverse=True)[:3]
        
        report = f"""# CEO Weekly Business Briefing

{status_color} **Financial Status: {status}**

**Report Period:** {weekly['period_start']} to {weekly['period_end']}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Prepared by:** Accounting Manager Skill

---

## Executive Summary

This week's financial performance shows **{status.lower()}** cash flow with a net balance of **${weekly['weekly_balance']:,.2f}**.

| Key Metric | This Week | Status |
|------------|-----------|--------|
| Total Revenue | ${weekly['weekly_income']:,.2f} | {'✅' if weekly['weekly_income'] > 0 else '⚠️'} |
| Total Expenses | ${weekly['weekly_expenses']:,.2f} | {'⚠️' if expense_ratio > 60 else '✅'} |
| Net Profit | ${weekly['weekly_balance']:,.2f} | {status_color} |
| Expense Ratio | {expense_ratio:.1f}% | {'⚠️' if expense_ratio > 60 else '✅'} |
| Profit Margin | {profit_margin:.1f}% | {'✅' if profit_margin > 30 else '⚠️'} |

---

## Financial Highlights

### 💰 Revenue Analysis
- **Total Income:** ${weekly['weekly_income']:,.2f}
- **Income Transactions:** {weekly['income_transactions']}
"""

        if weekly['top_income']:
            report += f"- **Largest Transaction:** ${weekly['top_income']['amount']:,.2f} - {weekly['top_income']['description']}\n"
        
        report += f"""
### 📝 Expense Analysis
- **Total Expenses:** ${weekly['weekly_expenses']:,.2f}
- **Expense Transactions:** {weekly['expense_transactions']}
"""

        if weekly['top_expense']:
            report += f"- **Largest Transaction:** ${weekly['top_expense']['amount']:,.2f} - {weekly['top_expense']['description']}\n"
        
        report += f"""
---

## Month-to-Date Performance

| Metric | Amount | % of Month Complete |
|--------|--------|---------------------|
| Monthly Income | ${month_summary['total_income']:,.2f} | {(weekly['weekly_income']/month_summary['total_income']*100) if month_summary['total_income'] > 0 else 0:.1f}% |
| Monthly Expenses | ${month_summary['total_expenses']:,.2f} | {(weekly['weekly_expenses']/month_summary['total_expenses']*100) if month_summary['total_expenses'] > 0 else 0:.1f}% |
| Monthly Balance | ${month_summary['balance']:,.2f} | - |

---

## Top Expenses Requiring CEO Attention

"""

        for i, exp in enumerate(top_expenses, 1):
            report += f"{i}. **${exp['amount']:,.2f}** - {exp['description']} ({exp['category'] or 'Uncategorized'})\n"
        
        if not top_expenses:
            report += "- No expenses recorded this period\n"
        
        report += """
---

## Strategic Insights

"""

        for i, insight in enumerate(weekly['insights'], 1):
            report += f"{i}. {insight}\n"
        
        report += """
---

## CEO Action Items

### Immediate (This Week)
"""

        # Generate action items based on data
        action_items = []
        
        if weekly['weekly_balance'] < 0:
            action_items.append("- [ ] Review and approve expense reduction plan")
            action_items.append("- [ ] Meet with finance team to address cash flow")
        
        if len(weekly['insights']) > 0:
            action_items.append("- [ ] Address identified financial concerns")
        
        if top_expenses:
            action_items.append("- [ ] Review top expenses for optimization opportunities")
        
        action_items.append("- [ ] Approve weekly financial report")
        action_items.append("- [ ] Set priorities for upcoming week")
        
        for item in action_items:
            report += f"{item}\n"
        
        report += """
### Strategic (This Month)
- [ ] Review monthly financial targets
- [ ] Evaluate business growth opportunities
- [ ] Assess competitive positioning
- [ ] Plan resource allocation

---

## Recommendations

"""

        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. **{rec}**\n"
        
        report += f"""
---

## Next Review

**Next Weekly Briefing:** {(datetime.now().strftime('%Y-%m-%d'))} (7 days)  
**Next Monthly Review:** {datetime.now().strftime('%Y-%m-01')} (First of next month)

---

*This report was automatically generated by the Accounting Manager Skill.*  
*For questions or clarifications, contact the Finance Department.*

**Confidentiality:** This document contains sensitive financial information.  
**Distribution:** CEO, CFO, Executive Team Only
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return str(output_path)

    def save(self):
        """Save entries to markdown file"""
        summary = self.get_summary()

        content = f"""# Accounting Records - {self.current_month}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Summary

| Metric | Amount |
|--------|--------|
| Total Income | ${summary['total_income']:,.2f} |
| Total Expenses | ${summary['total_expenses']:,.2f} |
| **Balance** | **${summary['balance']:,.2f}** |
| Total Entries | {summary['entry_count']} |

---

## Income

| Date | Amount | Description | Category | Notes |
|------|--------|-------------|----------|-------|
"""

        income_entries = [e for e in self.entries if e.type == 'income']
        for entry in sorted(income_entries, key=lambda x: x.date, reverse=True):
            content += f"| {entry.date} | ${entry.amount:,.2f} | {entry.description} | {entry.category} | {entry.notes} |\n"

        if not income_entries:
            content += "| - | - | No income recorded this month | - | - |\n"

        content += f"""
---

## Expenses

| Date | Amount | Description | Category | Notes |
|------|--------|-------------|----------|-------|
"""

        expense_entries = [e for e in self.entries if e.type == 'expense']
        for entry in sorted(expense_entries, key=lambda x: x.date, reverse=True):
            content += f"| {entry.date} | ${entry.amount:,.2f} | {entry.description} | {entry.category} | {entry.notes} |\n"

        if not expense_entries:
            content += "| - | - | No expenses recorded this month | - | - |\n"

        content += f"""
---

## Notes

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*File: {self.current_month_file.name}*
"""

        with open(self.current_month_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def list_entries(self, entry_type: str = None) -> List[Dict]:
        """List all entries, optionally filtered by type"""
        if entry_type:
            entries = [e for e in self.entries if e.type == entry_type]
        else:
            entries = self.entries

        return [asdict(e) for e in sorted(entries, key=lambda x: x.date, reverse=True)]

    def export_json(self, output_path: str = None) -> str:
        """Export entries to JSON"""
        if output_path is None:
            output_path = self.accounting_folder / f'{self.current_month}.json'
        else:
            output_path = Path(output_path)

        data = {
            'month': self.current_month,
            'summary': self.get_summary(),
            'entries': self.list_entries()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return str(output_path)


# MCP Server compatible functions
_accounting_skill = None


def get_skill() -> AccountingSkill:
    """Get or create accounting skill instance"""
    global _accounting_skill
    if _accounting_skill is None:
        _accounting_skill = AccountingSkill()
    return _accounting_skill


def log_income(amount: float, description: str, date: str = None, category: str = "", notes: str = "") -> str:
    """
    Log income entry
    
    Args:
        amount: Income amount (positive number)
        description: Description of income
        date: Date in YYYY-MM-DD format (defaults to today)
        category: Optional category
        notes: Optional additional notes
    
    Returns:
        JSON string with result
    """
    skill = get_skill()
    result = skill.add_income(amount, description, date, category, notes)
    return json.dumps(result, indent=2)


def log_expense(amount: float, description: str, date: str = None, category: str = "", notes: str = "") -> str:
    """
    Log expense entry
    
    Args:
        amount: Expense amount (positive number)
        description: Description of expense
        date: Date in YYYY-MM-DD format (defaults to today)
        category: Optional category
        notes: Optional additional notes
    
    Returns:
        JSON string with result
    """
    skill = get_skill()
    result = skill.add_expense(amount, description, date, category, notes)
    return json.dumps(result, indent=2)


def get_accounting_summary() -> str:
    """
    Get current month accounting summary
    
    Returns:
        JSON string with summary
    """
    skill = get_skill()
    return json.dumps(skill.get_summary(), indent=2)


def list_accounting_entries(entry_type: str = None) -> str:
    """
    List accounting entries
    
    Args:
        entry_type: Filter by 'income' or 'expense' (optional)
    
    Returns:
        JSON string with entries
    """
    skill = get_skill()
    entries = skill.list_entries(entry_type)
    return json.dumps({'entries': entries}, indent=2)


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Accounting Skill - Manage business finances')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Income command
    income_parser = subparsers.add_parser('income', help='Log income')
    income_parser.add_argument('amount', type=float, help='Amount')
    income_parser.add_argument('description', type=str, help='Description')
    income_parser.add_argument('--date', type=str, help='Date (YYYY-MM-DD)')
    income_parser.add_argument('--category', type=str, help='Category')
    income_parser.add_argument('--notes', type=str, help='Notes')

    # Expense command
    expense_parser = subparsers.add_parser('expense', help='Log expense')
    expense_parser.add_argument('amount', type=float, help='Amount')
    expense_parser.add_argument('description', type=str, help='Description')
    expense_parser.add_argument('--date', type=str, help='Date (YYYY-MM-DD)')
    expense_parser.add_argument('--category', type=str, help='Category')
    expense_parser.add_argument('--notes', type=str, help='Notes')

    # Summary command
    subparsers.add_parser('summary', help='Get monthly summary')

    # Weekly summary command
    weekly_parser = subparsers.add_parser('weekly-summary', help='Get weekly summary')
    weekly_parser.add_argument('--report', action='store_true', help='Generate full report file')

    # CEO weekly report command
    ceo_parser = subparsers.add_parser('ceo-report', help='Generate CEO Weekly Briefing')
    ceo_parser.add_argument('--output', type=str, help='Output file path')

    # List command
    list_parser = subparsers.add_parser('list', help='List entries')
    list_parser.add_argument('--type', type=str, choices=['income', 'expense'], help='Filter by type')

    # Export command
    subparsers.add_parser('export', help='Export to JSON')

    args = parser.parse_args()

    skill = AccountingSkill()

    if args.command == 'income':
        result = skill.add_income(
            args.amount,
            args.description,
            args.date,
            args.category or '',
            args.notes or ''
        )
        print(f"\n[OK] {result['message']}")
        print(f"   Date: {result['entry']['date']}")
        print(f"   Balance: ${skill.get_summary()['balance']:,.2f}")

    elif args.command == 'expense':
        result = skill.add_expense(
            args.amount,
            args.description,
            args.date,
            args.category or '',
            args.notes or ''
        )
        print(f"\n[EXP] {result['message']}")
        print(f"   Date: {result['entry']['date']}")
        print(f"   Balance: ${skill.get_summary()['balance']:,.2f}")

    elif args.command == 'summary':
        summary = skill.get_summary()
        print(f"\n=== Accounting Summary - {summary['month']} ===")
        print(f"   Total Income:   ${summary['total_income']:,.2f}")
        print(f"   Total Expenses: ${summary['total_expenses']:,.2f}")
        print(f"   Balance:        ${summary['balance']:,.2f}")
        print(f"   Entries:        {summary['entry_count']}")

    elif args.command == 'weekly-summary':
        weekly = skill.get_weekly_summary()
        print(f"\n=== Weekly Accounting Summary ===")
        print(f"Period: {weekly['period_start']} to {weekly['period_end']}")
        print(f"   Income:      ${weekly['weekly_income']:,.2f}")
        print(f"   Expenses:    ${weekly['weekly_expenses']:,.2f}")
        print(f"   Balance:     ${weekly['weekly_balance']:,.2f}")
        print(f"   Transactions: {weekly['income_transactions']} income, {weekly['expense_transactions']} expenses")
        print(f"\n--- Insights ---")
        for insight in weekly['insights']:
            print(f"  * {insight}")
        
        if args.report:
            report_path = skill.generate_weekly_report()
            print(f"\n[FILE] Weekly report generated: {report_path}")

    elif args.command == 'ceo-report':
        report_path = skill.generate_ceo_weekly_report(args.output)
        print(f"\n[CEO BRIEFING] Generated: {report_path}")

    elif args.command == 'list':
        entries = skill.list_entries(args.type)
        print(f"\n=== Accounting Entries ({len(entries)} entries) ===")
        for entry in entries[:10]:
            icon = '[+]' if entry['type'] == 'income' else '[-]'
            print(f"   {icon} {entry['date']} | ${entry['amount']:,.2f} | {entry['description']}")
        if len(entries) > 10:
            print(f"   ... and {len(entries) - 10} more entries")

    elif args.command == 'export':
        path = skill.export_json()
        print(f"\n[FILE] Exported to: {path}")

    else:
        parser.print_help()
        print("\n[INFO] Records saved to: AI_Employee_Vault/Accounting/current_month.md")
