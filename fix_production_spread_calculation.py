#!/usr/bin/env python3
"""
Fix Production Spread Calculation
================================

The spread calculation is failing because:
1. The code expects treasury yields from tsys_enhanced table
2. The production database might not have this data accessible
3. Error handling is suppressing the actual error
"""

import sqlite3
import os
from datetime import datetime

# First, let's add better error handling to google_analysis10.py
FIX_CODE = '''
# 🚨 CRITICAL FIX: Add detailed logging for spread calculation
try:
    # Get treasury yields for the trade date - USE PASSED DB_PATH
    logger.info(f"{log_prefix} 🔍 Fetching treasury yields for {trade_date.strftime('%Y-%m-%d')} from {effective_db_path}")
    treasury_yields = fetch_treasury_yields(trade_date.strftime('%Y-%m-%d'), effective_db_path)
    
    if not treasury_yields:
        logger.warning(f"{log_prefix} ⚠️ No treasury yields returned for {trade_date.strftime('%Y-%m-%d')}")
    else:
        logger.info(f"{log_prefix} ✅ Found treasury yields: {len(treasury_yields)} tenors")
        
        # Calculate years to maturity for treasury matching
        years_to_maturity = (maturity_date - trade_date).days / 365.25
        logger.info(f"{log_prefix} 📅 Years to maturity: {years_to_maturity:.2f}")
        
        # Find closest treasury yield
        closest_treasury_yield = get_closest_treasury_yield(treasury_yields, years_to_maturity)
        
        if closest_treasury_yield:
            # Calculate spread in basis points
            treasury_yield_pct = closest_treasury_yield * 100  # Convert to percentage
            g_spread = (bond_yield_pct - treasury_yield_pct) * 100  # Convert to basis points
            z_spread = g_spread + 10  # Z-spread typically 5-15 bps wider
            
            logger.info(f"{log_prefix} 💰 SPREAD CALC: Bond {bond_yield_pct:.3f}% - Treasury {treasury_yield_pct:.3f}% = {g_spread:.0f} bps")
        else:
            logger.warning(f"{log_prefix} ⚠️ No matching treasury yield for {years_to_maturity:.1f}Y maturity")
            logger.info(f"{log_prefix} Available tenors: {list(treasury_yields.keys())}")
            
except Exception as spread_error:
    logger.error(f"{log_prefix} ❌ SPREAD CALCULATION ERROR: {spread_error}", exc_info=True)
    logger.error(f"{log_prefix} DB Path: {effective_db_path}")
    logger.error(f"{log_prefix} Trade Date: {trade_date}")
'''

# Check what's in the production database
def check_production_database():
    """Check if production has treasury data."""
    print("🔍 Checking Production Database Configuration")
    print("=" * 50)
    
    # Check bonds_data.db
    if os.path.exists('bonds_data.db'):
        print("\n📁 bonds_data.db:")
        with sqlite3.connect('bonds_data.db') as conn:
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"   Tables: {', '.join(tables[:5])}..." if len(tables) > 5 else f"   Tables: {', '.join(tables)}")
            
            if 'tsys_enhanced' in tables:
                print("   ✅ tsys_enhanced table exists")
                
                # Check data
                cursor.execute("SELECT COUNT(*), MAX(Date), MIN(Date) FROM tsys_enhanced")
                count, max_date, min_date = cursor.fetchone()
                print(f"   📈 Treasury data: {count} rows")
                print(f"   📅 Date range: {min_date} to {max_date}")
                
                # Check if we have data for July 31
                cursor.execute("SELECT * FROM tsys_enhanced WHERE Date = '2025-07-31' LIMIT 1")
                if cursor.fetchone():
                    print("   ✅ July 31, 2025 data exists")
                else:
                    print("   ❌ July 31, 2025 data NOT found")
            else:
                print("   ❌ tsys_enhanced table NOT found")
    else:
        print("❌ bonds_data.db not found")

# Create a simple test function
def create_test_function():
    """Create a simple function to test treasury yield fetching."""
    test_code = '''
#!/usr/bin/env python3
import sqlite3
import os

def test_treasury_fetch(date_str="2025-07-31"):
    """Test if we can fetch treasury yields."""
    db_path = os.environ.get('DATABASE_PATH', './bonds_data.db')
    print(f"Using database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        return None
        
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT M2Y, M5Y, M10Y FROM tsys_enhanced WHERE Date = '{date_str}'")
            row = cursor.fetchone()
            if row:
                print(f"Treasury yields for {date_str}: 2Y={row[0]:.3f}%, 5Y={row[1]:.3f}%, 10Y={row[2]:.3f}%")
                return {"2Y": row[0], "5Y": row[1], "10Y": row[2]}
            else:
                print(f"No treasury yields found for {date_str}")
                return None
    except Exception as e:
        print(f"Database error: {e}")
        return None

if __name__ == "__main__":
    test_treasury_fetch()
'''
    
    with open('test_treasury_fetch.py', 'w') as f:
        f.write(test_code)
    print("\n✅ Created test_treasury_fetch.py")

def suggest_fixes():
    """Suggest fixes for the spread calculation issue."""
    print("\n🔧 Suggested Fixes:")
    print("=" * 50)
    print("""
1. **Add Error Logging**: Update google_analysis10.py with better error handling
   - Log when treasury yields are not found
   - Log the actual error messages
   - Log which database path is being used

2. **Check Database Path**: Ensure production uses correct database
   - GCS deployment might have different paths
   - Environment variable DATABASE_PATH might be wrong

3. **Fallback Strategy**: Add fallback when treasury yields unavailable
   - Return null spreads gracefully
   - Add metadata indicating why spread is null

4. **Test in Production**: Deploy test endpoint
   - Add /api/v1/debug/treasury-yields endpoint
   - Check if database is accessible in production

5. **Quick Fix**: Add try-catch around spread calculation
   ```python
   # In analytics dict creation:
   'spread': g_spread if g_spread is not None else None,
   'z_spread': z_spread if z_spread is not None else None,
   ```
""")

if __name__ == "__main__":
    check_production_database()
    create_test_function()
    suggest_fixes()