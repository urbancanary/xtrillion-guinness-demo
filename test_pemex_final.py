#!/usr/bin/env python3
"""
Final test of PEMEX bond with proper conventions
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google_analysis10 import process_bond_portfolio

def test_pemex_with_isin():
    """Test PEMEX bond using ISIN to get validated conventions"""
    print("🧪 Testing PEMEX bond with ISIN (should use Unadjusted convention)")
    print("=" * 60)
    
    # Create portfolio data with ISIN
    portfolio_data = {
        "data": [
            {
                "isin": "US71654QDF63",  # PEMEX ISIN
                "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
                "CLOSING PRICE": 100.0,
                "WEIGHTING": 100.0
            }
        ]
    }
    
    # Database paths
    db_path = './bonds_data.db'
    validated_db_path = './validated_quantlib_bonds.db'
    bloomberg_db_path = './bloomberg_index.db'
    
    print("\n📊 Testing with April 18, 2025 (Good Friday)...")
    
    try:
        # Process the bond with explicit settlement date
        results = process_bond_portfolio(
            portfolio_data,
            db_path,
            validated_db_path,
            bloomberg_db_path,
            settlement_days=0,
            settlement_date="2025-04-18"
        )
        
        if len(results) > 0:
            result = results[0]
            
            print("\n📈 Results:")
            print(f"   ISIN: {result.get('isin', 'N/A')}")
            print(f"   Description: {result.get('description', 'N/A')}")
            print(f"   Settlement Date: {result.get('settlement_date', 'N/A')}")
            print(f"   Accrued Interest: {result.get('accrued_interest', 'N/A')}%")
            
            # Calculate accrued per million
            accrued = float(result.get('accrued_interest', 0))
            accrued_per_million = accrued * 10000
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            print("\n💡 Expected from validated DB:")
            print("   Business Convention: Unadjusted")
            print("   Accrued per million: $15,444.44")
            
            # Check if fix worked
            expected_accrued_per_million = 15444.44
            tolerance = 1.0  # Allow $1 tolerance
            
            if abs(accrued_per_million - expected_accrued_per_million) < tolerance:
                print("\n✅ SUCCESS! Bond is using correct Unadjusted convention.")
                return True
            else:
                print("\n❌ Conventions not applied correctly.")
                return False
        else:
            print("❌ No results returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pemex_with_isin()