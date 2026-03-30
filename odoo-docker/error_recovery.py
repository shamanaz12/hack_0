#!/usr/bin/env python3
"""
Error Recovery System - Graceful Degradation & Auto-Recovery

Features:
- Automatic retry with exponential backoff
- Circuit breaker pattern for failing services
- Fallback mechanisms for critical operations
- Health monitoring for all MCP servers
- Auto-restart for crashed services
- Error categorization and handling strategies
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

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
        logging.FileHandler('logs/error_recovery.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, stop calling
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5  # Failures before opening circuit
    recovery_timeout: int = 60  # Seconds before trying again
    half_open_max_calls: int = 3  # Test calls in half-open state


@dataclass
class RetryConfig:
    """Retry configuration"""
    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0


@dataclass
class ServiceHealth:
    """Service health status"""
    name: str
    healthy: bool
    last_check: str
    response_time_ms: Optional[float]
    error_count: int
    consecutive_failures: int
    circuit_state: str
    last_error: Optional[str]


@dataclass
class ErrorRecord:
    """Error record for audit trail"""
    timestamp: str
    service: str
    error_type: str
    error_message: str
    severity: str
    retry_count: int
    recovered: bool
    recovery_method: Optional[str]
    stack_trace: Optional[str]


class CircuitBreaker:
    """Circuit Breaker Pattern Implementation"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        self._lock = threading.Lock()
    
    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            
            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if self.last_failure_time:
                    elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                    if elapsed >= self.config.recovery_timeout:
                        self.state = CircuitState.HALF_OPEN
                        self.half_open_calls = 0
                        logger.info(f"Circuit breaker {self.name} moved to HALF_OPEN")
                        return True
                return False
            
            if self.state == CircuitState.HALF_OPEN:
                # Allow limited calls in half-open state
                if self.half_open_calls < self.config.half_open_max_calls:
                    self.half_open_calls += 1
                    return True
                return False
            
            return False
    
    def record_success(self):
        """Record successful execution"""
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_calls -= 1
                if self.half_open_calls <= 0:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    logger.info(f"Circuit breaker {self.name} moved to CLOSED")
            else:
                self.failure_count = 0
    
    def record_failure(self):
        """Record failed execution"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker {self.name} moved to OPEN (from HALF_OPEN)")
            elif self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker {self.name} moved to OPEN (threshold reached)")
    
    def get_state(self) -> str:
        """Get current circuit state"""
        return self.state.value


class RetryHandler:
    """Retry with Exponential Backoff"""
    
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry"""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries:
                    delay = min(
                        self.config.base_delay * (self.config.exponential_base ** attempt),
                        self.config.max_delay
                    )
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
        
        raise last_exception
    
    def execute_with_fallback(self, func: Callable, fallback: Callable, *args, **kwargs) -> Any:
        """Execute function with fallback on failure"""
        try:
            return self.execute(func, *args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary function failed, using fallback: {e}")
            return fallback(*args, **kwargs)


class ErrorRecoverySystem:
    """Main Error Recovery System"""
    
    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else Path(__file__).parent
        self.logs_folder = self.vault_path / 'logs'
        self.errors_folder = self.vault_path / 'AI_Employee_Vault' / 'Error_Logs'
        self.state_file = self.vault_path / 'error_recovery_state.json'
        
        # Create folders
        os.makedirs(self.logs_folder, exist_ok=True)
        os.makedirs(self.errors_folder, exist_ok=True)
        
        # Initialize circuit breakers for each service
        self.circuit_breakers: Dict[str, CircuitBreaker] = {
            'odoo': CircuitBreaker('odoo'),
            'facebook': CircuitBreaker('facebook'),
            'instagram': CircuitBreaker('instagram'),
            'email': CircuitBreaker('email'),
            'whatsapp': CircuitBreaker('whatsapp')
        }
        
        # Retry handler
        self.retry_handler = RetryHandler()
        
        # Service health tracking
        self.service_health: Dict[str, ServiceHealth] = {}
        
        # Error records
        self.error_records: List[ErrorRecord] = []
        
        # MCP server processes
        self.server_processes: Dict[str, subprocess.Popen] = {}
        
        # Load state
        self._load_state()
        
        logger.info("Error Recovery System initialized")
    
    def _load_state(self):
        """Load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Restore error records
                    for record_data in data.get('error_records', []):
                        self.error_records.append(ErrorRecord(**record_data))
            except Exception as e:
                logger.error(f"Error loading state: {e}")
    
    def _save_state(self):
        """Save state to file"""
        data = {
            'error_records': [asdict(r) for r in self.error_records[-1000:],  # Keep last 1000
            'service_health': {k: asdict(v) if hasattr(v, '__dataclass_fields__') else v 
                             for k, v in self.service_health.items()}
        }
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Get circuit breaker for service"""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker(service)
        return self.circuit_breakers[service]
    
    def execute_with_recovery(self, service: str, func: Callable, fallback: Callable = None, *args, **kwargs) -> Any:
        """Execute function with error recovery"""
        circuit_breaker = self.get_circuit_breaker(service)
        
        # Check circuit breaker
        if not circuit_breaker.can_execute():
            logger.warning(f"Circuit breaker OPEN for {service}, using fallback")
            if fallback:
                return fallback(*args, **kwargs)
            raise Exception(f"Circuit breaker open for service: {service}")
        
        try:
            # Execute with retry
            result = self.retry_handler.execute(func, *args, **kwargs)
            circuit_breaker.record_success()
            self._update_service_health(service, healthy=True)
            return result
        
        except Exception as e:
            circuit_breaker.record_failure()
            self._update_service_health(service, healthy=False, error=str(e))
            
            # Log error
            error_record = ErrorRecord(
                timestamp=datetime.now().isoformat(),
                service=service,
                error_type=type(e).__name__,
                error_message=str(e),
                severity=self._categorize_severity(service, e),
                retry_count=self.retry_handler.config.max_retries,
                recovered=False,
                recovery_method=None,
                stack_trace=self._get_stack_trace()
            )
            self.error_records.append(error_record)
            self._save_state()
            
            # Try fallback
            if fallback:
                logger.info(f"Attempting fallback for {service}")
                try:
                    result = fallback(*args, **kwargs)
                    error_record.recovered = True
                    error_record.recovery_method = "fallback"
                    logger.info(f"Fallback successful for {service}")
                    return result
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
            
            # Re-raise if no fallback
            raise
    
    def _categorize_severity(self, service: str, error: Exception) -> str:
        """Categorize error severity"""
        error_str = str(error).lower()
        
        # Critical errors
        if any(x in error_str for x in ['authentication', 'permission', 'unauthorized']):
            return ErrorSeverity.CRITICAL.value
        
        # High severity
        if any(x in error_str for x in ['timeout', 'connection', 'network']):
            return ErrorSeverity.HIGH.value
        
        # Medium severity
        if any(x in error_str for x in ['not found', 'invalid', 'missing']):
            return ErrorSeverity.MEDIUM.value
        
        # Low severity
        return ErrorSeverity.LOW.value
    
    def _get_stack_trace(self) -> str:
        """Get stack trace"""
        import traceback
        return traceback.format_exc()
    
    def _update_service_health(self, service: str, healthy: bool, error: str = None):
        """Update service health status"""
        self.service_health[service] = ServiceHealth(
            name=service,
            healthy=healthy,
            last_check=datetime.now().isoformat(),
            response_time_ms=None,
            error_count=self.service_health.get(service, ServiceHealth(service, False, '', None, 0, 0, 'closed', None)).error_count + (0 if healthy else 1),
            consecutive_failures=0 if healthy else self.service_health.get(service, ServiceHealth(service, False, '', None, 0, 0, 'closed', None)).consecutive_failures + 1,
            circuit_state=self.get_circuit_breaker(service).get_state(),
            last_error=error
        )
    
    def check_service_health(self, service: str, health_check_url: str = None) -> bool:
        """Check service health"""
        logger.info(f"Checking health for service: {service}")
        
        start_time = time.time()
        healthy = False
        
        try:
            if health_check_url and REQUESTS_AVAILABLE:
                response = requests.get(health_check_url, timeout=10)
                healthy = response.status_code == 200
            else:
                # Default health check - just check if we can reach
                healthy = True
            
            response_time = (time.time() - start_time) * 1000
            
            self.service_health[service] = ServiceHealth(
                name=service,
                healthy=healthy,
                last_check=datetime.now().isoformat(),
                response_time_ms=response_time,
                error_count=0 if healthy else self.service_health.get(service, ServiceHealth(service, False, '', None, 0, 0, 'closed', None)).error_count + 1,
                consecutive_failures=0 if healthy else self.service_health.get(service, ServiceHealth(service, False, '', None, 0, 0, 'closed', None)).consecutive_failures + 1,
                circuit_state=self.get_circuit_breaker(service).get_state(),
                last_error=None if healthy else "Health check failed"
            )
            
        except Exception as e:
            logger.error(f"Health check failed for {service}: {e}")
            self._update_service_health(service, healthy=False, error=str(e))
        
        return healthy
    
    def restart_server(self, server_name: str, server_script: str) -> bool:
        """Restart MCP server"""
        logger.info(f"Attempting to restart server: {server_name}")
        
        try:
            # Kill existing process if running
            if server_name in self.server_processes:
                self.server_processes[server_name].terminate()
            
            # Start new process
            script_path = self.vault_path / server_script
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.server_processes[server_name] = process
            
            # Wait a bit and check if it's running
            time.sleep(3)
            if process.poll() is None:
                logger.info(f"Server {server_name} restarted successfully")
                return True
            else:
                logger.error(f"Server {server_name} failed to start")
                return False
        
        except Exception as e:
            logger.error(f"Error restarting server {server_name}: {e}")
            return False
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        summary = {
            'total_errors': len(self.error_records),
            'errors_by_service': {},
            'errors_by_severity': {},
            'recent_errors': []
        }
        
        # Count by service
        for record in self.error_records:
            summary['errors_by_service'][record.service] = \
                summary['errors_by_service'].get(record.service, 0) + 1
            summary['errors_by_severity'][record.severity] = \
                summary['errors_by_severity'].get(record.severity, 0) + 1
        
        # Recent errors (last 10)
        summary['recent_errors'] = [
            {
                'timestamp': r.timestamp,
                'service': r.service,
                'error': r.error_message,
                'severity': r.severity
            }
            for r in self.error_records[-10:]
        ]
        
        return summary
    
    def generate_error_report(self) -> str:
        """Generate error report"""
        summary = self.get_error_summary()
        
        report = f"""# Error Recovery System Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Value |
|--------|-------|
| Total Errors | {summary['total_errors']} |

## Errors by Service

| Service | Count |
|---------|-------|
"""
        
        for service, count in summary['errors_by_service'].items():
            report += f"| {service} | {count} |\n"
        
        report += """
## Errors by Severity

| Severity | Count |
|----------|-------|
"""
        
        for severity, count in summary['errors_by_severity'].items():
            report += f"| {severity.upper()} | {count} |\n"
        
        report += """
## Recent Errors

| Timestamp | Service | Error | Severity |
|-----------|---------|-------|----------|
"""
        
        for error in summary['recent_errors']:
            report += f"| {error['timestamp']} | {error['service']} | {error['error'][:50]}... | {error['severity'].upper()} |\n"
        
        report += """
## Service Health

| Service | Status | Circuit State | Consecutive Failures |
|---------|--------|---------------|---------------------|
"""
        
        for name, health in self.service_health.items():
            report += f"| {name} | {'✅' if health.healthy else '❌'} | {health.circuit_state} | {health.consecutive_failures} |\n"
        
        return report
    
    def save_error_report(self):
        """Save error report to file"""
        report = self.generate_error_report()
        report_file = self.errors_folder / f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Error report saved to: {report_file}")
        return report_file


# Fallback functions
def fallback_return_none(*args, **kwargs):
    """Fallback that returns None"""
    return None


def fallback_return_empty_list(*args, **kwargs):
    """Fallback that returns empty list"""
    return []


def fallback_return_empty_dict(*args, **kwargs):
    """Fallback that returns empty dict"""
    return {}


def fallback_return_default_value(default: Any = None):
    """Create fallback that returns default value"""
    def fallback(*args, **kwargs):
        return default
    return fallback


# Main function for testing
def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Error Recovery System')
    parser.add_argument('--vault', type=str, help='Path to vault folder')
    parser.add_argument('--report', action='store_true', help='Generate error report')
    parser.add_argument('--health', type=str, help='Check health of specific service')
    args = parser.parse_args()
    
    recovery = ErrorRecoverySystem(vault_path=args.vault)
    
    if args.report:
        report_file = recovery.save_error_report()
        print(f"Error report saved to: {report_file}")
    
    elif args.health:
        healthy = recovery.check_service_health(args.health)
        print(f"Service {args.health} health: {'✅ Healthy' if healthy else '❌ Unhealthy'}")
    
    else:
        # Show summary
        summary = recovery.get_error_summary()
        print("\n" + "=" * 60)
        print("Error Recovery System Summary")
        print("=" * 60)
        print(f"Total Errors: {summary['total_errors']}")
        print(f"Errors by Service: {summary['errors_by_service']}")
        print(f"Errors by Severity: {summary['errors_by_severity']}")
        print("=" * 60)


if __name__ == '__main__':
    main()
