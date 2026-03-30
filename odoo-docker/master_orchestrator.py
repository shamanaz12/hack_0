#!/usr/bin/env python3
"""
Master Orchestrator - Gold Tier Complete System Integration

Integrates all MCP servers and systems:
- Odoo MCP (Accounting)
- Facebook MCP (Social Media)
- Instagram MCP (Social Media)
- Email MCP (Communication)
- WhatsApp MCP (Communication)
- Weekly Audit System
- Error Recovery System
- Audit Logger
- Ralph Loop (AI Reasoning)

Usage:
    python master_orchestrator.py start     # Start all services
    python master_orchestrator.py stop      # Stop all services
    python master_orchestrator.py status    # Check status
    python master_orchestrator.py health    # Health check
    python master_orchestrator.py audit     # Run weekly audit
    python master_orchestrator.py report    # Generate reports
"""

import os
import sys
import json
import time
import signal
import logging
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/master_orchestrator.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    script: str
    port: Optional[int]
    health_endpoint: Optional[str]
    auto_start: bool
    restart_on_error: bool
    max_restarts: int
    env_vars: Dict[str, str]


@dataclass
class ServiceState:
    """Service state"""
    config: ServiceConfig
    status: ServiceStatus
    process: Optional[subprocess.Popen]
    pid: Optional[int]
    started_at: Optional[str]
    last_error: Optional[str]
    restart_count: int
    health_check_passed: Optional[bool]


