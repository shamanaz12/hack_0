"""
Cross-Domain Integration System
Handles both Personal and Business domain operations
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cross_domain.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DomainContext:
    """Represents a domain context (Personal or Business)"""
    
    def __init__(self, name: str, config: Dict = None):
        self.name = name
        self.config = config or {}
        self.enabled = True
        self.priority = config.get('priority', 1)
        self.settings = config.get('settings', {})
        
    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'enabled': self.enabled,
            'priority': self.priority,
            'settings': self.settings
        }


class CrossDomainIntegration:
    """
    Full Cross-Domain Integration System
    Manages both Personal and Business domains with context-aware operations
    """
    
    def __init__(self):
        self.domains: Dict[str, DomainContext] = {}
        self.active_domain: Optional[str] = None
        self.domain_rules: List[Dict] = []
        self.operation_log: List[Dict] = []
        
        self._init_default_domains()
        self._init_domain_rules()
        
        logger.info("Cross-Domain Integration initialized")
    
    def _init_default_domains(self):
        """Initialize default domains"""
        # Business Domain
        self.domains['business'] = DomainContext('business', {
            'priority': 1,
            'settings': {
                'odoo_enabled': True,
                'accounting_enabled': True,
                'social_media_enabled': True,
                'audit_enabled': True,
                'ceo_briefing_enabled': True,
                'work_hours': {'start': 9, 'end': 18},
                'auto_audit': True,
                'notification_channels': ['email', 'whatsapp']
            }
        })
        
        # Personal Domain
        self.domains['personal'] = DomainContext('personal', {
            'priority': 2,
            'settings': {
                'email_enabled': True,
                'social_media_enabled': True,
                'calendar_enabled': True,
                'reminders_enabled': True,
                'content_creation_enabled': True,
                'work_hours': {'start': 0, 'end': 24},
                'auto_post': False,
                'notification_channels': ['email']
            }
        })
    
    def _init_domain_rules(self):
        """Initialize domain routing rules"""
        self.domain_rules = [
            {
                'name': 'invoice_operations',
                'condition': lambda op: op.get('type') in ['invoice', 'payment', 'accounting'],
                'domain': 'business'
            },
            {
                'name': 'social_posting',
                'condition': lambda op: op.get('type') == 'social_post',
                'domain': lambda op: op.get('context', 'personal')
            },
            {
                'name': 'email_communication',
                'condition': lambda op: op.get('type') == 'email',
                'domain': lambda op: op.get('context', 'personal')
            },
            {
                'name': 'audit_operations',
                'condition': lambda op: op.get('type') == 'audit',
                'domain': 'business'
            },
            {
                'name': 'ceo_briefing',
                'condition': lambda op: op.get('type') == 'briefing',
                'domain': 'business'
            },
            {
                'name': 'personal_reminders',
                'condition': lambda op: op.get('type') == 'reminder',
                'domain': 'personal'
            }
        ]
    
    def get_domain(self, domain_name: str) -> Optional[DomainContext]:
        """Get domain by name"""
        return self.domains.get(domain_name)
    
    def set_active_domain(self, domain_name: str):
        """Set the active domain"""
        if domain_name in self.domains:
            self.active_domain = domain_name
            logger.info(f"Active domain set to: {domain_name}")
        else:
            logger.warning(f"Domain not found: {domain_name}")
    
    def determine_domain(self, operation: Dict) -> str:
        """Determine which domain an operation belongs to"""
        # Check explicit domain in operation
        if 'domain' in operation:
            return operation['domain']
        
        # Apply rules
        for rule in self.domain_rules:
            try:
                if rule['condition'](operation):
                    domain = rule['domain']
                    if callable(domain):
                        return domain(operation)
                    return domain
            except Exception as e:
                logger.debug(f"Rule evaluation error: {str(e)}")
        
        # Default to personal
        return 'personal'
    
    def execute_operation(self, operation: Dict) -> Dict:
        """Execute an operation in the appropriate domain"""
        start_time = datetime.now()
        
        # Determine domain
        domain_name = self.determine_domain(operation)
        domain = self.get_domain(domain_name)
        
        if not domain:
            return {
                'success': False,
                'error': f'Domain not found: {domain_name}',
                'timestamp': start_time.isoformat()
            }
        
        if not domain.enabled:
            return {
                'success': False,
                'error': f'Domain disabled: {domain_name}',
                'timestamp': start_time.isoformat()
            }
        
        logger.info(f"Executing operation '{operation.get('type')}' in domain '{domain_name}'")
        
        try:
            # Route to appropriate handler
            result = self._route_operation(operation, domain)
            
            # Log operation
            self._log_operation(domain_name, operation, result, start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Operation execution error: {str(e)}")
            result = {
                'success': False,
                'error': str(e),
                'domain': domain_name,
                'timestamp': start_time.isoformat()
            }
            self._log_operation(domain_name, operation, result, start_time)
            return result
    
    def _route_operation(self, operation: Dict, domain: DomainContext) -> Dict:
        """Route operation to appropriate handler"""
        op_type = operation.get('type')
        
        # Business domain operations
        if domain.name == 'business':
            return self._handle_business_operation(operation)
        
        # Personal domain operations
        elif domain.name == 'personal':
            return self._handle_personal_operation(operation)
        
        else:
            return {'success': False, 'error': f'Unknown domain: {domain.name}'}
    
    def _handle_business_operation(self, operation: Dict) -> Dict:
        """Handle business domain operations"""
        op_type = operation.get('type')
        
        try:
            if op_type == 'invoice':
                return self._create_invoice(operation)
            elif op_type == 'accounting':
                return self._get_accounting_data(operation)
            elif op_type == 'social_post':
                return self._post_business_social(operation)
            elif op_type == 'audit':
                return self._run_audit(operation)
            elif op_type == 'briefing':
                return self._generate_briefing(operation)
            elif op_type == 'report':
                return self._generate_report(operation)
            else:
                return {'success': False, 'error': f'Unknown business operation: {op_type}'}
        except Exception as e:
            logger.error(f"Business operation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _handle_personal_operation(self, operation: Dict) -> Dict:
        """Handle personal domain operations"""
        op_type = operation.get('type')
        
        try:
            if op_type == 'email':
                return self._send_email(operation)
            elif op_type == 'social_post':
                return self._post_personal_social(operation)
            elif op_type == 'reminder':
                return self._set_reminder(operation)
            elif op_type == 'content':
                return self._generate_content(operation)
            elif op_type == 'schedule':
                return self._schedule_personal(operation)
            else:
                return {'success': False, 'error': f'Unknown personal operation: {op_type}'}
        except Exception as e:
            logger.error(f"Personal operation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Business Operation Handlers
    def _create_invoice(self, operation: Dict) -> Dict:
        """Create invoice in Odoo"""
        from mcp_servers.odoo_accounting_mcp import OdooAccountingMCP
        
        odoo = OdooAccountingMCP()
        result = odoo.create_invoice(
            partner_id=operation.get('partner_id'),
            lines=operation.get('lines', []),
            invoice_type=operation.get('invoice_type', 'out_invoice')
        )
        
        return {
            'success': result.get('success', False),
            'data': result.get('data'),
            'domain': 'business',
            'operation': 'create_invoice',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_accounting_data(self, operation: Dict) -> Dict:
        """Get accounting data from Odoo"""
        from mcp_servers.odoo_accounting_mcp import OdooAccountingMCP
        
        odoo = OdooAccountingMCP()
        
        if operation.get('query') == 'financial_summary':
            result = odoo.get_financial_summary(operation.get('period', 'month'))
        elif operation.get('query') == 'invoices':
            result = odoo.get_invoices(operation.get('limit', 10))
        elif operation.get('query') == 'customers':
            result = odoo.get_customers(operation.get('limit', 50))
        else:
            result = {'success': False, 'error': 'Unknown query'}
        
        return {
            'success': result.get('success', False),
            'data': result.get('data') or result.get('summary'),
            'domain': 'business',
            'operation': 'accounting',
            'timestamp': datetime.now().isoformat()
        }
    
    def _post_business_social(self, operation: Dict) -> Dict:
        """Post to business social media"""
        from mcp_servers.social_media_mcp import SocialMediaMCP
        
        social = SocialMediaMCP()
        message = operation.get('message', '')
        image_url = operation.get('image_url')
        
        platforms = operation.get('platforms', ['facebook', 'instagram'])
        results = {}
        
        for platform in platforms:
            if platform == 'facebook':
                if image_url:
                    results['facebook'] = social.facebook.post_photo(image_url, message)
                else:
                    results['facebook'] = social.facebook.post_text(message)
            elif platform == 'instagram':
                if image_url:
                    results['instagram'] = social.instagram.create_image_post(image_url, message)
            elif platform == 'twitter':
                results['twitter'] = social.twitter.post_tweet(message)
        
        return {
            'success': all(r.get('success', False) for r in results.values()),
            'results': results,
            'domain': 'business',
            'operation': 'social_post',
            'timestamp': datetime.now().isoformat()
        }
    
    def _run_audit(self, operation: Dict) -> Dict:
        """Run business audit"""
        from mcp_servers.weekly_audit_mcp import WeeklyAuditSystem
        
        audit = WeeklyAuditSystem()
        report = audit.generate_weekly_audit_report()
        
        return {
            'success': True,
            'data': report,
            'domain': 'business',
            'operation': 'audit',
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_briefing(self, operation: Dict) -> Dict:
        """Generate CEO briefing"""
        from mcp_servers.weekly_audit_mcp import WeeklyAuditSystem
        
        audit = WeeklyAuditSystem()
        briefing = audit.generate_ceo_briefing()
        
        return {
            'success': True,
            'data': briefing,
            'domain': 'business',
            'operation': 'briefing',
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_report(self, operation: Dict) -> Dict:
        """Generate business report"""
        from mcp_servers.weekly_audit_mcp import WeeklyAuditSystem
        
        audit = WeeklyAuditSystem()
        report_type = operation.get('report_type', 'weekly')
        
        if report_type == 'weekly':
            result = audit.generate_weekly_audit_report()
        else:
            result = audit.generate_weekly_audit_report()
        
        return {
            'success': True,
            'data': result,
            'domain': 'business',
            'operation': 'report',
            'timestamp': datetime.now().isoformat()
        }
    
    # Personal Operation Handlers
    def _send_email(self, operation: Dict) -> Dict:
        """Send personal email"""
        from mcp_servers.email_communication_mcp import EmailCommunicationMCP
        
        comm = EmailCommunicationMCP()
        result = comm.gmail.send_email(
            to=operation.get('to'),
            subject=operation.get('subject'),
            body=operation.get('body'),
            html=operation.get('html', False)
        )
        
        return {
            'success': result.get('success', False),
            'data': result,
            'domain': 'personal',
            'operation': 'email',
            'timestamp': datetime.now().isoformat()
        }
    
    def _post_personal_social(self, operation: Dict) -> Dict:
        """Post to personal social media"""
        from mcp_servers.social_media_mcp import SocialMediaMCP
        
        social = SocialMediaMCP()
        message = operation.get('message', '')
        image_url = operation.get('image_url')
        
        results = {}
        
        if image_url:
            results['instagram'] = social.instagram.create_image_post(image_url, message)
        
        results['twitter'] = social.twitter.post_tweet(message)
        
        return {
            'success': True,
            'results': results,
            'domain': 'personal',
            'operation': 'social_post',
            'timestamp': datetime.now().isoformat()
        }
    
    def _set_reminder(self, operation: Dict) -> Dict:
        """Set personal reminder"""
        from skills.agent_skills import skill_manager
        
        result = skill_manager.execute_skill(
            'scheduling',
            action='set_reminder',
            title=operation.get('title'),
            start_time=operation.get('time')
        )
        
        return {
            'success': result.get('success', False),
            'data': result,
            'domain': 'personal',
            'operation': 'reminder',
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_content(self, operation: Dict) -> Dict:
        """Generate personal content"""
        from skills.agent_skills import skill_manager
        
        result = skill_manager.execute_skill(
            'content_generation',
            content_type=operation.get('content_type', 'social_post'),
            topic=operation.get('topic'),
            tone=operation.get('tone', 'casual')
        )
        
        return {
            'success': result.get('success', False),
            'data': result,
            'domain': 'personal',
            'operation': 'content',
            'timestamp': datetime.now().isoformat()
        }
    
    def _schedule_personal(self, operation: Dict) -> Dict:
        """Schedule personal event"""
        from skills.agent_skills import skill_manager
        
        result = skill_manager.execute_skill(
            'scheduling',
            action='schedule_meeting',
            title=operation.get('title'),
            start_time=operation.get('start_time'),
            end_time=operation.get('end_time'),
            attendees=operation.get('attendees'),
            location=operation.get('location')
        )
        
        return {
            'success': result.get('success', False),
            'data': result,
            'domain': 'personal',
            'operation': 'schedule',
            'timestamp': datetime.now().isoformat()
        }
    
    def _log_operation(self, domain_name: str, operation: Dict, 
                       result: Dict, start_time: datetime):
        """Log operation for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'domain': domain_name,
            'operation_type': operation.get('type'),
            'success': result.get('success', False),
            'duration_ms': (datetime.now() - start_time).total_seconds() * 1000
        }
        
        self.operation_log.append(log_entry)
        
        # Keep log size manageable
        if len(self.operation_log) > 1000:
            self.operation_log = self.operation_log[-1000:]
    
    def get_domain_status(self) -> Dict:
        """Get status of all domains"""
        return {
            'active_domain': self.active_domain,
            'domains': {name: domain.to_dict() for name, domain in self.domains.items()},
            'recent_operations': len(self.operation_log),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_operation_history(self, limit: int = 50, 
                              domain: str = None) -> List[Dict]:
        """Get recent operation history"""
        history = self.operation_log[-limit:]
        
        if domain:
            history = [op for op in history if op.get('domain') == domain]
        
        return history


# Global cross-domain integration instance
cross_domain = CrossDomainIntegration()


if __name__ == '__main__':
    print("Cross-Domain Integration System")
    print("=" * 50)
    
    # Get domain status
    print("\nDomain Status:")
    status = cross_domain.get_domain_status()
    print(json.dumps(status, indent=2))
    
    # Test business operation
    print("\n\nTesting Business Operation (Audit):")
    result = cross_domain.execute_operation({
        'type': 'audit',
        'domain': 'business'
    })
    print(f"Success: {result.get('success')}")
    print(f"Operation: {result.get('operation')}")
    
    # Test personal operation
    print("\n\nTesting Personal Operation (Content):")
    result = cross_domain.execute_operation({
        'type': 'content',
        'content_type': 'social_post',
        'topic': 'Weekend vibes',
        'tone': 'casual'
    })
    print(f"Success: {result.get('success')}")
    
    # Get operation history
    print("\n\nRecent Operations:")
    history = cross_domain.get_operation_history(10)
    for op in history:
        print(f"  - {op['timestamp']}: {op['domain']}/{op['operation_type']} ({op['success']})")
