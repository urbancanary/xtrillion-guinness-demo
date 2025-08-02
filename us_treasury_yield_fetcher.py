#!/usr/bin/env python3
"""
US Treasury Yield Curve Fetcher
================================

Fetches daily yield curve data directly from US Treasury website.
The Treasury publishes par yield curve rates daily around 3:30 PM ET.

Treasury Yield Curve Methodology:
- Uses most recently auctioned "on-the-run" securities
- Monotone convex spline interpolation
- Based on bid-side market price quotations at ~3:30 PM ET
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import logging
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from database_config import BONDS_DATA_DB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class USTreasuryYieldFetcher:
    """Fetch yield curve data from US Treasury website."""
    
    def __init__(self):
        # US Treasury data endpoints
        self.base_url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates"
        
        # Daily Treasury Yield Curve Rates endpoint
        # Format: XML feed with daily par yield curve rates
        self.yield_curve_url = (
            "https://home.treasury.gov/resource-center/data-chart-center/"
            "interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value={year}"
        )
        
        # Mapping of Treasury tenors to our database columns
        self.tenor_mapping = {
            '1 Mo': 'M1M',
            '2 Mo': 'M2M', 
            '3 Mo': 'M3M',
            '6 Mo': 'M6M',
            '1 Yr': 'M1Y',
            '2 Yr': 'M2Y',
            '3 Yr': 'M3Y',
            '5 Yr': 'M5Y',
            '7 Yr': 'M7Y',
            '10 Yr': 'M10Y',
            '20 Yr': 'M20Y',
            '30 Yr': 'M30Y'
        }
    
    def fetch_yield_curve_data(self, date: Optional[datetime] = None) -> Dict[str, float]:
        """
        Fetch yield curve data for a specific date.
        
        Args:
            date: Target date (defaults to today)
            
        Returns:
            Dictionary mapping tenor codes to yields (as percentages)
        """
        if date is None:
            date = datetime.now()
        
        year = date.year
        
        try:
            # Fetch data from Treasury website
            url = self.yield_curve_url.format(year=year)
            logger.info(f"Fetching Treasury yields from: {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse the response (could be XML or HTML table)
            # Treasury typically provides data in XML format
            if 'xml' in response.headers.get('Content-Type', ''):
                return self._parse_xml_response(response.text, date)
            else:
                return self._parse_html_response(response.text, date)
                
        except Exception as e:
            logger.error(f"Failed to fetch Treasury yields: {e}")
            # Try alternative parsing method
            return self._fetch_alternative_format(date)
    
    def _parse_xml_response(self, xml_data: str, target_date: datetime) -> Dict[str, float]:
        """Parse XML response from Treasury."""
        try:
            root = ET.fromstring(xml_data)
            
            # Find data for target date
            date_str = target_date.strftime('%Y-%m-%d')
            yields = {}
            
            # Treasury XML structure varies, but typically:
            # <entry><date>2025-07-31</date><bc_1month>5.25</bc_1month>...</entry>
            for entry in root.findall('.//entry'):
                entry_date = entry.find('date')
                if entry_date is not None and entry_date.text == date_str:
                    # Extract yields
                    for tenor_us, tenor_db in self.tenor_mapping.items():
                        # XML tags might be like 'bc_1month', 'bc_2year', etc.
                        tag_variations = [
                            f"bc_{tenor_us.lower().replace(' ', '')}",
                            f"tc_{tenor_us.lower().replace(' ', '')}",
                            tenor_us.lower().replace(' ', '_')
                        ]
                        
                        for tag in tag_variations:
                            elem = entry.find(tag)
                            if elem is not None and elem.text:
                                try:
                                    yields[tenor_db] = float(elem.text)
                                    break
                                except ValueError:
                                    continue
            
            return yields
            
        except Exception as e:
            logger.error(f"XML parsing failed: {e}")
            return {}
    
    def _parse_html_response(self, html_data: str, target_date: datetime) -> Dict[str, float]:
        """Parse HTML table response from Treasury."""
        try:
            # Use pandas to parse HTML tables
            tables = pd.read_html(html_data)
            
            if not tables:
                return {}
            
            # Usually the first table contains the yield curve data
            df = tables[0]
            
            # Find row for target date
            date_str = target_date.strftime('%m/%d/%Y')
            date_col = df.columns[0]  # Usually 'Date' is first column
            
            target_row = df[df[date_col] == date_str]
            if target_row.empty:
                # Try alternative date format
                date_str = target_date.strftime('%Y-%m-%d')
                target_row = df[df[date_col] == date_str]
            
            if not target_row.empty:
                yields = {}
                row = target_row.iloc[0]
                
                # Map columns to our tenor codes
                for col in df.columns[1:]:  # Skip date column
                    if col in self.tenor_mapping:
                        try:
                            yields[self.tenor_mapping[col]] = float(row[col])
                        except:
                            continue
                
                return yields
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
        
        return {}
    
    def _fetch_alternative_format(self, date: datetime) -> Dict[str, float]:
        """
        Alternative method: Fetch from Treasury Direct API or CSV format.
        """
        # Treasury also provides data in CSV format
        csv_url = (
            f"https://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData?"
            f"$filter=NEW_DATE eq datetime'{date.strftime('%Y-%m-%d')}'"
        )
        
        try:
            response = requests.get(csv_url, timeout=30)
            if response.status_code == 200:
                # Parse JSON response
                data = response.json()
                if 'value' in data and data['value']:
                    record = data['value'][0]
                    
                    yields = {}
                    # Map fields like 'BC_1MONTH' to our codes
                    field_mapping = {
                        'BC_1MONTH': 'M1M',
                        'BC_2MONTH': 'M2M',
                        'BC_3MONTH': 'M3M',
                        'BC_6MONTH': 'M6M',
                        'BC_1YEAR': 'M1Y',
                        'BC_2YEAR': 'M2Y',
                        'BC_3YEAR': 'M3Y',
                        'BC_5YEAR': 'M5Y',
                        'BC_7YEAR': 'M7Y',
                        'BC_10YEAR': 'M10Y',
                        'BC_20YEAR': 'M20Y',
                        'BC_30YEAR': 'M30Y'
                    }
                    
                    for field, tenor in field_mapping.items():
                        if field in record and record[field] is not None:
                            yields[tenor] = float(record[field])
                    
                    return yields
                    
        except Exception as e:
            logger.error(f"Alternative fetch failed: {e}")
        
        return {}
    
    def update_database(self, yields: Dict[str, float], date: datetime) -> bool:
        """Update the tsys_enhanced table with fetched yields."""
        if not yields:
            logger.warning("No yields to update")
            return False
        
        try:
            with sqlite3.connect(BONDS_DATA_DB) as conn:
                cursor = conn.cursor()
                date_str = date.strftime('%Y-%m-%d')
                
                # Check if date exists
                cursor.execute("SELECT COUNT(*) FROM tsys_enhanced WHERE Date = ?", (date_str,))
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    # Update existing
                    set_parts = [f"{tenor} = ?" for tenor in yields.keys()]
                    values = list(yields.values()) + [date_str]
                    
                    query = f"""
                        UPDATE tsys_enhanced 
                        SET {', '.join(set_parts)}, 
                            updated_at = CURRENT_TIMESTAMP,
                            source = 'US Treasury Direct'
                        WHERE Date = ?
                    """
                    cursor.execute(query, values)
                else:
                    # Insert new
                    columns = ['Date'] + list(yields.keys()) + ['source']
                    values = [date_str] + list(yields.values()) + ['US Treasury Direct']
                    
                    placeholders = ', '.join(['?' for _ in values])
                    columns_str = ', '.join(columns)
                    
                    query = f"INSERT INTO tsys_enhanced ({columns_str}) VALUES ({placeholders})"
                    cursor.execute(query, values)
                
                conn.commit()
                logger.info(f"Updated yields for {date_str}: {yields}")
                return True
                
        except Exception as e:
            logger.error(f"Database update failed: {e}")
            return False


def main():
    """Main function to fetch and update Treasury yields."""
    fetcher = USTreasuryYieldFetcher()
    
    # Fetch today's yields (or most recent business day)
    today = datetime.now()
    
    # If it's before 4 PM ET, use previous business day
    if today.hour < 16:  # Simplified check
        today -= timedelta(days=1)
    
    # Skip weekends
    while today.weekday() >= 5:  # Saturday = 5, Sunday = 6
        today -= timedelta(days=1)
    
    logger.info(f"Fetching Treasury yields for {today.strftime('%Y-%m-%d')}")
    
    yields = fetcher.fetch_yield_curve_data(today)
    
    if yields:
        logger.info("Successfully fetched yields:")
        for tenor, rate in sorted(yields.items()):
            print(f"  {tenor}: {rate:.2f}%")
        
        # Update database
        if fetcher.update_database(yields, today):
            print("\n✅ Database updated successfully!")
        else:
            print("\n❌ Failed to update database")
    else:
        logger.error("Failed to fetch yield data")
        print("\n❌ No yield data retrieved")
        print("\nNote: Treasury data endpoint format may have changed.")
        print("Check https://home.treasury.gov/resource-center/data-chart-center/interest-rates")


if __name__ == "__main__":
    main()