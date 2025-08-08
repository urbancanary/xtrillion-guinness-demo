#!/usr/bin/env python3
"""
GA10 Documentation Agent
========================

Project-specific documentation agent for Google Analysis 10 that uses
the universal doc checker as a sub-agent.

This agent:
1. Uses universal_doc_checker for basic validation
2. Adds GA10-specific checks (API endpoints, bond examples)
3. Can validate API examples against live API
4. Generates GA10-specific reports
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from universal_doc_checker import UniversalDocChecker

class GA10DocumentationAgent:
    """
    Google Analysis 10 specific documentation agent
    """
    
    def __init__(self, api_base: str = None, api_key: str = None):
        # Initialize universal checker with GA10 config
        self.checker = UniversalDocChecker({
            'file_patterns': ['*.md', '*.txt'],
            'code_languages': ['python', 'json', 'bash', 'yaml'],
            'check_links': True,
            'custom_validators': {
                'json': self._validate_ga10_json
            }
        })
        
        # GA10 specific config
        self.api_base = api_base or "http://localhost:8080"
        self.api_key = api_key or "xtrillion-ga9-key-2024"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        
        # GA10 specific documentation files
        self.critical_docs = [
            "API_SPECIFICATION_PRODUCTION_REALITY.md",
            "API_SPECIFICATION_EXTERNAL.md",
            "CLAUDE.md",
            "README.md"
        ]
        
        # Known API endpoints
        self.api_endpoints = [
            "/api/v1/bond/analysis",
            "/api/v1/portfolio/analysis",
            "/api/v1/treasury/status",
            "/api/v1/version",
            "/health"
        ]
    
    def run_full_check(self) -> Dict:
        """Run complete GA10 documentation check"""
        print("🔍 Running GA10 Documentation Check...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'universal_check': {},
            'api_validation': {},
            'ga10_specific': {},
            'summary': {}
        }
        
        # 1. Run universal documentation checks
        print("\n📝 Running universal documentation checks...")
        results['universal_check'] = self.checker.check_directory(".", recursive=False)
        
        # 2. Run GA10-specific checks
        print("\n🎯 Running GA10-specific checks...")
        results['ga10_specific'] = self._run_ga10_checks()
        
        # 3. Validate API examples if API is available
        if self._check_api_health():
            print("\n🌐 Validating API examples...")
            results['api_validation'] = self._validate_api_examples()
        else:
            print("\n⚠️  API not available - skipping live validation")
            results['api_validation'] = {'skipped': True, 'reason': 'API not accessible'}
        
        # 4. Generate summary
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _validate_ga10_json(self, code: str) -> Dict[str, List]:
        """Custom JSON validator for GA10 API examples"""
        # First run standard JSON validation
        result = {'issues': [], 'warnings': []}
        
        try:
            data = json.loads(code)
            
            # Check for GA10-specific patterns
            if isinstance(data, dict):
                # Check for bond analysis request
                if 'description' in data or 'isin' in data:
                    if 'price' not in data:
                        result['warnings'].append({
                            'type': 'missing_price',
                            'message': 'Bond analysis request missing price field'
                        })
                
                # Check for portfolio analysis request
                if 'data' in data and isinstance(data['data'], list):
                    for i, bond in enumerate(data['data']):
                        if 'CLOSING PRICE' not in bond and 'price' not in bond:
                            result['warnings'].append({
                                'type': 'missing_price',
                                'message': f'Portfolio bond {i} missing price field'
                            })
                
                # Check for deprecated fields
                deprecated_fields = ['parse_description', 'calculate_all']
                for field in deprecated_fields:
                    if field in data:
                        result['warnings'].append({
                            'type': 'deprecated_field',
                            'message': f'Using deprecated field: {field}'
                        })
            
        except json.JSONDecodeError as e:
            result['issues'].append({
                'type': 'json_error',
                'message': f'JSON syntax error: {e.msg}'
            })
        
        return result
    
    def _run_ga10_checks(self) -> Dict:
        """Run GA10-specific documentation checks"""
        ga10_results = {
            'endpoint_references': [],
            'bond_examples': [],
            'version_info': []
        }
        
        # Check critical documentation files
        for doc_file in self.critical_docs:
            if os.path.exists(doc_file):
                with open(doc_file, 'r') as f:
                    content = f.read()
                
                # Check endpoint references
                for endpoint in self.api_endpoints:
                    if endpoint in content:
                        ga10_results['endpoint_references'].append({
                            'file': doc_file,
                            'endpoint': endpoint,
                            'found': True
                        })
                
                # Check for version information
                if 'v2.3' in content or 'Version 2.3' in content:
                    ga10_results['version_info'].append({
                        'file': doc_file,
                        'version': 'v2.3',
                        'current': True
                    })
        
        return ga10_results
    
    def _check_api_health(self) -> bool:
        """Check if API is accessible"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _validate_api_examples(self) -> Dict:
        """Validate API examples from documentation"""
        validation_results = {
            'examples_tested': 0,
            'examples_passed': 0,
            'failures': []
        }
        
        # Extract examples from key documentation files
        for doc_file in ['API_SPECIFICATION_EXTERNAL.md', 'EXTERNAL_USER_GUIDE.md']:
            if not os.path.exists(doc_file):
                continue
            
            examples = self._extract_api_examples(doc_file)
            
            for example in examples:
                validation_results['examples_tested'] += 1
                
                # Determine endpoint
                if 'data' in example.get('content', {}):
                    endpoint = '/api/v1/portfolio/analysis'
                else:
                    endpoint = '/api/v1/bond/analysis'
                
                # Test the example
                try:
                    response = requests.post(
                        f"{self.api_base}{endpoint}",
                        json=example['content'],
                        headers=self.headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        validation_results['examples_passed'] += 1
                    else:
                        validation_results['failures'].append({
                            'file': doc_file,
                            'example_id': example['id'],
                            'status_code': response.status_code,
                            'error': response.text[:200]
                        })
                except Exception as e:
                    validation_results['failures'].append({
                        'file': doc_file,
                        'example_id': example['id'],
                        'error': str(e)
                    })
        
        return validation_results
    
    def _extract_api_examples(self, file_path: str) -> List[Dict]:
        """Extract API examples from documentation"""
        examples = []
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find JSON code blocks
        import re
        json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)
        
        for i, block in enumerate(json_blocks):
            try:
                parsed = json.loads(block)
                # Check if it looks like an API request
                if isinstance(parsed, dict) and any(
                    key in parsed for key in ['description', 'isin', 'data', 'bonds']
                ):
                    examples.append({
                        'id': i + 1,
                        'content': parsed
                    })
            except:
                pass
        
        return examples
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate summary of all checks"""
        summary = {
            'total_files_checked': results['universal_check'].get('files_checked', 0),
            'total_issues': results['universal_check'].get('total_issues', 0),
            'total_warnings': results['universal_check'].get('total_warnings', 0),
            'api_examples_tested': results['api_validation'].get('examples_tested', 0),
            'api_examples_passed': results['api_validation'].get('examples_passed', 0),
            'critical_docs_present': len([
                doc for doc in self.critical_docs if os.path.exists(doc)
            ]),
            'health_status': 'API Available' if not results['api_validation'].get('skipped') else 'API Unavailable'
        }
        
        # Calculate health score
        if summary['total_files_checked'] > 0:
            issue_rate = summary['total_issues'] / summary['total_files_checked']
            summary['health_score'] = max(0, 100 - (issue_rate * 10))
        else:
            summary['health_score'] = 0
        
        return summary
    
    def generate_report(self, results: Dict) -> str:
        """Generate GA10-specific report"""
        report = []
        report.append("=" * 60)
        report.append("GA10 Documentation Health Report")
        report.append("=" * 60)
        report.append(f"Generated: {results['timestamp']}")
        report.append("")
        
        # Summary section
        summary = results['summary']
        report.append("📊 SUMMARY")
        report.append("-" * 40)
        report.append(f"Health Score: {summary['health_score']:.1f}/100")
        report.append(f"Files Checked: {summary['total_files_checked']}")
        report.append(f"Issues Found: {summary['total_issues']}")
        report.append(f"Warnings: {summary['total_warnings']}")
        report.append(f"API Status: {summary['health_status']}")
        report.append("")
        
        # Critical documentation status
        report.append("📚 CRITICAL DOCUMENTATION")
        report.append("-" * 40)
        for doc in self.critical_docs:
            status = "✅" if os.path.exists(doc) else "❌"
            report.append(f"{status} {doc}")
        report.append("")
        
        # API validation results
        if not results['api_validation'].get('skipped'):
            report.append("🌐 API VALIDATION")
            report.append("-" * 40)
            api_val = results['api_validation']
            report.append(f"Examples Tested: {api_val['examples_tested']}")
            report.append(f"Examples Passed: {api_val['examples_passed']}")
            if api_val['failures']:
                report.append("\nFailed Examples:")
                for failure in api_val['failures'][:5]:  # Show first 5
                    report.append(f"  - {failure['file']} (example {failure['example_id']})")
        
        # Top issues
        if results['universal_check'].get('files'):
            report.append("\n🔍 TOP ISSUES")
            report.append("-" * 40)
            issue_count = 0
            for file_result in results['universal_check']['files']:
                if file_result.get('issues'):
                    for issue in file_result['issues'][:2]:  # Show first 2 per file
                        report.append(f"- {file_result['file']}: {issue['message']}")
                        issue_count += 1
                        if issue_count >= 10:
                            break
                if issue_count >= 10:
                    break
        
        return "\n".join(report)


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GA10 Documentation Agent")
    parser.add_argument('--api-base', default="http://localhost:8080", help='API base URL')
    parser.add_argument('--api-key', default="xtrillion-ga9-key-2024", help='API key')
    parser.add_argument('--output', help='Save report to file')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    
    args = parser.parse_args()
    
    # Create and run agent
    agent = GA10DocumentationAgent(args.api_base, args.api_key)
    results = agent.run_full_check()
    
    # Generate output
    if args.json:
        output = json.dumps(results, indent=2)
    else:
        output = agent.generate_report(results)
    
    # Display/save output
    print(output)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"\nReport saved to: {args.output}")


if __name__ == '__main__':
    main()