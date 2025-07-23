#!/usr/bin/env python3
"""
HIGH PRECISION YIELD COMPARISON - 6 DECIMAL PLACES
=================================================
Shows exact yield results to identify real vs rounding differences
"""

import sqlite3
import pandas as pd

def create_high_precision_yield_table():
    """Create detailed table showing yields to 6 decimal places"""
    
    print('🔍 HIGH PRECISION YIELD COMPARISON - 6 DECIMAL PLACES')
    print('=' * 90)
    
    # Connect to the FIXED database
    conn = sqlite3.connect('six_way_analysis_FIXED_20250722_104353.db')
    
    # Get yield results with high precision
    results_df = pd.read_sql_query('''
        SELECT bond_identifier as isin, method_name, yield_pct, success
        FROM six_way_results 
        WHERE yield_pct IS NOT NULL
        ORDER BY bond_identifier, method_name
    ''', conn)
    
    # Create pivot table for yields
    yield_pivot = results_df.pivot(index='isin', columns='method_name', values='yield_pct')
    
    # Bond descriptions for reference
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
    
    print(f"{'Bond':<15} {'Description':<40} {'DirIsin':<12} {'DirDesc':<12} {'ApiIsin':<12} {'ApiDesc':<12} {'CloudIsin':<12} {'CloudDesc':<12} {'MaxDiff':<8}")
    print('-' * 150)
    
    # Track discrepancies with high precision
    discrepancies = []
    
    for isin in sorted(yield_pivot.index):
        desc = bond_descriptions.get(isin, "Unknown")[:39]
        
        # Get yields for each method with high precision
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
        
        # Format values for display with 6 decimal places
        def fmt_yield(val):
            if pd.isna(val):
                return "   N/A     "
            return f"{val:10.6f}"
        
        print(f"{isin:<15} {desc:<40} {fmt_yield(dir_isin)} {fmt_yield(dir_desc)} {fmt_yield(api_isin)} {fmt_yield(api_desc)} {fmt_yield(cloud_isin)} {fmt_yield(cloud_desc)} {max_diff:7.3f}")
        
        # Track significant discrepancies (>0.001bp = 0.00001%)
        if max_diff > 0.001:
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
    
    print('\n🔬 HIGH PRECISION DISCREPANCY ANALYSIS:')
    print('=' * 60)
    
    if discrepancies:
        print(f"Found {len(discrepancies)} bonds with >0.001bp yield differences:\n")
        
        # Sort by max difference
        for i, disc in enumerate(sorted(discrepancies, key=lambda x: x['max_diff_bp'], reverse=True)[:5]):  # Show top 5
            print(f"🔍 #{i+1} WORST: {disc['isin']} - {disc['description']}")
            print(f"   Max Difference: {disc['max_diff_bp']:.6f}bp")
            print(f"   Direct ISIN:  {disc['dir_isin']:.6f}%")
            print(f"   Direct Desc:  {disc['dir_desc']:.6f}%") 
            print(f"   API ISIN:     {disc['api_isin']:.6f}%")
            print(f"   API Desc:     {disc['api_desc']:.6f}%")
            print(f"   Cloud ISIN:   {disc['cloud_isin']:.6f}%")
            print(f"   Cloud Desc:   {disc['cloud_desc']:.6f}%")
            
            # Calculate precise differences
            direct_api_diff = abs(disc['dir_isin'] - disc['api_isin']) * 100
            cloud_api_diff = abs(disc['cloud_isin'] - disc['api_isin']) * 100
            
            print(f"   Direct vs API:  {direct_api_diff:.6f}bp")
            print(f"   Cloud vs API:   {cloud_api_diff:.6f}bp")
            
            # Check if differences are truly identical or just very close
            if abs(disc['dir_isin'] - disc['cloud_isin']) < 1e-10:
                print(f"   ✅ Direct = Cloud (truly identical)")
            else:
                print(f"   ⚠️ Direct ≠ Cloud ({abs(disc['dir_isin'] - disc['cloud_isin'])*100:.6f}bp)")
            
            print()
    else:
        print("✅ NO DISCREPANCIES > 0.001bp found! All methods are truly identical.")
    
    # Precision analysis
    print('\n📊 PRECISION ANALYSIS:')
    print('=' * 30)
    
    all_diffs = [d['max_diff_bp'] for d in discrepancies]
    if all_diffs:
        print(f'Total bonds with differences: {len(discrepancies)}/25')
        print(f'Mean difference: {sum(all_diffs)/len(all_diffs):.6f}bp')
        print(f'Max difference:  {max(all_diffs):.6f}bp')
        print(f'Min difference:  {min(all_diffs):.6f}bp')
        
        # Categorize by precision
        tiny_diffs = [d for d in all_diffs if d < 0.01]  # <0.01bp
        small_diffs = [d for d in all_diffs if 0.01 <= d < 0.1]  # 0.01-0.1bp
        medium_diffs = [d for d in all_diffs if 0.1 <= d < 1]  # 0.1-1bp
        large_diffs = [d for d in all_diffs if d >= 1]  # ≥1bp
        
        print(f'\nDifference categorization:')
        print(f'  <0.01bp (rounding):     {len(tiny_diffs)}/25 bonds')
        print(f'  0.01-0.1bp (precision): {len(small_diffs)}/25 bonds')
        print(f'  0.1-1bp (minor):        {len(medium_diffs)}/25 bonds')
        print(f'  ≥1bp (significant):     {len(large_diffs)}/25 bonds')
        
        if len(large_diffs) == 0:
            print('\n✅ All differences <1bp - likely precision/rounding issues')
        else:
            print(f'\n⚠️ {len(large_diffs)} bonds have significant (≥1bp) differences - real calculation differences')
    
    conn.close()

if __name__ == "__main__":
    create_high_precision_yield_table()
