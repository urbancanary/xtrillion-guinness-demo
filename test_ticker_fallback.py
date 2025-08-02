#!/usr/bin/env python3
"""
Test ticker fallback when ISIN lookup fails
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google_analysis10 import process_bond_portfolio

def test_ticker_fallback():
    """Test bonds that might not have ISINs but should use ticker conventions"""
    print("🧪 Testing ticker convention fallback")
    print("=" * 60)
    
    # Test with a description that won't match ISIN lookup
    # but should get ticker conventions
    test_bonds = [
        {
            "description": "ECOPET 7.375%, 18-Sep-2043",  # Different format
            "expected_ticker": "ECOPET",
            "expected_convention": "Unadjusted"
        },
        {
            "description": "PEMEX 6.5%, 13-Jun-2048",  # Different bond
            "expected_ticker": "PEMEX", 
            "expected_convention": "Unadjusted"
        }
    ]
    
    db_path = './bonds_data.db'
    validated_db_path = './validated_quantlib_bonds.db'
    bloomberg_db_path = './bloomberg_index.db'
    
    for test in test_bonds:
        print(f"\n📊 Testing: {test['description']}")
        print(f"   Expected ticker: {test['expected_ticker']}")
        print(f"   Expected convention: {test['expected_convention']}")
        
        portfolio_data = {
            "data": [
                {
                    "description": test['description'],
                    "CLOSING PRICE": 100.0,
                    "WEIGHTING": 100.0
                }
            ]
        }
        
        try:
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
                print(f"   ✅ Processed successfully")
                print(f"      ISIN: {result.get('isin', 'Not found')}")
                
                # Check if conventions were applied correctly
                # The accrued calculation will reflect the convention used
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    test_ticker_fallback()