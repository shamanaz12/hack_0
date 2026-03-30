"""
Error Recovery & Graceful Degradation System
Implements circuit breakers, retry logic, and fallback mechanisms
"""

import os
import json
import logging
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/error_recovery.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half_open'
    
    def __init__(self, name: str, failure_threshold: int = 5, 
                 recovery_timeout: int = 60, half_open_max_calls: int = 3):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = self.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            if not self._can_execute():
                raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is open")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _can_execute(self) -> bool:
        """Check if execution is allowed"""
        if self.state == self.CLOSED:
            return True
        
        if self.state == self.OPEN:
            if self.last_failure_time and \
               datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = self.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        
        if self.state == self.HALF_OPEN:
            if self.half_open_calls < self.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False
        
        return False
    
    def _on_success(self):
        """Handle successful execution"""
        with self._lock:
            if self.state == self.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.half_open_max_calls:
                    self.state = self.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    logger.info(f"Circuit breaker {self.name} closed after successful recovery")
            else:
                self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed execution"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.state == self.HALF_OPEN:
                self.state = self.OPEN
                logger.warning(f"Circuit breaker {self.name} opened from half-open state")
            elif self.failure_count >= self.failure_threshold:
                self.state = self.OPEN
                logger.warning(f"Circuit breaker {self.name} opened after {self.failure_count} failures")
    
    def get_status(self) -> Dict:
        """Get circuit breaker status"""
        return {
            'name': self.name,
            'state': self.state,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'half_open_calls': self.half_open_calls
        }
    
    def reset(self):
        """Reset circuit breaker"""
        with self._lock:
            self.state = self.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.half_open_calls = 0
            logger.info(f"Circuit breaker {self.name} manually reset")


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class RetryPolicy:
    """Retry policy with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, exponential_base: float = 2.0,
                 retryable_exceptions: tuple = (Exception,)):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except self.retryable_exceptions as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = min(
                        self.base_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries + 1} failed. "
                        f"Retrying in {delay:.2f}s. Error: {str(e)}"
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries + 1} attempts failed. "
                        f"Last error: {str(e)}"
                    )
        
        raise last_exception


class FallbackHandler:
    """Fallback mechanism for graceful degradation"""
    
    def __init__(self):
        self.fallbacks: Dict[str, Callable] = {}
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: Dict[str, datetime] = {}
    
    def register_fallback(self, operation_name: str, fallback_func: Callable):
        """Register fallback function for an operation"""
        self.fallbacks[operation_name] = fallback_func
        logger.info(f"Registered fallback for operation: {operation_name}")
    
    def execute_with_fallback(self, operation_name: str, primary_func: Callable, 
                               *args, **kwargs) -> Any:
        """Execute primary function with fallback"""
        try:
            return primary_func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary operation {operation_name} failed: {str(e)}")
            
            # Try cache first
            cached_value = self._get_from_cache(operation_name)
            if cached_value is not None:
                logger.info(f"Returning cached value for {operation_name}")
                return cached_value
            
            # Try registered fallback
            if operation_name in self.fallbacks:
                try:
                    logger.info(f"Executing fallback for {operation_name}")
                    result = self.fallbacks[operation_name](*args, **kwargs)
                    self._cache_value(operation_name, result)
                    return result
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed for {operation_name}: {str(fallback_error)}")
            
            # Return default fallback
            return self._default_fallback(operation_name, e)
    
    def _cache_value(self, key: str, value: Any, ttl_seconds: int = 300):
        """Cache a value with TTL"""
        self.cache[key] = value
        self.cache_ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self.cache:
            if datetime.now() < self.cache_ttl.get(key, datetime.now()):
                return self.cache[key]
            else:
                # Expired
                del self.cache[key]
                if key in self.cache_ttl:
                    del self.cache_ttl[key]
        return None
    
    def _default_fallback(self, operation_name: str, error: Exception) -> Any:
        """Default fallback that returns safe default values"""
        logger.error(f"No fallback available for {operation_name}, returning default")
        
        # Return type-specific defaults
        if 'get' in operation_name.lower() or 'list' in operation_name.lower():
            return []
        elif 'count' in operation_name.lower():
            return 0
        elif 'summary' in operation_name.lower():
            return {'error': str(error), 'fallback': True}
        else:
            return {'success': False, 'error': str(error), 'fallback': True}


class ErrorRecoverySystem:
    """Main error recovery and graceful degradation system"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_policies: Dict[str, RetryPolicy] = {}
        self.fallback_handler = FallbackHandler()
        self.error_log: List[Dict] = []
        self.max_error_log_size = 1000
        
        # Initialize default circuit breakers
        self._init_default_circuit_breakers()
        
        # Initialize default retry policies
        self._init_default_retry_policies()
        
        logger.info("Error Recovery System initialized")
    
    def _init_default_circuit_breakers(self):
        """Initialize default circuit breakers for services"""
        services = [
            'odoo', 'facebook', 'instagram', 'twitter', 
            'gmail', 'whatsapp', 'ai_api'
        ]
        
        for service in services:
            self.circuit_breakers[service] = CircuitBreaker(
                name=service,
                failure_threshold=5,
                recovery_timeout=60
            )
    
    def _init_default_retry_policies(self):
        """Initialize default retry policies"""
        # Standard retry policy
        self.retry_policies['standard'] = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0
        )
        
        # Aggressive retry policy for critical operations
        self.retry_policies['aggressive'] = RetryPolicy(
            max_retries=5,
            base_delay=0.5,
            max_delay=60.0
        )
        
        # Conservative retry policy for non-critical operations
        self.retry_policies['conservative'] = RetryPolicy(
            max_retries=2,
            base_delay=2.0,
            max_delay=10.0
        )
    
    def execute_with_recovery(self, service: str, operation: str, 
                               func: Callable, *args, 
                               use_retry: bool = True,
                               retry_policy: str = 'standard',
                               **kwargs) -> Any:
        """Execute operation with full error recovery"""
        start_time = datetime.now()
        
        try:
            # Check circuit breaker
            if service in self.circuit_breakers:
                cb = self.circuit_breakers[service]
                result = cb.call(func, *args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Log success
            self._log_operation(service, operation, start_time, success=True)
            return result
            
        except CircuitBreakerOpenError as e:
            # Circuit breaker is open - use fallback
            logger.warning(f"Circuit breaker open for {service}, using fallback")
            self._log_operation(service, operation, start_time, 
                               success=False, error=str(e), circuit_breaker_open=True)
            return self.fallback_handler._default_fallback(operation, e)
            
        except Exception as e:
            # Log error
            self._log_operation(service, operation, start_time, 
                               success=False, error=str(e))
            
            # Try retry if enabled
            if use_retry and retry_policy in self.retry_policies:
                try:
                    policy = self.retry_policies[retry_policy]
                    result = policy.execute(func, *args, **kwargs)
                    self._log_operation(service, operation, start_time, 
                                       success=True, retried=True)
                    return result
                except Exception as retry_error:
                    logger.error(f"Retry also failed: {str(retry_error)}")
            
            # Use fallback
            return self.fallback_handler.execute_with_fallback(
                operation, func, *args, **kwargs
            )
    
    def _log_operation(self, service: str, operation: str, 
                       start_time: datetime, success: bool, 
                       error: str = None, circuit_breaker_open: bool = False,
                       retried: bool = False):
        """Log operation result"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'service': service,
            'operation': operation,
            'success': success,
            'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
            'error': error,
            'circuit_breaker_open': circuit_breaker_open,
            'retried': retried
        }
        
        self.error_log.append(log_entry)
        
        # Trim log if too large
        if len(self.error_log) > self.max_error_log_size:
            self.error_log = self.error_log[-self.max_error_log_size:]
        
        # Log to file
        if not success:
            logger.error(f"Operation failed: {json.dumps(log_entry)}")
        else:
            logger.info(f"Operation completed: {json.dumps(log_entry)}")
    
    def get_service_health(self, service: str) -> Dict:
        """Get health status for a service"""
        if service not in self.circuit_breakers:
            return {'status': 'unknown', 'service': service}
        
        cb = self.circuit_breakers[service]
        status = cb.get_status()
        
        # Calculate error rate from recent logs
        recent_errors = [
            e for e in self.error_log[-100:] 
            if e['service'] == service and not e['success']
        ]
        
        status['recent_error_count'] = len(recent_errors)
        status['health_score'] = self._calculate_health_score(service)
        
        return status
    
    def _calculate_health_score(self, service: str) -> float:
        """Calculate health score for a service (0-100)"""
        recent_logs = [e for e in self.error_log[-100:] if e['service'] == service]
        
        if not recent_logs:
            return 100.0
        
        success_count = sum(1 for e in recent_logs if e['success'])
        return (success_count / len(recent_logs)) * 100
    
    def get_all_health_status(self) -> Dict:
        """Get health status for all services"""
        return {
            service: self.get_service_health(service)
            for service in self.circuit_breakers
        }
    
    def get_error_report(self, hours: int = 24) -> Dict:
        """Generate error report for the specified period"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        filtered_logs = [
            e for e in self.error_log
            if datetime.fromisoformat(e['timestamp']) > cutoff
        ]
        
        # Group by service
        by_service = {}
        for log in filtered_logs:
            service = log['service']
            if service not in by_service:
                by_service[service] = {'total': 0, 'errors': 0}
            by_service[service]['total'] += 1
            if not log['success']:
                by_service[service]['errors'] += 1
        
        # Group by error type
        error_types = {}
        for log in filtered_logs:
            if log.get('error'):
                error_type = type(log.get('error', '')).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'period_hours': hours,
            'generated_at': datetime.now().isoformat(),
            'total_operations': len(filtered_logs),
            'total_errors': sum(1 for e in filtered_logs if not e['success']),
            'by_service': by_service,
            'error_types': error_types,
            'circuit_breaker_status': {
                name: cb.get_status() 
                for name, cb in self.circuit_breakers.items()
            }
        }
    
    def reset_circuit_breaker(self, service: str):
        """Manually reset a circuit breaker"""
        if service in self.circuit_breakers:
            self.circuit_breakers[service].reset()
            logger.info(f"Circuit breaker reset for service: {service}")
        else:
            logger.warning(f"No circuit breaker found for service: {service}")
    
    def register_fallback(self, operation_name: str, fallback_func: Callable):
        """Register a fallback function"""
        self.fallback_handler.register_fallback(operation_name, fallback_func)


