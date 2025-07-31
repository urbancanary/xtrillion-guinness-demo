#!/usr/bin/env python3
"""
Orphaned Code Detection Agent
=============================

Automated agent for identifying orphaned, unused, or obsolete code files
that should be archived or removed to reduce codebase confusion.

Usage:
    python3 orphaned_code_agent.py --scan          # Scan for orphaned code
    python3 orphaned_code_agent.py --quick         # Quick scan for obvious orphans
    python3 orphaned_code_agent.py --update-tasks  # Add archival tasks to _tasks.md
    python3 orphaned_code_agent.py --vultr         # Use Vultr for enhanced analysis
"""

import os
import sys
import re
import ast
import argparse
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import subprocess

class OrphanedCodeAgent:
    """
    Automated detection of orphaned, unused, and obsolete code files
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.orphaned_files = []
        self.archival_tasks = []
        
        # File patterns that suggest obsolescence
        self.obsolete_patterns = {
            'version_suffixes': [r'_v\d+', r'_version\d+', r'_\d{6,8}'],
            'backup_indicators': [r'_backup', r'_bak', r'_old', r'_original', r'\.backup'],
            'development_indicators': [r'_test\d+', r'_temp', r'_tmp', r'_working', r'_draft'],
            'status_indicators': [r'_broken', r'_fixed', r'_debug', r'_experimental'],
            'archive_indicators': [r'archive/', r'old/', r'deprecated/', r'unused/']
        }
        
        # Core files that should never be considered orphaned
        self.core_files = {
            'google_analysis10_api.py',    # Main API
            'bond_master_hierarchy_enhanced.py',  # Core calculations
            'google_analysis10.py',        # Portfolio processing
            'requirements.txt',
            'app.yaml',
            'README.md',
            'CLAUDE.md',
            '_tasks.md'
        }
        
        # Directories to analyze
        self.code_extensions = {'.py', '.js', '.ts', '.sh', '.yaml', '.yml', '.json'}
        self.ignore_dirs = {'__pycache__', '.git', '.pytest_cache', 'node_modules', '.venv', 'venv'}
    
    def log(self, message: str, level: str = "INFO"):
        """Structured logging with timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def get_all_project_files(self) -> List[str]:
        """Get all project files for analysis"""
        project_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in self.code_extensions):
                    full_path = os.path.join(root, file)
                    project_files.append(full_path)
        
        return project_files
    
    def analyze_import_dependencies(self, project_files: List[str]) -> Dict[str, Set[str]]:
        """Analyze which files import which other files"""
        dependencies = defaultdict(set)
        imported_files = set()
        
        for file_path in project_files:
            if not file_path.endswith('.py'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find import statements
                import_patterns = [
                    r'from\s+(\w+(?:\.\w+)*)\s+import',  # from module import
                    r'import\s+(\w+(?:\.\w+)*)',         # import module
                ]
                
                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Convert module name to potential file path
                        potential_file = match.replace('.', '/') + '.py'
                        
                        # Check if this file exists in our project
                        for project_file in project_files:
                            if project_file.endswith(potential_file):
                                dependencies[file_path].add(project_file)
                                imported_files.add(project_file)
                                break
                        
                        # Also check for direct filename matches
                        module_file = match + '.py'
                        for project_file in project_files:
                            if os.path.basename(project_file) == module_file:
                                dependencies[file_path].add(project_file)
                                imported_files.add(project_file)
                                break
            
            except Exception as e:
                self.log(f"Error analyzing imports in {file_path}: {e}", "WARNING")
        
        return dependencies, imported_files
    
    def detect_obsolete_naming_patterns(self, project_files: List[str]) -> List[Dict]:
        """Detect files with naming patterns suggesting they're obsolete"""
        obsolete_files = []
        
        for file_path in project_files:
            filename = os.path.basename(file_path)
            
            # Skip core files
            if filename in self.core_files:
                continue
            
            obsolete_score = 0
            matched_patterns = []
            
            # Check against obsolete patterns
            for category, patterns in self.obsolete_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, file_path.lower()):
                        obsolete_score += 1
                        matched_patterns.append(f"{category}: {pattern}")
            
            # Additional scoring factors
            file_stat = os.stat(file_path)
            last_modified = datetime.fromtimestamp(file_stat.st_mtime)
            days_since_modified = (datetime.now() - last_modified).days
            
            if days_since_modified > 90:  # Not modified in 3 months
                obsolete_score += 1
                matched_patterns.append(f"stale: {days_since_modified} days old")
            
            if obsolete_score > 0:
                obsolete_files.append({
                    'file_path': file_path,
                    'filename': filename,
                    'obsolete_score': obsolete_score,
                    'matched_patterns': matched_patterns,
                    'last_modified': last_modified.isoformat(),
                    'days_old': days_since_modified,
                    'size_kb': round(file_stat.st_size / 1024, 2)
                })
        
        # Sort by obsolete score (highest first)
        obsolete_files.sort(key=lambda x: x['obsolete_score'], reverse=True)
        return obsolete_files
    
    def detect_unused_files(self, project_files: List[str], dependencies: Dict, imported_files: Set[str]) -> List[Dict]:
        """Detect files that are never imported or referenced"""
        unused_files = []
        
        for file_path in project_files:
            filename = os.path.basename(file_path)
            
            # Skip core files and non-Python files for import analysis
            if filename in self.core_files or not file_path.endswith('.py'):
                continue
            
            # Check if file is imported by any other file
            is_imported = file_path in imported_files
            
            # Check if file is an executable script (has if __name__ == "__main__")
            is_executable = self._is_executable_script(file_path)
            
            # Check if file is in test directory or is a test file
            is_test_file = ('test' in file_path.lower() or 
                          filename.startswith('test_') or 
                          filename.endswith('_test.py'))
            
            # If not imported, not executable, and not a test, it might be unused
            if not is_imported and not is_executable and not is_test_file:
                file_stat = os.stat(file_path)
                last_modified = datetime.fromtimestamp(file_stat.st_mtime)
                
                unused_files.append({
                    'file_path': file_path,
                    'filename': filename,
                    'last_modified': last_modified.isoformat(),
                    'days_old': (datetime.now() - last_modified).days,
                    'size_kb': round(file_stat.st_size / 1024, 2),
                    'reason': 'Not imported, not executable, not test file'
                })
        
        return unused_files
    
    def _is_executable_script(self, file_path: str) -> bool:
        """Check if file is an executable script"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for if __name__ == "__main__" pattern
            return 'if __name__ == "__main__"' in content or content.startswith('#!/')
        
        except Exception:
            return False
    
    def detect_duplicate_functionality(self, project_files: List[str]) -> List[Dict]:
        """Detect files that might have duplicate functionality"""
        # Group files by similar base names
        name_groups = defaultdict(list)
        
        for file_path in project_files:
            filename = os.path.basename(file_path)
            # Remove version suffixes, extensions, and common suffixes
            base_name = re.sub(r'(_v?\d+|_backup|_old|_new|_fixed|_working|_test\d*|\.py)$', '', filename.lower())
            base_name = re.sub(r'_\d{6,8}', '', base_name)  # Remove dates
            
            if base_name:
                name_groups[base_name].append(file_path)
        
        # Find groups with multiple files that might be duplicates
        potential_duplicates = []
        for base_name, files in name_groups.items():
            if len(files) > 1:
                potential_duplicates.append({
                    'base_name': base_name,
                    'files': files,
                    'count': len(files),
                    'total_size_kb': sum(os.path.getsize(f) / 1024 for f in files if os.path.exists(f))
                })
        
        # Sort by count (most duplicates first)
        potential_duplicates.sort(key=lambda x: x['count'], reverse=True)
        return potential_duplicates
    
    def use_vultr_analysis(self, project_files: List[str]) -> Dict:
        """Use Vultr for enhanced code analysis (placeholder for future integration)"""
        # Placeholder for Vultr integration
        # This would use Vultr's compute resources for more intensive analysis
        self.log("🌥️  Vultr integration not implemented yet", "INFO")
        
        return {
            'vultr_analysis': False,
            'message': 'Vultr integration planned for enhanced analysis of large codebases'
        }
    
    def generate_archival_tasks(self, obsolete_files: List[Dict], unused_files: List[Dict], 
                               duplicate_groups: List[Dict]) -> List[Dict]:
        """Generate structured archival tasks for _tasks.md"""
        tasks = []
        task_id = 1
        
        # High-priority obsolete files (score > 2)
        high_priority_obsolete = [f for f in obsolete_files if f['obsolete_score'] > 2]
        if high_priority_obsolete:
            file_list = [f['file_path'] for f in high_priority_obsolete[:10]]  # Limit to top 10
            tasks.append({
                'id': f"ORPHAN-{task_id:03d}",
                'title': f"Archive {len(high_priority_obsolete)} highly obsolete files",
                'priority': 'HIGH',
                'type': 'code_archival',
                'description': f"Files with multiple obsolete indicators: backup suffixes, version numbers, old timestamps",
                'files': file_list,
                'suggested_approach': 'Move to archive/obsolete_files/ directory',
                'impact': f'Reduces codebase confusion and improves navigation'
            })
            task_id += 1
        
        # Large duplicate groups
        large_duplicate_groups = [g for g in duplicate_groups if g['count'] > 3]
        for group in large_duplicate_groups[:3]:  # Top 3 groups
            tasks.append({
                'id': f"ORPHAN-{task_id:03d}",
                'title': f"Consolidate {group['count']} files with '{group['base_name']}' pattern",
                'priority': 'MEDIUM',
                'type': 'file_consolidation',
                'description': f"Multiple files doing similar work: {', '.join([os.path.basename(f) for f in group['files'][:3]])}...",
                'files': group['files'],
                'suggested_approach': 'Keep most recent version, archive others',
                'impact': f"Saves {group['total_size_kb']:.1f}KB and reduces naming confusion"
            })
            task_id += 1
        
        # Old unused files
        old_unused = [f for f in unused_files if f['days_old'] > 60]
        if old_unused:
            file_list = [f['file_path'] for f in old_unused[:15]]  # Limit to 15
            tasks.append({
                'id': f"ORPHAN-{task_id:03d}",
                'title': f"Archive {len(old_unused)} unused files older than 60 days",
                'priority': 'LOW',
                'type': 'unused_code_cleanup',
                'description': 'Files not imported anywhere and not modified recently',
                'files': file_list,
                'suggested_approach': 'Move to archive/unused/ directory after verification',
                'impact': 'Reduces codebase clutter and improves maintainability'
            })
            task_id += 1
        
        return tasks
    
    def update_tasks_file(self, tasks: List[Dict]):
        """Update _tasks.md file with generated archival tasks"""
        tasks_file = os.path.join(self.project_root, '_tasks.md')
        
        # Read existing content
        existing_content = ""
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                existing_content = f.read()
        
        # Generate new section
        new_section = f"""
