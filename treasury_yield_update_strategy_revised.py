#!/usr/bin/env python3
"""
Treasury Yield Curve Update Strategy (Revised)
==============================================

Corrected strategy based on the fact that Treasury yields are published
ONCE per day after market close (typically around 3:30-4:00 PM ET).
"""

import sqlite3
import logging
from datetime import datetime, time, timedelta
from typing import Dict, Optional, Tuple
from pathlib import Path
import pytz

from database_config import BONDS_DATA_DB

logger = logging.getLogger(__name__)


class TreasuryYieldUpdater:
    """Manages Treasury yield curve updates based on daily publication schedule."""
    
    def __init__(self, db_path: Path = BONDS_DATA_DB):
        self.db_path = db_path
        # Treasury yields typically published around 3:30-4:00 PM ET
        self.publish_time_et = time(16, 0)  # 4:00 PM ET
        self.et_timezone = pytz.timezone('US/Eastern')
        
    def get_expected_publish_time(self, date: datetime) -> datetime:
        """
        Get the expected publish time for a given date.
        
        Treasury yields are published once per business day after market close.
        No updates on weekends or market holidays.
        """
        # Combine date with publish time in ET
        publish_dt = self.et_timezone.localize(
            datetime.combine(date.date(), self.publish_time_et)
        )
        
        # Skip weekends
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            # Move to next Monday
            days_until_monday = 7 - date.weekday()
            publish_dt += timedelta(days=days_until_monday)
        
        return publish_dt
    
    def check_data_status(self) -> Dict[str, any]:
        """
        Check the status of yield curve data.
        
        Returns detailed information about data freshness and update needs.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get the most recent data
                cursor.execute("""
                    SELECT Date, updated_at 
                    FROM tsys_enhanced 
                    ORDER BY Date DESC 
                    LIMIT 1
                """)
                
                result = cursor.fetchone()
                if not result:
                    return {
                        'status': 'NO_DATA',
                        'needs_update': True,
                        'reason': 'No yield curve data found in database'
                    }
                
                latest_data_date = datetime.strptime(result[0], '%Y-%m-%d')
                last_update_time = datetime.strptime(result[1], '%Y-%m-%d %H:%M:%S')
                
                # Current time
                now = datetime.now()
                today = now.date()
                
                # Determine the last business day with available data
                last_business_day = self._get_last_business_day(now)
                
                status = {
                    'latest_data_date': latest_data_date,
                    'last_update_time': last_update_time,
                    'last_business_day': last_business_day,
                    'current_time': now
                }
                
                # Check if we have data for the last business day
                if latest_data_date.date() >= last_business_day.date():
                    status.update({
                        'status': 'CURRENT',
                        'needs_update': False,
                        'reason': 'Data is current (have latest business day)'
                    })
                else:
                    # Calculate how many business days we're missing
                    missing_days = self._count_business_days(
                        latest_data_date.date(), 
                        last_business_day.date()
                    )
                    status.update({
                        'status': 'STALE',
                        'needs_update': True,
                        'reason': f'Missing {missing_days} business days of data',
                        'missing_days': missing_days
                    })
                
                return status
                
        except Exception as e:
            logger.error(f"Error checking data status: {e}")
            return {
                'status': 'ERROR',
                'needs_update': True,
                'reason': f'Error checking data: {e}'
            }
    
    def _get_last_business_day(self, from_date: datetime) -> datetime:
        """Get the last business day (Mon-Fri) from a given date."""
        current = from_date
        
        # If it's before publish time on a weekday, use previous business day
        if current.weekday() < 5 and current.time() < self.publish_time_et:
            current -= timedelta(days=1)
        
        # Skip back to Friday if weekend
        while current.weekday() >= 5:
            current -= timedelta(days=1)
            
        return current
    
    def _count_business_days(self, start_date, end_date) -> int:
        """Count business days between two dates."""
        count = 0
        current = start_date + timedelta(days=1)
        
        while current <= end_date:
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                count += 1
            current += timedelta(days=1)
            
        return count


def create_realistic_update_strategies():
    """
    Define update strategies based on daily yield publication.
    """
    
    strategies = {
        "DAILY_SCHEDULED": {
            "description": "Update once daily after Treasury publishes data",
            "schedule": "0 17 * * 1-5",  # 5 PM ET, Monday-Friday
            "pros": [
                "Aligns with Treasury publication schedule",
                "Predictable and reliable",
                "No wasted API calls",
                "Simple to implement and monitor"
            ],
            "cons": [
                "No real-time updates (because they don't exist)",
                "Need to handle holidays and market closures"
            ],
            "implementation": """
