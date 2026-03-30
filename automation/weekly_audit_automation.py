"""
Weekly Audit Automation
Gold Tier - Autonomous Business Audit System

Generates:
- Weekly business audit reports
- Accounting summaries
- CEO briefing reports
- Social media performance

Usage:
  python weekly_audit_automation.py --run
  python weekly_audit_automation.py --generate-report
  python weekly_audit_automation.py --ceo-briefing
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
REPORTS_DIR = Path('reports')
LOGS_DIR = Path('logs')

# Ensure directories exist
REPORTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


class WeeklyAuditAutomation:
    """Autonomous Weekly Audit System"""

    def __init__(self):
        self.report_file = None

    def collect_data(self) -> dict:
        """Collect data from all MCP servers"""
        print("\n[1/5] Collecting data from all sources...")
        
        data = {
            'collection_date': datetime.now().isoformat(),
            'period': 'weekly',
            'sources': {}
        }
        
        # Collect from Communication MCP
        comm_log = LOGS_DIR / 'whatsapp_outgoing.json'
        if comm_log.exists():
            with open(comm_log, 'r') as f:
                data['sources']['whatsapp'] = json.load(f)
        
        # Collect from Social Media MCP
        fb_log = LOGS_DIR / 'facebook_posts.json'
        if fb_log.exists():
            with open(fb_log, 'r') as f:
                data['sources']['facebook'] = json.load(f)
        
        ig_log = LOGS_DIR / 'instagram_posts.json'
        if ig_log.exists():
            with open(ig_log, 'r') as f:
                data['sources']['instagram'] = json.load(f)
        
        # Collect from Business MCP
        inv_log = LOGS_DIR / 'pending_invoices.json'
        if inv_log.exists():
            with open(inv_log, 'r') as f:
                data['sources']['invoices'] = json.load(f)
        
        print(f"  ✅ Data collected from {len(data['sources'])} sources")
        return data

    def generate_audit_report(self, data: dict) -> str:
        """Generate weekly audit report"""
        print("\n[2/5] Generating audit report...")
        
        report = "# WEEKLY BUSINESS AUDIT REPORT\n\n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report += f"**Period:** Weekly Audit\n\n"
        report += "=" * 60 + "\n\n"
        
        # Executive Summary
        report += "## Executive Summary\n\n"
        
        total_posts = 0
        total_invoices = 0
        total_amount = 0
        
        if 'facebook' in data['sources']:
            total_posts += len(data['sources']['facebook'])
        if 'instagram' in data['sources']:
            total_posts += len(data['sources']['instagram'])
        if 'invoices' in data['sources']:
            total_invoices += len(data['sources']['invoices'])
            total_amount += sum(inv.get('amount', 0) for inv in data['sources']['invoices'])
        
        report += f"- **Total Social Media Posts:** {total_posts}\n"
        report += f"- **Total Invoices:** {total_invoices}\n"
        report += f"- **Total Invoice Amount:** ${total_amount:.2f}\n\n"
        
        # Social Media Performance
        report += "## Social Media Performance\n\n"
        
        if 'facebook' in data['sources']:
            report += f"### Facebook\n- Posts: {len(data['sources']['facebook'])}\n\n"
        
        if 'instagram' in data['sources']:
            report += f"### Instagram\n- Posts: {len(data['sources']['instagram'])}\n\n"
        
        # Financial Summary
        report += "## Financial Summary\n\n"
        
        if 'invoices' in data['sources']:
            report += f"### Invoices\n- Total: {len(data['sources']['invoices'])}\n"
            report += f"- Total Amount: ${total_amount:.2f}\n\n"
            
            # List recent invoices
            report += "### Recent Invoices\n"
            for inv in data['sources']['invoices'][-5:]:
                report += f"- {inv.get('customer', 'Unknown')}: ${inv.get('amount', 0):.2f}\n"
        
        # Recommendations
        report += "\n## Recommendations\n\n"
        report += "1. Continue regular social media posting\n"
        report += "2. Follow up on pending invoices\n"
        report += "3. Review weekly performance metrics\n"
        report += "4. Plan next week's content calendar\n"
        
        report += "\n" + "=" * 60 + "\n"
        report += "**End of Report**\n"
        
        print(f"  ✅ Audit report generated")
        return report

    def generate_ceo_briefing(self, data: dict) -> str:
        """Generate CEO briefing"""
        print("\n[3/5] Generating CEO briefing...")
        
        briefing = "# CEO BRIEFING\n\n"
        briefing += f"**Date:** {datetime.now().strftime('%B %d, %Y')}\n"
        briefing += f"**Prepared by:** Autonomous Employee System\n\n"
        briefing += "=" * 60 + "\n\n"
        
        # Key Highlights
        briefing += "## Key Highlights\n\n"
        
        total_posts = 0
        if 'facebook' in data['sources']:
            total_posts += len(data['sources']['facebook'])
        if 'instagram' in data['sources']:
            total_posts += len(data['sources']['instagram'])
        
        briefing += f"✅ Social Media: {total_posts} posts published this week\n"
        
        if 'invoices' in data['sources']:
            total_amount = sum(inv.get('amount', 0) for inv in data['sources']['invoices'])
            briefing += f"✅ Revenue: ${total_amount:.2f} in invoices generated\n"
        
        # Areas Requiring Attention
        briefing += "\n## Areas Requiring Attention\n\n"
        
        pending_invoices = [inv for inv in data['sources'].get('invoices', []) 
                           if inv.get('status') == 'pending']
        if pending_invoices:
            briefing += f"⚠️  {len(pending_invoices)} invoices pending processing\n"
        
        # Action Items
        briefing += "\n## Action Items\n\n"
        briefing += "1. Review social media engagement metrics\n"
        briefing += "2. Approve pending invoices\n"
        briefing += "3. Schedule team meeting for next week\n"
        briefing += "4. Review customer feedback\n"
        
        # Next Week Focus
        briefing += "\n## Focus for Next Week\n\n"
        briefing += "- Increase social media engagement\n"
        briefing += "- Follow up on outstanding invoices\n"
        briefing += "- Launch new marketing campaign\n"
        
        briefing += "\n" + "=" * 60 + "\n"
        briefing += "**End of Briefing**\n"
        
        print(f"  ✅ CEO briefing generated")
        return briefing

    def save_reports(self, audit_report: str, ceo_briefing: str):
        """Save reports to files"""
        print("\n[4/5] Saving reports...")
        
        # Save audit report
        audit_file = REPORTS_DIR / f'weekly_audit_{datetime.now().strftime("%Y%m%d")}.md'
        with open(audit_file, 'w', encoding='utf-8') as f:
            f.write(audit_report)
        print(f"  ✅ Audit report saved: {audit_file}")
        
        # Save CEO briefing
        briefing_file = REPORTS_DIR / f'ceo_briefing_{datetime.now().strftime("%Y%m%d")}.md'
        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write(ceo_briefing)
        print(f"  ✅ CEO briefing saved: {briefing_file}")

    def run_audit(self):
        """Run complete weekly audit"""
        print("=" * 60)
        print("   WEEKLY AUDIT AUTOMATION")
        print("=" * 60)
        
        # Step 1: Collect data
        data = self.collect_data()
        
        # Step 2: Generate audit report
        audit_report = self.generate_audit_report(data)
        
        # Step 3: Generate CEO briefing
        ceo_briefing = self.generate_ceo_briefing(data)
        
        # Step 4: Save reports
        self.save_reports(audit_report, ceo_briefing)
        
        # Step 5: Summary
        print("\n[5/5] Audit complete!")
        print(f"\n  Reports generated:")
        print(f"  - Weekly Audit Report")
        print(f"  - CEO Briefing")
        print(f"\n  Location: {REPORTS_DIR.absolute()}")
        
        print("\n" + "=" * 60)
        print("   WEEKLY AUDIT COMPLETE!")
        print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Weekly Audit Automation')
    parser.add_argument('--run', action='store_true', help='Run weekly audit')
    parser.add_argument('--generate-report', action='store_true', help='Generate audit report')
    parser.add_argument('--ceo-briefing', action='store_true', help='Generate CEO briefing')
    
    args = parser.parse_args()
    
    automation = WeeklyAuditAutomation()
    
    if args.run:
        automation.run_audit()
    
    elif args.generate_report or args.ceo_briefing:
        print("Collecting data...")
        data = automation.collect_data()
        
        if args.generate_report:
            report = automation.generate_audit_report(data)
            print("\n" + report)
        
        if args.ceo_briefing:
            briefing = automation.generate_ceo_briefing(data)
            print("\n" + briefing)
    
    else:
        print("Weekly Audit Automation")
        print("=" * 60)
        print("\nUsage:")
        print("  python weekly_audit_automation.py --run")
        print("  python weekly_audit_automation.py --generate-report")
        print("  python weekly_audit_automation.py --ceo-briefing")
        print("\nFeatures:")
        print("  - Collects data from all MCP servers")
        print("  - Generates weekly audit report")
        print("  - Generates CEO briefing")
        print("  - Saves reports to reports/ folder")


if __name__ == '__main__':
    main()
