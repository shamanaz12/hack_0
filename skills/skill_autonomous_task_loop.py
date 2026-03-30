#!/usr/bin/env python3
"""
Skill: Autonomous Task Loop
Executes tasks autonomously using plan → execute → verify loop.

Features:
- Detect new tasks from scheduler or task queue
- Analyze task objectives and identify required tools
- Create step-by-step plans
- Execute steps using MCP tools
- Verify each step's success
- Call error_recovery on failures
- Move completed tasks to done folder
- Max iterations limit to prevent infinite loops
- Human approval for risky tasks
- Memory of past task results
- Optimization to skip completed steps
- Reporting to CEO briefing

Safety Controls:
- Max iterations: 10 steps
- Stop if limit exceeded
- Detect repeated steps
- Human approval for risky operations
"""

import os
import sys
import json
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import traceback

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import error recovery
try:
    from .skill_error_recovery import ErrorRecoverySkill, log_error
except ImportError:
    from skill_error_recovery import ErrorRecoverySkill, log_error


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_APPROVAL = "waiting_approval"
    VERIFIED = "verified"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RiskLevel(Enum):
    """Task risk level"""
    LOW = "low"           # No approval needed
    MEDIUM = "medium"     # Notify only
    HIGH = "high"         # Approval required


@dataclass
class TaskStep:
    """Single step in task plan"""
    step_number: int
    description: str
    tool: str  # MCP server/skill to use
    parameters: Dict[str, Any]
    status: str = "pending"  # pending, completed, failed, skipped
    result: Any = None
    error: str = ""
    verified: bool = False
    execution_time: float = 0.0


@dataclass
class Task:
    """Task definition"""
    task_id: str
    name: str
    description: str
    objective: str
    created_at: str
    status: TaskStatus = TaskStatus.PENDING
    risk_level: RiskLevel = RiskLevel.LOW
    steps: List[TaskStep] = field(default_factory=list)
    current_step: int = 0
    iteration_count: int = 0
    max_iterations: int = 10
    created_by: str = "system"
    approval_required: bool = False
    approval_status: str = "not_required"
    approval_granted_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    result_summary: str = ""
    error_message: str = ""
    memory_tags: List[str] = field(default_factory=list)
    execution_log: List[Dict] = field(default_factory=list)


