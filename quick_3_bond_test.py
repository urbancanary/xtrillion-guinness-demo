#!/usr/bin/env python3
"""
QUICK 3-BOND TEST - Database Path Fix Verification
=================================================

Tests 3 bonds to verify the database path fix works before running all 25.
"""

import sys
import os
sys.path.append('.')

from comprehensive_6way_tester import ComprehensiveBondTester

def quick_test():
    print("🧪 QUICK 3-BOND TEST - Database Path Fix Verification")
    print("=" * 70)
    
    # Test with just 3 bonds
    test_bonds = [
        {"isin": "US912810TJ79", "price": 71.66, "weighting": 8.09, "description": "US TREASURY N/B, 3%, 15-Aug-2052"},
        {"isin": "XS2249741674", "price": 77.88, "weighting": 3.88, "description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
        {"isin": "XS1709535097", "price": 89.40, "weighting": 4.12, "description": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"}
    ]
    
    # Initialize tester
    tester = ComprehensiveBondTester(local_api_url="http://localhost:8080")
    
    print(f"\n🚀 Testing {len(test_bonds)} bonds to verify database connectivity...")
    
    # Test with corrected settlement date
    settlement_date = "2025-06-30"
    results = tester.test_all_bonds(test_bonds, settlement_date=settlement_date)
    
    print(f"\n✅ QUICK TEST COMPLETED!")
    
    # Quick analysis
    success_count = 0
    total_tests = 0
    
    for isin, bond_result in results.items():
        for method_key, result in bond_result.get("results", {}).items():
            total_tests += 1
            if result.get("status") == "success":
                success_count += 1
    
    success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 QUICK RESULTS:")
    print(f"   • Tests Run: {total_tests}")
    print(f"   • Successful: {success_count}")
    print(f"   • Success Rate: {success_rate:.1f}%")
    
    if success_rate > 50:
        print(f"   ✅ Database connectivity FIXED! Ready for full 25-bond test.")
    elif success_rate > 0:
        print(f"   ⚠️  Partial success - some methods working, investigate remaining issues.")
    else:
        print(f"   ❌ Still failing - need further debugging.")
    
    return tester, results

if __name__ == "__main__":
    tester, results = quick_test()
