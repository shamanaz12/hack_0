"""
Advanced Ralph Wiggum Loop
Autonomous multi-step task execution with AI reasoning
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
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
        logging.FileHandler('logs/ralph_loop.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RalphLoopResult:
    """Result from Ralph Loop execution"""
    
    def __init__(self, status: str, iteration: int, 
                 max_iterations: int, all_results: List[Dict],
                 final_state: Dict = None):
        self.status = status  # completed, max_iterations_reached, error, stopped_by_user
        self.iteration = iteration
        self.max_iterations = max_iterations
        self.all_results = all_results
        self.final_state = final_state or {}
    
    def to_dict(self) -> Dict:
        return {
            'status': self.status,
            'iteration': self.iteration,
            'max_iterations': self.max_iterations,
            'all_results': self.all_results,
            'final_state': self.final_state
        }


class RalphLoop:
    """
    Advanced Ralph Wiggum Loop for autonomous multi-step execution
    
    The loop repeatedly calls AI with:
    1. Original task context
    2. Current state of work
    3. Previous iteration results
    
    Until completion or max iterations reached.
    """
    
    def __init__(self, task_file: str, 
                 completion_condition: Callable = None,
                 max_iterations: int = 10,
                 plans_folder: str = None,
                 api_key: str = None):
        self.task_file = Path(task_file)
        self.completion_condition = completion_condition
        self.max_iterations = max_iterations
        self.plans_folder = Path(plans_folder) if plans_folder else None
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY', '')
        
        self.state: Dict = {}
        self.iterations_data: List[Dict] = []
        self.all_results: List[Dict] = []
        self._stop_requested = False
        
        # Initialize state
        self._init_state()
        
        logger.info(f"Ralph Loop initialized for task: {task_file}")
    
    def _init_state(self):
        """Initialize loop state"""
        self.state = {
            'task_file': str(self.task_file),
            'status': 'initialized',
            'iteration': 0,
            'max_iterations': self.max_iterations,
            'started_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'task_content': '',
            'current_action': None,
            'completed_actions': [],
            'pending_actions': [],
            'errors': []
        }
        
        # Load task content
        if self.task_file.exists():
            self.state['task_content'] = self.task_file.read_text()
            self._parse_task_content()
        else:
            logger.warning(f"Task file not found: {self.task_file}")
            self.state['task_content'] = f"Task: {self.task_file.name}"
    
    def _parse_task_content(self):
        """Parse task file content to extract actions"""
        content = self.state['task_content']
        
        # Simple parsing - extract bullet points or numbered items as actions
        lines = content.split('\n')
        actions = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('*') or line[0].isdigit():
                # Clean up the action text
                action = line.lstrip('-*').strip()
                action = ''.join(c for c in action if not c.isdigit()).strip('.').strip()
                if action:
                    actions.append({
                        'action': action,
                        'status': 'pending',
                        'result': None
                    })
        
        if actions:
            self.state['pending_actions'] = actions
            logger.info(f"Parsed {len(actions)} actions from task file")
    
    def run(self, state_file: Path = None) -> RalphLoopResult:
        """Run the Ralph Loop"""
        logger.info("Starting Ralph Loop execution")
        self.state['status'] = 'running'
        
        try:
            for iteration in range(1, self.max_iterations + 1):
                if self._stop_requested:
                    logger.info("Stop requested by user")
                    return RalphLoopResult(
                        status='stopped_by_user',
                        iteration=iteration,
                        max_iterations=self.max_iterations,
                        all_results=self.all_results,
                        final_state=self.state
                    )
                
                # Execute iteration
                iteration_result = self._execute_iteration(iteration)
                self.iterations_data.append(iteration_result)
                self.all_results.append(iteration_result.get('result', {}))
                
                # Update state
                self.state['iteration'] = iteration
                self.state['last_updated'] = datetime.now().isoformat()
                
                # Save state
                self._save_state(state_file)
                
                # Check completion
                if self._check_completion(iteration_result):
                    logger.info(f"Completion condition met at iteration {iteration}")
                    self.state['status'] = 'completed'
                    self._save_state(state_file)
                    return RalphLoopResult(
                        status='completed',
                        iteration=iteration,
                        max_iterations=self.max_iterations,
                        all_results=self.all_results,
                        final_state=self.state
                    )
                
                # Small delay between iterations
                time.sleep(1)
            
            # Max iterations reached
            logger.warning(f"Max iterations ({self.max_iterations}) reached")
            self.state['status'] = 'max_iterations_reached'
            self._save_state(state_file)
            return RalphLoopResult(
                status='max_iterations_reached',
                iteration=self.max_iterations,
                max_iterations=self.max_iterations,
                all_results=self.all_results,
                final_state=self.state
            )
            
        except Exception as e:
            logger.error(f"Ralph Loop error: {str(e)}")
            self.state['status'] = 'error'
            self.state['errors'].append(str(e))
            self._save_state(state_file)
            return RalphLoopResult(
                status='error',
                iteration=self.state['iteration'],
                max_iterations=self.max_iterations,
                all_results=self.all_results,
                final_state=self.state
            )
    
    def _execute_iteration(self, iteration: int) -> Dict:
        """Execute a single iteration"""
        logger.info(f"Executing iteration {iteration}/{self.max_iterations}")
        
        iteration_start = datetime.now()
        
        # Build prompt for AI
        prompt = self._build_iteration_prompt(iteration)
        
        # Call AI
        ai_response = self._call_ai(prompt)
        
        # Process AI response
        action_result = self._process_ai_response(ai_response, iteration)
        
        # Update state based on result
        self._update_state_from_result(action_result)
        
        iteration_end = datetime.now()
        
        return {
            'iteration': iteration,
            'timestamp': iteration_start.isoformat(),
            'duration_seconds': (iteration_end - iteration_start).total_seconds(),
            'prompt': prompt[:500],  # Truncate for logging
            'ai_response': ai_response,
            'result': action_result,
            'state_updated': self.state.copy()
        }
    
    def _build_iteration_prompt(self, iteration: int) -> str:
        """Build prompt for AI iteration"""
        prompt = f"""You are an autonomous AI agent executing a task iteratively.

