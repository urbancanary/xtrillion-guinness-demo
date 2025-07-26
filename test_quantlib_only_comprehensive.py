"""
🧪 COMPREHENSIVE QUANTLIB-ONLY TESTING
Tests the professional QuantLib implementation against the QNB bond failure and full portfolio.

CRITICAL: This test validates that we've eliminated all homemade bond math.
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Add project root to path
project_root = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10'
sys.path.append(project_root)

try:
    from professional_quantlib_calculator import ProfessionalQuantLibCalculator
    import QuantLib as ql
    print("✅ QuantLib and professional calculator imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Installing QuantLib...")
    os.system("pip install quantlib-python")
    import QuantLib as ql
    from professional_quantlib_calculator import ProfessionalQuantLibCalculator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuantLibOnlyTester:
    """
    🧪 COMPREHENSIVE TESTER FOR QUANTLIB-ONLY IMPLEMENTATION
    
    Validates that:
    1. QNB bond (84-day) works without division by zero
    2. All portfolio bonds work with professional methods
    3. No homemade math is used anywhere
    """
    
    def __init__(self):
        self.calculator = ProfessionalQuantLibCalculator()
        self.results = []
        
        # Portfolio bonds for comprehensive testing
        self.portfolio_bonds = [
            {
                'isin': 'US912810TJ79',
                'description': 'T 3 15/08/52',
                'coupon': 3.0,
                'maturity': '2052-08-15',
                'price': 71.66,
                'expected_convention': 'ActualActual_ISDA'
            },
            {
                'isin': 'XS2233188353', 
                'description': 'QNB FINANCE LTD, 1.625%, 22-Sep-2025',
                'coupon': 1.625,
                'maturity': '2025-09-22',
                'price': 99.23,
                'expected_ytm': 5.02,  # Bloomberg expected
                'edge_case': True,  # 84-day bond that broke homemade math
                'test_priority': 'CRITICAL'
            },
            {
                'isin': 'XS2249741674',
                'description': 'GALAXY PIPELINE, 3.25%, 30-Sep-2040',
                'coupon': 3.25,
                'maturity': '2040-09-30',
                'price': 77.88
            },
            {
                'isin': 'XS1982113463',
                'description': 'SAUDI ARAB OIL, 4.25%, 16-Apr-2039',
                'coupon': 4.25,
                'maturity': '2039-04-16',
                'price': 87.14
            },
            {
                'isin': 'USP37466AS18',
                'description': 'EMPRESA METRO, 4.7%, 07-May-2050',
                'coupon': 4.7,
                'maturity': '2050-05-07',
                'price': 80.39
            }
        ]
    
    def test_qnb_bond_specifically(self):
        """
        🚨 CRITICAL TEST: QNB Bond that failed with homemade Newton-Raphson
        
        This MUST work with professional QuantLib methods.
        """
        print("=" * 60)
        print("🚨 CRITICAL TEST: QNB BOND FIX VALIDATION")
        print("=" * 60)
        
        qnb_bond = next(bond for bond in self.portfolio_bonds if bond['isin'] == 'XS2233188353')
        
        print(f"ISIN: {qnb_bond['isin']}")
        print(f"Description: {qnb_bond['description']}")
        print(f"Maturity: {qnb_bond['maturity']} (84-day edge case)")
        print(f"Price: {qnb_bond['price']}")
        print(f"Expected YTM: {qnb_bond['expected_ytm']}%")
        print()
        
        try:
            # Test with professional QuantLib calculator
            results = self.calculator.calculate_professional_bond_metrics(
                issue_date='2022-09-22',  # Estimated issue date
                maturity_date=qnb_bond['maturity'],
                coupon_rate=qnb_bond['coupon'],
                clean_price=qnb_bond['price'],
                settlement_date='2025-06-30',
                frequency='Semiannual',
                day_count='Thirty360_BondBasis'
            )
            
            print("🏦 PROFESSIONAL QUANTLIB RESULTS:")
            print(f"YTM: {results.get('ytm', 'FAILED'):.4f}%" if results.get('ytm') else "YTM: FAILED")
            print(f"Duration: {results.get('duration', 'FAILED'):.4f} years" if results.get('duration') else "Duration: FAILED")
            print(f"Accrued: {results.get('accrued_interest', 'FAILED'):.6f}" if results.get('accrued_interest') else "Accrued: FAILED")
            print(f"Method: {results.get('calculation_method', 'UNKNOWN')}")
            print(f"Homemade math used: {results.get('homemade_math_used', 'UNKNOWN')}")
            print()
            
            # Validate results
            if results.get('ytm') is not None:
                ytm_diff = abs(results['ytm'] - qnb_bond['expected_ytm'])
                if ytm_diff < 0.5:  # Within 50bp
                    print("✅ QNB BOND FIX SUCCESSFUL!")
                    print(f"✅ YTM within 50bp of Bloomberg: {ytm_diff:.2f}bp difference")
                    print("✅ No division by zero errors")
                    print("✅ Professional QuantLib methods working")
                else:
                    print(f"⚠️ QNB BOND CALCULATED BUT INACCURATE: {ytm_diff:.2f}bp difference")
            else:
                print("❌ QNB BOND STILL FAILING - Professional methods not working")
                
            return results
            
        except Exception as e:
            print(f"❌ QNB BOND TEST FAILED: {e}")
            return None
    
    def test_edge_cases(self):
        """
        🧪 TEST EDGE CASES THAT BREAK HOMEMADE MATH
        """
        print("=" * 60)
        print("🧪 EDGE CASE TESTING")
        print("=" * 60)
        
        edge_cases = [
            {
                'name': 'Very Short Term (30 days)',
                'issue_date': '2025-01-01',
                'maturity_date': '2025-07-30',  # ~30 days
                'coupon': 2.0,
                'price': 99.5
            },
            {
                'name': 'Long Term (50 years)',
                'issue_date': '2000-01-01',
                'maturity_date': '2050-01-01',
                'coupon': 4.0,
                'price': 85.0
            },
            {
                'name': 'Deep Discount',
                'issue_date': '2020-01-01',
                'maturity_date': '2030-01-01',
                'coupon': 1.0,
                'price': 60.0
            },
            {
                'name': 'High Premium',
                'issue_date': '2020-01-01',
                'maturity_date': '2030-01-01',
                'coupon': 8.0,
                'price': 120.0
            }
        ]
        
        for i, case in enumerate(edge_cases, 1):
            print(f"Test {i}: {case['name']}")
            try:
                results = self.calculator.calculate_professional_bond_metrics(
                    issue_date=case['issue_date'],
                    maturity_date=case['maturity_date'],
                    coupon_rate=case['coupon'],
                    clean_price=case['price'],
                    settlement_date='2025-06-30'
                )
                
                if results.get('ytm') is not None:
                    print(f"  ✅ YTM: {results['ytm']:.4f}%")
                    print(f"  ✅ Duration: {results.get('duration', 'N/A'):.4f} years" if results.get('duration') else "  ❌ Duration: FAILED")
                else:
                    print(f"  ❌ FAILED")
                    
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
            print()
    
    def test_full_portfolio(self):
        """
        📊 TEST FULL PORTFOLIO WITH PROFESSIONAL QUANTLIB
        """
        print("=" * 60)
        print("📊 FULL PORTFOLIO PROFESSIONAL TESTING")
        print("=" * 60)
        
        success_count = 0
        total_count = len(self.portfolio_bonds)
        
        for i, bond in enumerate(self.portfolio_bonds, 1):
            print(f"Bond {i}/{total_count}: {bond['isin']}")
            print(f"  Description: {bond['description']}")
            
            try:
                # Estimate issue date (maturity minus 10-30 years)
                maturity_year = int(bond['maturity'][:4])
                issue_year = max(2000, maturity_year - 20)  # Conservative estimate
                issue_date = f"{issue_year}-01-01"
                
                results = self.calculator.calculate_professional_bond_metrics(
                    issue_date=issue_date,
                    maturity_date=bond['maturity'],
                    coupon_rate=bond['coupon'],
                    clean_price=bond['price'],
                    settlement_date='2025-06-30',
                    day_count=bond.get('expected_convention', 'Thirty360_BondBasis')
                )
                
                if results.get('ytm') is not None:
                    print(f"  ✅ YTM: {results['ytm']:.4f}%")
                    print(f"  ✅ Duration: {results.get('duration', 'N/A'):.4f} years" if results.get('duration') else "  ⚠️ Duration: N/A")
                    success_count += 1
                    
                    # Special validation for QNB
                    if bond['isin'] == 'XS2233188353':
                        ytm_diff = abs(results['ytm'] - bond['expected_ytm'])
                        print(f"  🎯 Bloomberg difference: {ytm_diff:.2f}bp")
                else:
                    print(f"  ❌ FAILED")
                    
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
            
            print()
        
        success_rate = (success_count / total_count) * 100
        print(f"📊 PORTFOLIO SUCCESS RATE: {success_count}/{total_count} ({success_rate:.1f}%)")
        
        if success_rate >= 95:
            print("✅ PROFESSIONAL QUANTLIB PORTFOLIO TESTING SUCCESSFUL")
        else:
            print("⚠️ PROFESSIONAL QUANTLIB NEEDS IMPROVEMENT")
        
        return success_rate
    
    def test_no_homemade_math_validation(self):
        """
        🔒 VALIDATE NO HOMEMADE MATH IS BEING USED
        """
        print("=" * 60)
        print("🔒 NO HOMEMADE MATH VALIDATION")
        print("=" * 60)
        
        # Test a bond and check the results contain our professional markers
        test_results = self.calculator.calculate_professional_bond_metrics(
            issue_date='2020-01-01',
            maturity_date='2030-01-01',
            coupon_rate=4.0,
            clean_price=95.0,
            settlement_date='2025-06-30'
        )
        
        # Check professional markers
        homemade_math_used = test_results.get('homemade_math_used', True)
        calculation_method = test_results.get('calculation_method', 'UNKNOWN')
        professional_grade = test_results.get('professional_grade', False)
        
        print(f"Homemade math used: {homemade_math_used}")
        print(f"Calculation method: {calculation_method}")
        print(f"Professional grade: {professional_grade}")
        
        if not homemade_math_used and 'PROFESSIONAL_QUANTLIB' in calculation_method:
            print("✅ NO HOMEMADE MATH VALIDATION PASSED")
            print("✅ Only professional QuantLib methods being used")
        else:
            print("❌ HOMEMADE MATH STILL BEING USED - CRITICAL FAILURE")
        
        return not homemade_math_used
    
    def run_comprehensive_test(self):
        """
        🏆 RUN ALL TESTS - COMPREHENSIVE VALIDATION
        """
        print("🔒 QUANTLIB-ONLY COMPREHENSIVE TESTING")
        print("🚨 COMMITMENT: NO HOMEMADE BOND MATH ALLOWED")
        print("🎯 GOAL: Fix QNB bond and eliminate division by zero")
        print()
        
        # Test 1: QNB Bond Fix (CRITICAL)
        qnb_results = self.test_qnb_bond_specifically()
        qnb_success = qnb_results is not None and qnb_results.get('ytm') is not None
        
        # Test 2: Edge Cases
        print()
        self.test_edge_cases()
        
        # Test 3: Full Portfolio
        print()
        portfolio_success_rate = self.test_full_portfolio()
        
        # Test 4: No Homemade Math Validation
        print()
        no_homemade_math = self.test_no_homemade_math_validation()
        
        # Final Results
        print("=" * 60)
        print("🏆 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        print(f"QNB Bond Fix (Critical): {'✅ PASSED' if qnb_success else '❌ FAILED'}")
        print(f"Portfolio Success Rate: {portfolio_success_rate:.1f}%")
        print(f"No Homemade Math: {'✅ VERIFIED' if no_homemade_math else '❌ FAILED'}")
        print()
        
        if qnb_success and portfolio_success_rate >= 95 and no_homemade_math:
            print("🎉 QUANTLIB-ONLY IMPLEMENTATION SUCCESSFUL!")
            print("✅ QNB bond fixed - no more division by zero")
            print("✅ Portfolio processing working professionally")
            print("✅ No homemade math anywhere in calculations")
            print("🏦 Professional-grade bond calculations achieved")
        else:
            print("⚠️ QUANTLIB-ONLY IMPLEMENTATION NEEDS WORK")
            if not qnb_success:
                print("❌ QNB bond still failing - critical issue")
            if portfolio_success_rate < 95:
                print("❌ Portfolio success rate too low")
            if not no_homemade_math:
                print("❌ Homemade math still being used")

def main():
    """Run the comprehensive QuantLib-only test suite"""
    tester = QuantLibOnlyTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
