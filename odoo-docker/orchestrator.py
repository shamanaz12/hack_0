#!/usr/bin/env python3
"""
Orchestrator - Fully Automatic Gmail + WhatsApp Message Processor

This script:
1. Watches Gmail for new emails (via gmail_watcher.py)
2. Watches WhatsApp for new messages (via whatsapp_watcher.py)
3. Processes all files in Needs_Action/ using Ralph Loop (AI)
4. Moves processed files to Done/ folder automatically

FULLY AUTOMATIC - NO MANUAL INTERVENTION NEEDED!

Usage:
    python orchestrator.py

Or run in background:
    python orchestrator.py --background

Or run once (no watching):
    python orchestrator.py --once
"""

import os
import sys
import json
import time
import shutil
import logging
import hashlib
import re
import signal
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

# Try to import watchdog for efficient file watching
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Note: watchdog not installed. Using polling mode (less efficient).")
    print("Install with: pip install watchdog")

# Try to import dashscope for Qwen API
try:
    from dashscope import Generation
    import dashscope
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    print("Note: dashscope not installed. Will use simulated mode.")
    print("Install with: pip install dashscope")

# Try to import MCP client for email
try:
    from mcp_email_client import MCPEmailClient
    MCP_EMAIL_AVAILABLE = True
except ImportError:
    MCP_EMAIL_AVAILABLE = False
    print("Note: MCP email client not installed. Email notifications disabled.")
    print("Install with: pip install mcp")


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class Config:
    """Configuration container"""
    vault_path: Path
    needs_action_folder: Path
    processing_folder: Path
    done_folder: Path
    error_folder: Path
    plans_folder: Path
    logs_folder: Path
    approved_folder: Path
    api_key: Optional[str]
    model: str
    max_iterations: int
    poll_interval: float
    backoff_base: float
    backoff_max: float
    gmail_check_interval: int
    whatsapp_check_interval: int
    auto_run_watchers: bool
    enable_mcp_email: bool

    @classmethod
    def from_env(cls, vault_path: Optional[Path] = None) -> 'Config':
        """Load configuration from environment and .env file"""
        # Load from .env file first
        env_file = Path(__file__).parent / '.env'
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value and not os.getenv(key):
                            os.environ[key] = value

        if vault_path is None:
            vault_path = Path(os.getenv('VAULT_PATH', '.'))

        # Default folders based on existing structure
        silver_tier = vault_path / 'AI_Employee_Vault' / 'Silver_Tier'

        return cls(
            vault_path=vault_path,
            needs_action_folder=silver_tier / 'Needs_Action',
            processing_folder=silver_tier / 'Processing',
            done_folder=silver_tier / 'Done',
            error_folder=silver_tier / 'Error',
            approved_folder=silver_tier / 'Approved',
            plans_folder=vault_path / 'plans',
            logs_folder=vault_path / 'logs',
            api_key=os.getenv('DASHSCOPE_API_KEY'),
            model=os.getenv('MODEL_NAME', 'qwen-plus'),
            max_iterations=int(os.getenv('MAX_ITERATIONS', '10')),
            poll_interval=float(os.getenv('POLL_INTERVAL', '5.0')),
            backoff_base=float(os.getenv('BACKOFF_BASE', '2.0')),
            backoff_max=float(os.getenv('BACKOFF_MAX', '60.0')),
            gmail_check_interval=int(os.getenv('GMAIL_INTERVAL', '300')),
            whatsapp_check_interval=int(os.getenv('WHATSAPP_INTERVAL', '300')),
            auto_run_watchers=os.getenv('AUTO_RUN_WATCHERS', 'true').lower() == 'true',
            enable_mcp_email=os.getenv('ENABLE_MCP_EMAIL', 'true').lower() == 'true'
        )


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(logs_folder: Path) -> logging.Logger:
    """Configure logging"""
    os.makedirs(logs_folder, exist_ok=True)
    
    log_file = logs_folder / 'orchestrator.log'
    
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
    
    # Create logger
    logger = logging.getLogger('orchestrator')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# ============================================================================
# State Management
# ============================================================================

