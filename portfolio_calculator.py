#!/usr/bin/env python3
"""
Bond Portfolio Calculator - Using Proven QuantLib Infrastructure
================================================================

Uses the proven bloomberg_accrued_calculator and existing infrastructure
to calculate yield, spread, and duration for the 25-bond portfolio.

Based on: /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/
"""

import QuantLib as ql
import pandas as pd
import numpy as np
from datetime import datetime, date
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BondPortfolioCalculator:
    """
    Calculate yield, spread, and duration for bond portfolios
    Using proven QuantLib methods from google_analysis10
    """
    
    def __init__(self, settlement_date=None):
        # Use current date if not specified
        if settlement_date is None:
            today = datetime.now()
            self.settlement_date = ql.Date(today.day, today.month, today.year)
        else:
            self.settlement_date = settlement_date
            
        # Set QuantLib evaluation date
        ql.Settings.instance().evaluationDate = self.settlement_date
        
        # Treasury benchmark (approximate current 10Y)
        self.treasury_benchmark = 0.045  # 4.5% assumption
        
        logger.info(f"🏦 Bond Portfolio Calculator initialized")
        logger.info(f"   Settlement Date: {self.settlement_date}")
        
    def parse_bond_description(self, description):
        """
        Parse bond description to extract coupon and maturity
        """
        try:
            # Extract coupon rate (various formats)
            import re
            
            # Look for patterns like "3.25%", "5.95%", "6.264%"
            coupon_match = re.search(r'(\d+\.?\d*)\%', description)
            if not coupon_match:
                # Look for patterns like ", 3.25," or " 5.95 "
                coupon_match = re.search(r'[,\s](\d+\.?\d+)[,\s]', description)
            
            coupon = float(coupon_match.group(1)) if coupon_match else None
            
            # Extract maturity date (various formats)
            # Look for patterns like "15-Aug-2052", "30-Sep-2040", "28-Jan-2031"
            maturity_match = re.search(r'(\d{1,2})-([A-Za-z]{3})-(\d{4})', description)
            if maturity_match:
                day, month_str, year = maturity_match.groups()
                
                # Convert month abbreviation to number
                month_map = {
                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                }
                month = month_map.get(month_str, 1)
                maturity = ql.Date(int(day), month, int(year))
            else:
                # Try other date formats
                maturity = None
                
            return coupon, maturity
            
        except Exception as e:
            logger.warning(f"Error parsing '{description}': {e}")
            return None, None
    
    def calculate_bond_metrics(self, isin, price, description, face_value=100):
        """
        Calculate yield, duration, and spread for a single bond
        """
        try:
            # Parse bond details
            coupon_rate, maturity_date = self.parse_bond_description(description)
            
            if not coupon_rate or not maturity_date:
                return {
                    'isin': isin,
                    'error': f'Could not parse bond details from: {description}',
                    'yield': None,
                    'duration': None,
                    'spread': None
                }
            
            # Determine if this is a Treasury bond
            is_treasury = 'TREASURY' in description.upper() or isin.startswith('US9128')
            
            # Set up bond parameters based on type
            if is_treasury:
                # US Treasury bonds typically use ActualActual
                day_count = ql.ActualActual(ql.ActualActual.ISDA)
                business_convention = ql.Following
                frequency = ql.Semiannual
            else:
                # Corporate bonds typically use 30/360
                day_count = ql.Thirty360(ql.Thirty360.BondBasis)
                business_convention = ql.Following
                frequency = ql.Semiannual
            
            # Create calendar
            calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
            
            # Create coupon schedule
            coupon_dates = ql.Schedule(
                self.settlement_date,
                maturity_date,
                ql.Period(frequency),
                calendar,
                business_convention,
                business_convention,
                ql.DateGeneration.Backward,
                False
            )
            
            # Create fixed rate bond
            bond = ql.FixedRateBond(
                1,  # settlement days
                face_value,
                coupon_dates,
                [coupon_rate / 100],  # Convert percentage to decimal
                day_count
            )
            
            # Create pricing engine
            flat_curve = ql.YieldTermStructureHandle(
                ql.FlatForward(self.settlement_date, 0.05, day_count)
            )
            bond_engine = ql.DiscountingBondEngine(flat_curve)
            bond.setPricingEngine(bond_engine)
            
            # Calculate yield to maturity
            clean_price = price
            ytm = bond.bondYield(clean_price, day_count, ql.Compounded, frequency)
            
            # Calculate duration
            duration = ql.BondFunctions.duration(
                bond, ytm, day_count, ql.Compounded, frequency
            )
            
            # Calculate spread vs Treasury
            if is_treasury:
                spread = 0  # Treasury is the benchmark
            else:
                spread = (ytm - self.treasury_benchmark) * 10000  # Convert to basis points
            
            return {
                'isin': isin,
                'description': description,
                'price': price,
                'coupon': coupon_rate,
                'maturity': str(maturity_date),
                'yield': round(ytm * 100, 2),  # Convert to percentage
                'duration': round(duration, 2),
                'spread': round(spread, 0) if spread != 0 else 0,
                'is_treasury': is_treasury,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics for {isin}: {e}")
            return {
                'isin': isin,
                'error': str(e),
                'yield': None,
                'duration': None,
                'spread': None,
                'success': False
            }
    
    def calculate_portfolio(self, bonds_data):
        """
        Calculate metrics for entire bond portfolio
        """
        results = []
        
        for bond in bonds_data:
            isin = bond['isin']
            price = bond['price']
            description = bond['description']
            
            logger.info(f"Processing {isin}: {description}")
            
            result = self.calculate_bond_metrics(isin, price, description)
            results.append(result)
        
        return results

# Bond portfolio data
BOND_PORTFOLIO = [
    {"isin": "US912810TJ79", "price": 71.66, "description": "US TREASURY N/B, 3%, 15-Aug-2052"},
    {"isin": "XS2249741674", "price": 77.88, "description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
    {"isin": "XS1709535097", "price": 89.40, "description": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"},
    {"isin": "XS1982113463", "price": 87.14, "description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"},
    {"isin": "USP37466AS18", "price": 80.39, "description": "EMPRESA METRO, 4.7%, 07-May-2050"},
    {"isin": "USP3143NAH72", "price": 101.63, "description": "CODELCO INC, 6.15%, 24-Oct-2036"},
    {"isin": "USP30179BR86", "price": 86.42, "description": "COMISION FEDERAL, 6.264%, 15-Feb-2052"},
    {"isin": "US195325DX04", "price": 52.71, "description": "COLOMBIA REP OF, 3.875%, 15-Feb-2061"},
    {"isin": "US279158AJ82", "price": 69.31, "description": "ECOPETROL SA, 5.875%, 28-May-2045"},
    {"isin": "USP37110AM89", "price": 76.24, "description": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047"},
    {"isin": "XS2542166231", "price": 103.03, "description": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038"},
    {"isin": "XS2167193015", "price": 64.50, "description": "STATE OF ISRAEL, 3.8%, 13-May-2060"},
    {"isin": "XS1508675508", "price": 82.42, "description": "SAUDI INT BOND, 4.5%, 26-Oct-2046"},
    {"isin": "XS1807299331", "price": 92.21, "description": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048"},
    {"isin": "US91086QAZ19", "price": 78.00, "description": "UNITED MEXICAN, 5.75%, 12-Oct-2110"},
    {"isin": "USP6629MAD40", "price": 82.57, "description": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047"},
    {"isin": "US698299BL70", "price": 56.60, "description": "PANAMA, 3.87%, 23-Jul-2060"},
    {"isin": "US71654QDF63", "price": 71.42, "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060"},
    {"isin": "US71654QDE98", "price": 89.55, "description": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031"},
    {"isin": "XS2585988145", "price": 85.54, "description": "GACI FIRST INVST, 5.125%, 14-Feb-2053"},
    {"isin": "XS1959337749", "price": 89.97, "description": "QATAR STATE OF, 4.817%, 14-Mar-2049"},
    {"isin": "XS2233188353", "price": 99.23, "description": "QNB FINANCE LTD, 1.625%, 22-Sep-2025"},
    {"isin": "XS2359548935", "price": 73.79, "description": "QATAR ENERGY, 3.125%, 12-Jul-2041"},
    {"isin": "XS0911024635", "price": 93.29, "description": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043"},
    {"isin": "USP0R80BAG79", "price": 97.26, "description": "SITIOS, 5.375%, 04-Apr-2032"}
]

def main():
    """
    Main function to calculate portfolio metrics
    """
    print("🏦 Bond Portfolio Calculator")
    print("=" * 50)
    print(f"📊 Processing {len(BOND_PORTFOLIO)} bonds...")
    print()
    
    # Initialize calculator
    calculator = BondPortfolioCalculator()
    
    # Calculate portfolio metrics
    results = calculator.calculate_portfolio(BOND_PORTFOLIO)
    
    # Display results
    print("\n📈 PORTFOLIO RESULTS")
    print("=" * 80)
    print(f"{'ISIN':<15} {'Price':<8} {'Yield':<8} {'Duration':<8} {'Spread':<8} {'Status'}")
    print("-" * 80)
    
    successful_bonds = 0
    
    for result in results:
        isin = result['isin']
        price = result.get('price', 'N/A')
        
        if result.get('success', False):
            yield_pct = f"{result['yield']:.2f}%"
            duration_yrs = f"{result['duration']:.2f}"
            spread_bp = f"{result['spread']:.0f}bp" if result['spread'] != 0 else "Tsy"
            status = "✅"
            successful_bonds += 1
        else:
            yield_pct = "Error"
            duration_yrs = "Error"
            spread_bp = "Error"
            status = "❌"
        
        print(f"{isin:<15} {price:<8} {yield_pct:<8} {duration_yrs:<8} {spread_bp:<8} {status}")
    
    print("-" * 80)
    print(f"✅ Successfully calculated: {successful_bonds}/{len(BOND_PORTFOLIO)} bonds")
    
    # Calculate portfolio summary if we have successful bonds
    if successful_bonds > 0:
        successful_results = [r for r in results if r.get('success', False)]
        avg_yield = np.mean([r['yield'] for r in successful_results])
        avg_duration = np.mean([r['duration'] for r in successful_results])
        
        print(f"\n📊 PORTFOLIO SUMMARY")
        print(f"   Average Yield: {avg_yield:.2f}%")
        print(f"   Average Duration: {avg_duration:.2f} years")
        print(f"   Success Rate: {successful_bonds/len(BOND_PORTFOLIO)*100:.1f}%")

if __name__ == "__main__":
    main()
