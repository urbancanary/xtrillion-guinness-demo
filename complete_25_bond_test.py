#!/usr/bin/env python3
"""
Complete 25-Bond Test Suite
=========================

Test all 25 bonds using the new Treasury override system.
Expects 24/25 or 25/25 perfect matches between ISIN and description parsing.
"""

import sys
import logging
import json
from datetime import datetime
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

def get_test_bonds():
    """Return the 25 test bonds"""
    return [
        {"isin": "US912810TJ79", "price": 71.66, "name": "T 3 15/08/52", "duration": 16.357839, "yield": 4.898453},
        {"isin": "XS2249741674", "price": 77.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "duration": 10.097620, "yield": 5.637570},
        {"isin": "XS1709535097", "price": 89.40, "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "duration": 9.815219, "yield": 5.717451},
        {"isin": "XS1982113463", "price": 87.14, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "duration": 9.927596, "yield": 5.599746},
        {"isin": "USP37466AS18", "price": 80.39, "name": "EMPRESA METRO, 4.7%, 07-May-2050", "duration": 13.189567, "yield": 6.265800},
        {"isin": "USP3143NAH72", "price": 101.63, "name": "CODELCO INC, 6.15%, 24-Oct-2036", "duration": 8.024166, "yield": 5.949058},
        {"isin": "USP30179BR86", "price": 86.42, "name": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "duration": 11.583500, "yield": 7.442306},
        {"isin": "US195325DX04", "price": 52.71, "name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "duration": 12.975798, "yield": 7.836133},
        {"isin": "US279158AJ82", "price": 69.31, "name": "ECOPETROL SA, 5.875%, 28-May-2045", "duration": 9.812703, "yield": 9.282266},
        {"isin": "USP37110AM89", "price": 76.24, "name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", "duration": 12.389556, "yield": 6.542351},
        {"isin": "XS2542166231", "price": 103.03, "name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", "duration": 7.207705, "yield": 5.720213},
        {"isin": "XS2167193015", "price": 64.50, "name": "STATE OF ISRAEL, 3.8%, 13-May-2060", "duration": 15.269052, "yield": 6.337460},
        {"isin": "XS1508675508", "price": 82.42, "name": "SAUDI INT BOND, 4.5%, 26-Oct-2046", "duration": 12.598517, "yield": 5.967150},
        {"isin": "XS1807299331", "price": 92.21, "name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", "duration": 11.446459, "yield": 7.059957},
        {"isin": "US91086QAZ19", "price": 78.00, "name": "UNITED MEXICAN, 5.75%, 12-Oct-2110", "duration": 13.370728, "yield": 7.374879},
        {"isin": "USP6629MAD40", "price": 82.57, "name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", "duration": 11.382487, "yield": 7.070132},
        {"isin": "US698299BL70", "price": 56.60, "name": "PANAMA, 3.87%, 23-Jul-2060", "duration": 13.488582, "yield": 7.362747},
        {"isin": "US71654QDF63", "price": 71.42, "name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "duration": 9.719713, "yield": 9.875691},
        {"isin": "US71654QDE98", "price": 89.55, "name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "duration": 4.469801, "yield": 8.324595},
        {"isin": "XS2585988145", "price": 85.54, "name": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "duration": 13.327227, "yield": 6.228001},
        {"isin": "XS1959337749", "price": 89.97, "name": "QATAR STATE OF, 4.817%, 14-Mar-2049", "duration": 13.261812, "yield": 5.584981},
        {"isin": "XS2233188353", "price": 99.23, "name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "duration": 0.225205, "yield": 5.015259},
        {"isin": "XS2359548935", "price": 73.79, "name": "QATAR ENERGY, 3.125%, 12-Jul-2041", "duration": 11.512115, "yield": 5.628065},
        {"isin": "XS0911024635", "price": 93.29, "name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "duration": 11.237819, "yield": 5.663334},
        {"isin": "USP0R80BAG79", "price": 97.26, "name": "SITIOS, 5.375%, 04-Apr-2032", "duration": 5.514383, "yield": 5.870215}
    ]

def test_single_bond(parser, bond_data, test_number):
    """Test a single bond with both ISIN and description"""
    
    print(f"\n{'='*100}")
    print(f"🧪 Test {test_number}/25: {bond_data['name']}")
    print(f"   ISIN: {bond_data['isin']}")
    print(f"   Price: {bond_data['price']}")
    print(f"   Expected Yield: {bond_data['yield']}")
    print(f"{'='*100}")
    
    results = {}
    
    # Test 1: ISIN parsing
    try:
        isin_result = parser.parse_bond(bond_data['isin'])
        results['isin'] = {
            'success': getattr(isin_result, 'parsing_success', False),
            'parser_used': getattr(isin_result, 'parser_used', 'N/A'),
            'treasury_override': getattr(isin_result, 'treasury_override_applied', False),
            'day_count': isin_result.day_count,
            'frequency': isin_result.frequency,
            'business_convention': isin_result.business_convention,
            'coupon': isin_result.coupon_rate,
            'maturity': isin_result.maturity_date,
            'currency': isin_result.currency,
            'error': getattr(isin_result, 'error_message', None)
        }
        
        if results['isin']['success']:
            print(f"✅ ISIN Parsing Success")
            print(f"   Parser: {results['isin']['parser_used']}")
            print(f"   Treasury Override: {results['isin']['treasury_override']}")
            print(f"   Conventions: {results['isin']['day_count']}, {results['isin']['frequency']}")
            print(f"   Coupon: {results['isin']['coupon']}, Maturity: {results['isin']['maturity']}")
        else:
            print(f"❌ ISIN Parsing Failed: {results['isin']['error']}")
            
    except Exception as e:
        print(f"❌ ISIN Parsing Error: {e}")
        results['isin'] = {'success': False, 'error': str(e)}
    
    # Test 2: Description parsing
    try:
        desc_result = parser.parse_bond(bond_data['name'])
        results['description'] = {
            'success': getattr(desc_result, 'parsing_success', False),
            'parser_used': getattr(desc_result, 'parser_used', 'N/A'),
            'treasury_override': getattr(desc_result, 'treasury_override_applied', False),
            'day_count': desc_result.day_count,
            'frequency': desc_result.frequency,
            'business_convention': desc_result.business_convention,
            'coupon': desc_result.coupon_rate,
            'maturity': desc_result.maturity_date,
            'currency': desc_result.currency,
            'error': getattr(desc_result, 'error_message', None)
        }
        
        if results['description']['success']:
            print(f"✅ Description Parsing Success")
            print(f"   Parser: {results['description']['parser_used']}")
            print(f"   Treasury Override: {results['description']['treasury_override']}")
            print(f"   Conventions: {results['description']['day_count']}, {results['description']['frequency']}")
            print(f"   Coupon: {results['description']['coupon']}, Maturity: {results['description']['maturity']}")
        else:
            print(f"❌ Description Parsing Failed: {results['description']['error']}")
            
    except Exception as e:
        print(f"❌ Description Parsing Error: {e}")
        results['description'] = {'success': False, 'error': str(e)}
    
    # Compare results
    comparison_result = compare_parsing_results(results, bond_data)
    
    return results, comparison_result

def compare_parsing_results(results, bond_data):
    """Compare ISIN vs Description parsing results"""
    
    print(f"\n🔍 COMPARISON ANALYSIS:")
    
    isin_success = results.get('isin', {}).get('success', False)
    desc_success = results.get('description', {}).get('success', False)
    
    if not isin_success and not desc_success:
        print(f"   ❌ BOTH PARSING METHODS FAILED")
        return {"status": "both_failed", "match": False}
    
    if not isin_success:
        print(f"   ⚠️  ISIN parsing failed, Description succeeded")
        return {"status": "isin_failed", "match": False}
    
    if not desc_success:
        print(f"   ⚠️  Description parsing failed, ISIN succeeded")
        return {"status": "description_failed", "match": False}
    
    # Both succeeded - compare conventions
    isin_data = results['isin']
    desc_data = results['description']
    
    conventions_match = (
        isin_data['day_count'] == desc_data['day_count'] and
        isin_data['frequency'] == desc_data['frequency'] and
        isin_data['business_convention'] == desc_data['business_convention']
    )
    
    basic_data_match = (
        str(isin_data['coupon']) == str(desc_data['coupon']) and
        isin_data['maturity'] == desc_data['maturity']
    )
    
    if conventions_match and basic_data_match:
        print(f"   ✅ PERFECT MATCH!")
        print(f"      Conventions: {isin_data['day_count']}, {isin_data['frequency']}, {isin_data['business_convention']}")
        print(f"      Bond Data: Coupon {isin_data['coupon']}, Maturity {isin_data['maturity']}")
        
        # Check Treasury override status
        if isin_data['treasury_override'] or desc_data['treasury_override']:
            print(f"      🏛️ Treasury override applied (ISIN: {isin_data['treasury_override']}, DESC: {desc_data['treasury_override']})")
        
        return {"status": "perfect_match", "match": True}
    
    else:
        print(f"   ❌ MISMATCH DETECTED!")
        
        if not conventions_match:
            print(f"      Convention differences:")
            print(f"        ISIN: {isin_data['day_count']}, {isin_data['frequency']}, {isin_data['business_convention']}")
            print(f"        DESC: {desc_data['day_count']}, {desc_data['frequency']}, {desc_data['business_convention']}")
        
        if not basic_data_match:
            print(f"      Bond data differences:")
            print(f"        ISIN: Coupon {isin_data['coupon']}, Maturity {isin_data['maturity']}")
            print(f"        DESC: Coupon {desc_data['coupon']}, Maturity {desc_data['maturity']}")
        
        return {"status": "mismatch", "match": False, "conventions_match": conventions_match, "data_match": basic_data_match}

def run_complete_25_bond_test():
    """Run the complete 25-bond test suite"""
    
    try:
        from core.universal_bond_parser import UniversalBondParser
        
        print("🚀 Starting Complete 25-Bond Test Suite")
        print("=" * 100)
        print("Testing ISIN vs Description parsing with Treasury override system")
        print("Expected: 24/25 or 25/25 perfect matches")
        
        parser = UniversalBondParser(
            './bonds_data.db',
            './validated_quantlib_bonds.db',
            './bloomberg_index.db'
        )
        
        bonds = get_test_bonds()
        
        # Track results
        summary = {
            'total_bonds': len(bonds),
            'perfect_matches': 0,
            'mismatches': 0,
            'parsing_failures': 0,
            'treasury_bonds': 0,
            'detailed_results': []
        }
        
        # Test each bond
        for i, bond in enumerate(bonds, 1):
            try:
                results, comparison = test_single_bond(parser, bond, i)
                
                # Update summary
                if comparison['match']:
                    summary['perfect_matches'] += 1
                elif comparison['status'] in ['both_failed', 'isin_failed', 'description_failed']:
                    summary['parsing_failures'] += 1
                else:
                    summary['mismatches'] += 1
                
                # Check if Treasury override was applied
                if (results.get('isin', {}).get('treasury_override', False) or 
                    results.get('description', {}).get('treasury_override', False)):
                    summary['treasury_bonds'] += 1
                
                # Store detailed results
                summary['detailed_results'].append({
                    'bond': bond,
                    'results': results,
                    'comparison': comparison
                })
                
            except Exception as e:
                print(f"❌ Failed to test bond {i}: {e}")
                summary['parsing_failures'] += 1
        
        # Print final summary
        print_final_summary(summary)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"complete_25_bond_test_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\n📁 Detailed results saved to: {filename}")
        
        return summary
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

def print_final_summary(summary):
    """Print the final test summary"""
    
    print(f"\n{'='*100}")
    print(f"🎯 FINAL TEST SUMMARY")
    print(f"{'='*100}")
    
    print(f"📊 Overall Results:")
    print(f"   Total Bonds Tested: {summary['total_bonds']}")
    print(f"   ✅ Perfect Matches: {summary['perfect_matches']}/{summary['total_bonds']}")
    print(f"   ❌ Mismatches: {summary['mismatches']}")
    print(f"   💥 Parsing Failures: {summary['parsing_failures']}")
    print(f"   🏛️ Treasury Bonds (Override Applied): {summary['treasury_bonds']}")
    
    success_rate = (summary['perfect_matches'] / summary['total_bonds']) * 100
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 96:  # 24/25 or better
        print(f"🎉 EXCELLENT! Achieved expected 24/25+ perfect matches!")
    elif success_rate >= 90:
        print(f"✅ GOOD! Close to target - investigate remaining mismatches")
    else:
        print(f"⚠️  NEEDS IMPROVEMENT - investigate parsing issues")
    
    # List any mismatches for investigation
    if summary['mismatches'] > 0 or summary['parsing_failures'] > 0:
        print(f"\n🔍 Issues to Investigate:")
        for i, result in enumerate(summary['detailed_results'], 1):
            if not result['comparison']['match']:
                bond = result['bond']
                status = result['comparison']['status']
                print(f"   {i}. {bond['isin']} - {bond['name'][:50]}... ({status})")

if __name__ == "__main__":
    print(f"🧪 Complete 25-Bond Test Suite with Treasury Override")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    summary = run_complete_25_bond_test()
    
    print(f"\n🎯 TEST COMPLETE!")
    print(f"Expected: Treasury override eliminates fractional yield differences")
    print(f"Target: 24/25 or 25/25 perfect convention matches")
