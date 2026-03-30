#!/usr/bin/env python3
"""
Ralph Wiggum Reasoning Loop - Runner Script
Copied from skill_reasoning_loop.md for standalone execution

Usage:
    python skills/ralph_loop_runner.py "Your task prompt here"
"""

import os
import sys
import json
import time
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# ============================================================================
# Configuration
# ============================================================================

DEFAULT_MAX_ITERATIONS = 10
DEFAULT_MODEL = "qwen-plus"
COMPLETION_TAG = "<promise>COMPLETE</promise>"
MAX_BACKOFF = 16  # Maximum backoff delay in seconds
BASE_BACKOFF = 1  # Base backoff delay in seconds

# ============================================================================
# Setup Logging
# ============================================================================

def setup_logging(vault_path: Path) -> logging.Logger:
    """Configure logging to file and console"""
    log_dir = vault_path / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "ralph_loop.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Logger
    logger = logging.getLogger("ralph_loop")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class IterationRecord:
    """Record of a single iteration"""
    iteration: int
    timestamp: str
    prompt: str
    response: str
    is_complete: bool
    execution_time: float
    api_calls: int
    error: Optional[str] = None


@dataclass
class LoopState:
    """Complete state of the reasoning loop"""
    task_prompt: str
    status: str  # running, completed, max_iterations, error, stopped
    iteration: int
    max_iterations: int
    started_at: str
    last_updated: str
    vault_path: str
    state_file: str
    iterations: List[Dict]
    final_response: Optional[str]
    error: Optional[str]
    total_api_calls: int
    total_time: float

# ============================================================================
# Qwen API Wrapper
# ============================================================================

class QwenAPI:
    """Wrapper for Qwen DashScope API with retry logic"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.model = model
        self.client = None
        self.available = False
        
        # Try to import DashScope
        if self.api_key:
            try:
                import dashscope
                from dashscope import Generation
                dashscope.api_key = self.api_key
                self.client = Generation
                self.available = True
                logging.info(f"Qwen API initialized with model: {model}")
            except ImportError:
                logging.warning("DashScope package not installed. Run: pip install dashscope")
            except Exception as e:
                logging.warning(f"Failed to initialize Qwen API: {e}")
        else:
            logging.warning("No API key provided. Running in SIMULATED mode.")
    
    def call(self, prompt: str, max_retries: int = 5) -> Dict[str, Any]:
        """
        Call Qwen API with exponential backoff
        
        Returns:
            dict with keys: success, response, error, api_calls
        """
        api_calls = 0
        last_error = None
        
        for attempt in range(max_retries):
            try:
                api_calls += 1
                
                if not self.available:
                    # Simulated mode
                    return {
                        "success": True,
                        "response": self._generate_simulated_response(prompt),
                        "error": None,
                        "api_calls": api_calls
                    }
                
                # Call real API
                response = self.client.call(
                    model=self.model,
                    prompt=prompt,
                    result_format='message'
                )
                
                if response.status_code == 200:
                    content = response.output.choices[0].message.content
                    return {
                        "success": True,
                        "response": content,
                        "error": None,
                        "api_calls": api_calls
                    }
                else:
                    last_error = f"API error: {response.status_code}"
                    logging.warning(f"API call failed (attempt {attempt + 1}): {last_error}")
                    
            except Exception as e:
                last_error = str(e)
                logging.warning(f"API call exception (attempt {attempt + 1}): {last_error}")
            
            # Exponential backoff
            if attempt < max_retries - 1:
                delay = min(BASE_BACKOFF * (2 ** attempt), MAX_BACKOFF)
                logging.info(f"Retrying in {delay}s...")
                time.sleep(delay)
        
        return {
            "success": False,
            "response": None,
            "error": last_error,
            "api_calls": api_calls
        }
    
    def _generate_simulated_response(self, prompt: str) -> str:
        """Generate simulated response for testing without API key"""
        return f"""## Simulated Response

This is a simulated response because no API key was provided.

**Task Analysis:**
The task would be analyzed by Qwen API in real execution.

**Proposed Action:**
In real execution, the AI would propose specific actions here.

**Status:**
- Iteration progress: Ongoing
- Completion: Not yet signaled

