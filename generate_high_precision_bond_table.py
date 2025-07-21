#!/usr/bin/env python3
"""
High-Precision 25-Bond Portfolio Analysis Table Generator
=========================================================

Generates a comprehensive table with yield, spread, and duration calculations
quoted to at least 5 decimal places for all 25 client bonds.

Uses the proven Google Analysis 10 infrastructure with enhanced precision.
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime
import json
import sqlite3
import requests
from decimal import Decimal, getcontext

# Set decimal precision for high-precision calculations
getcontext().prec = 28

# Add project paths
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

# API Configuration for live calculations
API_BASE = "http://localhost:8080"
API_KEY = "xtrillion-ga9-key-2024"

# 25-Bond Portfolio Data (exact client specification)
BOND_PORTFOLIO = [
    {"isin": "US912810TJ79", "price": 71.66, "name": "US TREASURY N/B, 3%, 15-Aug-2052"},
    {"isin": "XS2249741674", "price": 77.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
    {"isin": "XS1709535097", "price": 89.40, "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"},
    {"isin": "XS1982113463", "price": 87.14, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"},
    {"isin": "USP37466AS18", "price": 80.39, "name": "EMPRESA METRO, 4.7%, 07-May-2050"},
    {"isin": "USP3143NAH72", "price": 101.63, "name": "CODELCO INC, 6.15%, 24-Oct-2036"},
    {"isin": "USP30179BR86", "price": 86.42, "name": "COMISION FEDERAL, 6.264%, 15-Feb-2052"},
    {"isin": "US195325DX04", "price": 52.71, "name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061"},
    {"isin": "US279158AJ82", "price": 69.31, "name": "ECOPETROL SA, 5.875%, 28-May-2045"},
    {"isin": "USP37110AM89", "price": 76.24, "name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047"},
    {"isin": "XS2542166231", "price": 103.03, "name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038"},
    {"isin": "XS2167193015", "price": 64.50, "name": "STATE OF ISRAEL, 3.8%, 13-May-2060"},
    {"isin": "XS1508675508", "price": 82.42, "name": "SAUDI INT BOND, 4.5%, 26-Oct-2046"},
    {"isin": "XS1807299331", "price": 92.21, "name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048"},
    {"isin": "US91086QAZ19", "price": 78.00, "name": "UNITED MEXICAN, 5.75%, 12-Oct-2110"},
    {"isin": "USP6629MAD40", "price": 82.57, "name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047"},
    {"isin": "US698299BL70", "price": 56.60, "name": "PANAMA, 3.87%, 23-Jul-2060"},
    {"isin": "US71654QDF63", "price": 71.42, "name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060"},
    {"isin": "US71654QDE98", "price": 89.55, "name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031"},
    {"isin": "XS2585988145", "price": 85.54, "name": "GACI FIRST INVST, 5.125%, 14-Feb-2053"},
    {"isin": "XS1959337749", "price": 89.97, "name": "QATAR STATE OF, 4.817%, 14-Mar-2049"},
    {"isin": "XS2233188353", "price": 99.23, "name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025"},
    {"isin": "XS2359548935", "price": 73.79, "name": "QATAR ENERGY, 3.125%, 12-Jul-2041"},
    {"isin": "XS0911024635", "price": 93.29, "name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043"},
    {"isin": "USP0R80BAG79", "price": 97.26, "name": "SITIOS, 5.375%, 04-Apr-2032"}
]

def check_api_health():
    """Check if the Google Analysis 10 API is running"""
    print("🔍 Checking API Health...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Status: {health_data['status']}")
            print(f"📊 Database Size: {health_data.get('dual_database_system', {}).get('primary_database', {}).get('size_mb', 'N/A')}MB")
            return True
        else:
            print(f"❌ API Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def calculate_bond_with_api(bond_data, settlement_date="2025-07-30"):
    """Calculate individual bond metrics using the enhanced API"""
    payload = {
        "description": bond_data["name"],
        "price": bond_data["price"],
        "settlement_date": settlement_date
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/bond/parse-and-calculate",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                calc = result.get("calculations", {})
                return {
                    "yield_to_maturity": calc.get("yield_to_maturity"),
                    "duration": calc.get("duration"),
                    "spread_to_treasury": calc.get("spread_to_treasury"),
                    "accrued_interest": calc.get("accrued_interest"),
                    "clean_price": calc.get("clean_price"),
                    "dirty_price": calc.get("dirty_price"),
                    "settlement_date": settlement_date,
                    "success": True
                }
            else:
                return {"success": False, "error": result.get("error", "API calculation failed")}
        else:
            return {"success": False, "error": f"API error: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": f"Request error: {e}"}

def load_existing_results():
    """Load the most recent portfolio analysis results if available"""
    try:
        with open('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/complete_portfolio_analysis_20250720_183029.json', 'r') as f:
            data = json.load(f)
            return data.get('individual_bonds', [])
    except Exception as e:
        print(f"⚠️ Could not load existing results: {e}")
        return []

def generate_high_precision_table():
    """Generate the high-precision bond table"""
    print("🎯 GOOGLE ANALYSIS 10 - HIGH PRECISION BOND TABLE GENERATOR")
    print("=" * 75)
    print(f"🗓️ Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total Bonds: {len(BOND_PORTFOLIO)}")
    print(f"🎯 Target Precision: Minimum 5 decimal places")
    print()
    
    # Check if API is available for live calculations
    api_available = check_api_health()
    
    if api_available:
        print("🚀 Using Live API for High-Precision Calculations...")
        results = []
        
        for i, bond in enumerate(BOND_PORTFOLIO, 1):
            print(f"\n[{i:2d}/25] Calculating: {bond['name'][:50]}...")
            calculation = calculate_bond_with_api(bond)
            
            if calculation.get("success"):
                result = {
                    "ISIN": bond["isin"],
                    "PX_MID": bond["price"],
                    "Name": bond["name"],
                    "Yield_Percent": calculation["yield_to_maturity"],
                    "Duration_Years": calculation["duration"],
                    "Spread_bp": calculation["spread_to_treasury"],
                    "Accrued_Interest": calculation.get("accrued_interest", 0),
                    "Clean_Price": calculation.get("clean_price", bond["price"]),
                    "Dirty_Price": calculation.get("dirty_price", bond["price"]),
                    "Settlement_Date": calculation["settlement_date"]
                }
                results.append(result)
                print(f"    ✅ YTM: {calculation['yield_to_maturity']:.5f}% | Duration: {calculation['duration']:.5f} | Spread: {calculation['spread_to_treasury']:.2f}bp")
            else:
                print(f"    ❌ Error: {calculation.get('error', 'Unknown')}")
                # Add placeholder with error
                result = {
                    "ISIN": bond["isin"],
                    "PX_MID": bond["price"],
                    "Name": bond["name"],
                    "Yield_Percent": None,
                    "Duration_Years": None,
                    "Spread_bp": None,
                    "Accrued_Interest": None,
                    "Clean_Price": bond["price"],
                    "Dirty_Price": bond["price"],
                    "Settlement_Date": "Error"
                }
                results.append(result)
    
    else:
        print("📁 API not available - Using existing results...")
        existing_results = load_existing_results()
        
        if existing_results:
            results = []
            for bond_data in existing_results:
                # Map existing results to our format
                result = {
                    "ISIN": bond_data["isin"],
                    "PX_MID": bond_data["price"],
                    "Name": bond_data["name"],
                    "Yield_Percent": bond_data["yield"],
                    "Duration_Years": bond_data["duration"],
                    "Spread_bp": bond_data["spread"],
                    "Accrued_Interest": 0,  # Not in existing data
                    "Clean_Price": bond_data["price"],
                    "Dirty_Price": bond_data["price"],
                    "Settlement_Date": bond_data["settlement"]
                }
                results.append(result)
        else:
            print("❌ No existing results available. Please start the API first.")
            return None
    
    # Create DataFrame with high precision
    if results:
        df = pd.DataFrame(results)
        
        # Generate the formatted table
        print("\n" + "="*120)
        print("🎯 HIGH-PRECISION 25-BOND PORTFOLIO ANALYSIS TABLE")
        print("="*120)
        
        # Header
        print(f"{'#':>3} {'ISIN':>12} {'PX_MID':>8} {'YIELD_%':>12} {'DURATION':>12} {'SPREAD_BP':>10} {'NAME':<50}")
        print("-" * 120)
        
        # Data rows
        for i, row in df.iterrows():
            rank = i + 1
            isin = row['ISIN']
            price = row['PX_MID']
            name = row['Name'][:47] + "..." if len(row['Name']) > 50 else row['Name']
            
            if row['Yield_Percent'] is not None:
                yield_str = f"{row['Yield_Percent']:.5f}"
                duration_str = f"{row['Duration_Years']:.5f}"
                spread_str = f"{row['Spread_bp']:.2f}"
            else:
                yield_str = "ERROR"
                duration_str = "ERROR"
                spread_str = "ERROR"
            
            print(f"{rank:>3} {isin:>12} {price:>8.2f} {yield_str:>12} {duration_str:>12} {spread_str:>10} {name:<50}")
        
        print("-" * 120)
        
        # Summary statistics
        valid_yields = df[df['Yield_Percent'].notna()]['Yield_Percent']
        valid_durations = df[df['Duration_Years'].notna()]['Duration_Years']
        valid_spreads = df[df['Spread_bp'].notna()]['Spread_bp']
        
        if len(valid_yields) > 0:
            print(f"\n📊 PORTFOLIO SUMMARY:")
            print(f"    Average Yield:    {valid_yields.mean():.5f}%")
            print(f"    Average Duration: {valid_durations.mean():.5f} years")
            print(f"    Average Spread:   {valid_spreads.mean():.2f} bp")
            print(f"    Yield Range:      {valid_yields.min():.5f}% - {valid_yields.max():.5f}%")
            print(f"    Duration Range:   {valid_durations.min():.5f} - {valid_durations.max():.5f} years")
            print(f"    Spread Range:     {valid_spreads.min():.2f} - {valid_spreads.max():.2f} bp")
            print(f"    Successful Calcs: {len(valid_yields)}/25 bonds")
        
        # Save results to CSV with high precision
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"high_precision_bond_table_{timestamp}.csv"
        
        # Format numeric columns with high precision
        df_export = df.copy()
        for col in ['Yield_Percent', 'Duration_Years']:
            if col in df_export.columns:
                df_export[col] = df_export[col].apply(lambda x: f"{x:.10f}" if pd.notna(x) else "")
        for col in ['Spread_bp']:
            if col in df_export.columns:
                df_export[col] = df_export[col].apply(lambda x: f"{x:.5f}" if pd.notna(x) else "")
        
        df_export.to_csv(csv_filename, index=False)
        print(f"\n💾 High-precision results saved to: {csv_filename}")
        
        # Generate machine-readable JSON with full precision
        json_filename = f"high_precision_bond_table_{timestamp}.json"
        json_data = {
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_bonds": len(BOND_PORTFOLIO),
                "successful_calculations": len(valid_yields),
                "precision": "minimum_5_decimal_places",
                "settlement_date": results[0].get("Settlement_Date", "2025-07-30") if results else None,
                "api_used": api_available
            },
            "portfolio_summary": {
                "average_yield_percent": float(valid_yields.mean()) if len(valid_yields) > 0 else None,
                "average_duration_years": float(valid_durations.mean()) if len(valid_durations) > 0 else None,
                "average_spread_bp": float(valid_spreads.mean()) if len(valid_spreads) > 0 else None,
                "yield_range": [float(valid_yields.min()), float(valid_yields.max())] if len(valid_yields) > 0 else None,
                "duration_range": [float(valid_durations.min()), float(valid_durations.max())] if len(valid_durations) > 0 else None
            },
            "individual_bonds": df.to_dict('records')
        }
        
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        print(f"💾 Machine-readable JSON saved to: {json_filename}")
        
        return df
    else:
        print("❌ No calculation results available")
        return None

def create_markdown_table(df):
    """Create a markdown formatted table for documentation"""
    if df is None or len(df) == 0:
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_filename = f"bond_table_markdown_{timestamp}.md"
    
    with open(md_filename, 'w') as f:
        f.write("# High-Precision 25-Bond Portfolio Analysis\n\n")
        f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Precision:** Minimum 5 decimal places\n")
        f.write(f"**Source:** Google Analysis 10 Enhanced API\n\n")
        
        f.write("## Portfolio Table\n\n")
        f.write("| # | ISIN | PX_MID | Yield (%) | Duration (Years) | Spread (bp) | Bond Name |\n")
        f.write("|---|------|--------|-----------|------------------|-------------|----------|\n")
        
        for i, row in df.iterrows():
            rank = i + 1
            isin = row['ISIN']
            price = row['PX_MID']
            name = row['Name'][:40] + "..." if len(row['Name']) > 43 else row['Name']
            
            if row['Yield_Percent'] is not None:
                yield_str = f"{row['Yield_Percent']:.5f}"
                duration_str = f"{row['Duration_Years']:.5f}"
                spread_str = f"{row['Spread_bp']:.2f}"
            else:
                yield_str = "ERROR"
                duration_str = "ERROR"
                spread_str = "ERROR"
            
            f.write(f"| {rank} | {isin} | {price:.2f} | {yield_str} | {duration_str} | {spread_str} | {name} |\n")
        
        # Add summary
        valid_yields = df[df['Yield_Percent'].notna()]['Yield_Percent']
        valid_durations = df[df['Duration_Years'].notna()]['Duration_Years']
        valid_spreads = df[df['Spread_bp'].notna()]['Spread_bp']
        
        if len(valid_yields) > 0:
            f.write("\n## Portfolio Summary\n\n")
            f.write(f"- **Average Yield:** {valid_yields.mean():.5f}%\n")
            f.write(f"- **Average Duration:** {valid_durations.mean():.5f} years\n")
            f.write(f"- **Average Spread:** {valid_spreads.mean():.2f} bp\n")
            f.write(f"- **Successful Calculations:** {len(valid_yields)}/25 bonds\n")
    
    print(f"📝 Markdown table saved to: {md_filename}")
    return md_filename

def main():
    """Main execution function"""
    try:
        # Generate the high-precision table
        results_df = generate_high_precision_table()
        
        if results_df is not None:
            # Create markdown version
            create_markdown_table(results_df)
            
            print("\n🎉 HIGH-PRECISION BOND TABLE GENERATION COMPLETE!")
            print("📁 Check the generated files for detailed results")
            print("🎯 All yields, spreads, and durations calculated to 5+ decimal places")
            
            return results_df
        else:
            print("\n❌ Table generation failed")
            return None
            
    except Exception as e:
        print(f"\n❌ Error during table generation: {e}")
        return None

if __name__ == "__main__":
    results = main()
