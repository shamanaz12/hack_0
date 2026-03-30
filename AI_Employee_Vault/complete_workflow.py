"""
Complete Workflow System - Gold Tier
Manages all services with proper workflow:
needs_action → logs → plans → inbox/approve → done

Usage:
  python complete_workflow.py start all
  python complete_workflow.py status
  python complete_workflow.py process
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directories
BASE_DIR = Path('AI_Employee_Vault')
BRONZE_DIR = BASE_DIR / 'Bronze_Tier'
SILVER_DIR = BASE_DIR / 'Silver_Tier'

# Workflow folders
WORKFLOW_FOLDERS = ['Needs_Action', 'Logs', 'Plans', 'inbox', 'Done']

# Services
SERVICES = {
    'facebook': {
        'watcher': 'watcher/facebook_instagram_watcher.py',
        'skill': 'skills/facebook_watcher_skill.py'
    },
    'instagram': {
        'watcher': 'watcher/facebook_instagram_watcher.py',
        'skill': 'skills/instagram_watcher_skill.py'
    },
    'gmail': {
        'watcher': 'gmail_watcher.py',
        'skill': 'skills/gmail_watcher_skill.py'
    },
    'whatsapp': {
        'watcher': 'whatsapp_watcher.py',
        'skill': 'skills/whatsapp_watcher_skill.py'
    },
    'calendar': {
        'server': 'mcp_servers/calendar_mcp.js',
        'skill': 'skills/calendar_skill.py'
    },
    'slack': {
        'server': 'mcp_servers/slack_mcp.js',
        'skill': 'skills/slack_skill.py'
    },
    'odoo': {
        'server': 'odoo_mcp_server.py',
        'skill': 'skills/odoo_skill.py'
    }
}


def create_workflow_folders():
    """Create workflow folders for all tiers"""
    print("Creating workflow folders...")
    
    for tier_dir in [BRONZE_DIR, SILVER_DIR]:
        for folder in WORKFLOW_FOLDERS:
            folder_path = tier_dir / folder
            folder_path.mkdir(exist_ok=True, parents=True)
            print(f"  [OK] {folder_path}")
    
    # Create skills folder
    skills_dir = BRONZE_DIR / 'skills'
    skills_dir.mkdir(exist_ok=True)
    print(f"  [OK] {skills_dir}")


def check_workflow_status():
    """Check status of all workflow items"""
    print("\n" + "=" * 60)
    print("   GOLD TIER - WORKFLOW STATUS")
    print("=" * 60)
    
    for tier_dir in [BRONZE_DIR, SILVER_DIR]:
        print(f"\n{tier_dir.name}:")
        print("-" * 40)
        
        for folder in WORKFLOW_FOLDERS:
            folder_path = tier_dir / folder
            if folder_path.exists():
                count = len(list(folder_path.glob('*.md')))
                print(f"  {folder:15} : {count} items")
    
    print("\n" + "=" * 60)


def process_needs_action():
    """Process items in Needs_Action folder"""
    print("\nProcessing Needs_Action items...")
    
    needs_action_dir = BRONZE_DIR / 'Needs_Action'
    
    if not needs_action_dir.exists():
        print("  ℹ️  Needs_Action folder not found")
        return
    
    files = list(needs_action_dir.glob('*.md'))
    
    if not files:
        print("  ℹ️  No items to process")
        return
    
    for file in files:
        print(f"\n  Processing: {file.name}")
        
        # Read the request
        content = file.read_text(encoding='utf-8')
        
        # Determine type and move to Logs
        if 'facebook' in file.name.lower() or 'facebook' in content.lower():
            service = 'facebook'
        elif 'instagram' in file.name.lower():
            service = 'instagram'
        elif 'email' in file.name.lower() or 'gmail' in content.lower():
            service = 'gmail'
        elif 'whatsapp' in file.name.lower():
            service = 'whatsapp'
        else:
            service = 'general'
        
        # Create log entry
        log_entry = f"""# Log Entry - {file.stem}

**Service:** {service}
**Started:** {datetime.now()}
**Status:** Processing

## Actions:
1. Received request
2. Analyzing content
3. Creating plan

"""
        
        log_file = BRONZE_DIR / 'Logs' / f"{file.stem}_log.md"
        log_file.write_text(log_entry, encoding='utf-8')
        print(f"    ✅ Log created: {log_file.name}")
        
        # Create plan
        plan_content = f"""# Plan - {file.stem}

**Original Request:** {file.name}
**Service:** {service}
**Created:** {datetime.now()}

## Plan:
1. Process request
2. Generate content/action
3. Submit for approval

## Next Steps:
- [ ] Generate content
- [ ] Submit for approval
- [ ] Execute after approval

"""
        
        plan_file = BRONZE_DIR / 'Plans' / f"{file.stem}_plan.md"
        plan_file.write_text(plan_content, encoding='utf-8')
        print(f"    ✅ Plan created: {plan_file.name}")
        
        # Move to inbox for approval
        inbox_content = f"""# Approval Required - {file.stem}

**Type:** {service.title()} Request
**Status:** Awaiting Approval
**Created:** {datetime.now()}

## Original Request:
```
{content[:500]}...
```

## Actions:
- [ ] Approve
- [ ] Edit
- [ ] Reject

## Approval:
**Approved by:** ________________
**Date:** ________________
**Comments:** ________________

"""
        
        inbox_file = BRONZE_DIR / 'inbox' / f"{file.stem}_approval.md"
        inbox_file.write_text(inbox_content, encoding='utf-8')
        print(f"    ✅ Approval request created: {inbox_file.name}")
        
        # Mark as processed (don't delete, just rename)
        processed_file = needs_action_dir / f"processed_{file.name}"
        file.rename(processed_file)
        print(f"    ✅ Moved to processed")
    
    print("\n  ✅ All Needs_Action items processed!")


def start_all_services():
    """Start all services"""
    print("\nStarting all services...")
    
    import subprocess
    
    for name, config in SERVICES.items():
        print(f"\n  Starting {name}...")
        
        if 'watcher' in config:
            script = Path(config['watcher'])
            if script.exists():
                # Start in background
                cmd = [sys.executable, str(script), '--interval', '60']
                subprocess.Popen(cmd, cwd=os.getcwd())
                print(f"    ✅ {name} watcher started")
            else:
                print(f"    ❌ Script not found: {script}")
        
        if 'server' in config:
            script = Path(config['server'])
            if script.exists():
                if script.suffix == '.js':
                    cmd = ['node', str(script)]
                else:
                    cmd = [sys.executable, str(script)]
                subprocess.Popen(cmd, cwd=os.getcwd())
                print(f"    ✅ {name} server started")
            else:
                print(f"    ❌ Script not found: {script}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python complete_workflow.py setup      - Create folders")
        print("  python complete_workflow.py start all  - Start all services")
        print("  python complete_workflow.py status     - Check status")
        print("  python complete_workflow.py process    - Process needs_action")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'setup':
        create_workflow_folders()
    
    elif command == 'start':
        if len(sys.argv) > 2 and sys.argv[2].lower() == 'all':
            start_all_services()
        else:
            print("Specify 'all' to start all services")
    
    elif command == 'status':
        check_workflow_status()
    
    elif command == 'process':
        process_needs_action()
    
    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
