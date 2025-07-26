#!/usr/bin/env python3
"""
Quick Test Script for Settlement Date Fix
=========================================

Tests that the settlement date fix is working correctly.
"""

import sys
import os
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

def test_prior_month_end():
    """Test the get_prior_month_end function"""
    from bond_master_hierarchy import get_prior_month_end
    
    prior_month_end = get_prior_month_end()
    print(f"📅 Prior month end: {prior_month_end}")
    
    # For July 2025, prior month end should be 2025-06-30
    from datetime import datetime
    today = datetime.now()
    if today.month == 7 and today.year == 2025:
        expected = "2025-06-30"
        if prior_month_end == expected:
            print("✅ Correct: Prior month end is 2025-06-30 for July 2025")
        else:
            print(f"❌ Expected {expected}, got {prior_month_end}")
    else:
        print(f"ℹ️  Current month: {today.month}/{today.year}")

def test_bond_calculation():
    """Test that the bond calculation includes correct settlement date"""
    from bond_master_hierarchy import calculate_bond_master
    import json
    
    print("\n🧪 Testing bond calculation with settlement date...")
    
    # Test Treasury bond without specifying settlement date
    result = calculate_bond_master(
        isin="US912810TJ79",
        description="T 3 15/08/52", 
        price=71.66,
        settlement_date=None  # Should default to prior month end
    )
    
    print(f"✅ Calculation successful: {result.get('success')}")
    print(f"📅 Settlement date: {result.get('settlement_date')}")
    print(f"🔧 Calculation method: {result.get('calculation_method')}")
    print(f"📊 Yield: {result.get('yield'):.4f}%" if result.get('yield') else "Yield: FAILED")
    
    # Verify settlement date is included
    if 'settlement_date' in result:
        print("✅ Settlement date is included in response")
    else:
        print("❌ Settlement date missing from response")
    
    # Verify calculation method is correct
    if result.get('calculation_method') == 'xtrillion_core':
        print("✅ Calculation method is correct: xtrillion_core")
    else:
        print(f"❌ Expected xtrillion_core, got {result.get('calculation_method')}")
    
    return result

if __name__ == "__main__":
    print("🚀 TESTING SETTLEMENT DATE FIXES")
    print("=" * 50)
    
    try:
        test_prior_month_end()
        result = test_bond_calculation()
        
        print("\n📋 SUMMARY:")
        print("✅ All tests completed")
        
        if result.get('success') and result.get('calculation_method') == 'xtrillion_core':
            print("🎉 SETTLEMENT DATE FIX SUCCESSFUL!")
        else:
            print("⚠️ Some issues detected - check the output above")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
