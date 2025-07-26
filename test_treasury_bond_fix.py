#!/usr/bin/env python3
"""
🏛️ DIRECT TREASURY BOND TEST - T 3 15/08/2052
Test the fixed calculate_bond_metrics_using_shared_engine function
ISIN: US912810TJ79, Price: 71.66, Coupon: 3%, Maturity: 15-Aug-2052
"""

import os
import sys
import QuantLib as ql
import pandas as pd
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path to import google_analysis10 functions
sys.path.insert(0, '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

# Import the fixed functions
from google_analysis10 import (
    calculate_bond_metrics_with_conventions_using_shared_engine,
    fetch_treasury_yields,
    create_treasury_curve,
    parse_date
)

def test_treasury_bond_direct():
    """
    Test the Treasury bond T 3 15/08/2052 directly with the fixed function
    """
    logger.info("🏛️ TESTING TREASURY BOND T 3 15/08/2052 WITH FIXED FUNCTION")
    
    # Bond data from the portfolio
    isin = "US912810TJ79"
    coupon = 3.0 / 100.0  # 3% as decimal
    maturity_date = "2052-08-15"  # August 15, 2052
    price = 71.66
    
    # Use current date as trade date (this should now be dynamic!)
    trade_date_str = "2025-07-21"  # Today's date
    trade_date_ql = parse_date(trade_date_str)
    
    logger.info(f"🔍 BOND DETAILS:")
    logger.info(f"   ISIN: {isin}")
    logger.info(f"   Coupon: {coupon*100:.1f}%")
    logger.info(f"   Maturity: {maturity_date}")
    logger.info(f"   Price: {price}")
    logger.info(f"   Trade Date: {trade_date_str} -> {trade_date_ql}")
    
    # Database path
    db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db'
    
    if not os.path.exists(db_path):
        db_path = './bonds_data.db'  # Fallback
    
    logger.info(f"📊 Using database: {db_path}")
    
    try:
        # Step 1: Get Treasury yields for the trade date
        logger.info("🔍 Step 1: Fetching Treasury yields...")
        yield_dict = fetch_treasury_yields(pd.to_datetime(trade_date_str), db_path)
        logger.info(f"✅ Treasury yields: {yield_dict}")
        
        # Step 2: Create Treasury curve
        logger.info("📈 Step 2: Creating Treasury curve...")
        treasury_handle = create_treasury_curve(yield_dict, trade_date_ql)
        logger.info(f"✅ Treasury curve created successfully")
        
        # Step 3: Test the PROPER QuantLib function with FIXED Treasury curve
        logger.info("🔧 Step 3: Testing PROPER QuantLib with FIXED Treasury curve...")
        logger.info(f"🎯 Using: Fixed Treasury curve (FixedRateBondHelper) + Accurate QuantLib + Dynamic settlement")
        logger.info(f"🎯 Settlement Date: {trade_date_str}")
        
        # Define Treasury conventions for accurate calculation
        treasury_conventions = {
            'day_count': 'ActualActual_Bond',  # FIXED: Use Bond not ISDA for consistency
            'business_convention': 'Following', 
            'frequency': 'Semiannual',
            'treasury_override': True  # This is a US Treasury
        }
        
        logger.info(f"🏛️ Treasury Conventions: {treasury_conventions}")
        
        bond_yield, bond_duration, spread, accrued_interest, error_msg = calculate_bond_metrics_with_conventions_using_shared_engine(
            isin=isin,
            coupon=coupon,
            maturity_date=maturity_date,
            price=price,
            trade_date=trade_date_ql,  # This is the QuantLib date object
            treasury_handle=treasury_handle,
            ticker_conventions=treasury_conventions,
            validated_db_path=None
        )
        
        # Step 4: Display results
        logger.info("📊 RESULTS:")
        if error_msg:
            logger.error(f"❌ Error: {error_msg}")
            return False
        else:
            logger.info(f"✅ SUCCESS! Treasury bond calculated:")
            logger.info(f"   🎯 Yield: {bond_yield:.5f}%")
            logger.info(f"   ⏰ Duration: {bond_duration:.5f} years")
            logger.info(f"   📈 Spread: {spread:.2f} bps")
            logger.info(f"   💰 Accrued Interest: {accrued_interest:.5f}%")
            
            # Expected values (from the document)
            expected_yield = 4.89916
            expected_duration = 16.35658
            
            logger.info(f"📋 COMPARISON WITH EXPECTED VALUES:")
            logger.info(f"   Expected Yield: {expected_yield:.5f}% vs Calculated: {bond_yield:.5f}%")
            logger.info(f"   Expected Duration: {expected_duration:.5f} vs Calculated: {bond_duration:.5f}")
            
            # Check if values are reasonable
            yield_diff = abs(bond_yield - expected_yield)
            duration_diff = abs(bond_duration - expected_duration)
            
            logger.info(f"🔍 ACCURACY CHECK:")
            logger.info(f"   Yield difference: {yield_diff:.5f}%")
            logger.info(f"   Duration difference: {duration_diff:.5f} years")
            
            if yield_diff < 0.1 and duration_diff < 0.5:
                logger.info("✅ EXCELLENT: Results match expected values closely!")
                return True
            elif yield_diff < 0.5 and duration_diff < 1.0:
                logger.info("⚠️  GOOD: Results are reasonable but may need fine-tuning")
                return True
            else:
                logger.warning("❌ CONCERN: Results differ significantly from expected")
                return False
                
    except Exception as e:
        logger.error(f"❌ EXCEPTION during Treasury bond test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_settlement_date_behavior():
    """
    Test that the function is actually using different settlement dates
    """
    logger.info("🔍 TESTING SETTLEMENT DATE BEHAVIOR...")
    
    # Test with two different trade dates to confirm dynamic behavior
    isin = "US912810TJ79"
    coupon = 3.0 / 100.0  
    maturity_date = "2052-08-15"
    price = 71.66
    db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db'
    
    try:
        # Treasury conventions for testing - FIXED: Consistent ActualActual_Bond
        treasury_conventions = {
            'day_count': 'ActualActual_Bond',  # FIXED: Use Bond not ISDA for consistency
            'business_convention': 'Following', 
            'frequency': 'Semiannual',
            'treasury_override': True
        }
        
        # Test Date 1: 2025-06-30 (the old hardcoded date)
        trade_date1 = parse_date("2025-06-30")
        yield_dict1 = fetch_treasury_yields(pd.to_datetime("2025-06-30"), db_path)
        treasury_handle1 = create_treasury_curve(yield_dict1, trade_date1)
        
        result1 = calculate_bond_metrics_with_conventions_using_shared_engine(
            isin, coupon, maturity_date, price, trade_date1, treasury_handle1, treasury_conventions
        )
        
        # Test Date 2: 2025-07-21 (today)
        trade_date2 = parse_date("2025-07-21")
        yield_dict2 = fetch_treasury_yields(pd.to_datetime("2025-07-21"), db_path)
        treasury_handle2 = create_treasury_curve(yield_dict2, trade_date2)
        
        result2 = calculate_bond_metrics_with_conventions_using_shared_engine(
            isin, coupon, maturity_date, price, trade_date2, treasury_handle2, treasury_conventions
        )
        
        logger.info(f"📊 SETTLEMENT DATE COMPARISON:")
        logger.info(f"   Date 1 (2025-06-30): Yield={result1[0]:.5f}%, Duration={result1[1]:.5f}")
        logger.info(f"   Date 2 (2025-07-21): Yield={result2[0]:.5f}%, Duration={result2[1]:.5f}")
        
        if result1[0] != result2[0] or result1[1] != result2[1]:
            logger.info("✅ EXCELLENT: Function is using dynamic dates (results differ)")
            return True
        else:
            logger.warning("⚠️  WARNING: Results are identical - may still be using fixed dates")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception in settlement date test: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 STARTING TREASURY BOND DIRECT TEST")
    logger.info("="*60)
    
    # Test 1: Direct Treasury bond calculation
    success1 = test_treasury_bond_direct()
    
    logger.info("="*60)
    
    # Test 2: Settlement date behavior
    success2 = test_settlement_date_behavior()
    
    logger.info("="*60)
    logger.info("📋 FINAL RESULTS:")
    logger.info(f"   Treasury Bond Test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    logger.info(f"   Settlement Date Test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        logger.info("🎉 ALL TESTS PASSED - FIX IS WORKING!")
    else:
        logger.info("⚠️  SOME TESTS FAILED - MAY NEED ADDITIONAL FIXES")
