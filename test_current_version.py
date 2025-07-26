#!/usr/bin/env python3
"""
TEST CURRENT VERSION WITH REAL BOND DATA
This script tests the current google_analysis9.py with the user's provided bond data
to see what results we actually get before making any changes.
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the current version
from google_analysis9 import process_bonds_without_weightings, process_bonds_with_weightings

def test_current_version():
    """Test current version with real bond data"""
    
    # User's actual bond data
    bond_data = [
        {"ISIN": "US912810TJ79", "PX_MID": 71.66, "Name": "US TREASURY N/B, 3%, 15-Aug-2052"},
        {"ISIN": "XS2249741674", "PX_MID": 77.88, "Name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
        {"ISIN": "XS1709535097", "PX_MID": 89.40, "Name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"},
        {"ISIN": "XS1982113463", "PX_MID": 87.14, "Name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"},
        {"ISIN": "USP37466AS18", "PX_MID": 80.39, "Name": "EMPRESA METRO, 4.7%, 07-May-2050"},
        {"ISIN": "USP3143NAH72", "PX_MID": 101.63, "Name": "CODELCO INC, 6.15%, 24-Oct-2036"},
        {"ISIN": "USP30179BR86", "PX_MID": 86.42, "Name": "COMISION FEDERAL, 6.264%, 15-Feb-2052"},
        {"ISIN": "US195325DX04", "PX_MID": 52.71, "Name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061"},
        {"ISIN": "US279158AJ82", "PX_MID": 69.31, "Name": "ECOPETROL SA, 5.875%, 28-May-2045"},
        {"ISIN": "USP37110AM89", "PX_MID": 76.24, "Name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047"},
        {"ISIN": "XS2542166231", "PX_MID": 103.03, "Name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038"},
        {"ISIN": "XS2167193015", "PX_MID": 64.50, "Name": "STATE OF ISRAEL, 3.8%, 13-May-2060"},
        {"ISIN": "XS1508675508", "PX_MID": 82.42, "Name": "SAUDI INT BOND, 4.5%, 26-Oct-2046"},
        {"ISIN": "XS1807299331", "PX_MID": 92.21, "Name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048"},
        {"ISIN": "US91086QAZ19", "PX_MID": 78.00, "Name": "UNITED MEXICAN, 5.75%, 12-Oct-2110"},
        {"ISIN": "USP6629MAD40", "PX_MID": 82.57, "Name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047"},
        {"ISIN": "US698299BL70", "PX_MID": 56.60, "Name": "PANAMA, 3.87%, 23-Jul-2060"},
        {"ISIN": "US71654QDF63", "PX_MID": 71.42, "Name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060"},
        {"ISIN": "US71654QDE98", "PX_MID": 89.55, "Name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031"},
        {"ISIN": "XS2585988145", "PX_MID": 85.54, "Name": "GACI FIRST INVST, 5.125%, 14-Feb-2053"},
        {"ISIN": "XS1959337749", "PX_MID": 89.97, "Name": "QATAR STATE OF, 4.817%, 14-Mar-2049"},
        {"ISIN": "XS2233188353", "PX_MID": 99.23, "Name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025"},
        {"ISIN": "XS2359548935", "PX_MID": 73.79, "Name": "QATAR ENERGY, 3.125%, 12-Jul-2041"},
        {"ISIN": "XS0911024635", "PX_MID": 93.29, "Name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043"},
        {"ISIN": "USP0R80BAG79", "PX_MID": 97.26, "Name": "SITIOS, 5.375%, 04-Apr-2032"}
    ]
    
    # Create DataFrame
    df = pd.DataFrame(bond_data)
    print(f"🧪 TESTING CURRENT VERSION WITH {len(df)} BONDS")
    print(f"Columns: {list(df.columns)}")
    print(f"Sample bond: {df.iloc[0].to_dict()}")
    print("\n" + "="*80 + "\n")
    
    # Database paths
    db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db"
    validated_db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/validated_quantlib_bonds.db"
    
    # Check if databases exist
    if not os.path.exists(db_path):
        print(f"❌ ERROR: Database not found: {db_path}")
        return
    if not os.path.exists(validated_db_path):
        print(f"❌ ERROR: Validated database not found: {validated_db_path}")
        return
    
    print(f"✅ Found databases:")
    print(f"   Main DB: {db_path}")
    print(f"   Validated DB: {validated_db_path}")
    print("\n" + "="*80 + "\n")
    
    try:
        print("🚀 TESTING: process_bonds_without_weightings()")
        results = process_bonds_without_weightings(
            data=df,
            db_path=db_path,
            validated_db_path=validated_db_path
        )
        
        print(f"✅ SUCCESS! Got results with shape: {results.shape}")
        print(f"Result columns: {list(results.columns)}")
        
        if len(results) > 0:
            print(f"\n📊 SAMPLE RESULTS (first 3 rows):")
            for i in range(min(3, len(results))):
                row = results.iloc[i]
                print(f"  Bond {i+1}: {dict(row)}")
            
            # Check for specific columns we expect
            expected_cols = ['isin', 'yield', 'duration', 'spread', 'price']
            found_cols = [col for col in expected_cols if col in results.columns]
            print(f"\n📈 KEY METRICS FOUND: {found_cols}")
            
            if 'yield' in results.columns:
                yields = results['yield'].dropna()
                if len(yields) > 0:
                    print(f"   Yield range: {yields.min():.2f}% to {yields.max():.2f}%")
            
            if 'duration' in results.columns:
                durations = results['duration'].dropna()
                if len(durations) > 0:
                    print(f"   Duration range: {durations.min():.2f} to {durations.max():.2f} years")
            
            # Summary statistics
            success_count = len(results[results.get('yield', pd.Series()).notna()])
            print(f"\n📋 SUMMARY:")
            print(f"   Total bonds processed: {len(results)}")
            print(f"   Successful calculations: {success_count}")
            print(f"   Success rate: {(success_count/len(results)*100):.1f}%")
        else:
            print("❌ No results returned")
            
    except Exception as e:
        print(f"❌ ERROR in process_bonds_without_weightings: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80 + "\n")
    print("🏁 TEST COMPLETE")
    print("This tells us what the current version actually produces!")

if __name__ == "__main__":
    test_current_version()
