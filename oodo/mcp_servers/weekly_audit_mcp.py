"""
Weekly Business & Accounting Audit System
Generates comprehensive business reports and CEO briefings
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/weekly_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeeklyAuditSystem:
    """Weekly Business & Accounting Audit System"""
    
    def __init__(self):
        self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
        self.ceo_briefings_dir = os.path.join(self.reports_dir, 'CEO_Briefings')
        self.audit_logs_dir = os.path.join(self.reports_dir, 'Audit_Logs')
        
        # Ensure directories exist
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.ceo_briefings_dir, exist_ok=True)
        os.makedirs(self.audit_logs_dir, exist_ok=True)
        
        logger.info("Weekly Audit System initialized")
    
    def get_financial_data(self) -> Dict:
        """Collect financial data from Odoo"""
        try:
            from mcp_servers.odoo_accounting_mcp import OdooAccountingMCP
            odoo = OdooAccountingMCP()
            
            # Get financial summaries
            weekly_summary = odoo.get_financial_summary('week')
            monthly_summary = odoo.get_financial_summary('month')
            receivable = odoo.get_accounts_receivable()
            payable = odoo.get_accounts_payable()
            invoices = odoo.get_invoices(limit=50)
            
            return {
                'success': True,
                'weekly': weekly_summary.get('summary', {}),
                'monthly': monthly_summary.get('summary', {}),
                'accounts_receivable': receivable.get('data', []),
                'accounts_payable': payable.get('data', []),
                'recent_invoices': invoices.get('data', [])
            }
        except Exception as e:
            logger.error(f"Financial data collection error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_social_media_data(self) -> Dict:
        """Collect social media performance data"""
        try:
            from mcp_servers.social_media_mcp import SocialMediaMCP
            social = SocialMediaMCP()
            
            summaries = social.get_all_summaries(7)
            
            return {
                'success': True,
                'facebook': summaries.get('facebook', {}),
                'instagram': summaries.get('instagram', {}),
                'twitter': summaries.get('twitter', {})
            }
        except Exception as e:
            logger.error(f"Social media data collection error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_communication_data(self) -> Dict:
        """Collect communication channel data"""
        try:
            from mcp_servers.email_communication_mcp import EmailCommunicationMCP
            comm = EmailCommunicationMCP()
            
            stats = comm.get_all_stats(7)
            
            return {
                'success': True,
                'gmail': stats.get('gmail', {}).get('stats', {}),
                'whatsapp': stats.get('whatsapp', {}).get('data', {})
            }
        except Exception as e:
            logger.error(f"Communication data collection error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def generate_weekly_audit_report(self, week_start: datetime = None) -> Dict:
        """Generate comprehensive weekly audit report"""
        if week_start is None:
            week_start = datetime.now() - timedelta(days=7)
        
        week_end = datetime.now()
        
        logger.info(f"Generating weekly audit report: {week_start} to {week_end}")
        
        # Collect all data
        financial_data = self.get_financial_data()
        social_data = self.get_social_media_data()
        communication_data = self.get_communication_data()
        
        # Build report
        report = {
            'report_type': 'Weekly Business Audit',
            'report_id': f"AUDIT_{week_start.strftime('%Y%m%d')}_{week_end.strftime('%Y%m%d')}",
            'period': {
                'start': week_start.strftime('%Y-%m-%d'),
                'end': week_end.strftime('%Y-%m-%d')
            },
            'generated_at': datetime.now().isoformat(),
            'financial_summary': financial_data,
            'social_media_performance': social_data,
            'communication_metrics': communication_data,
            'key_metrics': self._calculate_key_metrics(financial_data, social_data, communication_data),
            'alerts': self._generate_alerts(financial_data, social_data, communication_data),
            'recommendations': self._generate_recommendations(financial_data, social_data, communication_data)
        }
        
        # Save report
        report_path = os.path.join(
            self.audit_logs_dir,
            f"weekly_audit_{week_start.strftime('%Y%m%d')}.json"
        )
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also save markdown version
        md_report = self._convert_to_markdown(report)
        md_path = os.path.join(
            self.audit_logs_dir,
            f"weekly_audit_{week_start.strftime('%Y%m%d')}.md"
        )
        
        with open(md_path, 'w') as f:
            f.write(md_report)
        
        logger.info(f"Weekly audit report saved: {report_path}")
        
        return report
    
    def _calculate_key_metrics(self, financial: Dict, social: Dict, comm: Dict) -> Dict:
        """Calculate key business metrics"""
        metrics = {}
        
        # Financial metrics
        if financial.get('success'):
            weekly = financial.get('weekly', {})
            metrics['revenue'] = weekly.get('total_revenue', 0)
            metrics['expenses'] = weekly.get('total_expenses', 0)
            metrics['profit'] = weekly.get('net_profit', 0)
            metrics['profit_margin'] = (metrics['profit'] / metrics['revenue'] * 100) if metrics['revenue'] > 0 else 0
        
        # Social media metrics
        if social.get('success'):
            fb_metrics = social.get('facebook', {}).get('metrics', {})
            ig_metrics = social.get('instagram', {}).get('metrics', {})
            
            metrics['social_reach'] = (
                fb_metrics.get('reach', 0) + 
                ig_metrics.get('reach', 0)
            )
            metrics['social_engagement'] = (
                fb_metrics.get('engagement', 0) + 
                ig_metrics.get('engagement', 0)
            )
        
        # Communication metrics
        if comm.get('success'):
            gmail_stats = comm.get('gmail', {})
            metrics['emails_received'] = gmail_stats.get('week_count', 0)
            metrics['unread_emails'] = gmail_stats.get('unread_count', 0)
        
        return metrics
    
    def _generate_alerts(self, financial: Dict, social: Dict, comm: Dict) -> List[Dict]:
        """Generate business alerts based on data"""
        alerts = []
        
        # Financial alerts
        if financial.get('success'):
            weekly = financial.get('weekly', {})
            if weekly.get('net_profit', 0) < 0:
                alerts.append({
                    'type': 'warning',
                    'category': 'financial',
                    'message': 'Negative profit detected this week',
                    'severity': 'high'
                })
            
            receivable = financial.get('accounts_receivable', [])
            if len(receivable) > 10:
                alerts.append({
                    'type': 'info',
                    'category': 'financial',
                    'message': f'{len(receivable)} outstanding invoices need attention',
                    'severity': 'medium'
                })
        
        # Communication alerts
        if comm.get('success'):
            unread = comm.get('gmail', {}).get('unread_count', 0)
            if unread > 50:
                alerts.append({
                    'type': 'info',
                    'category': 'communication',
                    'message': f'{unread} unread emails require attention',
                    'severity': 'low'
                })
        
        return alerts
    
    def _generate_recommendations(self, financial: Dict, social: Dict, comm: Dict) -> List[str]:
        """Generate business recommendations"""
        recommendations = []
        
        # Financial recommendations
        if financial.get('success'):
            weekly = financial.get('weekly', {})
            if weekly.get('total_revenue', 0) > 0:
                recommendations.append('Consider reinvesting profits into marketing campaigns')
            
            if len(financial.get('accounts_receivable', [])) > 5:
                recommendations.append('Follow up on outstanding invoices to improve cash flow')
        
        # Social media recommendations
        if social.get('success'):
            fb_engagement = social.get('facebook', {}).get('metrics', {}).get('engagement', 0)
            if fb_engagement > 0:
                recommendations.append('Increase posting frequency on Facebook due to high engagement')
        
        # General recommendations
        recommendations.append('Review weekly metrics in CEO briefing for strategic decisions')
        
        return recommendations
    
    def _convert_to_markdown(self, report: Dict) -> str:
        """Convert report to markdown format"""
        md = f"""# Weekly Business Audit Report

