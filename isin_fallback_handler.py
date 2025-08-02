#!/usr/bin/env python3
"""
ISIN Fallback Handler - Implements proper fallback hierarchy
===========================================================

When ISIN lookup fails, implements the following hierarchy:
1. Parse ISIN as description to extract ticker
2. Analyze ISIN structure for conventions (US912 = Treasury)
3. Use most frequent conventions (30/360 for corporates)
"""

import re
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class ISINFallbackHandler:
    """Handles ISIN fallback with proper hierarchy"""
    
    def __init__(self):
        # ISIN patterns for different bond types
        self.treasury_patterns = ['US912', 'US91', 'US9128']
        self.agency_patterns = ['US313', 'US314']  # Fannie Mae, Freddie Mac
        
        # Default conventions by bond type
        self.default_conventions = {
            'treasury': {
                'day_count': 'ActualActual_Bond',
                'business_convention': 'Following',
                'frequency': 'Semiannual',
                'end_of_month': True
            },
            'corporate': {
                'day_count': '30/360',
                'business_convention': 'Following', 
                'frequency': 'Semiannual',
                'end_of_month': False
            },
            'agency': {
                'day_count': '30/360',
                'business_convention': 'Following',
                'frequency': 'Semiannual', 
                'end_of_month': False
            }
        }
    
    def analyze_isin_structure(self, isin: str) -> Tuple[str, Dict]:
        """
        Analyze ISIN structure to determine bond type and conventions
        
        Returns:
            (bond_type, conventions)
        """
        if not isin:
            return 'corporate', self.default_conventions['corporate']
            
        isin_upper = isin.upper().strip()
        
        # Check Treasury patterns
        for pattern in self.treasury_patterns:
            if isin_upper.startswith(pattern):
                logger.info(f"🏛️ ISIN {isin} identified as Treasury via pattern {pattern}")
                return 'treasury', self.default_conventions['treasury']
        
        # Check Agency patterns
        for pattern in self.agency_patterns:
            if isin_upper.startswith(pattern):
                logger.info(f"🏢 ISIN {isin} identified as Agency via pattern {pattern}")
                return 'agency', self.default_conventions['agency']
        
        # Check country code
        country_code = isin_upper[:2] if len(isin_upper) >= 2 else ''
        
        if country_code == 'US':
            # US corporate bond
            logger.info(f"🏭 ISIN {isin} identified as US Corporate")
            return 'corporate', self.default_conventions['corporate']
        elif country_code in ['GB', 'DE', 'FR', 'JP']:
            # International corporate - may have different conventions
            logger.info(f"🌍 ISIN {isin} identified as International Corporate ({country_code})")
            conventions = self.default_conventions['corporate'].copy()
            # Some international bonds use ActualActual
            if country_code in ['DE', 'FR']:
                conventions['day_count'] = 'ActualActual_ISDA'
            return 'corporate', conventions
        else:
            # Unknown - use corporate defaults
            logger.info(f"❓ ISIN {isin} unrecognized pattern - using corporate defaults")
            return 'corporate', self.default_conventions['corporate']
    
    def extract_ticker_from_isin(self, isin: str, description: Optional[str] = None) -> Optional[str]:
        """
        Try to extract a ticker from ISIN or use description if available
        
        Returns:
            ticker string or None
        """
        if description:
            # Parse description for ticker
            desc_upper = description.upper()
            
            # Common patterns
            if desc_upper.startswith('T '):
                return 'T'  # Treasury
            
            # Extract first word before comma or percent
            match = re.match(r'^([A-Z]+)\s*[,%]', desc_upper)
            if match:
                return match.group(1)
            
            # Extract first word
            words = desc_upper.split()
            if words:
                return words[0]
        
        # ISIN-based ticker extraction
        if isin:
            isin_upper = isin.upper()
            
            # Treasury
            if any(isin_upper.startswith(p) for p in self.treasury_patterns):
                return 'T'
            
            # Try to extract from ISIN structure
            # Some ISINs encode issuer info in middle characters
            # This is a simplified approach
            if len(isin_upper) >= 6:
                # Characters 3-5 sometimes indicate issuer
                potential_ticker = isin_upper[2:5]
                if potential_ticker.isalpha():
                    return potential_ticker
        
        return None
    
    def get_fallback_conventions(self, 
                                isin: Optional[str] = None,
                                description: Optional[str] = None,
                                parsed_data: Optional[Dict] = None) -> Dict:
        """
        Get fallback conventions using the hierarchy:
        1. Try to extract ticker and lookup conventions
        2. Analyze ISIN structure
        3. Use defaults based on bond type
        
        Returns:
            Dictionary of conventions
        """
        logger.info(f"🔄 Getting fallback conventions for ISIN: {isin}")
        
        # Step 1: Try to extract ticker
        ticker = self.extract_ticker_from_isin(isin, description)
        if ticker:
            logger.info(f"📊 Extracted ticker: {ticker}")
            # Here you could lookup ticker-specific conventions
            # For now, we'll just use it to determine bond type
            if ticker == 'T':
                return self.default_conventions['treasury']
        
        # Step 2: Analyze ISIN structure
        bond_type, conventions = self.analyze_isin_structure(isin)
        
        # Step 3: Override with parsed data if available
        if parsed_data:
            if parsed_data.get('bond_type') == 'treasury':
                return self.default_conventions['treasury']
        
        logger.info(f"📋 Using {bond_type} conventions: {conventions}")
        return conventions

# Singleton instance
isin_fallback_handler = ISINFallbackHandler()

def get_isin_fallback_conventions(isin: Optional[str] = None,
                                 description: Optional[str] = None,
                                 parsed_data: Optional[Dict] = None) -> Dict:
    """Convenience function to get fallback conventions"""
    return isin_fallback_handler.get_fallback_conventions(isin, description, parsed_data)