# Decorator for easy error recovery integration
def with_error_recovery(service: str, operation: str = None, 
                        retry: bool = True, policy: str = 'standard'):
    """Decorator for adding error recovery to functions"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            recovery_system = ErrorRecoverySystem()
            op_name = operation or func.__name__
            return recovery_system.execute_with_recovery(
                service, op_name, func, *args,
                use_retry=retry, retry_policy=policy,
                **kwargs
            )
        return wrapper
    return decorator


# Global error recovery system instance
error_recovery_system = ErrorRecoverySystem()


if __name__ == '__main__':
    print("Error Recovery & Graceful Degradation System")
    print("=" * 50)
    
    # Test circuit breaker
    cb = CircuitBreaker('test', failure_threshold=3, recovery_timeout=5)
    
    def failing_function():
        raise Exception("Simulated failure")
    
    def working_function():
        return "Success!"
    
    print("\nTesting circuit breaker...")
    
    # Test working function
    try:
        result = cb.call(working_function)
        print(f"Working function: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test failing function
    print("\nTesting failing function (should trip circuit breaker)...")
    for i in range(5):
        try:
            result = cb.call(failing_function)
            print(f"Attempt {i+1}: {result}")
        except CircuitBreakerOpenError as e:
            print(f"Attempt {i+1}: Circuit breaker open - {e}")
        except Exception as e:
            print(f"Attempt {i+1}: {e}")
    
    # Get status
    print(f"\nCircuit breaker status: {cb.get_status()}")
    
    # Test error recovery system
    print("\n\nTesting Error Recovery System...")
    health = error_recovery_system.get_all_health_status()
    print(f"Service health: {json.dumps(health, indent=2)}")
    
    # Get error report
    report = error_recovery_system.get_error_report(24)
    print(f"\nError report: {json.dumps(report, indent=2)}")
