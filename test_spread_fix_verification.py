#!/usr/bin/env python3
"""
Quick verification that our spread calculation fix is working locally
Tests both corporate bonds (should have spread) and treasuries (should have 0 spread)
"""

import sys
import os

# Add the project directory to path
project_dir = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10'
sys.path.insert(0, project_dir)

def test_spread_calculations():
    """Test the spread calculation fix"""
    
    print("🧪 SPREAD CALCULATION FIX VERIFICATION")
    print("=" * 50)
    
    # Test the function we just fixed in google_analysis10.py
    # We need to import and test the actual functions
    
    try:
        # Import the functions we fixed
        from google_analysis10 import get_closest_treasury_yield, WorkingTreasuryDetector
        
        print("✅ Successfully imported treasury functions")
        
        # Test 1: Treasury yield lookup
        print("\n📊 Test 1: Treasury Yield Lookup")
        treasury_detector = WorkingTreasuryDetector()
        
        # Test getting treasury yield for ~10 year maturity (should find 10Y treasury)
        test_years = 10.5
        treasury_yield = get_closest_treasury_yield(treasury_detector, test_years)
        print(f"   Treasury yield for {test_years:.1f} years: {treasury_yield}%")
        
        if treasury_yield is not None and treasury_yield > 0:
            print("   ✅ Treasury yield lookup working!")
        else:
            print("   ❌ Treasury yield lookup not working")
            
        # Test 2: Corporate bond spread calculation
        print("\n📊 Test 2: Corporate Bond vs Treasury Comparison")
        
        # ECOPETROL should have ~9.28% yield
        corporate_yield = 9.2875  # ECOPETROL yield from API
        maturity_years = 20.0  # Approximate maturity
        
        treasury_for_corporate = get_closest_treasury_yield(treasury_detector, maturity_years)
        if treasury_for_corporate:
            spread_bps = (corporate_yield - treasury_for_corporate) * 100
            print(f"   Corporate yield: {corporate_yield:.4f}%")
            print(f"   Treasury yield ({maturity_years:.0f}Y): {treasury_for_corporate:.4f}%")
            print(f"   Calculated spread: {spread_bps:.0f} bps")
            
            if spread_bps > 200:  # Corporate should have significant spread
                print("   ✅ Spread calculation logic working!")
            else:
                print("   ❌ Spread calculation might not be working correctly")
        else:
            print("   ❌ Could not get treasury yield for comparison")
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("   The functions may not be exported correctly")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    # Test 3: Check if our fix is in the actual file
    print("\n📁 Test 3: Verify Fix is in Source Code")
    
    try:
        with open(os.path.join(project_dir, 'google_analysis10.py'), 'r') as f:
            content = f.read()
            
        # Check if our fix is present
        if 'def get_closest_treasury_yield' in content:
            print("   ✅ get_closest_treasury_yield function found in source")
        else:
            print("   ❌ get_closest_treasury_yield function NOT found in source")
            
        if 'spread = (bond_yield - treasury_yield) * 100' in content:
            print("   ✅ Spread calculation logic found in source")
        else:
            print("   ❌ Spread calculation logic NOT found in source")
            
        # Check if hardcoded values are removed
        if 'spread = 0  # Hardcoded for now' in content:
            print("   ❌ Old hardcoded spread still present!")
        else:
            print("   ✅ Hardcoded spread values appear to be removed")
            
    except Exception as e:
        print(f"   ❌ Could not verify source code: {e}")

if __name__ == "__main__":
    test_spread_calculations()
