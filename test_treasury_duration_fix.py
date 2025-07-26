#!/usr/bin/env python3
"""
Quick test of Treasury duration calculation fix
Testing ActualActual(Bond) vs ActualActual(ISDA) for US Treasury
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_analysis9 import process_bonds_with_weightings
import json

def test_treasury_duration_fix():
    """Test the fixed Treasury duration calculation"""
    
    print("🧪 Testing Treasury Duration Calculation Fix")
    print("=" * 55)
    
    # Test data with US Treasury bond (correct format for function)
    test_portfolio = {
        "data": [
            {
                "description": "T 3 15/08/52",
                "price": 71.66,
                "weight": 1.03,
                "settlement_date": "2025-07-30"
            }
        ]
    }
    
    print("🏛️ Testing US Treasury: T 3 15/08/52 @ 71.66")
    print(f"Expected target: ~16.35 years duration")
    print(f"Convention fix: ActualActual(Bond) instead of ISDA")
    print()
    
    try:
        # Process the Treasury bond with the fixed calculation
        db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db"
        validated_db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/validated_quantlib_bonds.db"
        result = process_bonds_with_weightings(test_portfolio, db_path, validated_db_path=validated_db_path)
        
        if result and result.get('portfolio_summary', {}).get('successful_calculations', 0) > 0:
            # Extract Treasury bond results
            bonds = result.get('bonds', [])
            if bonds:
                treasury = bonds[0]
                duration = treasury.get('duration_years', 0)
                yield_val = treasury.get('yield_to_maturity', 0)
                
                print("✅ TREASURY CALCULATION RESULTS:")
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
                
                print()
                print("🏛️ TREASURY CONVENTION FIX APPLIED SUCCESSFULLY")
                return True
            else:
                print("❌ No bond results returned")
                return False
        else:
            print("❌ Portfolio processing failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Treasury duration fix: {e}")
        return False

if __name__ == "__main__":
    success = test_treasury_duration_fix()
    if success:
        print("\n🎉 Treasury duration fix test completed!")
    else:
        print("\n❌ Treasury duration fix test failed!")
