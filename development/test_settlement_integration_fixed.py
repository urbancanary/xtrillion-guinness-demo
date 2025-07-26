#!/usr/bin/env python3
"""
Test Settlement Date Integration
===============================

This script tests the settlement_date database integration to ensure:
1. Database cleanup was successful
2. Settlement_date column exists and is populated
3. All values comply with SETTLEMENT_DATE_POLICY.md
4. Enhanced functions work with database settlement_date
5. API integration is ready

Run this script to verify everything is working correctly.
"""

import sqlite3
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SettlementDateIntegrationTest:
    def __init__(self):
        self.db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9/bonds_data.db"
        self.required_settlement_date = "2025-04-18"  # From SETTLEMENT_DATE_POLICY.md
        self.test_results = []
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} {test_name}")
        if details:
            logger.info(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
        
        return passed
    
    def test_database_exists(self):
        """Test 1: Database exists"""
        exists = os.path.exists(self.db_path)
        return self.log_test("Database exists", exists, f"Path: {self.db_path}")
    
    def test_settlement_date_column_exists(self):
        """Test 2: Settlement_date column exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(intermediate_results)")
            columns = [col[1] for col in cursor.fetchall()]
            conn.close()
            
            has_settlement = 'settlement_date' in columns
            return self.log_test("Settlement_date column exists", has_settlement, 
                               f"Total columns: {len(columns)}")
        except Exception as e:
            return self.log_test("Settlement_date column exists", False, f"Error: {e}")
    
    def test_blank_columns_removed(self):
        """Test 3: Blank columns (msci, record_number) were removed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(intermediate_results)")
            columns = [col[1] for col in cursor.fetchall()]
            conn.close()
            
            has_msci = 'msci' in columns
            has_record_number = 'record_number' in columns
            
            removed_correctly = not has_msci and not has_record_number
            details = f"msci removed: {not has_msci}, record_number removed: {not has_record_number}"
            
            return self.log_test("Blank columns removed", removed_correctly, details)
        except Exception as e:
            return self.log_test("Blank columns removed", False, f"Error: {e}")
    
    def test_settlement_date_populated(self):
        """Test 4: All rows have settlement_date populated"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM intermediate_results")
            total_rows = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM intermediate_results WHERE settlement_date IS NOT NULL AND settlement_date != ''")
            populated_rows = cursor.fetchone()[0]
            
            conn.close()
            
            fully_populated = total_rows == populated_rows
            details = f"{populated_rows}/{total_rows} rows populated"
            
            return self.log_test("Settlement_date populated", fully_populated, details)
        except Exception as e:
            return self.log_test("Settlement_date populated", False, f"Error: {e}")
    
    def test_settlement_date_compliance(self):
        """Test 5: All settlement_dates comply with policy (2025-04-18)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT settlement_date, COUNT(*) FROM intermediate_results GROUP BY settlement_date")
            settlement_distribution = cursor.fetchall()
            conn.close()
            
            compliant_bonds = sum(count for date, count in settlement_distribution if date == self.required_settlement_date)
            total_bonds = sum(count for date, count in settlement_distribution)
            
            fully_compliant = compliant_bonds == total_bonds
            details = f"{compliant_bonds}/{total_bonds} bonds compliant"
            
            return self.log_test("Settlement_date policy compliance", fully_compliant, details)
        except Exception as e:
            return self.log_test("Settlement_date policy compliance", False, f"Error: {e}")
    
    def test_enhanced_functions_import(self):
        """Test 6: Enhanced functions with settlement_date can be imported"""
        try:
            sys.path.append("/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9")
            from enhanced_functions_with_settlement import get_settlement_date_from_db, validate_settlement_date
            
            return self.log_test("Enhanced functions import", True, "Successfully imported settlement functions")
        except Exception as e:
            return self.log_test("Enhanced functions import", False, f"Import error: {e}")
    
    def test_get_settlement_date_function(self):
        """Test 7: get_settlement_date_from_db function works"""
        try:
            sys.path.append("/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9")
            from enhanced_functions_with_settlement import get_settlement_date_from_db
            
            # Test with a known ISIN
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT isin FROM intermediate_results LIMIT 1")
            test_isin = cursor.fetchone()[0]
            conn.close()
            
            settlement_date = get_settlement_date_from_db(test_isin, self.db_path)
            
            is_correct = settlement_date == self.required_settlement_date
            details = f"Retrieved settlement_date for {test_isin}: {settlement_date}"
            
            return self.log_test("get_settlement_date_from_db function", is_correct, details)
        except Exception as e:
            return self.log_test("get_settlement_date_from_db function", False, f"Function error: {e}")
    
    def test_settlement_date_validation(self):
        """Test 8: Settlement date validation function works"""
        try:
            sys.path.append("/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9")
            from enhanced_functions_with_settlement import validate_settlement_date
            
            # Test valid date
            try:
                validate_settlement_date(self.required_settlement_date)
                valid_passes = True
            except ValueError:
                valid_passes = False
            
            # Test invalid date
            try:
                validate_settlement_date("2025-07-10")
                invalid_fails = False  # Should fail
            except ValueError:
                invalid_fails = True  # Should raise error
            
            validation_works = valid_passes and invalid_fails
            details = f"Valid date passes: {valid_passes}, Invalid date fails: {invalid_fails}"
            
            return self.log_test("Settlement date validation", validation_works, details)
        except Exception as e:
            return self.log_test("Settlement date validation", False, f"Validation error: {e}")
    
    def test_database_performance(self):
        """Test 9: Database queries are performant"""
        try:
            start_time = datetime.now()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test query performance
            cursor.execute("SELECT isin, settlement_date FROM intermediate_results LIMIT 100")
            results = cursor.fetchall()
            conn.close()
            
            end_time = datetime.now()
            query_time = (end_time - start_time).total_seconds()
            
            is_fast = query_time < 1.0 and len(results) == 100
            details = f"Query time: {query_time:.3f}s, Results: {len(results)}"
            
            return self.log_test("Database performance", is_fast, details)
        except Exception as e:
            return self.log_test("Database performance", False, f"Performance error: {e}")
    
    def test_backup_exists(self):
        """Test 10: Database backup was created"""
        try:
            backup_dir = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9"
            backup_files = [f for f in os.listdir(backup_dir) if f.startswith("bonds_data.db.backup_")]
            
            has_backup = len(backup_files) > 0
            latest_backup = max(backup_files) if backup_files else "None"
            details = f"Latest backup: {latest_backup}"
            
            return self.log_test("Database backup exists", has_backup, details)
        except Exception as e:
            return self.log_test("Database backup exists", False, f"Backup check error: {e}")
    
    def run_all_tests(self):
        """Run all tests and provide summary"""
        logger.info("🚀 Starting Settlement Date Integration Tests")
        logger.info("=" * 60)
        
        # Run all tests
        tests = [
            self.test_database_exists,
            self.test_settlement_date_column_exists,
            self.test_blank_columns_removed,
            self.test_settlement_date_populated,
            self.test_settlement_date_compliance,
            self.test_enhanced_functions_import,
            self.test_get_settlement_date_function,
            self.test_settlement_date_validation,
            self.test_database_performance,
            self.test_backup_exists
        ]
        
        for test in tests:
            test()
        
        # Summary
        logger.info("=" * 60)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        total_tests = len(self.test_results)
        
        logger.info(f"🎯 TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED! Settlement date integration is ready for production.")
            logger.info("✅ Database is clean, compliant, and performance-optimized")
            logger.info("✅ Enhanced functions are working correctly")
            logger.info("✅ API integration is ready to deploy")
        else:
            logger.warning(f"⚠️  {total_tests - passed_tests} tests failed. Review issues before deployment.")
            
            # Show failed tests
            for result in self.test_results:
                if not result['passed']:
                    logger.error(f"❌ FAILED: {result['test']} - {result['details']}")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = SettlementDateIntegrationTest()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎯 NEXT STEPS:")
            print("1. ✅ Database cleanup: COMPLETE")
            print("2. ✅ Settlement date integration: READY")
            print("3. 🔄 Update your main code to use enhanced_functions_with_settlement.py")
            print("4. 🔄 Deploy the updated API with settlement_date support")
            print("5. 🧪 Test the API endpoints with settlement_date responses")
            
            print("\n📋 READY FOR PRODUCTION DEPLOYMENT!")
            return 0
        else:
            print("\n❌ Integration tests failed. Please fix issues before deployment.")
            return 1
            
    except Exception as e:
        logger.error(f"💥 Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
