import requests
import json
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# --- Configuration & Constants ---

# Add the project directory to Python path to find custom modules
PROJECT_ROOT = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
sys.path.insert(0, PROJECT_ROOT)

# Import bond data and API configuration from the project
from bond_data import BONDS_25

API_URL = "http://127.0.0.1:8000/api/v1/bond/parse-and-calculate-sync"

# --- Bloomberg Baseline Data Loading with Diagnostics ---

BASELINE_PATH = Path(__file__).resolve().parent.parent / 'bbg_baseline.xlsx'
BASELINE_MAP = {}

print(f"\n--- 🔎 DEBUG: Loading Baseline Data ---")
print(f"Attempting to load from: {BASELINE_PATH}")
if BASELINE_PATH.exists():
    print(f"✅ File found.")
    try:
        _baseline_df = pd.read_excel(BASELINE_PATH)
        print(f"  - Columns in Excel: {list(_baseline_df.columns)}")
        if 'ISIN' in _baseline_df.columns:
            _baseline_df['ISIN'] = _baseline_df['ISIN'].str.strip()
            BASELINE_MAP = _baseline_df.set_index('ISIN').to_dict(orient='index')
            print(f"  - Success: Loaded {len(BASELINE_MAP)} records into BASELINE_MAP.")
            if BASELINE_MAP and BONDS_25:
                print(f"    - First ISIN in Excel: '{list(BASELINE_MAP.keys())[0]}'")
                print(f"    - First ISIN in Portfolio: '{BONDS_25[0]['isin']}'")
        else:
            print(f"  - 🚨 ERROR: 'ISIN' column not found in the Excel file. Cannot create lookup map.")
    except Exception as e:
        print(f"  - 🚨 ERROR: Failed to read or process Excel file: {e}")
else:
    print(f"⚠️ Bloomberg baseline file not found: {BASELINE_PATH}")
print(f"-------------------------------------\n")

# --- Core Test Functions ---

def test_single_bond(bond_data, route):
    """Sends a single bond to the API for calculation."""
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "data": [bond_data],
        "calculation_params": {
            "settlement_days": 0
        },
        "use_isin_convention": route == "with_isin"
    }
    
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=60)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        result = response.json()
        
        # The API returns a list, we are only interested in the first result
        if result and isinstance(result, list) and 'results' in result[0]:
             # Successful result structure
            return result[0]['results'][0]
        elif result and isinstance(result, list) and 'error' in result[0]:
            # Error result structure
            return {"success": False, "error": result[0]['error']}
        else:
            return {"success": False, "error": "Unexpected API response format"}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"API request failed: {e}"}
    except json.JSONDecodeError:
        return {"success": False, "error": "Failed to decode JSON response"}


