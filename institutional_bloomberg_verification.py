#!/usr/bin/env python3
"""
INSTITUTIONAL BLOOMBERG VERIFICATION - COMPREHENSIVE
===================================================

Verifies ALL THREE core Bloomberg metrics with institutional tolerances:
1. Accrued Interest per Million (<0.01% tolerance)
2. YTW - Yield to Worst (<0.01% tolerance) 
3. OAD - Option Adjusted Duration (<0.001 years tolerance)

INPUT: Bloomberg Excel file with YTW, OAD, and accrued data
OUTPUT: Institutional-grade verification against all Bloomberg metrics
TARGET: Achieve institutional precision across all bond analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import re
import logging
from typing import Optional, Tuple, Dict, Any
import math

# Try to import QuantLib for professional calculations
try:
    import QuantLib as ql
    QUANTLIB_AVAILABLE = True
    print("🚀 QuantLib available - using professional bond math")
except ImportError:
    QUANTLIB_AVAILABLE = False
    print("⚠️ QuantLib not available - using simplified calculations")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InstitutionalBloombergVerification:
    """
    INSTITUTIONAL-GRADE Bloomberg verification for ALL core metrics
    """
    
    def __init__(self, excel_file: str, settlement_date: str = "2025-07-30"):
        self.excel_file = excel_file
        self.settlement_date = datetime.strptime(settlement_date, "%Y-%m-%d")
        
        # INSTITUTIONAL TOLERANCES
        self.tolerances = {
            'accrued_interest': 0.01,      # 0.01% for accrued interest
            'ytw': 0.01,                   # 0.01% for yield (1 basis point)
            'oad': 0.001                   # 0.001 years for duration
        }
        
        # Statistics
        self.stats = {
            "total_bonds": 0,
            "successful_calculations": 0,
            "accrued_perfect": 0,
            "ytw_perfect": 0,
            "oad_perfect": 0,
            "all_three_perfect": 0,
            "calculation_errors": 0
        }
        
        logger.info(f"🏛️ INSTITUTIONAL Bloomberg Verification - ALL METRICS")
        logger.info(f"   Excel File: {excel_file}")
        logger.info(f"   Settlement Date: {settlement_date}")
        logger.info(f"   INSTITUTIONAL TOLERANCES:")
        logger.info(f"     Accrued Interest: ≤{self.tolerances['accrued_interest']:.3f}%")
        logger.info(f"     YTW: ≤{self.tolerances['ytw']:.3f}%")
        logger.info(f"     OAD: ≤{self.tolerances['oad']:.3f} years")

    def extract_coupon_from_description(self, description: str) -> Optional[float]:
        """Extract coupon rate from bond description - PROVEN METHOD"""
        if not description:
            return None
        
        try:
            # Fraction mappings
            fraction_map = {
                '⅛': 0.125, '¼': 0.25, '⅜': 0.375, '½': 0.5,
                '⅝': 0.625, '¾': 0.75, '⅞': 0.875,
                '1/8': 0.125, '1/4': 0.25, '3/8': 0.375, '1/2': 0.5,
                '5/8': 0.625, '3/4': 0.75, '7/8': 0.875
            }
            
            patterns = [
                r'(\d+)\s*([⅛¼⅜½⅝¾⅞]|\d/\d)',  # Integer + fraction
                r'(\d+\.\d+)',                      # Decimal
                r'(\d+)'                            # Integer only
            ]
            
            for pattern in patterns:
                match = re.search(pattern, description)
                if match:
                    if len(match.groups()) == 2:  # Integer + fraction
                        integer_part = float(match.group(1))
                        fraction_part = match.group(2)
                        fraction_value = fraction_map.get(fraction_part, 0)
                        return integer_part + fraction_value
                    else:  # Decimal or integer
                        return float(match.group(1))
            
            return None
            
        except Exception as e:
            logger.debug(f"Error parsing coupon from '{description}': {e}")
            return None

    def parse_maturity_from_description(self, description: str) -> Optional[datetime]:
        """Extract maturity date from bond description - PROVEN METHOD"""
        if not description:
            return None
        
        try:
            # Pattern for MM/DD/YY format
            match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2})', description)
            if match:
                month, day, year = match.groups()
                
                # Convert YY to full year
                year_int = int(year)
                if year_int < 50:
                    full_year = 2000 + year_int
                else:
                    full_year = 1900 + year_int
                
                return datetime(full_year, int(month), int(day))
            
            return None
            
        except Exception as e:
            logger.debug(f"Error parsing maturity from '{description}': {e}")
            return None

    def calculate_accrued_interest_30_360(self, coupon: float, last_payment: datetime, 
                                        settlement: datetime, frequency: int = 2) -> float:
        """Calculate accrued interest using 30/360 - PROVEN METHOD"""
        try:
            def days_30_360(start_date, end_date):
                d1, m1, y1 = start_date.day, start_date.month, start_date.year
                d2, m2, y2 = end_date.day, end_date.month, end_date.year
                
                if d1 == 31:
                    d1 = 30
                if d2 == 31 and d1 >= 30:
                    d2 = 30
                
                return (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
            
            days_accrued = days_30_360(last_payment, settlement)
            days_in_period = 360 // frequency
            
            coupon_rate = coupon / 100.0
            period_coupon = coupon_rate / frequency
            accrued_fraction = days_accrued / days_in_period
            accrued_interest_per_million = period_coupon * accrued_fraction * 1000000
            
            return accrued_interest_per_million
            
        except Exception as e:
            logger.debug(f"Error calculating accrued interest: {e}")
            return 0.0

    def calculate_ytm_quantlib(self, coupon: float, maturity: datetime, price: float, 
                              settlement: datetime, frequency: int = 2) -> Optional[float]:
        """Calculate YTM using QuantLib for institutional precision"""
        if not QUANTLIB_AVAILABLE:
            return self.calculate_ytm_simplified(coupon, maturity, price, settlement, frequency)
        
        try:
            # Convert dates to QuantLib
            settlement_ql = ql.Date(settlement.day, settlement.month, settlement.year)
            maturity_ql = ql.Date(maturity.day, maturity.month, maturity.year)
            
            # Set evaluation date
            ql.Settings.instance().evaluationDate = settlement_ql
            
            # Create bond schedule
            if frequency == 2:
                freq = ql.Semiannual
            else:
                freq = ql.Annual
            
            schedule = ql.Schedule(
                settlement_ql, maturity_ql,
                ql.Period(freq), ql.UnitedStates(ql.UnitedStates.GovernmentBond),
                ql.Following, ql.Following,
                ql.DateGeneration.Backward, False
            )
            
            # Create fixed rate bond
            bond = ql.FixedRateBond(
                0,  # settlementDays
                100.0,  # faceAmount
                schedule,
                [coupon / 100.0],  # coupon rates
                ql.ActualActual()  # day count
            )
            
            # Calculate YTM
            ytm = bond.bondYield(price, ql.ActualActual(), ql.Compounded, freq) * 100
            
            return ytm
            
        except Exception as e:
            logger.debug(f"QuantLib YTM calculation error: {e}")
            return self.calculate_ytm_simplified(coupon, maturity, price, settlement, frequency)

    def calculate_ytm_simplified(self, coupon: float, maturity: datetime, price: float, 
                                settlement: datetime, frequency: int = 2) -> float:
        """Simplified YTM calculation for fallback"""
        try:
            # Simplified yield approximation
            years_to_maturity = (maturity - settlement).days / 365.25
            annual_coupon = coupon
            
            # Simple approximation: (annual coupon + (100 - price) / years) / ((100 + price) / 2)
            if years_to_maturity > 0:
                ytm_approx = (annual_coupon + (100 - price) / years_to_maturity) / ((100 + price) / 2) * 100
                return max(0, ytm_approx)
            
            return coupon  # Fallback to coupon rate
            
        except Exception as e:
            logger.debug(f"Simplified YTM calculation error: {e}")
            return coupon

    def calculate_duration_quantlib(self, coupon: float, maturity: datetime, price: float, 
                                   settlement: datetime, yield_val: float, frequency: int = 2) -> Optional[float]:
        """Calculate modified duration using QuantLib"""
        if not QUANTLIB_AVAILABLE:
            return self.calculate_duration_simplified(coupon, maturity, price, settlement, yield_val, frequency)
        
        try:
            # Convert dates to QuantLib
            settlement_ql = ql.Date(settlement.day, settlement.month, settlement.year)
            maturity_ql = ql.Date(maturity.day, maturity.month, maturity.year)
            
            # Set evaluation date
            ql.Settings.instance().evaluationDate = settlement_ql
            
            # Create bond schedule
            if frequency == 2:
                freq = ql.Semiannual
            else:
                freq = ql.Annual
            
            schedule = ql.Schedule(
                settlement_ql, maturity_ql,
                ql.Period(freq), ql.UnitedStates(ql.UnitedStates.GovernmentBond),
                ql.Following, ql.Following,
                ql.DateGeneration.Backward, False
            )
            
            # Create fixed rate bond
            bond = ql.FixedRateBond(
                0,  # settlementDays
                100.0,  # faceAmount
                schedule,
                [coupon / 100.0],  # coupon rates
                ql.ActualActual()  # day count
            )
            
            # Calculate modified duration
            duration = ql.BondFunctions.duration(
                bond, yield_val / 100.0, ql.ActualActual(), ql.Compounded, freq
            )
            
            return duration
            
        except Exception as e:
            logger.debug(f"QuantLib duration calculation error: {e}")
            return self.calculate_duration_simplified(coupon, maturity, price, settlement, yield_val, frequency)

    def calculate_duration_simplified(self, coupon: float, maturity: datetime, price: float, 
                                     settlement: datetime, yield_val: float, frequency: int = 2) -> float:
        """Simplified duration calculation for fallback"""
        try:
            years_to_maturity = (maturity - settlement).days / 365.25
            
            # Simplified modified duration approximation
            if yield_val > 0:
                duration_approx = years_to_maturity / (1 + yield_val / 100.0 / frequency)
                return max(0, duration_approx)
            
            return years_to_maturity
            
        except Exception as e:
            logger.debug(f"Simplified duration calculation error: {e}")
            return 0.0

    def estimate_last_payment_date(self, maturity: datetime, frequency: int = 2) -> datetime:
        """Estimate last coupon payment date - PROVEN METHOD"""
        try:
            settlement = self.settlement_date
            current_payment = maturity
            
            while current_payment > settlement:
                if frequency == 2:  # Semi-annual
                    if current_payment.month > 6:
                        current_payment = current_payment.replace(month=current_payment.month - 6)
                    else:
                        current_payment = current_payment.replace(
                            year=current_payment.year - 1, 
                            month=current_payment.month + 6
                        )
                else:  # Annual
                    current_payment = current_payment.replace(year=current_payment.year - 1)
            
            return current_payment
            
        except Exception as e:
            logger.debug(f"Error estimating last payment date: {e}")
            return settlement - timedelta(days=180)

    def process_all_bonds(self) -> pd.DataFrame:
        """Process all bonds with INSTITUTIONAL verification of ALL THREE metrics"""
        logger.info("📊 Loading Bloomberg Excel file...")
        
        # Load Excel data
        df = pd.read_excel(self.excel_file, sheet_name=0)
        self.stats["total_bonds"] = len(df)
        logger.info(f"   Loaded {len(df):,} bonds")
        
        # Process each bond
        results = []
        
        for idx, bond in df.iterrows():
            if (idx + 1) % 250 == 0:
                logger.info(f"   Progress: {idx + 1:,}/{len(df):,} bonds processed")
            
            bond_result = self._process_single_bond(bond)
            if bond_result:
                results.append(bond_result)
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        if len(results_df) > 0:
            # Calculate differences for all three metrics
            results_df['accrued_diff_pct'] = abs(results_df['calculated_accrued'] - results_df['bloomberg_accrued']) / results_df['bloomberg_accrued'] * 100
            results_df['ytw_diff_pct'] = abs(results_df['calculated_ytw'] - results_df['bloomberg_ytw'])
            results_df['oad_diff_years'] = abs(results_df['calculated_oad'] - results_df['bloomberg_oad'])
            
            # Institutional tolerance checks
            results_df['accrued_perfect'] = results_df['accrued_diff_pct'] <= self.tolerances['accrued_interest']
            results_df['ytw_perfect'] = results_df['ytw_diff_pct'] <= self.tolerances['ytw']
            results_df['oad_perfect'] = results_df['oad_diff_years'] <= self.tolerances['oad']
            results_df['all_three_perfect'] = results_df['accrued_perfect'] & results_df['ytw_perfect'] & results_df['oad_perfect']
            
            # Update statistics
            self.stats["accrued_perfect"] = results_df['accrued_perfect'].sum()
            self.stats["ytw_perfect"] = results_df['ytw_perfect'].sum()
            self.stats["oad_perfect"] = results_df['oad_perfect'].sum()
            self.stats["all_three_perfect"] = results_df['all_three_perfect'].sum()
        
        self.stats["successful_calculations"] = len(results_df)
        
        # Log final institutional statistics
        self._log_institutional_statistics(results_df)
        
        return results_df

    def _process_single_bond(self, bond) -> Optional[Dict[str, Any]]:
        """Process single bond - ALL THREE Bloomberg metrics"""
        try:
            isin = bond.get('ISIN', '')
            description = bond.get('Description', '')
            price = bond.get('Price', 100.0)
            
            # Get Bloomberg values
            bloomberg_accrued = bond.get('bbg_accrued_per_million', 0.0)
            bloomberg_ytw = bond.get('YTW', 0.0)
            bloomberg_oad = bond.get('OAD', 0.0)
            
            # Skip if missing Bloomberg data
            if pd.isna(bloomberg_accrued) or pd.isna(bloomberg_ytw) or pd.isna(bloomberg_oad):
                self.stats["calculation_errors"] += 1
                return None
            
            # Parse bond details
            coupon = self.extract_coupon_from_description(description)
            maturity = self.parse_maturity_from_description(description)
            
            if coupon is None or maturity is None:
                self.stats["calculation_errors"] += 1
                return None
            
            # Calculate all three metrics
            # 1. Accrued Interest
            last_payment = self.estimate_last_payment_date(maturity)
            calculated_accrued = self.calculate_accrued_interest_30_360(
                coupon, last_payment, self.settlement_date
            )
            
            # 2. YTW (using our YTM calculation)
            calculated_ytw = self.calculate_ytm_quantlib(
                coupon, maturity, price, self.settlement_date
            )
            
            # 3. OAD (approximated with modified duration)
            calculated_oad = self.calculate_duration_quantlib(
                coupon, maturity, price, self.settlement_date, calculated_ytw or bloomberg_ytw
            )
            
            return {
                'isin': isin,
                'description': description,
                'coupon': coupon,
                'maturity': maturity.strftime('%Y-%m-%d') if maturity else None,
                'price': price,
                
                # Bloomberg values
                'bloomberg_accrued': bloomberg_accrued,
                'bloomberg_ytw': bloomberg_ytw,
                'bloomberg_oad': bloomberg_oad,
                
                # Our calculated values
                'calculated_accrued': calculated_accrued,
                'calculated_ytw': calculated_ytw or 0.0,
                'calculated_oad': calculated_oad or 0.0,
                
                'settlement_date': self.settlement_date.strftime('%Y-%m-%d'),
                'calculation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.stats["calculation_errors"] += 1
            logger.debug(f"Error processing bond {bond.get('ISIN', 'Unknown')}: {e}")
            return None

    def _log_institutional_statistics(self, results_df: pd.DataFrame):
        """Log INSTITUTIONAL verification statistics"""
        logger.info(f"✅ INSTITUTIONAL VERIFICATION Complete:")
        logger.info(f"   Total bonds processed: {self.stats['total_bonds']:,}")
        logger.info(f"   Successful calculations: {len(results_df):,}")
        logger.info(f"   Calculation errors: {self.stats['calculation_errors']:,}")
        
        if len(results_df) > 0:
            logger.info(f"\n🏛️ INSTITUTIONAL ACCURACY (Strict Tolerances):")
            logger.info(f"   Accrued Perfect (≤{self.tolerances['accrued_interest']:.3f}%): {self.stats['accrued_perfect']:,} ({self.stats['accrued_perfect']/len(results_df)*100:.1f}%)")
            logger.info(f"   YTW Perfect (≤{self.tolerances['ytw']:.3f}%): {self.stats['ytw_perfect']:,} ({self.stats['ytw_perfect']/len(results_df)*100:.1f}%)")
            logger.info(f"   OAD Perfect (≤{self.tolerances['oad']:.3f} years): {self.stats['oad_perfect']:,} ({self.stats['oad_perfect']/len(results_df)*100:.1f}%)")
            logger.info(f"   🏆 ALL THREE PERFECT: {self.stats['all_three_perfect']:,} ({self.stats['all_three_perfect']/len(results_df)*100:.1f}%)")

def main():
    """Run INSTITUTIONAL Bloomberg verification - ALL THREE METRICS"""
    
    excel_file = "EMUSTRUU Index as of Jul 29 20251.xlsm"
    settlement_date = "2025-07-30"  # T+1 from Bloomberg data date
    
    verifier = InstitutionalBloombergVerification(excel_file, settlement_date)
    
    logger.info("🚀 Starting INSTITUTIONAL verification - ALL THREE METRICS...")
    results_df = verifier.process_all_bonds()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"institutional_bloomberg_verification_{timestamp}.csv"
    results_df.to_csv(csv_file, index=False)
    logger.info(f"📊 INSTITUTIONAL results saved: {csv_file}")
    
    logger.info("🏛️ INSTITUTIONAL verification complete!")
    
    return results_df, csv_file

if __name__ == "__main__":
    results_df, csv_file = main()
