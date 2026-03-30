"""
Ralph Loop - Iterative AI Task Execution Pattern

Mimics the "Ralph Wiggum pattern" - repeatedly calls AI API with task context
and current state until a completion condition is met.

Features:
- Takes a task file path and completion condition
- Repeatedly calls Qwen API with task context and current state
- Max iteration count to prevent infinite loops
- Writes intermediate results to state file in /Plans folder
- Full logging and state persistence
"""
import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

# Try to import qwen SDK, fallback to API calls if not available
try:
    from dashscope import Generation
    import dashscope
    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False
    import requests


# Configure logging
log_dir = Path(__file__).parent / 'logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'ralph_loop.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LoopStatus(Enum):
    """Status of the ralph loop"""
    RUNNING = "running"
    COMPLETED = "completed"
    MAX_ITERATIONS = "max_iterations_reached"
    ERROR = "error"
    STOPPED = "stopped_by_user"


@dataclass
class LoopState:
    """State container for ralph loop"""
    task_file: str
    completion_condition: str
    status: str
    iteration: int
    max_iterations: int
    started_at: str
    last_updated: str
    iterations_data: List[Dict[str, Any]]
    final_result: Optional[str]
    error: Optional[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LoopState':
        return cls(**data)


class RalphLoop:
    """
    Ralph Loop - Iterative AI Task Execution
    
    This pattern repeatedly calls an AI API with:
    1. The original task context
    2. The current state of work
    3. Previous iteration results
    
    Until either:
    - Completion condition is met
    - Max iterations reached
    - Error occurs
    """
    
    def __init__(
        self,
        task_file: str,
        completion_condition: Callable[[Dict], bool],
        max_iterations: int = 10,
        plans_folder: str = None,
        api_key: str = None,
        model: str = "qwen-plus"
    ):
        """
        Initialize Ralph Loop
        
        Args:
            task_file: Path to the task markdown file
            completion_condition: Function that checks if task is complete
                                  Takes state dict, returns bool
            max_iterations: Maximum number of iterations before stopping
            plans_folder: Folder to store state files (default: AI_Employee_Vault/Plans)
            api_key: Qwen API key (or set DASHSCOPE_API_KEY env var)
            model: Qwen model to use
        """
        self.task_file = Path(task_file)
        self.completion_condition = completion_condition
        self.max_iterations = max_iterations
        self.plans_folder = Path(plans_folder) if plans_folder else None
        self.model = model
        
        # Set API key
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        if QWEN_AVAILABLE and self.api_key:
            dashscope.api_key = self.api_key
        
        # Initialize state
        self.state = self._create_initial_state()
        self._stop_requested = False
        
        logger.info(f"Ralph Loop initialized for task: {task_file}")
        logger.info(f"Max iterations: {max_iterations}")
        logger.info(f"Model: {model}")

    def _create_initial_state(self) -> LoopState:
        """Create initial loop state"""
        now = datetime.now().isoformat()
        
        # Read task file
        task_content = ""
        if self.task_file.exists():
            with open(self.task_file, 'r', encoding='utf-8') as f:
                task_content = f.read()
        else:
            logger.warning(f"Task file not found: {self.task_file}")
        
        return LoopState(
            task_file=str(self.task_file),
            completion_condition=self.completion_condition.__doc__ or "Custom condition",
            status=LoopStatus.RUNNING.value,
            iteration=0,
            max_iterations=self.max_iterations,
            started_at=now,
            last_updated=now,
            iterations_data=[],
            final_result=None,
            error=None
        )

    def _get_state_file_path(self) -> Path:
        """Get path to state file in Plans folder"""
        if self.plans_folder is None:
            self.plans_folder = Path(__file__).parent / 'AI_Employee_Vault' / 'Plans'
        
        os.makedirs(self.plans_folder, exist_ok=True)
        
        # Create state file name from task file name
        task_name = self.task_file.stem
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return self.plans_folder / f"ralph_state_{task_name}_{timestamp}.md"

    def _save_state(self, state_file: Path):
        """Save current state to file"""
        # Create markdown content with state
        content = f"""---
metadata:
  task_file: "{self.state.task_file}"
  status: "{self.state.status}"
  iteration: {self.state.iteration}
  max_iterations: {self.state.max_iterations}
  started_at: "{self.state.started_at}"
  last_updated: "{self.state.last_updated}"
  completion_condition: "{self.state.completion_condition}"
---

# Ralph Loop State

## Current Status
| Field | Value |
|-------|-------|
| **Status** | {self.state.status.upper()} |
| **Iteration** | {self.state.iteration} / {self.state.max_iterations} |
| **Started** | {self.state.started_at} |
| **Last Updated** | {self.state.last_updated} |

## Task File
```
{self.task_file.read_text(encoding='utf-8') if self.task_file.exists() else "File not found"}
```

## Iteration History

"""
        # Add iteration history
        for i, iteration_data in enumerate(self.state.iterations_data, 1):
            content += f"""### Iteration {i}
**Timestamp:** {iteration_data.get('timestamp', 'N/A')}
**Prompt:** {iteration_data.get('prompt', 'N/A')[:500]}...
**Response:** {iteration_data.get('response', 'N/A')[:500]}...
**Analysis:** {iteration_data.get('analysis', 'N/A')}

"""
        
        if self.state.final_result:
            content += f"""## Final Result
{self.state.final_result}
"""
        
        if self.state.error:
            content += f"""## Error
{self.state.error}
"""
        
        # Save to file
        with open(state_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Also save JSON for programmatic access
        json_file = state_file.with_suffix('.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.state.to_dict(), f, indent=2, default=str)
        
        logger.debug(f"State saved to: {state_file}")

    def _load_task_content(self) -> str:
        """Load task content from file"""
        if not self.task_file.exists():
            return ""
        
        with open(self.task_file, 'r', encoding='utf-8') as f:
            return f.read()

    def _build_prompt(self, iteration: int, previous_results: List[Dict]) -> str:
        """Build prompt for Qwen API"""
        task_content = self._load_task_content()
        
        # Build context from previous iterations
        context = ""
        if previous_results:
            context = "\n\n## Previous Iterations:\n"
            for i, result in enumerate(previous_results, 1):
                context += f"""
### Iteration {i}
**Action Taken:** {result.get('action', 'N/A')}
**Result:** {result.get('result', 'N/A')}
**Next Steps:** {result.get('next_steps', 'N/A')}
"""
        
        prompt = f"""You are working on a task iteratively. This is iteration {iteration}.

## Original Task:
{task_content}
{context}

## Current State:
- Iteration: {iteration} / {self.max_iterations}
- Status: {self.state.status}

## Instructions:
1. Analyze the task and previous work
2. Describe what action should be taken in this iteration
3. Explain what result you expect
4. Identify what still needs to be done

## Response Format:
{{
    "action": "What action to take in this iteration",
    "result": "Expected result from this action",
    "next_steps": "What still needs to be done after this iteration",
    "is_complete": false  // Set to true if task appears complete
}}
"""
        return prompt

    def _call_qwen_api(self, prompt: str) -> Dict[str, Any]:
        """Call Qwen API and parse response"""
        if QWEN_AVAILABLE and self.api_key:
            # Use official SDK
            try:
                response = Generation.call(
                    model=self.model,
                    prompt=prompt,
                    result_format='message'
                )
                
                if response.status_code == 200:
                    content = response.output.choices[0].message.content
                    # Try to parse as JSON
                    try:
                        # Extract JSON from response
                        import re
                        json_match = re.search(r'\{[\s\S]*\}', content)
                        if json_match:
                            return json.loads(json_match.group())
                        return {"action": content, "result": "", "next_steps": "", "is_complete": False}
                    except json.JSONDecodeError:
                        return {"action": content, "result": "", "next_steps": "", "is_complete": False}
                else:
                    logger.error(f"API error: {response.status_code}")
                    return {"action": "", "result": f"API Error: {response.status_code}", "next_steps": "", "is_complete": False}
                    
            except Exception as e:
                logger.error(f"API call failed: {e}")
                return {"action": "", "result": f"Error: {str(e)}", "next_steps": "", "is_complete": False}
        else:
            # Fallback: simulate API call (for testing without API key)
            logger.warning("Qwen API not available, using simulated response")
            return {
                "action": f"Simulated action for iteration {self.state.iteration + 1}",
                "result": "Simulated result - configure API key for real responses",
                "next_steps": "Continue iterations or set up API key",
                "is_complete": self.state.iteration >= self.max_iterations - 1
            }

    def _check_completion(self, iteration_result: Dict) -> bool:
        """Check if completion condition is met"""
        # Build state dict for condition check
        state_dict = {
            'iteration': self.state.iteration,
            'max_iterations': self.state.max_iterations,
            'status': self.state.status,
            'last_result': iteration_result,
            'all_results': self.state.iterations_data,
            'task_file': str(self.task_file)
        }
        
        try:
            return self.completion_condition(state_dict)
        except Exception as e:
            logger.error(f"Completion condition error: {e}")
            return False

    def run(self, state_file: Path = None) -> LoopState:
        """
        Run the Ralph Loop until completion
        
        Args:
            state_file: Optional path to state file (auto-generated if not provided)
        
        Returns:
            Final LoopState
        """
        if state_file is None:
            state_file = self._get_state_file_path()
        
        logger.info("=" * 60)
        logger.info(f"Starting Ralph Loop")
        logger.info(f"Task: {self.task_file}")
        logger.info(f"State file: {state_file}")
        logger.info("=" * 60)
        
        try:
            while self.state.iteration < self.state.max_iterations:
                # Check for stop request
                if self._stop_requested:
                    self.state.status = LoopStatus.STOPPED.value
                    logger.info("Loop stopped by user")
                    break
                
                # Increment iteration
                self.state.iteration += 1
                self.state.last_updated = datetime.now().isoformat()
                
                logger.info(f"\n{'='*40}")
                logger.info(f"Iteration {self.state.iteration} / {self.state.max_iterations}")
                logger.info(f"{'='*40}")
                
                # Build prompt
                prompt = self._build_prompt(
                    self.state.iteration,
                    self.state.iterations_data
                )
                
                # Call API
                logger.info("Calling Qwen API...")
                iteration_result = self._call_qwen_api(prompt)
                
                # Log result
                logger.info(f"Action: {iteration_result.get('action', 'N/A')}")
                logger.info(f"Result: {iteration_result.get('result', 'N/A')}")
                logger.info(f"Next Steps: {iteration_result.get('next_steps', 'N/A')}")
                
                # Store iteration data
                self.state.iterations_data.append({
                    'iteration': self.state.iteration,
                    'timestamp': datetime.now().isoformat(),
                    'prompt': prompt[:2000],  # Truncate for storage
                    'response': str(iteration_result),
                    'analysis': iteration_result.get('action', ''),
                    'action': iteration_result.get('action', ''),
                    'result': iteration_result.get('result', ''),
                    'next_steps': iteration_result.get('next_steps', ''),
                    'is_complete': iteration_result.get('is_complete', False)
                })
                
                # Save state
                self._save_state(state_file)
                logger.info(f"State saved to: {state_file}")
                
                # Check completion condition
                if self._check_completion(iteration_result):
                    logger.info("\n✓ Completion condition met!")
                    self.state.status = LoopStatus.COMPLETED.value
                    self.state.final_result = str(iteration_result)
                    break
                
                # Check if API says complete
                if iteration_result.get('is_complete', False):
                    logger.info("\n✓ API indicates task is complete!")
                    self.state.status = LoopStatus.COMPLETED.value
                    self.state.final_result = str(iteration_result)
                    break
                
                # Small delay between iterations
                time.sleep(1)
            
            # Final status
            if self.state.status == LoopStatus.RUNNING.value:
                if self.state.iteration >= self.state.max_iterations:
                    self.state.status = LoopStatus.MAX_ITERATIONS.value
                    logger.info(f"\n⚠ Max iterations ({self.state.max_iterations}) reached")
            
            # Final save
            self._save_state(state_file)
            
            logger.info("\n" + "=" * 60)
            logger.info(f"Loop finished with status: {self.state.status}")
            logger.info(f"Total iterations: {self.state.iteration}")
            logger.info(f"State file: {state_file}")
            logger.info("=" * 60)
            
        except KeyboardInterrupt:
            self.state.status = LoopStatus.STOPPED.value
            self.state.error = "Stopped by user"
            self._save_state(state_file)
            logger.info("Loop interrupted by user")
            
        except Exception as e:
            self.state.status = LoopStatus.ERROR.value
            self.state.error = str(e)
            self._save_state(state_file)
            logger.error(f"Loop error: {e}")
            raise
        
        return self.state

    def stop(self):
        """Request loop to stop"""
        self._stop_requested = True
        logger.info("Stop requested")


def run_ralph_loop(
    task_file: str,
    completion_condition: Callable[[Dict], bool],
    max_iterations: int = 10,
    plans_folder: str = None,
    api_key: str = None
) -> LoopState:
    """
    Convenience function to run a Ralph Loop
    
    Args:
        task_file: Path to task markdown file
        completion_condition: Function to check if task is complete
        max_iterations: Maximum iterations
        plans_folder: Folder for state files
        api_key: Qwen API key
    
    Returns:
        Final LoopState
    """
    loop = RalphLoop(
        task_file=task_file,
        completion_condition=completion_condition,
        max_iterations=max_iterations,
        plans_folder=plans_folder,
        api_key=api_key
    )
    return loop.run()


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Ralph Loop - Iterative AI Task Execution')
    parser.add_argument('--task', type=str, required=True, help='Path to task file')
    parser.add_argument('--max-iterations', type=int, default=10, help='Maximum iterations')
    parser.add_argument('--output', type=str, help='Output folder for state files')
    parser.add_argument('--api-key', type=str, help='Qwen API key')
    args = parser.parse_args()
    
    # Example completion condition: check if task file moved to Done folder
    def file_moved_to_done(state: Dict) -> bool:
        """Check if task file has been moved to Done folder"""
        task_file = state.get('task_file', '')
        done_folder = Path(task_file).parent.parent / 'Done'
        done_file = done_folder / Path(task_file).name
        return done_file.exists()
    
    # Example completion condition: check if API says complete
    def api_says_complete(state: Dict) -> bool:
        """Check if last iteration result indicates completion"""
        last_result = state.get('last_result', {})
        return last_result.get('is_complete', False)
    
    # Run the loop
    print(f"Starting Ralph Loop for task: {args.task}")
    print(f"Max iterations: {args.max_iterations}")
    
    result = run_ralph_loop(
        task_file=args.task,
        completion_condition=api_says_complete,  # Change condition as needed
        max_iterations=args.max_iterations,
        plans_folder=args.output,
        api_key=args.api_key
    )
    
    print(f"\n{'='*60}")
    print(f"Final Status: {result.status}")
    print(f"Iterations: {result.iteration}")
    print(f"Final Result: {result.final_result}")
    print(f"{'='*60}")
