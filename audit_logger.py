#!/usr/bin/env python3
"""
Comprehensive Audit Logging System

Features:
- Logs all system activities across MCP servers
- Tracks user actions and API calls
- Maintains immutable audit trail
- Supports search and filtering
- Generates compliance reports
- Database-backed storage (SQLite)
"""

import os
import sys
import json
import sqlite3
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import threading

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/audit.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    
    # Data Operations
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    
    # MCP Server Operations
    SERVER_START = "server_start"
    SERVER_STOP = "server_stop"
    SERVER_ERROR = "server_error"
    API_CALL = "api_call"
    
    # Business Operations
    INVOICE_CREATE = "invoice_create"
    INVOICE_SEND = "invoice_send"
    INVOICE_PAID = "invoice_paid"
    PAYMENT_RECEIVED = "payment_received"
    
    # Social Media
    SOCIAL_POST = "social_post"
    SOCIAL_COMMENT = "social_comment"
    SOCIAL_MESSAGE = "social_message"
    
    # Email
    EMAIL_SENT = "email_sent"
    EMAIL_RECEIVED = "email_received"
    EMAIL_FAILED = "email_failed"
    
    # System
    CONFIG_CHANGE = "config_change"
    BACKUP_CREATED = "backup_created"
    ERROR_OCCURRED = "error_occurred"
    RECOVERY_ACTION = "recovery_action"
    
    # Custom
    CUSTOM = "custom"


class AuditSeverity(Enum):
    """Severity levels for audit events"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event record"""
    id: Optional[int]
    timestamp: str
    event_type: str
    severity: str
    service: str
    action: str
    user: str
    resource: str
    resource_id: Optional[str]
    details: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    correlation_id: Optional[str]
    duration_ms: Optional[float]
    status_code: Optional[int]
    error_message: Optional[str]
    checksum: str  # For integrity verification
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AuditEvent':
        return cls(**data)


