# Ralph Loop - Iterative AI Task Execution

## Overview

The **Ralph Loop** pattern (inspired by the "Ralph Wiggum pattern") repeatedly calls an AI API with:
1. The original task context
2. The current state of work
3. Previous iteration results

Until either:
- Completion condition is met
- Max iterations reached
- Error occurs
- User stops it

## Features

- ✅ **Iterative AI Execution** - Repeatedly calls Qwen API with evolving context
- ✅ **Completion Conditions** - Custom functions to check if task is done
- ✅ **State Persistence** - Saves intermediate results to `/Plans` folder
- ✅ **Max Iterations** - Prevents infinite loops
- ✅ **Full Logging** - All iterations logged to `logs/ralph_loop.log`
- ✅ **Graceful Shutdown** - Can be stopped mid-execution

## Installation

```bash
# Install Qwen SDK (optional, for real API calls)
pip install dashscope

# Or just use the loop without API (simulated mode)
python ralph_loop.py --task path/to/task.md
```

## Basic Usage

### Example 1: Simple Task Execution

```python
from ralph_loop import run_ralph_loop, RalphLoop

# Define completion condition
def task_complete(state):
    """Check if task is complete"""
    # Check if last result indicates completion
    last_result = state.get('last_result', {})
    return last_result.get('is_complete', False)

# Run the loop
result = run_ralph_loop(
    task_file="AI_Employee_Vault/Needs_Action/task_001.md",
    completion_condition=task_complete,
    max_iterations=10,
    plans_folder="AI_Employee_Vault/Plans",
    api_key="your-qwen-api-key"  # Or set DASHSCOPE_API_KEY env var
)

print(f"Status: {result.status}")
print(f"Iterations: {result.iteration}")
```

### Example 2: Check if File Moved to Done

```python
from pathlib import Path

def file_moved_to_done(state):
    """Check if task file has been moved to Done folder"""
    task_file = state.get('task_file', '')
    task_path = Path(task_file)
    
    # Check if file exists in Done folder
    done_folder = task_path.parent.parent / 'Done'
    done_file = done_folder / task_path.name
    
    return done_file.exists()

result = run_ralph_loop(
    task_file="AI_Employee_Vault/Needs_Action/task_001.md",
    completion_condition=file_moved_to_done,
    max_iterations=15
)
```

### Example 3: Complex Completion Condition

```python
def complex_condition(state):
    """Multiple conditions for completion"""
    # Check iteration count
    if state['iteration'] >= state['max_iterations']:
        return True
    
    # Check if API says complete
    last_result = state.get('last_result', {})
    if last_result.get('is_complete', False):
        return True
    
    # Check if task file was modified
    task_file = Path(state.get('task_file', ''))
    if task_file.exists():
        # Check for completion marker in file
        content = task_file.read_text()
        if '[x] Task completed' in content:
            return True
    
    # Check if output file exists
    output_file = Path("AI_Employee_Vault/Done/output.md")
    if output_file.exists():
        return True
    
    return False

result = run_ralph_loop(
    task_file="AI_Employee_Vault/Needs_Action/task_001.md",
    completion_condition=complex_condition,
    max_iterations=20
)
```

### Example 4: Using the Class Directly

```python
from ralph_loop import RalphLoop

# Create loop instance
loop = RalphLoop(
    task_file="task.md",
    completion_condition=lambda s: s.get('last_result', {}).get('is_complete', False),
    max_iterations=10
)

# Run with custom state file
from pathlib import Path
state_file = Path("AI_Employee_Vault/Plans/custom_state.md")
result = loop.run(state_file=state_file)

# Or stop mid-execution
# loop.stop()  # Call from another thread
```

## Command Line Usage

```bash
# Basic run
python ralph_loop.py --task "AI_Employee_Vault/Needs_Action/task_001.md"

# With max iterations
python ralph_loop.py --task "task.md" --max-iterations 15

# With custom output folder
python ralph_loop.py --task "task.md" --output "AI_Employee_Vault/Plans"

# With API key
python ralph_loop.py --task "task.md" --api-key "sk-xxx"
```

## State File Format

State is saved to `/Plans` folder as both Markdown and JSON:

