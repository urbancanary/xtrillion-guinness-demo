#!/usr/bin/env python3
"""
Baseline Comparison Testing for XTrillion Bond Analytics API
Detects any changes in calculation results by comparing to known baselines
"""

import json
import requests
import datetime
import os
import sys
from typing import Dict, List, Tuple, Optional
import hashlib

# Fixed settlement date for consistent testing
BASELINE_SETTLEMENT_DATE = "2025-06-30"

# API Configuration
API_BASE_URL = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

# Test bonds with expected results
BASELINE_TEST_CASES = [
    {
        "name": "US Treasury 3% 2052",
        "request": {
            "description": "T 3 15/08/52",
            "price": 71.66,
            "settlement_date": BASELINE_SETTLEMENT_DATE
        }
    },
    {
        "name": "US Treasury 4.125% 2032",
        "request": {
            "description": "T 4.125 15/11/32",
            "price": 99.5,
            "settlement_date": BASELINE_SETTLEMENT_DATE
        }
    },
    {
        "name": "US Treasury 2.875% 2032",
        "request": {
            "description": "T 2.875 15/05/32",
            "price": 89.25,
            "settlement_date": BASELINE_SETTLEMENT_DATE
        }
    },
    {
        "name": "Panama 3.87% 2060",
        "request": {
            "description": "PANAMA 3.87 23/07/60",
            "price": 56.60,
            "settlement_date": BASELINE_SETTLEMENT_DATE
        }
    },
    {
        "name": "Pemex 6.5% 2027",
        "request": {
            "description": "PEMEX 6.5 13/06/27",
            "price": 95.75,
            "settlement_date": BASELINE_SETTLEMENT_DATE
        }
    }
]

