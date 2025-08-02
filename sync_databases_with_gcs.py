#!/usr/bin/env python3
"""
Bidirectional Database Sync with Google Cloud Storage
====================================================

Synchronizes local SQLite databases with GCS, handling:
- Treasury yield updates (daily changes)
- Bond data additions
- Conflict resolution
"""

import os
import sqlite3
import hashlib
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from google.cloud import storage
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseSync:
    """Handles bidirectional sync between local and GCS databases."""
    
    def __init__(self, bucket_name='json-receiver-databases', project_id='future-footing-414610'):
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.storage_client = storage.Client(project=project_id)
        self.bucket = self.storage_client.bucket(bucket_name)
        
        # Databases to sync
        self.databases = [
            'bonds_data.db',
            'validated_quantlib_bonds.db',
            'bloomberg_index.db'
        ]
        
        # Tables that get updated frequently
        self.update_tables = {
            'bonds_data.db': ['tsys_enhanced', 'treasury_securities'],
            'validated_quantlib_bonds.db': [],
            'bloomberg_index.db': []
        }
    
    def get_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def get_table_metadata(self, db_path: str, table_name: str) -> dict:
        """Get metadata about a table (row count, last update)."""
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Try to get last update time
            last_update = None
            try:
                # Check for updated_at column
                cursor.execute(f"SELECT MAX(updated_at) FROM {table_name}")
                last_update = cursor.fetchone()[0]
            except:
                try:
                    # Check for Date column (tsys_enhanced)
                    cursor.execute(f"SELECT MAX(Date) FROM {table_name}")
                    last_update = cursor.fetchone()[0]
                except:
                    pass
            
            return {
                'row_count': row_count,
                'last_update': last_update
            }
    
    def download_from_gcs(self, db_name: str, target_path: str):
        """Download database from GCS."""
        blob = self.bucket.blob(db_name)  # No subdirectory
        blob.download_to_filename(target_path)
        logger.info(f"Downloaded {db_name} from GCS")
    
    def upload_to_gcs(self, db_path: str, db_name: str):
        """Upload database to GCS with metadata."""
        blob = self.bucket.blob(db_name)  # No subdirectory
        
        # Calculate hash
        file_hash = self.get_file_hash(db_path)
        
        # Set metadata
        metadata = {
            'hash': file_hash,
            'updated_at': datetime.utcnow().isoformat(),
            'source': 'local_sync'
        }
        
        blob.metadata = metadata
        blob.upload_from_filename(db_path)
        logger.info(f"Uploaded {db_name} to GCS")
    
    def merge_treasury_updates(self, local_db: str, cloud_db: str) -> str:
        """Merge Treasury yield updates from cloud into local."""
        merged_db = local_db + '.merged'
        shutil.copy2(local_db, merged_db)
        
        try:
            # Attach cloud database
            with sqlite3.connect(merged_db) as conn:
                conn.execute(f"ATTACH DATABASE '{cloud_db}' AS cloud")
                
                # Merge tsys_enhanced table - take the most recent data
                conn.execute("""
                    INSERT OR REPLACE INTO tsys_enhanced
                    SELECT * FROM cloud.tsys_enhanced
                    WHERE Date NOT IN (SELECT Date FROM tsys_enhanced)
                    OR Date IN (
                        SELECT c.Date 
                        FROM cloud.tsys_enhanced c
                        JOIN tsys_enhanced l ON c.Date = l.Date
                        WHERE c.updated_at > l.updated_at
                        OR (c.updated_at IS NULL AND l.updated_at IS NULL)
                    )
                """)
                
                # Merge treasury_securities if it exists
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO treasury_securities
                        SELECT * FROM cloud.treasury_securities
                        WHERE cusip NOT IN (SELECT cusip FROM treasury_securities)
                        OR updated_at > (SELECT updated_at FROM treasury_securities WHERE cusip = cloud.treasury_securities.cusip)
                    """)
                except:
                    pass
                
                conn.commit()
                logger.info("Merged Treasury updates from cloud")
            
            return merged_db
            
        except Exception as e:
            logger.error(f"Merge failed: {e}")
            os.remove(merged_db)
            raise
    
    def vacuum_database(self, db_path: str):
        """Run VACUUM on database to ensure all changes are flushed."""
        try:
            with sqlite3.connect(db_path) as conn:
                # Checkpoint WAL file to ensure all changes are in main database
                conn.execute("PRAGMA wal_checkpoint(FULL)")
                # Vacuum to rebuild database and remove unused space
                conn.execute("VACUUM")
                logger.info(f"Vacuumed {db_path}")
        except Exception as e:
            logger.warning(f"Could not vacuum {db_path}: {e}")
    
    def sync_database(self, db_name: str):
        """Sync a single database with GCS."""
        local_path = Path(db_name)
        
        if not local_path.exists():
            # Local doesn't exist, download from cloud
            logger.info(f"Local {db_name} not found, downloading from GCS")
            self.download_from_gcs(db_name, str(local_path))
            return
        
        # Vacuum local database before syncing to ensure consistency
        logger.info(f"Preparing {db_name} for sync...")
        self.vacuum_database(str(local_path))
        
        # Download cloud version to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            cloud_path = tmp.name
        
        try:
            # Try to download from GCS
            self.download_from_gcs(db_name, cloud_path)
            
            # Compare hashes
            local_hash = self.get_file_hash(str(local_path))
            cloud_hash = self.get_file_hash(cloud_path)
            
            if local_hash == cloud_hash:
                logger.info(f"{db_name} is already in sync")
                return
            
            # Check if this database has updateable tables
            if db_name in self.update_tables and self.update_tables[db_name]:
                logger.info(f"{db_name} has differences, merging updates...")
                
                # Show what's different
                for table in self.update_tables[db_name]:
                    try:
                        local_meta = self.get_table_metadata(str(local_path), table)
                        cloud_meta = self.get_table_metadata(cloud_path, table)
                        
                        logger.info(f"  {table}:")
                        logger.info(f"    Local: {local_meta['row_count']} rows, last update: {local_meta['last_update']}")
                        logger.info(f"    Cloud: {cloud_meta['row_count']} rows, last update: {cloud_meta['last_update']}")
                    except Exception as e:
                        logger.warning(f"    Could not compare {table}: {e}")
                
                # Merge updates
                merged_path = self.merge_treasury_updates(str(local_path), cloud_path)
                
                # Replace local with merged
                shutil.move(merged_path, str(local_path))
                logger.info(f"Merged {db_name} successfully")
                
                # Upload merged version back to cloud
                self.upload_to_gcs(str(local_path), db_name)
            else:
                # No updateable tables, ask user what to do
                logger.warning(f"{db_name} has differences but no merge strategy")
                logger.info(f"  Local hash: {local_hash[:8]}...")
                logger.info(f"  Cloud hash: {cloud_hash[:8]}...")
                
                # For now, prefer local (assuming local has latest bond additions)
                logger.info(f"  Uploading local version to cloud")
                self.upload_to_gcs(str(local_path), db_name)
        
        finally:
            # Clean up temp file
            if os.path.exists(cloud_path):
                os.remove(cloud_path)
    
    def sync_all(self):
        """Sync all databases."""
        logger.info("Starting database sync with GCS")
        logger.info(f"Bucket: {self.bucket_name}")
        logger.info("=" * 60)
        
        for db_name in self.databases:
            logger.info(f"\nSyncing {db_name}...")
            try:
                self.sync_database(db_name)
            except Exception as e:
                logger.error(f"Failed to sync {db_name}: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("Sync complete!")


def main():
    """Main sync function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync databases with GCS')
    parser.add_argument('--bucket', default='xtrillion-db-prod', help='GCS bucket name')
    parser.add_argument('--project', default='future-footing-414610', help='GCP project ID')
    parser.add_argument('--database', help='Sync only specific database')
    
    args = parser.parse_args()
    
    syncer = DatabaseSync(bucket_name=args.bucket, project_id=args.project)
    
    if args.database:
        syncer.sync_database(args.database)
    else:
        syncer.sync_all()


if __name__ == "__main__":
    main()