class AuditDatabase:
    """SQLite database for audit logs"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    service TEXT NOT NULL,
                    action TEXT NOT NULL,
                    user TEXT NOT NULL,
                    resource TEXT,
                    resource_id TEXT,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    correlation_id TEXT,
                    duration_ms REAL,
                    status_code INTEGER,
                    error_message TEXT,
                    checksum TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON audit_events(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_event_type 
                ON audit_events(event_type)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_service 
                ON audit_events(service)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user 
                ON audit_events(user)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_severity 
                ON audit_events(severity)
            ''')
            
            conn.commit()
            conn.close()
    
    def insert(self, event: AuditEvent) -> int:
        """Insert audit event"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_events 
                (timestamp, event_type, severity, service, action, user, 
                 resource, resource_id, details, ip_address, user_agent, 
                 correlation_id, duration_ms, status_code, error_message, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.timestamp,
                event.event_type,
                event.severity,
                event.service,
                event.action,
                event.user,
                event.resource,
                event.resource_id,
                event.details,
                event.ip_address,
                event.user_agent,
                event.correlation_id,
                event.duration_ms,
                event.status_code,
                event.error_message,
                event.checksum
            ))
            
            event_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return event_id
    
    def query(self, 
              start_date: str = None,
              end_date: str = None,
              event_type: str = None,
              service: str = None,
              user: str = None,
              severity: str = None,
              limit: int = 1000) -> List[AuditEvent]:
        """Query audit events with filters"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT * FROM audit_events WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if service:
                query += " AND service = ?"
                params.append(service)
            
            if user:
                query += " AND user = ?"
                params.append(user)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                event = AuditEvent(
                    id=row[0],
                    timestamp=row[1],
                    event_type=row[2],
                    severity=row[3],
                    service=row[4],
                    action=row[5],
                    user=row[6],
                    resource=row[7],
                    resource_id=row[8],
                    details=row[9],
                    ip_address=row[10],
                    user_agent=row[11],
                    correlation_id=row[12],
                    duration_ms=row[13],
                    status_code=row[14],
                    error_message=row[15],
                    checksum=row[16]
                )
                events.append(event)
            
            conn.close()
            return events
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get audit statistics"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            stats = {}
            
            # Total events
            cursor.execute('''
                SELECT COUNT(*) FROM audit_events WHERE timestamp >= ?
            ''', (start_date,))
            stats['total_events'] = cursor.fetchone()[0]
            
            # Events by type
            cursor.execute('''
                SELECT event_type, COUNT(*) 
                FROM audit_events 
                WHERE timestamp >= ?
                GROUP BY event_type
                ORDER BY COUNT(*) DESC
            ''', (start_date,))
            stats['by_type'] = dict(cursor.fetchall())
            
            # Events by service
            cursor.execute('''
                SELECT service, COUNT(*) 
                FROM audit_events 
                WHERE timestamp >= ?
                GROUP BY service
                ORDER BY COUNT(*) DESC
            ''', (start_date,))
            stats['by_service'] = dict(cursor.fetchall())
            
            # Events by severity
            cursor.execute('''
                SELECT severity, COUNT(*) 
                FROM audit_events 
                WHERE timestamp >= ?
                GROUP BY severity
                ORDER BY COUNT(*) DESC
            ''', (start_date,))
            stats['by_severity'] = dict(cursor.fetchall())
            
            # Top users
            cursor.execute('''
                SELECT user, COUNT(*) 
                FROM audit_events 
                WHERE timestamp >= ?
                GROUP BY user
                ORDER BY COUNT(*) DESC
                LIMIT 10
            ''', (start_date,))
            stats['top_users'] = dict(cursor.fetchall())
            
            conn.close()
            return stats
    
    def verify_integrity(self) -> bool:
        """Verify audit log integrity"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, checksum FROM audit_events ORDER BY id")
            rows = cursor.fetchall()
            
            for row_id, stored_checksum in rows:
                # Recalculate checksum
                cursor.execute("SELECT * FROM audit_events WHERE id = ?", (row_id,))
                row = cursor.fetchone()
                
                # Calculate checksum of all fields except id and checksum
                data = {
                    'timestamp': row[1],
                    'event_type': row[2],
                    'severity': row[3],
                    'service': row[4],
                    'action': row[5],
                    'user': row[6],
                    'resource': row[7],
                    'resource_id': row[8],
                    'details': row[9],
                    'ip_address': row[10],
                    'user_agent': row[11],
                    'correlation_id': row[12],
                    'duration_ms': row[13],
                    'status_code': row[14],
                    'error_message': row[15]
                }
                
                calculated_checksum = hashlib.sha256(
                    json.dumps(data, sort_keys=True).encode()
                ).hexdigest()
                
                if calculated_checksum != stored_checksum:
                    logger.error(f"Integrity check failed for event ID {row_id}")
                    conn.close()
                    return False
            
            conn.close()
            return True