**Report ID:** {report['report_id']}
**Period:** {report['period']['start']} to {report['period']['end']}
**Generated:** {report['generated_at']}

---

## Executive Summary

### Key Metrics
| Metric | Value |
|--------|-------|
"""
        
        metrics = report.get('key_metrics', {})
        for key, value in metrics.items():
            if isinstance(value, float):
                md += f"| {key.replace('_', ' ').title()} | {value:,.2f} |\n"
            else:
                md += f"| {key.replace('_', ' ').title()} | {value:,} |\n"
        
        md += "\n---\n\n"
        
        # Financial Summary
        md += "## Financial Summary\n\n"
        financial = report.get('financial_summary', {})
        if financial.get('success'):
            weekly = financial.get('weekly', {})
            md += f"- **Revenue:** ${weekly.get('total_revenue', 0):,.2f}\n"
            md += f"- **Expenses:** ${weekly.get('total_expenses', 0):,.2f}\n"
            md += f"- **Net Profit:** ${weekly.get('net_profit', 0):,.2f}\n"
        md += "\n---\n\n"
        
        # Alerts
        md += "## Alerts\n\n"
        for alert in report.get('alerts', []):
            md += f"- **[{alert['severity'].upper()}]** {alert['message']}\n"
        md += "\n---\n\n"
        
        # Recommendations
        md += "## Recommendations\n\n"
        for i, rec in enumerate(report.get('recommendations', []), 1):
            md += f"{i}. {rec}\n"
        
        return md
    
    def generate_ceo_briefing(self, audit_report: Dict = None) -> Dict:
        """Generate CEO briefing from audit report"""
        if audit_report is None:
            audit_report = self.generate_weekly_audit_report()
        
        logger.info("Generating CEO briefing")
        
        briefing = {
            'briefing_type': 'CEO Executive Briefing',
            'briefing_id': f"CEO_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'period': audit_report.get('period', {}),
            'executive_summary': self._create_executive_summary(audit_report),
            'financial_highlights': self._create_financial_highlights(audit_report),
            'operational_highlights': self._create_operational_highlights(audit_report),
            'critical_alerts': [a for a in audit_report.get('alerts', []) if a.get('severity') == 'high'],
            'action_items': self._create_action_items(audit_report),
            'strategic_recommendations': audit_report.get('recommendations', [])
        }
        
        # Save briefing
        briefing_path = os.path.join(
            self.ceo_briefings_dir,
            f"ceo_briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(briefing_path, 'w') as f:
            json.dump(briefing, f, indent=2)
        
        # Also save markdown version
        md_briefing = self._convert_briefing_to_markdown(briefing)
        md_path = os.path.join(
            self.ceo_briefings_dir,
            f"ceo_briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        
        with open(md_path, 'w') as f:
            f.write(md_briefing)
        
        logger.info(f"CEO briefing saved: {briefing_path}")
        
        return briefing
    
    def _create_executive_summary(self, audit_report: Dict) -> str:
        """Create executive summary"""
        metrics = audit_report.get('key_metrics', {})
        
        summary = f"""This week's business performance shows:

