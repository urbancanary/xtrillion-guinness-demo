#!/usr/bin/env python3
"""
Parameter Parsing Debug Test
===========================

Check if your implementation is parsing bond parameters differently
"""

import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis10 import process_bond_portfolio
import logging

# Set up logging to see parameter parsing
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_parameter_parsing():
    """Test what parameters your implementation actually receives"""
    
    print("🔍 PARAMETER PARSING DEBUG TEST")
    print("=" * 60)
    
    # Same test data as comprehensive test
    portfolio_data = {
        "data": [
            {
                "isin": "US912810TJ79",
                "description": "T 3 15/08/52",
                "price": 71.66,
                "weighting": 1.0
            }
        ]
    }
    
    print("📋 INPUT DATA:")
    print(f"   ISIN: {portfolio_data['data'][0]['isin']}")
    print(f"   Description: {portfolio_data['data'][0]['description']}")
    print(f"   Price: {portfolio_data['data'][0]['price']}")
    
    print("\n🔍 RUNNING THROUGH YOUR IMPLEMENTATION...")
    print("-" * 50)
    
    # Let the implementation parse and show debug logs
    results = process_bond_portfolio(
        portfolio_data,
        db_path="/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/portfolio_database.db",
        validated_db_path="/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bloomberg_index.db",
        bloomberg_db_path="/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bloomberg_index.db",
        settlement_date="2025-06-30"
    )
    
    print("\n📊 PARSED RESULTS:")
    if results and len(results) > 0:
        result = results[0]
        print(f"   ISIN: {result.get('isin')}")
        print(f"   Yield: {result.get('yield', 'N/A')}")
        print(f"   Duration: {result.get('duration', 'N/A')}")
        print(f"   Conventions: {result.get('conventions', {})}")
        print(f"   Settlement Date: {result.get('settlement_date_str')}")
        
        print("\n🎯 KEY QUESTION:")
        print("   - Is the yield 4.899718% (correct) or 4.935783% (wrong)?")
        print("   - Is the duration 16.60 (correct) or 10.74 (wrong)?")
        print("   - Are the conventions correct?")
        
        print("\n🔍 EXPECTED vs ACTUAL:")
        print(f"   Expected Yield: 4.899718%")
        print(f"   Actual Yield: {result.get('yield', 'N/A')}")
        print(f"   Expected Duration: 16.600282")
        print(f"   Actual Duration: {result.get('duration', 'N/A')}")
        
        if result.get('yield'):
            yield_diff = abs(result.get('yield') - 4.899718)
            print(f"   Yield Difference: {yield_diff:.6f}")
            
        if result.get('duration'):
            duration_diff = abs(result.get('duration') - 16.600282)
            print(f"   Duration Difference: {duration_diff:.6f}")
            
    else:
        print("❌ NO RESULTS RETURNED")

if __name__ == "__main__":
    test_parameter_parsing()
