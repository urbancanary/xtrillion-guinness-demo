#!/usr/bin/env python3
"""
CRITICAL FIX: Issue Date Calculation Error
=========================================

This script fixes the massive duration calculation error caused by 
artificially setting issue dates to 6 months before settlement.

PROBLEM:
--------
Line 155 in google_analysis10.py:
issue_date = calendar.advance(settlement_date, ql.Period(-6, ql.Months))

This makes QuantLib think a 30-year Treasury bond was issued 6 months ago,
causing duration calculations to be off by 6+ years.

SOLUTION:
---------
Replace calculated issue dates with conservative estimates that don't
interfere with duration calculations.
"""

import sys
import os

def fix_issue_date_calculation():
    """
    Fix the critical issue date calculation error in google_analysis10.py
    """
    
    file_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/google_analysis10.py'
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # The problematic code block
    old_code = """        # For existing bonds, set issue_date to be well before settlement to ensure accrued interest calculation
        # Use a date that's at least 6 months before settlement
        issue_date = calendar.advance(settlement_date, ql.Period(-6, ql.Months))"""
    
    # The fixed code block
    new_code = """        # CRITICAL FIX: Never calculate fake issue dates - causes massive duration errors
        # Use conservative issue date that doesn't interfere with duration calculations
        # For most bonds, use a date well before any possible real issue date
        years_before_maturity = min(35, max(10, int((maturity_date.year - 2000))))  # Adaptive based on maturity
        conservative_issue = calendar.advance(ql_maturity, ql.Period(-years_before_maturity, ql.Years))
        issue_date = conservative_issue"""
    
    if old_code in content:
        # Replace the problematic code
        fixed_content = content.replace(old_code, new_code)
        
        # Create backup
        backup_path = file_path + '.backup_issue_date_fix_' + datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Created backup: {backup_path}")
        
        # Write the fixed version
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        print(f"✅ Applied critical fix to: {file_path}")
        
        # Update the log message as well
        old_log = """        logger.info(f"{log_prefix} Issue date set to: {format_ql_date(issue_date)} (for existing bond accrued interest)")"""
        new_log = """        logger.info(f"{log_prefix} Issue date set to: {format_ql_date(issue_date)} (conservative - prevents duration calculation errors)")"""
        
        if old_log in fixed_content:
            fixed_content = fixed_content.replace(old_log, new_log)
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            print(f"✅ Updated log message as well")
        
        return True
    else:
        print(f"⚠️  Could not find the problematic code in {file_path}")
        print("Manual fix required - see CRITICAL_BOND_CALCULATION_RULES.md")
        return False

def validate_fix():
    """
    Validate that the fix was applied correctly
    """
    file_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/google_analysis10.py'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for the problematic pattern
    if "ql.Period(-6, ql.Months)" in content:
        print("❌ STILL BROKEN: Found -6 months pattern in code")
        return False
    
    # Check for the fix pattern
    if "years_before_maturity" in content and "conservative_issue" in content:
        print("✅ FIX VALIDATED: Conservative issue date logic found")
        return True
    else:
        print("❌ FIX NOT FOUND: Could not validate the fix was applied")
        return False

if __name__ == "__main__":
    from datetime import datetime
    
    print("🚨 APPLYING CRITICAL DURATION CALCULATION FIX")
    print("=" * 50)
    
    success = fix_issue_date_calculation()
    
    if success:
        print("\n🔍 VALIDATING FIX...")
        if validate_fix():
            print("\n✅ SUCCESS: Critical issue date calculation fix applied!")
            print("\n📋 NEXT STEPS:")
            print("1. Test the fix with T 3 15/08/52 bond")
            print("2. Verify duration is now ~16.36 years (not 9.69)")
            print("3. Run full regression tests")
            print("4. Update all other files with similar issues")
        else:
            print("\n❌ VALIDATION FAILED: Fix may not have been applied correctly")
    else:
        print("\n❌ AUTOMATIC FIX FAILED")
        print("MANUAL ACTION REQUIRED:")
        print("1. Open google_analysis10.py")
        print("2. Find line ~155 with 'ql.Period(-6, ql.Months)'")
        print("3. Replace with conservative issue date logic")
        print("4. See docs/CRITICAL_BOND_CALCULATION_RULES.md for details")
