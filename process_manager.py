"""
Gold Tier Process Manager
Alternative to PM2 - Pure Python
Manages all Gold Tier services

Usage:
  python process_manager.py start all
  python process_manager.py start facebook-watcher
  python process_manager.py stop all
  python process_manager.py status
  python process_manager.py logs facebook-watcher
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path
from datetime import datetime

# Services configuration
SERVICES = {
    'facebook-watcher': {
        'script': 'watcher/facebook_instagram_watcher.py',
        'args': '--interval 60',
        'log': 'logs/process-facebook-watcher.log'
    },
    'gmail-watcher': {
        'script': 'gmail_watcher.py',
        'args': '',
        'log': 'logs/process-gmail-watcher.log'
    },
    'whatsapp-watcher': {
        'script': 'whatsapp_watcher.py',
        'args': '',
        'log': 'logs/process-whatsapp-watcher.log'
    },
    'orchestrator': {
        'script': 'orchestrator.py',
        'args': '',
        'log': 'logs/process-orchestrator.log'
    },
    'scheduler': {
        'script': 'scheduler.py',
        'args': '',
        'log': 'logs/process-scheduler.log'
    },
    'auto-processor': {
        'script': 'auto_processor.py',
        'args': '',
        'log': 'logs/process-auto-processor.log'
    },
    'mcp-email-server': {
        'script': 'mcp_email_server.py',
        'args': '',
        'log': 'logs/process-mcp-email.log'
    },
    'odoo-mcp-server': {
        'script': 'odoo_mcp_server.py',
        'args': '',
        'log': 'logs/process-odoo-mcp.log'
    }
}

PID_DIR = Path('pids')
PID_DIR.mkdir(exist_ok=True)


def start_service(name):
    """Start a service"""
    if name not in SERVICES:
        print(f"❌ Unknown service: {name}")
        return False
    
    service = SERVICES[name]
    pid_file = PID_DIR / f"{name}.pid"
    
    # Check if already running
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text())
            # Check if process is running
            os.kill(pid, 0)
            print(f"✅ {name} already running (PID: {pid})")
            return True
        except (ProcessLookupError, ValueError):
            pid_file.unlink()
    
    # Start service
    print(f"🚀 Starting {name}...")
    
    cmd = [sys.executable, service['script']]
    if service['args']:
        cmd.extend(service['args'].split())
    
    log_file = Path(service['log'])
    log_file.parent.mkdir(exist_ok=True)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Started at: {datetime.now()}\n")
        f.write(f"{'='*60}\n")
        f.flush()
        
        process = subprocess.Popen(
            cmd,
            stdout=f,
            stderr=f,
            cwd=os.getcwd()
        )
    
    # Save PID
    pid_file.write_text(str(process.pid))
    print(f"✅ {name} started (PID: {process.pid})")
    return True


def stop_service(name):
    """Stop a service"""
    pid_file = PID_DIR / f"{name}.pid"
    
    if not pid_file.exists():
        print(f"ℹ️  {name} not running")
        return False
    
    try:
        pid = int(pid_file.read_text())
        process = subprocess.Popen(f'taskkill /F /PID {pid}', shell=True)
        process.wait()
        pid_file.unlink()
        print(f"⏹️  {name} stopped")
        return True
    except Exception as e:
        print(f"❌ Error stopping {name}: {e}")
        return False


def status():
    """Show status of all services"""
    print("=" * 60)
    print("   GOLD TIER - SERVICE STATUS")
    print("=" * 60)
    print()
    
    for name in SERVICES:
        pid_file = PID_DIR / f"{name}.pid"
        
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text())
                os.kill(pid, 0)
                print(f"[RUNNING] {name:25} (PID: {pid})")
            except (ProcessLookupError, ValueError):
                print(f"[DEAD]    {name:25} (stale PID file)")
        else:
            print(f"[STOPPED]  {name:25}")
    
    print()
    print("=" * 60)


def logs(name, lines=50):
    """Show logs for a service"""
    if name not in SERVICES:
        print(f"❌ Unknown service: {name}")
        return
    
    log_file = Path(SERVICES[name]['log'])
    
    if not log_file.exists():
        print(f"ℹ️  No logs found for {name}")
        return
    
    print(f"\n{'='*60}")
    print(f"   LOGS: {name}")
    print(f"{'='*60}\n")
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Show last N lines
            lines_list = content.split('\n')[-lines:]
            print('\n'.join(lines_list))
    except Exception as e:
        print(f"❌ Error reading logs: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python process_manager.py start <service|all>")
        print("  python process_manager.py stop <service|all>")
        print("  python process_manager.py restart <service|all>")
        print("  python process_manager.py status")
        print("  python process_manager.py logs <service>")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        if len(sys.argv) < 3:
            print("Specify service name or 'all'")
            return
        
        service = sys.argv[2].lower()
        if service == 'all':
            for name in SERVICES:
                start_service(name)
        else:
            start_service(service)
    
    elif command == 'stop':
        if len(sys.argv) < 3:
            print("Specify service name or 'all'")
            return
        
        service = sys.argv[2].lower()
        if service == 'all':
            for name in reversed(list(SERVICES.keys())):
                stop_service(name)
        else:
            stop_service(service)
    
    elif command == 'restart':
        if len(sys.argv) < 3:
            print("Specify service name or 'all'")
            return
        
        service = sys.argv[2].lower()
        if service == 'all':
            for name in SERVICES:
                stop_service(name)
                time.sleep(1)
                start_service(name)
        else:
            stop_service(service)
            time.sleep(1)
            start_service(service)
    
    elif command == 'status':
        status()
    
    elif command == 'logs':
        if len(sys.argv) < 3:
            print("Specify service name")
            return
        logs(sys.argv[2])
    
    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
