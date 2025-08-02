#!/usr/bin/env python3
"""
Complete 25 Bond Analysis - All Results Table
Shows every single bond with Bloomberg vs XTrillion comparison
"""

import requests
import json
import pandas as pd
from datetime import datetime

# API Configuration
API_BASE = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

def call_xtrillion_api(description, price):
    """Call XTrillion API for bond analysis"""
    try:
        url = f"{API_BASE}/api/v1/bond/analysis"
        payload = {
            "description": description,
            "price": price
        }
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def get_all_25_bonds():
    """All 25 bonds with Bloomberg baseline data"""
    bonds = [
        {"bond": "T 3 15/08/52", "price": 71.66, "bbg_ytm": 4.898453, "bbg_duration": 16.357839, "bbg_accrued_pm": 11123.596},
        {"bond": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "price": 77.88, "bbg_ytm": 5.301905, "bbg_duration": 12.798703, "bbg_accrued_pm": 1644.444},
        {"bond": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "price": 89.40, "bbg_ytm": 5.533445, "bbg_duration": 15.610947, "bbg_accrued_pm": 12400.000},
        {"bond": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "price": 87.14, "bbg_ytm": 5.453088, "bbg_duration": 11.697249, "bbg_accrued_pm": 10688.889},
        {"bond": "EMPRESA METRO, 4.7%, 07-May-2050", "price": 80.39, "bbg_ytm": 6.623874, "bbg_duration": 13.397756, "bbg_accrued_pm": 2466.667},
        {"bond": "CODELCO INC, 6.15%, 24-Oct-2036", "price": 101.63, "bbg_ytm": 5.976502, "bbg_duration": 8.889844, "bbg_accrued_pm": 16925.000},
        {"bond": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "price": 86.42, "bbg_ytm": 7.552098, "bbg_duration": 11.650063, "bbg_accrued_pm": 8554.667},
        {"bond": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "price": 52.71, "bbg_ytm": 8.026804, "bbg_duration": 11.464089, "bbg_accrued_pm": 6660.556},
        {"bond": "ECOPETROL SA, 5.875%, 28-May-2045", "price": 69.31, "bbg_ytm": 9.282266, "bbg_duration": 9.812703, "bbg_accrued_pm": 19122.222},
        {"bond": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", "price": 76.24, "bbg_ytm": 6.652468, "bbg_duration": 13.863827, "bbg_accrued_pm": 13650.000},
        {"bond": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", "price": 103.03, "bbg_ytm": 5.766688, "bbg_duration": 9.488553, "bbg_accrued_pm": 18516.194},
        {"bond": "STATE OF ISRAEL, 3.8%, 13-May-2060", "price": 64.50, "bbg_ytm": 6.530154, "bbg_duration": 14.230769, "bbg_accrued_pm": 2800.000},
        {"bond": "SAUDI INT BOND, 4.5%, 26-Oct-2046", "price": 82.42, "bbg_ytm": 6.024052, "bbg_duration": 14.181278, "bbg_accrued_pm": 13725.000},
        {"bond": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", "price": 92.21, "bbg_ytm": 7.248117, "bbg_duration": 12.219556, "bbg_accrued_pm": 18618.750},
        {"bond": "UNITED MEXICAN, 5.75%, 12-Oct-2110", "price": 78.00, "bbg_ytm": 7.474806, "bbg_duration": 12.968655, "bbg_accrued_pm": 16437.500},
        {"bond": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", "price": 82.57, "bbg_ytm": 7.153206, "bbg_duration": 12.710427, "bbg_accrued_pm": 15291.667},
        {"bond": "PANAMA, 3.87%, 23-Jul-2060", "price": 56.60, "bbg_ytm": 7.362747, "bbg_duration": 13.488582, "bbg_accrued_pm": 14204.167},
        {"bond": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "price": 71.42, "bbg_ytm": 10.120543, "bbg_duration": 8.952893, "bbg_accrued_pm": 20188.194},
        {"bond": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "price": 89.55, "bbg_ytm": 7.334503, "bbg_duration": 5.441632, "bbg_accrued_pm": 17279.167},
        {"bond": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "price": 85.54, "bbg_ytm": 6.245277, "bbg_duration": 14.098906, "bbg_accrued_pm": 8802.083},
        {"bond": "QATAR STATE OF, 4.817%, 14-Mar-2049", "price": 89.97, "bbg_ytm": 5.556802, "bbg_duration": 15.464750, "bbg_accrued_pm": 17825.625},
        {"bond": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "price": 99.23, "bbg_ytm": 1.924742, "bbg_duration": 0.890635, "bbg_accrued_pm": 1005.556},
        {"bond": "QATAR ENERGY, 3.125%, 12-Jul-2041", "price": 73.79, "bbg_ytm": 5.090516, "bbg_duration": 13.498678, "bbg_accrued_pm": 377.604},
        {"bond": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "price": 93.29, "bbg_ytm": 5.675076, "bbg_duration": 13.089228, "bbg_accrued_pm": 14759.444},
        {"bond": "SITIOS, 5.375%, 04-Apr-2032", "price": 97.26, "bbg_ytm": 5.836506, "bbg_duration": 6.326421, "bbg_accrued_pm": 13706.250}
    ]
    return bonds

def analyze_all_bonds():
    """Analyze all 25 bonds and compare with Bloomberg"""
    bonds = get_all_25_bonds()
    results = []
    
    print("🔍 COMPLETE 25 BOND ANALYSIS")
    print("=" * 120)
    print(f"{'#':<3} {'Bond':<50} {'BBG YTM':<9} {'XT YTM':<9} {'YTM Δ':<8} {'BBG Dur':<9} {'XT Dur':<9} {'Dur Δ':<8} {'Status':<12}")
    print("=" * 120)
    
    for i, bond in enumerate(bonds, 1):
        # Call XTrillion API
        api_result = call_xtrillion_api(bond["bond"], bond["price"])
        
        if api_result.get("status") == "success":
            analytics = api_result.get("analytics", {})
            xt_ytm = analytics.get("ytm", 0)
            xt_duration = analytics.get("duration", 0)
            
            # Calculate differences
            ytm_diff = xt_ytm - bond["bbg_ytm"]
            dur_diff = xt_duration - bond["bbg_duration"]
            
            # Determine status
            if abs(ytm_diff) < 0.01 and abs(dur_diff) < 0.1:
                status = "✅ PERFECT"
            elif abs(ytm_diff) < 0.05 and abs(dur_diff) < 0.5:
                status = "🟢 GOOD"
            elif abs(ytm_diff) < 0.1 and abs(dur_diff) < 1.0:
                status = "🟡 MINOR"
            else:
                status = "🔴 ISSUE"
                
        else:
            xt_ytm = 0
            xt_duration = 0
            ytm_diff = 0
            dur_diff = 0
            status = "❌ ERROR"
        
        # Print row
        bond_name = bond["bond"][:45] + "..." if len(bond["bond"]) > 45 else bond["bond"]
        print(f"{i:<3} {bond_name:<50} {bond['bbg_ytm']:<9.3f} {xt_ytm:<9.3f} {ytm_diff:<8.3f} {bond['bbg_duration']:<9.2f} {xt_duration:<9.2f} {dur_diff:<8.2f} {status:<12}")
        
        # Store result
        results.append({
            "Bond_Num": i,
            "Bond": bond["bond"],
            "Price": bond["price"],
            "BBG_YTM": bond["bbg_ytm"],
            "XT_YTM": xt_ytm,
            "YTM_Diff": ytm_diff,
            "BBG_Duration": bond["bbg_duration"],
            "XT_Duration": xt_duration,
            "Duration_Diff": dur_diff,
            "Status": status,
            "API_Status": api_result.get("status", "unknown")
        })
    
    print("=" * 120)
    
    # Summary statistics
    successful = [r for r in results if "✅" in r["Status"] or "🟢" in r["Status"]]
    issues = [r for r in results if "🔴" in r["Status"] or "❌" in r["Status"]]
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total Bonds: {len(results)}")
    print(f"   Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"   Issues: {len(issues)} ({len(issues)/len(results)*100:.1f}%)")
    
    if issues:
        print(f"\n🔴 BONDS WITH ISSUES:")
        for issue in issues:
            print(f"   #{issue['Bond_Num']}: {issue['Bond'][:60]} - {issue['Status']}")
    
    return results

def save_results_csv(results):
    """Save results to CSV"""
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"all_25_bonds_analysis_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 Results saved to: {filename}")
    return filename

if __name__ == "__main__":
    print("🎯 COMPLETE 25 BOND ANALYSIS TABLE")
    print("   This will show EVERY bond with Bloomberg vs XTrillion comparison")
    print("   So you can see exactly which bonds have issues!")
    
    results = analyze_all_bonds()
    save_results_csv(results)
    
    print("\n✅ Complete table generated!")
    print("   Now you can see exactly which bonds are problematic!")
