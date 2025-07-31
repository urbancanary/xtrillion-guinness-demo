#!/usr/bin/env python3
"""
Code Duplication Detection Agent
================================

Automated agent for identifying code duplication patterns and creating
structured tasks for systematic consolidation.

Usage:
    python3 code_duplication_agent.py --scan          # Full duplication scan
    python3 code_duplication_agent.py --quick         # Quick scan for critical issues
    python3 code_duplication_agent.py --update-tasks  # Update _tasks.md with findings
"""

import os
import sys
import re
import hashlib
import argparse
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
from collections import defaultdict, Counter
import difflib

class CodeDuplicationAgent:
    """
    Automated code duplication detection and task generation
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.duplications_found = []
        self.tasks_generated = []
        
        # File patterns to analyze
        self.code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h'}
        self.ignore_patterns = {
            '__pycache__', '.git', '.pytest_cache', 'node_modules', 
            '.venv', 'venv', '.env', 'dist', 'build'
        }
        
        # Duplication detection patterns
        self.function_patterns = [
            r'def\s+(\w+)\s*\(',  # Python functions
            r'function\s+(\w+)\s*\(',  # JavaScript functions
            r'class\s+(\w+)\s*[:\(]',  # Class definitions
        ]
        
        # Bond-specific patterns to focus on
        self.domain_patterns = {
            'bond_calculation': [
                r'calculate_bond', r'bond_calc', r'yield.*calc', r'duration.*calc',
                r'price.*calc', r'accrued.*calc', r'convexity.*calc'
            ],
            'portfolio_processing': [
                r'process.*portfolio', r'portfolio.*process', r'analyze.*portfolio',
                r'aggregate.*portfolio', r'portfolio.*calc'
            ],
            'database_operations': [
                r'sqlite3\.connect', r'\.execute\(', r'cursor\(\)', r'\.fetchall\(\)',
                r'bond.*db', r'database.*manager'
            ],
            'api_endpoints': [
                r'@app\.route', r'\.post\(', r'\.get\(', r'flask.*app',
                r'jsonify\(', r'request\.json'
            ]
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Structured logging with timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def get_all_code_files(self) -> List[str]:
        """Get all code files in the project"""
        code_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.ignore_patterns)]
            
            for file in files:
                if any(file.endswith(ext) for ext in self.code_extensions):
                    code_files.append(os.path.join(root, file))
        
        return code_files
    
    def extract_functions(self, file_path: str) -> List[Dict]:
        """Extract function definitions from a file"""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in self.function_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    functions.append({
                        'name': match.group(1),
                        'file': file_path,
                        'line': line_num,
                        'pattern': pattern
                    })
        
        except Exception as e:
            self.log(f"Error reading {file_path}: {e}", "WARNING")
        
        return functions
    
    def detect_similar_functions(self, functions: List[Dict]) -> List[Dict]:
        """Detect functions with similar names or purposes"""
        similar_groups = defaultdict(list)
        
        # Group by similarity patterns
        for func in functions:
            name = func['name'].lower()
            
            # Group by semantic similarity
            for domain, patterns in self.domain_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, name):
                        similar_groups[f"{domain}_{pattern}"].append(func)
            
            # Group by name similarity (edit distance)
            base_name = re.sub(r'[0-9_]+$', '', name)  # Remove version suffixes
            similar_groups[f"name_similarity_{base_name}"].append(func)
        
        # Filter groups with multiple functions
        duplicates = []
        for group_name, group_functions in similar_groups.items():
            if len(group_functions) > 1:
                duplicates.append({
                    'type': 'similar_functions',
                    'pattern': group_name,
                    'functions': group_functions,
                    'severity': self._calculate_severity(group_functions)
                })
        
        return duplicates
    
    def detect_duplicate_files(self, code_files: List[str]) -> List[Dict]:
        """Detect files with similar names or purposes"""
        duplicates = []
        file_groups = defaultdict(list)
        
        for file_path in code_files:
            filename = os.path.basename(file_path)
            
            # Remove version suffixes and extensions
            base_name = re.sub(r'_v?\d+|_backup|_old|_new|_fixed|_working|\.py$', '', filename.lower())
            base_name = re.sub(r'_\d{8}|_\d{6}', '', base_name)  # Remove date stamps
            
            file_groups[base_name].append(file_path)
        
        # Find groups with multiple files
        for base_name, files in file_groups.items():
            if len(files) > 1:
                duplicates.append({
                    'type': 'duplicate_files',
                    'base_name': base_name,
                    'files': files,
                    'severity': 'HIGH' if 'api' in base_name else 'MEDIUM'
                })
        
        return duplicates
    
    def detect_code_block_similarity(self, code_files: List[str]) -> List[Dict]:
        """Detect similar code blocks across files"""
        similar_blocks = []
        
        # Sample a subset for performance
        sample_files = code_files[:20] if len(code_files) > 20 else code_files
        
        for i, file1 in enumerate(sample_files):
            for file2 in sample_files[i+1:]:
                similarity = self._calculate_file_similarity(file1, file2)
                if similarity > 0.7:  # 70% similar
                    similar_blocks.append({
                        'type': 'similar_code_blocks',
                        'file1': file1,
                        'file2': file2,
                        'similarity': similarity,
                        'severity': 'HIGH' if similarity > 0.9 else 'MEDIUM'
                    })
        
        return similar_blocks
    
    def _calculate_file_similarity(self, file1: str, file2: str) -> float:
        """Calculate similarity between two files"""
        try:
            with open(file1, 'r', encoding='utf-8') as f1:
                content1 = f1.read()
            with open(file2, 'r', encoding='utf-8') as f2:
                content2 = f2.read()
            
            # Use difflib to calculate similarity
            matcher = difflib.SequenceMatcher(None, content1, content2)
            return matcher.ratio()
        
        except Exception:
            return 0.0
    
    def _calculate_severity(self, functions: List[Dict]) -> str:
        """Calculate severity of duplication"""
        if len(functions) > 5:
            return 'HIGH'
        elif len(functions) > 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def scan_for_duplications(self) -> Dict:
        """Run comprehensive duplication scan"""
        self.log("🔍 Starting comprehensive code duplication scan...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'files_scanned': 0,
            'duplications': {
                'similar_functions': [],
                'duplicate_files': [],
                'similar_code_blocks': []
            },
            'summary': {}
        }
        
        # Get all code files
        code_files = self.get_all_code_files()
        results['files_scanned'] = len(code_files)
        self.log(f"📁 Found {len(code_files)} code files to analyze")
        
        # Extract all functions
        self.log("🔍 Extracting function definitions...")
        all_functions = []
        for file_path in code_files:
            functions = self.extract_functions(file_path)
            all_functions.extend(functions)
        
        self.log(f"📊 Extracted {len(all_functions)} function definitions")
        
        # Detect similar functions
        self.log("🔍 Detecting similar functions...")
        similar_functions = self.detect_similar_functions(all_functions)
        results['duplications']['similar_functions'] = similar_functions
        
        # Detect duplicate files
        self.log("🔍 Detecting duplicate files...")
        duplicate_files = self.detect_duplicate_files(code_files)
        results['duplications']['duplicate_files'] = duplicate_files
        
        # Detect similar code blocks
        self.log("🔍 Detecting similar code blocks...")
        similar_blocks = self.detect_code_block_similarity(code_files)
        results['duplications']['similar_code_blocks'] = similar_blocks
        
        # Generate summary
        total_duplications = (len(similar_functions) + len(duplicate_files) + len(similar_blocks))
        results['summary'] = {
            'total_duplications': total_duplications,
            'similar_functions': len(similar_functions),
            'duplicate_files': len(duplicate_files),
            'similar_code_blocks': len(similar_blocks)
        }
        
        self.log(f"📊 Scan complete: {total_duplications} duplication patterns found")
        return results
    
    def generate_tasks(self, scan_results: Dict) -> List[Dict]:
        """Generate structured tasks for _tasks.md"""
        tasks = []
        task_id = 1
        
        # Generate tasks for duplicate files (highest priority)
        for dup in scan_results['duplications']['duplicate_files']:
            if dup['severity'] == 'HIGH':
                tasks.append({
                    'id': f"DUPLICATION-{task_id:03d}",
                    'title': f"Consolidate duplicate {dup['base_name']} files",
                    'priority': 'HIGH',
                    'type': 'code_consolidation',
                    'description': f"Multiple files found with similar purposes: {', '.join([os.path.basename(f) for f in dup['files']])}",
                    'files': dup['files'],
                    'suggested_approach': 'Merge functionality into single file with environment-based configuration',
                    'impact': 'Reduces maintenance overhead and deployment confusion'
                })
                task_id += 1
        
        # Generate tasks for similar functions
        high_priority_functions = [dup for dup in scan_results['duplications']['similar_functions'] 
                                 if dup.get('severity') == 'HIGH']
        
        for dup in high_priority_functions[:5]:  # Limit to top 5
            tasks.append({
                'id': f"DUPLICATION-{task_id:03d}",
                'title': f"Consolidate {dup['pattern']} functions",
                'priority': 'MEDIUM',
                'type': 'function_consolidation',
                'description': f"Found {len(dup['functions'])} similar functions: {', '.join([f['name'] for f in dup['functions'][:3]])}",
                'functions': dup['functions'],
                'suggested_approach': 'Create single base function with configurable parameters',
                'impact': 'Reduces code duplication and improves maintainability'
            })
            task_id += 1
        
        # Generate tasks for similar code blocks
        for dup in scan_results['duplications']['similar_code_blocks']:
            if dup['severity'] == 'HIGH':
                tasks.append({
                    'id': f"DUPLICATION-{task_id:03d}",
                    'title': f"Refactor similar code in {os.path.basename(dup['file1'])} and {os.path.basename(dup['file2'])}",
                    'priority': 'LOW',
                    'type': 'code_refactoring',
                    'description': f"Files are {dup['similarity']:.1%} similar - opportunity for shared utilities",
                    'files': [dup['file1'], dup['file2']],
                    'suggested_approach': 'Extract common functionality into shared module',
                    'impact': 'Reduces code duplication and improves consistency'
                })
                task_id += 1
        
        return tasks
    
    def update_tasks_file(self, tasks: List[Dict]):
        """Update _tasks.md file with generated tasks"""
        tasks_file = os.path.join(self.project_root, '_tasks.md')
        
        # Read existing tasks if file exists
        existing_content = ""
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                existing_content = f.read()
        
        # Generate new tasks section
        new_section = f"""
