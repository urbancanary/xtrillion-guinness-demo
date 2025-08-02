#!/usr/bin/env python3
"""
Debug spread calculation in production environment
Test the exact same conditions as production
"""

import sys
import os
sys.path.append('.')

from google_analysis10 import fetch_treasury_yields, get_closest_treasury_yield
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_production_spread_calculation():
    """Test spread calculation using production-like conditions"""
    
    # Use production database path
    db_path = './bonds_data.db'
    
    print("🧪 Testing spread calculation in production-like environment...")
    print(f"📊 Database path: {db_path}")
    print(f"📅 Database exists: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ Database not found - cannot test spread calculation")
        return
    
    # Test treasury yield fetching for today's date
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"🗓️  Testing date: {today}")
    
    try:
        treasury_yields = fetch_treasury_yields(today, db_path)
        print(f"📈 Treasury yields: {treasury_yields}")
        
        if not treasury_yields:
            print("❌ No treasury yields found - testing recent dates...")
            
            # Try last few days
            from datetime import timedelta
            test_dates = []
            base_date = datetime.now()
            for i in range(5):
                test_date = (base_date - timedelta(days=i)).strftime('%Y-%m-%d')
                test_dates.append(test_date)
            
            for test_date in test_dates:
                yields = fetch_treasury_yields(test_date, db_path)
                if yields:
                    print(f"✅ Found treasury yields for {test_date}: {list(yields.keys())}")
                    treasury_yields = yields
                    break
                else:
                    print(f"❌ No yields for {test_date}")
        
        if treasury_yields:
            # Test spread calculation for ECOPETROL
            print("\n💰 Testing ECOPETROL spread calculation...")
            
            # ECOPETROL parameters (from API response)
            bond_yield = 9.287513294327896  # From API
            maturity_years = 20.0  # Approximate years to maturity
            
            closest_yield = get_closest_treasury_yield(treasury_yields, maturity_years)
            print(f"🎯 Closest treasury yield for {maturity_years}Y: {closest_yield}")
            
            if closest_yield:
                treasury_yield_pct = closest_yield * 100
                spread_bps = (bond_yield - treasury_yield_pct) * 100
                z_spread_bps = spread_bps + 10
                
                print(f"📊 Bond yield: {bond_yield:.4f}%")
                print(f"📊 Treasury yield: {treasury_yield_pct:.4f}%")
                print(f"💰 G-Spread: {spread_bps:.1f} bps")
                print(f"💰 Z-Spread: {z_spread_bps:.1f} bps")
                
                return {
                    'g_spread': spread_bps,
                    'z_spread': z_spread_bps,
                    'status': 'success'
                }
            else:
                print("❌ No matching treasury yield found")
                return {'status': 'no_matching_treasury'}
        else:
            print("❌ No treasury yields available")
            return {'status': 'no_treasury_data'}
            
    except Exception as e:
        print(f"❌ Error in spread calculation: {e}")
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'error': str(e)}

if __name__ == "__main__":
    result = test_production_spread_calculation()
    print(f"\n🎯 Final result: {result}")
