#!/usr/bin/env python3
"""
QuantLib Usage Analyzer - Find Duration Calculation Issues
==========================================================

This script systematically analyzes all QuantLib usage in the project to identify
potential causes of the massive duration calculation error (T 3 15/08/52: 
expected 16.36 years, getting 9.69 years - 6+ year error).

Usage:
    python3 quantlib_usage_analyzer.py
"""

import os
import re
import sys
from collections import defaultdict

def analyze_quantlib_usage():
    """
    Analyze all QuantLib usage patterns across the project
    """
    
    project_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10'
    
    # Patterns to search for
    critical_patterns = {
        'Duration Functions': [
            r'ql\.BondFunctions\.duration\(',
            r'BondFunctions\.duration\(',
            r'\.duration\('
        ],
        'Yield Functions': [
            r'\.bondYield\(',
            r'bond\.yield\(',
            r'ql\.BondFunctions\.yield\('
        ],
        'Schedule Creation': [
            r'ql\.Schedule\(',
            r'Schedule\(',
            r'MakeSchedule\('
        ],
        'Bond Creation': [
            r'ql\.FixedRateBond\(',
            r'FixedRateBond\('
        ],
        'Date Generation': [
            r'ql\.DateGeneration\.',
            r'DateGeneration\.'
        ],
        'Issue Date Problems': [
            r'ql\.Period\(-\d+.*ql\.Months\)',
            r'advance.*-\d+.*Months',
            r'issue_date.*settlement_date',
            r'timedelta.*days.*\d+'
        ],
        'Yield Input Format': [
            r'duration\(.*yield.*\*.*100',
            r'duration\(.*\*.*100.*yield',
            r'BondFunctions\.duration.*yield_percentage',
            r'BondFunctions\.duration.*yield_decimal'
        ],
        'Scaling Issues': [
            r'duration.*\*.*100',
            r'\.duration\(\).*\*',
            r'duration_raw.*\*'
        ]
    }
    
    print("🔍 QUANTLIB USAGE ANALYZER")
    print("=" * 50)
    print("Searching for potential duration calculation issues...")
    print()
    
    # Results storage
    findings = defaultdict(list)
    
    # Search through all Python files
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        # Check each pattern category
                        for category, patterns in critical_patterns.items():
                            for pattern in patterns:
                                matches = re.finditer(pattern, content, re.IGNORECASE)
                                for match in matches:
                                    # Find line number
                                    line_num = content[:match.start()].count('\n') + 1
                                    line_content = lines[line_num - 1].strip()
                                    
                                    findings[category].append({
                                        'file': relative_path,
                                        'line': line_num,
                                        'pattern': pattern,
                                        'content': line_content,
                                        'match': match.group()
                                    })
                                    
                except Exception as e:
                    print(f"⚠️  Error reading {relative_path}: {e}")
    
    # Analyze and report findings
    print("📊 ANALYSIS RESULTS")
    print("=" * 50)
    
    for category, items in findings.items():
        if items:
            print(f"\n🔍 {category.upper()} ({len(items)} instances):")
            print("-" * (len(category) + 20))
            
            # Group by file for better readability
            by_file = defaultdict(list)
            for item in items:
                by_file[item['file']].append(item)
            
            for file_path, file_items in sorted(by_file.items()):
                print(f"\n📁 {file_path}:")
                for item in sorted(file_items, key=lambda x: x['line']):
                    print(f"   Line {item['line']:3d}: {item['content']}")
                    if 'Issue Date' in category and 'Period(-' in item['content']:
                        print(f"            ⚠️  POTENTIAL ISSUE: Calculating issue date artificially")
                    elif 'Duration' in category and 'yield_decimal' in item['content']:
                        print(f"            ⚠️  POTENTIAL ISSUE: Using decimal yield (should be percentage)")
                    elif 'Scaling' in category and '* 100' in item['content']:
                        print(f"            💡 Check scaling: {item['match']}")
    
    # Summary analysis
    print(f"\n🎯 CRITICAL ISSUES SUMMARY")
    print("=" * 50)
    
    # Check for issue date problems
    issue_date_problems = len(findings.get('Issue Date Problems', []))
    if issue_date_problems > 0:
        print(f"❌ CRITICAL: Found {issue_date_problems} potential issue date calculation problems")
        print("   These can cause massive duration errors (6+ years off)")
    else:
        print("✅ GOOD: No obvious issue date calculation problems found")
    
    # Check for yield input format issues
    yield_format_issues = len(findings.get('Yield Input Format', []))
    if yield_format_issues > 0:
        print(f"⚠️  WARNING: Found {yield_format_issues} potential yield format issues")
        print("   Duration functions need percentage yield, not decimal yield")
    
    # Check for inconsistent scaling
    scaling_issues = len(findings.get('Scaling Issues', []))
    if scaling_issues > 0:
        print(f"💡 INFO: Found {scaling_issues} scaling operations to verify")
        print("   Ensure consistent scaling across all duration/convexity calculations")
    
    # Specific duration function analysis
    duration_functions = len(findings.get('Duration Functions', []))
    print(f"\n📊 DURATION FUNCTION USAGE: {duration_functions} instances found")
    
    if duration_functions == 0:
        print("❌ CRITICAL: No duration functions found - this is unexpected!")
    elif duration_functions > 10:
        print("⚠️  WARNING: Many duration function calls - check for consistency")
    else:
        print("✅ REASONABLE: Normal number of duration function calls")
    
    # Generate specific investigation targets
    print(f"\n🎯 INVESTIGATION PRIORITIES")
    print("=" * 50)
    
    priorities = []
    
    if issue_date_problems > 0:
        priorities.append("1. FIX: Issue date calculation problems (CRITICAL for duration)")
    
    if yield_format_issues > 0:
        priorities.append("2. REVIEW: Yield input format for duration functions")
    
    if findings.get('Duration Functions'):
        priorities.append("3. VALIDATE: All duration function parameters and scaling")
    
    if findings.get('Schedule Creation'):
        priorities.append("4. CHECK: Schedule generation methods and date generation rules")
    
    priorities.append("5. TEST: Compare QuantLib results vs Bloomberg for T 3 15/08/52")
    
    for priority in priorities:
        print(f"   {priority}")
    
    print(f"\n📋 FILES TO REVIEW IMMEDIATELY:")
    print("-" * 30)
    
    # Identify key files with duration calculations
    critical_files = set()
    for category in ['Duration Functions', 'Issue Date Problems', 'Yield Input Format']:
        for item in findings.get(category, []):
            critical_files.add(item['file'])
    
    for file_path in sorted(critical_files):
        print(f"   📄 {file_path}")
    
    print(f"\n💡 NEXT STEPS:")
    print("1. Review each critical file above")
    print("2. Check duration function parameters match QUANTLIB_COMPREHENSIVE_AUDIT.md")
    print("3. Verify issue date calculations are using conservative approach")
    print("4. Test changes against T 3 15/08/52 bond (should be ~16.36 years)")
    
    return findings

