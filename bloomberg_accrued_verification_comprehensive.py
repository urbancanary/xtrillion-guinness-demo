#!/usr/bin/env python3
"""
Bloomberg Accrued Interest Verification - COMPREHENSIVE
=======================================================

Verifies accrued interest calculations for ALL 2,056 bonds from Bloomberg Excel file
against your proven Bloomberg calculator methods.

INPUT: EMUSTRUU Index as of Jul 29 20251.xlsm (2,056 bonds)
OUTPUT: Comprehensive verification report with comparison statistics
TARGET: Verify 100% of bonds against Bloomberg accrued interest benchmarks
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import re
import logging
from typing import Optional, Tuple, Dict, Any
import math

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveAccruedVerification:
    """
    Verify accrued interest calculations against Bloomberg for all 2,056 bonds
    """
    
    def __init__(self, excel_file: str, settlement_date: str = "2025-07-29"):
        self.excel_file = excel_file
        self.settlement_date = datetime.strptime(settlement_date, "%Y-%m-%d")
        
        # Statistics
        self.stats = {
            "total_bonds": 0,
            "coupon_parsed": 0,
            "maturity_parsed": 0,
            "accrued_calculated": 0,
            "calculation_errors": 0,
            "perfect_matches": 0,
            "close_matches": 0,  # Within 1% difference
            "significant_differences": 0,  # >5% difference
        }
        
        logger.info(f"🧮 Bloomberg Accrued Interest Verification - COMPREHENSIVE")
        logger.info(f"   Excel File: {excel_file}")
        logger.info(f"   Settlement Date: {settlement_date}")

    def extract_coupon_from_description(self, description: str) -> Optional[float]:
        """
        Extract coupon rate from bond description using proven Bloomberg patterns
        
        Examples:
        "ARGENT 4 ⅛ 07/09/35" -> 4.125
        "ARGENT 0 ¾ 07/09/30" -> 0.75
        "PEMEX 7.69 01/23/50" -> 7.69
        """
        if not description:
            return None
        
        try:
            # Common fraction mappings
            fraction_map = {
                '⅛': 0.125, '¼': 0.25, '⅜': 0.375, '½': 0.5,
                '⅝': 0.625, '¾': 0.75, '⅞': 0.875,
                '1/8': 0.125, '1/4': 0.25, '3/8': 0.375, '1/2': 0.5,
                '5/8': 0.625, '3/4': 0.75, '7/8': 0.875
            }
            
            # Pattern to match coupon rates
            patterns = [
                # Integer + fraction (e.g., "4 ⅛", "0 ¾")
                r'(\d+)\s*([⅛¼⅜½⅝¾⅞]|\d/\d)',
                # Decimal number (e.g., "7.69", "11.535")
                r'(\d+\.\d+)',
                # Just integer (e.g., "5", "10")
                r'(\d+)'
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
        """
        Extract maturity date from bond description
        
        Examples:
        "ARGENT 4 ⅛ 07/09/35" -> 2035-07-09
        "PEMEX 7.69 01/23/50" -> 2050-01-23
        """
        if not description:
            return None
        
        try:
            # Pattern for MM/DD/YY format
            match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2})', description)
            if match:
                month, day, year = match.groups()
                
                # Convert YY to full year (assume 20XX for years < 50, 19XX for >= 50)
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
        """
        Calculate accrued interest using 30/360 day count convention
        
        Args:
            coupon: Annual coupon rate (as percentage, e.g., 4.125 for 4.125%)
            last_payment: Date of last coupon payment
            settlement: Settlement date
            frequency: Payment frequency per year (2 = semi-annual)
            
        Returns:
            Accrued interest per $1,000,000 face value
        """
        try:
            # Calculate days using 30/360 convention
            def days_30_360(start_date, end_date):
                d1, m1, y1 = start_date.day, start_date.month, start_date.year
                d2, m2, y2 = end_date.day, end_date.month, end_date.year
                
                # Adjust days according to 30/360 rules
                if d1 == 31:
                    d1 = 30
                if d2 == 31 and d1 >= 30:
                    d2 = 30
                
                return (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
            
            days_accrued = days_30_360(last_payment, settlement)
            days_in_period = 360 // frequency  # 180 for semi-annual
            
            # Calculate accrued interest per million
            coupon_rate = coupon / 100.0  # Convert percentage to decimal
            period_coupon = coupon_rate / frequency
            accrued_fraction = days_accrued / days_in_period
            accrued_interest_per_million = period_coupon * accrued_fraction * 1000000
            
            return accrued_interest_per_million
            
        except Exception as e:
            logger.debug(f"Error calculating accrued interest: {e}")
            return 0.0

    def estimate_last_payment_date(self, maturity: datetime, frequency: int = 2) -> datetime:
        """
        Estimate the most recent coupon payment date before settlement
        """
        try:
            settlement = self.settlement_date
            
            # Generate coupon payment dates working backwards from maturity
            current_payment = maturity
            while current_payment > settlement:
                if frequency == 2:  # Semi-annual
                    # Go back 6 months
                    if current_payment.month > 6:
                        current_payment = current_payment.replace(month=current_payment.month - 6)
                    else:
                        current_payment = current_payment.replace(year=current_payment.year - 1, 
                                                                month=current_payment.month + 6)
                else:  # Annual
                    current_payment = current_payment.replace(year=current_payment.year - 1)
            
            return current_payment
            
        except Exception as e:
            logger.debug(f"Error estimating last payment date: {e}")
            return settlement - timedelta(days=180)  # Default fallback

    def process_all_bonds(self) -> pd.DataFrame:
        """
        Process all bonds from Excel file and verify accrued interest calculations
        """
        logger.info("📊 Loading bonds from Bloomberg Excel file...")
        
        # Load Excel data
        df = pd.read_excel(self.excel_file, sheet_name=0)
        self.stats["total_bonds"] = len(df)
        logger.info(f"   Loaded {len(df):,} bonds")
        
        # Process each bond
        results = []
        
        for idx, bond in df.iterrows():
            if (idx + 1) % 500 == 0:
                logger.info(f"   Progress: {idx + 1:,}/{len(df):,} bonds processed")
            
            bond_result = self._process_single_bond(bond)
            if bond_result:
                results.append(bond_result)
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Calculate comparison statistics
        if len(results_df) > 0:
            results_df['difference_abs'] = abs(results_df['calculated_accrued'] - results_df['bloomberg_accrued'])
            results_df['difference_pct'] = (results_df['difference_abs'] / results_df['bloomberg_accrued'] * 100).fillna(0)
            
            # Categorize matches
            results_df['match_category'] = 'ERROR'
            results_df.loc[results_df['difference_pct'] <= 0.1, 'match_category'] = 'PERFECT'
            results_df.loc[(results_df['difference_pct'] > 0.1) & (results_df['difference_pct'] <= 1.0), 'match_category'] = 'CLOSE'
            results_df.loc[(results_df['difference_pct'] > 1.0) & (results_df['difference_pct'] <= 5.0), 'match_category'] = 'DIFFERENT'
            results_df.loc[results_df['difference_pct'] > 5.0, 'match_category'] = 'SIGNIFICANT'
            
            # Update statistics
            self.stats["perfect_matches"] = len(results_df[results_df['match_category'] == 'PERFECT'])
            self.stats["close_matches"] = len(results_df[results_df['match_category'] == 'CLOSE'])
            self.stats["significant_differences"] = len(results_df[results_df['match_category'] == 'SIGNIFICANT'])
        
        # Log final statistics
        self._log_final_statistics(results_df)
        
        return results_df

    def _process_single_bond(self, bond) -> Optional[Dict[str, Any]]:
        """Process a single bond and calculate accrued interest"""
        try:
            isin = bond.get('ISIN', '')
            description = bond.get('Description', '')
            price = bond.get('Price', 100.0)
            bloomberg_accrued = bond.get('bbg_accrued_per_million', 0.0)
            
            # Skip if no Bloomberg value to compare against
            if pd.isna(bloomberg_accrued) or bloomberg_accrued == 0:
                self.stats["calculation_errors"] += 1
                return None
            
            # Parse coupon and maturity
            coupon = self.extract_coupon_from_description(description)
            maturity = self.parse_maturity_from_description(description)
            
            if coupon is None:
                self.stats["calculation_errors"] += 1
                return None
            
            self.stats["coupon_parsed"] += 1
            
            if maturity is None:
                self.stats["calculation_errors"] += 1
                return None
            
            self.stats["maturity_parsed"] += 1
            
            # Calculate accrued interest
            last_payment = self.estimate_last_payment_date(maturity)
            calculated_accrued = self.calculate_accrued_interest_30_360(
                coupon, last_payment, self.settlement_date
            )
            
            self.stats["accrued_calculated"] += 1
            
            return {
                'isin': isin,
                'description': description,
                'coupon': coupon,
                'maturity': maturity.strftime('%Y-%m-%d') if maturity else None,
                'price': price,
                'bloomberg_accrued': bloomberg_accrued,
                'calculated_accrued': calculated_accrued,
                'settlement_date': self.settlement_date.strftime('%Y-%m-%d'),
                'calculation_method': '30_360_semi_annual',
                'last_payment_estimated': last_payment.strftime('%Y-%m-%d'),
                'calculation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.stats["calculation_errors"] += 1
            logger.debug(f"Error processing bond {bond.get('ISIN', 'Unknown')}: {e}")
            return None

    def _log_final_statistics(self, results_df: pd.DataFrame):
        """Log comprehensive statistics"""
        logger.info(f"✅ Comprehensive Verification Complete:")
        logger.info(f"   Total bonds processed: {self.stats['total_bonds']:,}")
        logger.info(f"   Successful calculations: {len(results_df):,}")
        logger.info(f"   Calculation errors: {self.stats['calculation_errors']:,}")
        
        if len(results_df) > 0:
            logger.info(f"\n📊 Accuracy Analysis:")
            logger.info(f"   Perfect matches (≤0.1%): {self.stats['perfect_matches']:,} ({self.stats['perfect_matches']/len(results_df)*100:.1f}%)")
            logger.info(f"   Close matches (≤1.0%): {self.stats['close_matches']:,} ({self.stats['close_matches']/len(results_df)*100:.1f}%)")
            logger.info(f"   Significant differences (>5%): {self.stats['significant_differences']:,} ({self.stats['significant_differences']/len(results_df)*100:.1f}%)")
            
            logger.info(f"\n📈 Statistical Summary:")
            logger.info(f"   Mean difference: {results_df['difference_abs'].mean():.2f}")
            logger.info(f"   Median difference: {results_df['difference_abs'].median():.2f}")
            logger.info(f"   Max difference: {results_df['difference_abs'].max():.2f}")
            logger.info(f"   Mean % difference: {results_df['difference_pct'].mean():.2f}%")

    def generate_comprehensive_report(self, results_df: pd.DataFrame, output_file: str = None):
        """Generate comprehensive HTML report"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"bloomberg_accrued_verification_comprehensive_{timestamp}.html"
        
        html_content = self._generate_html_report(results_df)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"📄 Comprehensive report saved: {output_file}")
        return output_file

    def _generate_html_report(self, results_df: pd.DataFrame) -> str:
        """Generate HTML report content"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Sample of different match categories
        perfect_sample = results_df[results_df['match_category'] == 'PERFECT'].head(5)
        significant_sample = results_df[results_df['match_category'] == 'SIGNIFICANT'].head(5)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bloomberg Accrued Interest Verification - COMPREHENSIVE</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .stats {{ background: #ecf0f1; padding: 15px; margin: 20px 0; }}
                .section {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .perfect {{ background-color: #d5f4e6; }}
                .close {{ background-color: #ffeaa7; }}
                .different {{ background-color: #fab1a0; }}
                .significant {{ background-color: #e17055; color: white; }}
                .summary-box {{ background: #3498db; color: white; padding: 15px; margin: 10px 0; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧮 Bloomberg Accrued Interest Verification</h1>
                <h2>COMPREHENSIVE ANALYSIS - ALL 2,056 BONDS</h2>
                <p>Generated: {timestamp}</p>
            </div>
            
            <div class="summary-box">
                <h3>📊 VERIFICATION SUMMARY</h3>
                <p><strong>Total Bonds:</strong> {self.stats['total_bonds']:,} | 
                   <strong>Successful Calculations:</strong> {len(results_df):,} | 
                   <strong>Success Rate:</strong> {len(results_df)/self.stats['total_bonds']*100:.1f}%</p>
            </div>
            
            <div class="stats">
                <h3>🎯 Accuracy Statistics</h3>
                <table>
                    <tr><th>Category</th><th>Count</th><th>Percentage</th><th>Criteria</th></tr>
                    <tr class="perfect">
                        <td><strong>Perfect Matches</strong></td>
                        <td>{self.stats['perfect_matches']:,}</td>
                        <td>{self.stats['perfect_matches']/len(results_df)*100:.1f}%</td>
                        <td>≤0.1% difference</td>
                    </tr>
                    <tr class="close">
                        <td><strong>Close Matches</strong></td>
                        <td>{self.stats['close_matches']:,}</td>
                        <td>{self.stats['close_matches']/len(results_df)*100:.1f}%</td>
                        <td>0.1% - 1.0% difference</td>
                    </tr>
                    <tr class="significant">
                        <td><strong>Significant Differences</strong></td>
                        <td>{self.stats['significant_differences']:,}</td>
                        <td>{self.stats['significant_differences']/len(results_df)*100:.1f}%</td>
                        <td>>5% difference</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h3>✅ Perfect Matches Sample (Bloomberg vs Our Calculation)</h3>
                <table>
                    <tr><th>ISIN</th><th>Description</th><th>Coupon</th><th>Bloomberg</th><th>Calculated</th><th>Diff %</th></tr>
        """
        
        # Add perfect matches sample
        for _, bond in perfect_sample.iterrows():
            html_content += f"""
                    <tr class="perfect">
                        <td>{bond['isin']}</td>
                        <td>{bond['description'][:30]}...</td>
                        <td>{bond['coupon']:.3f}%</td>
                        <td>{bond['bloomberg_accrued']:.0f}</td>
                        <td>{bond['calculated_accrued']:.0f}</td>
                        <td>{bond['difference_pct']:.3f}%</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h3>⚠️ Significant Differences Sample (Need Investigation)</h3>
                <table>
                    <tr><th>ISIN</th><th>Description</th><th>Coupon</th><th>Bloomberg</th><th>Calculated</th><th>Diff %</th></tr>
        """
        
        # Add significant differences sample
        for _, bond in significant_sample.iterrows():
            html_content += f"""
                    <tr class="significant">
                        <td>{bond['isin']}</td>
                        <td>{bond['description'][:30]}...</td>
                        <td>{bond['coupon']:.3f}%</td>
                        <td>{bond['bloomberg_accrued']:.0f}</td>
                        <td>{bond['calculated_accrued']:.0f}</td>
                        <td>{bond['difference_pct']:.2f}%</td>
                    </tr>
            """
        
        html_content += f"""
                </table>
            </div>
            
            <div class="stats">
                <h3>📈 Statistical Summary</h3>
                <p><strong>Mean Absolute Difference:</strong> {results_df['difference_abs'].mean():.2f}</p>
                <p><strong>Median Absolute Difference:</strong> {results_df['difference_abs'].median():.2f}</p>
                <p><strong>Maximum Difference:</strong> {results_df['difference_abs'].max():.2f}</p>
                <p><strong>Mean Percentage Difference:</strong> {results_df['difference_pct'].mean():.2f}%</p>
                <p><strong>Settlement Date Used:</strong> {self.settlement_date.strftime('%Y-%m-%d')}</p>
                <p><strong>Calculation Method:</strong> 30/360 Semi-Annual</p>
            </div>
            
            <div class="footer">
                <p>🎯 <strong>CONCLUSION:</strong> 
                {self.stats['perfect_matches'] + self.stats['close_matches']:,} bonds 
                ({(self.stats['perfect_matches'] + self.stats['close_matches'])/len(results_df)*100:.1f}%) 
                match Bloomberg within 1% accuracy.</p>
            </div>
        </body>
        </html>
        """
        
        return html_content

def main():
    """Run comprehensive Bloomberg accrued interest verification"""
    
    # Initialize verification system
    excel_file = "EMUSTRUU Index as of Jul 29 20251.xlsm"
    settlement_date = "2025-07-29"  # Use same date as Bloomberg
    
    verifier = ComprehensiveAccruedVerification(excel_file, settlement_date)
    
    # Process all bonds
    logger.info("🚀 Starting comprehensive verification of ALL bonds...")
    results_df = verifier.process_all_bonds()
    
    # Generate comprehensive report
    report_file = verifier.generate_comprehensive_report(results_df)
    
    # Save results to CSV for further analysis
    csv_file = f"bloomberg_verification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    results_df.to_csv(csv_file, index=False)
    logger.info(f"📊 Detailed results saved: {csv_file}")
    
    logger.info("🎉 Comprehensive verification complete!")
    
    return results_df, report_file

if __name__ == "__main__":
    results_df, report_file = main()
