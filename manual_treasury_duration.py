#!/usr/bin/env python3
"""
Manual Treasury Bond Duration Calculation
Bond: US TREASURY N/B, 3%, 15-Aug-2052
Price: 71.66
Target Duration: 16.35 (to verify)
"""

import QuantLib as ql

def calculate_treasury_duration():
    print("🔢 Manual Treasury Bond Duration Calculation")
    print("=" * 50)
    print("Bond: US TREASURY N/B, 3%, 15-Aug-2052")
    print("Price: 71.66")
    print()

    # Set up QuantLib calculation date (settlement date)
    settlement_date = ql.Date(30, 7, 2025)
    ql.Settings.instance().evaluationDate = settlement_date
    
    print(f"Settlement Date: {settlement_date}")

    # Treasury bond parameters
    face_value = 100.0
    coupon_rate = 0.03  # 3%
    price = 71.66

    # US Treasury conventions
    day_count = ql.ActualActual(ql.ActualActual.ISDA)
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    business_convention = ql.Following
    frequency = ql.Semiannual  # Treasury bonds pay semiannually
    settlement_days = 1
    compounding = ql.Compounded

    # Maturity date: August 15, 2052
    maturity_date = ql.Date(15, 8, 2052)
    
    years_to_maturity = (maturity_date - settlement_date) / 365.25
    print(f"Maturity Date: {maturity_date}")
    print(f"Time to Maturity: {years_to_maturity:.2f} years")
    print()

    # Create the schedule
    schedule = ql.Schedule(
        settlement_date, maturity_date, ql.Period(frequency),
        calendar, business_convention, business_convention,
        ql.DateGeneration.Backward, False
    )

    num_payments = len(schedule) - 1
    print(f"Number of coupon payments: {num_payments}")
    print(f"Payment Frequency: Semiannual")
    print(f"Day Count: ActualActual_ISDA")
    print()

    # Create the bond
    coupons = [coupon_rate]
    bond = ql.FixedRateBond(
        settlement_days, face_value, schedule, 
        coupons, day_count
    )

    print("✅ Bond Created Successfully")
    print()

    # Calculate clean price and yield
    clean_price = price
    print(f"Clean Price: {clean_price}")

    # Calculate yield to maturity
    bond_yield = bond.bondYield(clean_price, day_count, compounding, frequency)
    print(f"Yield to Maturity: {bond_yield:.4f} ({bond_yield*100:.2f}%)")
    print()

    # Calculate duration using QuantLib
    # Using BondFunctions.duration method
    modified_duration = ql.BondFunctions.duration(
        bond, ql.InterestRate(bond_yield, day_count, compounding, frequency)
    )
    
    print("📊 DURATION CALCULATION:")
    print(f"Modified Duration: {modified_duration:.2f} years")
    print()
    
    # Manual verification using price sensitivity
    delta_yield = 0.0001  # 1 basis point
    
    # Calculate prices at yield +/- 1bp
    yield_up = bond_yield + delta_yield
    yield_down = bond_yield - delta_yield
    
    price_up = bond.cleanPrice(yield_up, day_count, compounding, frequency)
    price_down = bond.cleanPrice(yield_down, day_count, compounding, frequency)
    
    # Manual duration calculation
    duration_manual = (price_down - price_up) / (2 * clean_price * delta_yield)
    
    print("🔍 MANUAL VERIFICATION:")
    print(f"Yield +1bp: {yield_up*100:.4f}% → Price: {price_up:.4f}")
    print(f"Yield -1bp: {yield_down*100:.4f}% → Price: {price_down:.4f}")
    print(f"Manual Duration: {duration_manual:.2f} years")
    print()
    
    # Compare with target
    target_duration = 16.35
    print("🎯 COMPARISON WITH TARGET:")
    print(f"Target Duration: {target_duration:.2f} years")
    print(f"Calculated Duration: {modified_duration:.2f} years")
    print(f"Difference: {abs(modified_duration - target_duration):.2f} years")
    print()
    
    if abs(modified_duration - target_duration) < 0.5:
        print("✅ MATCH: Duration calculation is close to target")
    else:
        print("❌ MISMATCH: Significant difference from target")
        print("   Possible causes:")
        print("   - Different settlement date")
        print("   - Different day count convention")
        print("   - Different compounding frequency")
        print("   - Different yield calculation method")
    
    return {
        'calculated_duration': modified_duration,
        'manual_duration': duration_manual,
        'target_duration': target_duration,
        'yield': bond_yield,
        'price': clean_price
    }

if __name__ == "__main__":
    try:
        result = calculate_treasury_duration()
        print("\n" + "="*50)
        print("SUMMARY:")
        print(f"Calculated Duration: {result['calculated_duration']:.2f} years")
        print(f"Target Duration: {result['target_duration']:.2f} years")
        print(f"Yield: {result['yield']*100:.2f}%")
        
    except Exception as e:
        print(f"Error in calculation: {e}")
        import traceback
        traceback.print_exc()
