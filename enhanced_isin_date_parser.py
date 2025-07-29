#!/usr/bin/env python3
"""
Enhanced Bond Description Parser with ISIN-Based Date Format Detection
=====================================================================

Intelligently determines date format (MM/DD/YY vs DD/MM/YY) based on ISIN country codes.
Replaces the naive date parsing with sophisticated regional format detection.
"""

import re
from datetime import datetime
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class EnhancedISINDateParser:
    """Enhanced parser that uses ISIN country codes to determine date formats"""
    
    def __init__(self):
        # ISIN country codes that use MM/DD/YY format (US format)
        self.us_format_countries = {
            'US',  # United States
            'CA',  # Canada (often uses US format for bonds)
            'MX',  # Mexico (in USD denominated bonds)
        }
        
        # ISIN country codes that use DD/MM/YY format (European format)  
        self.european_format_countries = {
            'GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'IE', 'PT', 'FI',  # Europe
            'XS',  # Eurobond/International (typically European format)
            'LU', 'CH', 'NO', 'SE', 'DK',  # Other European
            'AU', 'NZ',  # Australia/New Zealand (DD/MM format)
            'HK', 'SG',  # Hong Kong/Singapore (DD/MM format)
        }
        
        # Enhanced bond patterns with ISIN context
        self.bond_patterns = [
            # Treasury patterns: "T 4.1 02/15/28"
            (r'^T\s+([\d\s\/\.]+)\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})$', 'treasury'),
            # Corporate patterns: "AAPL 3.25 02/23/26"
            (r'^([A-Z\s]+)\s+([\d\.]+)\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})$', 'corporate'),
            # International patterns: "COMPANY, 3.25%, 30-Sep-2040"
            (r'^(.+?),\s*([\d\.]+)%?,\s*(\d{1,2})-([A-Za-z]{3})-(\d{4})$', 'international'),
        ]
    
    def extract_isin_country_code(self, isin: str) -> Optional[str]:
        """Extract country code from ISIN"""
        if not isin or len(isin) < 2:
            return None
        return isin[:2].upper()
    
    def determine_date_format(self, isin: str = None, description: str = None) -> str:
        """
        Determine date format based on ISIN country code and description context
        
        Returns:
            'US' for MM/DD/YY format
            'EU' for DD/MM/YY format  
        """
        # SPECIAL CASE: Treasury date format detection (NEW!)
        if description and 'T ' in description.upper():
            # Extract date components from Treasury description
            treasury_match = re.search(r'T\s+[\d\s\/\.]+\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})', description.upper())
            if treasury_match:
                comp1, comp2, year = treasury_match.groups()
                comp1_int, comp2_int = int(comp1), int(comp2)
                
                # If first component > 12, it must be DD/MM format
                if comp1_int > 12:
                    logger.info(f"🏛️ Treasury European date format detected: {comp1}/{comp2} (day > 12)")
                    return 'EU'
                # If second component > 12, it must be MM/DD format  
                elif comp2_int > 12:
                    logger.info(f"🏛️ Treasury US date format detected: {comp1}/{comp2} (month > 12)")
                    return 'US'
                # If both <= 12, use European format for Treasury (conservative)
                else:
                    logger.info(f"🏛️ Treasury ambiguous date, defaulting to European format: {comp1}/{comp2}")
                    return 'EU'
        
        # Priority 1: ISIN country code
        if isin:
            country_code = self.extract_isin_country_code(isin)
            if country_code in self.us_format_countries:
                logger.info(f"🇺🇸 US date format detected for ISIN {isin} (country: {country_code})")
                return 'US'
            elif country_code in self.european_format_countries:
                logger.info(f"🇪🇺 European date format detected for ISIN {isin} (country: {country_code})")
                return 'EU'
        
        # Priority 2: Description context (UPDATED - removed Treasury from US indicators)
        if description:
            description_upper = description.upper()
            # US indicators (removed Treasury patterns)
            if any(indicator in description_upper for indicator in ['UST', 'US TREASURY']):
                logger.info(f"🇺🇸 US date format detected from description context: {description}")
                return 'US'
            # European indicators  
            if any(indicator in description_upper for indicator in ['EUR', 'GBP', 'EUROBOND', 'LONDON']):
                logger.info(f"🇪🇺 European date format detected from description context: {description}")
                return 'EU'
        
        # Default: Use US format (safer for most bond data)
        logger.info(f"🌐 Default US date format applied (no clear indicators)")
        return 'US'
    
    def parse_date_with_format(self, month: str, day: str, year: str, date_format: str, isin: str = None) -> str:
        """
        Parse date components using the appropriate format
        
        Args:
            month: Month component (could be MM or DD depending on format)
            day: Day component (could be DD or MM depending on format)  
            year: Year component
            date_format: 'US' for MM/DD/YY or 'EU' for DD/MM/YY
            isin: ISIN for logging context
        """
        try:
            if date_format == 'US':
                # MM/DD/YY format (month, day, year)
                parsed_month = str(month).zfill(2)
                parsed_day = str(day).zfill(2)
            else:
                # DD/MM/YY format (day, month, year) - swap the components
                parsed_month = str(day).zfill(2)
                parsed_day = str(month).zfill(2)
            
            # Handle 2-digit years
            if len(str(year)) == 2:
                year_int = int(year)
                current_year = datetime.now().year
                current_century = current_year // 100
                
                # For bonds, assume future dates
                full_year_this_century = current_century * 100 + year_int
                if full_year_this_century < current_year:
                    # Year has passed, assume next century
                    parsed_year = str((current_century + 1) * 100 + year_int)
                else:
                    parsed_year = str(full_year_this_century)
            else:
                parsed_year = str(year)
            
            result = f"{parsed_year}-{parsed_month}-{parsed_day}"
            
            # Validate the date
            datetime.strptime(result, '%Y-%m-%d')
            
            logger.info(f"✅ Date parsed successfully: {month}/{day}/{year} → {result} (format: {date_format}, ISIN: {isin})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Date parsing failed: {month}/{day}/{year} with format {date_format} (ISIN: {isin}): {e}")
            raise
    
    def parse_bond_description_enhanced(self, description: str, isin: str = None) -> Optional[Dict]:
        """
        Enhanced bond description parsing with intelligent date format detection
        
        Args:
            description: Bond description to parse
            isin: Optional ISIN for intelligent format detection
            
        Returns:
            Dict with parsed bond information including intelligently formatted dates
        """
        if not description:
            return None
        
        description = description.strip().upper()
        
        # Determine the appropriate date format
        date_format = self.determine_date_format(isin, description)
        
        # Try each pattern
        for pattern, bond_type in self.bond_patterns:
            match = re.match(pattern, description)
            if match:
                groups = match.groups()
                logger.info(f"🎯 Pattern matched: {bond_type} for '{description}'")
                
                try:
                    if bond_type == 'treasury':
                        if len(groups) == 4:
                            coupon_str, comp1, comp2, year = groups
                            coupon = self._parse_fractional_coupon(coupon_str)
                            
                            # Use intelligent date format detection
                            # Fix parameter order based on detected format
                            if date_format == 'EU':
                                # For EU format (DD/MM/YY): comp1=day, comp2=month
                                maturity = self.parse_date_with_format(comp2, comp1, year, date_format, isin)
                            else:
                                # For US format (MM/DD/YY): comp1=month, comp2=day  
                                maturity = self.parse_date_with_format(comp1, comp2, year, date_format, isin)
                            
                            return {
                                'issuer': 'US Treasury',
                                'coupon': coupon,
                                'maturity': maturity,
                                'bond_type': 'government',
                                'currency': 'USD',
                                'date_format_used': date_format,
                                'isin': isin,
                                'description_input': description
                            }
                    
                    elif bond_type == 'corporate':
                        if len(groups) == 5:
                            issuer, coupon_str, comp1, comp2, year = groups
                            coupon = float(coupon_str)
                            
                            # Use intelligent date format detection
                            # Fix parameter order based on detected format
                            if date_format == 'EU':
                                # For EU format (DD/MM/YY): comp1=day, comp2=month
                                maturity = self.parse_date_with_format(comp2, comp1, year, date_format, isin)
                            else:
                                # For US format (MM/DD/YY): comp1=month, comp2=day  
                                maturity = self.parse_date_with_format(comp1, comp2, year, date_format, isin)
                            
                            return {
                                'issuer': issuer.strip(),
                                'coupon': coupon,
                                'maturity': maturity,
                                'bond_type': 'corporate',
                                'currency': 'USD',  # Could be enhanced with currency detection
                                'date_format_used': date_format,
                                'isin': isin,
                                'description_input': description
                            }
                    
                    elif bond_type == 'international':
                        if len(groups) == 5:
                            issuer, coupon_str, day, month_name, year = groups
                            coupon = float(coupon_str)
                            month = self._convert_month_name_to_number(month_name)
                            
                            # International bonds with month names don't need format detection
                            maturity = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            
                            return {
                                'issuer': issuer.strip(),
                                'coupon': coupon,
                                'maturity': maturity,
                                'bond_type': 'corporate',
                                'currency': 'USD',  # Could be enhanced
                                'date_format_used': 'international',
                                'isin': isin,
                                'description_input': description
                            }
                
                except Exception as e:
                    logger.error(f"❌ Error parsing {bond_type} bond '{description}': {e}")
                    continue
        
        logger.warning(f"⚠️ No pattern matched for: {description}")
        return None
    
    def _parse_fractional_coupon(self, coupon_str: str) -> float:
        """Parse fractional coupon notation like '4 1/4' -> 4.25"""
        coupon_str = coupon_str.strip()
        
        if ' ' in coupon_str and '/' in coupon_str:
            parts = coupon_str.split(' ')
            whole = float(parts[0])
            if '/' in parts[1]:
                num, den = parts[1].split('/')
                fraction = float(num) / float(den)
                return whole + fraction
        elif '.' in coupon_str:
            return float(coupon_str)
        else:
            return float(coupon_str)
    
    def _convert_month_name_to_number(self, month_name: str) -> str:
        """Convert month name to number"""
        month_map = {
            'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
            'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
            'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
        }
        return month_map.get(month_name.upper()[:3], '01')


# Integration wrapper for existing codebase
class SmartBondParserEnhanced:
    """Enhanced wrapper that integrates ISIN date format detection"""
    
    def __init__(self, db_path: str, validated_db_path: str, bloomberg_db_path: str):
        self.db_path = db_path
        self.validated_db_path = validated_db_path
        self.bloomberg_db_path = bloomberg_db_path
        self.enhanced_parser = EnhancedISINDateParser()
        self.logger = logging.getLogger(__name__)
    
    def parse_bond_description(self, description: str, isin: str = None) -> Optional[Dict]:
        """
        Enhanced parsing with ISIN context
        
        Args:
            description: Bond description
            isin: Optional ISIN for intelligent date format detection
        """
        return self.enhanced_parser.parse_bond_description_enhanced(description, isin)
