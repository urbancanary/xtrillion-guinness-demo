#!/usr/bin/env python3
"""
Universal Documentation Checker Sub-Agent
=========================================

A reusable documentation validation agent that can be used across different projects.
Designed to be imported and extended by project-specific agents.

Features:
- Extract code examples from Markdown files
- Validate JSON structures
- Check for broken links
- Verify code snippets syntax
- Generate standardized reports
- No external API dependencies for basic checks

Usage as a library:
    from universal_doc_checker import UniversalDocChecker
    
    checker = UniversalDocChecker()
    results = checker.check_documentation("README.md")
    
Usage as standalone:
    python3 universal_doc_checker.py --file README.md
    python3 universal_doc_checker.py --dir ./docs --recursive
"""

import os
import re
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import ast
import yaml

class UniversalDocChecker:
    """
    Universal documentation checker that can be used across projects
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the checker with optional configuration
        
        Args:
            config: Optional configuration dict with:
                - file_patterns: List of file patterns to check (default: ["*.md"])
                - code_languages: Languages to validate (default: ["python", "json", "yaml", "bash"])
                - check_links: Whether to validate links (default: False)
                - custom_validators: Dict of language -> validator function
        """
        self.config = config or {}
        self.file_patterns = self.config.get('file_patterns', ['*.md'])
        self.code_languages = self.config.get('code_languages', ['python', 'json', 'yaml', 'bash'])
        self.check_links = self.config.get('check_links', False)
        self.custom_validators = self.config.get('custom_validators', {})
        
        # Results storage
        self.results = {
            'files_checked': 0,
            'issues': [],
            'warnings': [],
            'code_blocks': [],
            'statistics': {}
        }
    
    def check_file(self, file_path: str) -> Dict[str, Any]:
        """
        Check a single documentation file
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            Dict with check results
        """
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
        
        self.results['files_checked'] += 1
        file_results = {
            'file': file_path,
            'issues': [],
            'warnings': [],
            'code_blocks': []
        }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract and validate code blocks
        code_blocks = self._extract_code_blocks(content)
        for block in code_blocks:
            block['file'] = file_path
            validation_result = self._validate_code_block(block)
            if validation_result['issues']:
                file_results['issues'].extend(validation_result['issues'])
            if validation_result['warnings']:
                file_results['warnings'].extend(validation_result['warnings'])
            file_results['code_blocks'].append(block)
        
        # Check for common documentation issues
        doc_issues = self._check_documentation_patterns(content, file_path)
        file_results['issues'].extend(doc_issues)
        
        # Check links if enabled
        if self.check_links:
            link_issues = self._check_links(content, file_path)
            file_results['issues'].extend(link_issues)
        
        return file_results
    
    def check_directory(self, directory: str, recursive: bool = True) -> Dict[str, Any]:
        """
        Check all documentation files in a directory
        
        Args:
            directory: Directory path to check
            recursive: Whether to check subdirectories
            
        Returns:
            Combined results for all files
        """
        directory = Path(directory)
        all_results = {
            'directory': str(directory),
            'files': [],
            'total_issues': 0,
            'total_warnings': 0
        }
        
        # Find all matching files
        for pattern in self.file_patterns:
            if recursive:
                files = directory.rglob(pattern)
            else:
                files = directory.glob(pattern)
            
            for file_path in files:
                if file_path.is_file():
                    result = self.check_file(str(file_path))
                    all_results['files'].append(result)
                    all_results['total_issues'] += len(result.get('issues', []))
                    all_results['total_warnings'] += len(result.get('warnings', []))
        
        return all_results
    
    def _extract_code_blocks(self, content: str) -> List[Dict]:
        """Extract code blocks from markdown content"""
        code_blocks = []
        
        # Pattern for fenced code blocks with optional language
        pattern = r'```(\w*)\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for i, (language, code) in enumerate(matches):
            code_blocks.append({
                'id': i + 1,
                'language': language or 'plain',
                'code': code,
                'line_count': len(code.splitlines())
            })
        
        return code_blocks
    
    def _validate_code_block(self, block: Dict) -> Dict[str, List]:
        """Validate a code block based on its language"""
        result = {'issues': [], 'warnings': []}
        language = block['language'].lower()
        code = block['code']
        
        # Use custom validator if available
        if language in self.custom_validators:
            return self.custom_validators[language](code)
        
        # Built-in validators
        if language == 'python':
            result = self._validate_python(code)
        elif language == 'json':
            result = self._validate_json(code)
        elif language == 'yaml' or language == 'yml':
            result = self._validate_yaml(code)
        elif language == 'bash' or language == 'sh':
            result = self._validate_bash(code)
        
        # Add context to issues
        for issue in result['issues']:
            issue['block_id'] = block['id']
            issue['language'] = language
        
        return result
    
    def _validate_python(self, code: str) -> Dict[str, List]:
        """Validate Python code syntax"""
        result = {'issues': [], 'warnings': []}
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            result['issues'].append({
                'type': 'syntax_error',
                'message': f'Python syntax error: {e.msg}',
                'line': e.lineno
            })
        except Exception as e:
            result['issues'].append({
                'type': 'parse_error',
                'message': f'Failed to parse Python code: {str(e)}'
            })
        
        # Check for common issues
        if 'print ' in code and 'print(' not in code:
            result['warnings'].append({
                'type': 'python2_syntax',
                'message': 'Code appears to use Python 2 print syntax'
            })
        
        return result
    
    def _validate_json(self, code: str) -> Dict[str, List]:
        """Validate JSON syntax"""
        result = {'issues': [], 'warnings': []}
        
        try:
            json.loads(code)
        except json.JSONDecodeError as e:
            result['issues'].append({
                'type': 'json_error',
                'message': f'JSON syntax error: {e.msg}',
                'position': e.pos
            })
        except Exception as e:
            result['issues'].append({
                'type': 'parse_error',
                'message': f'Failed to parse JSON: {str(e)}'
            })
        
        # Check for common JSON issues
        if code.strip().endswith(','):
            result['warnings'].append({
                'type': 'trailing_comma',
                'message': 'JSON has trailing comma'
            })
        
        return result
    
    def _validate_yaml(self, code: str) -> Dict[str, List]:
        """Validate YAML syntax"""
        result = {'issues': [], 'warnings': []}
        
        try:
            yaml.safe_load(code)
        except yaml.YAMLError as e:
            result['issues'].append({
                'type': 'yaml_error',
                'message': f'YAML syntax error: {str(e)}'
            })
        except Exception as e:
            result['issues'].append({
                'type': 'parse_error',
                'message': f'Failed to parse YAML: {str(e)}'
            })
        
        return result
    
    def _validate_bash(self, code: str) -> Dict[str, List]:
        """Basic bash script validation"""
        result = {'issues': [], 'warnings': []}
        
        # Check for common bash issues
        lines = code.splitlines()
        for i, line in enumerate(lines):
            # Check for missing quotes around variables
            if '$' in line and not any(q in line for q in ['"$', "'$", '${', '$(', '$/']):
                if not line.strip().startswith('#'):
                    result['warnings'].append({
                        'type': 'unquoted_variable',
                        'message': f'Line {i+1}: Variable may need quotes',
                        'line': i + 1
                    })
        
        return result
    
    def _check_documentation_patterns(self, content: str, file_path: str) -> List[Dict]:
        """Check for common documentation issues"""
        issues = []
        
        # Check for broken internal links
        internal_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        heading_anchors = [self._slugify(h) for h in headings]
        
        for link_text, anchor in internal_links:
            if anchor not in heading_anchors:
                issues.append({
                    'type': 'broken_anchor',
                    'file': file_path,
                    'message': f'Broken internal link: [{link_text}](#{anchor})'
                })
        
        # Check for TODO/FIXME items
        todos = re.findall(r'(TODO|FIXME|XXX|HACK):\s*(.+)', content)
        for marker, description in todos:
            issues.append({
                'type': 'todo_marker',
                'file': file_path,
                'message': f'{marker}: {description}',
                'severity': 'warning'
            })
        
        return issues
    
    def _check_links(self, content: str, file_path: str) -> List[Dict]:
        """Check for broken links (basic implementation)"""
        issues = []
        
        # Extract all links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        for link_text, url in links:
            # Check relative file links
            if not url.startswith(('http://', 'https://', '#')):
                # Assume it's a relative file path
                base_dir = os.path.dirname(file_path)
                full_path = os.path.join(base_dir, url)
                
                if not os.path.exists(full_path):
                    issues.append({
                        'type': 'broken_file_link',
                        'file': file_path,
                        'message': f'Broken file link: [{link_text}]({url})'
                    })
        
        return issues
    
    def _slugify(self, text: str) -> str:
        """Convert heading text to anchor format"""
        # Simple slugification - can be enhanced
        return text.lower().replace(' ', '-').replace('.', '')
    
    def generate_report(self, results: Optional[Dict] = None) -> str:
        """Generate a human-readable report"""
        results = results or self.results
        
        report = []
        report.append("Documentation Check Report")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if isinstance(results, dict) and 'files' in results:
            # Directory check results
            report.append(f"Directory: {results['directory']}")
            report.append(f"Files checked: {len(results['files'])}")
            report.append(f"Total issues: {results['total_issues']}")
            report.append(f"Total warnings: {results['total_warnings']}")
            report.append("")
            
            for file_result in results['files']:
                if file_result.get('issues') or file_result.get('warnings'):
                    report.append(f"\n📄 {file_result['file']}")
                    
                    for issue in file_result.get('issues', []):
                        report.append(f"   ❌ {issue.get('type', 'issue')}: {issue.get('message', 'No message')}")
                    
                    for warning in file_result.get('warnings', []):
                        report.append(f"   ⚠️  {warning.get('type', 'warning')}: {warning.get('message', 'No message')}")
        else:
            # Single file check results
            if 'file' in results:
                report.append(f"File: {results['file']}")
                report.append(f"Code blocks found: {len(results.get('code_blocks', []))}")
                report.append(f"Issues: {len(results.get('issues', []))}")
                report.append(f"Warnings: {len(results.get('warnings', []))}")
                report.append("")
                
                if results.get('issues'):
                    report.append("❌ ISSUES:")
                    for issue in results['issues']:
                        report.append(f"   - {issue.get('type', 'issue')}: {issue.get('message', 'No message')}")
                
                if results.get('warnings'):
                    report.append("\n⚠️  WARNINGS:")
                    for warning in results['warnings']:
                        report.append(f"   - {warning.get('type', 'warning')}: {warning.get('message', 'No message')}")
        
        return "\n".join(report)


def main():
    """CLI interface for the universal doc checker"""
    parser = argparse.ArgumentParser(description="Universal Documentation Checker")
    parser.add_argument('--file', help='Check a single file')
    parser.add_argument('--dir', help='Check all files in directory')
    parser.add_argument('--recursive', action='store_true', help='Check subdirectories')
    parser.add_argument('--check-links', action='store_true', help='Check links')
    parser.add_argument('--output', help='Output report to file')
    
    args = parser.parse_args()
    
    if not args.file and not args.dir:
        parser.error('Either --file or --dir must be specified')
    
    # Create checker
    checker = UniversalDocChecker({
        'check_links': args.check_links
    })
    
    # Run checks
    if args.file:
        results = checker.check_file(args.file)
    else:
        results = checker.check_directory(args.dir, args.recursive)
    
    # Generate report
    report = checker.generate_report(results)
    
    # Output report
    print(report)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {args.output}")


if __name__ == '__main__':
    main()