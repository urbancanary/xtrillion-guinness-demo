#!/usr/bin/env python3
"""
CORRECTED YTW + Accrued Convention Finder
Test all 22 convention combinations (11 day counts × 2 frequencies)
Find the closest YTW match among those with accrued difference ≤ 0.01
"""

import sqlite3
import QuantLib as ql
from datetime import datetime
import sys

# Define all day count conventions (11 total)
DAY_COUNT_CONVENTIONS = {
    "Thirty360_BondBasis": ql.Thirty360(ql.Thirty360.BondBasis),
    "Thirty360_USA": ql.Thirty360(ql.Thirty360.USA), 
    "Thirty360_European": ql.Thirty360(ql.Thirty360.European),
    "Thirty360_Italian": ql.Thirty360(ql.Thirty360.Italian),
    "Actual360": ql.Actual360(),
    "Actual365Fixed": ql.Actual365Fixed(),
    "ActualActual_ISMA": ql.ActualActual(ql.ActualActual.ISMA),
    "ActualActual_ISDA": ql.ActualActual(ql.ActualActual.ISDA),
    "ActualActual_Bond": ql.ActualActual(ql.ActualActual.Bond),
    "ActualActual_Historical": ql.ActualActual(ql.ActualActual.Historical),
    "ActualActual_AFB": ql.ActualActual(ql.ActualActual.AFB)
}

# Define payment frequencies (2 total)  
PAYMENT_FREQUENCIES = {
    "Annual": ql.Annual,
    "Semiannual": ql.Semiannual
}

def calculate_ytw_and_accrued(bond_data, day_count, frequency):
    """Calculate YTW and accrued interest for given conventions"""
    try:
        # Parse bond data
        coupon_rate = float(bond_data['coupon_rate'])
        maturity_str = bond_data['maturity_date'] 
        price = float(bond_data['price'])
        par_value = float(bond_data['par_value'])
        
        # Parse maturity date (MM/DD/YY format)
        parts = maturity_str.split('/')
        month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
        year = year + 2000 if year < 50 else year + 1900
        maturity_date = datetime(year, month, day)
        
        # Settlement date
        settlement_date = datetime(2025, 4, 18)
        
        # Convert to QuantLib dates
        ql_settlement = ql.Date(settlement_date.day, settlement_date.month, settlement_date.year)
        ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
        ql.Settings.instance().evaluationDate = ql_settlement
        
        # Create bond schedule
        us_calendar = ql.UnitedStates(ql.UnitedStates.Settlement)
        business_convention = ql.Following
        
        # Estimate issue date (conservative approach)
        issue_date = datetime(maturity_date.year - 10, maturity_date.month, maturity_date.day)
        ql_issue = ql.Date(issue_date.day, issue_date.month, issue_date.year)
        
        schedule = ql.Schedule(
            ql_issue, ql_maturity, ql.Period(frequency),
            us_calendar, business_convention, business_convention,
            ql.DateGeneration.Backward, False
        )
        
        # Create FixedRateBond
        bond = ql.FixedRateBond(
            0, 100, schedule, [coupon_rate / 100.0], 
            day_count, business_convention, 100.0, ql_issue
        )
        
        # Calculate accrued interest
        accrued_percentage = bond.accruedAmount(ql_settlement) 
        accrued_amount = (accrued_percentage / 100.0) * par_value
        
        # Calculate YTW using bond engine
        bond_engine = ql.DiscountingBondEngine(ql.FlatForward(ql_settlement, 0.05, day_count))
        bond.setPricingEngine(bond_engine)
        
        # Calculate yield from price
        clean_price = price
        ytw = bond.bondYield(clean_price, day_count, ql.Compounded, frequency) * 100
        
        return {
            'ytw': ytw,
            'accrued': accrued_amount,
            'success': True
        }
        
    except Exception as e:
        return {
            'ytw': None,
            'accrued': None, 
            'success': False,
            'error': str(e)
        }

