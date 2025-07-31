# XTrillion GA10 - Database Persistence Manager
# Downloads databases ONCE per instance startup (not per user request)

import os
import logging
import time
from google.cloud import storage

logger = logging.getLogger(__name__)

class PersistentDatabaseManager:
    """
    Manages database persistence with intelligent caching
    - Downloads databases ONCE per App Engine instance startup
    - Serves all user requests from local cached databases
    - Zero download overhead for user requests
    """
    
    def __init__(self):
        self.bucket_name = os.environ.get('DATABASE_BUCKET', 'xtrillion-ga10-databases')
        self.local_cache_dir = '/tmp'
        
        self.databases = {
            'primary': {
                'local_path': os.environ.get('DATABASE_PATH', '/tmp/bonds_data.db'),
                'gcs_path': 'bonds_data.db',
                'description': 'Primary bond database'
            },
            'validated': {
                'local_path': os.environ.get('VALIDATED_DB_PATH', '/tmp/validated_quantlib_bonds.db'),
                'gcs_path': 'validated_quantlib_bonds.db', 
                'description': 'Validated bond conventions'
            },
            'bloomberg': {
                'local_path': os.environ.get('BLOOMBERG_DB_PATH', '/tmp/bloomberg_index.db'),
                'gcs_path': 'bloomberg_index.db',
                'description': 'Bloomberg reference data'
            }
        }
    
    def ensure_databases_available(self):
        """
        Ensures databases are available locally
        Downloads ONCE per instance startup, not per user request
        """
        logger.info("🔍 Checking database availability...")
        
        # Check if all databases already cached locally
        all_cached = True
        for db_name, db_config in self.databases.items():
            if not os.path.exists(db_config['local_path']):
                all_cached = False
                break
            else:
                size_mb = os.path.getsize(db_config['local_path']) / (1024*1024)
                logger.info(f"✅ {db_config['description']}: {size_mb:.1f}MB (cached)")
        
        if all_cached:
            logger.info("✅ All databases already cached locally - ready for user requests")
            return True
        
        # Download missing databases (ONCE per instance)
        logger.info("⏳ Downloading databases for this instance (one-time setup)...")
        start_time = time.time()
        
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            
            for db_name, db_config in self.databases.items():
                if not os.path.exists(db_config['local_path']):
                    logger.info(f"📥 Downloading {db_config['description']}...")
                    
                    blob = bucket.blob(db_config['gcs_path'])
                    blob.download_to_filename(db_config['local_path'])
                    
                    size_mb = os.path.getsize(db_config['local_path']) / (1024*1024)
                    logger.info(f"✅ {db_config['description']}: {size_mb:.1f}MB downloaded")
            
            download_time = time.time() - start_time
            logger.info(f"✅ Instance database setup complete in {download_time:.1f}s")
            logger.info("🚀 All user requests will now use cached databases (0s overhead)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database download failed: {e}")
            return False
    
    def get_database_status(self):
        """Get status of all databases for health checks"""
        status = {}
        total_size_mb = 0
        
        for db_name, db_config in self.databases.items():
            if os.path.exists(db_config['local_path']):
                size_mb = os.path.getsize(db_config['local_path']) / (1024*1024)
                total_size_mb += size_mb
                status[db_name] = {
                    'status': 'available',
                    'size_mb': round(size_mb, 1),
                    'path': db_config['local_path']
                }
            else:
                status[db_name] = {
                    'status': 'missing',
                    'size_mb': 0,
                    'path': db_config['local_path']
                }
        
        status['total_size_mb'] = round(total_size_mb, 1)
        return status

# Global instance for API usage
database_manager = PersistentDatabaseManager()

def ensure_databases_available():
    """API compatibility function"""
    return database_manager.ensure_databases_available()

def get_database_status():
    """API compatibility function"""
    return database_manager.get_database_status()