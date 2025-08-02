#!/usr/bin/env python3
"""
Test the exact process_bond_portfolio call to see what it returns
"""

import sys
import os
sys.path.append('.')

from google_analysis10 import process_bond_portfolio
from datetime import datetime
import json

def test_portfolio_function_directly():
    """Test process_bond_portfolio directly to see spread output"""
    
    # Exact parameters like production API
    portfolio_data = {
        'data': [
            {
                'BOND_CD': 'ECOPETROL SA, 5.875%, 28-May-2045',
                'CLOSING PRICE': 69.31,
                'WEIGHTING': 100.0
            }
        ]
    }
    
    db_path = './bonds_data.db'
    validated_db_path = './validated_quantlib_bonds.db'
    bloomberg_db_path = './bloomberg_index.db'
    settlement_date = '2025-07-31'
    
    print("🧪 Testing process_bond_portfolio directly...")
    print(f"📊 Bond: ECOPETROL SA, 5.875%, 28-May-2045")
    print(f"💰 Price: 69.31")
    print(f"📅 Settlement: {settlement_date}")
    
    try:
        results = process_bond_portfolio(
            portfolio_data=portfolio_data,
            db_path=db_path,
            validated_db_path=validated_db_path,
            bloomberg_db_path=bloomberg_db_path,
            settlement_days=0,
            settlement_date=settlement_date
        )
        
        print(f"\n📋 Results type: {type(results)}")
        print(f"📋 Results length: {len(results) if hasattr(results, '__len__') else 'N/A'}")
        
        if results:
            first_result = results[0]
            print(f"\n🔍 First result keys: {list(first_result.keys()) if isinstance(first_result, dict) else 'Not a dict'}")
            
            # Focus on spread-related fields
            spread_fields = {}
            for key, value in first_result.items():
                if 'spread' in key.lower() or key in ['g_spread', 'z_spread', 'spread']:
                    spread_fields[key] = value
            
            print(f"💰 Spread-related fields: {spread_fields}")
            
            # Also check other key fields
            key_fields = ['ytm', 'duration', 'spread', 'yield', 'success', 'error']
            for field in key_fields:
                if field in first_result:
                    print(f"🔑 {field}: {first_result[field]}")
        else:
            print("❌ No results returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_portfolio_function_directly()
