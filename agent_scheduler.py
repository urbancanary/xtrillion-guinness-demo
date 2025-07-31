#!/usr/bin/env python3
"""
Agent Scheduler System
======================

Centralized scheduling and execution system for all maintenance agents.
Supports manual execution, cron scheduling, and automated workflows.

Usage:
    python3 agent_scheduler.py --run-all              # Run all agents now
    python3 agent_scheduler.py --run doc              # Run specific agent
    python3 agent_scheduler.py --schedule daily       # Set up daily schedule
    python3 agent_scheduler.py --status               # Check scheduled jobs
"""

import os
import sys
import subprocess
import argparse
import json
# import schedule  # Optional dependency for advanced scheduling
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading

class AgentScheduler:
    """
    Centralized scheduler for all maintenance agents
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.agents = {
            'doc': {
                'name': 'Documentation Maintenance',
                'script': 'doc_maintenance_agent.py',
                'args': ['--check'],
                'description': 'Validates API docs and examples',
                'requires_api': True,
                'frequency': 'before_demos'
            },
            'duplication': {
                'name': 'Code Duplication Detection', 
                'script': 'code_duplication_agent.py',
                'args': ['--scan', '--update-tasks'],
                'description': 'Finds duplicate code patterns',
                'requires_api': False,
                'frequency': 'weekly'
            },
            'orphaned': {
                'name': 'Orphaned Code Detection',
                'script': 'orphaned_code_agent.py', 
                'args': ['--scan', '--update-tasks'],
                'description': 'Finds unused and obsolete files',
                'requires_api': False,
                'frequency': 'bi_weekly'
            }
        }
        
        self.schedule_config_file = 'agent_schedule.json'
        self.last_run_file = 'agent_last_run.json'
        
    def log(self, message: str, level: str = "INFO"):
        """Structured logging with timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def check_agent_available(self, agent_key: str) -> bool:
        """Check if agent script exists and is executable"""
        agent = self.agents[agent_key]
        script_path = os.path.join(self.project_root, agent['script'])
        
        if not os.path.exists(script_path):
            self.log(f"❌ Agent script not found: {script_path}", "ERROR")
            return False
            
        if not os.access(script_path, os.X_OK):
            self.log(f"⚠️  Agent script not executable: {script_path}", "WARNING")
            try:
                os.chmod(script_path, 0o755)
                self.log(f"✅ Made script executable: {script_path}")
            except Exception as e:
                self.log(f"❌ Could not make executable: {e}", "ERROR")
                return False
        
        return True
    
    def check_api_available(self) -> bool:
        """Check if local API is running (for doc agent)"""
        try:
            import requests
            response = requests.get('http://localhost:8080/health', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def run_agent(self, agent_key: str, extra_args: List[str] = None) -> Dict:
        """Run a specific agent and return results"""
        if agent_key not in self.agents:
            return {'success': False, 'error': f'Unknown agent: {agent_key}'}
        
        agent = self.agents[agent_key]
        
        # Check if agent is available
        if not self.check_agent_available(agent_key):
            return {'success': False, 'error': 'Agent script not available'}
        
        # Check API requirement
        if agent.get('requires_api', False) and not self.check_api_available():
            self.log(f"⚠️  {agent['name']}: API not available, skipping", "WARNING")
            return {'success': False, 'error': 'API not available', 'skipped': True}
        
        # Prepare command
        script_path = os.path.join(self.project_root, agent['script'])
        cmd = ['python3', script_path] + agent['args']
        if extra_args:
            cmd.extend(extra_args)
        
        self.log(f"🚀 Running {agent['name']}...")
        
        try:
            # Run the agent
            start_time = time.time()
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            end_time = time.time()
            
            # Record the run
            self.record_agent_run(agent_key, {
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': round(end_time - start_time, 2),
                'exit_code': result.returncode,
                'success': result.returncode == 0
            })
            
            if result.returncode == 0:
                self.log(f"✅ {agent['name']} completed successfully ({end_time - start_time:.1f}s)")
                return {
                    'success': True,
                    'duration': end_time - start_time,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                self.log(f"❌ {agent['name']} failed with exit code {result.returncode}", "ERROR")
                return {
                    'success': False,
                    'exit_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
        
        except subprocess.TimeoutExpired:
            self.log(f"⏰ {agent['name']} timed out after 5 minutes", "ERROR")
            return {'success': False, 'error': 'Timeout after 5 minutes'}
        
        except Exception as e:
            self.log(f"❌ {agent['name']} failed: {e}", "ERROR")
            return {'success': False, 'error': str(e)}
    
    def run_all_agents(self, skip_api_dependent: bool = False) -> Dict:
        """Run all available agents"""
        self.log("🤖 Running all maintenance agents...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'agents_run': {},
            'summary': {'total': 0, 'successful': 0, 'failed': 0, 'skipped': 0}
        }
        
        for agent_key, agent in self.agents.items():
            if skip_api_dependent and agent.get('requires_api', False):
                self.log(f"⏭️  Skipping {agent['name']} (API-dependent)")
                results['summary']['skipped'] += 1
                continue
            
            result = self.run_agent(agent_key)
            results['agents_run'][agent_key] = result
            results['summary']['total'] += 1
            
            if result['success']:
                results['summary']['successful'] += 1
            elif result.get('skipped'):
                results['summary']['skipped'] += 1
            else:
                results['summary']['failed'] += 1
        
        # Print summary
        summary = results['summary']
        self.log(f"📊 Agent execution summary:")
        self.log(f"   Total: {summary['total']}, Successful: {summary['successful']}, Failed: {summary['failed']}, Skipped: {summary['skipped']}")
        
        return results
    
    def record_agent_run(self, agent_key: str, run_data: Dict):
        """Record when an agent was last run"""
        last_runs = {}
        
        # Load existing data
        if os.path.exists(self.last_run_file):
            try:
                with open(self.last_run_file, 'r') as f:
                    last_runs = json.load(f)
            except:
                pass
        
        # Update with new run
        last_runs[agent_key] = run_data
        
        # Save back
        with open(self.last_run_file, 'w') as f:
            json.dump(last_runs, f, indent=2)
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents and their last runs"""
        status = {
            'agents': {},
            'api_available': self.check_api_available(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Load last run data
        last_runs = {}
        if os.path.exists(self.last_run_file):
            try:
                with open(self.last_run_file, 'r') as f:
                    last_runs = json.load(f)
            except:
                pass
        
        # Check each agent
        for agent_key, agent in self.agents.items():
            agent_status = {
                'name': agent['name'],
                'description': agent['description'],
                'frequency': agent['frequency'],
                'requires_api': agent.get('requires_api', False),
                'script_available': self.check_agent_available(agent_key),
                'last_run': last_runs.get(agent_key, {})
            }
            
            # Calculate time since last run
            if agent_status['last_run']:
                try:
                    last_run_time = datetime.fromisoformat(agent_status['last_run']['timestamp'])
                    hours_since = (datetime.now() - last_run_time).total_seconds() / 3600
                    agent_status['hours_since_last_run'] = round(hours_since, 1)
                except:
                    pass
            
            status['agents'][agent_key] = agent_status
        
        return status
    
    def setup_cron_schedule(self, frequency: str = 'daily'):
        """Set up cron schedule for agents"""
        cron_entries = []
        
        if frequency == 'daily':
            # Documentation check daily at 9 AM (if API available)
            cron_entries.append(f"0 9 * * * cd {os.path.abspath(self.project_root)} && python3 agent_scheduler.py --run doc")
            
            # Code analysis weekly on Mondays at 8 AM
            cron_entries.append(f"0 8 * * 1 cd {os.path.abspath(self.project_root)} && python3 agent_scheduler.py --run duplication")
            
            # Orphaned code check bi-weekly on alternate Mondays at 8:30 AM
            cron_entries.append(f"30 8 * * 1 cd {os.path.abspath(self.project_root)} && python3 agent_scheduler.py --run orphaned")
        
        elif frequency == 'development':
            # More frequent checks for active development
            cron_entries.append(f"0 */4 * * * cd {os.path.abspath(self.project_root)} && python3 agent_scheduler.py --run doc")
            cron_entries.append(f"0 10 * * * cd {os.path.abspath(self.project_root)} && python3 agent_scheduler.py --run duplication")
            cron_entries.append(f"0 16 * * * cd {os.path.abspath(self.project_root)} && python3 agent_scheduler.py --run orphaned")
        
        # Write cron file
        cron_file = 'agent_cron_schedule.txt'
        with open(cron_file, 'w') as f:
            f.write(f"# XTrillion Agent Scheduler - {frequency.title()} Schedule\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# Add these lines to your crontab with 'crontab -e'\n\n")
            for entry in cron_entries:
                f.write(entry + "\n")
        
        self.log(f"📝 Created cron schedule file: {cron_file}")
        self.log(f"💡 To activate: crontab {cron_file}")
        
        return cron_entries

def main():
    parser = argparse.ArgumentParser(description="Agent Scheduler System")
    parser.add_argument('--run', help='Run specific agent (doc, duplication, orphaned)')
    parser.add_argument('--run-all', action='store_true', help='Run all agents')
    parser.add_argument('--status', action='store_true', help='Show agent status')
    parser.add_argument('--schedule', help='Set up schedule (daily, development)')
    parser.add_argument('--skip-api', action='store_true', help='Skip API-dependent agents')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    
    args = parser.parse_args()
    
    # Create scheduler
    scheduler = AgentScheduler(args.project_root)
    
    if args.status:
        status = scheduler.get_agent_status()
        print("\n🤖 Agent Status Report")
        print("=" * 50)
        print(f"API Available: {'✅' if status['api_available'] else '❌'}")
        print()
        
        for agent_key, agent_status in status['agents'].items():
            print(f"**{agent_status['name']}** ({agent_key})")
            print(f"   Description: {agent_status['description']}")
            print(f"   Frequency: {agent_status['frequency']}")
            print(f"   Script Available: {'✅' if agent_status['script_available'] else '❌'}")
            print(f"   Requires API: {'Yes' if agent_status['requires_api'] else 'No'}")
            
            if agent_status['last_run']:
                last_run = agent_status['last_run']
                hours_ago = agent_status.get('hours_since_last_run', 'Unknown')
                success = '✅' if last_run.get('success') else '❌'
                print(f"   Last Run: {hours_ago}h ago {success}")
            else:
                print(f"   Last Run: Never")
            print()
    
    elif args.run:
        result = scheduler.run_agent(args.run)
        if not result['success'] and not result.get('skipped'):
            sys.exit(1)
    
    elif args.run_all:
        results = scheduler.run_all_agents(skip_api_dependent=args.skip_api)
        if results['summary']['failed'] > 0:
            sys.exit(1)
    
    elif args.schedule:
        scheduler.setup_cron_schedule(args.schedule)
    
    else:
        print("🤖 XTrillion Agent Scheduler")
        print("=" * 30)
        print("Available commands:")
        print("  --status           Show agent status")
        print("  --run <agent>      Run specific agent")
        print("  --run-all          Run all agents")
        print("  --schedule daily   Set up daily schedule")
        print()
        print("Available agents: doc, duplication, orphaned")

if __name__ == "__main__":
    main()