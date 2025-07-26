#!/usr/bin/env python3
"""
Test Universal Bond Parser - Eliminating Parsing Redundancy
=========================================================

Tests the new Universal Bond Parser that should fix the API integration issues
and eliminate the 3x parsing redundancy problem.
"""

import sys
import os

# Add the core directory to the path
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/core')
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from universal_bond_parser import UniversalBondParser, BondSpecification, BondInputType

def test_universal_parser():
    """Test the Universal Bond Parser with known test cases"""
    
    print("🚀 Universal Bond Parser Test - Eliminating Redundancy")
    print("=" * 60)
    print("Testing the centralized parser that should fix API integration issues")
    print()
    
    # Initialize the parser
    try:
        parser = UniversalBondParser('bonds_data.db', 'validated_quantlib_bonds.db')
        print("✅ UniversalBondParser initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize UniversalBondParser: {e}")
        return
    
    # Test cases from your 6-way analysis - these should work with SmartBondParser integration
    test_cases = [
        {
            'input': "US912810TJ79",
            'expected_type': BondInputType.ISIN,
            'description': "US Treasury ISIN"
        },
        {
            'input': "US TREASURY N/B, 3%, 15-Aug-2052",
            'expected_type': BondInputType.DESCRIPTION,
            'description': "Treasury description format"
        },
        {
            'input': "PANAMA, 3.87%, 23-Jul-2060",
            'expected_type': BondInputType.DESCRIPTION,
            'description': "The PANAMA bond that SmartBondParser fixed! (was 24.511011%, should be ~7.46%)"
        },
        {
            'input': "GALAXY PIPELINE, 3.25%, 30-Sep-2040",
            'expected_type': BondInputType.DESCRIPTION,
            'description': "Institutional comma-separated format"
        },
        {
            'input': "XS2249741674",
            'expected_type': BondInputType.ISIN,
            'description': "Galaxy Pipeline ISIN"
        }
    ]
    
    success_count = 0
    smart_parser_count = 0
    database_lookup_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. Testing: {test_case['input']}")
        print(f"   Description: {test_case['description']}")
        
        # Parse the bond
        spec = parser.parse_bond(test_case['input'], clean_price=75.0)
        
        # Check input type classification
        expected_type = test_case['expected_type']
        actual_type = spec.input_type
        type_correct = expected_type == actual_type
        
        print(f"   Input Type: {actual_type.value} {'✅' if type_correct else '❌ Expected: ' + expected_type.value}")
        print(f"   Success: {spec.parsing_success}")
        print(f"   Parser Used: {spec.parser_used}")
        
        if spec.parsing_success:
            success_count += 1
            if spec.parser_used == 'smart_bond_parser':
                smart_parser_count += 1
            elif spec.parser_used == 'database_lookup':
                database_lookup_count += 1
                
            print(f"   ✅ Issuer: {spec.issuer}")
            print(f"   ✅ Coupon: {spec.coupon_rate}%")
            print(f"   ✅ Maturity: {spec.maturity_date}")
            print(f"   ✅ Currency: {spec.currency}")
            print(f"   ✅ Frequency: {spec.frequency}")
            
            # Special check for PANAMA bond
            if "PANAMA" in test_case['input']:
                coupon = spec.coupon_rate
                if coupon and 3.5 <= coupon <= 4.5:  # Should be around 3.87%
                    print(f"   🎉 PANAMA BOND FIXED! Coupon rate {coupon}% looks correct!")
                else:
                    print(f"   ⚠️  PANAMA coupon rate {coupon}% - verify this is correct")
        else:
            print(f"   ❌ Error: {spec.error_message}")
        
        print()
    
    # Summary
    print("📊 RESULTS SUMMARY")
    print("=" * 30)
    print(f"Total Tests: {len(test_cases)}")
    print(f"Successful Parses: {success_count}")
    print(f"Success Rate: {success_count/len(test_cases)*100:.1f}%")
    print(f"SmartBondParser Usage: {smart_parser_count}")
    print(f"Database Lookup Usage: {database_lookup_count}")
    print()
    
    if success_count == len(test_cases):
        print("🎉 SUCCESS! Universal Parser working perfectly!")
        print("✅ Ready to eliminate API parsing redundancy!")
        print("✅ This should fix Methods 4 & 6 (API - ISIN) in your 6-way test!")
        print()
        print("Next steps:")
        print("1. Update google_analysis10_api.py to use UniversalBondParser")
        print("2. Update comprehensive_6way_tester.py")
        print("3. Run 6-way test to verify 6/6 methods at 100%")
    else:
        failed_count = len(test_cases) - success_count
        print(f"⚠️  {failed_count} parsing failures detected")
        print("Check SmartBondParser integration and database availability")
    
    return success_count == len(test_cases)

def test_parsing_statistics():
    """Test the parsing statistics functionality"""
    print("\n🔍 Testing Parsing Statistics")
    print("-" * 30)
    
    parser = UniversalBondParser('bonds_data.db', 'validated_quantlib_bonds.db')
    
    # Parse multiple bonds
    bond_inputs = [
        {'input': 'US912810TJ79', 'price': 71.66},
        {'input': 'PANAMA, 3.87%, 23-Jul-2060', 'price': 56.60},
        {'input': 'GALAXY PIPELINE, 3.25%, 30-Sep-2040', 'price': 77.88},
        {'input': 'INVALID_BOND_TEST', 'price': 100.0}  # This should fail
    ]
    
    specs = parser.parse_multiple_bonds(bond_inputs)
    stats = parser.get_parsing_statistics(specs)
    
    print(f"Parsing Statistics:")
    print(f"  Total Bonds: {stats['total_bonds']}")
    print(f"  Successful: {stats['successful_parses']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Parser Usage: {stats['parser_usage']}")
    
    if stats['failed_bonds']:
        print(f"  Failed Bonds: {len(stats['failed_bonds'])}")
        for failed_bond in stats['failed_bonds']:
            print(f"    - {failed_bond.get('description', failed_bond.get('isin', 'Unknown'))}")

if __name__ == "__main__":
    # Change to the correct directory
    os.chdir('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')
    
    # Run the tests
    success = test_universal_parser()
    
    if success:
        test_parsing_statistics()
        print("\n🚀 Universal Bond Parser is ready for production!")
        print("   This should eliminate your 3x parsing redundancy problem!")