class AuditLogger:
    """Main Audit Logger"""
    
    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else Path(__file__).parent
        self.logs_folder = self.vault_path / 'logs'
        self.audit_folder = self.vault_path / 'AI_Employee_Vault' / 'Audit_Logs'
        
        # Create folders
        os.makedirs(self.logs_folder, exist_ok=True)
        os.makedirs(self.audit_folder, exist_ok=True)
        
        # Initialize database
        db_path = self.logs_folder / 'audit.db'
        self.db = AuditDatabase(str(db_path))
        
        # Default values
        self.default_user = os.getenv('AUDIT_DEFAULT_USER', 'system')
        self.default_service = os.getenv('AUDIT_DEFAULT_SERVICE', 'gold_tier')
        
        logger.info("Audit Logger initialized")
    
    def _calculate_checksum(self, data: Dict) -> str:
        """Calculate checksum for data integrity"""
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
    
    def log(self,
            event_type: AuditEventType,
            action: str,
            service: str = None,
            user: str = None,
            resource: str = None,
            resource_id: str = None,
            details: str = None,
            severity: AuditSeverity = AuditSeverity.INFO,
            ip_address: str = None,
            user_agent: str = None,
            correlation_id: str = None,
            duration_ms: float = None,
            status_code: int = None,
            error_message: str = None) -> int:
        """Log an audit event"""
        
        timestamp = datetime.now().isoformat()
        
        # Prepare data for checksum
        checksum_data = {
            'timestamp': timestamp,
            'event_type': event_type.value,
            'severity': severity.value,
            'service': service or self.default_service,
            'action': action,
            'user': user or self.default_user,
            'resource': resource,
            'resource_id': resource_id,
            'details': details,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'correlation_id': correlation_id,
            'duration_ms': duration_ms,
            'status_code': status_code,
            'error_message': error_message
        }
        
        checksum = self._calculate_checksum(checksum_data)
        
        event = AuditEvent(
            id=None,
            timestamp=timestamp,
            event_type=event_type.value,
            severity=severity.value,
            service=service or self.default_service,
            action=action,
            user=user or self.default_user,
            resource=resource,
            resource_id=resource_id,
            details=details or '',
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            duration_ms=duration_ms,
            status_code=status_code,
            error_message=error_message,
            checksum=checksum
        )
        
        event_id = self.db.insert(event)
        
        # Also log to file for quick access
        logger.info(f"[AUDIT] {event_type.value} | {service} | {action} | {user} | {details}")
        
        return event_id
    
    def log_api_call(self,
                     service: str,
                     endpoint: str,
                     method: str,
                     status_code: int,
                     duration_ms: float,
                     user: str = None,
                     error: str = None) -> int:
        """Log API call"""
        return self.log(
            event_type=AuditEventType.API_CALL,
            action=f"{method} {endpoint}",
            service=service,
            user=user,
            details=f"API call to {endpoint}",
            severity=AuditSeverity.ERROR if error else AuditSeverity.INFO,
            duration_ms=duration_ms,
            status_code=status_code,
            error_message=error
        )
    
    def log_error(self,
                  service: str,
                  error: Exception,
                  user: str = None,
                  resource: str = None) -> int:
        """Log error"""
        return self.log(
            event_type=AuditEventType.ERROR_OCCURRED,
            action='error',
            service=service,
            user=user,
            resource=resource,
            details=str(error),
            severity=AuditSeverity.ERROR,
            error_message=str(error)
        )
    
    def log_business_action(self,
                            action_type: str,
                            description: str,
                            resource_id: str = None,
                            user: str = None) -> int:
        """Log business action (invoice, payment, etc.)"""
        event_type_map = {
            'invoice_create': AuditEventType.INVOICE_CREATE,
            'invoice_send': AuditEventType.INVOICE_SEND,
            'invoice_paid': AuditEventType.INVOICE_PAID,
            'payment_received': AuditEventType.PAYMENT_RECEIVED,
            'social_post': AuditEventType.SOCIAL_POST,
            'email_sent': AuditEventType.EMAIL_SENT,
            'email_received': AuditEventType.EMAIL_RECEIVED
        }
        
        event_type = event_type_map.get(action_type, AuditEventType.CUSTOM)
        
        return self.log(
            event_type=event_type,
            action=action_type,
            service='business',
            user=user,
            resource_id=resource_id,
            details=description
        )
    
    def query_events(self,
                     start_date: str = None,
                     end_date: str = None,
                     event_type: str = None,
                     service: str = None,
                     user: str = None,
                     severity: str = None,
                     limit: int = 1000) -> List[Dict]:
        """Query audit events"""
        events = self.db.query(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            service=service,
            user=user,
            severity=severity,
            limit=limit
        )
        return [e.to_dict() for e in events]
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get audit statistics"""
        return self.db.get_statistics(days=days)
    
    def verify_integrity(self) -> bool:
        """Verify audit log integrity"""
        return self.db.verify_integrity()
    
    def generate_report(self, days: int = 7) -> str:
        """Generate audit report"""
        stats = self.get_statistics(days)
        integrity_ok = self.verify_integrity()
        
        report = f"""# Audit Log Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Period:** Last {days} days
**Integrity Check:** {'✅ PASSED' if integrity_ok else '❌ FAILED'}

