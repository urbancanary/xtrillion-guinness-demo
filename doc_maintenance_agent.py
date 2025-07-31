#!/usr/bin/env python3
"""
Documentation Maintenance Agent
===============================

Automated agent for regular monitoring and updating of API documentation.
Runs comprehensive checks to ensure examples work and documentation stays current.

Usage:
    python3 doc_maintenance_agent.py --check     # Check only, no changes
    python3 doc_maintenance_agent.py --update    # Check and auto-fix issues
    python3 doc_maintenance_agent.py --schedule  # Set up automated runs
"""

import os
import sys
import json
import time
import requests
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
import subprocess

class DocumentationMaintenanceAgent:
    """
    Automated documentation maintenance and validation agent
    """
    
    def __init__(self, api_base: str = "http://localhost:8080", api_key: str = "xtrillion-ga9-key-2024"):
        self.api_base = api_base
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
        
        # Documentation files to monitor
        self.doc_files = [
            "API_SPECIFICATION_PRODUCTION_REALITY.md",
            "API_SPECIFICATION_EXTERNAL.md", 
            "README.md",
            "CLAUDE.md",
            "geographic_performance_analysis.md"
        ]
        
        # Test files to validate
        self.test_files = [
            "test_25_bond_portfolio_comprehensive.py",
            "timing_test_25_portfolio.py",
            "geographic_performance_test.py"
        ]
        
        # Results tracking
        self.issues_found = []
        self.fixes_applied = []
        self.performance_data = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Structured logging with timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_api_health(self) -> bool:
        """Verify API is accessible before running checks"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=10)
            if response.status_code == 200:
                self.log("✅ API health check passed")
                return True
            else:
                self.log(f"❌ API health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ API not accessible: {e}", "ERROR")
            return False
    
    def extract_api_examples(self, file_path: str) -> List[Dict]:
        """Extract API examples from documentation files"""
        examples = []
        
        if not os.path.exists(file_path):
            return examples
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find JSON code blocks that look like API requests
        json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)
        
        for i, block in enumerate(json_blocks):
            try:
                parsed = json.loads(block)
                # Identify if this looks like an API request
                if any(key in parsed for key in ['description', 'data', 'isin', 'bonds']):
                    examples.append({
                        'file': file_path,
                        'example_id': i + 1,
                        'content': parsed,
                        'raw': block
                    })
            except json.JSONDecodeError:
                continue
                
        return examples
    
    def test_api_example(self, example: Dict) -> Dict:
        """Test an API example against the live API"""
        result = {
            'example': example,
            'success': False,
            'response_code': None,
            'response_time_ms': None,
            'issues': []
        }
        
        # Determine endpoint based on request structure
        request_data = example['content']
        
        if 'data' in request_data:  # Portfolio request
            endpoint = f"{self.api_base}/api/v1/portfolio/analysis"
        elif 'bonds' in request_data:  # Cash flow request
            endpoint = f"{self.api_base}/api/v1/bond/cashflow"
        elif 'description' in request_data or 'isin' in request_data:  # Single bond
            endpoint = f"{self.api_base}/api/v1/bond/analysis"
        else:
            result['issues'].append("Cannot determine appropriate endpoint")
            return result
        
        try:
            start_time = time.perf_counter()
            response = requests.post(endpoint, json=request_data, headers=self.headers, timeout=30)
            end_time = time.perf_counter()
            
            result['response_code'] = response.status_code
            result['response_time_ms'] = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                result['success'] = True
                
                # Validate response structure
                try:
                    response_data = response.json()
                    if 'status' in response_data and response_data['status'] != 'success':
                        result['issues'].append("API returned error status")
                except json.JSONDecodeError:
                    result['issues'].append("Invalid JSON response")
            else:
                result['issues'].append(f"HTTP {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            result['issues'].append("Request timeout (>30s)")
        except Exception as e:
            result['issues'].append(f"Request failed: {str(e)}")
            
        return result
    
    def measure_current_performance(self) -> Dict:
        """Measure current API performance for documentation updates"""
        performance = {}
        
        # Test single bond
        single_bond_request = {
            "description": "T 3 15/08/52",
            "price": 71.66
        }
        
        try:
            start_time = time.perf_counter()
            response = requests.post(
                f"{self.api_base}/api/v1/bond/analysis",
                json=single_bond_request,
                headers=self.headers,
                timeout=30
            )
            end_time = time.perf_counter()
            
            if response.status_code == 200:
                performance['single_bond_ms'] = (end_time - start_time) * 1000
                
        except Exception as e:
            self.log(f"⚠️ Single bond performance test failed: {e}", "WARNING")
        
        # Test 25-bond portfolio
        portfolio_request = {
            "data": [
                {"description": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 25.0},
                {"description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "CLOSING PRICE": 77.88, "WEIGHTING": 4.0},
                {"description": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "CLOSING PRICE": 89.40, "WEIGHTING": 4.0},
                # Add more bonds for full 25-bond test...
            ]
        }
        
        # Add remaining bonds to reach 25
        base_bonds = [
            {"description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "CLOSING PRICE": 87.14, "WEIGHTING": 4.0},
            {"description": "EMPRESA METRO, 4.7%, 07-May-2050", "CLOSING PRICE": 80.39, "WEIGHTING": 4.0},
            {"description": "CODELCO INC, 6.15%, 24-Oct-2036", "CLOSING PRICE": 101.63, "WEIGHTING": 4.0},
        ]
        portfolio_request["data"].extend(base_bonds)
        
        try:
            start_time = time.perf_counter()
            response = requests.post(
                f"{self.api_base}/api/v1/portfolio/analysis",
                json=portfolio_request,
                headers=self.headers,
                timeout=30
            )
            end_time = time.perf_counter()
            
            if response.status_code == 200:
                portfolio_time_ms = (end_time - start_time) * 1000
                bond_count = len(portfolio_request["data"])
                performance['portfolio_ms'] = portfolio_time_ms
                performance['portfolio_bonds'] = bond_count
                performance['bonds_per_second'] = bond_count / (portfolio_time_ms / 1000)
                
        except Exception as e:
            self.log(f"⚠️ Portfolio performance test failed: {e}", "WARNING")
        
        return performance
    
    def check_test_files(self) -> List[Dict]:
        """Check test files for correct endpoint usage"""
        test_issues = []
        
        for test_file in self.test_files:
            if not os.path.exists(test_file):
                continue
                
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Check for deprecated endpoints
            deprecated_patterns = [
                r'/api/v1/portfolio/calculate',
                r'/api/v1/bond/parse-and-calculate'
            ]
            
            for pattern in deprecated_patterns:
                if re.search(pattern, content):
                    test_issues.append({
                        'file': test_file,
                        'issue': f'Uses deprecated endpoint: {pattern}',
                        'fix': 'Update to current endpoint'
                    })
        
        return test_issues
    
    def run_comprehensive_check(self) -> Dict:
        """Run complete documentation maintenance check"""
        self.log("🔍 Starting comprehensive documentation check...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'api_accessible': False,
            'examples_tested': 0,
            'examples_passed': 0,
            'issues_found': [],
            'performance_data': {},
            'test_file_issues': []
        }
        
        # 1. Check API accessibility
        if not self.check_api_health():
            results['issues_found'].append("API not accessible - cannot validate examples")
            return results
        
        results['api_accessible'] = True
        
        # 2. Extract and test API examples
        self.log("📝 Extracting API examples from documentation...")
        all_examples = []
        
        for doc_file in self.doc_files:
            if os.path.exists(doc_file):
                examples = self.extract_api_examples(doc_file)
                all_examples.extend(examples)
                self.log(f"   Found {len(examples)} examples in {doc_file}")
        
        # 3. Test each example
        self.log(f"🧪 Testing {len(all_examples)} API examples...")
        
        for example in all_examples:
            test_result = self.test_api_example(example)
            results['examples_tested'] += 1
            
            if test_result['success']:
                results['examples_passed'] += 1
                self.log(f"   ✅ Example {example['example_id']} from {example['file']} - {test_result['response_time_ms']:.1f}ms")
            else:
                results['issues_found'].append({
                    'type': 'example_failure',
                    'file': example['file'],
                    'example_id': example['example_id'],
                    'issues': test_result['issues']
                })
                self.log(f"   ❌ Example {example['example_id']} from {example['file']}: {', '.join(test_result['issues'])}")
        
        # 4. Measure current performance
        self.log("⏱️ Measuring current API performance...")
        results['performance_data'] = self.measure_current_performance()
        
        # 5. Check test files
        self.log("🔍 Checking test files for issues...")
        results['test_file_issues'] = self.check_test_files()
        
        # 6. Summary
        success_rate = (results['examples_passed'] / results['examples_tested'] * 100) if results['examples_tested'] > 0 else 0
        self.log(f"📊 Documentation check complete:")
        self.log(f"   Examples tested: {results['examples_tested']}")
        self.log(f"   Success rate: {success_rate:.1f}%")
        self.log(f"   Issues found: {len(results['issues_found'])}")
        
        return results
    
    def generate_maintenance_report(self, results: Dict) -> str:
        """Generate a detailed maintenance report"""
        report = f"""# Documentation Maintenance Report
