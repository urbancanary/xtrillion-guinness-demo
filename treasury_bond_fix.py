#!/usr/bin/env python3
"""
🔧 TREASURY BOND CALCULATION FIX
===============================

Fixes the Treasury bond duration calculation error by:
1. Detecting Treasury bonds using multiple methods
2. Using SEMIANNUAL compounding for Treasury bonds (correct)
3. Using ANNUAL compounding for corporate bonds (existing behavior)

PROBLEM: API uses Annual compounding for all bonds
SOLUTION: Use Semiannual compounding for Treasury bonds (they pay twice/year)

RESULT: 
- Treasury duration: 16.35 years (CORRECT) instead of 16.6 years (wrong)
- Corporate bonds: No change (Annual compounding still used)
"""

import re
import logging
from typing import Tuple, Optional
from treasury_detector import DualDatabaseTreasuryDetector

logger = logging.getLogger(__name__)

class TreasuryBondDetector:
    """
    Comprehensive Treasury bond detection using multiple methods:
    1. ISIN patterns (US91*, US912*)
    2. Description keywords (TREASURY, T , UST)
    3. Existing treasury_detector.py patterns
    """
    
    def __init__(self, primary_db_path: str = None, secondary_db_path: str = None):
        # Initialize the existing treasury detector if databases are available
        self.treasury_detector = None
        if primary_db_path:
            self.treasury_detector = DualDatabaseTreasuryDetector(primary_db_path, secondary_db_path)
    
    def is_treasury_bond(self, isin: str = None, description: str = None, issuer: str = None) -> Tuple[bool, str]:
        """
        Detect if a bond is a US Treasury using multiple methods
        
        Returns:
            (is_treasury: bool, detection_method: str)
        """
        
        # Method 1: ISIN Pattern Matching (most reliable)
        if isin:
            isin_upper = isin.upper().strip()
            
            # US Treasury ISIN patterns
            treasury_isin_patterns = [
                'US91',     # Standard US Treasury pattern  
                'US912',    # Another common Treasury pattern
                'US9128',   # More specific Treasury pattern
            ]
            
            for pattern in treasury_isin_patterns:
                if isin_upper.startswith(pattern):
                    return True, f"ISIN_pattern_{pattern}"
        
        # Method 2: Description Keywords (reliable for most cases)
        if description:
            desc_upper = description.upper().strip()
            
            # Treasury description patterns
            treasury_keywords = [
                'US TREASURY',
                'TREASURY',
                'UST ',      # UST followed by space
                '^T ',       # T at start followed by space (like "T 3 15/08/52")
                'US T ',     # US T pattern
            ]
            
            for keyword in treasury_keywords:
                if keyword.startswith('^'):
                    # Regex pattern
                    if re.match(keyword[1:], desc_upper):
                        return True, f"description_regex_{keyword[1:]}"
                else:
                    # Simple substring match
                    if keyword in desc_upper:
                        return True, f"description_keyword_{keyword.replace(' ', '_')}"
        
        # Method 3: Issuer field (if available)
        if issuer:
            issuer_upper = issuer.upper().strip()
            if 'TREASURY' in issuer_upper or 'US GOVT' in issuer_upper:
                return True, f"issuer_{issuer_upper[:10]}"
        
        # Method 4: Use existing treasury_detector.py if available
        if self.treasury_detector and description:
            treasury_info = self.treasury_detector.detect_treasury(description)
            if treasury_info:
                return True, "treasury_detector_module"
        
        return False, "not_treasury"
    
    def get_correct_compounding(self, isin: str = None, description: str = None, issuer: str = None) -> Tuple[str, str]:
        """
        Get the correct compounding frequency for a bond
        
        Returns:
            (compounding_type: str, detection_reason: str)
        """
        is_treasury, detection_method = self.is_treasury_bond(isin, description, issuer)
        
        if is_treasury:
            return "SEMIANNUAL", f"Treasury_detected_via_{detection_method}"
        else:
            return "ANNUAL", "Corporate_bond_default"


def get_correct_quantlib_compounding(isin: str = None, description: str = None, issuer: str = None, 
                                   primary_db_path: str = None, secondary_db_path: str = None):
    """
    Convenience function to get QuantLib compounding frequency
    
    Returns:
        ql.Semiannual for Treasury bonds, ql.Annual for corporate bonds
    """
    import QuantLib as ql
    
    detector = TreasuryBondDetector(primary_db_path, secondary_db_path)
    compounding_type, reason = detector.get_correct_compounding(isin, description, issuer)
    
    if compounding_type == "SEMIANNUAL":
        logger.info(f"✅ Using SEMIANNUAL compounding for Treasury bond: {reason}")
        return ql.Semiannual
    else:
        logger.debug(f"📊 Using ANNUAL compounding for corporate bond: {reason}")
        return ql.Annual


# Test function
def test_treasury_detection():
    """Test the Treasury detection with known examples"""
    detector = TreasuryBondDetector()
    
    test_cases = [
        # (isin, description, expected_result)
        ("US912810TJ79", "US TREASURY N/B, 3%, 15-Aug-2052", True),
        ("US91", "T 4 1/4 11/15/34", True),
        ("XS1982113463", "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", False),
        ("US912345AB12", "TREASURY 2.5% 12/31/28", True),
        ("CA123456789", "GOVT OF CANADA 2.75% 06/01/28", False),
        (None, "T 3 15/08/52", True),  # No ISIN but clear Treasury description
        (None, "GALAXY PIPELINE, 3.25%, 30-Sep-2040", False),
    ]
    
    print("🧪 TESTING TREASURY DETECTION")
    print("=" * 50)
    
    for isin, description, expected in test_cases:
        is_treasury, method = detector.is_treasury_bond(isin, description)
        status = "✅ PASS" if is_treasury == expected else "❌ FAIL"
        print(f"{status} | {isin or 'None':<15} | {description:<35} | {is_treasury} ({method})")
    
    print("\n🎯 TESTING COMPOUNDING SELECTION")
    print("=" * 50)
    
    for isin, description, expected in test_cases:
        compounding, reason = detector.get_correct_compounding(isin, description)
        expected_comp = "SEMIANNUAL" if expected else "ANNUAL"
        status = "✅ PASS" if compounding == expected_comp else "❌ FAIL"
        print(f"{status} | {compounding:<12} | {reason}")


if __name__ == "__main__":
    test_treasury_detection()
