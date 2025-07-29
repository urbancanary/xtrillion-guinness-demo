#!/usr/bin/env python3
"""
Centralized Bond Date Parser - Sophisticated date parsing for all Google Analysis 10 components

This replaces all scattered date parsing throughout the codebase with one robust,
well-tested implementation that handles all bond date formats correctly.

Author: Created to solve scattered date parsing bugs
Usage: Import BondDateParser and use parse_date() method throughout codebase
"""

import re
from datetime import datetime, date
from typing import Optional, Union, Dict, List, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DateParseResult:
    """Result of date parsing with detailed metadata"""
    success: bool
    date_iso: Optional[str] = None  # YYYY-MM-DD format
    date_obj: Optional[date] = None
    original_input: Optional[str] = None
    detected_format: Optional[str] = None
    confidence: float = 0.0  # 0.0 to 1.0
    method_used: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class BondDateParser:
    """
    Sophisticated bond date parser that handles all formats found in financial markets
    
    Features:
    - Multiple format detection (US, European, International)
    - Intelligent century handling for 2-digit years
    - Country/region-specific format preferences
    - Month name parsing (Jan, Feb, Sep, etc.)
    - Multiple separator support (/, -, space, etc.)
    - ISIN country code detection for format hints
    - Comprehensive error handling and fallbacks
    - Detailed logging and debugging info
    """
    
    def __init__(self):
        # Month name mappings
        self.month_names = {
            'JAN': '01', 'JANUARY': '01',
            'FEB': '02', 'FEBRUARY': '02', 
            'MAR': '03', 'MARCH': '03',
            'APR': '04', 'APRIL': '04',
            'MAY': '05',
            'JUN': '06', 'JUNE': '06',
            'JUL': '07', 'JULY': '07',
            'AUG': '08', 'AUGUST': '08',
            'SEP': '09', 'SEPTEMBER': '09',
            'OCT': '10', 'OCTOBER': '10',
            'NOV': '11', 'NOVEMBER': '11',
            'DEC': '12', 'DECEMBER': '12'
        }
        
        # Country codes that typically use US format (MM/DD/YY)
        self.us_format_countries = {
            'US', 'CA', 'PH', 'PA', 'BS', 'FM', 'MH', 'PW'
        }
        
        # Country codes that typically use European format (DD/MM/YY)
        self.european_format_countries = {
            'GB', 'FR', 'DE', 'IT', 'ES', 'NL', 'BE', 'AT', 'IE', 'PT', 'FI', 
            'GR', 'MT', 'CY', 'SI', 'SK', 'EE', 'LV', 'LT', 'PL', 'CZ', 'HU',
            'XS',  # Eurobond/International (typically European format)
            'LU', 'CH', 'NO', 'SE', 'DK',  # Other European
            'AU', 'NZ',  # Australia/New Zealand (DD/MM format)
            'HK', 'SG',  # Hong Kong/Singapore (DD/MM format)
        }
        
        # Date parsing patterns (order matters - most specific first)
        self.date_patterns = [
            # ISO format: YYYY-MM-DD
            (r'^(\d{4})-(\d{1,2})-(\d{1,2})$', 'iso', self._parse_iso),
            
            # Full year formats: MM/DD/YYYY or DD/MM/YYYY  
            (r'^(\d{1,2})[\/\-\s](\d{1,2})[\/\-\s](\d{4})$', 'full_year_numeric', self._parse_full_year_numeric),
            
            # Two digit year: MM/DD/YY or DD/MM/YY
            (r'^(\d{1,2})[\/\-\s](\d{1,2})[\/\-\s](\d{2})$', 'two_digit_year', self._parse_two_digit_year),
            
            # Month name formats: DD-MMM-YYYY, DD-MMM-YY, etc.
            (r'^(\d{1,2})[\/\-\s]([A-Za-z]{3,9})[\/\-\s](\d{2,4})$', 'month_name', self._parse_month_name),
            
            # International bond format: DD-Mon-YYYY
            (r'^(\d{1,2})-([A-Za-z]{3})-(\d{4})$', 'international', self._parse_international),
            
            # Compact formats: DDMMYYYY, MMDDYYYY, DDMMYY, MMDDYY
            (r'^(\d{2})(\d{2})(\d{4})$', 'compact_full', self._parse_compact_full),
            (r'^(\d{2})(\d{2})(\d{2})$', 'compact_short', self._parse_compact_short),
        ]
    
    def parse_date(self, 
                   date_input: Union[str, datetime, date, None],
                   isin: Optional[str] = None,
                   description: Optional[str] = None,
                   country_hint: Optional[str] = None,
                   assume_future: bool = True) -> DateParseResult:
        """
        Parse any date input and return standardized result
        
        Args:
            date_input: Date to parse (string, datetime, date, or None)
            isin: ISIN code for country format hints
            description: Bond description for additional context
            country_hint: Explicit country code override
            assume_future: For 2-digit years, assume future dates (bond default)
            
        Returns:
            DateParseResult with parsed date and metadata
        """
        if not date_input:
            return DateParseResult(success=False, original_input=str(date_input))
        
        # Handle already parsed dates
        if isinstance(date_input, datetime):
            return DateParseResult(
                success=True,
                date_iso=date_input.date().isoformat(),
                date_obj=date_input.date(),
                original_input=str(date_input),
                detected_format="datetime_object",
                confidence=1.0,
                method_used="direct_conversion"
            )
        
        if isinstance(date_input, date):
            return DateParseResult(
                success=True,
                date_iso=date_input.isoformat(),
                date_obj=date_input,
                original_input=str(date_input),
                detected_format="date_object", 
                confidence=1.0,
                method_used="direct_conversion"
            )
        
        # Handle string input
        date_str = str(date_input).strip()
        if not date_str:
            return DateParseResult(success=False, original_input=date_str)
        
        logger.debug(f"📅 Parsing date: '{date_str}' (ISIN: {isin}, Country: {country_hint})")
        
        # Detect preferred format based on context
        preferred_format = self._detect_format_preference(isin, description, country_hint)
        
        # Try each pattern in order
        for pattern, format_name, parse_func in self.date_patterns:
            match = re.match(pattern, date_str)
            if match:
                try:
                    result = parse_func(match, preferred_format, assume_future)
                    if result.success:
                        result.original_input = date_str
                        result.detected_format = format_name
                        result.method_used = parse_func.__name__
                        logger.debug(f"✅ Parsed '{date_str}' → {result.date_iso} (method: {format_name})")
                        return result
                except Exception as e:
                    logger.warning(f"❌ Pattern '{format_name}' failed for '{date_str}': {e}")
                    continue
        
        # Fallback: try standard datetime formats
        fallback_result = self._fallback_parse(date_str)
        fallback_result.original_input = date_str
        
        if not fallback_result.success:
            logger.error(f"❌ Failed to parse date: '{date_str}'")
        
        return fallback_result
    
    def _detect_format_preference(self, isin: Optional[str], description: Optional[str], country_hint: Optional[str]) -> str:
        """Detect preferred date format based on context"""
        
        # Explicit country hint takes priority
        if country_hint:
            if country_hint.upper() in self.us_format_countries:
                return 'US'
            elif country_hint.upper() in self.european_format_countries:
                return 'EU'
        
        # ISIN country code detection
        if isin and len(isin) >= 2:
            country_code = isin[:2].upper()
            if country_code in self.us_format_countries:
                logger.debug(f"🇺🇸 US format detected from ISIN {isin} (country: {country_code})")
                return 'US'
            elif country_code in self.european_format_countries:
                logger.debug(f"🇪🇺 European format detected from ISIN {isin} (country: {country_code})")
                return 'EU'
        
        # Description context analysis
        if description:
            desc_upper = description.upper()
            # US Treasury indicators
            if any(indicator in desc_upper for indicator in ['T ', 'UST', 'US TREASURY', 'TREASURY']):
                logger.debug(f"🏛️ US Treasury format detected from description: {description}")
                return 'US'
            # European indicators (could be expanded)
            if any(indicator in desc_upper for indicator in ['BUND', 'OAT', 'BTP', 'GILT']):
                logger.debug(f"🇪🇺 European format detected from description: {description}")
                return 'EU'
        
        # Default to European format (safer for international bonds)
        logger.debug("🌐 Defaulting to European format (DD/MM/YY)")
        return 'EU'
    
    def _parse_iso(self, match: re.Match, preferred_format: str, assume_future: bool) -> DateParseResult:
        """Parse ISO format: YYYY-MM-DD"""
        year, month, day = match.groups()
        
        try:
            date_obj = date(int(year), int(month), int(day))
            return DateParseResult(
                success=True,
                date_iso=date_obj.isoformat(),
                date_obj=date_obj,
                confidence=1.0
            )
        except ValueError as e:
            return DateParseResult(success=False, warnings=[f"Invalid ISO date: {e}"])
    
    def _parse_full_year_numeric(self, match: re.Match, preferred_format: str, assume_future: bool) -> DateParseResult:
        """Parse full year numeric: MM/DD/YYYY or DD/MM/YYYY"""
        comp1, comp2, year = match.groups()
        
        # Determine format based on values and preference
        if preferred_format == 'US':
            month, day = comp1, comp2
        else:  # EU format
            day, month = comp1, comp2
        
        try:
            date_obj = date(int(year), int(month), int(day))
            return DateParseResult(
                success=True,
                date_iso=date_obj.isoformat(),
                date_obj=date_obj,
                confidence=0.9 if preferred_format else 0.7
            )
        except ValueError:
            # Try swapping if first attempt failed
            try:
                if preferred_format == 'US':
                    day, month = comp1, comp2
                else:
                    month, day = comp1, comp2
                
                date_obj = date(int(year), int(month), int(day))
                return DateParseResult(
                    success=True,
                    date_iso=date_obj.isoformat(),
                    date_obj=date_obj,
                    confidence=0.6,
                    warnings=[f"Swapped month/day order for format {preferred_format}"]
                )
            except ValueError as e:
                return DateParseResult(success=False, warnings=[f"Invalid date components: {e}"])
    
    def _parse_two_digit_year(self, match: re.Match, preferred_format: str, assume_future: bool) -> DateParseResult:
        """Parse two-digit year: MM/DD/YY or DD/MM/YY"""
        comp1, comp2, year_2d = match.groups()
        
        # Handle century logic for bonds (prefer future dates)
        full_year = self._expand_two_digit_year(int(year_2d), assume_future)
        
        # Determine month/day order
        if preferred_format == 'US':
            month, day = comp1, comp2
        else:  # EU format  
            day, month = comp1, comp2
        
        try:
            date_obj = date(full_year, int(month), int(day))
            return DateParseResult(
                success=True,
                date_iso=date_obj.isoformat(),
                date_obj=date_obj,
                confidence=0.8 if preferred_format else 0.6,
                warnings=[f"Expanded 2-digit year {year_2d} → {full_year}"]
            )
        except ValueError:
            # Try swapping month/day
            try:
                if preferred_format == 'US':
                    day, month = comp1, comp2
                else:
                    month, day = comp1, comp2
                
                date_obj = date(full_year, int(month), int(day))
                return DateParseResult(
                    success=True,
                    date_iso=date_obj.isoformat(),
                    date_obj=date_obj,
                    confidence=0.5,
                    warnings=[
                        f"Expanded 2-digit year {year_2d} → {full_year}",
                        f"Swapped month/day order for format {preferred_format}"
                    ]
                )
            except ValueError as e:
                return DateParseResult(success=False, warnings=[f"Invalid date components: {e}"])
    
    def _parse_month_name(self, match: re.Match, preferred_format: str, assume_future: bool) -> DateParseResult:
        """Parse month name format: DD-MMM-YYYY or DD-MMM-YY"""
        day, month_name, year = match.groups()
        
        # Convert month name to number
        month_num = self.month_names.get(month_name.upper())
        if not month_num:
            return DateParseResult(success=False, warnings=[f"Unknown month name: {month_name}"])
        
        # Handle 2-digit vs 4-digit year
        if len(year) == 2:
            full_year = self._expand_two_digit_year(int(year), assume_future)
            warnings = [f"Expanded 2-digit year {year} → {full_year}"]
        else:
            full_year = int(year)
            warnings = []
        
        try:
            date_obj = date(full_year, int(month_num), int(day))
            return DateParseResult(
                success=True,
                date_iso=date_obj.isoformat(),
                date_obj=date_obj,
                confidence=0.9,
                warnings=warnings
            )
        except ValueError as e:
            return DateParseResult(success=False, warnings=[f"Invalid date: {e}"])
    
    def _parse_international(self, match: re.Match, preferred_format: str, assume_future: bool) -> DateParseResult:
        """Parse international format: DD-Mon-YYYY"""
        return self._parse_month_name(match, preferred_format, assume_future)
    
    def _parse_compact_full(self, match: re.Match, preferred_format: str, assume_future: bool) -> DateParseResult:
        """Parse compact full year: DDMMYYYY or MMDDYYYY"""
        comp1, comp2, year = match.groups()
        
        if preferred_format == 'US':
            month, day = comp1, comp2
        else:
            day, month = comp1, comp2
        
        try:
            date_obj = date(int(year), int(month), int(day))
            return DateParseResult(
                success=True,
                date_iso=date_obj.isoformat(),
                date_obj=date_obj,
                confidence=0.7
            )
        except ValueError:
            # Try swapping
            try:
                if preferred_format == 'US':
                    day, month = comp1, comp2
                else:
                    month, day = comp1, comp2
                
                date_obj = date(int(year), int(month), int(day))
                return DateParseResult(
                    success=True,
                    date_iso=date_obj.isoformat(),
                    date_obj=date_obj,
                    confidence=0.5,
                    warnings=[f"Swapped month/day for compact format"]
                )
            except ValueError as e:
                return DateParseResult(success=False, warnings=[f"Invalid compact date: {e}"])
    
    def _parse_compact_short(self, match: re.Match, preferred_format: str, assume_future: bool) -> DateParseResult:
        """Parse compact short year: DDMMYY or MMDDYY"""
        comp1, comp2, year_2d = match.groups()
        
        full_year = self._expand_two_digit_year(int(year_2d), assume_future)
        
        if preferred_format == 'US':
            month, day = comp1, comp2
        else:
            day, month = comp1, comp2
        
        try:
            date_obj = date(full_year, int(month), int(day))
            return DateParseResult(
                success=True,
                date_iso=date_obj.isoformat(),
                date_obj=date_obj,
                confidence=0.6,
                warnings=[f"Expanded 2-digit year {year_2d} → {full_year}"]
            )
        except ValueError:
            # Try swapping
            try:
                if preferred_format == 'US':
                    day, month = comp1, comp2
                else:
                    month, day = comp1, comp2
                
                date_obj = date(full_year, int(month), int(day))
                return DateParseResult(
                    success=True,
                    date_iso=date_obj.isoformat(),
                    date_obj=date_obj,
                    confidence=0.4,
                    warnings=[
                        f"Expanded 2-digit year {year_2d} → {full_year}",
                        f"Swapped month/day for compact format"
                    ]
                )
            except ValueError as e:
                return DateParseResult(success=False, warnings=[f"Invalid compact short date: {e}"])
    
    def _expand_two_digit_year(self, year_2d: int, assume_future: bool = True) -> int:
        """
        Expand 2-digit year to 4-digit year with intelligent century handling
        
        For bonds, we typically assume future maturity dates.
        """
        current_year = datetime.now().year
        current_century = current_year // 100
        
        if assume_future:
            # Bond logic: assume future dates
            full_year_this_century = current_century * 100 + year_2d
            
            if full_year_this_century <= current_year:
                # Year has passed this century, assume next century
                return (current_century + 1) * 100 + year_2d
            else:
                # Year is in the future this century
                return full_year_this_century
        else:
            # General logic: 50-year window (could be past or future)
            full_year_this_century = current_century * 100 + year_2d
            
            if full_year_this_century - current_year > 50:
                # Too far in future, assume previous century
                return (current_century - 1) * 100 + year_2d
            elif current_year - full_year_this_century > 50:
                # Too far in past, assume next century
                return (current_century + 1) * 100 + year_2d
            else:
                # Within reasonable range
                return full_year_this_century
    
    def _fallback_parse(self, date_str: str) -> DateParseResult:
        """Last resort: try standard datetime parsing"""
        common_formats = [
            '%Y-%m-%d', '%d-%b-%Y', '%m/%d/%Y', '%d/%m/%Y',
            '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S',
            '%d-%m-%Y', '%m-%d-%Y', '%Y/%m/%d'
        ]
        
        for fmt in common_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return DateParseResult(
                    success=True,
                    date_iso=dt.date().isoformat(),
                    date_obj=dt.date(),
                    detected_format=f"fallback_{fmt}",
                    confidence=0.3,
                    warnings=[f"Used fallback format: {fmt}"]
                )
            except ValueError:
                continue
        
        return DateParseResult(
            success=False,
            warnings=[f"No fallback format worked for: {date_str}"]
        )


