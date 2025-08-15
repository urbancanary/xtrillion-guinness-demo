#!/usr/bin/env python3
"""
Test Current Duration Bug in google_analysis10.py
==================================================
This script tests the actual google_analysis10.py code to see what
duration value we're getting for T 3 15/08/52 with the current bug.
"""

import sys
import os

# Add project to path
sys.path.insert(0, '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

# Import the actual module
import google_analysis10 as ga10

def test_current_treasury_duration():
    """Test T 3 15/08/52 with current code"""
    print("🎯 Testing Current google_analysis10.py Code")
    print("=" * 60)
    
    # Test parameters
    description = "T 3 15/08/52"
    price = 71.66
    
    print(f"\n📋 TEST PARAMETERS:")
    print(f"   Bond: {description}")
    print(f"   Price: {price}")
    print(f"   Expected Duration: 16.351196 years (Bloomberg)")
    print()
    
    # Use the actual calculate_bond function
    print("🔍 Calling google_analysis10.calculate_bond()...")
    
    try:
        result = ga10.calculate_bond(
            isin=None,
            description=description,
            price=price,
            settlement_date_str=None
        )
        
        if result and 'success' in result:
            print("\n✅ Calculation completed successfully!")
            
            # Extract metrics
            yield_val = result.get('yield', 'N/A')
            duration = result.get('duration', 'N/A')
            accrued = result.get('accrued_interest', 'N/A')
            convexity = result.get('convexity', 'N/A')
            pvbp = result.get('pvbp', 'N/A')
            
            print("\n📊 ACTUAL RESULTS FROM CURRENT CODE:")
            print(f"   Yield:           {yield_val:.5f}%" if isinstance(yield_val, (int, float)) else f"   Yield:           {yield_val}")
            print(f"   Duration:        {duration:.6f} years" if isinstance(duration, (int, float)) else f"   Duration:        {duration}")
            print(f"   Accrued:         {accrued:.6f}%" if isinstance(accrued, (int, float)) else f"   Accrued:         {accrued}")
            print(f"   Convexity:       {convexity:.2f}" if isinstance(convexity, (int, float)) else f"   Convexity:       {convexity}")
            print(f"   PVBP:            {pvbp:.6f}" if isinstance(pvbp, (int, float)) else f"   PVBP:            {pvbp}")
            
            # Check if duration is wrong
            print("\n🔍 DURATION ANALYSIS:")
            print(f"   Current:  {duration:.6f} years")
            print(f"   Expected: 16.351196 years")
            
            if isinstance(duration, (int, float)):
                diff = abs(duration - 16.351196)
                print(f"   Difference: {diff:.6f} years")
                
                if diff > 0.001:
                    print("\n❌ DURATION REGRESSION CONFIRMED!")
                    print("   The duration is NOT matching Bloomberg!")
                    print("   This confirms the ActualActual.ISMA bug.")
                else:
                    print("\n✅ Duration is correct! No regression found.")
            
            # Also check conventions being used
            conventions = result.get('conventions', {})
            if conventions:
                print("\n📋 CONVENTIONS USED:")
                print(f"   Day Count: {conventions.get('day_count', 'Unknown')}")
                print(f"   Frequency: {conventions.get('fixed_frequency', 'Unknown')}")
                print(f"   Business Day: {conventions.get('business_day_convention', 'Unknown')}")
            
            return duration
            
        else:
            print("\n❌ Calculation failed!")
            print(f"   Result: {result}")
            return None
            
    except Exception as e:
        print(f"\n❌ Error during calculation: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_quantlib_import():
    """Verify QuantLib is available and check version"""
    print("\n📦 Checking QuantLib installation...")
    try:
        import QuantLib as ql
        print(f"   ✅ QuantLib version: {ql.__version__}")
        
        # Test the different ActualActual conventions
        print("\n🔍 Testing ActualActual conventions availability:")
        try:
            test_bond = ql.ActualActual(ql.ActualActual.Bond)
            print("   ✅ ActualActual.Bond is available")
        except:
            print("   ❌ ActualActual.Bond is NOT available")
            
        try:
            test_isma = ql.ActualActual(ql.ActualActual.ISMA)
            print("   ✅ ActualActual.ISMA is available")
        except:
            print("   ❌ ActualActual.ISMA is NOT available")
            
    except ImportError:
        print("   ❌ QuantLib is not installed!")
        print("   Run: pip install QuantLib")

def check_current_code():
    """Check what the current code actually has"""
    print("\n📄 Checking current google_analysis10.py code...")
    
    file_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/google_analysis10.py'
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Find the problematic lines
    for i, line in enumerate(lines):
        if "day_count_str == 'ActualActual_Bond'" in line:
            print(f"   Found at line {i+1}: {line.strip()}")
            if i+1 < len(lines):
                next_line = lines[i+1].strip()
                print(f"   Line {i+2}: {next_line}")
                
                if 'ISMA' in next_line:
                    print("   ❌ CONFIRMED: Using ISMA (WRONG!)")
                elif 'Bond' in next_line and 'ActualActual.Bond' in next_line:
                    print("   ✅ Using Bond convention (CORRECT!)")
                else:
                    print("   ⚠️ Unexpected convention")
            break

if __name__ == "__main__":
    # Check dependencies
    check_quantlib_import()
    
    # Check current code
    check_current_code()
    
    # Run the actual test
    print("\n" + "="*60)
    duration = test_current_treasury_duration()
    
    print("\n" + "="*60)
    print("🎯 SUMMARY:")
    if duration and isinstance(duration, (int, float)):
        if abs(duration - 16.351196) > 0.001:
            print(f"   ❌ Duration regression confirmed: {duration:.6f} != 16.351196")
            print("   The ActualActual.ISMA bug is causing incorrect duration!")
            print("\n   TO FIX: Change line 459 in google_analysis10.py")
            print("   FROM: ql.ActualActual(ql.ActualActual.ISMA)")
            print("   TO:   ql.ActualActual(ql.ActualActual.Bond)")
        else:
            print(f"   ✅ Duration is correct: {duration:.6f} ≈ 16.351196")
    else:
        print("   ⚠️ Could not calculate duration - check errors above")