To enable real AI responses:
1. Set DASHSCOPE_API_KEY environment variable
2. Install dashscope: pip install dashscope
3. Run again with valid API key

<promise>COMPLETE</promise>
"""

# ============================================================================
# State Manager
# ============================================================================

class StateManager:
    """Manages state persistence and retrieval"""
    
    def __init__(self, vault_path: Path, logger: logging.Logger):
        self.vault_path = vault_path
        self.plans_dir = vault_path / "plans"
        self.plans_dir.mkdir(exist_ok=True)
        self.logger = logger
    
    def create_state_file(self, task_prompt: str, max_iterations: int) -> Path:
        """Create new state file with initial data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_hash = hashlib.md5(task_prompt.encode()).hexdigest()[:8]
        
        state_file = self.plans_dir / f"ralph_state_{timestamp}_{task_hash}.md"
        json_file = self.plans_dir / f"ralph_state_{timestamp}_{task_hash}.json"
        
        initial_state = LoopState(
            task_prompt=task_prompt,
            status="running",
            iteration=0,
            max_iterations=max_iterations,
            started_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            vault_path=str(self.vault_path),
            state_file=str(state_file),
            iterations=[],
            final_response=None,
            error=None,
            total_api_calls=0,
            total_time=0.0
        )
        
        self.save_state(state_file, json_file, initial_state)
        return state_file
    
    def save_state(self, md_file: Path, json_file: Path, state: LoopState):
        """Save state to both markdown and JSON files"""
        state.last_updated = datetime.now().isoformat()
        
        # Save as markdown
        md_content = self._state_to_markdown(state)
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # Save as JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(state), f, indent=2, default=str)
        
        self.logger.debug(f"State saved to: {md_file}")
    
    def load_state(self, state_file: Path) -> LoopState:
        """Load state from JSON file"""
        json_file = state_file.with_suffix('.json')
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return LoopState(**data)
        raise FileNotFoundError(f"State file not found: {json_file}")
    
    def _state_to_markdown(self, state: LoopState) -> str:
        """Convert state to markdown format"""
        iterations_md = ""
        for i, iteration in enumerate(state.iterations, 1):
            iterations_md += f"""
### Iteration {i}
- **Timestamp**: {iteration.get('timestamp', 'N/A')}
- **Duration**: {iteration.get('execution_time', 0):.2f}s
- **API Calls**: {iteration.get('api_calls', 0)}
- **Complete**: {iteration.get('is_complete', False)}
- **Response**: {iteration.get('response', 'N/A')[:500]}...
"""
            if iteration.get('error'):
                iterations_md += f"- **Error**: {iteration['error']}\n"
        
        return f"""---
metadata:
  task_prompt: "{state.task_prompt[:200]}..."
  status: "{state.status}"
  iteration: {state.iteration}
  max_iterations: {state.max_iterations}
  started_at: "{state.started_at}"
  last_updated: "{state.last_updated}"
  total_api_calls: {state.total_api_calls}
  total_time: {state.total_time:.2f}s
---

# Ralph Wiggum Reasoning Loop - State

## Current Status

| Field | Value |
|-------|-------|
| **Status** | {state.status.upper()} |
| **Iteration** | {state.iteration} / {state.max_iterations} |
| **Started** | {state.started_at} |
| **Last Updated** | {state.last_updated} |
| **Total API Calls** | {state.total_api_calls} |
| **Total Time** | {state.total_time:.2f}s |

## Task Prompt

{state.task_prompt}

## Iteration History
{iterations_md}

## Final Response

{state.final_response or "Not yet completed"}

## Error

{state.error or "None"}

---
*Generated by Ralph Wiggum Reasoning Loop Skill*
"""
    
    def update_dashboard(self, state: LoopState):
        """Update Dashboard.md with completion summary"""
        dashboard_file = self.vault_path / "Dashboard.md"
        
        # Create dashboard if it doesn't exist
        if not dashboard_file.exists():
            dashboard_file.write_text("# AI Employee Vault Dashboard\n\n")
        
        # Read existing content
        existing_content = dashboard_file.read_text(encoding='utf-8')
        
        # Create summary entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = f"""
## Reasoning Loop Completed - {timestamp}

