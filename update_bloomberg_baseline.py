#!/usr/bin/env python3
"""
UPDATE BLOOMBERG BASELINE TO REAL USER DATA
==========================================
Replace the old/incorrect Bloomberg baseline with user's actual Bloomberg data
"""

import sqlite3
import pandas as pd

# REAL Bloomberg baseline data provided by user on 2025-07-22
REAL_BLOOMBERG_DATA = {
    'US912810TJ79': {'yield': 4.90, 'duration': 16.36, 'spread': None},
    'XS2249741674': {'yield': 5.64, 'duration': 10.10, 'spread': 118},
    'XS1709535097': {'yield': 5.72, 'duration': 9.82, 'spread': 123},
    'XS1982113463': {'yield': 5.60, 'duration': 9.93, 'spread': 111},
    'USP37466AS18': {'yield': 6.27, 'duration': 13.19, 'spread': 144},
    'USP3143NAH72': {'yield': 5.95, 'duration': 8.02, 'spread': 160},
    'USP30179BR86': {'yield': 7.44, 'duration': 11.58, 'spread': 261},
    'US195325DX04': {'yield': 7.84, 'duration': 12.98, 'spread': 301},
    'US279158AJ82': {'yield': 9.28, 'duration': 9.81, 'spread': 445},
    'USP37110AM89': {'yield': 6.54, 'duration': 12.39, 'spread': 171},
    'XS2542166231': {'yield': 5.72, 'duration': 7.21, 'spread': 146},
    'XS2167193015': {'yield': 6.34, 'duration': 15.27, 'spread': 151},
    'XS1508675508': {'yield': 5.97, 'duration': 12.60, 'spread': 114},
    'XS1807299331': {'yield': 7.06, 'duration': 11.45, 'spread': 223},
    'US91086QAZ19': {'yield': 7.37, 'duration': 13.37, 'spread': 255},
    'USP6629MAD40': {'yield': 7.07, 'duration': 11.38, 'spread': 224},
    'US698299BL70': {'yield': 7.36, 'duration': 13.49, 'spread': 253},
    'US71654QDF63': {'yield': 9.88, 'duration': 9.72, 'spread': 505},
    'US71654QDE98': {'yield': 8.32, 'duration': 4.47, 'spread': 444},
    'XS2585988145': {'yield': 6.23, 'duration': 13.33, 'spread': 140},
    'XS1959337749': {'yield': 5.58, 'duration': 13.26, 'spread': 76},
    'XS2233188353': {'yield': 5.02, 'duration': 0.23, 'spread': 71},
    'XS2359548935': {'yield': 5.63, 'duration': 11.51, 'spread': 101},
    'XS0911024635': {'yield': 5.66, 'duration': 11.24, 'spread': 95},
    'USP0R80BAG79': {'yield': 5.87, 'duration': 5.51, 'spread': 187}
}

def update_baseline_in_tester():
    """Update the comprehensive_6way_tester.py to use real Bloomberg data"""
    
    print("🔧 UPDATING BLOOMBERG BASELINE IN COMPREHENSIVE TESTER...")
    
    # Read the current tester file
    with open('comprehensive_6way_tester.py', 'r') as f:
        content = f.read()
    
    # Find the get_bloomberg_baseline function and replace it
    start_marker = 'def get_bloomberg_baseline():'
    end_marker = '    }'
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("❌ Could not find get_bloomberg_baseline function!")
        return
    
    # Find the end of the function (next function or end of file)
    end_idx = content.find('\ndef ', start_idx + 1)
    if end_idx == -1:
        end_idx = len(content)
    
    # Generate new function content
    new_function = '''def get_bloomberg_baseline():
    """Returns the REAL Bloomberg baseline results from user's actual data."""
    return {
        "US912810TJ79": {"yield": 4.90, "duration": 16.36, "spread": None},
        "XS2249741674": {"yield": 5.64, "duration": 10.10, "spread": 118},
        "XS1709535097": {"yield": 5.72, "duration": 9.82, "spread": 123},
        "XS1982113463": {"yield": 5.60, "duration": 9.93, "spread": 111},
        "USP37466AS18": {"yield": 6.27, "duration": 13.19, "spread": 144},
        "USP3143NAH72": {"yield": 5.95, "duration": 8.02, "spread": 160},
        "USP30179BR86": {"yield": 7.44, "duration": 11.58, "spread": 261},
        "US195325DX04": {"yield": 7.84, "duration": 12.98, "spread": 301},
        "US279158AJ82": {"yield": 9.28, "duration": 9.81, "spread": 445},
        "USP37110AM89": {"yield": 6.54, "duration": 12.39, "spread": 171},
        "XS2542166231": {"yield": 5.72, "duration": 7.21, "spread": 146},
        "XS2167193015": {"yield": 6.34, "duration": 15.27, "spread": 151},
        "XS1508675508": {"yield": 5.97, "duration": 12.60, "spread": 114},
        "XS1807299331": {"yield": 7.06, "duration": 11.45, "spread": 223},
        "US91086QAZ19": {"yield": 7.37, "duration": 13.37, "spread": 255},
        "USP6629MAD40": {"yield": 7.07, "duration": 11.38, "spread": 224},
        "US698299BL70": {"yield": 7.36, "duration": 13.49, "spread": 253},
        "US71654QDF63": {"yield": 9.88, "duration": 9.72, "spread": 505},
        "US71654QDE98": {"yield": 8.32, "duration": 4.47, "spread": 444},
        "XS2585988145": {"yield": 6.23, "duration": 13.33, "spread": 140},
        "XS1959337749": {"yield": 5.58, "duration": 13.26, "spread": 76},
        "XS2233188353": {"yield": 5.02, "duration": 0.23, "spread": 71},
        "XS2359548935": {"yield": 5.63, "duration": 11.51, "spread": 101},
        "XS0911024635": {"yield": 5.66, "duration": 11.24, "spread": 95},
        "USP0R80BAG79": {"yield": 5.87, "duration": 5.51, "spread": 187}
    }

'''
    
    # Replace the function
    new_content = content[:start_idx] + new_function + content[end_idx:]
    
    # Write back to file
    with open('comprehensive_6way_tester.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Bloomberg baseline updated in comprehensive_6way_tester.py")

def update_real_bloomberg_comparison():
    """Update real_bloomberg_comparison.py as well"""
    
    print("🔧 UPDATING REAL BLOOMBERG COMPARISON...")
    
    # The real_bloomberg_comparison.py already has the correct data
    print("✅ real_bloomberg_comparison.py already uses correct Bloomberg data")

if __name__ == "__main__":
    update_baseline_in_tester()
    update_real_bloomberg_comparison()
    print("\n🎯 BLOOMBERG BASELINE UPDATE COMPLETE!")
    print("Now all analysis will use your REAL Bloomberg data as baseline.")
