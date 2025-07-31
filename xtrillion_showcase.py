#!/usr/bin/env python3
"""
🎯 XTrillion Bond Analytics Showcase Script
Demonstrates core xt_ analytics functions using real bond data
Equivalent to Excel xt_ functions but in Python for analysis and Google Drive integration
"""

import requests
import json
import pandas as pd
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys

# XTrillion API Configuration
API_BASE_URL = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

class XTrillionAnalytics:
    """XTrillion API Analytics Client - Showcases xt_ function equivalents"""
    
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.base_url = API_BASE_URL
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def xt_health_check(self) -> bool:
        """Check if XTrillion API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ XTrillion API Status: {health_data.get('status', 'unknown')}")
                print(f"   Service: {health_data.get('service', 'Unknown')}")
                print(f"   Version: {health_data.get('version', 'Unknown')}")
                return True
            return False
        except Exception as e:
            print(f"❌ API Health Check Failed: {e}")
            return False
    
    def xt_bond_analysis(self, isin: str = None, description: str = None, price: float = 100.0) -> Dict[str, Any]:
        """
        Core xt_ bond analysis function
        Equivalent to Excel: =xt_analysis(ISIN, Description, Price)
        Returns all bond analytics in one call
        """
        try:
            payload = {"price": price}
            
            # Use ISIN if available, otherwise use description
            if isin and isin.strip():
                payload["isin"] = isin.strip()
            elif description and description.strip():
                payload["description"] = description.strip()
            else:
                return {"status": "error", "error": "No bond identifier provided"}
            
            response = self.session.post(
                f"{self.base_url}/api/v1/bond/analysis",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error", 
                    "error": f"API returned {response.status_code}",
                    "details": response.text[:200]
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def xt_yield(self, isin: str = None, description: str = None, price: float = 100.0) -> float:
        """
        Extract yield from bond analysis
        Equivalent to Excel: =xt_yield(ISIN, Description, Price)
        """
        analysis = self.xt_bond_analysis(isin, description, price)
        if analysis.get("status") == "success":
            return analysis.get("analytics", {}).get("ytm", 0.0)
        return 0.0
    
    def xt_duration(self, isin: str = None, description: str = None, price: float = 100.0) -> float:
        """
        Extract duration from bond analysis
        Equivalent to Excel: =xt_duration(ISIN, Description, Price)
        """
        analysis = self.xt_bond_analysis(isin, description, price)
        if analysis.get("status") == "success":
            return analysis.get("analytics", {}).get("duration", 0.0)
        return 0.0
    
    def xt_accrued_pm(self, isin: str = None, description: str = None, price: float = 100.0) -> float:
        """
        Extract accrued interest (Price Maker format)
        Equivalent to Excel: =xt_accrued_pm(ISIN, Description, Price)
        """
        analysis = self.xt_bond_analysis(isin, description, price)
        if analysis.get("status") == "success":
            return analysis.get("analytics", {}).get("accrued_interest", 0.0)
        return 0.0
    
    def xt_daycount(self, isin: str = None, description: str = None, price: float = 100.0) -> str:
        """
        Extract day count convention
        Equivalent to Excel: =xt_daycount(ISIN, Description, Price)
        """
        analysis = self.xt_bond_analysis(isin, description, price)
        if analysis.get("status") == "success":
            return analysis.get("calculations", {}).get("day_count", "Unknown")
        return "Unknown"
    
    def xt_status(self, isin: str = None, description: str = None, price: float = 100.0) -> str:
        """
        Get calculation status
        Equivalent to Excel: =xt_status(ISIN, Description, Price)
        """
        analysis = self.xt_bond_analysis(isin, description, price)
        return analysis.get("status", "error")
    
    def xt_spread(self, isin: str = None, description: str = None, price: float = 100.0) -> float:
        """
        Extract spread over treasury curve
        Equivalent to Excel: =xt_spread(ISIN, Description, Price)
        """
        analysis = self.xt_bond_analysis(isin, description, price)
        if analysis.get("status") == "success":
            spread = analysis.get("analytics", {}).get("spread")
            return spread if spread is not None else 0.0
        return 0.0
    
    def xt_convexity(self, isin: str = None, description: str = None, price: float = 100.0) -> float:
        """
        Extract convexity
        Equivalent to Excel: =xt_convexity(ISIN, Description, Price)
        """
        analysis = self.xt_bond_analysis(isin, description, price)
        if analysis.get("status") == "success":
            return analysis.get("analytics", {}).get("convexity", 0.0)
        return 0.0

def load_sample_bonds() -> List[Dict]:
    """Load the sample bond data provided by user"""
    bonds = [
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
    return bonds

def showcase_individual_analytics(api: XTrillionAnalytics, bonds: List[Dict], max_bonds: int = 5):
    """Showcase individual xt_ analytics functions"""
    print("\n" + "="*80)
    print("🎯 XTrillion Individual Analytics Showcase")
    print("   Demonstrating xt_ functions equivalent to Excel formulas")
    print("="*80)
    
    results = []
    
    for i, bond in enumerate(bonds[:max_bonds]):
        print(f"\n📊 Bond {i+1}: {bond['Name'][:50]}...")
        print(f"   ISIN: {bond['ISIN']} | Price: {bond['PX_MID']}")
        
        # Demonstrate each xt_ function
        isin = bond['ISIN']
        price = bond['PX_MID']
        name = bond['Name']
        
        # Call individual xt_ functions (like Excel formulas)
        yield_val = api.xt_yield(isin=isin, price=price)
        duration_val = api.xt_duration(isin=isin, price=price)
        accrued_val = api.xt_accrued_pm(isin=isin, price=price)
        daycount_val = api.xt_daycount(isin=isin, price=price)
        status_val = api.xt_status(isin=isin, price=price)
        spread_val = api.xt_spread(isin=isin, price=price)
        convexity_val = api.xt_convexity(isin=isin, price=price)
        
        # Display results
        print(f"   📈 xt_yield():     {yield_val:.4f}%")
        print(f"   ⏱️  xt_duration():  {duration_val:.2f} years")
        print(f"   💰 xt_accrued_pm(): {accrued_val:.4f}%")
        print(f"   📅 xt_daycount():  {daycount_val}")
        print(f"   ✅ xt_status():    {status_val}")
        print(f"   📊 xt_spread():    {spread_val:.0f} bps")
        print(f"   🎯 xt_convexity(): {convexity_val:.2f}")
        
        # Collect for DataFrame
        results.append({
            'ISIN': isin,
            'Name': name[:30] + "..." if len(name) > 30 else name,
            'Price': price,
            'Yield_%': round(yield_val, 4),
            'Duration_Years': round(duration_val, 2),
            'Accrued_%': round(accrued_val, 4),
            'Day_Count': daycount_val,
            'Status': status_val,
            'Spread_bps': round(spread_val, 0),
            'Convexity': round(convexity_val, 2)
        })
        
        # Add small delay to be respectful to API
        time.sleep(0.5)
    
    return results

def showcase_portfolio_analytics(api: XTrillionAnalytics, bonds: List[Dict]):
    """Showcase portfolio-level analytics using XTrillion API"""
    print("\n" + "="*80)
    print("🎯 XTrillion Portfolio Analytics Showcase")
    print("   Demonstrating portfolio-level xt_ analytics")
    print("="*80)
    
    # Prepare portfolio data for API
    portfolio_data = []
    for bond in bonds[:10]:  # Use first 10 bonds for portfolio
        portfolio_data.append({
            "BOND_CD": bond["ISIN"],
            "CLOSING PRICE": bond["PX_MID"],
            "WEIGHTING": 100.0 / len(bonds[:10])  # Equal weighting
        })
    
    try:
        # Call portfolio analysis API
        payload = {"data": portfolio_data}
        response = api.session.post(
            f"{api.base_url}/api/v1/portfolio/analysis",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            portfolio_result = response.json()
            
            print("✅ Portfolio Analysis Successful!")
            print(f"   Total Bonds: {len(portfolio_data)}")
            
            # Extract portfolio metrics
            portfolio_metrics = portfolio_result.get("portfolio_metrics", {})
            print(f"\n📊 Portfolio Metrics:")
            print(f"   Portfolio Yield: {portfolio_metrics.get('portfolio_yield', 'N/A')}")
            print(f"   Portfolio Duration: {portfolio_metrics.get('portfolio_duration', 'N/A')}")
            print(f"   Portfolio Spread: {portfolio_metrics.get('portfolio_spread', 'N/A')}")
            print(f"   Success Rate: {portfolio_metrics.get('success_rate', 'N/A')}")
            
            # Display individual bond results in portfolio
            bond_data = portfolio_result.get("bond_data", [])
            print(f"\n📋 Individual Bonds in Portfolio:")
            for i, bond_result in enumerate(bond_data[:5]):  # Show first 5
                print(f"   {i+1}. {bond_result.get('name', 'Unknown')[:40]}")
                print(f"      Yield: {bond_result.get('yield', 'N/A')}")
                print(f"      Duration: {bond_result.get('duration', 'N/A')}")
                print(f"      Status: {bond_result.get('status', 'N/A')}")
        else:
            print(f"❌ Portfolio analysis failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Portfolio analysis error: {e}")

def save_to_csv(results: List[Dict], filename: str = None):
    """Save results to CSV for Google Drive upload"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"xtrillion_bond_analytics_{timestamp}.csv"
    
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)
    print(f"\n💾 Results saved to: {filename}")
    print(f"   Ready for Google Drive upload!")
    return filename

