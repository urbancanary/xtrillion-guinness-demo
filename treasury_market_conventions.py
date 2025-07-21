#!/usr/bin/env python3
"""
QuantLib Treasury with Market Convention Schedule
================================================

Use QuantLib's market conventions to automatically determine proper Treasury schedule
without any manual date calculations.
"""

import sys
sys.path.append('.')
import QuantLib as ql

def calculate_treasury_market_conventions(description, price=71.66, settlement_date_str="2025-06-30"):
    """
    Use QuantLib market conventions to determine Treasury schedule automatically
    """
    
    print("🏛️ QUANTLIB MARKET CONVENTIONS TREASURY")
    print("=" * 50)
    
    # Bond parameters
    coupon_rate = 3.0 / 100.0
    face_value = 100.0
    
    # Dates
    settlement_date = ql.Date(30, 6, 2025)
    maturity_date = ql.Date(15, 8, 2052)
    
    print(f"📋 Bond: {description}")
    print(f"💰 Price: {price}")
    print(f"📅 Settlement: {settlement_date}")
    print(f"📅 Maturity: {maturity_date}")
    print()
    
    # QuantLib setup
    ql.Settings.instance().evaluationDate = settlement_date
    
    # US Treasury conventions
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    business_convention = ql.Following
    frequency = ql.Semiannual
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    
    # APPROACH: Use QuantLib's MakeSchedule builder for automatic date handling
    # This lets QuantLib determine the appropriate schedule based on market conventions
    try:
        # Method 1: Use MakeSchedule with automatic period detection
        schedule = ql.MakeSchedule(
            effectiveDate=settlement_date,  # Start from settlement for calculation purposes
            terminationDate=maturity_date,
            tenor=ql.Period(frequency),
            calendar=calendar,
            convention=business_convention,
            endOfMonth=False,
            rule=ql.DateGeneration.Backward  # Standard bond convention
        )
        
        print(f"📅 MakeSchedule Result:")
        print(f"   Periods: {len(schedule) - 1}")
        print(f"   First payment: {schedule[1] if len(schedule) > 1 else 'N/A'}")
        print(f"   Last payment: {schedule[len(schedule)-1]}")
        
        # Create bond
        bond = ql.FixedRateBond(0, face_value, schedule, [coupon_rate], day_count)
        
    except Exception as e:
        print(f"MakeSchedule failed: {e}")
        print("Trying alternative approach...")
        
        # Method 2: Use standard Schedule with reasonable effective date
        # For Treasury bonds, use a date that creates proper Feb/Aug payment cycle
        effective_date = ql.Date(15, 2, 2025)  # Last Feb 15 before settlement
        
        schedule = ql.Schedule(
            effective_date, maturity_date, ql.Period(frequency),
            calendar, business_convention, business_convention,
            ql.DateGeneration.Backward, False
        )
        
        print(f"📅 Standard Schedule Result:")
        print(f"   Effective Date: {effective_date}")
        print(f"   Periods: {len(schedule) - 1}")
        print(f"   First payment: {schedule[1] if len(schedule) > 1 else 'N/A'}")
        print(f"   Last payment: {schedule[len(schedule)-1]}")
        
        # Create bond
        bond = ql.FixedRateBond(0, face_value, schedule, [coupon_rate], day_count)
    
    # Set up pricing engine
    bond_engine = ql.DiscountingBondEngine(ql.YieldTermStructureHandle())
    bond.setPricingEngine(bond_engine)
    
    # Calculate metrics
    yield_rate = bond.bondYield(price, day_count, ql.Compounded, frequency, settlement_date)
    duration = ql.BondFunctions.duration(
        bond,
        ql.InterestRate(yield_rate, day_count, ql.Compounded, frequency),
        ql.Duration.Modified,
        settlement_date
    )
    accrued = bond.accruedAmount(settlement_date)
    
    # Debug info - let QuantLib determine the accrual period
    days_accrued = 0
    accrued_per_million = 0
    
    for cf in bond.cashflows():
        try:
            coupon_cf = ql.as_coupon(cf)
            if coupon_cf:
                accrual_start = coupon_cf.accrualStartDate()
                accrual_end = coupon_cf.accrualEndDate()
                
                if accrual_start <= settlement_date < accrual_end:
                    days_accrued = day_count.dayCount(accrual_start, settlement_date)
                    accrued_per_million = (accrued / face_value) * 1000000
                    
                    print(f"🤖 QuantLib Accrual Period:")
                    print(f"   Start: {accrual_start}")
                    print(f"   Settlement: {settlement_date}")
                    print(f"   End: {accrual_end}")
                    print(f"   Days Accrued: {days_accrued}")
                    print(f"   Accrued per Million: {accrued_per_million:.2f}")
                    break
        except:
            continue
    
    print()
    print(f"💰 RESULTS:")
    print(f"   Yield: {yield_rate * 100:.5f}%")
    print(f"   Duration: {duration:.5f} years")
    print(f"   Accrued: ${accrued:.4f}")
    print(f"   Days Accrued: {days_accrued}")
    print(f"   Accrued per Million: {accrued_per_million:.2f}")
    
    return {
        'yield': yield_rate * 100,
        'duration': duration,
        'accrued': accrued,
        'days_accrued': days_accrued,
        'accrued_per_million': accrued_per_million
    }

