---
name: reasoning-loop
description: Iterative AI task execution using the Ralph Wiggum pattern for multi-step autonomous tasks
version: 1.0.0
author: AI Employee Vault
created: 2026-03-23
updated: 2026-03-23
category: automation
tags:
  - ai
  - loop
  - autonomous
  - qwen
  - reasoning
parameters:
  - name: task_prompt
    type: string
    required: true
    description: High-level goal or task description to be executed iteratively
dependencies:
  - dashscope
  - requests
environment:
  - DASHSCOPE_API_KEY: Qwen API key (optional, falls back to simulated mode)
  - VAULT_PATH: Base path for vault folders (defaults to current directory)
---

# Reasoning Loop Skill

## Overview

This skill implements the **Ralph Wiggum pattern** - an iterative AI task execution approach that repeatedly calls the Qwen API with evolving context until a completion condition is met.

The loop continues until the AI outputs `<promise>COMPLETE</promise>` or the maximum iteration limit is reached.

## How It Works

1. **Initialize** - Load task prompt and create initial state
2. **Build Prompt** - Construct prompt with task context + previous iteration results
3. **Call AI** - Invoke Qwen API with the constructed prompt
4. **Parse Response** - Extract action, result, and check for completion marker
5. **Update State** - Save iteration data to state file
6. **Check Completion** - Look for `<promise>COMPLETE</promise>` in response
7. **Repeat** - Continue until complete or max iterations reached
8. **Summarize** - Update dashboard with completion summary

## Usage

### Bash Command Format

```bash
/ralph-loop "Your high-level task description here"
```

### Examples

```bash
# Simple task
/ralph-loop "Research Python best practices for async programming and create a summary document"

# Complex multi-step task
/ralph-loop "Analyze the codebase in ./src folder, identify code smells, create a report, and suggest refactoring improvements"

# Task with specific output
/ralph-loop "Create a README.md file for this project with installation instructions, usage examples, and API documentation"
```

### Programmatic Usage

```bash
python skills/skill_reasoning_loop.md "task prompt here"
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_prompt` | string | Yes | High-level goal or task description to be executed iteratively |

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `DASHSCOPE_API_KEY` | (none) | Qwen API key for real API calls |
| `VAULT_PATH` | Current directory | Base path for vault folders |
| `MAX_ITERATIONS` | 10 | Maximum loop iterations |
| `MODEL_NAME` | qwen-plus | Qwen model to use |

## Folder Structure

```
vault/
├── skills/
│   └── skill_reasoning_loop.md    # This skill file
├── plans/
│   └── ralph_state_*.md           # Iteration state files
├── logs/
│   └── ralph_loop.log             # Execution logs
└── Dashboard.md                   # Completion summary
```

---

## Implementation

