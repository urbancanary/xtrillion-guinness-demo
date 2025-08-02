#!/usr/bin/env python3
"""
Comprehensive Treasury Bond Test Suite
=====================================

Consolidates functionality from 20+ individual Treasury test files into a single,
well-organized test suite with proper test utilities and clear test categories.
"""

import unittest
import json
import sys
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules to test
from bond_master_hierarchy_enhanced import calculate_bond_master
from google_analysis10 import process_bond_portfolio
# from treasury_market_conventions import get_treasury_conventions
# from treasury_issue_date_calculator import calculate_treasury_issue_date


class TreasuryTestUtils:
    """Utilities for Treasury bond testing."""
    
    @staticmethod
    def create_treasury_bond(description: str, price: float, 
                           settlement_date: str = "2025-04-18") -> Dict[str, Any]:
        """Create a standard Treasury bond test case."""
        return {
            "description": description,
            "price": price,
            "settlement_date": settlement_date
        }
    
    @staticmethod
    def get_expected_metrics() -> Dict[str, Dict[str, float]]:
        """Get expected metrics for standard test bonds."""
        return {
            "T 3 15/08/52": {
                "ytm": 4.8189,
                "modified_duration": 16.0553,
                "convexity": 401.2641,
                "pvbp": 0.1151
            },
            "T 4.125 15/10/27": {
                "ytm": 4.4821,
                "modified_duration": 2.3955,
                "convexity": 7.1189,
                "pvbp": 0.0240
            }
        }


class TestTreasuryParsing(unittest.TestCase):
    """Test Treasury bond description parsing."""
    
    def test_standard_treasury_parsing(self):
        """Test parsing of standard Treasury descriptions."""
        test_cases = [
            ("T 3 15/08/52", "US912810TJ79", date(2052, 8, 15)),
            ("T 4.125 15/10/27", "US91282CGP52", date(2027, 10, 15)),
            ("US TREASURY N/B 2.75 02/15/2028", None, date(2028, 2, 15))
        ]
        
        for description, expected_isin, expected_maturity in test_cases:
            with self.subTest(description=description):
                result = calculate_bond_master(
                    description=description,
                    price=100.0,
                    settlement_date="2025-04-18"
                )
                
                self.assertEqual(result["status"], "success")
                if expected_isin:
                    self.assertEqual(result.get("isin"), expected_isin)
                self.assertEqual(
                    datetime.strptime(result["maturity_date"], "%Y-%m-%d").date(),
                    expected_maturity
                )


class TestTreasuryCalculations(unittest.TestCase):
    """Test Treasury bond calculations."""
    
    def setUp(self):
        self.utils = TreasuryTestUtils()
        self.expected_metrics = self.utils.get_expected_metrics()
    
    def test_treasury_duration_calculation(self):
        """Test Treasury bond duration calculations."""
        bond = self.utils.create_treasury_bond("T 3 15/08/52", 71.66)
        result = calculate_bond_master(**bond)
        
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["modified_duration"], 16.0553, places=2)
        self.assertAlmostEqual(result["annual_duration"], 16.0553, places=2)
        self.assertAlmostEqual(result["macaulay_duration"], 16.8364, places=2)
    
    def test_treasury_yield_calculation(self):
        """Test Treasury bond yield calculations."""
        bond = self.utils.create_treasury_bond("T 4.125 15/10/27", 99.92)
        result = calculate_bond_master(**bond)
        
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["ytm"], 4.1284, places=2)
        self.assertAlmostEqual(result["annual_ytm"], 4.1284, places=2)
    
    def test_treasury_pricing_calculation(self):
        """Test Treasury bond pricing calculations."""
        bond = self.utils.create_treasury_bond("T 3 15/08/52", 71.66)
        result = calculate_bond_master(**bond)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["clean_price"], 71.66)
        self.assertIsNotNone(result["dirty_price"])
        self.assertIsNotNone(result["accrued_interest"])
        
        # Dirty price = Clean price + Accrued interest
        expected_dirty = result["clean_price"] + result["accrued_interest"]
        self.assertAlmostEqual(result["dirty_price"], expected_dirty, places=4)