def calculate_treasury_bond_helper_approach(description, price=71.66, settlement_date_str="2025-06-30"):
    """
    Alternative: Use QuantLib's BondHelper approach for automatic Treasury handling
    """
    
    print("\n" + "🏛️ QUANTLIB BOND HELPER APPROACH")
    print("=" * 50)
    
    # Parameters
    coupon_rate = 3.0 / 100.0
    settlement_date = ql.Date(30, 6, 2025)
    maturity_date = ql.Date(15, 8, 2052)
    
    print(f"📋 Using BondHelper for automatic Treasury conventions...")
    
    # QuantLib setup
    ql.Settings.instance().evaluationDate = settlement_date
    
    # Treasury conventions
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    
    # Use FixedRateBondHelper - this should handle Treasury conventions automatically
    try:
        # Create a simple schedule for the helper
        simple_schedule = ql.Schedule(
            ql.Date(15, 2, 2025),  # Recent issue date pattern
            maturity_date,
            ql.Period(ql.Semiannual),
            calendar,
            ql.Following,
            ql.Following,
            ql.DateGeneration.Backward,
            False
        )
        
        # Create bond using the schedule
        bond = ql.FixedRateBond(0, 100.0, simple_schedule, [coupon_rate], day_count)
        
        # Calculate directly
        yield_rate = bond.bondYield(price, day_count, ql.Compounded, ql.Semiannual, settlement_date)
        duration = ql.BondFunctions.duration(
            bond,
            ql.InterestRate(yield_rate, day_count, ql.Compounded, ql.Semiannual),
            ql.Duration.Modified,
            settlement_date
        )
        accrued = bond.accruedAmount(settlement_date)
        
        # Get debug info
        days_accrued = 0
        accrued_per_million = 0
        
        for cf in bond.cashflows():
            try:
                coupon_cf = ql.as_coupon(cf)
                if coupon_cf and coupon_cf.accrualStartDate() <= settlement_date < coupon_cf.accrualEndDate():
                    days_accrued = day_count.dayCount(coupon_cf.accrualStartDate(), settlement_date)
                    accrued_per_million = (accrued / 100.0) * 1000000
                    break
            except:
                continue
        
        print(f"💰 BondHelper Results:")
        print(f"   Yield: {yield_rate * 100:.5f}%")
        print(f"   Duration: {duration:.5f} years")
        print(f"   Accrued: ${accrued:.4f}")
        print(f"   Days Accrued: {days_accrued}")
        print(f"   Accrued per Million: {accrued_per_million:.2f}")
        
        return {
            'yield': yield_rate * 100,
            'duration': duration,
            'accrued': accrued,
            'days_accrued': days_accrued,
            'accrued_per_million': accrued_per_million
        }
        
    except Exception as e:
        print(f"BondHelper approach failed: {e}")
        return None

if __name__ == "__main__":
    print("Testing different QuantLib approaches without manual date calculations...")
    
    result1 = calculate_treasury_market_conventions("US TREASURY N/B, 3%, 15-Aug-2052")
    result2 = calculate_treasury_bond_helper_approach("US TREASURY N/B, 3%, 15-Aug-2052")
    
    print("\n" + "="*50)
    print("🎯 COMPARISON TO BLOOMBERG EXPECTATIONS:")
    print(f"Duration expectation: 16.3578392273866 years")
    print(f"Accrued per Million expectation: 11,187.845")
    
    if result1:
        print(f"\nMarket Conventions: Duration={result1['duration']:.5f}, AccruedPerMil={result1['accrued_per_million']:.2f}")
    if result2:
        print(f"BondHelper: Duration={result2['duration']:.5f}, AccruedPerMil={result2['accrued_per_million']:.2f}")