```python
#!/usr/bin/env python3
"""
Ralph Wiggum Loop - Iterative AI Task Execution Skill

Implements autonomous multi-step task execution using Qwen API.
Continues iterating until AI outputs <promise>COMPLETE</promise>.
"""

import os
import sys
import json
import time
import random
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field

# Try to import dashscope SDK
try:
    from dashscope import Generation
    import dashscope
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    try:
        import requests
    except ImportError:
        requests = None


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class Config:
    """Configuration container"""
    vault_path: Path
    plans_folder: Path
    logs_folder: Path
    api_key: Optional[str]
    model: str
    max_iterations: int
    backoff_base: float
    backoff_max: float
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment"""
        vault_path = Path(os.getenv('VAULT_PATH', '.'))
        
        return cls(
            vault_path=vault_path,
            plans_folder=vault_path / 'plans',
            logs_folder=vault_path / 'logs',
            api_key=os.getenv('DASHSCOPE_API_KEY'),
            model=os.getenv('MODEL_NAME', 'qwen-plus'),
            max_iterations=int(os.getenv('MAX_ITERATIONS', '10')),
            backoff_base=float(os.getenv('BACKOFF_BASE', '2.0')),
            backoff_max=float(os.getenv('BACKOFF_MAX', '60.0'))
        )


# ============================================================================
# State Management
# ============================================================================

@dataclass
class IterationData:
    """Data from a single iteration"""
    iteration: int
    timestamp: str
    prompt: str
    response: str
    action: str
    result: str
    next_steps: str
    is_complete: bool


@dataclass 
class LoopState:
    """Complete state of the reasoning loop"""
    task_prompt: str
    status: str
    iteration: int
    max_iterations: int
    started_at: str
    last_updated: str
    iterations: List[IterationData] = field(default_factory=list)
    final_result: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LoopState':
        data['iterations'] = [IterationData(**i) if isinstance(i, dict) else i for i in data.get('iterations', [])]
        return cls(**data)


class StateManager:
    """Manages state persistence"""
    
    def __init__(self, plans_folder: Path):
        self.plans_folder = plans_folder
        os.makedirs(plans_folder, exist_ok=True)
    
    def get_state_file_path(self, task_hash: str) -> Path:
        """Generate state file path"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return self.plans_folder / f"ralph_state_{task_hash}_{timestamp}.md"
    
    def save_state(self, state: LoopState, file_path: Path):
        """Save state to markdown and JSON files"""
        # Markdown format
        md_content = self._to_markdown(state)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # JSON format
        json_path = file_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(state.to_dict(), f, indent=2, default=str)
    
    def _to_markdown(self, state: LoopState) -> str:
        """Convert state to markdown"""
        content = f"""---
metadata:
  task_prompt: "{state.task_prompt[:100]}..."
  status: "{state.status}"
  iteration: {state.iteration}
  max_iterations: {state.max_iterations}
  started_at: "{state.started_at}"
  last_updated: "{state.last_updated}"
---

# Ralph Loop State

## Status
| Field | Value |
|-------|-------|
| **Status** | {state.status.upper()} |
| **Iteration** | {state.iteration} / {state.max_iterations} |
| **Started** | {state.started_at} |
| **Last Updated** | {state.last_updated} |

## Task Prompt
{state.task_prompt}

## Iteration History

"""
        for i, iteration in enumerate(state.iterations, 1):
            content += f"""### Iteration {i}
**Timestamp:** {iteration.timestamp}
**Action:** {iteration.action}
**Result:** {iteration.result}
**Next Steps:** {iteration.next_steps}
**Complete:** {iteration.is_complete}

"""

        if state.final_result:
            content += f"""## Final Result
{state.final_result}
"""

        if state.error:
            content += f"""## Error
{state.error}
"""

        return content


# ============================================================================
# API Client
# ============================================================================

class QwenClient:
    """Qwen API client with retry logic"""
    
    def __init__(self, api_key: Optional[str], model: str, config: Config):
        self.api_key = api_key
        self.model = model
        self.config = config
        self.use_simulated = not api_key or not DASHSCOPE_AVAILABLE
        
        if DASHSCOPE_AVAILABLE and api_key:
            dashscope.api_key = api_key
    
    def call(self, prompt: str, iteration: int) -> Dict[str, Any]:
        """Call Qwen API with retry and backoff"""
        if self.use_simulated:
            return self._simulated_call(prompt, iteration)
        
        return self._call_with_retry(prompt, iteration)
    
    def _call_with_retry(self, prompt: str, iteration: int) -> Dict[str, Any]:
        """Call API with exponential backoff retry"""
        max_retries = 5
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return self._call_api(prompt)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    delay = min(
                        self.config.backoff_base ** attempt + random.uniform(0, 1),
                        self.config.backoff_max
                    )
                    logging.warning(f"API call failed (attempt {attempt + 1}), retrying in {delay:.1f}s: {e}")
                    time.sleep(delay)
        
        # All retries exhausted
        logging.error(f"API call failed after {max_retries} attempts: {last_error}")
        return {
            "action": f"Error: API call failed after {max_retries} retries",
            "result": str(last_error),
            "next_steps": "Check API key and network connection",
            "is_complete": False,
            "raw_response": ""
        }
    
    def _call_api(self, prompt: str) -> Dict[str, Any]:
        """Make actual API call"""
        if DASHSCOPE_AVAILABLE and self.api_key:
            # Use official SDK
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                result_format='message'
            )
            
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                return self._parse_response(content)
            else:
                raise Exception(f"API error: {response.status_code}")
        else:
            # Fallback to requests
            if requests is None:
                raise ImportError("requests library not available")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "input": {"prompt": prompt}
            }
            
            response = requests.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                content = response.json()['output']['text']
                return self._parse_response(content)
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        import re
        
        # Check for completion marker
        is_complete = '<promise>COMPLETE</promise>' in content
        
        # Try to extract structured sections
        action_match = re.search(r'<action>(.*?)</action>', content, re.DOTALL | re.IGNORECASE)
        result_match = re.search(r'<result>(.*?)</result>', content, re.DOTALL | re.IGNORECASE)
        next_match = re.search(r'<next_steps>(.*?)</next_steps>', content, re.DOTALL | re.IGNORECASE)
        
        action = action_match.group(1).strip() if action_match else ""
        result = result_match.group(1).strip() if result_match else ""
        next_steps = next_match.group(1).strip() if next_match else ""
        
        # If no structured tags, try JSON
        if not action and not result:
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    action = data.get('action', '')
                    result = data.get('result', '')
                    next_steps = data.get('next_steps', '')
                    is_complete = is_complete or data.get('is_complete', False)
                except json.JSONDecodeError:
                    pass
        
        # Fallback: use raw content
        if not action:
            action = content[:500] if content else "No action specified"
        
        return {
            "action": action,
            "result": result,
            "next_steps": next_steps,
            "is_complete": is_complete,
            "raw_response": content
        }
    
    def _simulated_call(self, prompt: str, iteration: int) -> Dict[str, Any]:
        """Simulated API call for testing without API key"""
        logging.warning("Using simulated API mode (no API key configured)")
        
        # Simulate progressive completion
        is_complete = iteration >= self.config.max_iterations
        
        return {
            "action": f"[SIMULATED] Processing iteration {iteration}",
            "result": f"[SIMULATED] Result for iteration {iteration}. Set DASHSCOPE_API_KEY for real responses.",
            "next_steps": "Continue processing or configure API key",
            "is_complete": is_complete,
            "raw_response": f"<promise>COMPLETE</promise>" if is_complete else ""
        }


# ============================================================================
# Prompt Builder
# ============================================================================

class PromptBuilder:
    """Builds prompts for the AI"""
    
    SYSTEM_PROMPT = """You are an autonomous AI assistant executing a task iteratively.

## Your Role
- Analyze the task and current state
- Decide what action to take in this iteration
- Execute the action (describe what you did)
- Report the result
- Identify next steps
- When the task is fully complete, include <promise>COMPLETE</promise> in your response

## Response Format
Use this format for your response:

<action>
Describe the specific action you are taking in this iteration
</action>

<result>
Describe the result or outcome of this action
</result>

<next_steps>
Describe what still needs to be done or what the next iteration should focus on
</next_steps>

<promise>COMPLETE</promise>  <!-- Include this tag ONLY when the task is fully complete -->

## Important Rules
1. Be specific and actionable
2. Track progress toward the goal
3. Don't repeat the same action twice
4. Include <promise>COMPLETE</promise> ONLY when the entire task is done
5. If you encounter errors, describe them and suggest alternatives
"""
    
    def build_prompt(self, task: str, iteration: int, previous_iterations: List[IterationData]) -> str:
        """Build complete prompt with context"""
        # Build previous iterations context
        context = ""
        if previous_iterations:
            context = "\n\n## Previous Iterations:\n"
            for i, prev in enumerate(previous_iterations, 1):
                context += f"""
### Iteration {i}
- **Action:** {prev.action}
- **Result:** {prev.result}
- **Next Steps:** {prev.next_steps}
"""

        prompt = f"""{self.SYSTEM_PROMPT}

## Current Task
{task}

## Current State
- **Iteration:** {iteration}
- **Status:** In Progress

{context}

## Instructions for This Iteration
Based on the task and previous work, please:
1. Analyze what has been accomplished
2. Determine the next logical action
3. Execute and report the result
4. Update the remaining work plan

Begin your response now:"""

        return prompt


# ============================================================================
# Dashboard Updater
# ============================================================================

class DashboardUpdater:
    """Updates the Dashboard.md with completion summary"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.dashboard_path = vault_path / 'Dashboard.md'
    
    def update(self, state: LoopState):
        """Add completion entry to dashboard"""
        # Create dashboard if doesn't exist
        if not self.dashboard_path.exists():
            self.dashboard_path.write_text("# AI Employee Vault Dashboard\n\n", encoding='utf-8')
        
        # Read existing content
        content = self.dashboard_path.read_text(encoding='utf-8')
        
        # Create completion entry
        entry = self._create_entry(state)
        
        # Insert after header
        if "\n\n## Recent Completions\n" not in content:
            content += "\n## Recent Completions\n"
        
        content = content.replace("## Recent Completions\n", f"## Recent Completions\n{entry}\n")
        
        # Save
        self.dashboard_path.write_text(content, encoding='utf-8')
        logging.info(f"Dashboard updated: {self.dashboard_path}")
    
    def _create_entry(self, state: LoopState) -> str:
        """Create dashboard entry"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        task_summary = state.task_prompt[:100] + "..." if len(state.task_prompt) > 100 else state.task_prompt
        
        return f"""### ✅ Completed: {timestamp}
- **Task:** {task_summary}
- **Iterations:** {state.iteration}
- **Status:** {state.status}
- **Summary:** {state.final_result[:200] if state.final_result else 'N/A'}...

---
"""


# ============================================================================
# Main Loop
# ============================================================================

class ReasoningLoop:
    """Main reasoning loop orchestrator"""
    
    def __init__(self, task_prompt: str, config: Config):
        self.task_prompt = task_prompt
        self.config = config
        self.state = self._create_initial_state()
        
        # Initialize components
        self.state_manager = StateManager(config.plans_folder)
        self.client = QwenClient(config.api_key, config.model, config)
        self.prompt_builder = PromptBuilder()
        self.dashboard_updater = DashboardUpdater(config.vault_path)
        
        # Setup logging
        self._setup_logging()
        
        # State file (set during run)
        self.state_file = None
    
    def _create_initial_state(self) -> LoopState:
        """Create initial loop state"""
        now = datetime.now().isoformat()
        return LoopState(
            task_prompt=self.task_prompt,
            status="running",
            iteration=0,
            max_iterations=self.config.max_iterations,
            started_at=now,
            last_updated=now,
            iterations=[],
            final_result=None,
            error=None
        )
    
    def _setup_logging(self):
        """Configure logging"""
        os.makedirs(self.config.logs_folder, exist_ok=True)
        log_file = self.config.logs_folder / 'ralph_loop.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def run(self) -> LoopState:
        """Execute the reasoning loop"""
        logging.info("=" * 60)
        logging.info("Ralph Wiggum Loop - Starting")
        logging.info(f"Task: {self.task_prompt[:100]}...")
        logging.info(f"Max iterations: {self.config.max_iterations}")
        logging.info(f"API Key: {'Configured' if self.config.api_key else 'Not configured (simulated mode)'}")
        logging.info("=" * 60)
        
        # Generate state file path
        import hashlib
        task_hash = hashlib.md5(self.task_prompt.encode()).hexdigest()[:8]
        self.state_file = self.state_manager.get_state_file_path(task_hash)
        
        try:
            while self.state.iteration < self.state.max_iterations:
                # Increment iteration
                self.state.iteration += 1
                self.state.last_updated = datetime.now().isoformat()
                
                logging.info(f"\n{'='*40}")
                logging.info(f"Iteration {self.state.iteration} / {self.state.max_iterations}")
                logging.info(f"{'='*40}")
                
                # Build prompt
                prompt = self.prompt_builder.build_prompt(
                    self.task_prompt,
                    self.state.iteration,
                    self.state.iterations
                )
                
                # Call AI
                logging.info("Calling AI...")
                result = self.client.call(prompt, self.state.iteration)
                
                # Log result
                logging.info(f"Action: {result.get('action', 'N/A')[:100]}...")
                logging.info(f"Result: {result.get('result', 'N/A')[:100]}...")
                
                # Store iteration data
                iteration_data = IterationData(
                    iteration=self.state.iteration,
                    timestamp=datetime.now().isoformat(),
                    prompt=prompt[:2000],
                    response=result.get('raw_response', ''),
                    action=result.get('action', ''),
                    result=result.get('result', ''),
                    next_steps=result.get('next_steps', ''),
                    is_complete=result.get('is_complete', False)
                )
                self.state.iterations.append(iteration_data)
                
                # Save state
                self.state_manager.save_state(self.state, self.state_file)
                logging.info(f"State saved: {self.state_file}")
                
                # Check completion
                if result.get('is_complete', False):
                    logging.info("\n✓ Task marked as COMPLETE by AI!")
                    self.state.status = "completed"
                    self.state.final_result = result.get('raw_response', str(result))
                    break
                
                # Small delay between iterations
                time.sleep(1)
            
            # Final status
            if self.state.status == "running":
                if self.state.iteration >= self.state.max_iterations:
                    self.state.status = "max_iterations_reached"
                    logging.info(f"\n⚠ Max iterations ({self.state.max_iterations}) reached")
            
            # Final save
            self.state_manager.save_state(self.state, self.state_file)
            
            # Update dashboard
            self.dashboard_updater.update(self.state)
            
            logging.info("\n" + "=" * 60)
            logging.info(f"Loop finished - Status: {self.state.status}")
            logging.info(f"Total iterations: {self.state.iteration}")
            logging.info("=" * 60)
            
        except KeyboardInterrupt:
            self.state.status = "interrupted"
            self.state.error = "Stopped by user"
            self.state_manager.save_state(self.state, self.state_file)
            logging.info("Loop interrupted by user")
            
        except Exception as e:
            self.state.status = "error"
            self.state.error = str(e)
            self.state_manager.save_state(self.state, self.state_file)
            logging.error(f"Loop error: {e}")
            raise
        
        return self.state


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description='Ralph Wiggum Loop - Iterative AI Task Execution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Research Python async best practices and create a summary"
  %(prog)s "Analyze codebase and identify code smells"
  %(prog)s "Create README.md with installation and usage docs"
        """
    )
    
    parser.add_argument(
        'task_prompt',
        type=str,
        help='High-level task description to execute'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=None,
        help='Override max iterations (default: from env or 10)'
    )
    parser.add_argument(
        '--vault-path',
        type=str,
        default=None,
        help='Override vault path (default: current dir or VAULT_PATH env)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Override model name (default: qwen-plus)'
    )
    
    args = parser.parse_args()
    
    # Load config
    config = Config.from_env()
    
    # Apply CLI overrides
    if args.max_iterations:
        config.max_iterations = args.max_iterations
    if args.vault_path:
        config.vault_path = Path(args.vault_path)
        config.plans_folder = config.vault_path / 'plans'
        config.logs_folder = config.vault_path / 'logs'
    if args.model:
        config.model = args.model
    
    # Run the loop
    loop = ReasoningLoop(task_prompt=args.task_prompt, config=config)
    result = loop.run()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Final Status: {result.status}")
    print(f"Iterations: {result.iteration} / {result.max_iterations}")
    print(f"State File: {loop.state_file}")
    print(f"{'='*60}")
    
    # Exit code based on status
    if result.status == "completed":
        sys.exit(0)
    elif result.status == "error":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == '__main__':
    main()
```

