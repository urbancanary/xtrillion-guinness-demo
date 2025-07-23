#!/usr/bin/env python3
"""
DETAILED 25-BOND YIELD COMPARISON TABLE
======================================
Shows exact yield results for all methods to identify discrepancies
"""

import sqlite3
import pandas as pd

def create_detailed_yield_table():
    """Create detailed table showing yields for all 25 bonds across all methods"""
    
    print('🔍 DETAILED YIELD COMPARISON - ALL 25 BONDS')
    print('=' * 80)
    
    # Connect to the FIXED database
    conn = sqlite3.connect('six_way_analysis_FIXED_20250722_104353.db')
    
    # Get yield results
    results_df = pd.read_sql_query('''
        SELECT bond_identifier as isin, method_name, yield_pct, success, error_message
        FROM six_way_results 
        ORDER BY bond_identifier, method_name
    ''', conn)
    
    # Create pivot table for yields
    yield_pivot = results_df.pivot(index='isin', columns='method_name', values='yield_pct')
    
    # Get error information for failed calculations
    error_df = results_df[results_df['success'] == 0][['isin', 'method_name', 'error_message']]
    
    # Reorder columns for logical comparison
    method_order = ['local_isin', 'local_desc', 'local_api_isin', 'local_api_desc', 'cloud_api_isin', 'cloud_api_desc']
    
    # Get bond descriptions for reference
    bond_descriptions = {
        "US912810TJ79": "US TREASURY N/B, 3%, 15-Aug-2052",
        "XS2249741674": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", 
        "XS1709535097": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047",
        "XS1982113463": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039",
        "USP37466AS18": "EMPRESA METRO, 4.7%, 07-May-2050",
        "USP3143NAH72": "CODELCO INC, 6.15%, 24-Oct-2036",
        "USP30179BR86": "COMISION FEDERAL, 6.264%, 15-Feb-2052",
        "US195325DX04": "COLOMBIA REP OF, 3.875%, 15-Feb-2061",
        "US279158AJ82": "ECOPETROL SA, 5.875%, 28-May-2045",
        "USP37110AM89": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047",
        "XS2542166231": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038",
        "XS2167193015": "STATE OF ISRAEL, 3.8%, 13-May-2060",
        "XS1508675508": "SAUDI INT BOND, 4.5%, 26-Oct-2046",
        "XS1807299331": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048",
        "US91086QAZ19": "UNITED MEXICAN, 5.75%, 12-Oct-2110",
        "USP6629MAD40": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047",
        "US698299BL70": "PANAMA, 3.87%, 23-Jul-2060",
        "US71654QDF63": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
        "US71654QDE98": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031",
        "XS2585988145": "GACI FIRST INVST, 5.125%, 14-Feb-2053",
        "XS1959337749": "QATAR STATE OF, 4.817%, 14-Mar-2049",
        "XS2233188353": "QNB FINANCE LTD, 1.625%, 22-Sep-2025",
        "XS2359548935": "QATAR ENERGY, 3.125%, 12-Jul-2041",
        "XS0911024635": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043",
        "USP0R80BAG79": "SITIOS, 5.375%, 04-Apr-2032"
    }
    
    print(f"{'Bond':<15} {'Description':<35} {'DirIsin':<8} {'DirDesc':<8} {'ApiIsin':<8} {'ApiDesc':<8} {'CloudIsin':<8} {'CloudDesc':<8} {'Max Diff':<8}")
    print('-' * 120)
    
    # Track discrepancies
    discrepancies = []
    
    for isin in sorted(yield_pivot.index):
        desc = bond_descriptions.get(isin, "Unknown")[:34]
        
        # Get yields for each method
        dir_isin = yield_pivot.loc[isin, 'local_isin'] if 'local_isin' in yield_pivot.columns else None
        dir_desc = yield_pivot.loc[isin, 'local_desc'] if 'local_desc' in yield_pivot.columns else None
        api_isin = yield_pivot.loc[isin, 'local_api_isin'] if 'local_api_isin' in yield_pivot.columns else None
        api_desc = yield_pivot.loc[isin, 'local_api_desc'] if 'local_api_desc' in yield_pivot.columns else None
        cloud_isin = yield_pivot.loc[isin, 'cloud_api_isin'] if 'cloud_api_isin' in yield_pivot.columns else None
        cloud_desc = yield_pivot.loc[isin, 'cloud_api_desc'] if 'cloud_api_desc' in yield_pivot.columns else None
        
        # Calculate max difference among all values
        values = [v for v in [dir_isin, dir_desc, api_isin, api_desc, cloud_isin, cloud_desc] if pd.notna(v)]
        max_diff = 0
        if len(values) > 1:
            max_diff = (max(values) - min(values)) * 100  # in basis points
        
        # Format values for display
        def fmt_yield(val):
            if pd.isna(val):
                return "  N/A  "
            return f"{val:7.3f}"
        
        print(f"{isin:<15} {desc:<35} {fmt_yield(dir_isin)} {fmt_yield(dir_desc)} {fmt_yield(api_isin)} {fmt_yield(api_desc)} {fmt_yield(cloud_isin)} {fmt_yield(cloud_desc)} {max_diff:7.1f}bp")
        
        # Track significant discrepancies
        if max_diff > 1.0:  # More than 1bp difference
            discrepancies.append({
                'isin': isin,
                'description': desc,
                'max_diff_bp': max_diff,
                'dir_isin': dir_isin,
                'dir_desc': dir_desc,
                'api_isin': api_isin,
                'api_desc': api_desc,
                'cloud_isin': cloud_isin,
                'cloud_desc': cloud_desc
            })
    
    print('\n🚨 DISCREPANCY ANALYSIS:')
    print('=' * 50)
    
    if discrepancies:
        print(f"Found {len(discrepancies)} bonds with >1bp yield differences:\n")
        
        for disc in sorted(discrepancies, key=lambda x: x['max_diff_bp'], reverse=True):
            print(f"🔍 {disc['isin']} - {disc['description']}")
            print(f"   Max Difference: {disc['max_diff_bp']:.1f}bp")
            print(f"   Direct ISIN:  {disc['dir_isin']:.5f}%")
            print(f"   Direct Desc:  {disc['dir_desc']:.5f}%") 
            print(f"   API ISIN:     {disc['api_isin']:.5f}%")
            print(f"   API Desc:     {disc['api_desc']:.5f}%")
            print(f"   Cloud ISIN:   {disc['cloud_isin']:.5f}%")
            print(f"   Cloud Desc:   {disc['cloud_desc']:.5f}%")
            
            # Analyze pattern of differences
            if abs(disc['dir_isin'] - disc['api_isin']) < 0.0001:
                print(f"   ✅ Direct ISIN = API ISIN (architecture fix worked)")
            else:
                print(f"   ❌ Direct ISIN ≠ API ISIN ({abs(disc['dir_isin'] - disc['api_isin'])*100:.1f}bp diff)")
            
            if abs(disc['api_isin'] - disc['cloud_isin']) < 0.0001:
                print(f"   ✅ Local API = Cloud API (consistent)")
            else:
                print(f"   ❌ Local API ≠ Cloud API ({abs(disc['api_isin'] - disc['cloud_isin'])*100:.1f}bp diff)")
            
            print()
    else:
        print("✅ NO DISCREPANCIES > 1bp found! All methods are aligned.")
    
    # Check for any failed calculations
    if not error_df.empty:
        print('❌ FAILED CALCULATIONS:')
        print('=' * 30)
        for _, row in error_df.iterrows():
            print(f"{row['isin']} - {row['method_name']}: {row['error_message']}")
    else:
        print('✅ ALL CALCULATIONS SUCCESSFUL')
    
    print('\n🎯 ARCHITECTURE STATUS:')
    print('=' * 25)
    
    # Check if Direct Local matches APIs
    significant_arch_issues = 0
    for disc in discrepancies:
        if abs(disc['dir_isin'] - disc['api_isin']) > 0.001:  # >0.1bp
            significant_arch_issues += 1
    
    if significant_arch_issues == 0:
        print('✅ ARCHITECTURE FIX SUCCESSFUL: Direct Local matches APIs')
    else:
        print(f'⚠️ ARCHITECTURE ISSUE: {significant_arch_issues} bonds show Direct Local ≠ API')
    
    # Summary statistics
    all_diffs = [d['max_diff_bp'] for d in discrepancies]
    if all_diffs:
        print(f'\n📊 DIFFERENCE STATISTICS:')
        print(f'   Mean: {sum(all_diffs)/len(all_diffs):.1f}bp')
        print(f'   Max:  {max(all_diffs):.1f}bp')
        print(f'   Bonds with >1bp diff: {len(discrepancies)}/25 ({len(discrepancies)/25*100:.1f}%)')
    
    conn.close()

if __name__ == "__main__":
    create_detailed_yield_table()
