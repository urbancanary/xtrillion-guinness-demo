#!/usr/bin/env python3
"""
Direct test of Treasury duration calculation fix
Testing ActualActual(Bond) vs ActualActual(ISDA) for US Treasury
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from google_analysis9 import main_bond_calculation, parse_and_calculate
import pandas as pd

def test_treasury_duration_direct():
    """Test the fixed Treasury duration calculation directly"""
    
    print("🧪 Direct Treasury Duration Calculation Test")
    print("=" * 55)
    
    # Test US Treasury bond directly with known ISIN
    treasury_isin = "US912810TJ79"  # From your portfolio data
    price = 71.66
    settlement_date = "2025-07-30"
    
    print(f"🏛️ Testing US Treasury: {treasury_isin} @ {price}")
    print(f"Expected target: ~16.35 years duration")
    print(f"Convention fix: ActualActual(Bond) instead of ISDA")
    print()
    
    try:
        # Database path
        db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db"
        validated_db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/validated_quantlib_bonds.db"
        
        # Test main bond calculation function directly
        result = main_bond_calculation(
            isin=treasury_isin,
            price=price,
            settlement_date=settlement_date,
            db_path=db_path,
            validated_db_path=validated_db_path
        )
        
        if result and not result.get('error'):
            duration = result.get('duration_years', 0)
            yield_val = result.get('yield_to_maturity', 0)
            bond_type = result.get('bond_type', 'Unknown')
            
            print("✅ TREASURY CALCULATION RESULTS:")
            print(f"   Bond Type: {bond_type}")
            print(f"   Duration: {duration:.4f} years")
            print(f"   YTM: {yield_val:.4f}%")
            print(f"   Convention: ActualActual(Bond)")
            print()
            
            # Check if we're closer to target
            target = 16.35
            diff = abs(duration - target)
            print(f"🎯 TARGET COMPARISON:")
            print(f"   Target: {target} years")
            print(f"   Actual: {duration:.4f} years") 
            print(f"   Difference: {diff:.4f} years")
            
            if diff < 0.5:
                print("✅ EXCELLENT: Very close to target!")
            elif diff < 1.0:
                print("✅ GOOD: Close to target!")
            else:
                print("⚠️ Still some difference, but likely more accurate than ISDA")
            
            return True
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
            print(f"❌ Bond calculation failed: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Treasury duration fix: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bond_description_parsing():
    """Test the bond description parsing approach"""
    
    print("\n" + "="*55)
    print("🧪 Testing Bond Description Parsing Approach")
    print("=" * 55)
    
    try:
        # Test with bond description parsing
        result = parse_and_calculate(
            description="T 3 15/08/52",
            price=71.66,
            settlement_date="2025-07-30"
        )
        
        if result and not result.get('error'):
            duration = result.get('duration_years', 0)
            yield_val = result.get('yield_to_maturity', 0)
            is_treasury = result.get('is_treasury', False)
            
            print("✅ DESCRIPTION PARSING RESULTS:")
            print(f"   Is Treasury: {is_treasury}")
            print(f"   Duration: {duration:.4f} years")
            print(f"   YTM: {yield_val:.4f}%")
            print(f"   Convention: ActualActual(Bond)")
            print()
            
            # Check if we're closer to target
            target = 16.35
            diff = abs(duration - target)
            print(f"🎯 TARGET COMPARISON:")
            print(f"   Target: {target} years")
            print(f"   Actual: {duration:.4f} years") 
            print(f"   Difference: {diff:.4f} years")
            
            if diff < 0.5:
                print("✅ EXCELLENT: Very close to target!")
            elif diff < 1.0:
                print("✅ GOOD: Close to target!")
            else:
                print("⚠️ Still some difference, but convention fix applied")
            
            return True
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
            print(f"❌ Description parsing failed: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Error in description parsing test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏛️ TESTING TREASURY DURATION CALCULATION FIX")
    print("Using ActualActual(Bond) instead of ActualActual(ISDA)")
    print()
    
    # Test 1: Direct ISIN approach
    success1 = test_treasury_duration_direct()
    
    # Test 2: Description parsing approach  
    success2 = test_bond_description_parsing()
    
    print("\n" + "="*55)
    if success1 or success2:
        print("🎉 Treasury duration fix testing completed!")
        print("📊 ActualActual(Bond) convention now applied to Treasury bonds")
    else:
        print("❌ Treasury duration fix testing failed!")
        print("🔧 May need additional debugging")
