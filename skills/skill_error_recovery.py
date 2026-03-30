#!/usr/bin/env python3
"""
Skill: Error Recovery
Handles failures and recovers tasks automatically in the AI Employee System.

Features:
- Monitor MCP tasks and executions
- Detect failed tasks
- Capture error details (task name, timestamp, error message)
- Log errors to logs/errors.log (append mode)
- Move failed task data to AI_Employee_Vault/errors/
- Retry logic (wait 5 minutes, retry once)
- Final status tracking (RECOVERED or FAILED_FINAL)

Safety Rules:
- Do not break existing MCP servers
- Do not duplicate tasks
- Avoid infinite retry loops (max retry: 1)
"""

import os
import sys
import json
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import threading
import traceback

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class ErrorRecord:
    """Error record for tracking failures"""
    timestamp: str
    task_name: str
    task_id: str
    error_message: str
    error_type: str
    stack_trace: str
    source_file: str
    status: str  # 'pending', 'retrying', 'recovered', 'failed_final'
    retry_count: int = 0
    recovered_at: str = ""
    final_error: str = ""


class ErrorRecoverySkill:
    """
    Error Recovery Skill
    Handles failures and recovers tasks automatically
    """

    def __init__(self, vault_path: str = None):
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent

        # Folders
        self.logs_folder = self.vault_path / 'logs'
        self.errors_folder = self.vault_path / 'AI_Employee_Vault' / 'errors'
        self.plans_folder = self.vault_path / 'AI_Employee_Vault' / 'Plans'
        self.inbox_folder = self.vault_path / 'AI_Employee_Vault' / 'inbox'

        # Create folders
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        self.errors_folder.mkdir(parents=True, exist_ok=True)

        # Files
        self.error_log = self.logs_folder / 'errors.log'
        self.error_state = self.errors_folder / 'error_state.json'

        # Configuration
        self.max_retries = 1
        self.retry_delay_seconds = 300  # 5 minutes

        # In-memory tracking
        self.pending_errors: Dict[str, ErrorRecord] = {}
        self.recovery_history: List[ErrorRecord] = []

        # Load existing state
        self.load_state()

        # Retry timer
        self.retry_timers: Dict[str, threading.Timer] = {}

    def load_state(self):
        """Load error state from file"""
        if self.error_state.exists():
            try:
                with open(self.error_state, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    for record_data in state.get('pending_errors', []):
                        record = ErrorRecord(**record_data)
                        self.pending_errors[record.task_id] = record
                    self.recovery_history = [
                        ErrorRecord(**r) for r in state.get('history', [])
                    ]
            except Exception as e:
                self.log_error(
                    task_name='error_recovery',
                    task_id='state_load',
                    error_message=str(e),
                    error_type='StateLoadError',
                    source_file=str(self.error_state)
                )

    def save_state(self):
        """Save error state to file"""
        state = {
            'pending_errors': [asdict(r) for r in self.pending_errors.values()],
            'history': [asdict(r) for r in self.recovery_history[-100:]],  # Keep last 100
            'last_updated': datetime.now().isoformat()
        }

        with open(self.error_state, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

    def log_error(self, task_name: str, task_id: str, error_message: str,
                  error_type: str = 'Unknown', source_file: str = '',
                  stack_trace: str = None, task_data: Dict = None) -> ErrorRecord:
        """
        Log an error and initiate recovery process

        Args:
            task_name: Name of the failed task
            task_id: Unique task identifier
            error_message: Human-readable error message
            error_type: Type/category of error
            source_file: Source file where error occurred
            stack_trace: Full stack trace (optional)
            task_data: Task payload/data (optional)

        Returns:
            ErrorRecord for the error
        """
        if stack_trace is None:
            stack_trace = traceback.format_exc() if sys.exc_info()[0] else ''

        # Create error record
        record = ErrorRecord(
            timestamp=datetime.now().isoformat(),
            task_name=task_name,
            task_id=task_id,
            error_message=error_message,
            error_type=error_type,
            stack_trace=stack_trace,
            source_file=source_file,
            status='pending',
            retry_count=0
        )

        # Log to errors.log (append mode)
        self._append_to_error_log(record)

        # Move task data to errors folder if provided
        if task_data:
            self._move_task_data(task_id, task_data)

        # Add to pending errors
        self.pending_errors[task_id] = record

        # Save state
        self.save_state()

        # Schedule retry
        self._schedule_retry(record)

        return record

    def _append_to_error_log(self, record: ErrorRecord):
        """Append error to errors.log"""
        log_line = (
            f"[{record.timestamp}] | {record.task_name} | "
            f"{record.status.upper()} | {record.error_message}\n"
        )

        with open(self.error_log, 'a', encoding='utf-8') as f:
            f.write(log_line)

    def _move_task_data(self, task_id: str, task_data: Dict):
        """Move failed task data to errors folder"""
        error_file = self.errors_folder / f'{task_id}.json'

        error_data = {
            'task_id': task_id,
            'captured_at': datetime.now().isoformat(),
            'task_data': task_data
        }

        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, indent=2)

    def _schedule_retry(self, record: ErrorRecord):
        """Schedule retry for failed task"""
        if record.retry_count >= self.max_retries:
            return

        def retry_task():
            self._execute_retry(record)

        timer = threading.Timer(self.retry_delay_seconds, retry_task)
        self.retry_timers[record.task_id] = timer
        timer.start()

        # Update status
        record.status = 'retrying'
        record.retry_count += 1
        self.save_state()

    def _execute_retry(self, record: ErrorRecord):
        """Execute retry for failed task"""
        # Check if task has a recovery handler
        recovery_file = self.errors_folder / f'{record.task_id}_recovery.json'

        if recovery_file.exists():
            # Load recovery handler
            try:
                with open(recovery_file, 'r', encoding='utf-8') as f:
                    recovery_config = json.load(f)

                # Execute recovery based on config
                recovery_type = recovery_config.get('type', 'generic')

                if recovery_type == 'file_move':
                    # Move file back and retry operation
                    source = self.errors_folder / recovery_config.get('source_file', '')
                    dest = Path(recovery_config.get('dest_file', ''))

                    if source.exists():
                        shutil.move(str(source), str(dest))
                        record.status = 'recovered'
                        record.recovered_at = datetime.now().isoformat()
                        self._log_recovery(record)

                elif recovery_type == 'function_call':
                    # Call recovery function
                    module_name = recovery_config.get('module', '')
                    function_name = recovery_config.get('function', '')

                    if module_name and function_name:
                        try:
                            module = __import__(module_name, fromlist=[''])
                            func = getattr(module, function_name)
                            result = func(record.task_id, recovery_config.get('args', {}))

                            if result.get('success', False):
                                record.status = 'recovered'
                                record.recovered_at = datetime.now().isoformat()
                                self._log_recovery(record)
                            else:
                                record.status = 'failed_final'
                                record.final_error = result.get('error', 'Recovery failed')
                                self._log_final_failure(record)

                        except Exception as e:
                            record.status = 'failed_final'
                            record.final_error = str(e)
                            self._log_final_failure(record)

            except Exception as e:
                record.status = 'failed_final'
                record.final_error = str(e)
                self._log_final_failure(record)
        else:
            # Generic retry - just mark for manual review
            record.status = 'failed_final'
            record.final_error = 'No recovery handler - manual review required'
            self._log_final_failure(record)

        # Clean up timer
        if record.task_id in self.retry_timers:
            del self.retry_timers[record.task_id]

        # Save state
        self.save_state()

    def _log_recovery(self, record: ErrorRecord):
        """Log successful recovery"""
        log_line = (
            f"[{datetime.now().isoformat()}] | {record.task_name} | "
            f"RECOVERED | Task recovered after {record.retry_count} retry(ies)\n"
        )

        with open(self.error_log, 'a', encoding='utf-8') as f:
            f.write(log_line)

        # Move to history
        self.recovery_history.append(record)
        if record.task_id in self.pending_errors:
            del self.pending_errors[record.task_id]

        self.save_state()

    def _log_final_failure(self, record: ErrorRecord):
        """Log final failure after all retries exhausted"""
        log_line = (
            f"[{datetime.now().isoformat()}] | {record.task_name} | "
            f"FAILED_FINAL | {record.final_error}\n"
        )

        with open(self.error_log, 'a', encoding='utf-8') as f:
            f.write(log_line)

        # Move to history
        self.recovery_history.append(record)
        if record.task_id in self.pending_errors:
            del self.pending_errors[record.task_id]

        self.save_state()

    def register_recovery_handler(self, task_id: str, recovery_type: str,
                                   config: Dict):
        """
        Register a recovery handler for a task

        Args:
            task_id: Task identifier
            recovery_type: Type of recovery ('file_move', 'function_call', 'generic')
            config: Recovery configuration
        """
        recovery_file = self.errors_folder / f'{task_id}_recovery.json'

        recovery_config = {
            'task_id': task_id,
            'type': recovery_type,
            'registered_at': datetime.now().isoformat(),
            **config
        }

        with open(recovery_file, 'w', encoding='utf-8') as f:
            json.dump(recovery_config, f, indent=2)

    def get_pending_errors(self) -> List[ErrorRecord]:
        """Get list of pending errors"""
        return list(self.pending_errors.values())

    def get_recovery_history(self, limit: int = 50) -> List[ErrorRecord]:
        """Get recovery history"""
        return self.recovery_history[-limit:]

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        pending = list(self.pending_errors.values())
        history = self.recovery_history

        return {
            'pending_count': len(pending),
            'recovered_count': len([r for r in history if r.status == 'recovered']),
            'failed_count': len([r for r in history if r.status == 'failed_final']),
            'total_retries': sum(r.retry_count for r in history),
            'recovery_rate': (
                len([r for r in history if r.status == 'recovered']) / len(history) * 100
                if history else 0
            )
        }

    def clear_old_errors(self, days: int = 30):
        """Clear errors older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)

        # Clear from history
        self.recovery_history = [
            r for r in self.recovery_history
            if datetime.fromisoformat(r.timestamp) > cutoff
        ]

        # Clear old error files
        for error_file in self.errors_folder.glob('*.json'):
            try:
                mtime = datetime.fromtimestamp(error_file.stat().st_mtime)
                if mtime < cutoff:
                    error_file.unlink()
            except Exception:
                pass

        self.save_state()


# Global instance
_error_recovery = None


def get_skill() -> ErrorRecoverySkill:
    """Get or create error recovery skill instance"""
    global _error_recovery
    if _error_recovery is None:
        _error_recovery = ErrorRecoverySkill()
    return _error_recovery


def log_error(task_name: str, task_id: str, error_message: str,
              error_type: str = 'Unknown', source_file: str = '',
              task_data: Dict = None) -> Dict:
    """
    Log an error for recovery

    Args:
        task_name: Name of the failed task
        task_id: Unique task identifier
        error_message: Error message
        error_type: Type of error
        source_file: Source file
        task_data: Task payload

    Returns:
        JSON dict with error record
    """
    skill = get_skill()
    record = skill.log_error(
        task_name=task_name,
        task_id=task_id,
        error_message=error_message,
        error_type=error_type,
        source_file=source_file,
        task_data=task_data
    )
    return asdict(record)


def register_recovery(task_id: str, recovery_type: str, config: Dict) -> bool:
    """
    Register recovery handler for a task

    Args:
        task_id: Task identifier
        recovery_type: Type of recovery
        config: Recovery configuration

    Returns:
        True if registered successfully
    """
    skill = get_skill()
    skill.register_recovery_handler(task_id, recovery_type, config)
    return True


def get_error_summary() -> Dict:
    """Get error summary"""
    skill = get_skill()
    return skill.get_error_summary()


# Decorator for automatic error recovery
def with_error_recovery(task_name: str = None):
    """
    Decorator for automatic error recovery

    Usage:
        @with_error_recovery(task_name='my_task')
        def my_function(...):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            name = task_name or func.__name__
            task_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_error(
                    task_name=name,
                    task_id=task_id,
                    error_message=str(e),
                    error_type=type(e).__name__,
                    source_file=func.__module__
                )
                raise
        return wrapper
    return decorator


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Error Recovery Skill')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Log error command
    log_parser = subparsers.add_parser('log', help='Log an error')
    log_parser.add_argument('task_name', type=str, help='Task name')
    log_parser.add_argument('task_id', type=str, help='Task ID')
    log_parser.add_argument('error_message', type=str, help='Error message')
    log_parser.add_argument('--type', type=str, default='Unknown', help='Error type')
    log_parser.add_argument('--source', type=str, default='', help='Source file')

    # Summary command
    subparsers.add_parser('summary', help='Get error summary')

    # List pending command
    subparsers.add_parser('pending', help='List pending errors')

    # Clear old command
    clear_parser = subparsers.add_parser('clear', help='Clear old errors')
    clear_parser.add_argument('--days', type=int, default=30, help='Days to keep')

    args = parser.parse_args()

    skill = ErrorRecoverySkill()

    if args.command == 'log':
        record = skill.log_error(
            task_name=args.task_name,
            task_id=args.task_id,
            error_message=args.error_message,
            error_type=args.type,
            source_file=args.source
        )
        print(f"\n[ERROR LOGGED]")
        print(f"  Task: {record.task_name}")
        print(f"  ID: {record.task_id}")
        print(f"  Status: {record.status}")
        print(f"  Message: {record.error_message}")

    elif args.command == 'summary':
        summary = skill.get_error_summary()
        print(f"\n=== Error Recovery Summary ===")
        print(f"  Pending: {summary['pending_count']}")
        print(f"  Recovered: {summary['recovered_count']}")
        print(f"  Failed Final: {summary['failed_count']}")
        print(f"  Total Retries: {summary['total_retries']}")
        print(f"  Recovery Rate: {summary['recovery_rate']:.1f}%")

    elif args.command == 'pending':
        pending = skill.get_pending_errors()
        print(f"\n=== Pending Errors ({len(pending)}) ===")
        for error in pending:
            print(f"  [{error.status}] {error.task_name} ({error.task_id})")
            print(f"    Error: {error.error_message}")
            print(f"    Retries: {error.retry_count}")

    elif args.command == 'clear':
        skill.clear_old_errors(args.days)
        print(f"\n[CLEARED] Errors older than {args.days} days")

    else:
        parser.print_help()
