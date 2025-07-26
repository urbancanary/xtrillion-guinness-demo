#!/usr/bin/env python3
"""
Direct test of pure QuantLib without any processing pipeline
to isolate where the settlement date is being changed
"""

import QuantLib as ql

def test_pure_quantlib_direct():
    """Test QuantLib directly without any processing pipeline"""
    
    print("🧪 DIRECT QUANTLIB TEST - No Processing Pipeline")
    print("=" * 60)
    
    # Bond parameters - exactly as specified
    coupon_rate = 3.0 / 100.0
    price = 71.66
    settlement_date = ql.Date(30, 6, 2025)  # EXACTLY June 30, 2025
    maturity_date = ql.Date(15, 8, 2052)
    
    print(f"Input settlement date: {settlement_date}")
    print(f"Input maturity date: {maturity_date}")
    print(f"Input price: {price}")
    print(f"Input coupon: {coupon_rate * 100}%")
    print()
    
    # Set evaluation date
    ql.Settings.instance().evaluationDate = settlement_date
    print(f"QuantLib evaluation date set to: {settlement_date}")
    
    # Treasury conventions
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    business_convention = ql.Following
    frequency = ql.Semiannual
    
    # Check if settlement date gets adjusted
    adjusted_settlement = calendar.adjust(settlement_date, business_convention)
    print(f"Calendar adjusted settlement: {adjusted_settlement}")
    
    if adjusted_settlement != settlement_date:
        print(f"❌ PROBLEM: Settlement date moved from {settlement_date} to {adjusted_settlement}")
        print("This will cause zero accrued interest!")
    else:
        print(f"✅ Settlement date unchanged: {settlement_date}")
    
    print()
    
    # Use the BondHelper approach - no manual date calculations
    schedule_start = ql.Date(15, 2, 2025)  # Simple, reasonable start
    
    schedule = ql.Schedule(
        schedule_start, maturity_date, ql.Period(frequency),
        calendar, business_convention, business_convention,
        ql.DateGeneration.Backward, False
    )
    
    print(f"Schedule start: {schedule_start}")
    print(f"Schedule periods: {len(schedule) - 1}")
    print(f"First payment: {schedule[1] if len(schedule) > 1 else 'N/A'}")
    print()
    
    # Create bond
    bond = ql.FixedRateBond(0, 100.0, schedule, [coupon_rate], day_count)
    
    # Calculate with ORIGINAL settlement date (not adjusted)
    print("📊 CALCULATING WITH ORIGINAL SETTLEMENT DATE:")
    yield_orig = bond.bondYield(price, day_count, ql.Compounded, frequency, settlement_date)
    accrued_orig = bond.accruedAmount(settlement_date)
    
    print(f"Yield: {yield_orig * 100:.5f}%")
    print(f"Accrued: ${accrued_orig:.4f}")
    
    # Find accrual details
    for cf in bond.cashflows():
        try:
            coupon_cf = ql.as_coupon(cf)
            if coupon_cf:
                start = coupon_cf.accrualStartDate()
                end = coupon_cf.accrualEndDate()
                
                if start <= settlement_date < end:
                    days = day_count.dayCount(start, settlement_date)
                    accrued_per_mil = (accrued_orig / 100.0) * 1000000
                    
                    print(f"Current period: {start} to {end}")
                    print(f"Days accrued: {days}")
                    print(f"Accrued per million: {accrued_per_mil:.2f}")
                    break
        except:
            continue
    
    print()
    
    # Also test with adjusted settlement date for comparison
    if adjusted_settlement != settlement_date:
        print("📊 CALCULATING WITH ADJUSTED SETTLEMENT DATE:")
        yield_adj = bond.bondYield(price, day_count, ql.Compounded, frequency, adjusted_settlement)
        accrued_adj = bond.accruedAmount(adjusted_settlement)
        
        print(f"Yield: {yield_adj * 100:.5f}%")
        print(f"Accrued: ${accrued_adj:.4f}")
        
        # Find accrual details for adjusted date
        for cf in bond.cashflows():
            try:
                coupon_cf = ql.as_coupon(cf)
                if coupon_cf:
                    start = coupon_cf.accrualStartDate()
                    end = coupon_cf.accrualEndDate()
                    
                    if start <= adjusted_settlement < end:
                        days = day_count.dayCount(start, adjusted_settlement)
                        accrued_per_mil = (accrued_adj / 100.0) * 1000000
                        
                        print(f"Adjusted period: {start} to {end}")
                        print(f"Adjusted days accrued: {days}")
                        print(f"Adjusted accrued per million: {accrued_per_mil:.2f}")
                        break
            except:
                continue
    
    print()
    print("🎯 Expected Bloomberg values:")
    print("Duration: 16.3578392273866 years")
    print("Accrued per Million: 11,187.845")
    print("Days Accrued: Should be 132")

if __name__ == "__main__":
    test_pure_quantlib_direct()
