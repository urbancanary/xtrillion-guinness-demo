#!/usr/bin/env python3
"""
Validation Script for Refactored Universal Bond Parser System
============================================================

Quick validation that all the refactored components work together properly.
Run this BEFORE the comprehensive 6-way test to ensure everything is working.
"""

import sys
import os
import logging

# Add paths
sys.path.append('./core')
sys.path.append('.')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_universal_parser():
    """Test the Universal Bond Parser directly"""
    print("🚀 Testing Universal Bond Parser")
    print("=" * 40)
    
    try:
        from universal_bond_parser import UniversalBondParser, BondSpecification
        
        parser = UniversalBondParser('bonds_data.db', 'validated_quantlib_bonds.db')
        print("✅ Universal Parser initialized successfully")
        
        # Test cases that should work
        test_cases = [
            ("US912810TJ79", "US Treasury ISIN"),
            ("PANAMA, 3.87%, 23-Jul-2060", "PANAMA description (the problematic one!)"),
            ("US TREASURY N/B, 3%, 15-Aug-2052", "Treasury description"),
            ("GALAXY PIPELINE, 3.25%, 30-Sep-2040", "Institutional format")
        ]
        
        success_count = 0
        for i, (bond_input, description) in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: {bond_input}")
            print(f"   Description: {description}")
            
            spec = parser.parse_bond(bond_input, clean_price=75.0)
            
            print(f"   Success: {spec.parsing_success}")
            print(f"   Parser: {spec.parser_used}")
            print(f"   Input Type: {spec.input_type.value}")
            
            if spec.parsing_success:
                success_count += 1
                print(f"   ✅ Issuer: {spec.issuer}")
                print(f"   ✅ Coupon: {spec.coupon_rate}%")
                
                # Special check for PANAMA
                if "PANAMA" in bond_input:
                    coupon = spec.coupon_rate
                    if coupon and 3.5 <= coupon <= 4.5:
                        print(f"   🎉 PANAMA FIXED! Coupon {coupon}% looks correct!")
                    else:
                        print(f"   ⚠️  PANAMA coupon {coupon}% - check if correct")
            else:
                print(f"   ❌ Error: {spec.error_message}")
        
        print(f"\n📊 Universal Parser Results: {success_count}/{len(test_cases)} successful")
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ Universal Parser test failed: {e}")
        return False

def test_refactored_api():
    """Test the refactored API (if running)"""
    print("\n🌐 Testing Refactored API")
    print("=" * 40)
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:8080/api/health", timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ API is running")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Universal Parser Available: {health_data.get('universal_parser_available')}")
            print(f"   Parser Test Passed: {health_data.get('parser_test_passed')}")
            
            # Test parser endpoint
            test_payload = {
                "bond_input": "PANAMA, 3.87%, 23-Jul-2060"
            }
            
            response = requests.post("http://localhost:8080/api/parser/test", json=test_payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Parser test endpoint working")
                print(f"   Parsing Success: {data.get('parsing_successful')}")
                print(f"   Parser Used: {data.get('parser_used')}")
                
                if "PANAMA" in test_payload["bond_input"]:
                    spec = data.get('bond_specification', {})
                    coupon = spec.get('coupon_rate')
                    if coupon and 3.5 <= coupon <= 4.5:
                        print(f"   🎉 API PANAMA FIXED! Coupon {coupon}%")
                
                return True
            else:
                print(f"❌ Parser test failed: {response.status_code}")
                return False
        else:
            print(f"❌ API not responding: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  API test failed (API may not be running): {e}")
        return False

def validate_file_structure():
    """Validate that all required files exist"""
    print("\n📁 Validating File Structure")
    print("=" * 40)
    
    required_files = [
        './core/universal_bond_parser.py',
        './bond_description_parser.py',
        './google_analysis10.py',
        './google_analysis10_api_refactored.py',
        './comprehensive_6way_tester_refactored.py',
        './test_universal_parser.py',
        './bonds_data.db'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (MISSING)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {len(missing_files)}")
        return False
    else:
        print(f"\n✅ All required files present")
        return True

def main():
    """Main validation function"""
    print("🔧 REFACTORED SYSTEM VALIDATION")
    print("=" * 50)
    print("Validating Universal Bond Parser system before comprehensive testing")
    print()
    
    results = {}
    
    # Test 1: File structure
    results['files'] = validate_file_structure()
    
    # Test 2: Universal Parser
    results['parser'] = test_universal_parser()
    
    # Test 3: API (optional - may not be running)
    results['api'] = test_refactored_api()
    
    # Summary
    print("\n🎯 VALIDATION SUMMARY")
    print("=" * 30)
    
    if results['files']:
        print("✅ File Structure: All files present")
    else:
        print("❌ File Structure: Missing files")
    
    if results['parser']:
        print("✅ Universal Parser: Working correctly")
    else:
        print("❌ Universal Parser: Has issues")
    
    if results['api']:
        print("✅ Refactored API: Working correctly")
    else:
        print("⚠️  Refactored API: Not available or has issues")
    
    # Overall status
    core_working = results['files'] and results['parser']
    
    if core_working:
        print("\n🎉 CORE SYSTEM READY!")
        print("✅ Universal Bond Parser is working")
        print("✅ Should fix Methods 4 & 6 in comprehensive test")
        print("✅ PANAMA bond parsing should now work consistently")
        print()
        print("Next steps:")
        print("1. Start refactored API: python3 google_analysis10_api_refactored.py")
        print("2. Run comprehensive test: python3 comprehensive_6way_tester_refactored.py")
        print("3. Expect 6/6 methods at 100% success rate!")
    else:
        print("\n❌ CORE SYSTEM HAS ISSUES")
        print("Fix the above issues before running comprehensive test")
    
    return core_working

if __name__ == "__main__":
    # Change to correct directory
    os.chdir('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')
    
    success = main()
    
    if success:
        print("\n🚀 Ready for comprehensive testing!")
    else:
        print("\n🔧 Fix issues before proceeding")
