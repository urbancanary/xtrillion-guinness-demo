#!/usr/bin/env python3
"""
🎯 Claude Code Deployment Agent Menu System
Safe deployment management for google_analysis10 production system

This menu system provides safe deployment management with:
- Production protection (external users protected)
- Development freedom (safe consolidation work)
- Emergency hotfix capability (critical bug fixes)
- Automated rollback (disaster recovery)
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class ClaudeCodeDeploymentAgent:
    def __init__(self):
        self.project_root = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
        self.current_branch = self.get_current_branch()
        self.deployment_log = os.path.join(self.project_root, "deployment.log")
        
    def get_current_branch(self):
        """Get current git branch"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"], 
                cwd=self.project_root,
                capture_output=True, 
                text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def log_action(self, action, status="INFO"):
        """Log deployment actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {status}: {action}\n"
        
        try:
            with open(self.deployment_log, "a") as f:
                f.write(log_entry)
        except:
            pass
        
        print(f"🔍 {log_entry.strip()}")
    
    def run_command(self, command, description="Command"):
        """Safely run shell command with logging"""
        self.log_action(f"Running: {description}")
        self.log_action(f"Command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.log_action(f"✅ {description} completed successfully", "SUCCESS")
                if result.stdout:
                    print(f"📄 Output: {result.stdout[:200]}...")
                return True
            else:
                self.log_action(f"❌ {description} failed: {result.stderr}", "ERROR")
                print(f"💥 Error: {result.stderr[:200]}...")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_action(f"⏰ {description} timed out", "ERROR")
            return False
        except Exception as e:
            self.log_action(f"💥 {description} exception: {str(e)}", "ERROR")
            return False
    
    def show_status(self):
        """Show current system status"""
        print(f"\n📊 Current Status:")
        print(f"   🌿 Branch: {self.current_branch}")
        print(f"   📂 Project: {self.project_root}")
        print(f"   📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check API health
        try:
            import requests
            response = requests.get("https://future-footing-414610.uc.r.appspot.com/health", timeout=5)
            if response.status_code == 200:
                print(f"   🟢 Production API: Healthy")
            else:
                print(f"   🟡 Production API: Status {response.status_code}")
        except:
            print(f"   🔴 Production API: Unreachable")
    
    def simple_menu(self):
        """Simple text-based menu (no external dependencies)"""
        while True:
            self.show_status()
            
            print(f"\n🎯 Claude Code Deployment Agent Menu")
            print(f"1. 🚀 Development Deployment (Safe)")
            print(f"2. 🚨 Hotfix Deployment (Critical Bugs)")  
            print(f"3. 🔒 Production Deployment (External Users)")
            print(f"4. ⏪ Emergency Rollback")
            print(f"5. 🌿 Branch Management")
            print(f"6. 📊 System Health Check")
            print(f"7. 📋 View Deployment Log")
            print(f"8. ❌ Exit")
            
            try:
                choice = input("\nSelect option (1-8): ").strip()
                
                if choice == "1":
                    self.development_deployment()
                elif choice == "2":
                    self.hotfix_deployment()
                elif choice == "3":
                    self.production_deployment()
                elif choice == "4":
                    self.emergency_rollback()
                elif choice == "5":
                    self.branch_management()
                elif choice == "6":
                    self.system_health_check()
                elif choice == "7":
                    self.view_deployment_log()
                elif choice == "8":
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-8.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
    
    def development_deployment(self):
        """Safe development deployment"""
        print("\n🚀 Development Deployment - Safe for Consolidation Work")
        print("   This deploys to development environment only")
        print("   External users are NOT affected")
        
        if self.current_branch != "develop":
            print(f"\n⚠️  Current branch: {self.current_branch}")
            switch = input("Switch to develop branch? (y/N): ").lower().startswith('y')
            if switch:
                if not self.run_command("git checkout develop", "Switch to develop branch"):
                    return
                self.current_branch = "develop"
            else:
                print("❌ Development deployment requires develop branch")
                return
        
        print("\n📋 Development Deployment Plan:")
        print("   ✅ Deploy to development environment")
        print("   ✅ Test API endpoints safely")
        print("   ✅ No impact on external users")
        print("   ✅ Safe for code consolidation")
        
        confirm = input("Proceed with development deployment? (y/N): ").lower().startswith('y')
        if confirm:
            self.log_action("Starting development deployment", "INFO")
            
            if self.run_command("./deploy_development.sh", "Development deployment"):
                print("\n🎉 Development deployment successful!")
                print("   🔗 Development URL: https://dev-analytics.future-footing-414610.uc.r.appspot.com")
                print("   🧪 Test your changes safely")
            else:
                print("\n💥 Development deployment failed!")
    
    def hotfix_deployment(self):
        """Critical hotfix deployment"""
        print("\n🚨 Hotfix Deployment - Critical Bug Fixes Only")
        print("   This creates a hotfix branch and deploys critical fixes")
        
        hotfix_name = input("Hotfix name (e.g., 'critical-api-bug'): ").strip()
        if not hotfix_name:
            return
        
        hotfix_branch = f"hotfix/{hotfix_name}"
        
        print(f"\n📋 Hotfix Deployment Plan:")
        print(f"   🌿 Create branch: {hotfix_branch}")
        print(f"   🔧 Apply critical fixes")
        print(f"   🧪 Test in hotfix environment") 
        print(f"   🚀 Deploy to production (if confirmed)")
        
        confirm = input("Create hotfix branch and deploy? (y/N): ").lower().startswith('y')
        if confirm:
            self.log_action(f"Starting hotfix deployment: {hotfix_name}", "HOTFIX")
            
            if self.run_command(f"git checkout main", "Switch to main"):
                if self.run_command(f"git checkout -b {hotfix_branch}", "Create hotfix branch"):
                    
                    print(f"\n🌿 Hotfix branch {hotfix_branch} created")
                    print("   🔧 Make your critical fixes now")
                    print("   🧪 Test thoroughly")
                    
                    ready = input("Ready to deploy hotfix? (y/N): ").lower().startswith('y')
                    if ready:
                        if self.run_command("./deploy_hotfix.sh", "Hotfix deployment"):
                            print("\n🎉 Hotfix deployed to staging!")
                            
                            production_deploy = input(
                                "Deploy hotfix to PRODUCTION? (External users affected) (y/N): "
                            ).lower().startswith('y')
                            
                            if production_deploy:
                                if self.run_command("./deploy_production.sh", "Production hotfix"):
                                    print("\n🚀 Hotfix deployed to production!")
                                    # Merge back to main and develop
                                    self.run_command("git checkout main && git merge " + hotfix_branch, "Merge to main")
                                    self.run_command("git checkout develop && git merge main", "Merge to develop")
    
    def production_deployment(self):
        """Protected production deployment"""
        print("\n🔒 Production Deployment - External Users Affected")
        print("   ⚠️  This affects live users!")
        print("   ⚠️  Only deploy tested, stable code!")
        
        if self.current_branch == "develop":
            print("\n📋 Production Deployment from develop branch:")
            print("   1. Merge develop → main")
            print("   2. Deploy main to production") 
            print("   3. External users get updates")
            
            confirm1 = input("Are you SURE you want to deploy to production? (y/N): ").lower().startswith('y')
            if not confirm1:
                return
                
            confirm2 = input("This will affect external users. Continue? (y/N): ").lower().startswith('y')
            if not confirm2:
                return
            
            self.log_action("Starting production deployment from develop", "PRODUCTION")
            
            if self.run_command("git checkout main", "Switch to main"):
                if self.run_command("git merge develop", "Merge develop to main"):
                    if self.run_command("./deploy_production.sh", "Production deployment"):
                        print("\n🚀 Production deployment successful!")
                        print("   🌐 Live URL: https://future-footing-414610.uc.r.appspot.com")
                        print("   👥 External users now have updates")
                    else:
                        print("\n💥 Production deployment failed!")
                        rollback = input("Emergency rollback? (Y/n): ").lower() != 'n'
                        if rollback:
                            self.run_command("./rollback_production.sh", "Emergency rollback")
        
        elif self.current_branch == "main":
            print("\n📋 Direct production deployment from main:")
            print("   ⚠️  Deploying current main branch")
            
            confirm = input("Deploy current main to production? (y/N): ").lower().startswith('y')
            if confirm:
                self.log_action("Starting production deployment from main", "PRODUCTION")
                if self.run_command("./deploy_production.sh", "Production deployment"):
                    print("\n🚀 Production deployment successful!")
                else:
                    print("\n💥 Production deployment failed!")
        else:
            print(f"\n❌ Cannot deploy from branch: {self.current_branch}")
            print("   Switch to 'main' or 'develop' first")
    
    def emergency_rollback(self):
        """Emergency rollback"""
        print("\n⏪ Emergency Rollback - Disaster Recovery")
        print("   This rolls back production to last known good state")
        
        confirm1 = input("Is this a PRODUCTION EMERGENCY? (y/N): ").lower().startswith('y')
        if not confirm1:
            return
            
        confirm2 = input("Rollback will affect external users. Continue? (y/N): ").lower().startswith('y')
        if not confirm2:
            return
            
        confirm3 = input("FINAL CONFIRMATION: Execute emergency rollback? (y/N): ").lower().startswith('y')
        if not confirm3:
            return
        
        self.log_action("EMERGENCY ROLLBACK INITIATED", "EMERGENCY")
        print("\n🚨 Executing emergency rollback...")
        
        if self.run_command("./rollback_production.sh", "Emergency rollback"):
            print("\n✅ Emergency rollback completed!")
            print("   🔄 Production restored to previous version")
            print("   📞 Notify stakeholders of rollback")
        else:
            print("\n💥 Emergency rollback FAILED!")
            print("   📞 Contact infrastructure team immediately")
    
    def branch_management(self):
        """Branch management"""
        print(f"\n🌿 Branch Management - Current: {self.current_branch}")
        print("1. Switch to develop (Safe development)")
        print("2. Switch to main (Production branch)")
        print("3. Create new feature branch")
        print("4. View all branches")
        print("5. Initialize git strategy")
        print("6. Back to main menu")
        
        choice = input("Select option (1-6): ").strip()
        
        if choice == "1":
            self.run_command("git checkout develop", "Switch to develop")
            self.current_branch = "develop"
        elif choice == "2":
            self.run_command("git checkout main", "Switch to main")
            self.current_branch = "main"
        elif choice == "3":
            feature_name = input("Feature branch name: ").strip()
            if feature_name:
                self.run_command(f"git checkout develop", "Switch to develop")
                self.run_command(f"git checkout -b feature/{feature_name}", "Create feature branch")
                self.current_branch = f"feature/{feature_name}"
        elif choice == "4":
            self.run_command("git branch -a", "View all branches")
        elif choice == "5":
            self.run_command("./setup_git_branching.sh", "Initialize git strategy")
    
    def system_health_check(self):
        """System health check"""
        print("\n📊 System Health Check")
        
        # Check API endpoints
        endpoints = [
            ("Production", "https://future-footing-414610.uc.r.appspot.com/health"),
        ]
        
        for name, url in endpoints:
            try:
                import requests
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   🟢 {name} API: Healthy")
                else:
                    print(f"   🟡 {name} API: Status {response.status_code}")
            except:
                print(f"   🔴 {name} API: Unreachable")
        
        # Check database files
        db_files = ["bonds_data.db", "bloomberg_index.db", "validated_quantlib_bonds.db"]
        for db_file in db_files:
            db_path = os.path.join(self.project_root, db_file)
            if os.path.exists(db_path):
                size_mb = os.path.getsize(db_path) / (1024 * 1024)
                print(f"   📊 {db_file}: {size_mb:.1f} MB")
            else:
                print(f"   ❌ {db_file}: Missing")
        
        # Check deployment scripts
        scripts = ["deploy_production.sh", "deploy_development.sh", "rollback_production.sh"]
        for script in scripts:
            script_path = os.path.join(self.project_root, script)
            if os.path.exists(script_path) and os.access(script_path, os.X_OK):
                print(f"   ✅ {script}: Ready")
            else:
                print(f"   ❌ {script}: Missing or not executable")
    
    def view_deployment_log(self):
        """View deployment log"""
        print("\n📋 Recent Deployment Log")
        
        try:
            with open(self.deployment_log, "r") as f:
                lines = f.readlines()
                for line in lines[-20:]:
                    print(f"   {line.strip()}")
        except FileNotFoundError:
            print("   📄 No deployment log found")
        except Exception as e:
            print(f"   ❌ Error reading log: {e}")

def main():
    """Main entry point"""
    print("🎯 Claude Code Deployment Agent")
    print("   Safe deployment management for google_analysis10")
    print("   Production system with external user protection")
    
    agent = ClaudeCodeDeploymentAgent()
    
    # Check if in correct directory
    if not os.path.exists(os.path.join(agent.project_root, "google_analysis10.py")):
        print("\n❌ Not in google_analysis10 project directory")
        print(f"   Expected: {agent.project_root}")
        print(f"   Current: {os.getcwd()}")
        sys.exit(1)
    
    try:
        agent.simple_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Deployment agent stopped")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        agent.log_action(f"Agent crashed: {e}", "ERROR")

if __name__ == "__main__":
    main()