class ProcessingStatus(Enum):
    """Processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class ProcessingRecord:
    """Record of a processed file"""
    file_path: str
    file_hash: str
    status: str
    started_at: str
    completed_at: Optional[str]
    iterations: int
    error: Optional[str]
    plan_file: Optional[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class StateManager:
    """Manages processing state to prevent duplicates"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.state_file = vault_path / 'orchestrator_state.json'
        self.records: Dict[str, ProcessingRecord] = {}
        self._load_state()
    
    def _load_state(self):
        """Load state from file"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key, value in data.items():
                    self.records[key] = ProcessingRecord(**value)
    
    def _save_state(self):
        """Save state to file"""
        data = {k: v.to_dict() for k, v in self.records.items()}
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_file_hash(self, file_path: Path) -> str:
        """Generate hash for file"""
        content = file_path.read_bytes()
        return hashlib.md5(content).hexdigest()
    
    def is_already_processed(self, file_path: Path) -> bool:
        """Check if file was already processed"""
        file_hash = self.get_file_hash(file_path)
        return file_hash in self.records
    
    def mark_processing(self, file_path: Path):
        """Mark file as being processed"""
        file_hash = self.get_file_hash(file_path)
        self.records[file_hash] = ProcessingRecord(
            file_path=str(file_path),
            file_hash=file_hash,
            status=ProcessingStatus.PROCESSING.value,
            started_at=datetime.now().isoformat(),
            completed_at=None,
            iterations=0,
            error=None,
            plan_file=None
        )
        self._save_state()
    
    def mark_completed(self, file_hash: str, iterations: int, plan_file: Optional[str]):
        """Mark file as completed"""
        if file_hash in self.records:
            self.records[file_hash].status = ProcessingStatus.COMPLETED.value
            self.records[file_hash].completed_at = datetime.now().isoformat()
            self.records[file_hash].iterations = iterations
            self.records[file_hash].plan_file = plan_file
            self._save_state()
    
    def mark_error(self, file_hash: str, error: str):
        """Mark file as error"""
        if file_hash in self.records:
            self.records[file_hash].status = ProcessingStatus.ERROR.value
            self.records[file_hash].completed_at = datetime.now().isoformat()
            self.records[file_hash].error = error
            self._save_state()
    
    def get_summary(self) -> Dict[str, int]:
        """Get processing summary"""
        summary = {
            'total': len(self.records),
            'completed': 0,
            'error': 0,
            'processing': 0
        }
        for record in self.records.values():
            if record.status == ProcessingStatus.COMPLETED.value:
                summary['completed'] += 1
            elif record.status == ProcessingStatus.ERROR.value:
                summary['error'] += 1
            elif record.status == ProcessingStatus.PROCESSING.value:
                summary['processing'] += 1
        return summary


# ============================================================================
# Qwen API Client
# ============================================================================

class QwenClient:
    """Qwen API client with retry logic"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.api_key = config.api_key
        self.model = config.model
        self.use_simulated = not config.api_key or not DASHSCOPE_AVAILABLE
        
        if DASHSCOPE_AVAILABLE and config.api_key:
            dashscope.api_key = config.api_key
            self.logger.info("Qwen API configured with dashscope SDK")
        else:
            self.logger.warning("Qwen API not configured - using simulated mode")
    
    def call(self, prompt: str, iteration: int) -> Dict[str, Any]:
        """Call Qwen API with retry and backoff"""
        if self.use_simulated:
            return self._simulated_call(prompt, iteration)
        
        return self._call_with_retry(prompt, iteration)
    
    def _call_with_retry(self, prompt: str, iteration: int) -> Dict[str, Any]:
        """Call API with exponential backoff retry"""
        import random
        
        max_retries = 5
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return self._call_api(prompt)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    delay = min(
                        self.config.backoff_base ** attempt + random.uniform(0, 1),
                        self.config.backoff_max
                    )
                    self.logger.warning(f"API call failed (attempt {attempt + 1}), retrying in {delay:.1f}s: {e}")
                    time.sleep(delay)
        
        self.logger.error(f"API call failed after {max_retries} attempts: {last_error}")
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
            raise ImportError("Qwen API not available")
    
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
        is_complete = iteration >= self.config.max_iterations
        
        return {
            "action": f"[SIMULATED] Processing iteration {iteration}",
            "result": f"[SIMULATED] Result for iteration {iteration}. Configure DASHSCOPE_API_KEY for real responses.",
            "next_steps": "Continue processing or configure API key",
            "is_complete": is_complete,
            "raw_response": f"<promise>COMPLETE</promise>" if is_complete else ""
        }


