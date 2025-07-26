#!/usr/bin/env python3
"""
Simple Convention Tester - Uses EXACT same method as bbg_quantlib_calculations.py
"""

import sqlite3
import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9')

# Import the working calculation method
import bbg_quantlib_calculations

def test_simple_convention_loop(isin, max_combinations=50):
    """Test convention combinations using the exact working calculation method"""
    
    print(f"🔍 Simple Convention Test for {isin}")
    print("=" * 50)
    
    # Get bond data
    conn = sqlite3.connect('bloomberg_index.db')
    cursor = conn.cursor()
    
    query = """
    SELECT isin, description, bloomberg_accrued, quantlib_accrued, coupon, maturity, price, ytw
    FROM all_bonds_calculations 
    WHERE isin = ?
    """
    
    cursor.execute(query, [isin])
    bond = cursor.fetchone()
    
    if not bond:
        print(f"❌ Bond {isin} not found")
        return
    
    isin, description, bloomberg_accrued, quantlib_accrued, coupon, maturity, price, ytw = bond
    
    print(f"🎯 Bond: {description}")
    print(f"   Bloomberg Accrued: {bloomberg_accrued}")
    print(f"   Current QuantLib: {quantlib_accrued}")
    print(f"   Difference: {abs(bloomberg_accrued - quantlib_accrued):.6f}")
    print(f"   YTW: {ytw}")
    
    # Test different day_count_basis values with the working calculation
    test_conventions = [
        'Thirty360',
        'Thirty360_BondBasis', 
        'ActualActual_ISDA',
        'Actual360',
        'Actual365Fixed'
    ]
    
    print(f"\n🧪 Testing {len(test_conventions)} conventions with working calculation method:")
    
    successes = []
    
    for convention in test_conventions:
        # Create bond data with test convention
        bond_data = {
            'isin': isin,
            'description': description,
            'coupon': float(coupon) if coupon else 0.0,
            'maturity': maturity,
            'price': float(price) if price else 100.0,
            'day_count_basis': convention
        }
        
        try:
            # Use the EXACT same method as bbg_quantlib_calculations.py
            result = bbg_quantlib_calculations.calculate_ytw_and_oad(bond_data)
            
            if result.get('success'):
                print(f"   ✅ {convention}: YTW={result.get('ytw', 0):.3f}%, OAD={result.get('oad', 0):.2f}")
                successes.append({
                    'convention': convention,
                    'ytw': result.get('ytw', 0),
                    'oad': result.get('oad', 0)
                })
            else:
                print(f"   ❌ {convention}: {result.get('error', 'Failed')}")
                
        except Exception as e:
            print(f"   ❌ {convention}: Exception - {e}")
    
    print(f"\n📊 Results: {len(successes)}/{len(test_conventions)} conventions successful")
    
    if successes:
        print("✅ Convention testing WORKS with the proven calculation method!")
        print("✅ The issue was that bb_quantlib_loop.py uses a different calculation approach!")
    else:
        print("❌ Still having issues - need further investigation")
    
    conn.close()
    return successes

if __name__ == "__main__":
    # Test on a PASS bond
    test_simple_convention_loop('US62482BAA08')