| Metric | Value |
|--------|-------|
| **Task** | {state.task_prompt[:100]}... |
| **Status** | {state.status} |
| **Iterations** | {state.iteration} / {state.max_iterations} |
| **Duration** | {state.total_time:.2f}s |
| **API Calls** | {state.total_api_calls} |
| **State File** | [{state.state_file}]({state.state_file}) |

"""
        # Prepend to existing content
        new_content = existing_content + summary
        dashboard_file.write_text(new_content, encoding='utf-8')
        
        self.logger.info(f"Dashboard updated: {dashboard_file}")

# ============================================================================
# Reasoning Loop
# ============================================================================

class ReasoningLoop:
    """Main reasoning loop implementation"""
    
    def __init__(
        self,
        task_prompt: str,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        vault_path: Optional[Path] = None
    ):
        self.task_prompt = task_prompt
        self.max_iterations = max_iterations
        self.vault_path = vault_path or Path.cwd()
        
        # Initialize components
        self.logger = setup_logging(self.vault_path)
        self.api = QwenAPI()
        self.state_manager = StateManager(self.vault_path, self.logger)
        
        # Create initial state
        self.state_file = self.state_manager.create_state_file(task_prompt, max_iterations)
        self.state = self.state_manager.load_state(self.state_file)
        
        self.logger.info(f"Reasoning Loop initialized")
        self.logger.info(f"Task: {task_prompt[:100]}...")
        self.logger.info(f"Max iterations: {max_iterations}")
        self.logger.info(f"State file: {self.state_file}")
    
    def build_prompt(self, iteration: int) -> str:
        """Build prompt for Qwen API with context"""
        # Get previous iterations context
        context = ""
        if self.state.iterations:
            context = "\n\n## Previous Iterations:\n"
            for i, prev in enumerate(self.state.iterations, 1):
                context += f"""
### Iteration {i}
**Action**: {prev.get('response', 'N/A')[:300]}...
"""
        
        return f"""You are an autonomous AI agent completing a multi-step task.

## Original Task
{self.task_prompt}
{context}

## Current Iteration
You are on iteration {iteration + 1} of {self.max_iterations}.

## Instructions
1. Analyze the task and any previous work
2. Describe what action you are taking in this iteration
3. Explain what result you achieved
4. Identify what still needs to be done
5. If the task is COMPLETE, output exactly: <promise>COMPLETE</promise>

