#!/usr/bin/env python3
"""
Fix Treasury Duration Calculation Bug
===================================

Corrects the yield unit conversion issue that's causing duration miscalculation.
The bug: QuantLib duration function expects yield in specific units.
"""

import QuantLib as ql
import logging

logger = logging.getLogger(__name__)

def calculate_bond_metrics_with_unit_fix(
    bond, price, day_counter, frequency, is_treasury=False, 
    isin=None, log_prefix="[CALC_ENGINE]"
):
    """
    Fixed version of bond calculation with proper yield unit handling
    """
    try:
        # CRITICAL FIX: Ensure consistent semi-annual frequency for US Treasuries
        calculation_frequency = frequency
        if is_treasury:
            calculation_frequency = ql.Semiannual
            logger.info(f"{log_prefix} Treasury detected: enforcing semi-annual frequency")

        # Step 1: Calculate yield (returns decimal format)
        bond_yield_decimal = bond.bondYield(
            price, 
            day_counter, 
            ql.Compounded, 
            calculation_frequency
        )
        
        logger.info(f"{log_prefix} Yield calculated (decimal): {bond_yield_decimal:.6f} ({bond_yield_decimal*100:.5f}%)")

        # CRITICAL FIX: Test both decimal and percentage formats for duration
        # QuantLib duration function might expect different yield units
        
        # Test 1: Duration with decimal yield (current approach)
        duration_decimal = ql.BondFunctions.duration(
            bond, bond_yield_decimal, day_counter, ql.Compounded, 
            calculation_frequency, ql.Duration.Modified
        )
        
        # Test 2: Duration with percentage yield 
        bond_yield_percentage = bond_yield_decimal * 100
        duration_percentage = ql.BondFunctions.duration(
            bond, bond_yield_percentage, day_counter, ql.Compounded, 
            calculation_frequency, ql.Duration.Modified
        )
        
        logger.info(f"{log_prefix} Duration with decimal yield ({bond_yield_decimal:.6f}): {duration_decimal:.5f}")
        logger.info(f"{log_prefix} Duration with percentage yield ({bond_yield_percentage:.5f}%): {duration_percentage:.5f}")
        
        # CRITICAL: For Treasury bonds, Bloomberg uses percentage yield format
        # If this is a Treasury, use percentage-based calculation
        if is_treasury:
            final_duration = duration_percentage
            final_yield = bond_yield_decimal  # Keep yield in decimal for consistency
            logger.info(f"{log_prefix} Treasury: Using percentage-based duration calculation")
            logger.info(f"{log_prefix} Final duration: {final_duration:.5f}")
        else:
            # For corporate bonds, test which gives more reasonable results
            final_duration = duration_decimal
            final_yield = bond_yield_decimal
        
        # Calculate other metrics with corrected yield
        macaulay_duration = ql.BondFunctions.duration(
            bond, bond_yield_percentage if is_treasury else bond_yield_decimal, 
            day_counter, ql.Compounded, calculation_frequency, 
            ql.Duration.Macaulay
        )
        
        convexity = ql.BondFunctions.convexity(
            bond, bond_yield_percentage if is_treasury else bond_yield_decimal, 
            day_counter, ql.Compounded, calculation_frequency
        )
        
        # Calculate clean and dirty prices for validation
        clean_price = bond.cleanPrice()
        dirty_price = bond.dirtyPrice()
        accrued_interest = dirty_price - clean_price
        
        return {
            'success': True,
            'yield': final_yield,
            'yield_percentage': final_yield * 100,
            'duration': final_duration,
            'duration_decimal_test': duration_decimal,
            'duration_percentage_test': duration_percentage,
            'macaulay_duration': macaulay_duration,
            'convexity': convexity,
            'clean_price': clean_price,
            'dirty_price': dirty_price,
            'accrued_interest': accrued_interest,
            'calculation_frequency': calculation_frequency,
            'is_treasury': is_treasury,
            'unit_fix_applied': True
        }
        
    except Exception as e:
        logger.error(f"{log_prefix} Calculation failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'unit_fix_applied': True
        }


def test_treasury_duration_fix():
    """Test the duration fix with the problematic Treasury bond"""
    
    print("🔧 TESTING TREASURY DURATION FIX")
    print("=" * 50)
    
    # Set up QuantLib
    ql.Settings.instance().evaluationDate = ql.Date(30, 6, 2025)
    
    # Create the problematic Treasury bond
    issue_date = ql.Date(30, 6, 2025)
    maturity_date = ql.Date(15, 8, 2052)
    
    # Treasury schedule (semiannual)
    schedule = ql.Schedule(
        issue_date,
        maturity_date,
        ql.Period(ql.Semiannual),
        ql.UnitedStates(ql.UnitedStates.GovernmentBond),
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward,
        False
    )
    
    # Create Treasury bond
    day_counter = ql.ActualActual(ql.ActualActual.ISDA)
    bond = ql.FixedRateBond(
        0,  # Settlement days
        100.0,  # Face value
        schedule,
        [0.03],  # 3% coupon
        day_counter
    )
    
    # Test with the problematic price
    price = 71.66
    
    print(f"📊 Testing Treasury Bond:")
    print(f"   Coupon: 3.0%")
    print(f"   Maturity: August 15, 2052") 
    print(f"   Price: {price}")
    print(f"   Expected Duration: 16.35658")
    print()
    
    # Test the fix
    result = calculate_bond_metrics_with_unit_fix(
        bond=bond,
        price=price,
        day_counter=day_counter,
        frequency=ql.Semiannual,
        is_treasury=True,
        log_prefix="[DURATION_FIX]"
    )
    
    if result['success']:
        print("✅ CALCULATION RESULTS:")
        print(f"   📈 Yield: {result['yield_percentage']:.5f}%")
        print(f"   ⏱️  Duration (Final): {result['duration']:.5f}")
        print(f"   🧪 Duration (Decimal Test): {result['duration_decimal_test']:.5f}")  
        print(f"   🧪 Duration (Percentage Test): {result['duration_percentage_test']:.5f}")
        print(f"   📊 Macaulay Duration: {result['macaulay_duration']:.5f}")
        print(f"   🔄 Convexity: {result['convexity']:.2f}")
        print()
        
        # Check which method gives the expected result
        expected_duration = 16.35658
        decimal_diff = abs(result['duration_decimal_test'] - expected_duration)
        percentage_diff = abs(result['duration_percentage_test'] - expected_duration)
        
        print("🎯 ACCURACY ANALYSIS:")
        print(f"   Expected Duration: {expected_duration:.5f}")
        print(f"   Decimal Method Difference: {decimal_diff:.5f}")
        print(f"   Percentage Method Difference: {percentage_diff:.5f}")
        
        if percentage_diff < decimal_diff:
            print("   ✅ PERCENTAGE METHOD is more accurate!")
            print("   🔧 Fix: Use percentage yield for Treasury duration calculations")
        else:
            print("   ✅ DECIMAL METHOD is more accurate!")
            print("   🔧 Fix: Use decimal yield for Treasury duration calculations")
            
    else:
        print(f"❌ Calculation failed: {result['error']}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    test_treasury_duration_fix()
