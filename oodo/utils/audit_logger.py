"""
Comprehensive Audit Logging System
SQLite-based audit trail for all system operations
"""

import os
import json
import logging
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/audit_logger.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AuditLogger:
    """Comprehensive audit logging system with SQLite backend"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'audit', 'audit_log.db'
            )
        
        self.db_path = db_path
        self._lock = threading.Lock()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Audit Logger initialized with database: {db_path}")
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Main audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    service TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    user_id TEXT,
                    status TEXT NOT NULL,
                    duration_ms REAL,
                    request_data TEXT,
                    response_data TEXT,
                    error_message TEXT,
                    ip_address TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    checksum TEXT
                )
            ''')
            
            # User actions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    ip_address TEXT,
                    metadata TEXT
                )
            ''')
            
            # System events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    component TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TEXT,
                    resolved_by TEXT
                )
            ''')
            
            # Business operations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS business_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT,
                    amount REAL,
                    currency TEXT,
                    status TEXT NOT NULL,
                    performed_by TEXT,
                    metadata TEXT
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                ON audit_logs(timestamp)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_event_type 
                ON audit_logs(event_type)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_service 
                ON audit_logs(service)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_actions_timestamp 
                ON user_actions(timestamp)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_system_events_timestamp 
                ON system_events(timestamp)
            ''')
            
            conn.commit()
            conn.close()
    
    def _generate_checksum(self, data: Dict) -> str:
        """Generate checksum for data integrity verification"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def log_audit(self, event_type: str, category: str, service: str, 
                  operation: str, status: str, user_id: str = None,
                  duration_ms: float = None, request_data: Dict = None,
                  response_data: Dict = None, error_message: str = None,
                  ip_address: str = None, session_id: str = None,
                  metadata: Dict = None) -> int:
        """Log an audit entry"""
        timestamp = datetime.now().isoformat()
        
        # Prepare data for checksum
        checksum_data = {
            'timestamp': timestamp,
            'event_type': event_type,
            'category': category,
            'service': service,
            'operation': operation,
            'status': status
        }
        checksum = self._generate_checksum(checksum_data)
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_logs (
                    timestamp, event_type, category, service, operation,
                    user_id, status, duration_ms, request_data, response_data,
                    error_message, ip_address, session_id, metadata, checksum
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, event_type, category, service, operation,
                user_id, status, duration_ms,
                json.dumps(request_data) if request_data else None,
                json.dumps(response_data) if response_data else None,
                error_message, ip_address, session_id,
                json.dumps(metadata) if metadata else None, checksum
            ))
            
            entry_id = cursor.lastrowid
            conn.commit()
            conn.close()
        
        logger.debug(f"Audit log entry created: ID={entry_id}, event={event_type}")
        return entry_id
    
    def log_user_action(self, user_id: str, action: str, resource_type: str = None,
                        resource_id: str = None, old_value: Dict = None,
                        new_value: Dict = None, ip_address: str = None,
                        metadata: Dict = None) -> int:
        """Log a user action"""
        timestamp = datetime.now().isoformat()
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_actions (
                    timestamp, user_id, action, resource_type, resource_id,
                    old_value, new_value, ip_address, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, user_id, action, resource_type, resource_id,
                json.dumps(old_value) if old_value else None,
                json.dumps(new_value) if new_value else None,
                ip_address, json.dumps(metadata) if metadata else None
            ))
            
            entry_id = cursor.lastrowid
            conn.commit()
            conn.close()
        
        logger.debug(f"User action logged: ID={entry_id}, user={user_id}, action={action}")
        return entry_id
    
    def log_system_event(self, event_type: str, component: str, 
                         severity: str, message: str, details: Dict = None) -> int:
        """Log a system event"""
        timestamp = datetime.now().isoformat()
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_events (
                    timestamp, event_type, component, severity, message, details
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, event_type, component, severity, message,
                json.dumps(details) if details else None
            ))
            
            entry_id = cursor.lastrowid
            conn.commit()
            conn.close()
        
        logger.debug(f"System event logged: ID={entry_id}, type={event_type}")
        return entry_id
    
    def log_business_operation(self, operation_type: str, entity_type: str,
                               entity_id: str = None, amount: float = None,
                               currency: str = 'USD', status: str = 'completed',
                               performed_by: str = None, metadata: Dict = None) -> int:
        """Log a business operation"""
        timestamp = datetime.now().isoformat()
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO business_operations (
                    timestamp, operation_type, entity_type, entity_id,
                    amount, currency, status, performed_by, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, operation_type, entity_type, entity_id,
                amount, currency, status, performed_by,
                json.dumps(metadata) if metadata else None
            ))
            
            entry_id = cursor.lastrowid
            conn.commit()
            conn.close()
        
        logger.debug(f"Business operation logged: ID={entry_id}, type={operation_type}")
        return entry_id
    
    def get_audit_logs(self, start_date: datetime = None, end_date: datetime = None,
                       event_type: str = None, service: str = None,
                       status: str = None, limit: int = 100) -> List[Dict]:
        """Query audit logs with filters"""
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if service:
            query += " AND service = ?"
            params.append(service)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
        
        return [dict(row) for row in rows]
    
    def get_user_actions(self, user_id: str = None, action: str = None,
                         limit: int = 100) -> List[Dict]:
        """Query user actions"""
        query = "SELECT * FROM user_actions WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if action:
            query += " AND action = ?"
            params.append(action)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
        
        return [dict(row) for row in rows]
    
    def get_system_events(self, component: str = None, severity: str = None,
                          unresolved_only: bool = False, limit: int = 100) -> List[Dict]:
        """Query system events"""
        query = "SELECT * FROM system_events WHERE 1=1"
        params = []
        
        if component:
            query += " AND component = ?"
            params.append(component)
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        if unresolved_only:
            query += " AND resolved = FALSE"
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
        
        return [dict(row) for row in rows]
    
    def get_business_operations(self, operation_type: str = None,
                                 entity_type: str = None,
                                 start_date: datetime = None,
                                 end_date: datetime = None,
                                 limit: int = 100) -> List[Dict]:
        """Query business operations"""
        query = "SELECT * FROM business_operations WHERE 1=1"
        params = []
        
        if operation_type:
            query += " AND operation_type = ?"
            params.append(operation_type)
        
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
        
        return [dict(row) for row in rows]
    
    def verify_integrity(self) -> Dict:
        """Verify audit log integrity using checksums"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, timestamp, event_type, category, service, operation, status, checksum FROM audit_logs")
            rows = cursor.fetchall()
            conn.close()
        
        total = len(rows)
        valid = 0
        invalid = []
        
        for row in rows:
            checksum_data = {
                'timestamp': row['timestamp'],
                'event_type': row['event_type'],
                'category': row['category'],
                'service': row['service'],
                'operation': row['operation'],
                'status': row['status']
            }
            expected_checksum = self._generate_checksum(checksum_data)
            
            if row['checksum'] == expected_checksum:
                valid += 1
            else:
                invalid.append(row['id'])
        
        return {
            'total_entries': total,
            'valid_entries': valid,
            'invalid_entries': len(invalid),
            'invalid_ids': invalid,
            'integrity_verified': len(invalid) == 0,
            'verified_at': datetime.now().isoformat()
        }
    
    def get_statistics(self, hours: int = 24) -> Dict:
        """Get audit log statistics"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Total events
            cursor.execute(
                "SELECT COUNT(*) as count FROM audit_logs WHERE timestamp >= ?",
                (cutoff,)
            )
            total = cursor.fetchone()['count']
            
            # By status
            cursor.execute(
                "SELECT status, COUNT(*) as count FROM audit_logs WHERE timestamp >= ? GROUP BY status",
                (cutoff,)
            )
            by_status = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # By service
            cursor.execute(
                "SELECT service, COUNT(*) as count FROM audit_logs WHERE timestamp >= ? GROUP BY service",
                (cutoff,)
            )
            by_service = {row['service']: row['count'] for row in cursor.fetchall()}
            
            # By event type
            cursor.execute(
                "SELECT event_type, COUNT(*) as count FROM audit_logs WHERE timestamp >= ? GROUP BY event_type",
                (cutoff,)
            )
            by_event_type = {row['event_type']: row['count'] for row in cursor.fetchall()}
            
            # Average duration
            cursor.execute(
                "SELECT AVG(duration_ms) as avg_duration FROM audit_logs WHERE timestamp >= ? AND duration_ms IS NOT NULL",
                (cutoff,)
            )
            avg_duration = cursor.fetchone()['avg_duration'] or 0
            
            conn.close()
        
        return {
            'period_hours': hours,
            'generated_at': datetime.now().isoformat(),
            'total_events': total,
            'by_status': by_status,
            'by_service': by_service,
            'by_event_type': by_event_type,
            'average_duration_ms': avg_duration
        }
    
    def cleanup_old_logs(self, days: int = 90) -> int:
        """Delete audit logs older than specified days"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM audit_logs WHERE timestamp < ?", (cutoff,))
            deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
        
        logger.info(f"Cleaned up {deleted} audit logs older than {days} days")
        return deleted


# Global audit logger instance
audit_logger = AuditLogger()


# Convenience functions for easy logging
def log_api_call(service: str, operation: str, status: str, 
                 request_data: Dict = None, response_data: Dict = None,
                 error_message: str = None, duration_ms: float = None,
                 user_id: str = None):
    """Log an API call"""
    return audit_logger.log_audit(
        event_type='api_call',
        category='api',
        service=service,
        operation=operation,
        status=status,
        user_id=user_id,
        duration_ms=duration_ms,
        request_data=request_data,
        response_data=response_data,
        error_message=error_message
    )


def log_user_action(user_id: str, action: str, resource_type: str = None,
                    resource_id: str = None, old_value: Dict = None,
                    new_value: Dict = None):
    """Log a user action"""
    return audit_logger.log_user_action(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_value=old_value,
        new_value=new_value
    )


def log_system_event(component: str, severity: str, message: str, 
                     details: Dict = None, event_type: str = 'system'):
    """Log a system event"""
    return audit_logger.log_system_event(
        event_type=event_type,
        component=component,
        severity=severity,
        message=message,
        details=details
    )


def log_business_operation(operation_type: str, entity_type: str,
                           entity_id: str = None, amount: float = None,
                           currency: str = 'USD', status: str = 'completed',
                           performed_by: str = None):
    """Log a business operation"""
    return audit_logger.log_business_operation(
        operation_type=operation_type,
        entity_type=entity_type,
        entity_id=entity_id,
        amount=amount,
        currency=currency,
        status=status,
        performed_by=performed_by
    )


if __name__ == '__main__':
    print("Comprehensive Audit Logging System")
    print("=" * 50)
    
    # Test audit logging
    print("\nTesting audit logging...")
    
    # Log API call
    log_api_call(
        service='odoo',
        operation='create_invoice',
        status='success',
        request_data={'partner_id': 1, 'amount': 1000},
        response_data={'invoice_id': 123},
        duration_ms=150.5,
        user_id='user_001'
    )
    
    # Log user action
    log_user_action(
        user_id='user_001',
        action='update_profile',
        resource_type='user',
        resource_id='user_001',
        old_value={'name': 'Old Name'},
        new_value={'name': 'New Name'}
    )
    
    # Log system event
    log_system_event(
        component='database',
        severity='warning',
        message='High connection count detected',
        details={'connections': 95, 'max': 100}
    )
    
    # Log business operation
    log_business_operation(
        operation_type='invoice_created',
        entity_type='invoice',
        entity_id='INV-2026-001',
        amount=1500.00,
        currency='USD',
        status='completed',
        performed_by='user_001'
    )
    
    # Get statistics
    print("\nAudit Statistics:")
    stats = audit_logger.get_statistics(24)
    print(json.dumps(stats, indent=2))
    
    # Verify integrity
    print("\nIntegrity Verification:")
    integrity = audit_logger.verify_integrity()
    print(json.dumps(integrity, indent=2))
    
    # Get recent logs
    print("\nRecent Audit Logs:")
    logs = audit_logger.get_audit_logs(limit=5)
    for log in logs:
        print(f"  - {log['timestamp']}: {log['event_type']} ({log['status']})")
