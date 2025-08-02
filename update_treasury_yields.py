#!/usr/bin/env python3
"""
Update Treasury Yields in tsys_enhanced Table
=============================================

Script to update treasury yield curve data with intelligent caching.
Can be run manually, via cron, or called from API.
"""

import sqlite3
import logging
import requests
from datetime import datetime, timedelta
import pandas as pd
import json
import sys
from typing import Dict, Optional
import argparse

from database_config import BONDS_DATA_DB
from treasury_yield_update_strategy import TreasuryYieldUpdater

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TreasuryYieldFetcher:
    """Fetches treasury yield data from various sources."""
    
    def __init__(self):
        # In production, these would be actual Treasury data endpoints
        # For now, using mock data structure
        self.sources = {
            'primary': 'https://api.treasury.gov/yields',  # Example
            'backup': 'https://data.treasury.gov/feed'     # Example
        }
    
    def fetch_latest_yields(self) -> Dict[str, float]:
        """
        Fetch latest treasury yields from data source.
        
        Returns:
            Dictionary mapping tenor to yield (as percentage)
            e.g., {'1M': 4.25, '3M': 4.50, ..., '30Y': 4.85}
        """
        try:
            # TODO: Implement actual API call to Treasury data source
            # For now, return mock data with slight variations
            
            # This would be replaced with actual API call:
            # response = requests.get(self.sources['primary'], timeout=10)
            # data = response.json()
            
            # Mock data for demonstration
            base_yields = {
                'M1M': 4.25,
                'M2M': 4.30,
                'M3M': 4.45,
                'M6M': 4.65,
                'M1Y': 4.10,
                'M2Y': 3.95,
                'M3Y': 3.88,
                'M5Y': 3.92,
                'M7Y': 4.05,
                'M10Y': 4.22,
                'M20Y': 4.55,
                'M30Y': 4.68
            }
            
            # Add small random variations to simulate market movement
            import random
            for tenor in base_yields:
                base_yields[tenor] += random.uniform(-0.05, 0.05)
                base_yields[tenor] = round(base_yields[tenor], 2)
            
            logger.info(f"Fetched yields: {base_yields}")
            return base_yields
            
        except Exception as e:
            logger.error(f"Error fetching treasury yields: {e}")
            raise


def update_treasury_yields(force: bool = False) -> Dict[str, any]:
    """
    Update treasury yields in database.
    
    Args:
        force: Force update even if cache is fresh
        
    Returns:
        Dictionary with update status and details
    """
    result = {
        'status': 'success',
        'updated': False,
        'message': '',
        'data_date': None,
        'yields_updated': 0
    }
    
    try:
        # Check if update is needed
        updater = TreasuryYieldUpdater()
        recommendation = updater.get_update_recommendation()
        
        if not force and not recommendation['needs_update']:
            result['message'] = f"Cache is fresh: {recommendation['reason']}"
            logger.info(result['message'])
            return result
        
        # Fetch latest yields
        fetcher = TreasuryYieldFetcher()
        yields = fetcher.fetch_latest_yields()
        
        if not yields:
            raise ValueError("No yield data received")
        
        # Update database
        with sqlite3.connect(BONDS_DATA_DB) as conn:
            cursor = conn.cursor()
            
            # Get today's date
            today = datetime.now().date()
            
            # Check if today's data already exists
            cursor.execute(
                "SELECT COUNT(*) FROM tsys_enhanced WHERE Date = ?",
                (today.strftime('%Y-%m-%d'),)
            )
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Update existing record
                set_clause = ", ".join([f"{k} = ?" for k in yields.keys()])
                values = list(yields.values()) + [today.strftime('%Y-%m-%d')]
                
                cursor.execute(f"""
                    UPDATE tsys_enhanced 
                    SET {set_clause}, 
                        updated_at = CURRENT_TIMESTAMP,
                        source = 'Treasury API Update'
                    WHERE Date = ?
                """, values)
            else:
                # Insert new record
                columns = ['Date'] + list(yields.keys()) + ['source']
                values = [today.strftime('%Y-%m-%d')] + list(yields.values()) + ['Treasury API Update']
                
                placeholders = ", ".join(["?" for _ in values])
                columns_str = ", ".join(columns)
                
                cursor.execute(f"""
                    INSERT INTO tsys_enhanced ({columns_str})
                    VALUES ({placeholders})
                """, values)
            
            conn.commit()
            
            result['updated'] = True
            result['data_date'] = today.strftime('%Y-%m-%d')
            result['yields_updated'] = len(yields)
            result['message'] = f"Successfully updated {len(yields)} yield points for {today}"
            
            logger.info(result['message'])
            
    except Exception as e:
        result['status'] = 'error'
        result['message'] = str(e)
        logger.error(f"Failed to update treasury yields: {e}")
    
    return result


def get_current_yields(date: Optional[str] = None) -> Dict[str, float]:
    """
    Get current treasury yields from database.
    
    Args:
        date: Specific date to fetch (YYYY-MM-DD format), defaults to latest
        
    Returns:
        Dictionary of tenor to yield mappings
    """
    try:
        with sqlite3.connect(BONDS_DATA_DB) as conn:
            if date:
                query = "SELECT * FROM tsys_enhanced WHERE Date = ?"
                df = pd.read_sql_query(query, conn, params=[date])
            else:
                query = "SELECT * FROM tsys_enhanced ORDER BY Date DESC LIMIT 1"
                df = pd.read_sql_query(query, conn)
            
            if df.empty:
                return {}
            
            # Extract yield columns
            row = df.iloc[0]
            yields = {}
            for col in df.columns:
                if col.startswith('M') and (col.endswith('Y') or col.endswith('M')):
                    if pd.notna(row[col]):
                        yields[col] = row[col]
            
            return yields
            
    except Exception as e:
        logger.error(f"Error fetching current yields: {e}")
        return {}


def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description='Update Treasury Yields')
    parser.add_argument('--force', action='store_true', 
                       help='Force update even if cache is fresh')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check if update is needed')
    parser.add_argument('--show-current', action='store_true',
                       help='Show current yields in database')
    
    args = parser.parse_args()
    
    if args.check_only:
        updater = TreasuryYieldUpdater()
        recommendation = updater.get_update_recommendation()
        print(json.dumps(recommendation, indent=2, default=str))
        return 0 if not recommendation['needs_update'] else 1
    
    if args.show_current:
        yields = get_current_yields()
        if yields:
            print("Current Treasury Yields:")
            for tenor, yield_val in sorted(yields.items()):
                print(f"  {tenor}: {yield_val:.2f}%")
        else:
            print("No yield data found")
        return 0
    
    # Perform update
    result = update_treasury_yields(force=args.force)
    print(json.dumps(result, indent=2))
    
    return 0 if result['status'] == 'success' else 1


if __name__ == "__main__":
    sys.exit(main())