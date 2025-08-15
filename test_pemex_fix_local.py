#!/usr/bin/env python3
"""
Test PEMEX bond fix locally
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google_analysis10 import process_bonds_with_weightings
import pandas as pd
from datetime import datetime

def test_pemex_local():
    """Test PEMEX bond calculation with the fix"""
    print("🧪 Testing PEMEX bond fix locally")
    print("=" * 60)
    
    # Create portfolio data in the format expected by process_bonds_with_weightings
    portfolio_data = {
        "data": [
            {
                "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
                "CLOSING PRICE": 100.0,
                "WEIGHTING": 100.0,
                "Inventory Date": "2025/04/21"
            }
        ]
    }
    
    # Database paths
    db_path = './bonds_data.db'
    validated_db_path = './validated_quantlib_bonds.db'
    
    print("📊 Processing PEMEX bond...")
    
    try:
        # Process the bond
        results = process_bonds_with_weightings(
            portfolio_data,
            db_path,
            validated_db_path=validated_db_path
        )
        
        if len(results) > 0:
            result = results.iloc[0]
            
            print("\n📈 Results:")
            print(f"   Description: {result.get('description', 'N/A')}")
            print(f"   Yield: {result.get('yield', 'N/A')}%")
            print(f"   Duration: {result.get('duration', 'N/A')} years")
            print(f"   Accrued Interest: {result.get('accrued_interest', 'N/A')}%")
            
            # Calculate accrued per million
            accrued = float(result.get('accrued_interest', 0))
            accrued_per_million = accrued * 10000
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            print("\n💡 Expected values:")
            print("   Accrued interest: 1.602361%")
            print("   Accrued per million: $16,023.61")
            
            # Check if fix worked
            if abs(accrued_per_million - 16023.61) < 1.0:
                print("\n✅ FIX SUCCESSFUL! Values match expected.")
            else:
                print("\n❌ Fix not working correctly.")
        else:
            print("❌ No results returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pemex_local()