Generated: {results['timestamp']}

## Summary
- API Accessible: {'✅' if results['api_accessible'] else '❌'}
- Examples Tested: {results['examples_tested']}
- Examples Passed: {results['examples_passed']}
- Success Rate: {(results['examples_passed'] / results['examples_tested'] * 100):.1f}%
- Issues Found: {len(results['issues_found'])}

## Performance Data
"""
        
        if results['performance_data']:
            perf = results['performance_data']
            if 'single_bond_ms' in perf:
                report += f"- Single Bond: {perf['single_bond_ms']:.1f}ms\n"
            if 'portfolio_ms' in perf:
                report += f"- Portfolio ({perf['portfolio_bonds']} bonds): {perf['portfolio_ms']:.1f}ms ({perf['bonds_per_second']:.1f} bonds/sec)\n"
        
        report += "\n## Issues Found\n"
        
        for issue in results['issues_found']:
            if issue['type'] == 'example_failure':
                report += f"- **{issue['file']}** Example {issue['example_id']}: {', '.join(issue['issues'])}\n"
        
        for issue in results['test_file_issues']:
            report += f"- **{issue['file']}**: {issue['issue']}\n"
        
        return report
    
    def save_results(self, results: Dict, filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            filename = f"doc_maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.log(f"📁 Results saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Documentation Maintenance Agent")
    parser.add_argument('--check', action='store_true', help='Run checks only, no changes')
    parser.add_argument('--update', action='store_true', help='Run checks and auto-fix issues')
    parser.add_argument('--schedule', action='store_true', help='Set up automated runs')
    parser.add_argument('--api-base', default='http://localhost:8080', help='API base URL')
    parser.add_argument('--api-key', default='xtrillion-ga9-key-2024', help='API key')
    
    args = parser.parse_args()
    
    # Create agent
    agent = DocumentationMaintenanceAgent(args.api_base, args.api_key)
    
    if args.schedule:
        print("🕐 Automated scheduling not implemented yet")
        print("💡 Run manually with cron: */30 * * * * cd /path/to/project && python3 doc_maintenance_agent.py --check")
        return
    
    # Run comprehensive check
    results = agent.run_comprehensive_check()
    
    # Generate and save report
    report = agent.generate_maintenance_report(results)
    print("\n" + "="*60)
    print(report)
    
    agent.save_results(results)
    
    # Auto-fix if requested
    if args.update:
        print("\n🔧 Auto-fix functionality not implemented yet")
        print("💡 Review issues above and apply fixes manually")

if __name__ == "__main__":
    main()