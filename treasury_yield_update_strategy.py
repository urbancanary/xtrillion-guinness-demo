#!/usr/bin/env python3
"""
Treasury Yield Curve Update Strategy
====================================

Hybrid approach for updating tsys_enhanced table that balances data freshness
with system efficiency.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import os
from pathlib import Path

# Import database config
from database_config import BONDS_DATA_DB

logger = logging.getLogger(__name__)


class TreasuryYieldUpdater:
    """Manages Treasury yield curve updates with intelligent caching."""
    
    def __init__(self, db_path: Path = BONDS_DATA_DB):
        self.db_path = db_path
        self.cache_duration_hours = 4  # Cache for 4 hours during market hours
        self.weekend_cache_hours = 72  # Cache for 3 days on weekends
        
    def check_data_freshness(self) -> Tuple[bool, Optional[datetime], Optional[datetime]]:
        """
        Check if yield curve data needs updating.
        
        Returns:
            Tuple of (needs_update, latest_data_date, last_update_time)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get the most recent data date and update time
                cursor.execute("""
                    SELECT Date, updated_at 
                    FROM tsys_enhanced 
                    ORDER BY Date DESC 
                    LIMIT 1
                """)
                
                result = cursor.fetchone()
                if not result:
                    return True, None, None
                
                latest_date = datetime.strptime(result[0], '%Y-%m-%d')
                last_update = datetime.strptime(result[1], '%Y-%m-%d %H:%M:%S')
                
                # Determine if update is needed
                now = datetime.now()
                today = now.date()
                
                # Check if it's a weekend
                is_weekend = now.weekday() >= 5  # Saturday = 5, Sunday = 6
                
                # Determine cache duration
                cache_duration = timedelta(hours=self.weekend_cache_hours if is_weekend else self.cache_duration_hours)
                
                # Update needed if:
                # 1. Data is older than today (missing recent data)
                # 2. Last update exceeded cache duration
                needs_update = (
                    latest_date.date() < today or 
                    (now - last_update) > cache_duration
                )
                
                return needs_update, latest_date, last_update
                
        except Exception as e:
            logger.error(f"Error checking data freshness: {e}")
            return True, None, None
    
    def get_update_recommendation(self) -> Dict[str, any]:
        """
        Get recommendation for update strategy based on current state.
        """
        needs_update, latest_date, last_update = self.check_data_freshness()
        now = datetime.now()
        
        recommendation = {
            "needs_update": needs_update,
            "latest_data_date": latest_date,
            "last_update_time": last_update,
            "current_time": now,
            "recommendation": "",
            "reason": ""
        }
        
        if not needs_update:
            hours_since_update = (now - last_update).total_seconds() / 3600
            recommendation["recommendation"] = "USE_CACHED"
            recommendation["reason"] = f"Data updated {hours_since_update:.1f} hours ago, still fresh"
        else:
            if latest_date is None:
                recommendation["recommendation"] = "UPDATE_IMMEDIATELY"
                recommendation["reason"] = "No yield curve data found"
            elif latest_date.date() < now.date():
                recommendation["recommendation"] = "UPDATE_IMMEDIATELY"
                recommendation["reason"] = f"Missing data for {(now.date() - latest_date.date()).days} days"
            else:
                recommendation["recommendation"] = "UPDATE_STALE_CACHE"
                recommendation["reason"] = f"Cache expired (last update: {last_update})"
        
        return recommendation


def create_update_strategies():
    """
    Define the three update strategies for different use cases.
    """
    
    strategies = {
        "SCHEDULED": {
            "description": "Daily scheduled updates for production",
            "schedule": "0 6,12,16,20 * * *",  # 6am, 12pm, 4pm, 8pm daily
            "pros": [
                "Predictable system load",
                "Guaranteed fresh data for most requests",
                "Can be run during off-peak hours",
                "Reduces API calls to Treasury data source"
            ],
            "cons": [
                "May have stale data between updates",
                "Unnecessary updates on weekends/holidays"
            ],
            "implementation": """
# Cron job (add to crontab -e):
0 6,12,16,20 * * * /usr/bin/python3 /path/to/update_treasury_yields.py --scheduled

# Or use systemd timer for more control
            """
        },
        
        "ON_DEMAND": {
            "description": "Update only when requested by users",
            "pros": [
                "Always provides latest available data",
                "No unnecessary updates",
                "User controls data freshness"
            ],
            "cons": [
                "Potential delays for first user each day",
                "Multiple concurrent requests could cause issues",
                "Unpredictable system load"
            ],
            "implementation": """
# In API endpoint:
if request.args.get('force_update'):
    update_treasury_yields()
return get_yields()
            """
        },
        
        "HYBRID": {
            "description": "Smart caching with automatic updates (RECOMMENDED)",
            "pros": [
                "Balances freshness with efficiency",
                "Automatic updates during market hours",
                "Cached data for rapid responses",
                "Weekend/holiday awareness"
            ],
            "cons": [
                "Slightly more complex implementation",
                "Need to maintain cache logic"
            ],
            "implementation": """
# Check cache on each request:
updater = TreasuryYieldUpdater()
recommendation = updater.get_update_recommendation()

if recommendation['needs_update']:
    # Update in background thread to avoid blocking
    threading.Thread(target=update_treasury_yields).start()
    
# Return current data (may be slightly stale during update)
return get_current_yields()
            """
        }
    }
    
    return strategies


def display_recommendation():
    """Display the recommendation for treasury yield updates."""
    print("🏦 Treasury Yield Curve Update Strategy Analysis")
    print("=" * 60)
    
    # Check current state
    updater = TreasuryYieldUpdater()
    recommendation = updater.get_update_recommendation()
    
    print("\n📊 Current Status:")
    print(f"   Latest Data: {recommendation['latest_data_date']}")
    print(f"   Last Update: {recommendation['last_update_time']}")
    print(f"   Status: {'⚠️ NEEDS UPDATE' if recommendation['needs_update'] else '✅ UP TO DATE'}")
    print(f"   Reason: {recommendation['reason']}")
    
    # Display strategies
    print("\n📋 Update Strategy Options:")
    strategies = create_update_strategies()
    
    for name, strategy in strategies.items():
        recommended = " 🌟 RECOMMENDED" if name == "HYBRID" else ""
        print(f"\n{name}{recommended}:")
        print(f"   {strategy['description']}")
        print("\n   Pros:")
        for pro in strategy['pros']:
            print(f"   ✅ {pro}")
        print("\n   Cons:")
        for con in strategy['cons']:
            print(f"   ❌ {con}")
    
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATION: Use HYBRID approach")
    print("=" * 60)
    print("""
Implementation Plan:
1. Create update_treasury_yields.py script
2. Add intelligent caching logic to API
3. Set up daily baseline update at 6am
4. Allow force updates via API parameter
5. Monitor update patterns and adjust cache duration
    """)


if __name__ == "__main__":
    display_recommendation()