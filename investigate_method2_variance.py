#!/usr/bin/env python3
"""
Method 2 Variance Investigation Tool
===================================

Investigates why Direct Local - ISIN (Method 2) shows different results
from the other 5 methods. Method 2 uses SmartBondParser for description
parsing while others use ISIN database lookups.

Key Investigation Areas:
1. Data Source Differences (Database vs SmartBondParser)
2. Convention Differences (Day count, frequency, etc.)
3. Settlement Date Variations
4. Calculation Parameter Differences
"""

import sys
import os

# Add paths
sys.path.append('./core')
sys.path.append('.')

from universal_bond_parser import UniversalBondParser, BondSpecification
from google_analysis10 import process_bonds_with_weightings
from treasury_detector import enhance_bond_processing_with_treasuries
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_prior_month_end():
    """Get prior month end date"""
    today = datetime.now()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    return last_day_previous_month.strftime("%Y-%m-%d")

def investigate_method_differences():
    """Investigate why Method 2 differs from other methods"""
    
    print("🔍 METHOD 2 VARIANCE INVESTIGATION")
    print("=" * 50)
    print("Analyzing why Direct Local - ISIN differs from other methods")
    print()
    
    # Initialize Universal Parser
    parser = UniversalBondParser('bonds_data.db', 'validated_quantlib_bonds.db')
    
    # Test bonds that showed differences in your previous results
    test_bonds = [
        {
            'isin': 'US912810TJ79',
            'description': 'US TREASURY N/B, 3%, 15-Aug-2052',
            'price': 71.66,
            'name': 'US Treasury'
        },
        {
            'isin': 'US698299BL70', 
            'description': 'PANAMA, 3.87%, 23-Jul-2060',
            'price': 56.60,
            'name': 'PANAMA (the problematic one!)'
        },
        {
            'isin': 'XS2249741674',
            'description': 'GALAXY PIPELINE, 3.25%, 30-Sep-2040', 
            'price': 77.88,
            'name': 'Galaxy Pipeline'
        },
        {
            'isin': 'US279158AJ82',
            'description': 'ECOPETROL SA, 5.875%, 28-May-2045',
            'price': 69.31,
            'name': 'Ecopetrol'
        }
    ]
    
    for bond in test_bonds:
        print(f"\n📊 INVESTIGATING: {bond['name']}")
        print("=" * 40)
        
        # Method Simulation (ISIN lookup - what Methods 1,3,4,5,6 do)
        print("🔍 Method 1 (ISIN Database Lookup):")
        spec_isin = parser.parse_bond(bond['isin'], clean_price=bond['price'])
        print(f"   Success: {spec_isin.parsing_success}")
        print(f"   Parser Used: {spec_isin.parser_used}")
        print(f"   Issuer: {spec_isin.issuer}")
        print(f"   Coupon: {spec_isin.coupon_rate}%")
        print(f"   Day Count: {spec_isin.day_count}")
        print(f"   Frequency: {spec_isin.frequency}")
        print(f"   Currency: {spec_isin.currency}")
        
        # Method 2 (Description parsing - SmartBondParser)
        print("\n🔍 Method 2 (Description SmartBondParser):")
        spec_desc = parser.parse_bond(bond['description'], clean_price=bond['price'])
        print(f"   Success: {spec_desc.parsing_success}")
        print(f"   Parser Used: {spec_desc.parser_used}")
        print(f"   Issuer: {spec_desc.issuer}")
        print(f"   Coupon: {spec_desc.coupon_rate}%")
        print(f"   Day Count: {spec_desc.day_count}")
        print(f"   Frequency: {spec_desc.frequency}")
        print(f"   Currency: {spec_desc.currency}")
        
        # Compare the specifications
        print("\n📊 DIFFERENCE ANALYSIS:")
        differences = []
        
        if spec_isin.issuer != spec_desc.issuer:
            differences.append(f"Issuer: '{spec_isin.issuer}' vs '{spec_desc.issuer}'")
        
        if spec_isin.coupon_rate != spec_desc.coupon_rate:
            differences.append(f"Coupon: {spec_isin.coupon_rate}% vs {spec_desc.coupon_rate}%")
            
        if spec_isin.day_count != spec_desc.day_count:
            differences.append(f"Day Count: '{spec_isin.day_count}' vs '{spec_desc.day_count}'")
            
        if spec_isin.frequency != spec_desc.frequency:
            differences.append(f"Frequency: '{spec_isin.frequency}' vs '{spec_desc.frequency}'")
            
        if spec_isin.currency != spec_desc.currency:
            differences.append(f"Currency: '{spec_isin.currency}' vs '{spec_desc.currency}'")
        
        if differences:
            print("   ⚠️  DIFFERENCES FOUND:")
            for diff in differences:
                print(f"      - {diff}")
                
            # Test actual calculation differences
            print("\n🧮 CALCULATION IMPACT TEST:")
            try:
                # Calculate using ISIN specification
                result_isin = calculate_bond_from_spec(spec_isin)
                print(f"   ISIN Method Yield: {result_isin.get('yield', 'N/A')}%")
                
                # Calculate using Description specification  
                result_desc = calculate_bond_from_spec(spec_desc)
                print(f"   Desc Method Yield: {result_desc.get('yield', 'N/A')}%")
                
                if result_isin.get('yield') and result_desc.get('yield'):
                    diff_bps = (result_desc['yield'] - result_isin['yield']) * 100
                    print(f"   📈 Yield Difference: {diff_bps:.2f} basis points")
                    
                    if abs(diff_bps) > 1.0:
                        print(f"   🚨 SIGNIFICANT DIFFERENCE! > 1bp variance")
                        
                        # Identify likely cause
                        if spec_isin.day_count != spec_desc.day_count:
                            print(f"   🎯 LIKELY CAUSE: Day count convention difference")
                        if spec_isin.frequency != spec_desc.frequency:
                            print(f"   🎯 LIKELY CAUSE: Payment frequency difference")
                        if spec_isin.coupon_rate != spec_desc.coupon_rate:
                            print(f"   🎯 LIKELY CAUSE: Coupon rate parsing difference")
                    else:
                        print(f"   ✅ Acceptable variance (< 1bp)")
                        
            except Exception as e:
                print(f"   ❌ Calculation test failed: {e}")
        else:
            print("   ✅ No specification differences found")
            print("   💡 If yield differs, check calculation engine parameters")

