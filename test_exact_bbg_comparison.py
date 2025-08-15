#!/usr/bin/env python3
"""
Test exact Bloomberg comparison for T 3 15/08/52
Bloomberg YTM: 4.89916%
Our YTM: 4.899064%
Difference: 0.000096% (0.96 basis points of a percent)
"""

import QuantLib as ql
from datetime import datetime

def test_treasury_calculation():
    """Test T 3 15/08/52 @ 71.66 on 2025-06-30"""
    
    # Setup dates
    calculation_date = ql.Date(30, 6, 2025)
    ql.Settings.instance().evaluationDate = calculation_date
    
    # Bond parameters
    issue_date = ql.Date(15, 8, 2022)
    maturity_date = ql.Date(15, 8, 2052)
    coupon_rate = 3.0 / 100.0  # 3%
    price = 71.66
    
    # Test different day count conventions
    conventions = [
        ("ActualActual(Bond)", ql.ActualActual(ql.ActualActual.Bond)),
        ("ActualActual(ISDA)", ql.ActualActual(ql.ActualActual.ISDA)),
        ("ActualActual(ISMA)", ql.ActualActual(ql.ActualActual.ISMA)),
        ("ActualActual(AFB)", ql.ActualActual(ql.ActualActual.AFB)),
    ]
    
    print(f"Testing T 3 15/08/52 @ {price} on 2025-06-30")
    print(f"Bloomberg YTM: 4.89916%")
    print("=" * 60)
    
    for name, day_counter in conventions:
        # Create schedule
        schedule = ql.Schedule(
            issue_date,
            maturity_date,
            ql.Period(ql.Semiannual),
            ql.UnitedStates(ql.UnitedStates.GovernmentBond),
            ql.Following,
            ql.Following,
            ql.DateGeneration.Backward,
            True  # end of month
        )
        
        # Create bond
        bond = ql.FixedRateBond(
            0,  # settlement days
            100.0,  # face value
            schedule,
            [coupon_rate],
            day_counter
        )
        
        # Calculate YTM with different compounding
        ytm_semi = bond.bondYield(
            price,
            day_counter,
            ql.Compounded,
            ql.Semiannual
        ) * 100
        
        ytm_annual = bond.bondYield(
            price,
            day_counter,
            ql.Compounded,
            ql.Annual
        ) * 100
        
        # Calculate with simple rate
        ytm_simple = bond.bondYield(
            price,
            day_counter,
            ql.Simple,
            ql.Annual
        ) * 100
        
        print(f"\n{name}:")
        print(f"  Semi-annual YTM: {ytm_semi:.6f}%")
        print(f"  Annual YTM:      {ytm_annual:.6f}%")
        print(f"  Simple YTM:      {ytm_simple:.6f}%")
        print(f"  Diff from BBG:   {abs(ytm_semi - 4.89916):.6f}% ({abs(ytm_semi - 4.89916)*100:.2f} bps)")
        
        # Check accrued interest
        accrued = bond.accruedAmount(calculation_date)
        clean_price = price
        dirty_price = clean_price + accrued
        
        print(f"  Accrued:         {accrued:.6f}")
        print(f"  Dirty Price:     {dirty_price:.6f}")

if __name__ == "__main__":
    test_treasury_calculation()