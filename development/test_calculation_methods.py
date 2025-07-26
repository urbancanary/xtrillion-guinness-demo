#!/usr/bin/env python3
"""
Simple test to confirm the difference between the two calculation methods
"""

import sqlite3
import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9')

# Import both calculation methods
import bbg_quantlib_calculations
from calculators.bond_calculation_registry import get_working_accrued_calculation

def test_calculation_methods():
    """Test the difference between main calculator and loop calculator"""
    
    print("🔍 Testing Calculation Method Differences")
    print("=" * 50)
    
    # Get a PASS bond
    conn = sqlite3.connect('bloomberg_index.db')
    cursor = conn.cursor()
    
    query = """
    SELECT isin, description, bloomberg_accrued, quantlib_accrued, coupon, maturity, price, day_count_basis
    FROM all_bonds_calculations 
    WHERE match_status = 'PASS' AND bloomberg_accrued > 0 
    LIMIT 1
    """
    
    cursor.execute(query)
    bond = cursor.fetchone()
    
    if bond:
        isin, description, bloomberg_accrued, quantlib_accrued, coupon, maturity, price, day_count_basis = bond
        
        print(f"🎯 Test Bond: {isin}")
        print(f"   Description: {description}")
        print(f"   Bloomberg Accrued: {bloomberg_accrued}")
        print(f"   Current QuantLib Accrued: {quantlib_accrued}")
        print(f"   Convention: {day_count_basis}")
        
        # Create bond data
        bond_data = {
            'isin': isin,
            'description': description,
            'coupon': float(coupon) if coupon else 0.0,
            'maturity': maturity,
            'price': float(price) if price else 100.0,
            'day_count_basis': day_count_basis
        }
        
        print(f"\n🧪 Method 1: bbg_quantlib_calculations.calculate_ytw_and_oad")
        try:
            result1 = bbg_quantlib_calculations.calculate_ytw_and_oad(bond_data)
            print(f"   Result: {result1}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print(f"\n🧪 Method 2: get_working_accrued_calculation (used by loop)")
        try:
            # This is what the loop uses internally
            result2 = get_working_accrued_calculation(bond_data)
            print(f"   Result: {result2}")
        except Exception as e:
            print(f"   Error: {e}")
            
        print(f"\n💡 SOLUTION:")
        print(f"   The loop should use the same method as bbg_quantlib_calculations.py")
        print(f"   instead of get_working_accrued_calculation from the registry.")
    
    conn.close()

if __name__ == "__main__":
    test_calculation_methods()
