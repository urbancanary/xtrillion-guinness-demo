#!/usr/bin/env python3
"""
Cloud Treasury Updater for App Engine
=====================================

Updates Treasury yields directly in GCS databases.
Designed to be called by App Engine cron jobs.
"""

import tempfile
import os
from datetime import datetime, timedelta
from google.cloud import storage
import logging
from us_treasury_yield_fetcher import USTreasuryYieldFetcher
from sync_databases_with_gcs import DatabaseSync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudTreasuryUpdater:
    """Updates Treasury yields in cloud databases."""
    
    def __init__(self, bucket_name='json-receiver-databases', project_id='future-footing-414610'):
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.storage_client = storage.Client(project=project_id)
        self.bucket = self.storage_client.bucket(bucket_name)
        self.fetcher = USTreasuryYieldFetcher()
    
    def update_treasury_yields(self) -> dict:
        """Update Treasury yields in GCS database."""
        result = {
            'status': 'error',
            'message': '',
            'yields_updated': 0
        }
        
        # Create temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                # Download bonds_data.db from GCS
                local_db_path = os.path.join(tmpdir, 'bonds_data.db')
                blob = self.bucket.blob('bonds_data.db')  # No subdirectory
                blob.download_to_filename(local_db_path)
                logger.info("Downloaded bonds_data.db from GCS")
                
                # Get target date
                today = datetime.now()
                if today.hour < 16:  # Before 4 PM ET
                    today -= timedelta(days=1)
                
                # Skip weekends
                while today.weekday() >= 5:
                    today -= timedelta(days=1)
                
                # Fetch latest yields
                yields = self.fetcher.fetch_yield_curve_data(today)
                
                if yields:
                    # Update the database
                    success = self.fetcher.update_database(yields, today)
                    
                    if success:
                        # Upload updated database back to GCS
                        metadata = {
                            'updated_at': datetime.utcnow().isoformat(),
                            'source': 'treasury_yield_update',
                            'update_date': today.strftime('%Y-%m-%d'),
                            'yields_count': str(len(yields))
                        }
                        
                        # Vacuum database to ensure all changes are flushed
                        try:
                            import sqlite3
                            with sqlite3.connect(local_db_path) as conn:
                                conn.execute("PRAGMA wal_checkpoint(FULL)")
                                conn.execute("VACUUM")
                            logger.info("Vacuumed database before upload")
                        except Exception as e:
                            logger.warning(f"Could not vacuum: {e}")
                        
                        blob.metadata = metadata
                        blob.upload_from_filename(local_db_path)
                        logger.info("Uploaded updated database to GCS")
                        
                        result = {
                            'status': 'success',
                            'message': f'Updated {len(yields)} yields for {today.strftime("%Y-%m-%d")}',
                            'yields_updated': len(yields),
                            'date': today.strftime('%Y-%m-%d'),
                            'yields': yields
                        }
                    else:
                        result['message'] = 'Failed to update database'
                else:
                    result['message'] = 'No yield data retrieved from Treasury'
                    
            except Exception as e:
                logger.error(f"Treasury update failed: {e}")
                result['message'] = str(e)
        
        return result


def update_yields_for_app_engine():
    """Function to be called from App Engine endpoint."""
    updater = CloudTreasuryUpdater()
    return updater.update_treasury_yields()


if __name__ == "__main__":
    # For local testing
    result = update_yields_for_app_engine()
    print(f"\nUpdate result: {result['status']}")
    print(f"Message: {result['message']}")
    if result['status'] == 'success':
        print(f"Yields updated: {result['yields_updated']}")
        for tenor, rate in sorted(result['yields'].items()):
            print(f"  {tenor}: {rate:.2f}%")