class BaselineComparator:
    def __init__(self):
        self.baseline_file = "calculation_baseline.json"
        self.changes_detected = []
        self.new_results = {}
        
    def load_baseline(self) -> Dict:
        """Load existing baseline or return empty dict"""
        if os.path.exists(self.baseline_file):
            with open(self.baseline_file, 'r') as f:
                return json.load(f)
        return {}
        
    def save_baseline(self, baseline: Dict):
        """Save baseline results"""
        with open(self.baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)
            
    def calculate_bond(self, bond_request: Dict) -> Optional[Dict]:
        """Call API to calculate bond metrics"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/bond/analysis",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": API_KEY
                },
                json=bond_request,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Request Error: {e}")
            return None
            
    def extract_key_metrics(self, response: Dict) -> Dict:
        """Extract key metrics for comparison"""
        analytics = response.get('analytics', {})
        
        # Round to consistent precision for comparison
        return {
            'ytm': round(analytics.get('ytm', 0), 6),
            'duration': round(analytics.get('duration', 0), 6),
            'convexity': round(analytics.get('convexity', 0), 6),
            'pvbp': round(analytics.get('pvbp', 0), 6),
            'macaulay_duration': round(analytics.get('macaulay_duration', 0), 6),
            'clean_price': round(analytics.get('clean_price', 0), 6),
            'dirty_price': round(analytics.get('dirty_price', 0), 6),
            'accrued_interest': round(analytics.get('accrued_interest', 0), 6),
            'ytm_annual': round(analytics.get('ytm_annual', 0), 6),
            'duration_annual': round(analytics.get('duration_annual', 0), 6),
            'spread': analytics.get('spread'),  # May be null
            'z_spread': analytics.get('z_spread')  # May be null
        }
        
    def compare_metrics(self, baseline: Dict, current: Dict) -> List[Dict]:
        """Compare baseline and current metrics to 6 decimal places"""
        differences = []
        
        for key in baseline:
            baseline_val = baseline.get(key)
            current_val = current.get(key)
            
            # Handle None values
            if baseline_val is None and current_val is None:
                continue
                
            if baseline_val is None or current_val is None:
                differences.append({
                    'metric': key,
                    'baseline': baseline_val,
                    'current': current_val,
                    'difference': 'One value is None'
                })
                continue
                
            # Calculate difference
            if isinstance(baseline_val, (int, float)) and isinstance(current_val, (int, float)):
                # Compare to 6 decimal places
                baseline_rounded = round(baseline_val, 6)
                current_rounded = round(current_val, 6)
                
                if baseline_rounded != current_rounded:
                    diff = abs(current_val - baseline_val)
                    
                    # Format difference based on metric type
                    if key in ['ytm', 'ytm_annual', 'spread', 'z_spread']:
                        # For yields/spreads, show basis points
                        diff_str = f"{diff*100:.6f} bps"
                    elif key in ['duration', 'macaulay_duration', 'duration_annual']:
                        # For duration
                        diff_str = f"{diff:.6f} years"
                    else:
                        # For other metrics
                        diff_str = f"{diff:.6f}"
                    
                    differences.append({
                        'metric': key,
                        'baseline': f"{baseline_val:.6f}",
                        'current': f"{current_val:.6f}",
                        'difference': diff_str
                    })
                        
        return differences
        
    def run_comparison_tests(self, save_new_baseline: bool = False) -> Dict:
        """Run all tests and compare to baseline"""
        baseline = self.load_baseline()
        results = {
            'test_date': datetime.datetime.now().isoformat(),
            'settlement_date': BASELINE_SETTLEMENT_DATE,
            'bonds_tested': len(BASELINE_TEST_CASES),
            'changes_detected': 0,
            'details': []
        }
        
        print(f"🧪 Running Baseline Comparison Tests")
        print(f"   Settlement Date: {BASELINE_SETTLEMENT_DATE}")
        print(f"   Baseline Exists: {'Yes' if baseline else 'No'}")
        print("=" * 60)
        
        for test_case in BASELINE_TEST_CASES:
            bond_name = test_case['name']
            print(f"\n📊 Testing: {bond_name}")
            
            # Calculate current results
            response = self.calculate_bond(test_case['request'])
            
            if not response or response.get('status') != 'success':
                print(f"   ❌ API call failed")
                results['details'].append({
                    'bond': bond_name,
                    'status': 'API_FAILED',
                    'error': response.get('error') if response else 'No response'
                })
                continue
                
            # Extract metrics
            current_metrics = self.extract_key_metrics(response)
            bond_key = self.create_bond_key(test_case['request'])
            
            # Store for potential new baseline
            self.new_results[bond_key] = {
                'name': bond_name,
                'request': test_case['request'],
                'metrics': current_metrics,
                'response': response
            }
            
            # Compare if baseline exists
            if bond_key in baseline:
                baseline_metrics = baseline[bond_key]['metrics']
                differences = self.compare_metrics(baseline_metrics, current_metrics)
                
                if differences:
                    print(f"   ⚠️  CHANGES DETECTED:")
                    for diff in differences:
                        print(f"      - {diff['metric']}: {diff['baseline']} → {diff['current']} ({diff['difference']})")
                    
                    results['changes_detected'] += 1
                    results['details'].append({
                        'bond': bond_name,
                        'status': 'CHANGED',
                        'differences': differences
                    })
                else:
                    print(f"   ✅ No changes - all metrics match baseline")
                    results['details'].append({
                        'bond': bond_name,
                        'status': 'UNCHANGED'
                    })
            else:
                print(f"   🆕 New bond - no baseline for comparison")
                results['details'].append({
                    'bond': bond_name,
                    'status': 'NEW',
                    'metrics': current_metrics
                })
                
        # Summary
        print("\n" + "=" * 60)
        print(f"📋 SUMMARY:")
        print(f"   Total Bonds Tested: {results['bonds_tested']}")
        print(f"   Changes Detected: {results['changes_detected']}")
        
        if results['changes_detected'] > 0:
            print(f"\n⚠️  WARNING: {results['changes_detected']} bonds have changed calculations!")
            print("   This could indicate:")
            print("   - Code changes affecting calculations")
            print("   - Database updates")
            print("   - Convention changes")
            
        # Save results
        report_file = f"baseline_comparison_{datetime.date.today()}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Optionally save new baseline
        if save_new_baseline or not baseline:
            self.save_baseline(self.new_results)
            print(f"💾 New baseline saved to: {self.baseline_file}")
            
        return results
        
    def create_bond_key(self, request: Dict) -> str:
        """Create unique key for bond"""
        # Use description + price + settlement as key
        key_string = f"{request['description']}_{request['price']}_{request['settlement_date']}"
        return hashlib.md5(key_string.encode()).hexdigest()
        
    def show_baseline_details(self):
        """Display current baseline details"""
        baseline = self.load_baseline()
        
        if not baseline:
            print("No baseline exists yet. Run tests to create one.")
            return
            
        print(f"\n📊 Current Baseline Details")
        print(f"   Bonds in baseline: {len(baseline)}")
        print(f"   Settlement date: {BASELINE_SETTLEMENT_DATE}")
        print("\nBonds:")
        
        for key, data in baseline.items():
            print(f"\n{data['name']}:")
            metrics = data['metrics']
            print(f"   YTM: {metrics['ytm']:.4f}%")
            print(f"   Duration: {metrics['duration']:.4f} years")
            print(f"   Convexity: {metrics['convexity']:.4f}")
            print(f"   PVBP: {metrics['pvbp']:.4f}")
            print(f"   Accrued Interest: {metrics['accrued_interest']:.4f}%")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Baseline comparison testing for bond calculations')
    parser.add_argument('--save-baseline', action='store_true', 
                       help='Save current results as new baseline')
    parser.add_argument('--show-baseline', action='store_true',
                       help='Display current baseline values')
    parser.add_argument('--add-bond', type=str,
                       help='Add a new bond to test (format: "DESCRIPTION,PRICE")')
    
    args = parser.parse_args()
    
    comparator = BaselineComparator()
    
    if args.show_baseline:
        comparator.show_baseline_details()
    elif args.add_bond:
        # Parse and add new bond
        parts = args.add_bond.split(',')
        if len(parts) == 2:
            BASELINE_TEST_CASES.append({
                "name": parts[0],
                "request": {
                    "description": parts[0],
                    "price": float(parts[1]),
                    "settlement_date": BASELINE_SETTLEMENT_DATE
                }
            })
        comparator.run_comparison_tests(save_new_baseline=True)
    else:
        # Run comparison tests
        results = comparator.run_comparison_tests(save_new_baseline=args.save_baseline)
        
        # Exit with error code if changes detected
        sys.exit(1 if results['changes_detected'] > 0 else 0)

if __name__ == "__main__":
    main()