## Response Format
Provide a detailed response explaining your reasoning and actions.
End with <promise>COMPLETE</promise> ONLY if the task is fully complete.
"""
    
    def check_completion(self, response: str) -> bool:
        """Check if response contains completion signal"""
        return COMPLETION_TAG in response
    
    def run(self) -> LoopState:
        """Execute the reasoning loop"""
        self.logger.info("=" * 60)
        self.logger.info("Starting Reasoning Loop")
        self.logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            while self.state.iteration < self.state.max_iterations:
                iteration_start = time.time()
                self.state.iteration += 1
                
                self.logger.info(f"\n{'='*40}")
                self.logger.info(f"Iteration {self.state.iteration} / {self.state.max_iterations}")
                self.logger.info(f"{'='*40}")
                
                # Build prompt
                prompt = self.build_prompt(self.state.iteration - 1)
                
                # Call API
                self.logger.info("Calling Qwen API...")
                result = self.api.call(prompt)
                
                iteration_time = time.time() - iteration_start
                
                # Process response
                if result["success"]:
                    response = result["response"]
                    is_complete = self.check_completion(response)
                    
                    self.logger.info(f"Response received ({len(response)} chars)")
                    self.logger.info(f"Execution time: {iteration_time:.2f}s")
                    
                    if is_complete:
                        self.logger.info("[OK] Completion signal detected!")
                    
                    # Record iteration
                    record = IterationRecord(
                        iteration=self.state.iteration,
                        timestamp=datetime.now().isoformat(),
                        prompt=prompt[:2000],
                        response=response,
                        is_complete=is_complete,
                        execution_time=iteration_time,
                        api_calls=result["api_calls"]
                    )
                    
                    self.state.iterations.append(asdict(record))
                    self.state.total_api_calls += result["api_calls"]
                    
                    if is_complete:
                        self.state.status = "completed"
                        self.state.final_response = response
                        self.state.total_time = time.time() - start_time
                        break
                else:
                    # API failed
                    self.logger.error(f"API call failed: {result['error']}")
                    record = IterationRecord(
                        iteration=self.state.iteration,
                        timestamp=datetime.now().isoformat(),
                        prompt=prompt[:2000],
                        response="",
                        is_complete=False,
                        execution_time=iteration_time,
                        api_calls=result["api_calls"],
                        error=result["error"]
                    )
                    self.state.iterations.append(asdict(record))
                
                # Save state
                json_file = self.state_file.with_suffix('.json')
                self.state_manager.save_state(self.state_file, json_file, self.state)
                
                # Small delay between iterations
                time.sleep(0.5)
            
            # Final status
            if self.state.status == "running":
                if self.state.iteration >= self.state.max_iterations:
                    self.state.status = "max_iterations"
                    self.logger.warning(f"Max iterations ({self.max_iterations}) reached")
            
            self.state.total_time = time.time() - start_time
            
            # Final save
            json_file = self.state_file.with_suffix('.json')
            self.state_manager.save_state(self.state_file, json_file, self.state)
            
            # Update dashboard
            self.state_manager.update_dashboard(self.state)
            
            self.logger.info("\n" + "=" * 60)
            self.logger.info(f"Loop finished: {self.state.status}")
            self.logger.info(f"Total iterations: {self.state.iteration}")
            self.logger.info(f"Total time: {self.state.total_time:.2f}s")
            self.logger.info(f"Total API calls: {self.state.total_api_calls}")
            self.logger.info("=" * 60)
            
        except KeyboardInterrupt:
            self.state.status = "stopped"
            self.state.error = "Interrupted by user"
            json_file = self.state_file.with_suffix('.json')
            self.state_manager.save_state(self.state_file, json_file, self.state)
            self.logger.info("Loop interrupted by user")
        
        except Exception as e:
            self.state.status = "error"
            self.state.error = str(e)
            json_file = self.state_file.with_suffix('.json')
            self.state_manager.save_state(self.state_file, json_file, self.state)
            self.logger.error(f"Loop error: {e}")
            raise
        
        return self.state

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for CLI"""
    if len(sys.argv) < 2:
        print("Usage: /ralph-loop \"task prompt here\"")
        print("   or: python skills/ralph_loop_runner.py \"task prompt here\"")
        print("\nExample:")
        print('  /ralph-loop "Write a blog post about AI automation"')
        sys.exit(1)
    
    task_prompt = sys.argv[1]
    
    # Get vault path from environment or use current directory
    vault_path = Path(os.getenv("VAULT_PATH", Path.cwd()))
    
    # Get max iterations from environment or use default
    max_iterations = int(os.getenv("RALPH_MAX_ITERATIONS", DEFAULT_MAX_ITERATIONS))
    
    print(f"\n{'='*60}")
    print("Ralph Wiggum Reasoning Loop")
    print(f"{'='*60}")
    print(f"Task: {task_prompt[:100]}...")
    print(f"Max Iterations: {max_iterations}")
    print(f"Vault Path: {vault_path}")
    print(f"{'='*60}\n")
    
    # Run the loop
    loop = ReasoningLoop(
        task_prompt=task_prompt,
        max_iterations=max_iterations,
        vault_path=vault_path
    )
    
    result = loop.run()
    
    # Print summary
    print(f"\n{'='*60}")
    print("EXECUTION COMPLETE")
    print(f"{'='*60}")
    print(f"Status: {result.status}")
    print(f"Iterations: {result.iteration} / {result.max_iterations}")
    print(f"Total Time: {result.total_time:.2f}s")
    print(f"API Calls: {result.total_api_calls}")
    print(f"State File: {result.state_file}")
    print(f"{'='*60}\n")
    
    if result.status == "completed":
        print("[OK] Task completed successfully!")
    elif result.status == "max_iterations":
        print("[WARN] Max iterations reached - task may be incomplete")
    elif result.status == "error":
        print(f"[ERROR] Error: {result.error}")
    
    return 0 if result.status == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