def display_summary_table(results: List[Dict]):
    """Display a nice summary table"""
    if not results:
        return
        
    print("\n" + "="*120)
    print("📊 XTrillion Analytics Summary Table")
    print("="*120)
    
    df = pd.DataFrame(results)
    
    # Configure pandas display options for nice formatting
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 120)
    pd.set_option('display.max_colwidth', 30)
    
    print(df.to_string(index=False))
    
    print("\n📈 Quick Stats:")
    print(f"   Average Yield: {df['Yield_%'].mean():.2f}%")
    print(f"   Average Duration: {df['Duration_Years'].mean():.2f} years")
    print(f"   Average Spread: {df['Spread_bps'].mean():.0f} bps")
    print(f"   Success Rate: {len(df[df['Status'] == 'success']) / len(df) * 100:.1f}%")

def main():
    """Main showcase function"""
    print("🎯 XTrillion Bond Analytics Showcase")
    print("    Demonstrating Excel xt_ function equivalents in Python")
    print("    Perfect for Google Drive integration and analysis")
    print("=" * 80)
    
    # Initialize API client
    api = XTrillionAnalytics()
    
    # Health check
    if not api.xt_health_check():
        print("❌ Cannot connect to XTrillion API. Exiting...")
        sys.exit(1)
    
    # Load sample bonds
    bonds = load_sample_bonds()
    print(f"\n📋 Loaded {len(bonds)} sample bonds for analysis")
    
    # Showcase individual analytics (like Excel formulas)
    print("\n🎯 Part 1: Individual Bond Analytics (Excel xt_ functions)")
    results = showcase_individual_analytics(api, bonds, max_bonds=8)
    
    # Display nice summary table
    display_summary_table(results)
    
    # Showcase portfolio analytics
    print("\n🎯 Part 2: Portfolio Analytics")
    showcase_portfolio_analytics(api, bonds)
    
    # Save results to CSV for Google Drive
    csv_filename = save_to_csv(results)
    
    print("\n" + "="*80)
    print("✅ XTrillion Showcase Complete!")
    print(f"📊 Analyzed {len(results)} bonds using xt_ analytics functions")
    print(f"💾 Results saved to: {csv_filename}")
    print("🚀 Ready for Google Drive upload and further analysis!")
    print("="*80)
    
    # Show Excel equivalent formulas
    print("\n📝 Excel Formula Equivalents:")
    print("   =xt_yield(A2, B2, C2)      → Python: api.xt_yield(isin, price)")
    print("   =xt_duration(A2, B2, C2)   → Python: api.xt_duration(isin, price)")
    print("   =xt_accrued_pm(A2, B2, C2) → Python: api.xt_accrued_pm(isin, price)")
    print("   =xt_daycount(A2, B2, C2)   → Python: api.xt_daycount(isin, price)")
    print("   =xt_status(A2, B2, C2)     → Python: api.xt_status(isin, price)")

if __name__ == "__main__":
    main()