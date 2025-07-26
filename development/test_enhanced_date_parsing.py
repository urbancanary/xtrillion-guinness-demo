#!/usr/bin/env python3
"""
Test the enhanced date parsing fix
"""

import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9')

from calculators.bond_calculation_registry import get_working_accrued_calculation

def test_date_formats():
    """Test various date formats to ensure parsing works"""
    
    print("🧪 TESTING ENHANCED DATE PARSING")
    print("="*60)
    
    # Get the working calculation function
    calc_func = get_working_accrued_calculation()
    
    # Test cases with different date formats
    test_cases = [
        {
            "name": "YYYY-MM-DD format (QuantLib database style)",
            "isin": "US71654QDD16",
            "coupon": 7.69,
            "maturity": "2050-01-23",  # ISO format
            "settlement": "2025-04-18"
        },
        {
            "name": "MM/DD/YY format (Bloomberg Excel style)",
            "isin": "US71654QDD16", 
            "coupon": 7.69,
            "maturity": "01/23/50",  # Excel format
            "settlement": "04/18/25"
        },
        {
            "name": "MM/DD/YYYY format (Full year Excel)",
            "isin": "US71654QDD16",
            "coupon": 7.69,
            "maturity": "01/23/2050",  # Full year Excel format
            "settlement": "04/18/2025"
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n📝 Testing: {test['name']}")
        print(f"   Maturity: {test['maturity']}")
        print(f"   Settlement: {test['settlement']}")
        
        try:
            result = calc_func(
                test['isin'], 
                test['coupon'], 
                test['maturity'], 
                test['settlement']
            )
            
            if result['success']:
                accrued = result['accrued_per_million']
                print(f"   ✅ SUCCESS: Accrued = ${accrued:,.2f} per $1M")
                print(f"   📅 Last Coupon: {result['last_coupon_date']}")
                print(f"   📅 Next Coupon: {result['next_coupon_date']}")
                print(f"   📊 Days Accrued: {result['days_accrued']}")
                
                results.append({
                    'test': test['name'],
                    'success': True,
                    'accrued': accrued,
                    'last_coupon': result['last_coupon_date'],
                    'days_accrued': result['days_accrued']
                })
            else:
                print(f"   ❌ FAILED: {result['error']}")
                results.append({
                    'test': test['name'],
                    'success': False,
                    'error': result['error']
                })
                
        except Exception as e:
            print(f"   💥 EXCEPTION: {e}")
            results.append({
                'test': test['name'],
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY OF DATE PARSING TESTS")
    print("="*60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print("\n🎯 SUCCESSFUL TESTS:")
        for result in successful:
            print(f"   ✅ {result['test']}")
            print(f"      Accrued: ${result['accrued']:,.2f} per $1M")
            print(f"      Last Coupon: {result['last_coupon']}")
            print(f"      Days Accrued: {result['days_accrued']}")
    
    if failed:
        print("\n❌ FAILED TESTS:")
        for result in failed:
            print(f"   ❌ {result['test']}")
            print(f"      Error: {result['error']}")
    
    # Consistency check
    if len(successful) > 1:
        print("\n🔍 CONSISTENCY CHECK:")
        base_accrued = successful[0]['accrued']
        base_days = successful[0]['days_accrued']
        
        all_consistent = True
        for result in successful[1:]:
            if abs(result['accrued'] - base_accrued) > 0.01:
                print(f"   ⚠️  INCONSISTENT ACCRUED: {result['test']} = ${result['accrued']:,.2f} vs ${base_accrued:,.2f}")
                all_consistent = False
            if result['days_accrued'] != base_days:
                print(f"   ⚠️  INCONSISTENT DAYS: {result['test']} = {result['days_accrued']} vs {base_days}")
                all_consistent = False
        
        if all_consistent:
            print("   ✅ ALL RESULTS CONSISTENT - Date parsing is working correctly!")
        else:
            print("   ❌ INCONSISTENT RESULTS - Date parsing needs adjustment")
    
    return len(failed) == 0

if __name__ == "__main__":
    success = test_date_formats()
    
    if success:
        print("\n🎉 ALL DATE FORMAT TESTS PASSED!")
        print("✅ Enhanced date parsing is working correctly")
        print("✅ Ready to fix pemex_calculations vs validated_calculations discrepancy")
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("❌ Date parsing needs more work")
    
    print("\n" + "="*60)