def find_best_ytw_accrued_match(bond_data, bloomberg_ytw, bloomberg_accrued):
    """Find best YTW match among conventions with accrued ≤ 0.01 difference"""
    
    print(f"Testing {len(DAY_COUNT_CONVENTIONS)} day count × {len(PAYMENT_FREQUENCIES)} frequency = {len(DAY_COUNT_CONVENTIONS) * len(PAYMENT_FREQUENCIES)} total combinations")
    
    # Test all 22 combinations
    valid_combinations = []
    
    for dc_name, day_count in DAY_COUNT_CONVENTIONS.items():
        for freq_name, frequency in PAYMENT_FREQUENCIES.items():
            
            result = calculate_ytw_and_accrued(bond_data, day_count, frequency)
            
            if result['success']:
                accrued_diff = abs(result['accrued'] - bloomberg_accrued)
                ytw_diff = abs(result['ytw'] - bloomberg_ytw) if result['ytw'] else float('inf')
                
                combo_name = f"{dc_name}|{freq_name}"
                
                print(f"  {combo_name}: YTW={result['ytw']:.4f} (diff={ytw_diff:.4f}), Accrued={result['accrued']:.6f} (diff={accrued_diff:.6f})")
                
                # Keep combinations where accrued difference ≤ 0.01
                if accrued_diff <= 0.01:
                    valid_combinations.append({
                        'combination': combo_name,
                        'day_count': dc_name, 
                        'frequency': freq_name,
                        'ytw': result['ytw'],
                        'accrued': result['accrued'],
                        'ytw_diff': ytw_diff,
                        'accrued_diff': accrued_diff
                    })
    
    if not valid_combinations:
        return None
        
    # Among valid combinations, find the one with closest YTW match
    best_combo = min(valid_combinations, key=lambda x: x['ytw_diff'])
    
    print(f"\n✅ Found {len(valid_combinations)} combinations with accrued ≤ 0.01")
    print(f"🎯 Best YTW match: {best_combo['combination']} (YTW diff: {best_combo['ytw_diff']:.4f}, Accrued diff: {best_combo['accrued_diff']:.6f})")
    
    return best_combo

def test_bond_with_ytw_accrued():
    """Test the YTW + accrued logic on a sample bond"""
    
    # Connect to database
    db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9/bonds_data.db'
    conn = sqlite3.connect(db_path)
    
    # Get a bond with YTW data
    cursor = conn.cursor()
    cursor.execute("""
        SELECT isin, description, coupon_rate, maturity_date, price, par_value, ytw, bloomberg_accrued
        FROM bonds_data 
        WHERE ytw IS NOT NULL AND bloomberg_accrued IS NOT NULL 
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    if not row:
        print("No bonds found with YTW and accrued data")
        return
        
    # Parse bond data
    bond_data = {
        'isin': row[0],
        'description': row[1], 
        'coupon_rate': row[2],
        'maturity_date': row[3],
        'price': row[4],
        'par_value': row[5]
    }
    
    bloomberg_ytw = float(row[6])
    bloomberg_accrued = float(row[7])
    
    print(f"Testing bond: {bond_data['description']}")
    print(f"Bloomberg YTW: {bloomberg_ytw:.4f}")
    print(f"Bloomberg Accrued: {bloomberg_accrued:.6f}")
    print(f"Coupon: {bond_data['coupon_rate']:.3f}%")
    print(f"Maturity: {bond_data['maturity_date']}")
    print(f"Price: {bond_data['price']:.4f}")
    print()
    
    # Find best match
    best_match = find_best_ytw_accrued_match(bond_data, bloomberg_ytw, bloomberg_accrued)
    
    if best_match:
        print(f"\n🎯 FINAL RESULT:")
        print(f"Best combination: {best_match['combination']}")
        print(f"YTW: {best_match['ytw']:.4f} (Bloomberg: {bloomberg_ytw:.4f}, diff: {best_match['ytw_diff']:.4f})")
        print(f"Accrued: {best_match['accrued']:.6f} (Bloomberg: {bloomberg_accrued:.6f}, diff: {best_match['accrued_diff']:.6f})")
    else:
        print("❌ No valid combinations found (all accrued differences > 0.01)")
    
    conn.close()

if __name__ == "__main__":
    test_bond_with_ytw_accrued()
