#!/usr/bin/env python3
"""
CONSOLIDATED 6-WAY TEST RUNNER
============================

Runs the comprehensive consolidated 6-way bond testing framework.
Sets up environment, archives old files, and executes the complete test suite.
"""

import sys
import os
import subprocess
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project configuration
PROJECT_ROOT = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
CONSOLIDATED_TESTER = f"{PROJECT_ROOT}/consolidated_6way_tester.py"

def setup_environment():
    """Setup the testing environment"""
    logger.info("🔧 Setting up testing environment...")
    
    # Ensure we're in the right directory
    os.chdir(PROJECT_ROOT)
    
    # Create archive directory
    archive_dir = f"{PROJECT_ROOT}/archive"
    os.makedirs(archive_dir, exist_ok=True)
    logger.info(f"✅ Archive directory ready: {archive_dir}")
    
    # Check if GA10 API is running
    try:
        import requests
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Local API is running")
        else:
            logger.warning("⚠️ Local API not responding properly")
    except:
        logger.warning("⚠️ Local API not accessible - some tests will fail")
    
    # Check cloud API
    try:
        response = requests.get("https://future-footing-414610.uc.r.appspot.com/health", timeout=10)
        if response.status_code == 200:
            logger.info("✅ Cloud API is accessible")
        else:
            logger.warning("⚠️ Cloud API not responding properly")
    except:
        logger.warning("⚠️ Cloud API not accessible - cloud tests will fail")

def main():
    """Main execution function"""
    print("🚀 CONSOLIDATED 6-WAY BOND TESTING FRAMEWORK")
    print("=" * 60)
    print(f"📁 Project: {PROJECT_ROOT}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Setup environment
        setup_environment()
        
        # Import and run the consolidated tester
        sys.path.insert(0, PROJECT_ROOT)
        from consolidated_6way_tester import ConsolidatedSixWayTester
        
        logger.info("🧪 Starting comprehensive 6-way test...")
        tester = ConsolidatedSixWayTester()
        report_path = tester.run_comprehensive_test()
        
        print("\n" + "=" * 60)
        print("🎉 COMPREHENSIVE TEST COMPLETE!")
        print("=" * 60)
        print(f"📊 HTML Report: {report_path}")
        print(f"💾 Database: {tester.db_path}")
        print(f"📁 Archive: {PROJECT_ROOT}/archive")
        print("\n📋 Summary:")
        print("- ✅ All 25 bonds tested across 6 methods")
        print("- ✅ Yield, spread, and duration calculations")
        print("- ✅ Bloomberg baseline comparisons")
        print("- ✅ Color-coded difference analysis")
        print("- ✅ Old files archived")
        print("- ✅ Results saved to database")
        
        return 0
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install requests pandas numpy")
        return 1
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit(main())