## Orphaned Code Cleanup Tasks (Generated {datetime.now().strftime('%Y-%m-%d')})

"""
        
        for task in tasks:
            new_section += f"""### {task['id']}: {task['title']} [{task['priority']}]
**Type**: {task['type']}
**Description**: {task['description']}
**Suggested Approach**: {task['suggested_approach']}
**Impact**: {task['impact']}

"""
            if 'files' in task and len(task['files']) <= 10:
                new_section += f"**Files to archive**:\n"
                for file_path in task['files']:
                    new_section += f"- `{file_path}`\n"
                new_section += "\n"
            elif 'files' in task:
                new_section += f"**Files to archive**: {len(task['files'])} files (see detailed scan results)\n\n"
        
        # Append to existing content
        with open(tasks_file, 'w') as f:
            f.write(existing_content)
            if existing_content and not existing_content.endswith('\n'):
                f.write('\n')
            f.write("---\n")
            f.write(new_section)
        
        self.log(f"📝 Updated {tasks_file} with {len(tasks)} archival tasks")
    
    def scan_for_orphaned_code(self, use_vultr: bool = False) -> Dict:
        """Run comprehensive orphaned code scan"""
        self.log("🔍 Starting orphaned code detection scan...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'files_scanned': 0,
            'obsolete_files': [],
            'unused_files': [],
            'duplicate_groups': [],
            'vultr_analysis': {},
            'summary': {}
        }
        
        # Get all project files
        project_files = self.get_all_project_files()
        results['files_scanned'] = len(project_files)
        self.log(f"📁 Found {len(project_files)} project files to analyze")
        
        # Analyze import dependencies
        self.log("🔗 Analyzing import dependencies...")
        dependencies, imported_files = self.analyze_import_dependencies(project_files)
        self.log(f"📊 Found {len(imported_files)} files that are imported by others")
        
        # Detect obsolete naming patterns
        self.log("🔍 Detecting obsolete naming patterns...")
        obsolete_files = self.detect_obsolete_naming_patterns(project_files)
        results['obsolete_files'] = obsolete_files
        self.log(f"📊 Found {len(obsolete_files)} files with obsolete patterns")
        
        # Detect unused files
        self.log("🔍 Detecting unused files...")
        unused_files = self.detect_unused_files(project_files, dependencies, imported_files)
        results['unused_files'] = unused_files
        self.log(f"📊 Found {len(unused_files)} potentially unused files")
        
        # Detect duplicate functionality
        self.log("🔍 Detecting duplicate functionality...")
        duplicate_groups = self.detect_duplicate_functionality(project_files)
        results['duplicate_groups'] = duplicate_groups
        self.log(f"📊 Found {len(duplicate_groups)} groups of potentially duplicate files")
        
        # Use Vultr for enhanced analysis if requested
        if use_vultr:
            self.log("🌥️  Running Vultr-enhanced analysis...")
            results['vultr_analysis'] = self.use_vultr_analysis(project_files)
        
        # Generate summary
        results['summary'] = {
            'total_obsolete': len(obsolete_files),
            'total_unused': len(unused_files),
            'total_duplicate_groups': len(duplicate_groups),
            'high_priority_obsolete': len([f for f in obsolete_files if f['obsolete_score'] > 2]),
            'old_unused': len([f for f in unused_files if f['days_old'] > 60])
        }
        
        total_issues = results['summary']['total_obsolete'] + results['summary']['total_unused']
        self.log(f"📊 Scan complete: {total_issues} orphaned code issues found")
        
        return results

def main():
    parser = argparse.ArgumentParser(description="Orphaned Code Detection Agent")
    parser.add_argument('--scan', action='store_true', help='Run full orphaned code scan')
    parser.add_argument('--quick', action='store_true', help='Run quick scan for obvious orphans')
    parser.add_argument('--update-tasks', action='store_true', help='Update _tasks.md with archival tasks')
    parser.add_argument('--vultr', action='store_true', help='Use Vultr for enhanced analysis')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    
    args = parser.parse_args()
    
    # Create agent
    agent = OrphanedCodeAgent(args.project_root)
    
    if args.quick:
        agent.log("🚀 Running quick orphaned code scan...")
        print("Quick scan not implemented yet - use --scan for full analysis")
        return
    
    if args.scan or args.update_tasks:
        # Run full scan
        results = agent.scan_for_orphaned_code(use_vultr=args.vultr)
        
        # Generate archival tasks
        tasks = agent.generate_archival_tasks(
            results['obsolete_files'],
            results['unused_files'], 
            results['duplicate_groups']
        )
        
        # Print summary
        print(f"\n📊 Orphaned Code Detection Summary:")
        print(f"   Files scanned: {results['files_scanned']}")
        print(f"   Obsolete files: {results['summary']['total_obsolete']}")
        print(f"   Unused files: {results['summary']['total_unused']}")
        print(f"   Duplicate groups: {results['summary']['total_duplicate_groups']}")
        print(f"   Archival tasks generated: {len(tasks)}")
        
        if args.update_tasks:
            agent.update_tasks_file(tasks)
        else:
            print(f"\n💡 Run with --update-tasks to add {len(tasks)} archival tasks to _tasks.md")

if __name__ == "__main__":
    main()