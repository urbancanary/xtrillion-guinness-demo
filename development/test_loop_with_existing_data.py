#!/usr/bin/env python3
"""
Quick test of the fixed convention loop logic using existing accrued calculations
"""

import sqlite3
import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9')

def test_convention_loop_with_existing_data(isin):
    """Test convention loop using existing quantlib_accrued data"""
    
    print(f"🔍 Testing Convention Loop with Existing Data for {isin}")
    print("=" * 60)
    
    conn = sqlite3.connect('bloomberg_index.db')
    cursor = conn.cursor()
    
    # Get bond data
    cursor.execute("""
        SELECT isin, description, bloomberg_accrued, quantlib_accrued, ytw, oad, day_count_basis
        FROM all_bonds_calculations 
        WHERE isin = ?
    """, [isin])
    
    bond = cursor.fetchone()
    if not bond:
        print(f"❌ Bond {isin} not found")
        return
    
    isin, description, bloomberg_accrued, quantlib_accrued, ytw, oad, day_count_basis = bond
    
    print(f"🎯 Bond: {description}")
    print(f"   Bloomberg Accrued: {bloomberg_accrued:.6f}")
    print(f"   Current QuantLib: {quantlib_accrued:.6f}")
    print(f"   Difference: {abs(bloomberg_accrued - quantlib_accrued):.6f}")
    print(f"   Current Convention: {day_count_basis}")
    print(f"   Bloomberg YTW: {ytw}")
    
    # Check if this bond passes the current tolerance
    current_diff = abs(bloomberg_accrued - quantlib_accrued)
    tolerance = 0.01
    
    print(f"\n📊 Current Status Analysis:")
    if current_diff <= tolerance:
        print(f"   ✅ CURRENT CONVENTION WORKS: {day_count_basis}")
        print(f"   ✅ Difference ({current_diff:.6f}) ≤ tolerance ({tolerance})")
        print(f"   ✅ This bond doesn't need convention optimization!")
        
        # For working bonds, we can test other conventions for comparison
        print(f"\n🧪 Testing Alternative Conventions for Comparison:")
        test_conventions = ['ActualActual_ISDA', 'Actual360', 'Actual365Fixed']
        
        for test_conv in test_conventions:
            # Temporarily update convention and check if calculation changes
            cursor.execute("UPDATE all_bonds_calculations SET day_count_basis = ? WHERE isin = ?", (test_conv, isin))
            conn.commit()
            
            # For a real test, we'd need to recalculate, but for now just show it's testable
            print(f"   🔧 Would test: {test_conv}")
        
        # Restore original convention
        cursor.execute("UPDATE all_bonds_calculations SET day_count_basis = ? WHERE isin = ?", (day_count_basis, isin))
        conn.commit()
        
    else:
        print(f"   ❌ CURRENT CONVENTION FAILS: {day_count_basis}")
        print(f"   ❌ Difference ({current_diff:.6f}) > tolerance ({tolerance})")
        print(f"   🎯 This bond NEEDS convention optimization!")
        
        print(f"\n🔧 Convention Loop Strategy:")
        print(f"   1. Test different day_count_basis values")
        print(f"   2. For each convention, run the working calculation")
        print(f"   3. Compare results against Bloomberg accrued")
        print(f"   4. Find convention that achieves ≤{tolerance} difference")
    
    print(f"\n💡 KEY INSIGHT:")
    print(f"   The convention loop should use bbg_quantlib_calculations.calculate_comprehensive_enhanced")
    print(f"   on individual bonds with different day_count_basis values, then compare the")
    print(f"   resulting quantlib_accrued against bloomberg_accrued.")
    
    conn.close()

if __name__ == "__main__":
    # Test with a PASS bond first
    test_convention_loop_with_existing_data('US62482BAA08')
    
    print("\n" + "="*60)
    
    # Test with a FAIL bond
    import sqlite3
    conn = sqlite3.connect('bloomberg_index.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT isin FROM all_bonds_calculations 
        WHERE ABS(bloomberg_accrued - quantlib_accrued) > 0.01 
        LIMIT 1
    """)
    fail_bond = cursor.fetchone()
    if fail_bond:
        test_convention_loop_with_existing_data(fail_bond[0])
    conn.close()