### Markdown (`ralph_state_taskname.md`)
```markdown
---
metadata:
  task_file: "AI_Employee_Vault/Needs_Action/task_001.md"
  status: "completed"
  iteration: 5
  max_iterations: 10
  started_at: "2026-03-22T21:00:00"
  last_updated: "2026-03-22T21:05:00"
---

# Ralph Loop State

## Current Status
| Field | Value |
|-------|-------|
| **Status** | COMPLETED |
| **Iteration** | 5 / 10 |
| **Started** | 2026-03-22T21:00:00 |
| **Last Updated** | 2026-03-22T21:05:00 |

## Iteration History

### Iteration 1
**Timestamp:** 2026-03-22T21:00:30
**Action:** Analyze task requirements
**Result:** Requirements documented
**Next Steps:** Implement solution

### Iteration 2
**Timestamp:** 2026-03-22T21:01:30
**Action:** Implement solution
**Result:** Code written
**Next Steps:** Test and verify

...

## Final Result
{...}
```

### JSON (`ralph_state_taskname.json`)
```json
{
  "task_file": "AI_Employee_Vault/Needs_Action/task_001.md",
  "status": "completed",
  "iteration": 5,
  "max_iterations": 10,
  "iterations_data": [...],
  "final_result": "..."
}
```

## Completion Condition Examples

### Check File Status
```python
def check_file_exists(state):
    """Check if output file was created"""
    output_file = Path("AI_Employee_Vault/Done/output.md")
    return output_file.exists()
```

### Check Content
```python
def check_content(state):
    """Check if task file contains completion marker"""
    task_file = Path(state.get('task_file', ''))
    if task_file.exists():
        content = task_file.read_text()
        return '[x] COMPLETED' in content
    return False
```

### Check External API
```python
def check_external_api(state):
    """Check external service for completion status"""
    import requests
    try:
        response = requests.get('https://api.example.com/task/status')
        return response.json().get('status') == 'complete'
    except:
        return False
```

### Check Iteration Results
```python
def check_all_results(state):
    """Check if all iterations produced valid results"""
    all_results = state.get('all_results', [])
    if len(all_results) < 3:
        return False
    
    # Check if last 3 results are consistent
    last_three = all_results[-3:]
    return all(r.get('is_complete', False) for r in last_three)
```

## API Configuration

### Using Qwen API (Real)

```bash
# Set environment variable
export DASHSCOPE_API_KEY="sk-your-api-key"

# Or pass directly
python ralph_loop.py --task "task.md" --api-key "sk-your-api-key"
```

### Simulated Mode (No API Key)

If no API key is provided, the loop runs in simulated mode:
- Generates placeholder responses
- Useful for testing workflow
- Logs warnings about missing API key

## Loop States

| Status | Description |
|--------|-------------|
| `running` | Loop is actively iterating |
| `completed` | Completion condition met |
| `max_iterations_reached` | Hit max iteration limit |
| `error` | Error occurred |
| `stopped_by_user` | User requested stop |

## Logging

All activity is logged to `logs/ralph_loop.log`:

```
2026-03-22 21:00:00 - INFO - Starting Ralph Loop
2026-03-22 21:00:01 - INFO - Task: AI_Employee_Vault/Needs_Action/task_001.md
2026-03-22 21:00:02 - INFO - ========================================
2026-03-22 21:00:02 - INFO - Iteration 1 / 10
2026-03-22 21:00:03 - INFO - Calling Qwen API...
2026-03-22 21:00:05 - INFO - Action: Analyze requirements
2026-03-22 21:00:05 - INFO - Result: Requirements documented
2026-03-22 21:00:05 - INFO - State saved to: AI_Employee_Vault/Plans/ralph_state_task_001.md
```

## Integration with AI Employee Vault

The Ralph Loop integrates with the workflow system:

```
Drop_Folder → Needs_Action → [Ralph Loop] → Plans → Done
                                    ↓
                              State files saved here
```

### Example Workflow

1. Task file created in `Needs_Action`
2. Ralph Loop starts processing
3. State saved to `Plans` after each iteration
4. When complete, task moved to `Done`
5. Completion condition detects move, loop stops

## Best Practices

1. **Set reasonable max_iterations** - Prevents runaway loops
2. **Use specific completion conditions** - Clear end criteria
3. **Monitor state files** - Check progress in `/Plans`
4. **Log important decisions** - Review iteration history
5. **Handle errors gracefully** - Check status after run

## Troubleshooting

### Loop doesn't stop
- Check completion condition logic
- Increase max_iterations if needed
- Use `loop.stop()` to force stop

### API errors
- Verify API key is set
- Check network connection
- Review `logs/ralph_loop.log`

### State file not created
- Ensure `/Plans` folder exists
- Check write permissions
- Review error logs