**Financial Performance:**
- Revenue: ${metrics.get('revenue', 0):,.2f}
- Net Profit: ${metrics.get('profit', 0):,.2f}
- Profit Margin: {metrics.get('profit_margin', 0):.1f}%

**Digital Presence:**
- Social Media Reach: {metrics.get('social_reach', 0):,}
- Social Engagement: {metrics.get('social_engagement', 0):,}

**Communication:**
- Emails Received: {metrics.get('emails_received', 0)}
- Unread requiring attention: {metrics.get('unread_emails', 0)}
"""
        return summary
    
    def _create_financial_highlights(self, audit_report: Dict) -> List[Dict]:
        """Create financial highlights"""
        highlights = []
        
        financial = audit_report.get('financial_summary', {})
        if financial.get('success'):
            weekly = financial.get('weekly', {})
            
            highlights.append({
                'title': 'Weekly Revenue',
                'value': f"${weekly.get('total_revenue', 0):,.2f}",
                'trend': 'positive' if weekly.get('net_profit', 0) > 0 else 'negative'
            })
            
            highlights.append({
                'title': 'Net Profit',
                'value': f"${weekly.get('net_profit', 0):,.2f}",
                'trend': 'positive' if weekly.get('net_profit', 0) > 0 else 'negative'
            })
            
            receivable = financial.get('accounts_receivable', [])
            highlights.append({
                'title': 'Outstanding Invoices',
                'value': str(len(receivable)),
                'trend': 'neutral'
            })
        
        return highlights
    
    def _create_operational_highlights(self, audit_report: Dict) -> List[Dict]:
        """Create operational highlights"""
        highlights = []
        
        social = audit_report.get('social_media_performance', {})
        if social.get('success'):
            fb = social.get('facebook', {})
            ig = social.get('instagram', {})
            
            highlights.append({
                'title': 'Facebook Reach',
                'value': f"{fb.get('metrics', {}).get('reach', 0):,}",
                'trend': 'neutral'
            })
            
            highlights.append({
                'title': 'Instagram Reach',
                'value': f"{ig.get('metrics', {}).get('reach', 0):,}",
                'trend': 'neutral'
            })
        
        return highlights
    
    def _create_action_items(self, audit_report: Dict) -> List[Dict]:
        """Create action items from audit"""
        action_items = []
        
        # Add action items based on alerts
        for alert in audit_report.get('alerts', []):
            if alert.get('severity') in ['high', 'medium']:
                action_items.append({
                    'action': f"Address: {alert['message']}",
                    'priority': alert['severity'],
                    'category': alert['category'],
                    'status': 'pending'
                })
        
        # Add standard weekly actions
        action_items.append({
            'action': 'Review outstanding invoices and follow up on payments',
            'priority': 'high',
            'category': 'financial',
            'status': 'pending'
        })
        
        action_items.append({
            'action': 'Process unread emails requiring response',
            'priority': 'medium',
            'category': 'communication',
            'status': 'pending'
        })
        
        return action_items
    
    def _convert_briefing_to_markdown(self, briefing: Dict) -> str:
        """Convert CEO briefing to markdown"""
        md = f"""# CEO Executive Briefing

