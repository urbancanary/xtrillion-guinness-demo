#!/usr/bin/env python3
"""
Demonstrates how calculation changes are detected
This simulates what would happen if the API returns different values
"""

import json
import shutil
import os

def simulate_calculation_change():
    """Simulate a calculation change by modifying the baseline"""
    
    print("🔬 Demonstrating Calculation Change Detection")
    print("=" * 60)
    
    # First, backup the current baseline
    if os.path.exists("calculation_baseline.json"):
        shutil.copy("calculation_baseline.json", "calculation_baseline_backup.json")
        print("✅ Backed up current baseline")
    
    # Load the baseline
    with open("calculation_baseline.json", "r") as f:
        baseline = json.load(f)
    
    # Simulate a calculation change - modify YTM for one bond
    for key in baseline:
        if "US Treasury 3% 2052" in baseline[key]["name"]:
            print(f"\n📝 Simulating change for: {baseline[key]['name']}")
            old_ytm = baseline[key]["metrics"]["ytm"]
            new_ytm = old_ytm + 0.01  # Add 1 basis point
            baseline[key]["metrics"]["ytm"] = new_ytm
            print(f"   YTM changed: {old_ytm:.6f} → {new_ytm:.6f} (+1 bp)")
            
            # Also change duration slightly
            old_duration = baseline[key]["metrics"]["duration"]
            new_duration = old_duration - 0.02
            baseline[key]["metrics"]["duration"] = new_duration
            print(f"   Duration changed: {old_duration:.6f} → {new_duration:.6f}")
            break
    
    # Save the modified baseline
    with open("calculation_baseline_modified.json", "w") as f:
        json.dump(baseline, f, indent=2)
    
    print("\n📊 Now run the baseline comparison test to see the changes:")
    print("   python3 baseline_comparison_test.py")
    print("\nOr run the full test suite:")
    print("   python3 daily_test_suite.py")
    print("\n💡 The test will detect these changes and report them!")
    
    # Show what the detection would look like
    print("\n" + "=" * 60)
    print("Expected Detection Output:")
    print("-" * 60)
    print("📊 Testing: US Treasury 3% 2052")
    print("   ⚠️  CHANGES DETECTED:")
    print("      - ytm: 4.890596 → 4.900596 (1.000 bps)")
    print("      - duration: 16.547889 → 16.527889 (0.0200 years)")
    print("\n⚠️  WARNING: 1 bonds have changed calculations!")
    print("   This could indicate:")
    print("   - Code changes affecting calculations")
    print("   - Database updates")
    print("   - Convention changes")
    
    print("\n✅ To restore original baseline:")
    print("   cp calculation_baseline_backup.json calculation_baseline.json")

if __name__ == "__main__":
    simulate_calculation_change()