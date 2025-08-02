#!/usr/bin/env python3
"""
XTrillion Core - Claude Code Deployment Agent
Interactive menu system for safe deployment management
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional
import requests

class XTrillionDeploymentAgent:
    def __init__(self):
        self.project_root = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
        self.current_branch = self.get_current_branch()
        self.version = "v10.0.0"
        
        # Color codes for output
        self.colors = {
            'RED': '\033[0;31m',
            'GREEN': '\033[0;32m',
            'YELLOW': '\033[1;33m',
            'BLUE': '\033[0;34m',
            'PURPLE': '\033[0;35m',
            'CYAN': '\033[0;36m',
            'WHITE': '\033[1;37m',
            'NC': '\033[0m'  # No Color
        }
        
    def print_colored(self, text: str, color: str = 'WHITE'):
        """Print colored text"""
        print(f"{self.colors.get(color, '')}{text}{self.colors['NC']}")
        
    def get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def check_git_status(self) -> Dict:
        """Check git repository status"""
        try:
            # Check for uncommitted changes
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         capture_output=True, text=True, cwd=self.project_root)
            has_changes = bool(status_result.stdout.strip())
            
            # Get current commit
            commit_result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                         capture_output=True, text=True, cwd=self.project_root)
            commit_hash = commit_result.stdout.strip()
            
            return {
                'branch': self.current_branch,
                'has_uncommitted_changes': has_changes,
                'commit_hash': commit_hash,
                'changes': status_result.stdout.strip().split('\n') if has_changes else []
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_api_health(self, url: str) -> Dict:
        """Check API health endpoint"""
        try:
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                return {'status': 'healthy', 'data': response.json()}
            else:
                return {'status': 'unhealthy', 'code': response.status_code}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def run_deployment_script(self, script_name: str) -> Dict:
        """Run deployment script and capture output"""
        script_path = os.path.join(self.project_root, script_name)
        
        if not os.path.exists(script_path):
            return {'success': False, 'error': f'Script {script_name} not found'}
        
        try:
            # Make script executable
            subprocess.run(['chmod', '+x', script_path])
            
            # Run script interactively
            process = subprocess.Popen([script_path], 
                                     cwd=self.project_root,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     text=True,
                                     bufsize=1,
                                     universal_newlines=True)
            
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    output_lines.append(output.strip())
            
            return_code = process.poll()
            return {
                'success': return_code == 0,
                'output': '\n'.join(output_lines),
                'return_code': return_code
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def display_main_menu(self):
        """Display main deployment menu"""
        os.system('clear')  # Clear screen
        
        self.print_colored("🚀 XTrillion Core - Claude Code Deployment Agent", 'CYAN')
        self.print_colored("=" * 60, 'BLUE')
        
        # Show current status
        git_status = self.check_git_status()
        self.print_colored(f"📋 Current Branch: {git_status.get('branch', 'unknown')}", 'YELLOW')
        self.print_colored(f"📋 Commit: {git_status.get('commit_hash', 'unknown')}", 'YELLOW')
        
        if git_status.get('has_uncommitted_changes'):
            self.print_colored("⚠️  WARNING: Uncommitted changes detected", 'RED')
            for change in git_status.get('changes', []):
                self.print_colored(f"   {change}", 'RED')
        else:
            self.print_colored("✅ Repository clean", 'GREEN')
        
        print()
        
        # Menu options based on current branch
        if self.current_branch == 'main':
            self.display_main_branch_menu()
        elif self.current_branch.startswith('hotfix/'):
            self.display_hotfix_branch_menu()
        elif self.current_branch == 'develop':
            self.display_develop_branch_menu()
        else:
            self.display_other_branch_menu()
    
    def display_main_branch_menu(self):
        """Menu for main branch (production)"""
        self.print_colored("🔒 MAIN BRANCH - PRODUCTION LOCKED", 'RED')
        self.print_colored("External users depend on this branch being stable!", 'RED')
        print()
        
        self.print_colored("Available Actions:", 'WHITE')
        self.print_colored("1. 🏥 Check Production Health", 'GREEN')
        self.print_colored("2. 🚨 Create Hotfix Branch (Critical Issues Only)", 'YELLOW')
        self.print_colored("3. 🔄 Emergency Rollback", 'RED')
        self.print_colored("4. 🌿 Switch to Develop Branch (Safe Development)", 'BLUE')
        self.print_colored("5. 📊 View Production Metrics", 'CYAN')
        self.print_colored("6. 📚 View External User Guide", 'PURPLE')
        self.print_colored("0. ❌ Exit", 'WHITE')
    
    def display_hotfix_branch_menu(self):
        """Menu for hotfix branch"""
        self.print_colored("🚨 HOTFIX BRANCH - CRITICAL FIXES", 'YELLOW')
        self.print_colored(f"Working on: {self.current_branch}", 'YELLOW')
        print()
        
        self.print_colored("Available Actions:", 'WHITE')
        self.print_colored("1. 🧪 Deploy to Hotfix Environment", 'YELLOW')
        self.print_colored("2. 🔍 Test Hotfix Environment", 'CYAN')
        self.print_colored("3. ✅ Merge to Main (After Testing)", 'GREEN')
        self.print_colored("4. 🚀 Deploy to Production", 'RED')
        self.print_colored("5. 🌿 Switch to Develop Branch", 'BLUE')
        self.print_colored("0. ❌ Exit", 'WHITE')
    
    def display_develop_branch_menu(self):
        """Menu for develop branch (safe development)"""
        self.print_colored("🔧 DEVELOP BRANCH - SAFE DEVELOPMENT", 'BLUE')
        self.print_colored("Safe to make changes - external users unaffected!", 'GREEN')
        print()
        
        self.print_colored("Available Actions:", 'WHITE')
        self.print_colored("1. 🔧 Deploy to Development Environment", 'BLUE')
        self.print_colored("2. 🔍 Test Development Environment", 'CYAN')
        self.print_colored("3. 🧪 Run Test Suite", 'GREEN')
        self.print_colored("4. 📊 Run Bloomberg Verification", 'PURPLE')
        self.print_colored("5. 🌿 Switch to Main Branch", 'YELLOW')
        self.print_colored("6. 📋 View Consolidation Tasks", 'CYAN')
        self.print_colored("7. 🏗️ Start Code Consolidation Work", 'GREEN')
        self.print_colored("0. ❌ Exit", 'WHITE')
    
    def display_other_branch_menu(self):
        """Menu for other branches"""
        self.print_colored(f"🌿 BRANCH: {self.current_branch}", 'WHITE')
        print()
        
        self.print_colored("Available Actions:", 'WHITE')
        self.print_colored("1. 🔧 Switch to Develop Branch", 'BLUE')
        self.print_colored("2. 🔒 Switch to Main Branch", 'YELLOW')
        self.print_colored("3. 🧪 Run Tests", 'GREEN')
        self.print_colored("0. ❌ Exit", 'WHITE')
    
    def handle_main_branch_actions(self, choice: str):
        """Handle actions for main branch"""
        if choice == '1':
            self.check_production_health()
        elif choice == '2':
            self.create_hotfix_branch()
        elif choice == '3':
            self.emergency_rollback()
        elif choice == '4':
            self.switch_branch('develop')
        elif choice == '5':
            self.view_production_metrics()
        elif choice == '6':
            self.view_external_user_guide()
    
    def handle_hotfix_branch_actions(self, choice: str):
        """Handle actions for hotfix branch"""
        if choice == '1':
            self.deploy_hotfix()
        elif choice == '2':
            self.test_hotfix_environment()
        elif choice == '3':
            self.merge_hotfix_to_main()
        elif choice == '4':
            self.deploy_production()
        elif choice == '5':
            self.switch_branch('develop')
    
    def handle_develop_branch_actions(self, choice: str):
        """Handle actions for develop branch"""
        if choice == '1':
            self.deploy_development()
        elif choice == '2':
            self.test_development_environment()
        elif choice == '3':
            self.run_test_suite()
        elif choice == '4':
            self.run_bloomberg_verification()
        elif choice == '5':
            self.switch_branch('main')
        elif choice == '6':
            self.view_consolidation_tasks()
        elif choice == '7':
            self.start_consolidation_work()
    
    def check_production_health(self):
        """Check production API health"""
        self.print_colored("🏥 Checking Production Health...", 'CYAN')
        
        prod_url = "https://future-footing-414610.uc.r.appspot.com"
        health = self.check_api_health(prod_url)
        
        if health['status'] == 'healthy':
            self.print_colored("✅ Production API is healthy!", 'GREEN')
            data = health.get('data', {})
            self.print_colored(f"   Service: {data.get('service', 'Unknown')}", 'WHITE')
            self.print_colored(f"   Version: {data.get('version', 'Unknown')}", 'WHITE')
            self.print_colored(f"   Status: {data.get('status', 'Unknown')}", 'WHITE')
        else:
            self.print_colored("❌ Production API health check failed!", 'RED')
            self.print_colored(f"   Error: {health.get('error', 'Unknown error')}", 'RED')
        
        input("\nPress Enter to continue...")
    
    def create_hotfix_branch(self):
        """Create a new hotfix branch"""
        self.print_colored("🚨 Creating Hotfix Branch", 'YELLOW')
        self.print_colored("WARNING: Only for critical production issues!", 'RED')
        
        issue_description = input("Enter hotfix description (e.g., 'bloomberg-calculation-fix'): ")
        if not issue_description:
            self.print_colored("❌ Hotfix description required", 'RED')
            input("Press Enter to continue...")
            return
        
        branch_name = f"hotfix/{issue_description}"
        
        try:
            subprocess.run(['git', 'checkout', '-b', branch_name], 
                         cwd=self.project_root, check=True)
            self.current_branch = branch_name
            self.print_colored(f"✅ Created and switched to {branch_name}", 'GREEN')
        except subprocess.CalledProcessError:
            self.print_colored("❌ Failed to create hotfix branch", 'RED')
        
        input("Press Enter to continue...")
    
    def emergency_rollback(self):
        """Emergency production rollback"""
        self.print_colored("🔄 EMERGENCY PRODUCTION ROLLBACK", 'RED')
        self.print_colored("WARNING: This affects external users!", 'RED')
        
        confirm = input("Type 'ROLLBACK' to confirm emergency rollback: ")
        if confirm != 'ROLLBACK':
            self.print_colored("❌ Rollback cancelled", 'GREEN')
            input("Press Enter to continue...")
            return
        
        target_version = input("Enter target version (e.g., 'v10.0.0'): ")
        if not target_version:
            self.print_colored("❌ Target version required", 'RED')
            input("Press Enter to continue...")
            return
        
        result = self.run_deployment_script(f"rollback_production.sh {target_version}")
        
        if result['success']:
            self.print_colored("✅ Rollback completed successfully!", 'GREEN')
        else:
            self.print_colored("❌ Rollback failed!", 'RED')
            self.print_colored(f"Error: {result.get('error', 'Unknown error')}", 'RED')
        
        input("Press Enter to continue...")
    
    def deploy_development(self):
        """Deploy to development environment"""
        self.print_colored("🔧 Deploying to Development Environment", 'BLUE')
        self.print_colored("Safe deployment - external users unaffected", 'GREEN')
        
        result = self.run_deployment_script("deploy_development.sh")
        
        if result['success']:
            self.print_colored("✅ Development deployment successful!", 'GREEN')
        else:
            self.print_colored("❌ Development deployment failed!", 'RED')
        
        input("Press Enter to continue...")
    
    def deploy_hotfix(self):
        """Deploy to hotfix environment"""
        self.print_colored("🧪 Deploying to Hotfix Environment", 'YELLOW')
        
        result = self.run_deployment_script("deploy_hotfix.sh")
        
        if result['success']:
            self.print_colored("✅ Hotfix deployment successful!", 'GREEN')
        else:
            self.print_colored("❌ Hotfix deployment failed!", 'RED')
        
        input("Press Enter to continue...")
    
    def deploy_production(self):
        """Deploy to production (dangerous)"""
        self.print_colored("🚀 PRODUCTION DEPLOYMENT", 'RED')
        self.print_colored("WARNING: This affects external users!", 'RED')
        
        confirm = input("Type 'DEPLOY' to confirm production deployment: ")
        if confirm != 'DEPLOY':
            self.print_colored("❌ Production deployment cancelled", 'GREEN')
            input("Press Enter to continue...")
            return
        
        result = self.run_deployment_script("deploy_production.sh")
        
        if result['success']:
            self.print_colored("✅ Production deployment successful!", 'GREEN')
        else:
            self.print_colored("❌ Production deployment failed!", 'RED')
        
        input("Press Enter to continue...")
    
    def switch_branch(self, target_branch: str):
        """Switch git branch"""
        try:
            subprocess.run(['git', 'checkout', target_branch], 
                         cwd=self.project_root, check=True)
            self.current_branch = target_branch
            self.print_colored(f"✅ Switched to {target_branch} branch", 'GREEN')
        except subprocess.CalledProcessError:
            self.print_colored(f"❌ Failed to switch to {target_branch}", 'RED')
        
        input("Press Enter to continue...")
    
    def run_test_suite(self):
        """Run comprehensive test suite"""
        self.print_colored("🧪 Running Test Suite", 'GREEN')
        
        tests = [
            ("test_25_bonds_complete.py", "25-Bond Test Suite"),
            ("bloomberg_verification_framework.py", "Bloomberg Verification"),
        ]
        
        for test_file, test_name in tests:
            test_path = os.path.join(self.project_root, test_file)
            if os.path.exists(test_path):
                self.print_colored(f"Running {test_name}...", 'CYAN')
                try:
                    result = subprocess.run(['python3', test_file], 
                                          cwd=self.project_root, 
                                          capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        self.print_colored(f"✅ {test_name} passed", 'GREEN')
                    else:
                        self.print_colored(f"❌ {test_name} failed", 'RED')
                        print(result.stderr)
                except subprocess.TimeoutExpired:
                    self.print_colored(f"⏰ {test_name} timed out", 'YELLOW')
                except Exception as e:
                    self.print_colored(f"❌ {test_name} error: {e}", 'RED')
            else:
                self.print_colored(f"⚠️ {test_file} not found", 'YELLOW')
        
        input("Press Enter to continue...")
    
    def view_consolidation_tasks(self):
        """View current consolidation tasks"""
        self.print_colored("📋 Code Consolidation Tasks", 'CYAN')
        
        tasks_file = os.path.join(self.project_root, "_tasks.md")
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                content = f.read()
            
            # Show first part of tasks file
            lines = content.split('\n')
            for i, line in enumerate(lines[:50]):  # Show first 50 lines
                print(line)
            
            if len(lines) > 50:
                self.print_colored(f"\n... {len(lines) - 50} more lines ...", 'YELLOW')
        else:
            self.print_colored("❌ Tasks file not found", 'RED')
        
        input("\nPress Enter to continue...")
    
    def start_consolidation_work(self):
        """Start code consolidation work"""
        self.print_colored("🏗️ Code Consolidation Work", 'GREEN')
        
        self.print_colored("Available Consolidation Tasks:", 'WHITE')
        self.print_colored("1. 📁 API File Consolidation (TASK-001)", 'BLUE')
        self.print_colored("2. 🔧 Bond Calculation Unification (TASK-002)", 'BLUE')
        self.print_colored("3. 🧪 Test Suite Consolidation (TASK-003)", 'BLUE')
        self.print_colored("4. 🗄️ Database Connection Standardization (TASK-004)", 'BLUE')
        self.print_colored("5. 📊 Portfolio Processing Consolidation (TASK-005)", 'BLUE')
        self.print_colored("6. 🧹 File Cleanup (TASK-006)", 'BLUE')
        
        choice = input("\nSelect task to work on (1-6): ")
        
        task_guides = {
            '1': "Start with google_analysis10_api*.py files - consolidate into single API with environment detection",
            '2': "Focus on bond_master_hierarchy_enhanced.py as single source of truth for calculations", 
            '3': "Create test_treasury_comprehensive.py to replace 26+ individual test files",
            '4': "Create DatabaseConnectionManager class to replace 56+ duplicate connection patterns",
            '5': "Unify portfolio calculation functions into PortfolioAnalyticsEngine",
            '6': "Archive backup files and clean up repository structure"
        }
        
        if choice in task_guides:
            self.print_colored(f"📋 Task {choice} Guide:", 'CYAN')
            self.print_colored(task_guides[choice], 'WHITE')
            self.print_colored("\n✅ Work in develop branch - external users unaffected!", 'GREEN')
            self.print_colored("💡 Use ./deploy_development.sh to test changes", 'BLUE')
        else:
            self.print_colored("❌ Invalid task selection", 'RED')
        
        input("\nPress Enter to continue...")
    
    def view_external_user_guide(self):
        """View external user guide"""
        guide_file = os.path.join(self.project_root, "EXTERNAL_USER_GUIDE.md")
        if os.path.exists(guide_file):
            self.print_colored("📚 Opening External User Guide...", 'CYAN')
            subprocess.run(['open', guide_file])  # macOS
        else:
            self.print_colored("❌ External User Guide not found", 'RED')
        
        input("Press Enter to continue...")
    
    def run(self):
        """Main application loop"""
        while True:
            self.current_branch = self.get_current_branch()  # Refresh branch info
            self.display_main_menu()
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '0':
                self.print_colored("👋 Goodbye!", 'GREEN')
                break
            
            # Route to appropriate handler based on current branch
            if self.current_branch == 'main':
                self.handle_main_branch_actions(choice)
            elif self.current_branch.startswith('hotfix/'):
                self.handle_hotfix_branch_actions(choice)
            elif self.current_branch == 'develop':
                self.handle_develop_branch_actions(choice)
            else:
                if choice == '1':
                    self.switch_branch('develop')
                elif choice == '2':
                    self.switch_branch('main')
                elif choice == '3':
                    self.run_test_suite()

def main():
    """Main entry point"""
    agent = XTrillionDeploymentAgent()
    
    # Check if we're in the right directory
    if not os.path.exists(agent.project_root):
        print(f"❌ Project directory not found: {agent.project_root}")
        sys.exit(1)
    
    agent.run()

if __name__ == "__main__":
    main()