---

## Output Files

After execution, the skill creates:

| File | Description |
|------|-------------|
| `plans/ralph_state_*.md` | Full iteration history in markdown |
| `plans/ralph_state_*.json` | Machine-readable state data |
| `logs/ralph_loop.log` | Detailed execution logs |
| `Dashboard.md` | Updated with completion summary |

## Response Format

The AI should respond using XML-style tags:

```xml
<action>
Specific action taken in this iteration
</action>

<result>
Outcome or result of the action
</result>

<next_steps>
What still needs to be done
</next_steps>

<promise>COMPLETE</promise>
```

## Error Handling

- **API Failures**: Exponential backoff retry (2^attempt seconds, max 60s)
- **Missing API Key**: Falls back to simulated mode with warnings
- **Interrupts**: Graceful shutdown with state preservation
- **Max Iterations**: Stops cleanly with status `max_iterations_reached`

## Best Practices

1. **Be Specific**: Clear task prompts yield better results
2. **Monitor Progress**: Check `plans/` folder for intermediate state
3. **Set Limits**: Use appropriate `MAX_ITERATIONS` for task complexity
4. **Review Logs**: Check `logs/ralph_loop.log` for debugging
5. **Configure API**: Set `DASHSCOPE_API_KEY` for real AI responses

## Troubleshooting

### Simulated Mode Warning
```
WARNING: Using simulated API mode (no API key configured)
```
**Solution**: Set `DASHSCOPE_API_KEY` environment variable

### Max Iterations Reached
```
⚠ Max iterations (10) reached
```
**Solution**: Increase `MAX_ITERATIONS` or refine task scope

### API Errors
```
ERROR: API call failed after 5 attempts
```
**Solution**: Check API key validity and network connection
