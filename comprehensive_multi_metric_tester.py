#!/usr/bin/env python3
"""
Comprehensive Multi-Metric Bond Tester - Google Analysis 10
===========================================================

Tests all 25 bonds for ALL available metrics from calculate_bond_master:
- Yield to Maturity 
- Modified Duration
- Treasury Spread
- Accrued Interest
- Convexity (if available)
- Additional metrics from conventions

Generates comprehensive HTML report with Bloomberg baselines where available.
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project path
PROJECT_ROOT = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10'
sys.path.insert(0, PROJECT_ROOT)

from bond_master_hierarchy import calculate_bond_master
from comprehensive_html_generator import ComprehensiveHTMLReportGenerator

# 25-Bond Test Portfolio with Bloomberg Baselines (where available)
BONDS_25_WITH_BLOOMBERG = [
    # Bond data with Bloomberg baselines where available
    {"isin": "US912810TJ79", "price": 71.66, "description": "US TREASURY N/B, 3%, 15-Aug-2052",
     "bloomberg_yield": 4.898, "bloomberg_duration": 16.36, "bloomberg_spread": None},
    
    {"isin": "XS2249741674", "price": 77.88, "description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040",
     "bloomberg_yield": 5.638, "bloomberg_duration": None, "bloomberg_spread": 118},
    
    {"isin": "XS1709535097", "price": 89.40, "description": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047",
     "bloomberg_yield": 5.717, "bloomberg_duration": None, "bloomberg_spread": 123},
    
    {"isin": "XS1982113463", "price": 87.14, "description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039",
     "bloomberg_yield": 5.600, "bloomberg_duration": None, "bloomberg_spread": 111},
    
    {"isin": "USP37466AS18", "price": 80.39, "description": "EMPRESA METRO, 4.7%, 07-May-2050",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 144},
    
    {"isin": "USP3143NAH72", "price": 101.63, "description": "CODELCO INC, 6.15%, 24-Oct-2036",
     "bloomberg_yield": 5.949, "bloomberg_duration": None, "bloomberg_spread": 160},
    
    {"isin": "USP30179BR86", "price": 86.42, "description": "COMISION FEDERAL, 6.264%, 15-Feb-2052",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 261},
    
    {"isin": "US195325DX04", "price": 52.71, "description": "COLOMBIA REP OF, 3.875%, 15-Feb-2061",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 301},
    
    {"isin": "US279158AJ82", "price": 69.31, "description": "ECOPETROL SA, 5.875%, 28-May-2045",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 445},
    
    {"isin": "USP37110AM89", "price": 76.24, "description": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 171},
    
    {"isin": "XS2542166231", "price": 103.03, "description": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 146},
    
    {"isin": "XS2167193015", "price": 64.50, "description": "STATE OF ISRAEL, 3.8%, 13-May-2060",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 151},
    
    {"isin": "XS1508675508", "price": 82.42, "description": "SAUDI INT BOND, 4.5%, 26-Oct-2046",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 114},
    
    {"isin": "XS1807299331", "price": 92.21, "description": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 223},
    
    {"isin": "US91086QAZ19", "price": 78.00, "description": "UNITED MEXICAN, 5.75%, 12-Oct-2110",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 255},
    
    {"isin": "USP6629MAD40", "price": 82.57, "description": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 224},
    
    {"isin": "US698299BL70", "price": 56.60, "description": "PANAMA, 3.87%, 23-Jul-2060",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 253},
    
    {"isin": "US71654QDF63", "price": 71.42, "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 505},
    
    {"isin": "US71654QDE98", "price": 89.55, "description": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 444},
    
    {"isin": "XS2585988145", "price": 85.54, "description": "GACI FIRST INVST, 5.125%, 14-Feb-2053",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 140},
    
    {"isin": "XS1959337749", "price": 89.97, "description": "QATAR STATE OF, 4.817%, 14-Mar-2049",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 76},
    
    {"isin": "XS2233188353", "price": 99.23, "description": "QNB FINANCE LTD, 1.625%, 22-Sep-2025",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 71},
    
    {"isin": "XS2359548935", "price": 73.79, "description": "QATAR ENERGY, 3.125%, 12-Jul-2041",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 101},
    
    {"isin": "XS0911024635", "price": 93.29, "description": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 95},
    
    {"isin": "USP0R80BAG79", "price": 97.26, "description": "SITIOS, 5.375%, 04-Apr-2032",
     "bloomberg_yield": None, "bloomberg_duration": None, "bloomberg_spread": 187}
]


class ComprehensiveMultiMetricTester:
    """Comprehensive multi-metric bond testing for HTML report generation"""
    
    def __init__(self, settlement_date: str = "2025-06-30"):
        self.settlement_date = settlement_date
        self.test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_data = {
            'yield_results': [],
            'duration_results': [],
            'spread_results': [],
            'accrued_results': [],
            'additional_metrics': [],
            'test_metadata': {
                'settlement_date': settlement_date,
                'timestamp': self.test_timestamp,
                'total_bonds': len(BONDS_25_WITH_BLOOMBERG)
            }
        }
    
    def test_single_bond(self, bond_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single bond with comprehensive metric extraction"""
        
        try:
            print(f"🧪 Testing: {bond_data['isin']} - {bond_data['description'][:50]}...")
            
            # Test with ISIN (Route 1)
            result = calculate_bond_master(
                isin=bond_data['isin'],
                description=bond_data['description'],
                price=bond_data['price'],
                settlement_date=self.settlement_date
            )
            
            if result.get('success'):
                bond_result = {
                    'isin': bond_data['isin'],
                    'description': bond_data['description'],
                    'price': bond_data['price'],
                    'calculated_yield': result.get('yield'),
                    'calculated_duration': result.get('duration'),
                    'calculated_spread': result.get('spread'),
                    'calculated_accrued': result.get('accrued_interest'),
                    'bloomberg_yield': bond_data.get('bloomberg_yield'),
                    'bloomberg_duration': bond_data.get('bloomberg_duration'),
                    'bloomberg_spread': bond_data.get('bloomberg_spread'),
                    'conventions': result.get('conventions', {}),
                    'route_used': result.get('route_used'),
                    'calculation_method': result.get('calculation_method'),
                    'success': True,
                    'error': None
                }
                
                # Calculate Bloomberg differences where available
                if bond_result['bloomberg_yield'] and bond_result['calculated_yield']:
                    bond_result['yield_diff_bps'] = abs(bond_result['calculated_yield'] - bond_result['bloomberg_yield']) * 100
                
                if bond_result['bloomberg_duration'] and bond_result['calculated_duration']:
                    bond_result['duration_diff_years'] = abs(bond_result['calculated_duration'] - bond_result['bloomberg_duration'])
                
                if bond_result['bloomberg_spread'] and bond_result['calculated_spread']:
                    bond_result['spread_diff_bps'] = abs(bond_result['calculated_spread'] - bond_result['bloomberg_spread'])
                
                print(f"   ✅ Success: Yield={bond_result['calculated_yield']:.3f}%, Duration={bond_result['calculated_duration']:.2f}y")
                return bond_result
                
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                return {
                    'isin': bond_data['isin'],
                    'description': bond_data['description'],
                    'price': bond_data['price'],
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'bloomberg_yield': bond_data.get('bloomberg_yield'),
                    'bloomberg_duration': bond_data.get('bloomberg_duration'),
                    'bloomberg_spread': bond_data.get('bloomberg_spread')
                }
                
        except Exception as e:
            print(f"   🚨 Exception: {str(e)}")
            return {
                'isin': bond_data['isin'],
                'description': bond_data['description'],
                'price': bond_data['price'],
                'success': False,
                'error': f"Exception: {str(e)}",
                'bloomberg_yield': bond_data.get('bloomberg_yield'),
                'bloomberg_duration': bond_data.get('bloomberg_duration'),
                'bloomberg_spread': bond_data.get('bloomberg_spread')
            }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test on all 25 bonds for all metrics"""
        
        print("🚀 COMPREHENSIVE MULTI-METRIC BOND TESTING")
        print("=" * 80)
        print(f"📊 Testing {len(BONDS_25_WITH_BLOOMBERG)} bonds for ALL metrics")
        print(f"📅 Settlement Date: {self.settlement_date}")
        print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        successful_tests = 0
        
        for i, bond_data in enumerate(BONDS_25_WITH_BLOOMBERG, 1):
            print(f"\n[{i:2d}/25] ", end="")
            
            result = self.test_single_bond(bond_data)
            
            if result['success']:
                successful_tests += 1
                
                # Store results by metric for HTML generation
                self.results_data['yield_results'].append({
                    'bond_num': i,
                    'isin': result['isin'],
                    'description': result['description'],
                    'calculated': result.get('calculated_yield'),
                    'bloomberg': result.get('bloomberg_yield'),
                    'difference_bps': result.get('yield_diff_bps'),
                    'accuracy_rating': self._get_yield_accuracy_rating(result.get('yield_diff_bps'))
                })
                
                self.results_data['duration_results'].append({
                    'bond_num': i,
                    'isin': result['isin'],
                    'description': result['description'],
                    'calculated': result.get('calculated_duration'),
                    'bloomberg': result.get('bloomberg_duration'),
                    'difference_years': result.get('duration_diff_years'),
                    'accuracy_rating': self._get_duration_accuracy_rating(result.get('duration_diff_years'))
                })
                
                self.results_data['spread_results'].append({
                    'bond_num': i,
                    'isin': result['isin'],
                    'description': result['description'],
                    'calculated': result.get('calculated_spread'),
                    'bloomberg': result.get('bloomberg_spread'),
                    'difference_bps': result.get('spread_diff_bps'),
                    'accuracy_rating': self._get_spread_accuracy_rating(result.get('spread_diff_bps'))
                })
                
                self.results_data['accrued_results'].append({
                    'bond_num': i,
                    'isin': result['isin'],
                    'description': result['description'],
                    'calculated': result.get('calculated_accrued'),
                    'bloomberg': None,  # Usually not compared for accrued interest
                    'price': result.get('price')
                })
                
                # Extract additional metrics from conventions if available
                conventions = result.get('conventions', {})
                additional_metrics = {
                    'bond_num': i,
                    'isin': result['isin'],
                    'description': result['description'],
                    'payment_frequency': conventions.get('payment_frequency'),
                    'day_count': conventions.get('day_count'),
                    'calendar': conventions.get('calendar'),
                    'business_day_convention': conventions.get('business_day_convention'),
                    'is_treasury': conventions.get('is_treasury', False)
                }
                self.results_data['additional_metrics'].append(additional_metrics)
                
            else:
                # Store failed results with empty calculated values
                for metric_list in ['yield_results', 'duration_results', 'spread_results', 'accrued_results']:
                    self.results_data[metric_list].append({
                        'bond_num': i,
                        'isin': result['isin'],
                        'description': result['description'],
                        'calculated': None,
                        'bloomberg': result.get(f"bloomberg_{metric_list.split('_')[0]}"),
                        'error': result.get('error'),
                        'success': False
                    })
        
        # Update metadata
        self.results_data['test_metadata'].update({
            'successful_tests': successful_tests,
            'success_rate': (successful_tests / len(BONDS_25_WITH_BLOOMBERG)) * 100,
            'completed_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        print(f"\n" + "=" * 80)
        print(f"📈 COMPREHENSIVE TEST COMPLETE")
        print(f"✅ Successful Tests: {successful_tests}/{len(BONDS_25_WITH_BLOOMBERG)} ({successful_tests/len(BONDS_25_WITH_BLOOMBERG)*100:.1f}%)")
        print(f"🕒 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return self.results_data
    
    def _get_yield_accuracy_rating(self, diff_bps: Optional[float]) -> str:
        """Get accuracy rating for yield comparison"""
        if diff_bps is None:
            return "N/A"
        elif diff_bps < 1:
            return "🎯 EXCELLENT"
        elif diff_bps < 5:
            return "✅ GOOD"
        elif diff_bps < 15:
            return "⚠️ FAIR"
        else:
            return "❌ POOR"
    
    def _get_duration_accuracy_rating(self, diff_years: Optional[float]) -> str:
        """Get accuracy rating for duration comparison"""
        if diff_years is None:
            return "N/A"
        elif diff_years < 0.01:
            return "🎯 EXCELLENT"
        elif diff_years < 0.05:
            return "✅ GOOD"
        elif diff_years < 0.2:
            return "⚠️ FAIR"
        else:
            return "❌ POOR"
    
    def _get_spread_accuracy_rating(self, diff_bps: Optional[float]) -> str:
        """Get accuracy rating for spread comparison"""
        if diff_bps is None:
            return "N/A"
        elif diff_bps < 2:
            return "🎯 EXCELLENT"
        elif diff_bps < 10:
            return "✅ GOOD"
        elif diff_bps < 25:
            return "⚠️ FAIR"
        else:
            return "❌ POOR"
    
    def save_results_json(self, filename: Optional[str] = None) -> str:
        """Save comprehensive results to JSON file"""
        if filename is None:
            filename = f"comprehensive_multi_metric_results_{self.test_timestamp}.json"
        
        filepath = os.path.join(PROJECT_ROOT, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.results_data, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {filepath}")
        return filepath


def main():
    """Main function to run comprehensive multi-metric testing with automatic HTML generation"""
    
    # Change to project directory
    os.chdir(PROJECT_ROOT)
    
    # Create tester instance
    tester = ComprehensiveMultiMetricTester(settlement_date="2025-06-30")
    
    # Run comprehensive test
    results = tester.run_comprehensive_test()
    
    # Save JSON results
    json_filepath = tester.save_results_json()
    
    print(f"\n📊 JSON Results saved: {json_filepath}")
    
    # Automatically generate HTML report
    print("\n🎨 Generating comprehensive HTML report...")
    try:
        html_generator = ComprehensiveHTMLReportGenerator(results)
        html_filepath = html_generator.generate_html_report()
        
        print(f"✅ HTML Report generated: {html_filepath}")
        print(f"🌐 Open in browser: open {html_filepath}")
        
        # Try to automatically open in browser (macOS)
        try:
            os.system(f"open {html_filepath}")
            print("🚀 HTML report opened in your default browser!")
        except:
            print("💡 Manually open the HTML file in your browser to view the report")
            
    except Exception as e:
        print(f"❌ Error generating HTML report: {e}")
        print(f"💡 You can manually generate it with:")
        print(f"   from comprehensive_html_generator import generate_html_from_json")
        print(f"   generate_html_from_json('{json_filepath}')")
    
    return results


if __name__ == "__main__":
    results = main()
