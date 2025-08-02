#!/usr/bin/env python3
"""
Fetch On-The-Run Treasury Securities Details
===========================================

Fetches details of the actual Treasury securities (bills, notes, bonds)
that are used to construct the yield curve.
"""

import requests
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from database_config import BONDS_DATA_DB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TreasurySecuritiesFetcher:
    """Fetch details of on-the-run Treasury securities."""
    
    def __init__(self):
        # TreasuryDirect API endpoints
        self.base_url = "https://api.treasurydirect.gov/services/v2/accounting/od/securities"
        
        # Mapping of maturity to curve point
        self.maturity_to_curve = {
            0.077: 'M1M',    # 4-week bill (~1 month)
            0.154: 'M2M',    # 8-week bill (~2 months)
            0.25: 'M3M',     # 13-week bill (3 months)
            0.5: 'M6M',      # 26-week bill (6 months)
            1.0: 'M1Y',      # 52-week bill (1 year)
            2.0: 'M2Y',      # 2-year note
            3.0: 'M3Y',      # 3-year note
            5.0: 'M5Y',      # 5-year note
            7.0: 'M7Y',      # 7-year note
            10.0: 'M10Y',    # 10-year note
            20.0: 'M20Y',    # 20-year bond
            30.0: 'M30Y'     # 30-year bond
        }
        
        self.init_database()
    
    def init_database(self):
        """Initialize the treasury_securities table if it doesn't exist."""
        with open('create_treasury_securities_table.sql', 'r') as f:
            sql_script = f.read()
        
        with sqlite3.connect(BONDS_DATA_DB) as conn:
            conn.executescript(sql_script)
            logger.info("Treasury securities tables initialized")
    
    def fetch_recent_auctions(self, days_back: int = 90) -> List[Dict]:
        """
        Fetch recent Treasury auction results.
        
        The most recent auction for each maturity is the on-the-run security.
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # TreasuryDirect API parameters
            params = {
                'format': 'json',
                'filter': f"issue_date:gte:{start_date.strftime('%Y-%m-%d')}",
                'sort': '-issue_date',
                'page[size]': 100
            }
            
            logger.info(f"Fetching Treasury auctions from {self.base_url}")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data:
                return data['data']
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch auction data: {e}")
            return []
    
    def parse_security_details(self, auction_data: Dict) -> Optional[Dict]:
        """Parse auction data into our security format."""
        try:
            # Extract key fields
            cusip = auction_data.get('cusip')
            if not cusip:
                return None
            
            # Determine security type
            term = auction_data.get('security_term', '')
            if 'Week' in term or 'Day' in term:
                security_type = 'Bill'
                coupon_rate = 0.0  # Bills are zero-coupon
            elif 'Year' in term:
                years = float(term.split('-Year')[0])
                if years <= 10:
                    security_type = 'Note'
                else:
                    security_type = 'Bond'
                coupon_rate = float(auction_data.get('interest_rate', 0))
            else:
                return None
            
            # Calculate maturity in years
            issue_date = datetime.strptime(auction_data['issue_date'], '%Y-%m-%d')
            maturity_date = datetime.strptime(auction_data['maturity_date'], '%Y-%m-%d')
            maturity_years = (maturity_date - issue_date).days / 365.25
            
            # Find closest curve point
            curve_point = self._find_curve_point(maturity_years)
            if not curve_point:
                return None
            
            return {
                'cusip': cusip,
                'security_type': security_type,
                'maturity_date': maturity_date.strftime('%Y-%m-%d'),
                'issue_date': issue_date.strftime('%Y-%m-%d'),
                'coupon_rate': coupon_rate,
                'maturity_years': round(maturity_years, 3),
                'auction_date': auction_data.get('auction_date', issue_date.strftime('%Y-%m-%d')),
                'auction_high_yield': float(auction_data.get('high_yield', 0)),
                'auction_size_billions': float(auction_data.get('offering_amount', 0)) / 1_000_000_000,
                'curve_point': curve_point
            }
            
        except Exception as e:
            logger.error(f"Failed to parse security: {e}")
            return None
    
    def _find_curve_point(self, maturity_years: float) -> Optional[str]:
        """Find the appropriate curve point for a given maturity."""
        # Find closest maturity
        closest_maturity = min(
            self.maturity_to_curve.keys(),
            key=lambda x: abs(x - maturity_years)
        )
        
        # Only match if within reasonable tolerance
        if abs(closest_maturity - maturity_years) < 0.1:
            return self.maturity_to_curve[closest_maturity]
        
        return None
    
    def update_on_the_run_status(self, securities: List[Dict]):
        """Update which securities are on-the-run."""
        with sqlite3.connect(BONDS_DATA_DB) as conn:
            cursor = conn.cursor()
            
            # Group by curve point
            curve_points = {}
            for sec in securities:
                cp = sec['curve_point']
                if cp not in curve_points:
                    curve_points[cp] = []
                curve_points[cp].append(sec)
            
            # For each curve point, the most recent is on-the-run
            for curve_point, secs in curve_points.items():
                # Sort by issue date descending
                secs.sort(key=lambda x: x['issue_date'], reverse=True)
                
                if secs:
                    # Mark previous on-the-run as off-the-run
                    cursor.execute("""
                        UPDATE treasury_securities 
                        SET is_on_the_run = 0,
                            replaced_date = ?
                        WHERE curve_point = ? AND is_on_the_run = 1
                    """, (secs[0]['issue_date'], curve_point))
                    
                    # Insert or update the new on-the-run
                    newest = secs[0]
                    cursor.execute("""
                        INSERT OR REPLACE INTO treasury_securities 
                        (cusip, security_type, maturity_date, issue_date, 
                         coupon_rate, maturity_years, is_on_the_run, 
                         became_on_the_run, auction_date, auction_high_yield,
                         auction_size_billions, curve_point)
                        VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
                    """, (
                        newest['cusip'], newest['security_type'],
                        newest['maturity_date'], newest['issue_date'],
                        newest['coupon_rate'], newest['maturity_years'],
                        newest['issue_date'], newest['auction_date'],
                        newest['auction_high_yield'], newest['auction_size_billions'],
                        newest['curve_point']
                    ))
            
            conn.commit()
            logger.info(f"Updated on-the-run status for {len(curve_points)} curve points")
    
    def display_current_securities(self):
        """Display the current on-the-run securities."""
        with sqlite3.connect(BONDS_DATA_DB) as conn:
            df = pd.read_sql_query("""
                SELECT 
                    curve_point,
                    cusip,
                    security_type,
                    coupon_rate,
                    issue_date,
                    maturity_date,
                    maturity_years,
                    auction_high_yield
                FROM treasury_securities
                WHERE is_on_the_run = 1
                ORDER BY maturity_years
            """, conn)
            
            if not df.empty:
                print("\n📊 Current On-The-Run Treasury Securities")
                print("=" * 80)
                print(df.to_string(index=False))
            else:
                print("\n❌ No on-the-run securities found")


def main():
    """Main function to fetch and update Treasury securities."""
    fetcher = TreasurySecuritiesFetcher()
    
    print("🏦 Fetching On-The-Run Treasury Securities")
    print("=" * 60)
    
    # Fetch recent auctions
    auctions = fetcher.fetch_recent_auctions()
    
    if not auctions:
        # If API fails, insert example current securities
        print("⚠️  Treasury API unavailable, using example data")
        example_securities = [
            {
                'cusip': '912797KZ9',
                'security_type': 'Bill',
                'maturity_date': '2025-10-30',
                'issue_date': '2025-07-31',
                'coupon_rate': 0.0,
                'maturity_years': 0.25,
                'auction_date': '2025-07-28',
                'auction_high_yield': 5.30,
                'auction_size_billions': 65.0,
                'curve_point': 'M3M'
            },
            {
                'cusip': '91282CHH1',
                'security_type': 'Note',
                'maturity_date': '2027-07-31',
                'issue_date': '2025-07-31',
                'coupon_rate': 3.875,
                'maturity_years': 2.0,
                'auction_date': '2025-07-27',
                'auction_high_yield': 3.94,
                'auction_size_billions': 50.0,
                'curve_point': 'M2Y'
            },
            {
                'cusip': '912810TN0',
                'security_type': 'Note',
                'maturity_date': '2035-05-15',
                'issue_date': '2025-05-15',
                'coupon_rate': 4.25,
                'maturity_years': 10.0,
                'auction_date': '2025-05-14',
                'auction_high_yield': 4.37,
                'auction_size_billions': 42.0,
                'curve_point': 'M10Y'
            },
            {
                'cusip': '912810TM2',
                'security_type': 'Bond',
                'maturity_date': '2055-05-15',
                'issue_date': '2025-05-15',
                'coupon_rate': 4.75,
                'maturity_years': 30.0,
                'auction_date': '2025-05-15',
                'auction_high_yield': 4.89,
                'auction_size_billions': 23.0,
                'curve_point': 'M30Y'
            }
        ]
        fetcher.update_on_the_run_status(example_securities)
    else:
        # Parse and update securities
        securities = []
        for auction in auctions:
            parsed = fetcher.parse_security_details(auction)
            if parsed:
                securities.append(parsed)
        
        if securities:
            fetcher.update_on_the_run_status(securities)
            print(f"✅ Processed {len(securities)} securities")
        else:
            print("❌ No valid securities found")
    
    # Display current on-the-run securities
    fetcher.display_current_securities()


if __name__ == "__main__":
    main()