## Task Information
Task File: {self.task_file.name}

## Original Task
{self.state.get('task_content', 'No task content available')}

## Current State
- Iteration: {iteration}/{self.max_iterations}
- Status: {self.state.get('status', 'unknown')}
- Completed Actions: {len(self.state.get('completed_actions', []))}
- Pending Actions: {len(self.state.get('pending_actions', []))}

## Pending Actions
"""
        
        for i, action in enumerate(self.state.get('pending_actions', [])[:5], 1):
            prompt += f"{i}. {action.get('action', 'Unknown action')}\n"
        
        if len(self.state.get('pending_actions', [])) > 5:
            prompt += f"... and {len(self.state.get('pending_actions', [])) - 5} more actions\n"
        
        prompt += """
## Previous Iteration Results
"""
        
        if self.all_results:
            for i, result in enumerate(self.all_results[-3:], 1):
                prompt += f"Iteration {iteration - len(self.all_results) + i}: {json.dumps(result, indent=2)}\n"
        else:
            prompt += "No previous iterations yet.\n"
        
        prompt += """
## Your Task
Based on the current state and pending actions, determine:
1. What action to take next
2. How to execute it
3. What the expected outcome should be

Respond with a JSON object containing:
- action: The action to take
- parameters: Any parameters needed for the action
- expected_outcome: What you expect to achieve
- reasoning: Why you chose this action
"""
        
        return prompt
    
    def _call_ai(self, prompt: str) -> Dict:
        """Call AI API for decision making"""
        if not self.api_key:
            logger.warning("No API key available, using simulated response")
            return self._get_simulated_response(prompt)
        
        try:
            import dashscope
            from dashscope import Generation
            
            response = Generation.call(
                model='qwen-turbo',
                api_key=self.api_key,
                prompt=prompt
            )
            
            if response.status_code == 200:
                # Try to parse JSON from response
                response_text = response.output.text
                try:
                    # Find JSON in response
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx]
                        return json.loads(json_str)
                    else:
                        return {'raw_response': response_text}
                except json.JSONDecodeError:
                    return {'raw_response': response_text}
            else:
                logger.warning(f"AI API error: {response.code}")
                return self._get_simulated_response(prompt)
                
        except Exception as e:
            logger.error(f"AI API call error: {str(e)}")
            return self._get_simulated_response(prompt)
    
    def _get_simulated_response(self, prompt: str) -> Dict:
        """Get simulated AI response when API is unavailable"""
        pending = self.state.get('pending_actions', [])
        
        if pending:
            next_action = pending.pop(0)
            self.state['pending_actions'] = pending
            self.state['completed_actions'].append({
                **next_action,
                'status': 'completed',
                'completed_at': datetime.now().isoformat()
            })
            
            return {
                'action': next_action.get('action', 'Unknown'),
                'parameters': {},
                'expected_outcome': 'Action completed successfully',
                'reasoning': 'Selected next pending action from queue',
                'simulated': True
            }
        else:
            return {
                'action': 'complete_task',
                'parameters': {},
                'expected_outcome': 'All actions completed',
                'reasoning': 'No pending actions remaining',
                'simulated': True
            }
    
    def _process_ai_response(self, ai_response: Dict, iteration: int) -> Dict:
        """Process AI response and execute action"""
        action = ai_response.get('action', 'unknown')
        parameters = ai_response.get('parameters', {})
        
        logger.info(f"Iteration {iteration}: Executing action '{action}'")
        
        # Execute the action (in production, this would call actual tools/APIs)
        result = {
            'action': action,
            'parameters': parameters,
            'executed_at': datetime.now().isoformat(),
            'success': True,
            'output': f"Action '{action}' executed with parameters: {parameters}"
        }
        
        # Update pending/completed actions
        if self.state.get('pending_actions'):
            for i, pending_action in enumerate(self.state['pending_actions']):
                if action.lower() in pending_action.get('action', '').lower():
                    completed = self.state['pending_actions'].pop(i)
                    completed['status'] = 'completed'
                    completed['result'] = result
                    completed['completed_at'] = datetime.now().isoformat()
                    self.state['completed_actions'].append(completed)
                    break
        
        return result
    
    def _update_state_from_result(self, result: Dict):
        """Update state based on action result"""
        if result.get('success'):
            self.state['current_action'] = result.get('action')
        else:
            self.state['errors'].append(result.get('error', 'Unknown error'))
    
    def _check_completion(self, iteration_result: Dict) -> bool:
        """Check if task is complete"""
        # First check custom completion condition
        if self.completion_condition:
            try:
                if self.completion_condition(self.state):
                    return True
            except Exception as e:
                logger.error(f"Completion condition error: {str(e)}")
        
        # Check if all actions are completed
        if not self.state.get('pending_actions'):
            return True
        
        # Check if AI says task is complete
        result = iteration_result.get('result', {})
        if result.get('action') == 'complete_task':
            return True
        
        return False
    
    def _save_state(self, state_file: Path = None):
        """Save current state to file"""
        if state_file is None:
            state_file = self._get_default_state_file()
        
        if state_file is None:
            return
        
        try:
            # Ensure parent directory exists
            state_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as JSON
            json_state = {
                'metadata': {
                    'task_file': self.state.get('task_file'),
                    'status': self.state.get('status'),
                    'iteration': self.state.get('iteration'),
                    'max_iterations': self.state.get('max_iterations'),
                    'started_at': self.state.get('started_at'),
                    'last_updated': self.state.get('last_updated')
                },
                'state': self.state,
                'iterations': self.iterations_data,
                'all_results': self.all_results
            }
            
            with open(state_file.with_suffix('.json'), 'w') as f:
                json.dump(json_state, f, indent=2)
            
            # Save as Markdown
            md_content = self._generate_markdown_state()
            with open(state_file.with_suffix('.md'), 'w') as f:
                f.write(md_content)
            
            logger.info(f"State saved to: {state_file}")
            
        except Exception as e:
            logger.error(f"Error saving state: {str(e)}")
    
    def _get_default_state_file(self) -> Optional[Path]:
        """Get default state file path"""
        if self.plans_folder:
            return self.plans_folder / f"ralph_state_{self.task_file.stem}"
        
        # Default to task file location
        return self.task_file.parent / f"ralph_state_{self.task_file.stem}"
    
    def _generate_markdown_state(self) -> str:
        """Generate markdown representation of state"""
        md = f"""# Ralph Loop State