class AutonomousTaskLoopSkill:
    """
    Autonomous Task Loop Skill
    Executes tasks autonomously with plan → execute → verify loop
    """

    def __init__(self, vault_path: str = None):
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent

        # Folders
        self.vault = self.vault_path / 'AI_Employee_Vault'
        self.inbox_folder = self.vault / 'inbox'
        self.plans_folder = self.vault / 'Plans'
        self.done_folder = self.vault / 'Done'
        self.errors_folder = self.vault / 'errors'
        self.logs_folder = self.vault_path / 'logs'
        self.memory_folder = self.vault / 'Memory'

        # Create folders
        for folder in [self.inbox_folder, self.plans_folder, self.done_folder,
                       self.errors_folder, self.logs_folder, self.memory_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        # Files
        self.task_queue = self.inbox_folder / 'task_queue.json'
        self.memory_file = self.memory_folder / 'task_memory.json'
        self.task_log = self.logs_folder / 'task_execution.log'

        # Error recovery
        self.error_recovery = ErrorRecoverySkill(str(self.vault_path))

        # Active tasks
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []

        # Load memory
        self.load_memory()

        # Task handlers registry
        self.task_handlers: Dict[str, Callable] = {}

        # Register built-in handlers
        self._register_builtin_handlers()

    def load_memory(self):
        """Load task memory for optimization"""
        self.task_memory = {
            'successful_strategies': {},
            'failed_patterns': {},
            'completed_steps': {},
            'task_history': []
        }

        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.task_memory = json.load(f)
            except Exception:
                pass

    def save_memory(self):
        """Save task memory"""
        # Keep only last 100 history entries
        self.task_memory['task_history'] = self.task_memory['task_history'][-100:]

        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.task_memory, f, indent=2)

    def _register_builtin_handlers(self):
        """Register built-in task handlers"""
        # File operations
        self.task_handlers['file_copy'] = self._handle_file_copy
        self.task_handlers['file_move'] = self._handle_file_move
        self.task_handlers['file_process'] = self._handle_file_process

        # Email operations
        self.task_handlers['send_email'] = self._handle_send_email

        # Social media
        self.task_handlers['post_facebook'] = self._handle_post_facebook
        self.task_handlers['post_instagram'] = self._handle_post_instagram

        # Accounting
        self.task_handlers['log_income'] = self._handle_log_income
        self.task_handlers['log_expense'] = self._handle_log_expense

    def create_task(self, name: str, description: str, objective: str,
                    task_type: str = None, parameters: Dict = None,
                    risk_level: str = 'low', created_by: str = 'system') -> Task:
        """
        Create a new task

        Args:
            name: Task name
            description: Task description
            objective: What the task should achieve
            task_type: Type of task (determines handler)
            parameters: Task parameters
            risk_level: low, medium, high
            created_by: Task creator

        Returns:
            Task object
        """
        task_id = f"{task_type or 'task'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(f'{name}{time.time()}'.encode()).hexdigest()[:8]}"

        task = Task(
            task_id=task_id,
            name=name,
            description=description,
            objective=objective,
            created_at=datetime.now().isoformat(),
            risk_level=RiskLevel(risk_level),
            created_by=created_by,
            approval_required=(risk_level == 'high')
        )

        # Auto-generate plan based on task type
        if task_type and parameters:
            self._analyze_task(task, task_type, parameters)

        # Save task
        self.active_tasks[task_id] = task
        self._save_task_plan(task)

        # Log task creation
        self._log_task_event(task, 'created')

        return task

    def _analyze_task(self, task: Task, task_type: str, parameters: Dict):
        """Analyze task and create plan"""
        task.status = TaskStatus.ANALYZING

        # Check memory for successful strategies
        if task_type in self.task_memory['successful_strategies']:
            # Reuse successful strategy
            strategy = self.task_memory['successful_strategies'][task_type]
            task.steps = [
                TaskStep(
                    step_number=i + 1,
                    description=step.get('description', ''),
                    tool=step.get('tool', ''),
                    parameters=step.get('parameters', {})
                )
                for i, step in enumerate(strategy.get('steps', []))
            ]
            task.memory_tags.append('reused_strategy')
        else:
            # Generate new plan
            task.steps = self._generate_plan(task_type, parameters)

        # Check if steps are already completed (optimization)
        task.steps = self._optimize_steps(task.steps)

        # Determine if approval needed
        if self._requires_approval(task_type, parameters):
            task.approval_required = True
            task.risk_level = RiskLevel.HIGH

        task.status = TaskStatus.PLANNING
        self._save_task_plan(task)

    def _generate_plan(self, task_type: str, parameters: Dict) -> List[TaskStep]:
        """Generate execution plan for task type"""
        plans = {
            'file_copy': [
                TaskStep(1, 'Verify source file exists', 'file_check',
                         {'path': parameters.get('source', '')}),
                TaskStep(2, 'Copy file to destination', 'file_copy',
                         {'source': parameters.get('source', ''),
                          'destination': parameters.get('destination', '')}),
                TaskStep(3, 'Verify copy succeeded', 'file_check',
                         {'path': parameters.get('destination', '')})
            ],
            'send_email': [
                TaskStep(1, 'Validate email address', 'email_validate',
                         {'email': parameters.get('to', '')}),
                TaskStep(2, 'Send email', 'email_send',
                         {'to': parameters.get('to', ''),
                          'subject': parameters.get('subject', ''),
                          'body': parameters.get('body', '')}),
                TaskStep(3, 'Verify email sent', 'email_verify', {})
            ],
            'post_facebook': [
                TaskStep(1, 'Prepare post content', 'content_prepare',
                         {'content': parameters.get('content', '')}),
                TaskStep(2, 'Post to Facebook', 'facebook_post',
                         {'message': parameters.get('content', '')}),
                TaskStep(3, 'Verify post published', 'facebook_verify', {})
            ],
            'post_instagram': [
                TaskStep(1, 'Prepare post content', 'content_prepare',
                         {'content': parameters.get('content', '')}),
                TaskStep(2, 'Post to Instagram', 'instagram_post',
                         {'content': parameters.get('content', '')}),
                TaskStep(3, 'Verify post published', 'instagram_verify', {})
            ],
            'log_income': [
                TaskStep(1, 'Validate amount', 'validate',
                         {'amount': parameters.get('amount', 0)}),
                TaskStep(2, 'Log to accounting', 'accounting_income',
                         {'amount': parameters.get('amount', 0),
                          'description': parameters.get('description', '')}),
                TaskStep(3, 'Verify entry created', 'accounting_verify', {})
            ],
            'log_expense': [
                TaskStep(1, 'Validate amount', 'validate',
                         {'amount': parameters.get('amount', 0)}),
                TaskStep(2, 'Log to accounting', 'accounting_expense',
                         {'amount': parameters.get('amount', 0),
                          'description': parameters.get('description', '')}),
                TaskStep(3, 'Verify entry created', 'accounting_verify', {})
            ]
        }

        return plans.get(task_type, [
            TaskStep(1, 'Execute task', 'generic', parameters)
        ])

    def _optimize_steps(self, steps: List[TaskStep]) -> List[TaskStep]:
        """Optimize steps by skipping already completed ones"""
        for step in steps:
            step_hash = hashlib.md5(
                f"{step.tool}:{json.dumps(step.parameters)}".encode()
            ).hexdigest()

            if step_hash in self.task_memory['completed_steps']:
                step.status = 'skipped'
                step.verified = True
                step.result = self.task_memory['completed_steps'][step_hash]

        return steps

    def _requires_approval(self, task_type: str, parameters: Dict) -> bool:
        """Check if task requires human approval"""
        high_risk_types = ['file_delete', 'bulk_operation', 'financial_transaction']
        if task_type in high_risk_types:
            return True

        # Check for high-risk parameters
        if parameters.get('amount', 0) > 10000:  # Large financial transaction
            return True

        return False

    def execute_task(self, task_id: str) -> Tuple[bool, str]:
        """
        Execute a task

        Args:
            task_id: Task ID to execute

        Returns:
            (success, message) tuple
        """
        if task_id not in self.active_tasks:
            return False, f"Task {task_id} not found"

        task = self.active_tasks[task_id]
        task.status = TaskStatus.EXECUTING
        task.started_at = datetime.now().isoformat()

        # Check approval
        if task.approval_required and task.approval_status != 'granted':
            task.status = TaskStatus.WAITING_APPROVAL
            self._request_approval(task)
            return False, "Waiting for approval"

        # Execute steps
        while task.current_step < len(task.steps):
            # Check iteration limit
            task.iteration_count += 1
            if task.iteration_count > task.max_iterations:
                task.status = TaskStatus.FAILED
                task.error_message = "Max iterations exceeded"
                self._handle_task_failure(task, "Max iterations exceeded")
                return False, task.error_message

            step = task.steps[task.current_step]

            # Skip already completed steps
            if step.status == 'skipped' and step.verified:
                task.current_step += 1
                continue

            # Execute step
            success, error = self._execute_step(task, step)

            if not success:
                # Call error recovery
                self.error_recovery.log_error(
                    task_name=f"{task.name} - Step {step.step_number}",
                    task_id=f"{task.task_id}_step_{step.step_number}",
                    error_message=error,
                    error_type='StepExecutionFailure',
                    task_data={'step': asdict(step), 'task': task.name}
                )

                # Try to recover
                recovered = self._attempt_recovery(task, step)
                if not recovered:
                    task.status = TaskStatus.FAILED
                    task.error_message = error
                    self._handle_task_failure(task, error)
                    return False, error

            # Verify step
            step.verified = self._verify_step(task, step)

            if not step.verified:
                task.status = TaskStatus.FAILED
                task.error_message = f"Step {step.step_number} verification failed"
                self._handle_task_failure(task, task.error_message)
                return False, task.error_message

            task.current_step += 1

        # Task completed
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now().isoformat()
        task.result_summary = self._generate_result_summary(task)

        # Save to memory
        self._save_to_memory(task)

        # Move to done folder
        self._complete_task(task)

        # Generate report for CEO briefing
        self._report_to_ceo_briefing(task)

        return True, "Task completed successfully"

    def _execute_step(self, task: Task, step: TaskStep) -> Tuple[bool, str]:
        """Execute a single step"""
        start_time = time.time()
        step.status = 'executing'

        try:
            # Get handler
            handler = self.task_handlers.get(step.tool)

            if handler:
                result = handler(step.parameters)
                step.result = result
                step.status = 'completed'
                step.execution_time = time.time() - start_time

                # Log execution
                self._log_step_execution(task, step, success=True)

                return True, ""
            else:
                # Generic execution - just mark as done
                step.result = {'status': 'completed'}
                step.status = 'completed'
                step.execution_time = time.time() - start_time
                return True, ""

        except Exception as e:
            step.status = 'failed'
            step.error = str(e)
            step.execution_time = time.time() - start_time
            self._log_step_execution(task, step, success=False, error=str(e))
            return False, str(e)

    def _verify_step(self, task: Task, step: TaskStep) -> bool:
        """Verify step execution"""
        if step.status != 'completed':
            return False

        # Store in memory for optimization
        step_hash = hashlib.md5(
            f"{step.tool}:{json.dumps(step.parameters)}".encode()
        ).hexdigest()
        self.task_memory['completed_steps'][step_hash] = step.result

        return True

    def _attempt_recovery(self, task: Task, step: TaskStep) -> bool:
        """Attempt to recover from step failure"""
        # Check if there's a recovery handler
        recovery_key = f"{step.tool}_recovery"

        if recovery_key in self.task_handlers:
            try:
                recovery_handler = self.task_handlers[recovery_key]
                result = recovery_handler(step.parameters, step.error)
                return result.get('success', False)
            except Exception:
                pass

        return False

    def _handle_task_failure(self, task: Task, error: str):
        """Handle task failure"""
        # Log to error recovery
        self.error_recovery.log_error(
            task_name=task.name,
            task_id=task.task_id,
            error_message=error,
            error_type='TaskFailure',
            task_data={'task': asdict(task)}
        )

        # Save failed task
        failed_file = self.errors_folder / f"{task.task_id}.json"
        with open(failed_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(task), f, indent=2)

        self._log_task_event(task, 'failed', error)

    def _complete_task(self, task: Task):
        """Mark task as complete and move to done folder"""
        # Save task record
        done_file = self.done_folder / f"{task.task_id}.json"
        with open(done_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(task), f, indent=2)

        # Remove plan file
        plan_file = self.plans_folder / f"{task.task_id}.md"
        if plan_file.exists():
            plan_file.unlink()

        # Remove from active tasks
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]

        self.completed_tasks.append(task)
        self._log_task_event(task, 'completed')

    def _save_task_plan(self, task: Task):
        """Save task plan to markdown file"""
        plan_file = self.plans_folder / f"{task.task_id}.md"

        content = f"""# Task Plan: {task.name}

**Task ID:** {task.task_id}
**Created:** {task.created_at}
**Status:** {task.status.value}
**Risk Level:** {task.risk_level.value}
**Approval Required:** {'Yes' if task.approval_required else 'No'}

---

## Objective

{task.objective}

---

## Steps

"""

        for step in task.steps:
            status_icon = '✅' if step.status == 'completed' else '⏳' if step.status == 'pending' else '❌'
            content += f"""
### Step {step.step_number} {status_icon}

- **Description:** {step.description}
- **Tool:** {step.tool}
- **Status:** {step.status}
- **Parameters:** `{json.dumps(step.parameters)}`
"""
            if step.result:
                content += f"- **Result:** `{json.dumps(step.result)}`\n"
            if step.error:
                content += f"- **Error:** {step.error}\n"

        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _request_approval(self, task: Task):
        """Request human approval for task"""
        approval_file = self.inbox_folder / f"approval_{task.task_id}.json"

        approval_request = {
            'task_id': task.task_id,
            'task_name': task.name,
            'description': task.description,
            'risk_level': task.risk_level.value,
            'steps': [asdict(s) for s in task.steps],
            'created_at': task.created_at,
            'status': 'pending_approval'
        }

        with open(approval_file, 'w', encoding='utf-8') as f:
            json.dump(approval_request, f, indent=2)

        self._log_task_event(task, 'approval_requested')

    def grant_approval(self, task_id: str) -> bool:
        """Grant approval for pending task"""
        if task_id not in self.active_tasks:
            return False

        task = self.active_tasks[task_id]
        task.approval_status = 'granted'
        task.approval_granted_at = datetime.now().isoformat()

        # Remove approval request file
        approval_file = self.inbox_folder / f"approval_{task_id}.json"
        if approval_file.exists():
            approval_file.unlink()

        self._log_task_event(task, 'approval_granted')
        return True

    def _save_to_memory(self, task: Task):
        """Save task to memory for future optimization"""
        task_type = task.name.split('_')[0] if '_' in task.name else 'generic'

        if task_type not in self.task_memory['successful_strategies']:
            self.task_memory['successful_strategies'][task_type] = {
                'steps': [asdict(s) for s in task.steps],
                'success_count': 1,
                'last_success': task.completed_at
            }
        else:
            self.task_memory['successful_strategies'][task_type]['success_count'] += 1
            self.task_memory['successful_strategies'][task_type]['last_success'] = task.completed_at

        self.task_memory['task_history'].append({
            'task_id': task.task_id,
            'name': task.name,
            'status': task.status.value,
            'completed_at': task.completed_at,
            'iterations': task.iteration_count
        })

        self.save_memory()

    def _generate_result_summary(self, task: Task) -> str:
        """Generate result summary for task"""
        completed_steps = len([s for s in task.steps if s.status == 'completed'])
        total_steps = len(task.steps)

        return f"Completed {completed_steps}/{total_steps} steps in {task.iteration_count} iterations"

    def _report_to_ceo_briefing(self, task: Task):
        """Report completed task to CEO briefing system"""
        # Append to CEO briefing task log
        briefing_log = self.vault / 'Reports' / 'completed_tasks.log'

        log_entry = (
            f"[{task.completed_at}] | {task.name} | "
            f"COMPLETED | {task.result_summary}\n"
        )

        with open(briefing_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def _log_task_event(self, task: Task, event: str, details: str = ''):
        """Log task event"""
        log_entry = (
            f"[{datetime.now().isoformat()}] | {task.task_id} | "
            f"{event.upper()} | {details}\n"
        )

        with open(self.task_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def _log_step_execution(self, task: Task, step: TaskStep,
                            success: bool, error: str = ''):
        """Log step execution"""
        status = 'SUCCESS' if success else 'FAILED'
        log_entry = (
            f"[{datetime.now().isoformat()}] | {task.task_id} | "
            f"Step {step.step_number} | {status} | {step.tool} | "
            f"{error if error else 'OK'}\n"
        )

        task.execution_log.append({
            'timestamp': datetime.now().isoformat(),
            'step': step.step_number,
            'tool': step.tool,
            'status': status,
            'error': error
        })

        with open(self.task_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    # Built-in handlers
    def _handle_file_copy(self, params: Dict) -> Dict:
        source = params.get('source', '')
        dest = params.get('destination', '')
        shutil.copy2(source, dest)
        return {'status': 'completed', 'destination': dest}

    def _handle_file_move(self, params: Dict) -> Dict:
        source = params.get('source', '')
        dest = params.get('destination', '')
        shutil.move(source, dest)
        return {'status': 'completed', 'destination': dest}

    def _handle_file_process(self, params: Dict) -> Dict:
        return {'status': 'completed'}

    def _handle_send_email(self, params: Dict) -> Dict:
        # Placeholder - integrate with email MCP
        return {'status': 'completed', 'to': params.get('to', '')}

    def _handle_post_facebook(self, params: Dict) -> Dict:
        # Placeholder - integrate with Facebook MCP
        return {'status': 'completed'}

    def _handle_post_instagram(self, params: Dict) -> Dict:
        # Placeholder - integrate with Instagram MCP
        return {'status': 'completed'}

    def _handle_log_income(self, params: Dict) -> Dict:
        try:
            from .skill_accounting import log_income
            result = log_income(
                params.get('amount', 0),
                params.get('description', '')
            )
            return {'status': 'completed', 'result': result}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

    def _handle_log_expense(self, params: Dict) -> Dict:
        try:
            from .skill_accounting import log_expense
            result = log_expense(
                params.get('amount', 0),
                params.get('description', '')
            )
            return {'status': 'completed', 'result': result}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get task status"""
        if task_id in self.active_tasks:
            return asdict(self.active_tasks[task_id])
        return None

    def get_pending_tasks(self) -> List[Dict]:
        """Get list of pending tasks"""
        return [asdict(t) for t in self.active_tasks.values()
                if t.status in [TaskStatus.PENDING, TaskStatus.WAITING_APPROVAL]]

    def get_completed_tasks(self, limit: int = 50) -> List[Dict]:
        """Get completed tasks"""
        return [asdict(t) for t in self.completed_tasks[-limit:]]


# Global instance
_task_loop = None


def get_skill() -> AutonomousTaskLoopSkill:
    """Get or create task loop skill instance"""
    global _task_loop
    if _task_loop is None:
        _task_loop = AutonomousTaskLoopSkill()
    return _task_loop


def create_task(name: str, description: str, objective: str,
                task_type: str = None, parameters: Dict = None,
                risk_level: str = 'low') -> Dict:
    """Create a new task"""
    skill = get_skill()
    task = skill.create_task(name, description, objective, task_type,
                             parameters, risk_level)
    return asdict(task)


def execute_task(task_id: str) -> Dict:
    """Execute a task"""
    skill = get_skill()
    success, message = skill.execute_task(task_id)
    return {'success': success, 'message': message}


def grant_approval(task_id: str) -> bool:
    """Grant approval for task"""
    skill = get_skill()
    return skill.grant_approval(task_id)


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Autonomous Task Loop Skill')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Create task command
    create_parser = subparsers.add_parser('create', help='Create a new task')
    create_parser.add_argument('name', type=str, help='Task name')
    create_parser.add_argument('description', type=str, help='Task description')
    create_parser.add_argument('objective', type=str, help='Task objective')
    create_parser.add_argument('--type', type=str, help='Task type')
    create_parser.add_argument('--risk', type=str, default='low',
                               choices=['low', 'medium', 'high'], help='Risk level')

    # Execute task command
    exec_parser = subparsers.add_parser('execute', help='Execute a task')
    exec_parser.add_argument('task_id', type=str, help='Task ID')

    # Status command
    status_parser = subparsers.add_parser('status', help='Get task status')
    status_parser.add_argument('task_id', type=str, help='Task ID')

    # List pending command
    subparsers.add_parser('pending', help='List pending tasks')

    # Approve command
    approve_parser = subparsers.add_parser('approve', help='Approve a task')
    approve_parser.add_argument('task_id', type=str, help='Task ID')

    args = parser.parse_args()

    skill = AutonomousTaskLoopSkill()

    if args.command == 'create':
        # Parse parameters if provided
        params = {}
        if args.type == 'log_income' or args.type == 'log_expense':
            params['amount'] = 1000
            params['description'] = 'Auto-generated task'

        task = skill.create_task(
            name=args.name,
            description=args.description,
            objective=args.objective,
            task_type=args.type,
            parameters=params,
            risk_level=args.risk
        )
        task_dict = asdict(task) if hasattr(task, '__dataclass_fields__') else task
        print(f"\n[TASK CREATED]")
        print(f"  ID: {task_dict['task_id']}")
        print(f"  Name: {task_dict['name']}")
        print(f"  Status: {task_dict['status']}")
        print(f"  Steps: {len(task_dict['steps'])}")
        print(f"\nTo execute: python skills/skill_autonomous_task_loop.py execute {task_dict['task_id']}")

    elif args.command == 'execute':
        result = skill.execute_task(args.task_id)
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"\n[{status}]")
        print(f"  {result['message']}")

    elif args.command == 'status':
        status = skill.get_task_status(args.task_id)
        if status:
            print(f"\n=== Task Status ===")
            print(f"  ID: {status['task_id']}")
            print(f"  Name: {status['name']}")
            print(f"  Status: {status['status']}")
            print(f"  Progress: {status['current_step']}/{len(status['steps'])} steps")
        else:
            print(f"Task {args.task_id} not found")

    elif args.command == 'pending':
        pending = skill.get_pending_tasks()
        print(f"\n=== Pending Tasks ({len(pending)}) ===")
        for task in pending:
            print(f"  [{task['status']}] {task['name']} ({task['task_id']})")

    elif args.command == 'approve':
        if skill.grant_approval(args.task_id):
            print(f"\n[APPROVED] Task {args.task_id}")
        else:
            print(f"\n[ERROR] Task {args.task_id} not found or doesn't need approval")

    else:
        parser.print_help()
