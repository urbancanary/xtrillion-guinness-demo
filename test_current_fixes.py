#!/usr/bin/env python3
"""
Test the current fixed version with real bond data
"""

import pandas as pd
from google_analysis9 import process_bonds_with_weightings
import json

# Your actual bond data
bond_data = [
    {'ISIN': 'US912810TJ79', 'PX_MID': 71.66, 'Name': 'US TREASURY N/B, 3%, 15-Aug-2052'},
    {'ISIN': 'XS2249741674', 'PX_MID': 77.88, 'Name': 'GALAXY PIPELINE, 3.25%, 30-Sep-2040'},
    {'ISIN': 'XS1709535097', 'PX_MID': 89.40, 'Name': 'ABU DHABI CRUDE, 4.6%, 02-Nov-2047'},
    {'ISIN': 'XS1982113463', 'PX_MID': 87.14, 'Name': 'SAUDI ARAB OIL, 4.25%, 16-Apr-2039'},
    {'ISIN': 'USP37466AS18', 'PX_MID': 80.39, 'Name': 'EMPRESA METRO, 4.7%, 07-May-2050'},
    {'ISIN': 'USP3143NAH72', 'PX_MID': 101.63, 'Name': 'CODELCO INC, 6.15%, 24-Oct-2036'},
    {'ISIN': 'USP30179BR86', 'PX_MID': 86.42, 'Name': 'COMISION FEDERAL, 6.264%, 15-Feb-2052'},
    {'ISIN': 'US195325DX04', 'PX_MID': 52.71, 'Name': 'COLOMBIA REP OF, 3.875%, 15-Feb-2061'},
    {'ISIN': 'US279158AJ82', 'PX_MID': 69.31, 'Name': 'ECOPETROL SA, 5.875%, 28-May-2045'},
    {'ISIN': 'USP37110AM89', 'PX_MID': 76.24, 'Name': 'EMPRESA NACIONAL, 4.5%, 14-Sep-2047'},
    {'ISIN': 'XS2542166231', 'PX_MID': 103.03, 'Name': 'GREENSAIF PIPELI, 6.129%, 23-Feb-2038'},
    {'ISIN': 'XS2167193015', 'PX_MID': 64.50, 'Name': 'STATE OF ISRAEL, 3.8%, 13-May-2060'},
    {'ISIN': 'XS1508675508', 'PX_MID': 82.42, 'Name': 'SAUDI INT BOND, 4.5%, 26-Oct-2046'},
    {'ISIN': 'XS1807299331', 'PX_MID': 92.21, 'Name': 'KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048'},
    {'ISIN': 'US91086QAZ19', 'PX_MID': 78.00, 'Name': 'UNITED MEXICAN, 5.75%, 12-Oct-2110'},
    {'ISIN': 'USP6629MAD40', 'PX_MID': 82.57, 'Name': 'MEXICO CITY ARPT, 5.5%, 31-Jul-2047'},
    {'ISIN': 'US698299BL70', 'PX_MID': 56.60, 'Name': 'PANAMA, 3.87%, 23-Jul-2060'},
    {'ISIN': 'US71654QDF63', 'PX_MID': 71.42, 'Name': 'PETROLEOS MEXICA, 6.95%, 28-Jan-2060'},
    {'ISIN': 'US71654QDE98', 'PX_MID': 89.55, 'Name': 'PETROLEOS MEXICA, 5.95%, 28-Jan-2031'},
    {'ISIN': 'XS2585988145', 'PX_MID': 85.54, 'Name': 'GACI FIRST INVST, 5.125%, 14-Feb-2053'},
    {'ISIN': 'XS1959337749', 'PX_MID': 89.97, 'Name': 'QATAR STATE OF, 4.817%, 14-Mar-2049'},
    {'ISIN': 'XS2233188353', 'PX_MID': 99.23, 'Name': 'QNB FINANCE LTD, 1.625%, 22-Sep-2025'},
    {'ISIN': 'XS2359548935', 'PX_MID': 73.79, 'Name': 'QATAR ENERGY, 3.125%, 12-Jul-2041'},
    {'ISIN': 'XS0911024635', 'PX_MID': 93.29, 'Name': 'SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043'},
    {'ISIN': 'USP0R80BAG79', 'PX_MID': 97.26, 'Name': 'SITIOS, 5.375%, 04-Apr-2032'}
]

def test_current_version():
    print("🧪 TESTING CURRENT FIXED VERSION WITH YOUR BOND DATA")
    print("=" * 60)
    
    # Convert to the format expected by the function
    # The function expects: BOND_CD (for ISIN) and WEIGHTING
    # For testing, let's give each bond equal weight
    test_data = []
    weight_per_bond = 100.0 / len(bond_data)  # Equal weights totaling 100%
    
    for bond in bond_data:
        test_data.append({
            'BOND_CD': bond['ISIN'],  # Use BOND_CD as the ISIN column
            'WEIGHTING': weight_per_bond
        })
    
    # Format for the function
    formatted_data = {'data': test_data}
    
    try:
        # Test with the current fixed version
        result = process_bonds_with_weightings(formatted_data, './bonds_data.db')
        
        print(f"✅ PROCESSING COMPLETE!")
        print(f"📊 Results DataFrame shape: {result.shape}")
        print(f"📋 Columns: {result.columns.tolist()}")
        print()
        
        # Analyze the results
        if 'error' in result.columns:
            errors = result[result['error'].notna()]
            successes = result[result['error'].isna()]
            
            print(f"📊 SUMMARY:")
            print(f"   ✅ Successful: {len(successes)}/{len(result)} bonds ({len(successes)/len(result)*100:.1f}%)")
            print(f"   ❌ Failed: {len(errors)}/{len(result)} bonds ({len(errors)/len(result)*100:.1f}%)")
            print()
            
            if len(successes) > 0:
                print("🎉 SUCCESSFUL BONDS:")
                for idx, row in successes.iterrows():
                    bond_name = next((b['Name'] for b in bond_data if b['ISIN'] == row['isin']), 'Unknown')
                    print(f"   ✅ {row['isin']}: {bond_name}")
                print()
            
            if len(errors) > 0:
                print("❌ FAILED BONDS:")
                error_summary = {}
                for idx, row in errors.iterrows():
                    bond_name = next((b['Name'] for b in bond_data if b['ISIN'] == row['isin']), 'Unknown')
                    error_msg = str(row['error'])[:100]  # Truncate long errors
                    print(f"   ❌ {row['isin']}: {bond_name}")
                    print(f"      Error: {error_msg}")
                    
                    # Count error types
                    error_type = error_msg.split(':')[0] if ':' in error_msg else error_msg
                    error_summary[error_type] = error_summary.get(error_type, 0) + 1
                
                print()
                print("📈 ERROR BREAKDOWN:")
                for error_type, count in error_summary.items():
                    print(f"   {error_type}: {count} bonds")
        
        # Save detailed results
        result_file = 'current_version_test_results.json'
        result_dict = result.to_dict('records')
        with open(result_file, 'w') as f:
            json.dump(result_dict, f, indent=2, default=str)
        print(f"\n💾 Detailed results saved to: {result_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_current_version()