def calculate_bond_from_spec(bond_spec: BondSpecification):
    """Calculate bond metrics from BondSpecification"""
    try:
        # Convert to format expected by calculation engine
        bond_input = {
            'isin': bond_spec.isin,
            'description': bond_spec.description or bond_spec.issuer,
            'price': bond_spec.clean_price,
            'settlement_date': bond_spec.settlement_date or get_prior_month_end()
        }
        
        bonds_list = [bond_input]
        enhanced_bonds = enhance_bond_processing_with_treasuries(bonds_list)
        results = process_bonds_with_weightings(enhanced_bonds, use_prior_month_end=True)
        
        return results[0] if results else {}
        
    except Exception as e:
        logger.error(f"Calculation failed: {e}")
        return {}

def deep_dive_panama():
    """Deep dive on PANAMA bond specifically"""
    print("\n🎯 PANAMA BOND DEEP DIVE")
    print("=" * 30)
    print("The bond that was showing 24.511011% vs 7.459882%")
    
    parser = UniversalBondParser('bonds_data.db', 'validated_quantlib_bonds.db')
    
    # Test PANAMA specifically
    panama_isin = 'US698299BL70'
    panama_desc = 'PANAMA, 3.87%, 23-Jul-2060'
    panama_price = 56.60
    
    print(f"\nISIN Input: {panama_isin}")
    spec_isin = parser.parse_bond(panama_isin, clean_price=panama_price)
    
    print(f"Description Input: {panama_desc}")
    spec_desc = parser.parse_bond(panama_desc, clean_price=panama_price)
    
    print("\nPANAMA ISIN Parsing:")
    print(f"   Success: {spec_isin.parsing_success}")
    print(f"   Parser: {spec_isin.parser_used}")
    print(f"   Error: {spec_isin.error_message}")
    
    print("\nPANAMA Description Parsing:")
    print(f"   Success: {spec_desc.parsing_success}")
    print(f"   Parser: {spec_desc.parser_used}")
    print(f"   Error: {spec_desc.error_message}")
    
    if spec_desc.parsing_success:
        print(f"   ✅ SmartBondParser working!")
        print(f"   Issuer: {spec_desc.issuer}")
        print(f"   Coupon: {spec_desc.coupon_rate}%")
        print(f"   Maturity: {spec_desc.maturity_date}")
        
        # Try calculation
        try:
            result = calculate_bond_from_spec(spec_desc)
            yield_val = result.get('yield')
            print(f"   📊 Calculated Yield: {yield_val}%")
            
            if yield_val:
                if 7.0 <= yield_val <= 8.0:
                    print(f"   🎉 PANAMA YIELD LOOKS CORRECT! (~7.46% expected)")
                elif yield_val > 20:
                    print(f"   🚨 PANAMA STILL BROKEN! Yield too high (>20%)")
                else:
                    print(f"   ⚠️  PANAMA yield unusual - verify if correct")
        except Exception as e:
            print(f"   ❌ PANAMA calculation failed: {e}")
    else:
        print(f"   🚨 SmartBondParser failed for PANAMA!")

def main():
    """Main investigation function"""
    print("🚀 METHOD 2 VARIANCE INVESTIGATION TOOL")
    print("=" * 60)
    print("Investigating why Direct Local - ISIN (SmartBondParser) differs")
    print("from ISIN database lookup methods")
    print()
    
    # Change to correct directory
    os.chdir('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')
    
    # Run investigations
    investigate_method_differences()
    deep_dive_panama()
    
    print("\n🎯 INVESTIGATION SUMMARY")
    print("=" * 30)
    print("Key potential causes of Method 2 variance:")
    print("1. 📊 Day Count Convention differences (Database vs SmartBondParser)")
    print("2. 🔄 Payment Frequency differences (Annual vs Semiannual)")
    print("3. 💰 Coupon Rate parsing differences") 
    print("4. 📅 Settlement Date variations")
    print("5. 🏛️ Bond Type classification differences (Treasury vs Corporate)")
    print()
    print("💡 RECOMMENDATION:")
    print("   - Run this investigation before comprehensive 6-way test")
    print("   - Fix any specification differences found")
    print("   - Ensure SmartBondParser uses same conventions as database")

if __name__ == "__main__":
    main()
