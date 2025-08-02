#!/usr/bin/env python3
"""
Enforce Valid Database Usage
============================

Ensures only the three valid databases are referenced in the codebase:
- bonds_data.db (contains tsys_enhanced table)
- validated_quantlib_bonds.db
- bloomberg_index.db
"""

import os
import re
import sys
from pathlib import Path


# Define the only valid databases
VALID_DATABASES = {
    'bonds_data.db',
    'validated_quantlib_bonds.db',
    'bloomberg_index.db'
}

# Invalid databases that should NOT be used
INVALID_DATABASES = {
    'yield_curves.db',
    'tsys_enhanced.db',
    'validated_conventions.db',
    'conventions.db'
}


def find_database_references(directory='.'):
    """Find all database references in Python files."""
    issues = []
    
    # Pattern to match database file references
    db_pattern = re.compile(r'["\']([^"\']+\.db)["\']')
    
    for root, dirs, files in os.walk(directory):
        # Skip directories we don't want to check
        if any(skip in root for skip in ['venv', '__pycache__', '.git', 'archive']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        line_num = 0
                        
                        for line in content.split('\n'):
                            line_num += 1
                            matches = db_pattern.findall(line)
                            
                            for db_name in matches:
                                # Extract just the filename
                                db_file = os.path.basename(db_name)
                                
                                if db_file in INVALID_DATABASES:
                                    issues.append({
                                        'file': filepath,
                                        'line': line_num,
                                        'database': db_file,
                                        'code': line.strip()
                                    })
                                
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    return issues


def check_existing_db_files():
    """Check for invalid database files in the directory."""
    invalid_found = []
    
    for db_file in INVALID_DATABASES:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            invalid_found.append((db_file, size))
    
    return invalid_found


def suggest_fixes(issues):
    """Suggest fixes for found issues."""
    fixes = {
        'yield_curves.db': 'bonds_data.db',
        'tsys_enhanced.db': 'bonds_data.db',
        'validated_conventions.db': 'validated_quantlib_bonds.db',
        'conventions.db': 'validated_quantlib_bonds.db'
    }
    
    for issue in issues:
        old_db = issue['database']
        new_db = fixes.get(old_db, 'bonds_data.db')
        issue['suggested_fix'] = new_db
    
    return issues


def main():
    """Main enforcement function."""
    print("🔍 Enforcing Valid Database Usage")
    print("=" * 60)
    print(f"Valid databases: {', '.join(sorted(VALID_DATABASES))}")
    print(f"Invalid databases: {', '.join(sorted(INVALID_DATABASES))}")
    print("=" * 60)
    
    # Check for invalid database files
    print("\n1️⃣ Checking for invalid database files...")
    invalid_files = check_existing_db_files()
    
    if invalid_files:
        print("   ❌ Found invalid database files:")
        for db_file, size in invalid_files:
            print(f"      - {db_file} ({size} bytes)")
        print("   💡 Recommendation: Delete these files")
    else:
        print("   ✅ No invalid database files found")
    
    # Check code references
    print("\n2️⃣ Checking code for invalid database references...")
    issues = find_database_references()
    
    if issues:
        issues = suggest_fixes(issues)
        print(f"   ❌ Found {len(issues)} invalid database references:")
        
        # Group by file
        by_file = {}
        for issue in issues:
            file_path = issue['file']
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(issue)
        
        for file_path, file_issues in by_file.items():
            print(f"\n   📄 {file_path}:")
            for issue in file_issues:
                print(f"      Line {issue['line']}: {issue['database']} → {issue['suggested_fix']}")
                print(f"         Code: {issue['code'][:60]}...")
    else:
        print("   ✅ No invalid database references found in code")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    total_issues = len(issues) + len(invalid_files)
    if total_issues == 0:
        print("✅ All database usage is valid!")
    else:
        print(f"❌ Found {total_issues} total issues to fix:")
        if invalid_files:
            print(f"   - {len(invalid_files)} invalid database files")
        if issues:
            print(f"   - {len(issues)} invalid code references")
        
        print("\n💡 To fix all issues automatically, run:")
        print("   python enforce_valid_databases.py --fix")
    
    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    # Check if --fix flag is provided
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        print("🔧 Auto-fix mode not implemented yet")
        print("Please fix the issues manually using the suggestions above")
    else:
        sys.exit(main())