def generate_fix_script(findings):
    """
    Generate a script to automatically fix common QuantLib issues
    """
    
    print(f"\n🔧 AUTOMATIC FIX GENERATOR")
    print("=" * 50)
    
    # Check if we found any obvious issues to fix
    issue_date_problems = findings.get('Issue Date Problems', [])
    
    if issue_date_problems:
        print("Found issue date problems that can be automatically fixed:")
        
        fixes = []
        for problem in issue_date_problems:
            if 'Period(-' in problem['content'] and 'Months' in problem['content']:
                fixes.append({
                    'file': problem['file'],
                    'line': problem['line'],
                    'issue': 'Artificial issue date calculation',
                    'current': problem['content'],
                    'fix': 'Replace with conservative issue date calculation'
                })
        
        if fixes:
            print(f"\n✅ Can automatically fix {len(fixes)} issue date problems:")
            for fix in fixes:
                print(f"   📄 {fix['file']}:{fix['line']} - {fix['issue']}")
            
            print(f"\nWould you like to generate a fix script? (Already created fix_issue_date_calculation.py)")
    else:
        print("✅ No obvious automatic fixes needed for issue date problems")
    
    # Check for other common patterns that could be fixed
    duration_inconsistencies = []
    for item in findings.get('Duration Functions', []):
        if 'yield_decimal' in item['content'].lower():
            duration_inconsistencies.append(item)
    
    if duration_inconsistencies:
        print(f"\n⚠️  Found {len(duration_inconsistencies)} potential duration function issues:")
        for issue in duration_inconsistencies:
            print(f"   📄 {issue['file']}:{issue['line']} - Check yield input format")

if __name__ == "__main__":
    print("🚀 Starting QuantLib Usage Analysis...")
    print("This will help identify the root cause of the duration calculation error.")
    print()
    
    try:
        findings = analyze_quantlib_usage()
        generate_fix_script(findings)
        
        print(f"\n🎉 ANALYSIS COMPLETE!")
        print("Review the findings above to identify duration calculation issues.")
        print("Focus on Issue Date Problems and Yield Input Format issues first.")
        
    except Exception as e:
        print(f"❌ ERROR: Analysis failed: {e}")
        import traceback
        traceback.print_exc()
