#!/usr/bin/env python3
"""
App Engine Entry Point for Google Analysis 10 Bond Analytics API
===============================================================

This is the entry point for Google App Engine deployment.
It downloads databases from GCS and imports the Flask app.
"""

import os
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_databases_from_gcs():
    """Download database files from Google Cloud Storage"""
    gcs_bucket = "json-receiver-databases"
    databases = [
        "bonds_data.db",
        "bloomberg_index.db", 
        "validated_quantlib_bonds.db"
    ]
    
    logger.info("🔽 Downloading databases from GCS...")
    
    for db_file in databases:
        try:
            # Check if file already exists
            if os.path.exists(db_file):
                file_size = os.path.getsize(db_file) / (1024 * 1024)  # Size in MB
                logger.info(f"✅ {db_file} already exists locally ({file_size:.1f} MB)")
                continue
                
            # Download from GCS
            gcs_path = f"gs://{gcs_bucket}/{db_file}"
            cmd = ["gsutil", "cp", gcs_path, "./"]
            
            logger.info(f"📡 Downloading {db_file}...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                file_size = os.path.getsize(db_file) / (1024 * 1024)  # Size in MB
                logger.info(f"✅ Downloaded {db_file} successfully ({file_size:.1f} MB)")
            else:
                logger.warning(f"⚠️ Failed to download {db_file}: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"⚠️ Error downloading {db_file}: {str(e)}")
    
    # List available databases with full paths
    db_files = list(Path(".").glob("*.db"))
    if db_files:
        logger.info(f"📊 Available databases:")
        for db_file in db_files:
            file_size = db_file.stat().st_size / (1024 * 1024)  # Size in MB
            full_path = db_file.absolute()
            logger.info(f"   📁 {db_file.name} ({file_size:.1f} MB) at {full_path}")
    else:
        logger.warning("⚠️ No database files found after download attempt")
    
    # Test database connectivity
    try:
        import sqlite3
        for db_file in ["bonds_data.db", "bloomberg_index.db", "validated_quantlib_bonds.db"]:
            if os.path.exists(db_file):
                try:
                    conn = sqlite3.connect(db_file, timeout=5)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    conn.close()
                    logger.info(f"✅ {db_file} connection test passed ({len(tables)} tables)")
                except Exception as e:
                    logger.error(f"❌ {db_file} connection test failed: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Database connectivity test failed: {str(e)}")

# Download databases before importing the app
if os.getenv('GAE_ENV', '').startswith('standard'):
    # Running on App Engine, download databases
    logger.info("🌐 Running on App Engine - downloading databases from GCS")
    download_databases_from_gcs()
else:
    logger.info("💻 Running locally - using local databases")

# Import the Flask app
from google_analysis10_api import app

# Add a debug endpoint to the app
@app.route('/debug/files', methods=['GET'])
def debug_files():
    """Debug endpoint to show available files and database status"""
    import sqlite3
    
    current_dir = os.getcwd()
    files_info = []
    
    # List all .db files
    for file_path in Path(".").glob("*"):
        if file_path.is_file():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            files_info.append({
                "name": file_path.name,
                "size_mb": round(size_mb, 2),
                "full_path": str(file_path.absolute()),
                "exists": True
            })
    
    # Test database connections
    db_status = {}
    for db_name in ["bonds_data.db", "bloomberg_index.db", "validated_quantlib_bonds.db"]:
        db_status[db_name] = {"exists": False, "tables": [], "error": None}
        
        if os.path.exists(db_name):
            db_status[db_name]["exists"] = True
            try:
                conn = sqlite3.connect(db_name, timeout=5)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                db_status[db_name]["tables"] = tables
                conn.close()
            except Exception as e:
                db_status[db_name]["error"] = str(e)
    
    return {
        "current_directory": current_dir,
        "files": files_info,
        "database_status": db_status,
        "environment": os.getenv('GAE_ENV', 'local'),
        "total_db_files": len([f for f in files_info if f["name"].endswith(".db")])
    }

# App Engine will automatically use this 'app' variable
if __name__ == '__main__':
    # This runs when testing locally
    app.run(host='127.0.0.1', port=8080, debug=True)
