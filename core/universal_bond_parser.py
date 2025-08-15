#!/usr/bin/env python3
"""
Universal Bond Parser - Centralized Bond Processing System
=======================================================

Eliminates parsing redundancy by providing a single entry point for ALL bond parsing.
Integrates the proven SmartBondParser with ISIN lookup for complete coverage.

Usage:
    parser = UniversalBondParser(db_path, validated_db_path)
    bond_spec = parser.parse_bond(input_data)  # Works with ISIN or description
    
Architecture:
    Bond Input → UniversalBondParser → StandardizedBondSpec → All Calculation Methods
"""

import re
import sqlite3
from datetime import datetime
from typing import Dict, Optional, Union, List
import logging
from dataclasses import dataclass
from enum import Enum
import sys
import os

# Add parent directory to path to import SmartBondParser
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from bond_description_parser import SmartBondParser
    from enhanced_isin_date_parser import SmartBondParserEnhanced
    ENHANCED_PARSER_AVAILABLE = True
    print("✅ Enhanced ISIN Date Parser available")
except ImportError:
    # Fallback path
    sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')
    try:
        from bond_description_parser import SmartBondParser
        from enhanced_isin_date_parser import SmartBondParserEnhanced
        ENHANCED_PARSER_AVAILABLE = True
        print("✅ Enhanced ISIN Date Parser available (fallback path)")
    except ImportError:
        from bond_description_parser import SmartBondParser
        ENHANCED_PARSER_AVAILABLE = False
        print("⚠️ Enhanced parser not available, using standard parser")

# Treasury detection patterns
TREASURY_ISIN_PATTERNS = [
    r'^US912[0-9A-Z]{8}$',  # US Treasury ISIN pattern
    r'^US00206R[0-9A-Z]{4}$',  # Alternative Treasury pattern
]

TREASURY_DESCRIPTION_PATTERNS = [
    r'\bTREASURY\b',
    r'\bT\s+[\d.]+\s+\d{2}/\d{2}/\d{2,4}',  # "T 4.3 02/15/30"
    r'\bUS\s+TREASURY\b',
    r'\bUST\b',
]


class BondInputType(Enum):
    """Bond input classification"""
    ISIN = "isin"
    DESCRIPTION = "description"
    UNKNOWN = "unknown"


