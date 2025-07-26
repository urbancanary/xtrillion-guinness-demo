#!/usr/bin/env python3
"""
Test the fixed duration calculation code
"""

import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis9 import process_bonds_with_weightings
import json

def test_fixed_treasury_duration():
    print("🎯 Testing FIXED Treasury Duration Calculation")
    print("=" * 50)
    
    # Test with the Treasury bond - use proper format
    bond_data = {
        "data": [
            {
                "isin": "US912810TJ79",
                "price": 71.66,
                "weightings": 1.03,
                "record_number": 1,
                "name": "T 3 15/08/52"
            }
        ]
    }
    
    print("Testing bond: US TREASURY N/B, 3%, 15-Aug-2052")
    print("Price: 71.66")
    print("Expected improvements: More accurate duration with proper conventions")
    print()
    
    try:
        results = process_bonds_with_weightings(
            bond_data, 
            'bonds_data.db', 
            'validated_quantlib_bonds.db'
        )
        
        if results and len(results) > 0:
            result = results[0]
            
            print("📊 FIXED CALCULATION RESULTS:")
            print(f"ISIN: {result.get('isin', 'N/A')}")
            print(f"Yield: {result.get('yield', 'N/A'):.4f}%")
            print(f"Duration: {result.get('duration', 'N/A'):.6f} years")
            print(f"Spread: {result.get('spread', 'N/A'):.0f} bps")
            print(f"Method: {result.get('processing_method', 'N/A')}")
            print()
            
            # Compare with target
            target_duration = 16.35
            calculated_duration = result.get('duration', 0)
            
            if calculated_duration:
                difference = abs(calculated_duration - target_duration)
                print("🎯 COMPARISON:")
                print(f"Target Duration: {target_duration:.2f} years")
                print(f"Calculated Duration: {calculated_duration:.2f} years") 
                print(f"Difference: {difference:.4f} years")
                
                if difference < 0.01:
                    print("✅ SPOT-ON ACCURACY ACHIEVED!")
                elif difference < 0.05:
                    print("✅ EXCELLENT ACCURACY!")
                elif difference < 0.22:
                    print("✅ IMPROVED ACCURACY!")
                else:
                    print("⚠️ Still needs improvement")
            else:
                print("❌ Duration calculation failed")
                
        else:
            print("❌ No results returned")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_treasury_duration()