# Cron job for 5 PM ET (adjust for your timezone):
0 17 * * 1-5 /usr/bin/python3 /path/to/update_treasury_yields.py

# Or for 6 PM ET to ensure data is available:
0 18 * * 1-5 /usr/bin/python3 /path/to/update_treasury_yields.py
            """
        },
        
        "LAZY_FETCH": {
            "description": "Check for new data on first request each day",
            "pros": [
                "No updates if system not in use",
                "Automatic catch-up after downtime",
                "No scheduled job needed"
            ],
            "cons": [
                "First user of the day experiences delay",
                "Need to handle concurrent update attempts"
            ],
            "implementation": """
# In API request handler:
status = updater.check_data_status()
if status['needs_update']:
    # Fetch yesterday's close data
    update_treasury_yields_for_date(status['last_business_day'])
            """
        },
        
        "HYBRID_DAILY": {
            "description": "Daily schedule with on-demand catch-up (RECOMMENDED)",
            "pros": [
                "Best of both approaches",
                "Handles missed updates gracefully",
                "Users can force refresh if needed",
                "Minimal complexity"
            ],
            "cons": [
                "Slightly more complex than pure scheduled"
            ],
            "implementation": """
# Daily cron at 6 PM ET:
0 18 * * 1-5 /usr/bin/python3 /path/to/update_treasury_yields.py

# In API: Check if data is current
status = updater.check_data_status()
if status['needs_update']:
    logger.warning(f"Yield data is stale: {status['reason']}")
    # Return stale data with warning, update in background
            """
        }
    }
    
    return strategies


def display_corrected_recommendation():
    """Display the corrected recommendation for treasury yield updates."""
    print("🏦 Treasury Yield Curve Update Strategy (Corrected)")
    print("=" * 60)
    print("📌 KEY FACT: Treasury yields are published ONCE per day after market close")
    print("=" * 60)
    
    # Check current state
    updater = TreasuryYieldUpdater()
    status = updater.check_data_status()
    
    print("\n📊 Current Data Status:")
    print(f"   Latest Data: {status.get('latest_data_date', 'N/A')}")
    print(f"   Last Update: {status.get('last_update_time', 'N/A')}")
    print(f"   Status: {status.get('status', 'UNKNOWN')}")
    print(f"   Reason: {status.get('reason', 'N/A')}")
    
    if status.get('missing_days'):
        print(f"   ⚠️  Missing {status['missing_days']} business days of data")
    
    # Display strategies
    print("\n📋 Realistic Update Strategies:")
    strategies = create_realistic_update_strategies()
    
    for name, strategy in strategies.items():
        recommended = " 🌟 RECOMMENDED" if name == "HYBRID_DAILY" else ""
        print(f"\n{name}{recommended}:")
        print(f"   {strategy['description']}")
        print("\n   Pros:")
        for pro in strategy['pros']:
            print(f"   ✅ {pro}")
        print("\n   Cons:")
        for con in strategy['cons']:
            print(f"   ❌ {con}")
    
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATION: Use HYBRID_DAILY approach")
    print("=" * 60)
    print("""
Implementation Plan:
1. Set up daily cron job at 6 PM ET (after market close)
2. Add status check to API responses
3. Log warnings when serving stale data
4. Optional: Email alerts if updates fail for multiple days
5. Handle market holidays (check Treasury calendar)

Note: Since you're missing 35 days of data, you'll need to:
- Backfill historical data from your data provider
- Or accept the gap and start fresh from today
    """)


if __name__ == "__main__":
    display_corrected_recommendation()