**Briefing ID:** {briefing['briefing_id']}
**Generated:** {briefing['generated_at']}
**Period:** {briefing['period'].get('start', 'N/A')} to {briefing['period'].get('end', 'N/A')}

---

## Executive Summary

{briefing['executive_summary']}

---

## Financial Highlights

| Metric | Value | Trend |
|--------|-------|-------|
"""
        
        for highlight in briefing.get('financial_highlights', []):
            trend_icon = '📈' if highlight.get('trend') == 'positive' else '📉' if highlight.get('trend') == 'negative' else '➡️'
            md += f"| {highlight['title']} | {highlight['value']} | {trend_icon} |\n"
        
        md += "\n---\n\n"
        
        md += "## Operational Highlights\n\n"
        for highlight in briefing.get('operational_highlights', []):
            md += f"- **{highlight['title']}:** {highlight['value']}\n"
        
        md += "\n---\n\n"
        
        md += "## Critical Alerts\n\n"
        for alert in briefing.get('critical_alerts', []):
            md += f"⚠️ **{alert['message']}**\n"
        
        if not briefing.get('critical_alerts'):
            md += "No critical alerts this period.\n"
        
        md += "\n---\n\n"
        
        md += "## Action Items\n\n"
        for i, item in enumerate(briefing.get('action_items', []), 1):
            priority_icon = '🔴' if item.get('priority') == 'high' else '🟡' if item.get('priority') == 'medium' else '🟢'
            md += f"{i}. {priority_icon} [{item['category'].title()}] {item['action']}\n"
        
        md += "\n---\n\n"
        
        md += "## Strategic Recommendations\n\n"
        for i, rec in enumerate(briefing.get('strategic_recommendations', []), 1):
            md += f"{i}. {rec}\n"
        
        return md


# Main execution
if __name__ == '__main__':
    audit_system = WeeklyAuditSystem()
    
    print("Weekly Business & Accounting Audit System")
    print("=" * 50)
    
    # Generate weekly audit
    print("\nGenerating weekly audit report...")
    audit_report = audit_system.generate_weekly_audit_report()
    print(f"Audit Report ID: {audit_report.get('report_id')}")
    
    # Generate CEO briefing
    print("\nGenerating CEO briefing...")
    ceo_briefing = audit_system.generate_ceo_briefing(audit_report)
    print(f"CEO Briefing ID: {ceo_briefing.get('briefing_id')}")
    
    print("\n✓ Audit and briefing generation complete!")
    print(f"Reports saved to: {audit_system.reports_dir}")
