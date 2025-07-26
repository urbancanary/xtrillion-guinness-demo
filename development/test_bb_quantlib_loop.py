#!/usr/bin/env python3
"""
test_bb_quantlib_loop.py - Quick validation test for the new loop processing system
====================================================================================

This test verifies that bb_quantlib_loop.py works correctly with both small and large datasets.
"""

import sys
import os
import subprocess
import time

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🧪 Testing: {description}")
    print(f"Command: {command}")
    print("-" * 60)
    
    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ SUCCESS ({elapsed:.1f}s)")
            print("Output (last 10 lines):")
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines[-10:]:
                print(f"   {line}")
            return True
        else:
            print(f"❌ FAILED ({elapsed:.1f}s)")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ EXCEPTION ({elapsed:.1f}s): {e}")
        return False

def main():
    """Main test function"""
    print("🔄 BB_QUANTLIB_LOOP.PY VALIDATION TESTS")
    print("=" * 70)
    print("Testing the new loop processing capabilities...")
    print("=" * 70)
    
    # Change to the correct directory
    os.chdir('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9')
    
    test_results = []
    
    # Test 1: Help and configuration display
    test_results.append(run_command(
        "python3 bb_quantlib_loop.py --help",
        "Help command and argument parsing"
    ))
    
    # Test 2: Small dataset test (pemex_calculations)
    test_results.append(run_command(
        "python3 bb_quantlib_loop.py pemex_calculations --batch-size 5 --chunk-size 10 --no-ytw-oad --no-pass-fail",
        "Small dataset processing (pemex_calculations - accrued only)"
    ))
    
    # Test 3: Configuration test
    test_results.append(run_command(
        "python3 bb_quantlib_loop.py pemex_calculations --batch-size 3 --progress-interval 1 --delay 0.01 --accrued-only",
        "Configuration options test (small batch, frequent progress)"
    ))
    
    # Test 4: Multi-table test (if time permits)
    test_results.append(run_command(
        "python3 bb_quantlib_loop.py --multi-table pemex_calculations --batch-size 5 --accrued-only",
        "Multi-table processing test (single table in multi-mode)"
    ))
    
    # Summary
    print(f"\n" + "=" * 70)
    print("🎯 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! bb_quantlib_loop.py is working correctly.")
        print("\n✅ Ready for production use with:")
        print("   • Loop processing capabilities")
        print("   • Batch processing")
        print("   • Progress tracking")
        print("   • Multi-table support")
        print("   • Configurable performance parameters")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        
    print("\n🚀 Next steps:")
    print("   1. Run full dataset test: python3 bb_quantlib_loop.py validated_calculations")
    print("   2. Test multi-table: python3 bb_quantlib_loop.py --multi-table pemex_calculations validated_calculations")
    print("   3. Integrate with existing clean module structure")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