# ============================================================================
# Reasoning Loop
# ============================================================================

class ReasoningLoop:
    """Ralph Wiggum Loop - Iterative AI task execution"""
    
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
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.client = QwenClient(config, logger)
        self.iterations_data: List[Dict] = []
    
    def build_prompt(self, task: str, iteration: int) -> str:
        """Build prompt for AI"""
        # Build previous iterations context
        context = ""
        if self.iterations_data:
            context = "\n\n## Previous Iterations:\n"
            for i, prev in enumerate(self.iterations_data, 1):
                context += f"""
### Iteration {i}
- **Action:** {prev.get('action', 'N/A')}
- **Result:** {prev.get('result', 'N/A')}
- **Next Steps:** {prev.get('next_steps', 'N/A')}
"""

        prompt = f"""{self.SYSTEM_PROMPT}

## Current Task
{task}

## Current State
- **Iteration:** {iteration}
- **Max Iterations:** {self.config.max_iterations}
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
    
    def run(self, task_prompt: str) -> Dict[str, Any]:
        """Execute the reasoning loop"""
        self.logger.info("=" * 50)
        self.logger.info("Ralph Loop - Starting")
        self.logger.info(f"Task: {task_prompt[:100]}...")
        self.logger.info(f"Max iterations: {self.config.max_iterations}")
        self.logger.info("=" * 50)
        
        self.iterations_data = []
        
        for iteration in range(1, self.config.max_iterations + 1):
            self.logger.info(f"\n{'='*40}")
            self.logger.info(f"Iteration {iteration} / {self.config.max_iterations}")
            self.logger.info(f"{'='*40}")
            
            # Build prompt
            prompt = self.build_prompt(task_prompt, iteration)
            
            # Call AI
            self.logger.info("Calling AI...")
            result = self.client.call(prompt, iteration)
            
            # Log result
            self.logger.info(f"Action: {result.get('action', 'N/A')[:100]}...")
            self.logger.info(f"Result: {result.get('result', 'N/A')[:100]}...")
            
            # Store iteration data
            self.iterations_data.append({
                'iteration': iteration,
                'timestamp': datetime.now().isoformat(),
                'prompt': prompt[:2000],
                'action': result.get('action', ''),
                'result': result.get('result', ''),
                'next_steps': result.get('next_steps', ''),
                'is_complete': result.get('is_complete', False)
            })
            
            # Check completion
            if result.get('is_complete', False):
                self.logger.info("\n✓ Task marked as COMPLETE!")
                return {
                    'status': 'completed',
                    'iterations': iteration,
                    'final_result': result.get('raw_response', ''),
                    'iterations_data': self.iterations_data
                }
            
            # Small delay between iterations
            time.sleep(1)
        
        self.logger.info(f"\n⚠ Max iterations ({self.config.max_iterations}) reached")
        return {
            'status': 'max_iterations_reached',
            'iterations': self.config.max_iterations,
            'final_result': self.iterations_data[-1] if self.iterations_data else '',
            'iterations_data': self.iterations_data
        }


# ============================================================================
# File Orchestrator
# ============================================================================

class FileOrchestrator:
    """Main file orchestrator - Watches Gmail, WhatsApp and auto-processes"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logging(config.logs_folder)
        self.state_manager = StateManager(config.vault_path)
        self.reasoning_loop = ReasoningLoop(config, self.logger)
        
        # Initialize MCP email client if available
        self.email_client = MCPEmailClient() if MCP_EMAIL_AVAILABLE else None

        # Create folders
        self._create_folders()

        # Running flag
        self.running = True

        # Watcher timing
        self.last_gmail_check = 0
        self.last_whatsapp_check = 0
        self.last_approved_check = 0

        self.logger.info("File Orchestrator initialized")
        self.logger.info(f"Needs Action: {config.needs_action_folder}")
        self.logger.info(f"Processing: {config.processing_folder}")
        self.logger.info(f"Done: {config.done_folder}")
        self.logger.info(f"Error: {config.error_folder}")
        self.logger.info(f"Approved: {config.approved_folder}")
        self.logger.info(f"Plans: {config.plans_folder}")
        self.logger.info(f"Gmail Check Interval: {config.gmail_check_interval}s")
        self.logger.info(f"WhatsApp Check Interval: {config.whatsapp_check_interval}s")
        self.logger.info(f"Auto-run watchers: {config.auto_run_watchers}")
        self.logger.info(f"MCP Email enabled: {config.enable_mcp_email and MCP_EMAIL_AVAILABLE}")
    
    def _create_folders(self):
        """Create all required folders"""
        for folder in [
            self.config.needs_action_folder,
            self.config.processing_folder,
            self.config.done_folder,
            self.config.error_folder,
            self.config.approved_folder,
            self.config.plans_folder,
            self.config.logs_folder
        ]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def _run_gmail_watcher(self):
        """Run Gmail watcher to fetch new emails"""
        if not self.config.auto_run_watchers:
            return 0
        
        try:
            self.logger.info("Running Gmail watcher...")
            
            # Import and run gmail_watcher
            gmail_watcher_path = Path(__file__).parent / 'gmail_watcher.py'
            
            if gmail_watcher_path.exists():
                import subprocess
                result = subprocess.run(
                    [sys.executable, str(gmail_watcher_path), '--once'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Count new files created
                new_files = len(list(self.config.needs_action_folder.glob('Gmail_*.md')))
                self.logger.info(f"Gmail watcher completed. Files in Needs_Action: {new_files}")
                return new_files
            else:
                self.logger.warning(f"Gmail watcher not found: {gmail_watcher_path}")
                return 0
                
        except subprocess.TimeoutExpired:
            self.logger.error("Gmail watcher timed out")
            return 0
        except Exception as e:
            self.logger.error(f"Gmail watcher error: {e}")
            return 0
    
    def _run_whatsapp_watcher(self):
        """Run WhatsApp watcher to fetch new messages"""
        if not self.config.auto_run_watchers:
            return 0
        
        try:
            self.logger.info("Running WhatsApp watcher...")
            
            # Import and run whatsapp_watcher
            whatsapp_watcher_path = Path(__file__).parent / 'whatsapp_watcher.py'
            
            if whatsapp_watcher_path.exists():
                import subprocess
                result = subprocess.run(
                    [sys.executable, str(whatsapp_watcher_path), '--once'],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                # Count new files created
                new_files = len(list(self.config.needs_action_folder.glob('WhatsApp_*.md')))
                self.logger.info(f"WhatsApp watcher completed. Files in Needs_Action: {new_files}")
                return new_files
            else:
                self.logger.warning(f"WhatsApp watcher not found: {whatsapp_watcher_path}")
                return 0
                
        except subprocess.TimeoutExpired:
            self.logger.error("WhatsApp watcher timed out")
            return 0
        except Exception as e:
            self.logger.error(f"WhatsApp watcher error: {e}")
            return 0

    def _check_approved_folder(self):
        """Check Approved folder for files that need email notification"""
        if not self.config.enable_mcp_email or not MCP_EMAIL_AVAILABLE:
            return 0
        
        try:
            approved_files = list(self.config.approved_folder.glob('*.md'))
            
            if not approved_files:
                return 0
            
            self.logger.info(f"Found {len(approved_files)} approved files to process")
            
            processed_count = 0
            
            for file_path in approved_files:
                if self._send_approval_email(file_path):
                    # Move to Done after email sent
                    self.move_file(file_path, self.config.done_folder)
                    processed_count += 1
            
            return processed_count
            
        except Exception as e:
            self.logger.error(f"Approved folder check error: {e}")
            return 0

    def _send_approval_email(self, file_path: Path) -> bool:
        """Send email notification for approved file"""
        try:
            # Extract email details from file
            content = file_path.read_text(encoding='utf-8')
            
            # Parse frontmatter for email metadata
            to_email = ""
            subject = ""
            email_body = ""
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    email_body = parts[2].strip()
                    
                    # Extract email fields
                    for match in re.finditer(r'(\w+):\s*"?([^"\n]+)"?', frontmatter):
                        key, value = match.groups()
                        if key == 'to_email':
                            to_email = value.strip()
                        elif key == 'email_subject':
                            subject = value.strip()
            
            # If no metadata, use file name as subject
            if not subject:
                subject = f"Approved: {file_path.name}"
            
            if not email_body:
                email_body = f"File approved: {file_path.name}"
            
            # Default recipient if not specified
            if not to_email:
                to_email = os.getenv('DEFAULT_EMAIL', '')
            
            if not to_email:
                self.logger.warning(f"No recipient email for {file_path.name}")
                return False
            
            # Send email via MCP
            self.logger.info(f"Sending approval email to: {to_email}")
            
            import asyncio
            
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.email_client.send_email(to_email, subject, email_body)
            )
            
            if result.get('success'):
                self.logger.info(f"Email sent successfully: {result.get('message')}")
                return True
            else:
                self.logger.error(f"Email failed: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Send email error: {e}")
            return False
    
    def extract_task_prompt(self, file_path: Path) -> str:
        """Extract task prompt from file content"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Try to extract from frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    body = parts[2].strip()
                    # Get first meaningful content
                    lines = body.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip() and not line.startswith('#'):
                            # Found first content line, use rest as prompt
                            prompt = '\n'.join(lines[i:]).strip()
                            if len(prompt) > 50:
                                return prompt
                    
                    # Fallback: use body
                    return body
            
            # No frontmatter, use entire content
            return content.strip()
            
        except Exception as e:
            self.logger.error(f"Error extracting task prompt: {e}")
            return content if 'content' in dir() else str(file_path)
    
    def move_file(self, source: Path, dest_folder: Path) -> Optional[Path]:
        """Move file to destination folder"""
        try:
            dest = dest_folder / source.name
            
            # Copy first (safer)
            shutil.copy2(source, dest)
            
            # Then delete original
            source.unlink()
            
            self.logger.info(f"Moved: {source.name} -> {dest_folder.name}/")
            return dest
            
        except Exception as e:
            self.logger.error(f"Error moving file: {e}")
            return None
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single file"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Processing: {file_path.name}")
        self.logger.info(f"{'='*60}")
        
        file_hash = self.state_manager.get_file_hash(file_path)
        
        try:
            # Check if already processed
            if self.state_manager.is_already_processed(file_path):
                self.logger.info(f"Skipping - already processed")
                return True
            
            # Move to Processing folder
            processing_file = self.move_file(file_path, self.config.processing_folder)
            if not processing_file:
                raise Exception("Failed to move to Processing folder")
            
            # Mark as processing
            self.state_manager.mark_processing(processing_file)
            
            # Extract task prompt
            task_prompt = self.extract_task_prompt(processing_file)
            self.logger.info(f"Task prompt extracted ({len(task_prompt)} chars)")
            
            # Run reasoning loop
            result = self.reasoning_loop.run(task_prompt)
            
            # Create plan file in Plans folder
            plan_file = self._create_plan_file(processing_file, result)
            
            # Move to appropriate folder
            if result['status'] == 'completed':
                self.move_file(processing_file, self.config.done_folder)
                self.state_manager.mark_completed(file_hash, result['iterations'], plan_file)
                self.logger.info(f"[OK] Completed in {result['iterations']} iterations")
                return True
            else:
                # Max iterations reached - still move to Done but log warning
                self.move_file(processing_file, self.config.done_folder)
                self.state_manager.mark_completed(file_hash, result['iterations'], plan_file)
                self.logger.info(f"[OK] Completed (max iterations) in {result['iterations']} iterations")
                return True
                
        except Exception as e:
            self.logger.error(f"[ERROR] Processing failed: {e}")
            
            # Move to Error folder
            try:
                # Try to move from Processing if it exists there
                processing_file = self.config.processing_folder / file_path.name
                if processing_file.exists():
                    self.move_file(processing_file, self.config.error_folder)
                elif file_path.exists():
                    self.move_file(file_path, self.config.error_folder)
            except:
                pass
            
            # Mark error
            if 'file_hash' in dir():
                self.state_manager.mark_error(file_hash, str(e))
            
            return False
    
    def _create_plan_file(self, source_file: Path, result: Dict) -> Optional[str]:
        """Create plan file in Plans folder"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            plan_filename = f"plan_{source_file.stem}_{timestamp}.md"
            plan_path = self.config.plans_folder / plan_filename
            
            # Build plan content
            content = f"""---
metadata:
  source_file: "{source_file.name}"
  created: "{datetime.now().isoformat()}"
  status: "{result['status']}"
  iterations: {result['iterations']}
  processor: "Orchestrator with Ralph Loop"
---

# Plan: {source_file.name}

## Processing Summary
| Field | Value |
|-------|-------|
| **Source** | {source_file.name} |
| **Status** | {result['status']} |
| **Iterations** | {result['iterations']} |
| **Created** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |

## Iteration History

"""
            # Add iteration history
            for i, iteration in enumerate(result.get('iterations_data', []), 1):
                content += f"""### Iteration {i}
**Action:** {iteration.get('action', 'N/A')}
**Result:** {iteration.get('result', 'N/A')}
**Next Steps:** {iteration.get('next_steps', 'N/A')}

"""

            content += f"""## Final Result
{result.get('final_result', 'N/A')}

---
*Generated by Orchestrator with Ralph Loop*
"""
            
            plan_path.write_text(content, encoding='utf-8')
            self.logger.info(f"Plan created: {plan_filename}")
            
            return str(plan_path)
            
        except Exception as e:
            self.logger.error(f"Error creating plan file: {e}")
            return None
    
    def scan_and_process(self) -> int:
        """Scan Needs_Action folder and process files"""
        processed_count = 0
        
        # Get all .md files
        md_files = list(self.config.needs_action_folder.glob('*.md'))
        
        if not md_files:
            self.logger.debug("No .md files in Needs_Action folder")
            return 0
        
        self.logger.info(f"Found {len(md_files)} .md file(s) to process")
        
        for file_path in md_files:
            # Skip if currently being processed
            if self.state_manager.is_already_processed(file_path):
                continue
            
            if self.process_file(file_path):
                processed_count += 1
        
        return processed_count
    
    def run_watchdog(self):
        """Run using watchdog (efficient file watching)"""
        if not WATCHDOG_AVAILABLE:
            self.logger.warning("watchdog not available, falling back to polling")
            return self.run_polling()
        
        self.logger.info("Starting watchdog mode (file system events)")
        
        class NewFileHandler(FileSystemEventHandler):
            def __init__(self, orchestrator):
                self.orchestrator = orchestrator
            
            def on_created(self, event):
                if event.is_directory:
                    return
                
                file_path = Path(event.src_path)
                
                # Check if it's in Needs_Action and is .md
                if file_path.parent == self.orchestrator.config.needs_action_folder:
                    if file_path.suffix.lower() == '.md':
                        self.logger.info(f"New file detected: {file_path.name}")
                        # Small delay to ensure file is fully written
                        time.sleep(0.5)
                        self.orchestrator.process_file(file_path)
        
        handler = NewFileHandler(self)
        observer = Observer()
        observer.schedule(handler, str(self.config.needs_action_folder), recursive=False)
        observer.start()
        
        self.logger.info(f"Watching: {self.config.needs_action_folder}")
        self.logger.info("Press Ctrl+C to stop")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("\nStopping watchdog...")
            observer.stop()
        
        observer.join()
        self.logger.info("Watchdog stopped")
    
    def run_polling(self):
        """Run using polling (simple file checking) - Also runs Gmail/WhatsApp watchers"""
        self.logger.info(f"Starting polling mode (interval: {self.config.poll_interval}s)")
        self.logger.info(f"Watching: {self.config.needs_action_folder}")
        self.logger.info(f"Gmail check: Every {self.config.gmail_check_interval}s")
        self.logger.info(f"WhatsApp check: Every {self.config.whatsapp_check_interval}s")
        self.logger.info(f"Approved check: Every {self.config.poll_interval}s")
        self.logger.info("Press Ctrl+C to stop")

        try:
            while self.running:
                current_time = time.time()

                # Check Gmail (based on interval)
                if current_time - self.last_gmail_check >= self.config.gmail_check_interval:
                    self._run_gmail_watcher()
                    self.last_gmail_check = current_time

                # Check WhatsApp (based on interval)
                if current_time - self.last_whatsapp_check >= self.config.whatsapp_check_interval:
                    self._run_whatsapp_watcher()
                    self.last_whatsapp_check = current_time

                # Check Approved folder (every poll interval)
                if current_time - self.last_approved_check >= self.config.poll_interval:
                    approved_count = self._check_approved_folder()
                    self.last_approved_check = current_time
                    if approved_count > 0:
                        self.logger.info(f"Processed {approved_count} approved file(s)")

                # Process files in Needs_Action
                processed = self.scan_and_process()

                if processed > 0:
                    self.logger.info(f"Processed {processed} file(s)")

                # Wait for next poll
                for _ in range(int(self.config.poll_interval)):
                    if not self.running:
                        break
                    time.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("\nStopping polling...")

        self.logger.info("Polling stopped")
    
    def run_once(self) -> int:
        """Run once (no watching)"""
        self.logger.info("Running once (no continuous watching)")
        return self.scan_and_process()
    
    def stop(self):
        """Stop the orchestrator"""
        self.running = False
        self.logger.info("Stop requested")
    
    def get_status(self) -> Dict:
        """Get orchestrator status"""
        summary = self.state_manager.get_summary()
        
        # Count files in each folder
        needs_action = len(list(self.config.needs_action_folder.glob('*.md')))
        gmail_files = len(list(self.config.needs_action_folder.glob('Gmail_*.md')))
        whatsapp_files = len(list(self.config.needs_action_folder.glob('WhatsApp_*.md')))
        processing = len(list(self.config.processing_folder.glob('*.md')))
        done = len(list(self.config.done_folder.glob('*.md')))
        error = len(list(self.config.error_folder.glob('*.md')))
        
        return {
            'mode': 'watchdog' if WATCHDOG_AVAILABLE else 'polling',
            'folders': {
                'Needs_Action': needs_action,
                'Gmail_Files': gmail_files,
                'WhatsApp_Files': whatsapp_files,
                'Processing': processing,
                'Done': done,
                'Error': error
            },
            'processing_history': summary,
            'api_configured': bool(self.config.api_key),
            'running': self.running,
            'gmail_interval': self.config.gmail_check_interval,
            'whatsapp_interval': self.config.whatsapp_check_interval
        }


# ============================================================================
# Dashboard Updater
# ============================================================================

class DashboardUpdater:
    """Updates Dashboard.md with processing summary"""
    
    def __init__(self, vault_path: Path, logger: logging.Logger):
        self.vault_path = vault_path
        self.dashboard_path = vault_path / 'AI_Employee_Vault' / 'Dashboard.md'
        self.logger = logger
        
        # Create if doesn't exist
        if not self.dashboard_path.exists():
            self.dashboard_path.write_text("# AI Employee Vault Dashboard\n\n", encoding='utf-8')
    
    def update(self, orchestrator_status: Dict):
        """Update dashboard with latest status"""
        try:
            content = self.dashboard_path.read_text(encoding='utf-8')
            
            # Create status section
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            status_section = f"""## Orchestrator Status (Updated: {timestamp})

| Metric | Value |
|--------|-------|
| **Mode** | {orchestrator_status['mode']} |
| **API Configured** | {'Yes' if orchestrator_status['api_configured'] else 'No'} |
| **Running** | {'Yes' if orchestrator_status['running'] else 'No'} |

### Folder Status
| Folder | Files |
|--------|-------|
| Needs_Action | {orchestrator_status['folders']['Needs_Action']} |
| Processing | {orchestrator_status['folders']['Processing']} |
| Done | {orchestrator_status['folders']['Done']} |
| Error | {orchestrator_status['folders']['Error']} |

### Processing History
| Status | Count |
|--------|-------|
| Total Processed | {orchestrator_status['processing_history']['total']} |
| Completed | {orchestrator_status['processing_history']['completed']} |
| Errors | {orchestrator_status['processing_history']['error']} |

---

"""
            
            # Insert or update status section
            if "## Orchestrator Status" in content:
                # Replace existing section
                import re
                pattern = r'## Orchestrator Status.*?(?=##|\Z)'
                content = re.sub(pattern, status_section, content, flags=re.DOTALL)
            else:
                # Add after header
                if "# AI Employee Vault Dashboard\n" in content:
                    content = content.replace(
                        "# AI Employee Vault Dashboard\n",
                        f"# AI Employee Vault Dashboard\n\n{status_section}"
                    )
                else:
                    content = f"# AI Employee Vault Dashboard\n\n{status_section}{content}"
            
            self.dashboard_path.write_text(content, encoding='utf-8')
            self.logger.info("Dashboard updated")
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Orchestrator - Automatic Task Processor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Run continuously (watchdog or polling)
  %(prog)s --once              # Process existing files once
  %(prog)s --polling           # Force polling mode
  %(prog)s --status            # Show current status
  %(prog)s --vault /path       # Specify vault path
        """
    )
    
    parser.add_argument(
        '--vault',
        type=str,
        default=None,
        help='Vault path (default: current directory)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once (process existing files, then exit)'
    )
    parser.add_argument(
        '--polling',
        action='store_true',
        help='Force polling mode (instead of watchdog)'
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=None,
        help='Polling interval in seconds (default: 5.0)'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=None,
        help='Max reasoning loop iterations (default: 10)'
    )
    parser.add_argument(
        '--gmail-interval',
        type=int,
        default=None,
        help='Gmail check interval in seconds (default: 300)'
    )
    parser.add_argument(
        '--whatsapp-interval',
        type=int,
        default=None,
        help='WhatsApp check interval in seconds (default: 300)'
    )
    parser.add_argument(
        '--no-watchers',
        action='store_true',
        help='Disable auto-running Gmail/WhatsApp watchers'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current status and exit'
    )
    parser.add_argument(
        '--background',
        action='store_true',
        help='Run in background mode (same as default)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    vault_path = Path(args.vault) if args.vault else Path.cwd()
    config = Config.from_env(vault_path)
    
    # Apply CLI overrides
    if args.interval:
        config.poll_interval = args.interval
    if args.max_iterations:
        config.max_iterations = args.max_iterations
    if args.gmail_interval:
        config.gmail_check_interval = args.gmail_interval
    if args.whatsapp_interval:
        config.whatsapp_check_interval = args.whatsapp_interval
    if args.no_watchers:
        config.auto_run_watchers = False
    
    # Create orchestrator
    orchestrator = FileOrchestrator(config)
    
    # Dashboard updater
    dashboard_updater = DashboardUpdater(vault_path, orchestrator.logger)
    
    try:
        if args.status:
            # Show status
            status = orchestrator.get_status()
            print("\n" + "=" * 60)
            print("ORCHESTRATOR STATUS")
            print("=" * 60)
            print(f"Mode: {status['mode']}")
            print(f"API Configured: {status['api_configured']}")
            print(f"Running: {status['running']}")
            print(f"\nFolder Status:")
            for folder, count in status['folders'].items():
                print(f"  {folder}: {count} files")
            print(f"\nProcessing History:")
            for key, value in status['processing_history'].items():
                print(f"  {key}: {value}")
            print(f"\nWatcher Intervals:")
            print(f"  Gmail: Every {status['gmail_interval']}s")
            print(f"  WhatsApp: Every {status['whatsapp_interval']}s")
            print("=" * 60)
            
        elif args.once:
            # Run once
            processed = orchestrator.run_once()
            print(f"\n[OK] Processed {processed} file(s)")
            
            # Update dashboard
            dashboard_updater.update(orchestrator.get_status())
            
        else:
            # Run continuously
            print("\n" + "=" * 60)
            print("Orchestrator - Fully Automatic Gmail + WhatsApp Processor")
            print("=" * 60)
            print(f"Vault: {vault_path}")
            print(f"Mode: {'polling' if args.polling or not WATCHDOG_AVAILABLE else 'watchdog'}")
            print(f"Polling Interval: {config.poll_interval}s")
            print(f"Gmail Check: Every {config.gmail_check_interval}s")
            print(f"WhatsApp Check: Every {config.whatsapp_check_interval}s")
            print(f"Max Iterations: {config.max_iterations}")
            print(f"API Key: {'Configured' if config.api_key else 'Not configured (simulated mode)'}")
            print(f"Auto-run Watchers: {config.auto_run_watchers}")
            print("=" * 60)
            print("\nSystem will automatically:")
            print("  1. Check Gmail for new emails")
            print("  2. Check WhatsApp for new messages")
            print("  3. Process all files using AI (Ralph Loop)")
            print("  4. Move processed files to Done folder")
            print("=" * 60)
            print("\nPress Ctrl+C to stop\n")
            
            # Start watching
            if args.polling or not WATCHDOG_AVAILABLE:
                orchestrator.run_polling()
            else:
                orchestrator.run_watchdog()
            
            # Final dashboard update
            dashboard_updater.update(orchestrator.get_status())
            
    except KeyboardInterrupt:
        orchestrator.stop()
        print("\nStopped by user")
    except Exception as e:
        orchestrator.logger.error(f"Fatal error: {e}")
        raise
    
    print("\n" + "=" * 60)
    print("Orchestrator stopped")
    print("=" * 60)


if __name__ == '__main__':
    main()
