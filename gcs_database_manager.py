#!/usr/bin/env python3
"""
GCS Database Manager for Google Analysis 10
=============================================
Fetches bond databases from Google Cloud Storage on app startup.
Eliminates need to deploy 166MB+ databases with every deployment.
"""

import os
import time
import logging
from typing import List, Optional
from google.cloud import storage
from google.api_core import exceptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GCSDatabaseManager:
    """
    Manages database downloads from Google Cloud Storage.
    Optimized for Google App Engine startup.
    """
    
    def __init__(self, 
                 bucket_name: str = "json-receiver-databases",
                 project_id: str = "future-footing-414610"):
        """
        Initialize the GCS Database Manager.
        
        Args:
            bucket_name: GCS bucket containing databases
            project_id: Google Cloud Project ID
        """
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.client = None
        self.bucket = None
        
        # Required databases for google_analysis10
        self.required_databases = [
            "bonds_data.db",
            "validated_quantlib_bonds.db"
        ]
    
    def _init_gcs_client(self) -> bool:
        """
        Initialize GCS client and bucket.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"🔧 Initializing GCS client for project: {self.project_id}")
            self.client = storage.Client(project=self.project_id)
            self.bucket = self.client.bucket(self.bucket_name)
            
            # Test bucket access
            exists = self.bucket.exists()
            if not exists:
                logger.error(f"❌ Bucket {self.bucket_name} does not exist")
                return False
                
            logger.info(f"✅ GCS client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize GCS client: {e}")
            return False
    
    def check_local_databases(self) -> dict:
        """
        Check which databases exist locally and their sizes.
        
        Returns:
            Dictionary with database status information
        """
        status = {}
        
        for db_name in self.required_databases:
            if os.path.exists(db_name):
                size_mb = os.path.getsize(db_name) / (1024 * 1024)
                status[db_name] = {
                    "exists": True,
                    "size_mb": round(size_mb, 2),
                    "path": os.path.abspath(db_name)
                }
                logger.info(f"✅ Local database found: {db_name} ({size_mb:.1f}MB)")
            else:
                status[db_name] = {
                    "exists": False,
                    "size_mb": 0,
                    "path": None
                }
                logger.warning(f"❌ Local database missing: {db_name}")
        
        return status
    
    def download_database(self, db_name: str, force_download: bool = False) -> bool:
        """
        Download a single database from GCS.
        
        Args:
            db_name: Name of the database file
            force_download: Force download even if file exists locally
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if file already exists and we're not forcing download
            if os.path.exists(db_name) and not force_download:
                size_mb = os.path.getsize(db_name) / (1024 * 1024)
                logger.info(f"⏭️  {db_name} already exists locally ({size_mb:.1f}MB), skipping download")
                return True
            
            # Initialize GCS client if needed
            if not self.client:
                if not self._init_gcs_client():
                    return False
            
            logger.info(f"📥 Downloading {db_name} from gs://{self.bucket_name}/")
            
            # Download the file
            blob = self.bucket.blob(db_name)
            
            # Check if blob exists in GCS
            if not blob.exists():
                logger.error(f"❌ {db_name} not found in GCS bucket")
                return False
            
            # Get blob size for progress tracking
            blob.reload()  # Refresh metadata
            blob_size_mb = blob.size / (1024 * 1024)
            
            start_time = time.time()
            blob.download_to_filename(db_name)
            download_time = time.time() - start_time
            
            # Verify download
            if os.path.exists(db_name):
                local_size_mb = os.path.getsize(db_name) / (1024 * 1024)
                speed_mbps = local_size_mb / download_time if download_time > 0 else 0
                
                logger.info(f"✅ Successfully downloaded {db_name}")
                logger.info(f"   📊 Size: {local_size_mb:.1f}MB")
                logger.info(f"   ⏱️  Time: {download_time:.1f}s ({speed_mbps:.1f} MB/s)")
                return True
            else:
                logger.error(f"❌ Download failed: {db_name} not found after download")
                return False
                
        except exceptions.NotFound:
            logger.error(f"❌ Database {db_name} not found in GCS bucket")
            return False
        except exceptions.Forbidden:
            logger.error(f"❌ Access denied to GCS bucket {self.bucket_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Error downloading {db_name}: {e}")
            return False
    
    def fetch_all_databases(self, force_download: bool = False) -> bool:
        """
        Download all required databases from GCS.
        
        Args:
            force_download: Force download even if files exist locally
            
        Returns:
            True if all databases downloaded successfully, False otherwise
        """
        logger.info("🚀 Starting database fetch from GCS...")
        start_time = time.time()
        
        # Check local database status
        local_status = self.check_local_databases()
        
        # Determine which databases need downloading
        databases_to_download = []
        for db_name in self.required_databases:
            if force_download or not local_status[db_name]["exists"]:
                databases_to_download.append(db_name)
        
        if not databases_to_download:
            logger.info("✅ All databases already exist locally")
            return True
        
        logger.info(f"📥 Need to download: {databases_to_download}")
        
        # Download each database
        success_count = 0
        for db_name in databases_to_download:
            if self.download_database(db_name, force_download):
                success_count += 1
            else:
                logger.error(f"❌ Failed to download {db_name}")
        
        total_time = time.time() - start_time
        
        # Summary
        if success_count == len(databases_to_download):
            logger.info(f"🎉 Successfully downloaded all {success_count} databases")
            logger.info(f"⏱️  Total download time: {total_time:.1f}s")
            
            # Final verification
            final_status = self.check_local_databases()
            missing = [db for db, status in final_status.items() if not status["exists"]]
            
            if missing:
                logger.error(f"❌ Some databases still missing: {missing}")
                return False
            else:
                logger.info("✅ All required databases are now available locally")
                return True
        else:
            logger.error(f"❌ Download failed: {success_count}/{len(databases_to_download)} successful")
            return False
    
    def get_database_info(self) -> dict:
        """
        Get comprehensive information about databases (local and GCS).
        
        Returns:
            Dictionary with detailed database information
        """
        info = {
            "local_databases": self.check_local_databases(),
            "gcs_bucket": self.bucket_name,
            "project_id": self.project_id,
            "required_databases": self.required_databases
        }
        
        # Add GCS information if client is available
        if self.client:
            try:
                info["gcs_accessible"] = True
                info["bucket_exists"] = self.bucket.exists() if self.bucket else False
            except:
                info["gcs_accessible"] = False
                info["bucket_exists"] = False
        else:
            info["gcs_accessible"] = False
            info["bucket_exists"] = False
        
        return info


def ensure_databases_available(force_download: bool = False) -> bool:
    """
    Convenience function to ensure all databases are available.
    Call this during app startup.
    
    Args:
        force_download: Force download even if files exist locally
        
    Returns:
        True if all databases are available, False otherwise
    """
    logger.info("🔍 Ensuring bond databases are available...")
    
    db_manager = GCSDatabaseManager()
    success = db_manager.fetch_all_databases(force_download=force_download)
    
    if success:
        logger.info("✅ Database availability check passed")
    else:
        logger.error("❌ Database availability check failed")
    
    return success


if __name__ == "__main__":
    # Command-line interface for testing
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        print("🔄 Force downloading all databases...")
        ensure_databases_available(force_download=True)
    else:
        print("📥 Ensuring databases are available...")
        ensure_databases_available(force_download=False)
