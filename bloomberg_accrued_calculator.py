#!/usr/bin/env python3
"""
Bloomberg Accrued Interest Calculator for Validation Benchmarks
============================================================

Processes bloomberg_index.db all_bonds table to calculate accrued interest
per million for validation benchmarking against enhanced QuantLib calculations.

INPUT: quantlib_project_v3/bloomberg_index.db (12,343 bonds)
OUTPUT: New table bloomberg_accrued_benchmarks with calculated accrued interest
TARGET: Create 5,961+ validation benchmarks for google_analysis9 validation
"""

import sqlite3
import pandas as pd
import numpy as np
import re
from datetime import datetime, date
import logging
from typing import Optional, Tuple, Dict, Any
# Note: QuantLib import removed since we're using Bloomberg differential calculation

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BloombergAccruedCalculator:
    """
    Calculate Bloomberg-style accrued interest for validation benchmarks
    """
    
    def __init__(self, source_db_path: str, settlement_date: str = "2025-04-17"):
        self.source_db_path = source_db_path
        self.settlement_date = settlement_date
        
        # Statistics
        self.stats = {
            "total_bonds": 0,
            "coupon_parsed": 0,
            "maturity_parsed": 0,
            "accrued_calculated": 0,
            "calculation_errors": 0,
            "validation_ready": 0
        }
        
        logger.info(f"🏦 Bloomberg Differential Calculator initialized")
        logger.info(f"   Source: {source_db_path}")
        logger.info(f"   Settlement: {settlement_date}")

    def _parse_settlement_date(self, date_str: str) -> datetime:
        """Convert settlement date string to datetime"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception as e:
            logger.error(f"Error parsing settlement date: {e}")
            return datetime.now()

    def extract_coupon_from_description(self, description: str) -> Optional[float]:
        """
        Extract coupon rate from bond description
        
        Examples:
        "SATS 10 ¾ 11/30/29" -> 10.75
        "MEDIND 3 ⅜ 04/01/29" -> 3.375
        "QUIKHO 6 ⅝ 03/01/32" -> 6.625
        "TIBX 6 ½ 03/31/29" -> 6.5
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
            
            # Pattern to match coupon rates like "10 ¾" or "3.375" or "6.5"
            patterns = [
                # Integer + fraction (e.g., "10 ¾", "6 ½")
                r'(\d+)\s*([⅛¼⅜½⅝¾⅞]|\d/\d)',
                # Decimal number (e.g., "3.375", "6.5")
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

    def calculate_bloomberg_differential(self, mv_usd: float, par_val: float) -> Optional[float]:
        """
        Calculate Bloomberg-style market value differential per million
        
        Formula: (mv_usd - par_val) / par_val * 1000000
        
        Args:
            mv_usd: Market value in USD
            par_val: Par value (face value)
            
        Returns:
            Differential per $1M face value
        """
        try:
            if par_val == 0 or par_val is None:
                return None
            
            differential_per_million = (mv_usd - par_val) / par_val * 1000000.0
            return differential_per_million
            
        except Exception as e:
            logger.debug(f"Error calculating Bloomberg differential: {e}")
            return None

    def process_all_bonds(self) -> pd.DataFrame:
        """
        Process all bonds from bloomberg_index.db and calculate Bloomberg differential
        """
        logger.info("📊 Loading bonds from bloomberg_index.db...")
        
        # Load data
        conn = sqlite3.connect(self.source_db_path)
        df = pd.read_sql_query("SELECT * FROM all_bonds", conn)
        conn.close()
        
        self.stats["total_bonds"] = len(df)
        logger.info(f"   Loaded {len(df):,} bonds")
        
        # Handle duplicate columns by using specific column indices
        # We have both 'par val' (index 6) and 'par_val' (index 12) - they're identical
        # We have 'mv (usd)' (index 7)
        logger.info("   Using column indices to avoid duplicate names")
        
        # Process each bond
        results = []
        
        for idx, row in df.iterrows():
            if (idx + 1) % 1000 == 0:
                logger.info(f"   Progress: {idx + 1:,}/{len(df):,} bonds processed")
            
            bond_result = self._process_single_bond_by_index(row, df.columns)
            if bond_result:
                results.append(bond_result)
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Log statistics
        self.stats["validation_ready"] = len(results_df)
        logger.info(f"✅ Processing complete:")
        logger.info(f"   Total bonds: {self.stats['total_bonds']:,}")
        logger.info(f"   MV/Par available: {self.stats['coupon_parsed']:,}")
        logger.info(f"   Valid calculations: {self.stats['accrued_calculated']:,}")
        logger.info(f"   Calculation errors: {self.stats['calculation_errors']:,}")
        logger.info(f"   Ready for validation: {self.stats['validation_ready']:,}")
        
        return results_df

    def _process_single_bond_by_index(self, row, columns) -> Optional[Dict[str, Any]]:
        """Process a single bond row using column indices to avoid duplicate names"""
        try:
            # Use column indices to avoid duplicate column name issues
            isin = row.iloc[0]  # 'isin'
            description = row.iloc[1]  # 'description'
            price = row.iloc[3]  # 'price'
            mv_usd = row.iloc[7]  # 'mv (usd)'
            par_val = row.iloc[12]  # 'par_val' (use the cleaner column name)
            country = row.iloc[11]  # 'country'
            ticker = row.iloc[13]  # 'ticker'
            maturity = row.iloc[15]  # 'maturity'
            ytw = row.iloc[4]  # 'ytw'
            oas = row.iloc[9]  # 'oas'
            weight = row.iloc[8]  # 'weight'
            rating = row.iloc[10]  # 'index rating (string)'
            
            if pd.isna(mv_usd) or pd.isna(par_val) or par_val == 0:
                self.stats["calculation_errors"] += 1
                return None
            
            self.stats["coupon_parsed"] += 1  # Reusing stat for "data available"
            
            # Calculate Bloomberg differential using your formula
            bloomberg_differential = self.calculate_bloomberg_differential(mv_usd, par_val)
            if bloomberg_differential is None:
                self.stats["calculation_errors"] += 1
                return None
            
            self.stats["accrued_calculated"] += 1
            
            # Extract coupon for reference (optional)
            coupon = self.extract_coupon_from_description(description)
            
            return {
                'isin': isin,
                'description': description,
                'coupon': coupon,
                'maturity': maturity,
                'price': price,
                'mv_usd': mv_usd,
                'par_val': par_val,
                'bloomberg_differential_per_million': bloomberg_differential,
                'settlement_date': self.settlement_date,
                'calculation_method': 'bloomberg_mv_par_differential',
                'calculation_timestamp': datetime.now().isoformat(),
                'country': country,
                'ticker': ticker,
                'rating': str(rating).replace('(', '').replace(')', '') if not pd.isna(rating) else '',
                'ytw': ytw if not pd.isna(ytw) else None,
                'oas': oas if not pd.isna(oas) else None,
                'weight': weight if not pd.isna(weight) else None
            }
            
        except Exception as e:
            self.stats["calculation_errors"] += 1
            logger.debug(f"Error processing bond: {e}")
            return None

    def _process_single_bond(self, row) -> Optional[Dict[str, Any]]:
        """Process a single bond row using Bloomberg differential calculation"""
        try:
            isin = row.get('isin')
            description = row.get('description', '')
            maturity_str = row.get('maturity', '')
            price = row.get('price', 100.0)
            
            # Get market value and par value from Bloomberg data
            mv_usd = row.get('mv_usd', None)  # Market value (USD)
            par_val = row.get('par_val', None)  # Par value
            
            if mv_usd is None or par_val is None:
                self.stats["calculation_errors"] += 1
                return None
            
            self.stats["coupon_parsed"] += 1  # Reusing stat for "data available"
            
            # Calculate Bloomberg differential using your formula
            bloomberg_differential = self.calculate_bloomberg_differential(mv_usd, par_val)
            if bloomberg_differential is None:
                self.stats["calculation_errors"] += 1
                return None
            
            self.stats["accrued_calculated"] += 1
            
            # Extract coupon for reference (optional)
            coupon = self.extract_coupon_from_description(description)
            
            return {
                'isin': isin,
                'description': description,
                'coupon': coupon,
                'maturity': maturity_str,
                'price': price,
                'mv_usd': mv_usd,
                'par_val': par_val,
                'bloomberg_differential_per_million': bloomberg_differential,
                'settlement_date': self.settlement_date,
                'calculation_method': 'bloomberg_mv_par_differential',
                'calculation_timestamp': datetime.now().isoformat(),
                'country': row.get('country'),
                'ticker': row.get('ticker'),
                'rating': row.get('index_rating_string', '').replace('(', '').replace(')', ''),
                'ytw': row.get('ytw'),
                'oas': row.get('oas'),
                'weight': row.get('weight')
            }
            
        except Exception as e:
            self.stats["calculation_errors"] += 1
            logger.debug(f"Error processing bond {row.get('isin', 'unknown')}: {e}")
            return None

    def create_validation_table(self, results_df: pd.DataFrame, 
                              target_db_path: str = None) -> str:
        """
        Create bloomberg_accrued_benchmarks table for validation
        """
        if target_db_path is None:
            target_db_path = self.source_db_path
        
        logger.info(f"📊 Creating validation table in {target_db_path}...")
        
        # Connect to database
        conn = sqlite3.connect(target_db_path)
        
        # Create table
        table_name = "bloomberg_accrued_benchmarks"
        results_df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # Add indexes for performance
        cursor = conn.cursor()
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_isin ON {table_name} (isin)")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_differential ON {table_name} (bloomberg_differential_per_million)")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Table '{table_name}' created with {len(results_df):,} records")
        return table_name

    def generate_validation_summary(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary for validation framework integration"""
        return {
            "database_path": self.source_db_path,
            "table_name": "bloomberg_accrued_benchmarks",
            "settlement_date": self.settlement_date,
            "calculation_method": "bloomberg_mv_par_differential",
            "formula": "(mv_usd - par_val) / par_val * 1000000",
            "total_benchmarks": len(results_df),
            "differential_range": {
                "min": float(results_df['bloomberg_differential_per_million'].min()),
                "max": float(results_df['bloomberg_differential_per_million'].max()),
                "mean": float(results_df['bloomberg_differential_per_million'].mean())
            },
            "countries": results_df['country'].value_counts().head(10).to_dict(),
            "ready_for_validation": True,
            "integration_notes": [
                "Update production_validation.py BLOOMBERG_DB_PATH to quantlib_project_v3/bloomberg_index.db",
                "Change table reference to bloomberg_accrued_benchmarks",
                "Update column references for bloomberg_differential_per_million",
                "This calculates market value vs par value spread, not traditional accrued interest"
            ]
        }


def main():
    """
    Main function to calculate Bloomberg market value differential benchmarks
    """
    print("🏦 Bloomberg Market Value Differential Calculator")
    print("=" * 55)
    
    # Configuration
    source_db = "/Users/andyseaman/Notebooks/quantlib_project_v3/bloomberg_index.db"
    settlement_date = "2025-04-17"  # Same as your other validation work
    
    print(f"Source database: {source_db}")
    print(f"Settlement date: {settlement_date}")
    print(f"Formula: (mv_usd - par_val) / par_val * 1000000")
    print()
    
    # Initialize calculator
    calculator = BloombergAccruedCalculator(source_db, settlement_date)
    
    # Process all bonds
    results_df = calculator.process_all_bonds()
    
    if len(results_df) == 0:
        print("❌ No bonds processed successfully")
        return
    
    # Create validation table
    table_name = calculator.create_validation_table(results_df)
    
    # Generate summary
    summary = calculator.generate_validation_summary(results_df)
    
    print(f"\n🎯 SUCCESS: {len(results_df):,} Bloomberg benchmarks ready!")
    print(f"✅ Table created: {table_name}")
    print(f"📊 Differential range: {summary['differential_range']['min']:,.0f} - {summary['differential_range']['max']:,.0f}")
    print(f"💰 Average differential: {summary['differential_range']['mean']:,.0f} per $1M")
    
    print(f"\n🔗 Integration Steps:")
    for step in summary['integration_notes']:
        print(f"   • {step}")
    
    print(f"\n✅ Ready to update validation framework with {len(results_df):,} benchmarks!")
    print(f"📝 Note: This calculates market value vs par differential, not traditional accrued interest")
    
    return results_df, summary


if __name__ == "__main__":
    results, summary = main()