# Global instance for easy importing
bond_date_parser = BondDateParser()


def parse_bond_date(date_input: Union[str, datetime, date, None],
                   isin: Optional[str] = None,
                   description: Optional[str] = None,
                   country_hint: Optional[str] = None,
                   assume_future: bool = True) -> DateParseResult:
    """
    Convenience function for parsing bond dates
    
    Args:
        date_input: Date to parse (string, datetime, date, or None)
        isin: ISIN code for country format hints
        description: Bond description for additional context
        country_hint: Explicit country code override
        assume_future: For 2-digit years, assume future dates (bond default)
        
    Returns:
        DateParseResult with parsed date and metadata
    """
    return bond_date_parser.parse_date(date_input, isin, description, country_hint, assume_future)


def parse_bond_date_simple(date_input: Union[str, datetime, date, None]) -> Optional[str]:
    """
    Simple wrapper that returns just the ISO date string or None
    
    Args:
        date_input: Date to parse
        
    Returns:
        ISO date string (YYYY-MM-DD) or None if parsing failed
    """
    result = bond_date_parser.parse_date(date_input)
    return result.date_iso if result.success else None


if __name__ == "__main__":
    # Quick test of the parser
    import sys
    
    test_dates = [
        "15/08/52",  # The problematic date
        "T 3 15/08/52",  # With description
        "02/15/25",  # US format
        "15-Feb-2025",  # Month name
        "2025-02-15",  # ISO
        "15022025",  # Compact
    ]
    
    parser = BondDateParser()
    
    for test_date in test_dates:
        print(f"\n📅 Testing: '{test_date}'")
        result = parser.parse_date(test_date, isin="US912810TJ79")
        if result.success:
            print(f"   ✅ Success: {result.date_iso}")
            print(f"   📊 Format: {result.detected_format}")
            print(f"   🎯 Confidence: {result.confidence}")
            if result.warnings:
                print(f"   ⚠️  Warnings: {result.warnings}")
        else:
            print(f"   ❌ Failed: {result.warnings}")