class MasterOrchestrator:
    """Master Orchestrator for Gold Tier System"""
    
    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else Path(__file__).parent
        self.logs_folder = self.vault_path / 'logs'
        self.state_folder = self.vault_path / 'AI_Employee_Vault' / 'Orchestrator'
        
        # Create folders
        os.makedirs(self.logs_folder, exist_ok=True)
        os.makedirs(self.state_folder, exist_ok=True)
        
        # State file
        self.state_file = self.vault_path / 'master_orchestrator_state.json'
        
        # Initialize services
        self.services: Dict[str, ServiceState] = {}
        self._init_services()
        
        # Load state
        self._load_state()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Master Orchestrator initialized")
    
    def _init_services(self):
        """Initialize service configurations"""
        
        services_config = [
            ServiceConfig(
                name='odoo_mcp',
                script='odoo_mcp_server.py',
                port=None,
                health_endpoint=None,
                auto_start=True,
                restart_on_error=True,
                max_restarts=3,
                env_vars={}
            ),
            ServiceConfig(
                name='facebook_mcp',
                script='facebook_mcp.js',
                port=3000,
                health_endpoint='/health',
                auto_start=os.getenv('FACEBOOK_AUTO_START', 'false').lower() == 'true',
                restart_on_error=True,
                max_restarts=3,
                env_vars={}
            ),
            ServiceConfig(
                name='instagram_mcp',
                script='instagram_mcp.js',
                port=3001,
                health_endpoint='/health',
                auto_start=os.getenv('INSTAGRAM_AUTO_START', 'false').lower() == 'true',
                restart_on_error=True,
                max_restarts=3,
                env_vars={}
            ),
            ServiceConfig(
                name='email_mcp',
                script='mcp_email_server.py',
                port=None,
                health_endpoint=None,
                auto_start=True,
                restart_on_error=True,
                max_restarts=3,
                env_vars={}
            ),
            ServiceConfig(
                name='gmail_watcher',
                script='gmail_watcher.py',
                port=None,
                health_endpoint=None,
                auto_start=True,
                restart_on_error=True,
                max_restarts=3,
                env_vars={}
            ),
            ServiceConfig(
                name='whatsapp_watcher',
                script='whatsapp_watcher.py',
                port=None,
                health_endpoint=None,
                auto_start=True,
                restart_on_error=True,
                max_restarts=3,
                env_vars={}
            ),
            ServiceConfig(
                name='orchestrator',
                script='orchestrator.py',
                port=None,
                health_endpoint=None,
                auto_start=True,
                restart_on_error=True,
                max_restarts=3,
                env_vars={}
            ),
            ServiceConfig(
                name='ralph_loop',
                script='ralph_loop.py',
                port=None,
                health_endpoint=None,
                auto_start=False,
                restart_on_error=False,
                max_restarts=1,
                env_vars={}
            )
        ]
        
        for config in services_config:
            self.services[config.name] = ServiceState(
                config=config,
                status=ServiceStatus.STOPPED,
                process=None,
                pid=None,
                started_at=None,
                last_error=None,
                restart_count=0,
                health_check_passed=None
            )
    
    def _load_state(self):
        """Load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded state from {self.state_file}")
            except Exception as e:
                logger.error(f"Error loading state: {e}")
    
    def _save_state(self):
        """Save state to file"""
        data = {}
        for name, state in self.services.items():
            data[name] = {
                'status': state.status.value,
                'pid': state.pid,
                'started_at': state.started_at,
                'last_error': state.last_error,
                'restart_count': state.restart_count
            }
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop_all()
        sys.exit(0)
    
    def start_service(self, service_name: str) -> bool:
        """Start a service"""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        state = self.services[service_name]
        
        if state.status in [ServiceStatus.RUNNING, ServiceStatus.STARTING]:
            logger.warning(f"Service {service_name} is already running")
            return True
        
        logger.info(f"Starting service: {service_name}")
        state.status = ServiceStatus.STARTING
        
        try:
            script_path = self.vault_path / state.config.script
            
            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_path}")
            
            # Determine command
            if script_path.suffix == '.js':
                cmd = ['node', str(script_path)]
            else:
                cmd = [sys.executable, str(script_path)]
            
            # Set environment
            env = os.environ.copy()
            env.update(state.config.env_vars)
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=str(self.vault_path)
            )
            
            state.process = process
            state.pid = process.pid
            state.started_at = datetime.now().isoformat()
            state.status = ServiceStatus.RUNNING
            state.last_error = None
            
            logger.info(f"Service {service_name} started with PID {process.pid}")
            
            self._save_state()
            return True
        
        except Exception as e:
            state.status = ServiceStatus.ERROR
            state.last_error = str(e)
            logger.error(f"Error starting service {service_name}: {e}")
            self._save_state()
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a service"""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        state = self.services[service_name]
        
        if state.status == ServiceStatus.STOPPED:
            logger.info(f"Service {service_name} is already stopped")
            return True
        
        logger.info(f"Stopping service: {service_name}")
        state.status = ServiceStatus.STOPPING
        
        try:
            if state.process:
                state.process.terminate()
                state.process.wait(timeout=10)
            
            state.process = None
            state.pid = None
            state.status = ServiceStatus.STOPPED
            
            logger.info(f"Service {service_name} stopped")
            
            self._save_state()
            return True
        
        except Exception as e:
            state.status = ServiceStatus.ERROR
            state.last_error = str(e)
            logger.error(f"Error stopping service {service_name}: {e}")
            
            # Force kill
            if state.process:
                state.process.kill()
            
            self._save_state()
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a service"""
        logger.info(f"Restarting service: {service_name}")
        self.stop_service(service_name)
        time.sleep(2)
        return self.start_service(service_name)
    
    def start_all(self):
        """Start all auto-start services"""
        logger.info("=" * 60)
        logger.info("Starting all services")
        logger.info("=" * 60)
        
        for name, state in self.services.items():
            if state.config.auto_start:
                self.start_service(name)
                time.sleep(2)  # Stagger starts
        
        logger.info("All services started")
    
    def stop_all(self):
        """Stop all services"""
        logger.info("=" * 60)
        logger.info("Stopping all services")
        logger.info("=" * 60)
        
        for name in reversed(list(self.services.keys())):
            self.stop_service(name)
            time.sleep(1)
        
        logger.info("All services stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        status = {}
        
        for name, state in self.services.items():
            status[name] = {
                'status': state.status.value,
                'pid': state.pid,
                'started_at': state.started_at,
                'uptime': self._calculate_uptime(state.started_at),
                'restart_count': state.restart_count,
                'last_error': state.last_error,
                'health_check': state.health_check_passed
            }
        
        return status
    
    def _calculate_uptime(self, started_at: str) -> str:
        """Calculate uptime from start time"""
        if not started_at:
            return "0s"
        
        try:
            start = datetime.fromisoformat(started_at)
            delta = datetime.now() - start
            return str(delta).split('.')[0]  # Remove microseconds
        except:
            return "unknown"
    
    def health_check(self) -> Dict[str, bool]:
        """Run health checks on all running services"""
        import requests
        
        results = {}
        
        for name, state in self.services.items():
            if state.status != ServiceStatus.RUNNING:
                results[name] = None  # Not running
                continue
            
            if state.config.health_endpoint and state.config.port:
                try:
                    url = f"http://localhost:{state.config.port}{state.config.health_endpoint}"
                    response = requests.get(url, timeout=5)
                    healthy = response.status_code == 200
                    results[name] = healthy
                    state.health_check_passed = healthy
                    
                    if not healthy:
                        logger.warning(f"Health check failed for {name}")
                
                except Exception as e:
                    results[name] = False
                    state.health_check_passed = False
                    logger.error(f"Health check error for {name}: {e}")
            else:
                # No health endpoint, assume healthy if running
                results[name] = True
                state.health_check_passed = True
        
        self._save_state()
        return results
    
    def run_weekly_audit(self) -> bool:
        """Run weekly business audit"""
        logger.info("Running weekly audit...")
        
        try:
            audit_script = self.vault_path / 'weekly_audit.py'
            
            if not audit_script.exists():
                logger.error("Weekly audit script not found")
                return False
            
            result = subprocess.run(
                [sys.executable, str(audit_script)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("Weekly audit completed successfully")
                return True
            else:
                logger.error(f"Weekly audit failed: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Weekly audit error: {e}")
            return False
    
    def generate_reports(self) -> List[str]:
        """Generate all reports"""
        report_files = []
        
        # Import audit logger
        try:
            sys.path.insert(0, str(self.vault_path))
            from audit_logger import AuditLogger
            
            audit = AuditLogger(vault_path=str(self.vault_path))
            report_file = audit.save_report(days=7)
            report_files.append(str(report_file))
            logger.info(f"Audit report saved: {report_file}")
        
        except Exception as e:
            logger.error(f"Error generating audit report: {e}")
        
        # Import error recovery
        try:
            from error_recovery import ErrorRecoverySystem
            
            recovery = ErrorRecoverySystem(vault_path=str(self.vault_path))
            report_file = recovery.save_error_report()
            report_files.append(str(report_file))
            logger.info(f"Error report saved: {report_file}")
        
        except Exception as e:
            logger.error(f"Error generating error report: {e}")
        
        return report_files
    
    def monitor_loop(self, check_interval: int = 60):
        """Run monitoring loop"""
        logger.info(f"Starting monitoring loop (interval: {check_interval}s)")
        
        while True:
            try:
                # Health check
                health_results = self.health_check()
                
                # Check for failed services
                for name, healthy in health_results.items():
                    if healthy == False:  # Failed
                        state = self.services[name]
                        
                        if state.config.restart_on_error:
                            if state.restart_count < state.config.max_restarts:
                                logger.warning(f"Restarting failed service: {name}")
                                state.restart_count += 1
                                self.restart_service(name)
                            else:
                                logger.error(f"Service {name} exceeded max restarts")
                
                # Sleep
                time.sleep(check_interval)
            
            except KeyboardInterrupt:
                logger.info("Monitoring interrupted")
                break
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(check_interval)
    
    def print_status(self):
        """Print formatted status"""
        status = self.get_status()
        
        print("\n" + "=" * 80)
        print("MASTER ORCHESTRATOR - SERVICE STATUS")
        print("=" * 80)
        print(f"{'Service':<20} {'Status':<12} {'PID':<8} {'Uptime':<15} {'Restarts':<10} {'Health'}")
        print("-" * 80)
        
        for name, info in status.items():
            status_icon = {
                'running': '✅',
                'stopped': '⏹️',
                'error': '❌',
                'starting': '🔄',
                'stopping': '🛑'
            }.get(info['status'], '❓')
            
            health_icon = {
                True: '✅',
                False: '❌',
                None: '-'
            }.get(info['health_check'], '-')
            
            print(f"{name:<20} {status_icon} {info['status']:<10} {str(info['pid'] or 'N/A'):<8} {info['uptime']:<15} {info['restart_count']:<10} {health_icon}")
        
        print("=" * 80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Master Orchestrator')
    parser.add_argument('command', type=str, choices=[
        'start', 'stop', 'status', 'health', 'audit', 'report', 'monitor', 'restart'
    ], help='Command to execute')
    parser.add_argument('--service', type=str, help='Specific service to operate on')
    parser.add_argument('--vault', type=str, help='Path to vault folder')
    parser.add_argument('--interval', type=int, default=60, help='Monitor check interval (seconds)')
    args = parser.parse_args()
    
    orchestrator = MasterOrchestrator(vault_path=args.vault)
    
    if args.command == 'start':
        if args.service:
            orchestrator.start_service(args.service)
        else:
            orchestrator.start_all()
    
    elif args.command == 'stop':
        if args.service:
            orchestrator.stop_service(args.service)
        else:
            orchestrator.stop_all()
    
    elif args.command == 'status':
        orchestrator.print_status()
    
    elif args.command == 'health':
        results = orchestrator.health_check()
        print("\nHealth Check Results:")
        for name, healthy in results.items():
            icon = '✅' if healthy else ('❌' if healthy == False else '-')
            print(f"  {icon} {name}")
    
    elif args.command == 'audit':
        success = orchestrator.run_weekly_audit()
        print(f"Weekly audit: {'✅ Success' if success else '❌ Failed'}")
    
    elif args.command == 'report':
        reports = orchestrator.generate_reports()
        print("\nGenerated Reports:")
        for report in reports:
            print(f"  📄 {report}")
    
    elif args.command == 'restart':
        if args.service:
            orchestrator.restart_service(args.service)
        else:
            orchestrator.stop_all()
            time.sleep(3)
            orchestrator.start_all()
    
    elif args.command == 'monitor':
        orchestrator.monitor_loop(check_interval=args.interval)


if __name__ == '__main__':
    main()