def generate_html_report(results):
    """Generates a self-contained HTML report from the test results."""
    html = ["<html><head><title>Bond Calculation Test Report</title><style>",
            "body { font-family: sans-serif; margin: 2em; }",
            "h1, h2 { color: #333; }",
            "table { border-collapse: collapse; width: 100%; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            ".success { color: green; } .fail { color: red; }",
            ".convergence { background-color: #e6ffed; }",
            ".divergence { background-color: #ffedeb; }",
            "</style></head><body><h1>Bond Calculation Master Test Report</h1>"]

    # Summary Section
    total_bonds = len(results)
    isin_success = sum(1 for r in results if r['isin_status'] == '✅ SUCCESS')
    parse_success = sum(1 for r in results if r['parse_status'] == '✅ SUCCESS')
    convergence_count = sum(1 for r in results if r['converged'])
    
    html.append(f"<h2>Test Summary</h2>")
    html.append(f"<p><b>Run Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
    html.append(f"<p><b>Total Bonds Tested:</b> {total_bonds}</p>")
    html.append(f"<p><b>ISIN Route Success:</b> {isin_success}/{total_bonds} ({isin_success/total_bonds:.0%})</p>")
    html.append(f"<p><b>Parse Route Success:</b> {parse_success}/{total_bonds} ({parse_success/total_bonds:.0%})</p>")
    html.append(f"<p><b>Yield Convergence (<1bp):</b> {convergence_count}/{total_bonds} ({convergence_count/total_bonds:.0%})</p>")

    # Detailed Results Table
    html.append("<h2>Detailed Results</h2><table><tr><th>#</th><th>ISIN</th><th>Name</th><th>ISIN Route</th><th>Yield (ISIN)</th><th>Parse Route</th><th>Yield (Parse)</th><th>BBG Yield</th><th>Max Diff (bps)</th></tr>")
    
    for i, res in enumerate(results, 1):
        row_class = 'convergence' if res['converged'] else 'divergence'
        html.append(f"<tr class='{row_class}'>")
        html.append(f"<td>{i}</td><td>{res['isin']}</td><td>{res['name']}</td>")
        html.append(f"<td><span class='{ 'success' if 'SUCCESS' in res['isin_status'] else 'fail' }'>{res['isin_status']}</span></td>")
        html.append(f"<td>{res['isin_yield']}</td>")
        html.append(f"<td><span class='{ 'success' if 'SUCCESS' in res['parse_status'] else 'fail' }'>{res['parse_status']}</span></td>")
        html.append(f"<td>{res['parse_yield']}</td>")
        html.append(f"<td>{res['bbg_yield']}</td>")
        html.append(f"<td>{res['max_diff_yield']}</td>")
        html.append("</tr>")
        
    html.append("</table></body></html>")
    
    # Write to file
    html_filename = f"{PROJECT_ROOT}/bond_master_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(''.join(html))
    return html_filename

# --- Main Execution Logic ---

def main():
    """Run comprehensive test on all 25 bonds"""
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print("🎯 COMPREHENSIVE 25-BOND MASTER CALCULATOR TEST")
    print("=" * 150)
    print(f"⏰ Started: {start_time}")
    print(f"📁 Project: {PROJECT_ROOT}")
    print(f"📊 Testing: {len(BONDS_25)} bonds")
    print(f"📅 Settlement: T+0 from today")
    print("🔍 Routes: ISIN Hierarchy vs Parse Hierarchy")
    print("=" * 150)

    results_summary = []
    total_bonds = len(BONDS_25)

    for i, bond in enumerate(BONDS_25, 1):
        print(f"\n🧪 Testing Bond {i}/{total_bonds}: {bond['isin']} - {bond['name'][:50]}...")
        
        # Test with ISIN (Route 1)
        result_with_isin = test_single_bond(bond, "with_isin")
        
        # Test without ISIN (Route 2) 
        result_without_isin = test_single_bond(bond, "without_isin")
        
        # Process results for reporting
        isin_status = "✅ SUCCESS" if result_with_isin.get("success") else f"❌ FAILED: {result_with_isin.get('error', 'Unknown')}"
        parse_status = "✅ SUCCESS" if result_without_isin.get("success") else f"❌ FAILED: {result_without_isin.get('error', 'Unknown')}"
        
        isin_yield_val = result_with_isin.get("yield")
        parse_yield_val = result_without_isin.get("yield")

        isin_yield_display = f"{isin_yield_val:.6%}" if isinstance(isin_yield_val, (int, float)) else 'N/A'
        parse_yield_display = f"{parse_yield_val:.6%}" if isinstance(parse_yield_val, (int, float)) else 'N/A'

        # Check convergence
        converged = False
        if isinstance(isin_yield_val, (int, float)) and isinstance(parse_yield_val, (int, float)):
            if abs(isin_yield_val - parse_yield_val) * 10000 < 1: # < 1bp difference
                converged = True
        
        # Get Bloomberg baseline
        baseline = BASELINE_MAP.get(bond['isin'], {})
        bbg_yield = baseline.get('Yield')
        bbg_yield_display = f"{bbg_yield:.6%}" if isinstance(bbg_yield, (int, float)) else 'N/A'

        # Calculate max difference
        max_diff_yield = 'N/A'
        if isinstance(bbg_yield, (int, float)):
            valid_yields = [y for y in [isin_yield_val, parse_yield_val] if isinstance(y, (int, float))]
            if valid_yields:
                max_diff = max(abs(y - bbg_yield) for y in valid_yields) * 10000 # in bps
                max_diff_yield = f"{max_diff:.2f}"

        results_summary.append({
            'isin': bond['isin'],
            'name': bond['name'],
            'isin_status': isin_status,
            'isin_yield': isin_yield_display,
            'parse_status': parse_status,
            'parse_yield': parse_yield_display,
            'converged': converged,
            'bbg_yield': bbg_yield_display,
            'max_diff_yield': max_diff_yield
        })

    # Generate and open report
    report_file = generate_html_report(results_summary)
    print("\n" + "=" * 150)
    print(f"✅ Test complete. Report generated: {report_file}")
    print("=" * 150)
    
    # Open the HTML report in the default web browser
    try:
        import webbrowser
        webbrowser.open(f'file://{report_file}')
    except ImportError:
        print("Could not import webbrowser module. Please open the report manually.")

if __name__ == "__main__":
    main()