## Current Status
| Field | Value |
|-------|-------|
| **Status** | {self.state.get('status', 'unknown').upper()} |
| **Iteration** | {self.state.get('iteration', 0)} / {self.state.get('max_iterations', 0)} |
| **Started** | {self.state.get('started_at', 'N/A')} |
| **Last Updated** | {self.state.get('last_updated', 'N/A')} |
| **Task File** | {self.state.get('task_file', 'N/A')} |

## Progress Summary
- **Completed Actions:** {len(self.state.get('completed_actions', []))}
- **Pending Actions:** {len(self.state.get('pending_actions', []))}
- **Errors:** {len(self.state.get('errors', []))}

## Completed Actions
"""
        
        for action in self.state.get('completed_actions', []):
            md += f"- ✅ {action.get('action', 'Unknown')} (completed: {action.get('completed_at', 'N/A')})\n"
        
        md += "\n## Pending Actions\n"
        
        for action in self.state.get('pending_actions', []):
            md += f"- ⏳ {action.get('action', 'Unknown')}\n"
        
        md += "\n## Iteration History\n"
        
        for iteration in self.iterations_data[-5:]:  # Last 5 iterations
            md += f"\n### Iteration {iteration.get('iteration', '?')}\n"
            md += f"**Timestamp:** {iteration.get('timestamp', 'N/A')}\n"
            md += f"**Duration:** {iteration.get('duration_seconds', 0):.2f}s\n"
            
            result = iteration.get('result', {})
            md += f"**Action:** {result.get('action', 'N/A')}\n"
            md += f"**Success:** {'Yes' if result.get('success') else 'No'}\n"
        
        if self.state.get('errors'):
            md += "\n## Errors\n"
            for error in self.state.get('errors', []):
                md += f"- ❌ {error}\n"
        
        return md
    
    def stop(self):
        """Request loop to stop"""
        self._stop_requested = True
        logger.info("Stop requested")


def run_ralph_loop(task_file: str, 
                   completion_condition: Callable = None,
                   max_iterations: int = 10,
                   plans_folder: str = None,
                   api_key: str = None) -> RalphLoopResult:
    """Convenience function to run Ralph Loop"""
    loop = RalphLoop(
        task_file=task_file,
        completion_condition=completion_condition,
        max_iterations=max_iterations,
        plans_folder=plans_folder,
        api_key=api_key
    )
    return loop.run()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Ralph Wiggum Loop - Autonomous Task Execution')
    parser.add_argument('--task', '-t', required=True, help='Task file to execute')
    parser.add_argument('--max-iterations', '-m', type=int, default=10, help='Maximum iterations')
    parser.add_argument('--output', '-o', help='Output folder for state files')
    parser.add_argument('--api-key', '-k', help='Dashscope API key')
    
    args = parser.parse_args()
    
    print("Advanced Ralph Wiggum Loop")
    print("=" * 50)
    print(f"Task: {args.task}")
    print(f"Max Iterations: {args.max_iterations}")
    
    # Define simple completion condition
    def default_completion_condition(state):
        # Complete if no pending actions
        return len(state.get('pending_actions', [])) == 0
    
    # Run the loop
    result = run_ralph_loop(
        task_file=args.task,
        completion_condition=default_completion_condition,
        max_iterations=args.max_iterations,
        plans_folder=args.output,
        api_key=args.api_key
    )
    
    print("\n" + "=" * 50)
    print(f"Status: {result.status}")
    print(f"Iterations: {result.iteration}/{result.max_iterations}")
    print(f"Results: {len(result.all_results)} iterations executed")
    
    if result.final_state.get('completed_actions'):
        print(f"\nCompleted Actions: {len(result.final_state['completed_actions'])}")
        for action in result.final_state['completed_actions']:
            print(f"  ✅ {action.get('action', 'Unknown')}")
    
    if result.final_state.get('pending_actions'):
        print(f"\nPending Actions: {len(result.final_state['pending_actions'])}")
        for action in result.final_state['pending_actions']:
            print(f"  ⏳ {action.get('action', 'Unknown')}")