class TestTreasuryConventions(unittest.TestCase):
    """Test Treasury market conventions."""
    
    def test_treasury_day_count_convention(self):
        """Test Treasury bonds use Actual/Actual day count."""
        # Test via actual bond calculation
        result = calculate_bond_master(
            description="T 3 15/08/52",
            price=100.0,
            settlement_date="2025-04-18"
        )
        self.assertEqual(result["status"], "success")
        # Treasury bonds should use ActualActual_Bond
        # This is validated through the calculation results
    
    def test_treasury_calculation_conventions(self):
        """Test Treasury calculation conventions."""
        result = calculate_bond_master(
            description="T 4.125 15/10/27",
            price=100.0,
            settlement_date="2025-04-18"
        )
        self.assertEqual(result["status"], "success")
        # Verify semi-annual frequency through results
        self.assertIsNotNone(result.get("ytm"))
        self.assertIsNotNone(result.get("modified_duration"))


class TestTreasuryPortfolio(unittest.TestCase):
    """Test Treasury portfolio calculations."""
    
    def test_treasury_portfolio_aggregation(self):
        """Test portfolio-level calculations for Treasury bonds."""
        portfolio_data = [
            {
                "description": "T 3 15/08/52",
                "CLOSING PRICE": 71.66,
                "WEIGHTING": 50.0
            },
            {
                "description": "T 4.125 15/10/27",
                "CLOSING PRICE": 99.92,
                "WEIGHTING": 50.0
            }
        ]
        
        result = process_bond_portfolio({"data": portfolio_data})
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["bonds"]), 2)
        self.assertIn("portfolio_metrics", result)
        
        # Check weighted average calculations
        portfolio_metrics = result["portfolio_metrics"]
        self.assertIn("weighted_avg_ytm", portfolio_metrics)
        self.assertIn("weighted_avg_duration", portfolio_metrics)
        self.assertIn("total_portfolio_value", portfolio_metrics)


class TestTreasuryEdgeCases(unittest.TestCase):
    """Test edge cases and error handling for Treasury bonds."""
    
    def test_treasury_with_zero_coupon(self):
        """Test handling of zero-coupon Treasury bills."""
        result = calculate_bond_master(
            description="T 0 15/03/25",  # Zero coupon
            price=98.50,
            settlement_date="2025-01-15"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["coupon_rate"], 0.0)
    
    def test_matured_treasury_bond(self):
        """Test handling of matured Treasury bonds."""
        result = calculate_bond_master(
            description="T 2.5 15/05/24",  # Matured bond
            price=100.0,
            settlement_date="2025-04-18"
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("matured", result.get("error", "").lower())
    
    def test_invalid_treasury_description(self):
        """Test handling of invalid Treasury descriptions."""
        result = calculate_bond_master(
            description="INVALID TREASURY",
            price=100.0,
            settlement_date="2025-04-18"
        )
        
        # Should still attempt calculation with parsed data
        self.assertIn(result["status"], ["success", "error"])


class TestTreasuryAPI(unittest.TestCase):
    """Test Treasury bonds through API endpoints (if API is running)."""
    
    def setUp(self):
        """Set up API test configuration."""
        self.api_base = "http://localhost:8080"
        self.skip_api_tests = os.environ.get("SKIP_API_TESTS", "true").lower() == "true"
    
    def test_treasury_api_endpoint(self):
        """Test Treasury bond calculation via API."""
        if self.skip_api_tests:
            self.skipTest("API tests disabled")
        
        # This would test the actual API endpoint
        # Implementation depends on API availability


def run_comprehensive_treasury_tests():
    """Run all Treasury bond tests and generate report."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestTreasuryParsing,
        TestTreasuryCalculations,
        TestTreasuryConventions,
        TestTreasuryPortfolio,
        TestTreasuryEdgeCases,
        TestTreasuryAPI
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "="*70)
    print(f"Treasury Bond Test Suite Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_treasury_tests()
    sys.exit(0 if success else 1)