class TreasuryDetector:
    """Detects US Treasury bonds and notes"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def is_us_treasury(self, isin: Optional[str] = None, 
                       description: Optional[str] = None,
                       country: Optional[str] = None,
                       issuer: Optional[str] = None) -> bool:
        """Detect if bond is a US Treasury using multiple criteria"""
        
        # Method 1: ISIN pattern matching
        if isin:
            isin_clean = isin.strip().upper()
            for pattern in TREASURY_ISIN_PATTERNS:
                if re.match(pattern, isin_clean):
                    self.logger.info(f"🏛️ Treasury detected by ISIN pattern: {isin}")
                    return True
        
        # Method 2: Description pattern matching
        if description:
            desc_upper = description.upper()
            for pattern in TREASURY_DESCRIPTION_PATTERNS:
                if re.search(pattern, desc_upper):
                    self.logger.info(f"🏛️ Treasury detected by description pattern: {description}")
                    return True
        
        return False


class TreasuryOverride:
    """Applies correct Treasury conventions, overriding incorrect database data"""
    
    def __init__(self):
        self.detector = TreasuryDetector()
        self.logger = logging.getLogger(__name__)
        
    def apply_treasury_override(self, bond_spec) -> bool:
        """Apply Treasury convention override to bond specification"""
        
        # Detect if this is a Treasury bond
        is_treasury = self.detector.is_us_treasury(
            isin=getattr(bond_spec, 'isin', None),
            description=getattr(bond_spec, 'description', None),
            country=getattr(bond_spec, 'country', None),
            issuer=getattr(bond_spec, 'issuer', None)
        )
        
        if not is_treasury:
            return False
        
        # Apply Treasury convention overrides (correct QuantLib conventions)
        original_day_count = getattr(bond_spec, 'day_count', None)
        original_business_convention = getattr(bond_spec, 'business_convention', None)
        
        # Override with correct Treasury conventions
        bond_spec.day_count = "ActualActual(Bond)"  # Correct for US Treasuries
        bond_spec.frequency = "Semiannual"
        bond_spec.business_convention = "Following"
        bond_spec.currency = "USD"
        bond_spec.country = "US"
        
        # Mark that override was applied
        bond_spec.treasury_override_applied = True
        
        # Log the override action
        self.logger.info(f"🏛️ Treasury convention override applied:")
        self.logger.info(f"   Day Count: {original_day_count} → {bond_spec.day_count}")
        self.logger.info(f"   Business Convention: {original_business_convention} → {bond_spec.business_convention}")
        
        return True


@dataclass
class BondSpecification:
    """Standardized bond specification for all calculation methods"""
    # Core identifiers
    isin: Optional[str] = None
    description: Optional[str] = None
    
    # Parsed bond details
    issuer: Optional[str] = None
    coupon_rate: Optional[float] = None
    maturity_date: Optional[str] = None
    
    # Market conventions (from SmartBondParser or database)
    day_count: str = 'ActualActual_ISDA'
    business_convention: str = 'Following'
    frequency: str = 'Semiannual'
    currency: str = 'USD'
    country: str = 'Unknown'
    
    # Calculation inputs
    clean_price: Optional[float] = None
    settlement_date: Optional[str] = None
    
    # Parsing metadata
    input_type: BondInputType = BondInputType.UNKNOWN
    parser_used: str = 'unknown'
    parsing_success: bool = False
    error_message: Optional[str] = None
    treasury_override_applied: bool = False  # Track Treasury convention overrides
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return {
            'isin': self.isin,
            'description': self.description,
            'issuer': self.issuer,
            'coupon_rate': self.coupon_rate,
            'maturity_date': self.maturity_date,
            'day_count': self.day_count,
            'business_convention': self.business_convention,
            'frequency': self.frequency,
            'currency': self.currency,
            'country': self.country,
            'clean_price': self.clean_price,
            'settlement_date': self.settlement_date,
            'input_type': self.input_type.value,
            'parser_used': self.parser_used,
            'parsing_success': self.parsing_success,
            'error_message': self.error_message
        }


class UniversalBondParser:
    """
    Universal Bond Parser - Single entry point for ALL bond parsing
    
    Eliminates redundancy by routing through:
    1. ISIN lookup (database) for exact matches
    2. SmartBondParser (720 lines, proven) for descriptions
    3. Fallback strategies for edge cases
    """
    
    def __init__(self, db_path: str, validated_db_path: str, bloomberg_db_path: str):
        self.db_path = db_path
        self.validated_db_path = validated_db_path
        self.bloomberg_db_path = bloomberg_db_path
        self.bloomberg_db_path = bloomberg_db_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize enhanced parser with ISIN date format detection
        try:
            if ENHANCED_PARSER_AVAILABLE:
                self.smart_parser = SmartBondParserEnhanced(self.db_path, self.validated_db_path, self.bloomberg_db_path)
                self.logger.info("✅ Enhanced ISIN Date Parser initialized")
            else:
                self.smart_parser = SmartBondParser(self.bloomberg_db_path, self.validated_db_path, self.db_path)
                self.logger.info("✅ Standard SmartBondParser initialized (fallback)")
            self.smart_parser_available = True
        except Exception as e:
            self.logger.warning(f"SmartBondParser initialization failed: {e}")
            self.smart_parser = None
            self.smart_parser_available = False
        
        self.logger.info("UniversalBondParser initialized with centralized parsing")
    
    def parse_bond(self, 
                   input_data: str, 
                   clean_price: Optional[float] = None,
                   settlement_date: Optional[str] = None) -> BondSpecification:
        """
        Universal bond parsing - single entry point for ALL parsing needs
        
        Args:
            input_data: ISIN code or bond description
            clean_price: Optional market price
            settlement_date: Optional settlement date
            
        Returns:
            BondSpecification: Standardized bond object for all calculation methods
        """
        # Create base specification
        spec = BondSpecification(
            clean_price=clean_price,
            settlement_date=settlement_date
        )
        
        try:
            # Step 1: Classify input type
            input_type = self._classify_input(input_data)
            spec.input_type = input_type
            
            # Step 2: Route to appropriate parser
            if input_type == BondInputType.ISIN:
                if not self._parse_by_isin(input_data, spec):
                    # Fallback: try description parsing if ISIN lookup fails
                    self._parse_by_description(input_data, spec)
            elif input_type == BondInputType.DESCRIPTION:
                if not self._parse_by_description(input_data, spec):
                    # Fallback: try ISIN lookup if description parsing fails
                    self._parse_by_isin(input_data, spec)
            else:
                # Fallback: try both methods for unknown input
                if not self._parse_by_isin(input_data, spec):
                    self._parse_by_description(input_data, spec)
            
            # Step 2.5: Apply Treasury override if detected (NEW!)
            treasury_override = TreasuryOverride()
            if treasury_override.apply_treasury_override(spec):
                self.logger.info(f"✅ Treasury conventions corrected for: {input_data}")
            
            # Step 3: Validate and finalize
            self._validate_specification(spec)
            
        except Exception as e:
            self.logger.error(f"Universal parsing failed for '{input_data}': {e}")
            spec.parsing_success = False
            spec.error_message = str(e)
            spec.parser_used = 'failed'
        
        return spec
    
    def _classify_input(self, input_data: str) -> BondInputType:
        """Classify input as ISIN or description"""
        input_clean = input_data.strip().upper()
        
        # ISIN pattern: 12 characters, starts with 2 letters, ends with 10 alphanumeric
        isin_pattern = r'^[A-Z]{2}[A-Z0-9]{10}$'
        
        if re.match(isin_pattern, input_clean):
            return BondInputType.ISIN
        elif len(input_clean) >= 5:  # Minimum for meaningful description
            return BondInputType.DESCRIPTION
        else:
            return BondInputType.UNKNOWN
    
    def _parse_by_isin(self, isin: str, spec: BondSpecification) -> bool:
        """Parse bond using ISIN database lookup - PRIMARY: bloomberg_index.db"""
        try:
            # PRIMARY: Try bloomberg_index.db first (contains validated bond specifications)
            bond_data = self._lookup_isin_in_database(isin, self.bloomberg_db_path)
            
            # Fallback: Try validated_quantlib_bonds.db if not found
            if not bond_data:
                bond_data = self._lookup_isin_in_database(isin, self.validated_db_path)
            
            # Last resort: Try bonds_data.db (market data, not specifications)
            if not bond_data:
                bond_data = self._lookup_isin_in_database(isin, self.db_path)
            
            if bond_data:
                self._populate_spec_from_database(bond_data, spec)
                spec.isin = isin
                spec.parser_used = 'database_lookup'
                spec.parsing_success = True
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"ISIN lookup failed for {isin}: {e}")
            return False
    
    def _parse_by_description(self, description: str, spec: BondSpecification) -> bool:
        """Parse bond using proven SmartBondParser (720 lines)"""
        if not self.smart_parser_available:
            self.logger.warning("SmartBondParser not available for description parsing")
            return False
            
        try:
            # Use enhanced parser with ISIN context for intelligent date format detection
            isin_context = spec.isin if hasattr(spec, 'isin') else None
            
            if ENHANCED_PARSER_AVAILABLE and hasattr(self.smart_parser, 'parse_bond_description'):
                # Enhanced parser with ISIN date format detection
                parsed_result = self.smart_parser.parse_bond_description(description, isin_context)
                self.logger.info(f"🧠 Enhanced parser used with ISIN context: {isin_context}")
            else:
                # Fallback to standard parser  
                parsed_result = self.smart_parser.parse_bond_description(description)
                self.logger.info(f"📝 Standard parser used (no ISIN context)")
            
            if parsed_result:
                self._populate_spec_from_smart_parser(parsed_result, spec)
                spec.description = description
                spec.parser_used = 'enhanced_smart_parser' if ENHANCED_PARSER_AVAILABLE else 'smart_bond_parser'
                spec.parsing_success = True
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"SmartBondParser failed for '{description}': {e}")
            return False
    
    def _lookup_isin_in_database(self, isin: str, db_path: str) -> Optional[Dict]:
        """Generic database lookup for ISIN"""
        try:
            if not os.path.exists(db_path):
                return None
                
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # FIXED: Use actual table names that exist in the databases
                if 'validated_quantlib_bonds.db' in db_path:
                    tables_to_try = ['validated_quantlib_bonds']
                    isin_columns = ['ISIN']
                elif 'bloomberg_index.db' in db_path:
                    tables_to_try = ['validated_quantlib_bonds']
                    isin_columns = ['isin']
                else:  # bonds_data.db
                    tables_to_try = ['legatruu_raw', 'bond_pricing', 'raw', 'live', 'static']
                    isin_columns = ['isin', 'ISIN']
                
                for table in tables_to_try:
                    for isin_col in isin_columns:
                        try:
                            cursor.execute(f"SELECT * FROM {table} WHERE {isin_col} = ?", (isin,))
                            result = cursor.fetchone()
                            if result:
                                self.logger.info(f"✅ ISIN {isin} found in {table}.{isin_col}")
                                return dict(result)
                        except sqlite3.Error as e:
                            self.logger.debug(f"Table {table}.{isin_col} lookup failed: {e}")
                            continue  # Table or column doesn't exist
                
                self.logger.warning(f"⚠️ ISIN {isin} not found in any table in {db_path}")
                return None
                
        except Exception as e:
            self.logger.debug(f"Database lookup failed for {isin} in {db_path}: {e}")
            return None
    
    def _populate_spec_from_database(self, bond_data: Dict, spec: BondSpecification):
        """Populate specification from database lookup"""
        # Map database columns to specification fields
        field_mappings = {
            'issuer': ['issuer', 'company_name', 'name', 'bond_name', 'NAME'],
            'coupon_rate': ['coupon', 'coupon_rate', 'rate', 'cpn', 'CPN', 'Coupon'],
            'maturity_date': ['maturity', 'maturity_date', 'mat_date', 'expiry', 'MATURITY', 'Maturity'],
            'day_count': ['day_count', 'day_count_convention', 'dcc'],
            'frequency': ['frequency', 'payment_frequency', 'freq'],
            'business_convention': ['business_convention', 'bus_conv'],
            'currency': ['currency', 'crncy', 'curr', 'CRNCY', 'ccy'],
            'country': ['country', 'country_iso', 'cntry'],
            'description': ['description', 'Description', 'bond_description', 'desc']
        }
        
        for spec_field, possible_columns in field_mappings.items():
            for column in possible_columns:
                if column in bond_data and bond_data[column] is not None:
                    setattr(spec, spec_field, bond_data[column])
                    break  # Use first match found
        
        # Apply defaults as specified by user
        if not spec.currency:
            spec.currency = 'USD'  # Default currency
    
    def _populate_spec_from_smart_parser(self, parsed_result: Dict, spec: BondSpecification):
        """Populate specification from SmartBondParser result"""
        # Map SmartBondParser output to specification
        if 'issuer' in parsed_result:
            spec.issuer = parsed_result['issuer']
        
        # Handle both 'coupon' and 'coupon_rate' field names
        if 'coupon_rate' in parsed_result:
            spec.coupon_rate = parsed_result['coupon_rate']
        elif 'coupon' in parsed_result:
            spec.coupon_rate = parsed_result['coupon']
        
        # Handle both 'maturity' and 'maturity_date' field names
        if 'maturity_date' in parsed_result:
            spec.maturity_date = parsed_result['maturity_date']
        elif 'maturity' in parsed_result:
            spec.maturity_date = parsed_result['maturity']
            
        # Handle currency and bond type
        if 'currency' in parsed_result:
            spec.currency = parsed_result['currency']
        if 'bond_type' in parsed_result:
            spec.country = parsed_result['bond_type']  # Map bond_type to country for now
            
        if 'conventions' in parsed_result:
            conventions = parsed_result['conventions']
            spec.day_count = conventions.get('day_count', spec.day_count)
            spec.business_convention = conventions.get('business_convention', spec.business_convention)
            spec.frequency = conventions.get('frequency', spec.frequency)
            spec.currency = conventions.get('currency', spec.currency)
            spec.country = conventions.get('country', spec.country)
    
    def _validate_specification(self, spec: BondSpecification):
        """Validate and finalize bond specification"""
        # Ensure we have minimum required fields
        if not spec.parsing_success:
            return
        
        # Set defaults if missing
        if not spec.day_count:
            spec.day_count = 'ActualActual_ISDA'
        if not spec.frequency:
            spec.frequency = 'Semiannual'
        if not spec.currency:
            spec.currency = 'USD'
        
        # Validate required fields for calculations
        required_fields = ['coupon_rate', 'maturity_date']
        missing_fields = [field for field in required_fields if not getattr(spec, field)]
        
        if missing_fields:
            spec.parsing_success = False
            spec.error_message = f"Missing required fields: {missing_fields}"
    
    def parse_multiple_bonds(self, 
                           bond_inputs: List[Dict],
                           default_settlement_date: Optional[str] = None) -> List[BondSpecification]:
        """
        Parse multiple bonds efficiently
        
        Args:
            bond_inputs: List of {'input': str, 'price': float, 'settlement': str}
            default_settlement_date: Default settlement if not specified per bond
            
        Returns:
            List[BondSpecification]: Parsed bond specifications
        """
        results = []
        
        for bond_input in bond_inputs:
            input_data = bond_input.get('input', '')
            clean_price = bond_input.get('price')
            settlement_date = bond_input.get('settlement', default_settlement_date)
            
            spec = self.parse_bond(input_data, clean_price, settlement_date)
            results.append(spec)
        
        return results
    
    def get_parsing_statistics(self, specs: List[BondSpecification]) -> Dict:
        """Get parsing success statistics"""
        total = len(specs)
        successful = sum(1 for spec in specs if spec.parsing_success)
        
        parser_usage = {}
        for spec in specs:
            parser = spec.parser_used
            parser_usage[parser] = parser_usage.get(parser, 0) + 1
        
        return {
            'total_bonds': total,
            'successful_parses': successful,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'parser_usage': parser_usage,
            'failed_bonds': [spec.to_dict() for spec in specs if not spec.parsing_success]
        }


# Convenience functions for backward compatibility
def parse_bond(input_data: str, 
               db_path: str, 
               validated_db_path: str, 
               bloomberg_db_path: str, 
               **kwargs) -> BondSpecification:
    """Convenience function for single bond parsing"""
    parser = UniversalBondParser(db_path, validated_db_path)
    return parser.parse_bond(input_data, **kwargs)


def is_isin(input_data: str) -> bool:
    """Quick check if input looks like an ISIN"""
    parser = UniversalBondParser('', '', '')
    return parser._classify_input(input_data) == BondInputType.ISIN


if __name__ == "__main__":
    # Example usage
    parser = UniversalBondParser('bonds_data.db', 'validated_quantlib_bonds.db')
    
    # Test cases from your 6-way analysis
    test_cases = [
        "US912810TJ79",  # US Treasury ISIN
        "US TREASURY N/B, 3%, 15-Aug-2052",  # Treasury description
        "PANAMA, 3.87%, 23-Jul-2060",  # The problematic PANAMA bond that SmartBondParser fixed!
        "GALAXY PIPELINE, 3.25%, 30-Sep-2040",  # Institutional format
    ]
    
    print("🚀 Universal Bond Parser Test")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case}")
        spec = parser.parse_bond(test_case, clean_price=75.0)
        print(f"Success: {spec.parsing_success}")
        print(f"Parser: {spec.parser_used}")
        print(f"Input Type: {spec.input_type.value}")
        if spec.parsing_success:
            print(f"Issuer: {spec.issuer}")
            print(f"Coupon: {spec.coupon_rate}%")
            print(f"Maturity: {spec.maturity_date}")
        else:
            print(f"Error: {spec.error_message}")
