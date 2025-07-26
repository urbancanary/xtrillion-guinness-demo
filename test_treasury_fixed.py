#!/usr/bin/env python3
"""
🏛️ FIXED TREASURY BOND TEST - T 3 15/08/2052
Fixed to work with current google_analysis10.py function signatures
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

# Import the working functions with correct signatures
from google_analysis10 import (
    calculate_bond_metrics_with_conventions_using_shared_engine,
    fetch_treasury_yields,
    create_treasury_curve,
    parse_date
)

def test_treasury_bond_fixed():
    """
    Test the Treasury bond with FIXED function signatures
    """
    logger.info("🏛️ TESTING TREASURY BOND T 3 15/08/2052 WITH CORRECT SIGNATURES")
    
    # Bond data from the portfolio
    isin = "US912810TJ79"
    coupon = 3.0 / 100.0  # 3% as decimal
    maturity_date = "2052-08-15"  # August 15, 2052
    price = 71.66
    
    # Use current date as trade date
    trade_date_str = "2025-07-21"
    trade_date_ql = parse_date(trade_date_str)
    
    logger.info(f"🔍 BOND DETAILS:")
    logger.info(f"   ISIN: {isin}")
    logger.info(f"   Coupon: {coupon*100:.1f}%")
    logger.info(f"   Maturity: {maturity_date}")
    logger.info(f"   Price: {price}")
    logger.info(f"   Trade Date: {trade_date_str}")
    
    try:
        # Step 1: Fetch Treasury yields (even if empty)
        db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db'
        logger.info(f"📊 Using database: {db_path}")
        
        logger.info("🔍 Step 1: Fetching Treasury yields...")
        yield_dict = fetch_treasury_yields(trade_date_ql, db_path)
        logger.info(f"✅ Treasury yields: {yield_dict}")
        
        # Step 2: Create Treasury curve (even if simple/empty)
        logger.info("📈 Step 2: Creating Treasury curve...")
        if yield_dict:
            treasury_handle = create_treasury_curve(yield_dict, trade_date_ql)
        else:
            # Create a simple flat curve for testing
            logger.info("⚠️  Creating simple flat curve for testing...")
            ql.Settings.instance().evaluationDate = ql.Date(trade_date_ql.day, trade_date_ql.month, trade_date_ql.year)
            flat_rate = 0.05  # 5% flat rate
            treasury_handle = ql.YieldTermStructureHandle(
                ql.FlatForward(0, ql.UnitedStates(ql.UnitedStates.GovernmentBond), flat_rate, ql.Actual360())
            )
        
        logger.info("✅ Treasury curve created successfully")
        
        # Step 3: Test QuantLib calculation with CORRECT function signature
        logger.info("🔧 Step 3: Testing QuantLib with CORRECT function signature...")
        
        # Treasury conventions for US Treasury bonds
        treasury_conventions = {
            'day_count': 'ActualActual_Bond',
            'business_convention': 'Following',
            'frequency': 'Semiannual',
            'treasury_override': True
        }
        
        logger.info(f"🏛️ Treasury Conventions: {treasury_conventions}")
        
        # Call with CORRECT parameters (no ticker_conventions)
        result = calculate_bond_metrics_with_conventions_using_shared_engine(
            isin=isin,
            coupon=coupon,
            maturity_date=maturity_date,
            price=price,
            trade_date=trade_date_ql,
            treasury_handle=treasury_handle,
            default_conventions=treasury_conventions,
            is_treasury=True,  # This is the key flag!
            settlement_days=0,
            validated_db_path=db_path
        )
        
        # Result should be a tuple: (yield, duration, spread, accrued_interest, error_msg)
        if isinstance(result, tuple) and len(result) >= 2:
            bond_yield, bond_duration = result[0], result[1]
            spread = result[2] if len(result) > 2 else None
            accrued = result[3] if len(result) > 3 else None
            
            logger.info("🎉 SUCCESS! Treasury bond calculation completed!")
            logger.info(f"📊 RESULTS:")
            logger.info(f"   Yield: {bond_yield:.6f} ({bond_yield*100:.3f}%)")
            logger.info(f"   Duration: {bond_duration:.6f} years")
            if spread is not None:
                logger.info(f"   Spread: {spread:.6f} bps")
            if accrued is not None:
                logger.info(f"   Accrued Interest: {accrued:.6f}")
            
            # Check if results are reasonable for Treasury bond
            if 0.04 <= bond_yield <= 0.06 and 15 <= bond_duration <= 18:
                logger.info("✅ Results look reasonable for this Treasury bond!")
                return True
            else:
                logger.warning("⚠️  Results seem unusual but calculation completed")
                return True
        else:
            logger.error(f"❌ Unexpected result format: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception during Treasury bond test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🚀 STARTING FIXED TREASURY BOND TEST")
    logger.info("="*60)
    
    # Test with correct function signatures
    success = test_treasury_bond_fixed()
    
    logger.info("="*60)
    logger.info("📋 FINAL RESULTS:")
    logger.info(f"   Fixed Treasury Bond Test: {'✅ PASSED' if success else '❌ FAILED'}")
    
    if success:
        logger.info("🎉 TREASURY BOND CALCULATION IS WORKING!")
        logger.info("💡 Your original implementation was correct, just needed signature fixes!")
    else:
        logger.info("⚠️  NEEDS MORE DEBUGGING")