## Summary

| Metric | Value |
|--------|-------|
| Total Events | {stats['total_events']:,} |

## Events by Type

| Type | Count |
|------|-------|
"""
        
        for event_type, count in stats['by_type'].items():
            report += f"| {event_type} | {count:,} |\n"
        
        report += """
## Events by Service

| Service | Count |
|---------|-------|
"""
        
        for service, count in stats['by_service'].items():
            report += f"| {service} | {count:,} |\n"
        
        report += """
## Events by Severity

| Severity | Count |
|----------|-------|
"""
        
        for severity, count in stats['by_severity'].items():
            report += f"| {severity.upper()} | {count:,} |\n"
        
        report += """
## Top Users

| User | Events |
|------|--------|
"""
        
        for user, count in stats['top_users'].items():
            report += f"| {user} | {count:,} |\n"
        
        report += """
---

*This report was generated by the AI Employee Vault Audit System.*
"""
        
        return report
    
    def save_report(self, days: int = 7) -> Path:
        """Save audit report to file"""
        report = self.generate_report(days)
        report_file = self.audit_folder / f"audit_report_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Audit report saved to: {report_file}")
        return report_file


# Context manager for automatic audit logging
class AuditContext:
    """Context manager for auditing code blocks"""
    
    def __init__(self, audit_logger: AuditLogger, action: str, service: str = None, **kwargs):
        self.audit_logger = audit_logger
        self.action = action
        self.service = service
        self.kwargs = kwargs
        self.start_time = None
        self.event_id = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (datetime.now() - self.start_time).total_seconds() * 1000
        
        if exc_type:
            self.audit_logger.log(
                event_type=AuditEventType.ERROR_OCCURRED,
                action=self.action,
                service=self.service,
                duration_ms=duration_ms,
                error_message=str(exc_val),
                severity=AuditSeverity.ERROR,
                **self.kwargs
            )
        else:
            self.audit_logger.log(
                event_type=AuditEventType.CUSTOM,
                action=self.action,
                service=self.service,
                duration_ms=duration_ms,
                status_code=200,
                **self.kwargs
            )
        
        return False  # Don't suppress exceptions


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger(vault_path: str = None) -> AuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(vault_path=vault_path)
    return _audit_logger


def audit_action(action: str, service: str = None, **kwargs):
    """Decorator for auditing functions"""
    def decorator(func):
        def wrapper(*args, **func_kwargs):
            audit_logger = get_audit_logger()
            with AuditContext(audit_logger, action, service, **kwargs):
                return func(*args, func_kwargs)
        return wrapper
    return decorator


# Main function
def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit Logging System')
    parser.add_argument('--vault', type=str, help='Path to vault folder')
    parser.add_argument('--report', action='store_true', help='Generate audit report')
    parser.add_argument('--days', type=int, default=7, help='Number of days for report')
    parser.add_argument('--verify', action='store_true', help='Verify audit integrity')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    args = parser.parse_args()
    
    audit = AuditLogger(vault_path=args.vault)
    
    if args.report:
        report_file = audit.save_report(days=args.days)
        print(f"Audit report saved to: {report_file}")
    
    elif args.verify:
        integrity_ok = audit.verify_integrity()
        print(f"Integrity check: {'✅ PASSED' if integrity_ok else '❌ FAILED'}")
    
    elif args.stats:
        stats = audit.get_statistics(days=args.days)
        print("\n" + "=" * 60)
        print("Audit Statistics")
        print("=" * 60)
        print(f"Total Events: {stats['total_events']:,}")
        print(f"By Type: {stats['by_type']}")
        print(f"By Service: {stats['by_service']}")
        print(f"By Severity: {stats['by_severity']}")
        print("=" * 60)
    
    else:
        # Demo: Log a test event
        event_id = audit.log(
            event_type=AuditEventType.CUSTOM,
            action='test_event',
            service='audit_system',
            user='admin',
            details='Test audit event'
        )
        print(f"Test event logged with ID: {event_id}")


if __name__ == '__main__':
    main()