## Code Duplication Tasks (Generated {datetime.now().strftime('%Y-%m-%d')})

"""
        
        for task in tasks:
            new_section += f"""### {task['id']}: {task['title']} [{task['priority']}]
**Type**: {task['type']}
**Description**: {task['description']}
**Suggested Approach**: {task['suggested_approach']}
**Impact**: {task['impact']}

"""
            if 'files' in task:
                new_section += f"**Files involved**:\n"
                for file_path in task['files']:
                    new_section += f"- `{file_path}`\n"
                new_section += "\n"
        
        # Write updated content
        with open(tasks_file, 'w') as f:
            if existing_content:
                f.write(existing_content)
                f.write("\n---\n")
            f.write(new_section)
        
        self.log(f"📝 Updated {tasks_file} with {len(tasks)} duplication tasks")

def main():
    parser = argparse.ArgumentParser(description="Code Duplication Detection Agent")
    parser.add_argument('--scan', action='store_true', help='Run full duplication scan')
    parser.add_argument('--quick', action='store_true', help='Run quick scan for critical issues')
    parser.add_argument('--update-tasks', action='store_true', help='Update _tasks.md with findings')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--dir', help='Specific directory to scan (reduces tokens)')
    parser.add_argument('--pattern', help='File pattern to match (e.g., "*.py")')
    parser.add_argument('--top', type=int, help='Only report top N issues')
    parser.add_argument('--skip-content', action='store_true', help='Skip file content analysis (faster)')
    
    args = parser.parse_args()
    
    # Create agent
    agent = CodeDuplicationAgent(args.project_root)
    
    if args.quick:
        agent.log("🚀 Running quick duplication scan...")
        # Quick scan logic here
        print("Quick scan not implemented yet - use --scan for full analysis")
        return
    
    if args.scan or args.update_tasks:
        # Run full scan
        results = agent.scan_for_duplications()
        
        # Generate tasks
        tasks = agent.generate_tasks(results)
        
        # Print summary
        print(f"\n📊 Duplication Detection Summary:")
        print(f"   Files scanned: {results['files_scanned']}")
        print(f"   Duplications found: {results['summary']['total_duplications']}")
        print(f"   Tasks generated: {len(tasks)}")
        
        if args.update_tasks:
            agent.update_tasks_file(tasks)
        else:
            print(f"\n💡 Run with --update-tasks to add {len(tasks)} tasks to _tasks.md")

if __name__ == "__main__":
    main()