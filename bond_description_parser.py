#!/usr/bin/env python3
"""
Smart Bond Description Parser for Google Analysis9 API
====================================================

Intelligently parses bond descriptions like "T 4.1 02/15/28" and predicts
most likely conventions using validated_quantlib_bonds database patterns.

Features:
- Parses common bond description formats
- Predicts "most likely" conventions from database patterns
- Supports intelligent defaults with user overrides
- Integrates with existing google_analysis9 calculation engine
"""

import re
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
import logging
from isin_fallback_handler import get_isin_fallback_conventions
from collections import Counter

# 🎯 BREAKTHROUGH: Import centralized sophisticated date parser - FIXES ALL DATE BUGS!
from centralized_bond_date_parser import parse_bond_date_simple, parse_bond_date

class SmartBondParser:
    """Intelligent bond description parser with convention prediction"""
    
    def __init__(self, db_path: str, validated_db_path: str, bloomberg_db_path: str):
        self.db_path = db_path
        self.validated_db_path = validated_db_path
        self.logger = logging.getLogger(__name__)
        
        # For ticker convention lookup - use bloomberg_index.db
        self.bloomberg_db_path = bloomberg_db_path
        
        # Enhanced parsing patterns for various bond description formats
        self.bond_patterns = [
            # *** NEW INSTITUTIONAL COMMA-SEPARATED PATTERNS ***
            # Institutional format: "GALAXY PIPELINE, 3.25%, 30-Sep-2040"
            (r'^(.+?),\s*([\d\.]+)%?,\s*(\d{1,2})-([A-Za-z]{3})-(\d{4})$', 'institutional'),
            
            # Institutional alternative: "COMPANY NAME, 3.25, 30-Sep-2040" (no %)
            (r'^(.+?),\s*([\d\.]+),\s*(\d{1,2})-([A-Za-z]{3})-(\d{4})$', 'institutional_no_percent'),
            
            # Corporate comma format: "COMPANY, 3.25%, 30/09/2040"
            (r'^(.+?),\s*([\d\.]+)%?,\s*(\d{1,2})\/(\d{1,2})\/(\d{4})$', 'corporate_comma_date'),
            
            # *** EXISTING PATTERNS (unchanged) ***
            # Treasury patterns: "T 4.1 02/15/28", "T 4 1/4 11/15/34"
            (r'^T\s+([\d\s\/\.]+)\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})$', 'treasury'),
            
            # UST patterns: "UST 2.5 05/31/24"
            (r'^UST?\s+([\d\.]+)\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})$', 'treasury'),
            
            # US TREASURY patterns: "US TREASURY N/B, 3%, 15-Aug-2052"
            (r'^US TREASURY.*?,\s*([\d\.]+)%?,\s*(\d{1,2})-([A-Za-z]{3})-(\d{4})$', 'treasury'),
            
            # Corporate patterns: "AAPL 3.25 02/23/26", "MSFT 2.4 08/08/22"
            (r'^([A-Z]{2,6})\s+([\d\.]+)\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})$', 'corporate'),
            
            # Full name patterns: "Apple Inc 3.25% 02/23/26"
            (r'^(.+?)\s+([\d\.]+)%?\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})$', 'corporate'),
            
            # Government patterns: "GERMANY 1.5 08/15/31"
            (r'^([A-Z]{3,})\s+([\d\.]+)\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})$', 'government'),
            
            # Zero coupon: "STRIPS 0 05/15/30"
            (r'^(.+?)\s+(0\.?\d*)\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})$', 'zero_coupon')
        ]
        
        # Default conventions by bond type
        self.default_conventions = {
            'treasury': {
                'day_count': 'ActualActual_Bond',  # Treasury standard - Bond not ISDA
                'business_convention': 'Following',
                'frequency': 'Semiannual',
                'currency': 'USD',
                'country': 'United States'
            },
            'corporate': {
                'day_count': 'Thirty360_BondBasis',
                'business_convention': 'Following', 
                'frequency': 'Semiannual',
                'currency': 'USD',
                'country': 'United States'
            },
            'government': {
                'day_count': 'ActualActual_ISDA',
                'business_convention': 'Following',
                'frequency': 'Annual',
                'currency': 'USD',
                'country': 'Unknown'
            },
            'institutional': {
                'day_count': 'Thirty360_BondBasis',
                'business_convention': 'Following',
                'frequency': 'Semiannual',
                'currency': 'USD',
                'country': 'International'
            },
            'zero_coupon': {
                'day_count': 'ActualActual_ISDA',
                'business_convention': 'Following',
                'frequency': 'Zero',
                'currency': 'USD',
                'country': 'United States'
            }
        }
    
    def extract_ticker_from_parsed_bond(self, bond_data: Dict) -> Optional[str]:
        """Extract ticker from parsed bond data for ticker_convention_preferences lookup"""
        if not bond_data:
            return None
            
        # 🔧 FIX: Handle potential numeric values
        issuer = str(bond_data.get('issuer', '')).strip().upper()
        bond_type = bond_data.get('bond_type', '')
        
        # ENHANCED: Map issuers to standard tickers used in ticker_convention_preferences
        issuer_to_ticker_map = {
            # Treasury bonds
            'US TREASURY': 'T',
            'TREASURY': 'T', 
            'UST': 'T',
            'US TREASURY N/B': 'T',
            
            # Corporate bonds from your test data
            'GALAXY PIPELINE': 'CORP',
            'ABU DHABI CRUDE': 'CORP',
            'SAUDI ARAB OIL': 'CORP', 
            'EMPRESA METRO': 'CORP',
            'CODELCO INC': 'CORP',
            'COMISION FEDERAL': 'CORP',
            'COLOMBIA REP OF': 'CORP',
            'ECOPETROL SA': 'CORP',
            'EMPRESA NACIONAL': 'CORP',
            'GREENSAIF PIPELI': 'CORP',
            'STATE OF ISRAEL': 'CORP',
            'SAUDI INT BOND': 'CORP',
            'KAZMUNAYGAS NAT': 'CORP',
            
            # Tech companies (keep existing)
            'APPLE INC': 'AAPL',
            'MICROSOFT': 'MSFT',
            'TESLA': 'TSLA',
            'AMAZON': 'AMZN',
            'GOOGLE': 'GOOGL',
            'META': 'META',
            'NETFLIX': 'NFLX',
            'NVIDIA': 'NVDA'
        }
        
        # Direct issuer mapping
        if issuer in issuer_to_ticker_map:
            return issuer_to_ticker_map[issuer]
        
        # For treasury bonds, always use 'T'
        if bond_type == 'treasury' or 'TREASURY' in issuer or issuer == 'T':
            return 'T'
        
        # ENHANCED: Try partial matching for corporate issuers
        for known_issuer, ticker in issuer_to_ticker_map.items():
            if known_issuer in issuer or issuer in known_issuer:
                self.logger.info(f"🎯 PARTIAL MATCH: {issuer} -> {ticker} via {known_issuer}")
                return ticker
        
        # ENHANCED: Extract company name patterns for known bond issuers
        # Common patterns in your bond data
        company_patterns = {
            'GALAXY': 'GALA',
            'ABU DHABI': 'ABU', 
            'SAUDI': 'SAUD',
            'EMPRESA': 'EMPR',
            'CODELCO': 'CODE',
            'COMISION': 'COMI',
            'COLOMBIA': 'COLO',
            'ECOPETROL': 'ECOP',
            'GREENSAIF': 'GREE',
            'ISRAEL': 'STAT',
            'KAZMUNAYGAS': 'KAZM',
            'PEMEX': 'PEMEX',
            'MEXICO': 'MEX',
            'QATAR': 'QATAR',
            'CHILE': 'CHILE'
        }
        
        for pattern, mapped_ticker in company_patterns.items():
            if pattern in issuer:
                self.logger.info(f"🎯 COMPANY PATTERN MATCH: {issuer} -> {mapped_ticker} via {pattern}")
                return mapped_ticker
        
        # ENHANCED: For any unknown corporate bond, use generic 'CORP' ticker
        if bond_type == 'corporate':
            self.logger.info(f"🎯 UNKNOWN CORPORATE: {issuer} -> using generic 'CORP' ticker")
            return 'CORP'
        
        # ENHANCED: Last resort - create synthetic ticker from first word
        words = issuer.split()
        if words:
            synthetic_ticker = words[0][:4].upper()  # First 4 chars of first word
            self.logger.info(f"🎯 SYNTHETIC TICKER: {issuer} -> {synthetic_ticker}")
            return synthetic_ticker
        
        return 'CORP'  # Ultimate fallback
    
    def lookup_ticker_conventions(self, ticker: str) -> Optional[Dict]:
        """Lookup ticker-specific conventions from ticker_convention_preferences table"""
        if not ticker:
            return None
            
        try:
            conn = sqlite3.connect(self.bloomberg_db_path)
            cursor = conn.cursor()
            
            # Query ticker_convention_preferences table
            query = """
                SELECT day_count_convention, business_convention, payment_frequency, frequency_count
                FROM ticker_convention_preferences 
                WHERE ticker = ?
            """
            
            cursor.execute(query, (ticker,))
            result = cursor.fetchone()
            
            if result:
                day_count, business_conv, frequency, count = result
                self.logger.info(f"✅ Found ticker conventions for {ticker}: {day_count}|{business_conv}|{frequency} (count: {count})")
                
                conn.close()
                return {
                    'day_count': day_count,
                    'business_convention': business_conv,
                    'frequency': frequency,
                    'prediction_confidence': 'very_high',
                    'based_on_ticker_preferences': True,
                    'ticker_frequency_count': count,
                    'source': 'ticker_convention_preferences'
                }
            else:
                self.logger.info(f"⚠️ No ticker conventions found for {ticker}, trying fallback...")
                conn.close()
                
                # Try fallback tickers
                fallback_tickers = ['CORP', 'GOVERNMENT', 'MUNICIPAL']
                for fallback_ticker in fallback_tickers:
                    if fallback_ticker != ticker:  # Don't retry the same ticker
                        self.logger.info(f"🔄 Trying fallback ticker: {fallback_ticker}")
                        fallback_result = self.lookup_ticker_conventions(fallback_ticker)
                        if fallback_result:
                            fallback_result['source'] = f'fallback_from_{ticker}_to_{fallback_ticker}'
                            fallback_result['prediction_confidence'] = 'medium'
                            return fallback_result
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to lookup ticker conventions for {ticker}: {e}")
            return None
    
    def parse_fractional_coupon(self, coupon_str: str) -> float:
        """Convert fractional coupon notation to decimal"""
        # 🔧 FIX: Handle numeric inputs
        coupon_str = str(coupon_str).strip()
        
        # Handle fractions like "4 1/4" -> 4.25
        if ' ' in coupon_str and '/' in coupon_str:
            parts = coupon_str.split(' ')
            whole = float(parts[0])
            
            # Parse fraction
            if '/' in parts[1]:
                num, den = parts[1].split('/')
                fraction = float(num) / float(den)
                return whole + fraction
        
        # Handle simple decimals like "2.5"
        elif '.' in coupon_str:
            return float(coupon_str)
        
        # Handle whole numbers
        else:
            return float(coupon_str)
    
    def parse_maturity_date(self, month: str, day: str, year: str) -> str:
        """
        Convert date components to ISO format using centralized sophisticated date parser
        
        🎯 BREAKTHROUGH: Now uses centralized parser - eliminates all date parsing bugs!
        """
        # Create date string in format that our parser can understand
        date_str = f"{month}/{day}/{year}"
        
        # Use our sophisticated centralized parser
        result = parse_bond_date_simple(date_str)
        
        if result:
            self.logger.debug(f"✅ Centralized parser: '{date_str}' → '{result}'")
            return result
        else:
            # Fallback to basic logic (shouldn't happen with our robust parser)
            self.logger.warning(f"❌ Centralized parser failed for '{date_str}', using fallback")
            return self._fallback_date_parse(month, day, year)
    
    def _fallback_date_parse(self, month: str, day: str, year: str) -> str:
        """Fallback date parsing (legacy method for emergencies only)"""
        # Ensure all inputs are strings (handle both string and int inputs)
        month = str(month)
        day = str(day)  
        year = str(year)
        
        if len(year) == 2:
            year_int = int(year)
            current_year = datetime.now().year
            current_century = current_year // 100
            
            # For bonds, assume future dates
            # If year is in the past this century, assume next century
            full_year_this_century = current_century * 100 + year_int
            
            if full_year_this_century <= current_year:
                # Year has passed, assume next century (e.g., 61 -> 2061, not 1961)
                year = str((current_century + 1) * 100 + year_int)
            else:
                # Year is in the future this century
                year = str(full_year_this_century)
        
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    def convert_month_name_to_number(self, month_name: str) -> str:
        """Convert month name (e.g., 'Sep') to month number (e.g., '09')"""
        month_map = {
            'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
            'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
            'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
        }
        return month_map.get(month_name.upper(), '01')
    
    def parse_bond_description(self, description: str) -> Optional[Dict]:
        """Parse bond description and extract components"""
        if not description:
            return None
        
        # 🔧 FIX: Handle numeric inputs from Google Sheets
        if isinstance(description, (int, float)):
            description = str(description)
        
        description = description.strip().upper()
        
        for pattern, bond_type in self.bond_patterns:
            match = re.match(pattern, description)
            if match:
                groups = match.groups()
                
                try:
                    # *** NEW INSTITUTIONAL PATTERNS ***
                    if bond_type == 'institutional' or bond_type == 'institutional_no_percent':
                        # Format: "GALAXY PIPELINE, 3.25%, 30-Sep-2040" or "COMPANY, 3.25, 30-Sep-2040"
                        issuer, coupon_str, day, month_name, year = groups
                        coupon = float(coupon_str)
                        month = self.convert_month_name_to_number(month_name)
                        maturity = self.parse_maturity_date(month, day, year)
                        
                        # Determine bond type based on issuer
                        if any(gov_keyword in issuer.upper() for gov_keyword in ['REP OF', 'STATE OF', 'REPUBLIC', 'GOVERNMENT']):
                            bond_type = 'government'
                        else:
                            bond_type = 'corporate'
                    
                    elif bond_type == 'corporate_comma_date':
                        # Format: "COMPANY, 3.25%, 30/09/2040"
                        issuer, coupon_str, day, month, year = groups
                        coupon = float(coupon_str)
                        maturity = self.parse_maturity_date(month, day, year)
                    
                    # *** EXISTING PATTERNS (unchanged) ***
                    elif bond_type == 'treasury':
                        if len(groups) == 4:
                            # Handle both old "T 4.1 02/15/28" and new "US TREASURY N/B, 3%, 15-Aug-2052" formats
                            if groups[2].isalpha():  # New format: month is a name (e.g., "Aug")
                                coupon_str, day, month_name, year = groups
                                coupon = float(coupon_str)
                                month = self.convert_month_name_to_number(month_name)
                                issuer = "US Treasury"
                                # For Treasury patterns, pass month, day, year in correct order
                                maturity = self.parse_maturity_date(month, day, year)
                            else:  # Old format: month is a number
                                coupon_str, month, day, year = groups  # ✅ FIXED: For Treasury format "T 4.1 02/15/28" = MM/DD/YY
                                coupon = self.parse_fractional_coupon(coupon_str)
                                issuer = "US Treasury"
                                maturity = self.parse_maturity_date(month, day, year)
                        else:
                            continue
                    
                    elif bond_type == 'corporate':
                        if len(groups) == 4:  # AAPL 3.25 02/23/26 format
                            issuer, coupon_str, month, day, year = groups  # ✅ KEEPING: MM/DD/YY format for corporates
                            coupon = float(coupon_str)
                            maturity = self.parse_maturity_date(month, day, year)
                        elif len(groups) == 5:  # Full name format
                            issuer, coupon_str, month, day, year = groups  # ✅ KEEPING: MM/DD/YY format for corporates
                            coupon = float(coupon_str)
                            maturity = self.parse_maturity_date(month, day, year)
                        else:
                            continue
                    
                    elif bond_type == 'government':
                        issuer, coupon_str, month, day, year = groups  # ✅ CORRECTED: MM/DD/YY format
                        coupon = float(coupon_str)
                        maturity = self.parse_maturity_date(month, day, year)
                    
                    elif bond_type == 'zero_coupon':
                        issuer, coupon_str, month, day, year = groups  # ✅ CORRECTED: MM/DD/YY format
                        coupon = float(coupon_str)
                        maturity = self.parse_maturity_date(month, day, year)
                    
                    return {
                        'issuer': issuer,
                        'coupon': coupon,
                        'maturity': maturity,
                        'bond_type': bond_type,
                        'parsed_successfully': True
                    }
                
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"Failed to parse bond description {description}: {e}")
                    continue
        
        # If no pattern matches, try to extract components manually
        return self.fallback_parse(description)
    
    def fallback_parse(self, description: str) -> Optional[Dict]:
        """Fallback parsing for complex descriptions"""
        # Look for coupon rate (number followed by optional %)
        coupon_match = re.search(r'(\d+\.?\d*)\s*%?', description)
        
        # Look for maturity date (MM/DD/YY or MM/DD/YYYY)
        date_match = re.search(r'(\d{1,2})\/(\d{1,2})\/(\d{2,4})', description)
        
        if coupon_match and date_match:
            try:
                coupon = float(coupon_match.group(1))
                month, day, year = date_match.groups()  # ✅ MM/DD/YY format is correct here
                maturity = self.parse_maturity_date(month, day, year)
                
                # Extract issuer (everything before the coupon)
                coupon_pos = coupon_match.start()
                issuer = description[:coupon_pos].strip()
                
                return {
                    'issuer': issuer if issuer else 'Unknown',
                    'coupon': coupon,
                    'maturity': maturity,
                    'bond_type': 'generic',
                    'parsed_successfully': True,
                    'fallback_parsing': True
                }
            except:
                pass
        
        return None
    
    def predict_most_likely_conventions(self, bond_data: Dict) -> Dict:
        """Predict conventions using ticker_convention_preferences table FIRST, then fallback"""
        try:
            # STEP 1: Try ticker-specific conventions (NEW!)
            ticker = self.extract_ticker_from_parsed_bond(bond_data)
            if ticker:
                ticker_conventions = self.lookup_ticker_conventions(ticker)
                if ticker_conventions:
                    self.logger.info(f"🎯 Using ticker-specific conventions for {ticker}")
                    return ticker_conventions
                else:
                    self.logger.info(f"📈 No ticker conventions found for {ticker}, falling back to general patterns")
            
            # STEP 2: Fallback to validated database patterns (existing logic)
            import os
            if not os.path.exists(self.validated_db_path):
                self.logger.warning(f"Validated database not found: {self.validated_db_path}")
                return self._get_default_conventions(bond_data)
            
            conn = sqlite3.connect(self.validated_db_path)
            cursor = conn.cursor()
            
            # Get convention statistics from validated bonds
            query = """
                SELECT fixed_day_count, fixed_business_convention, fixed_frequency, 
                       COUNT(*) as count
                FROM validated_quantlib_bonds 
                WHERE pass_status = 'PASS'
                GROUP BY fixed_day_count, fixed_business_convention, fixed_frequency
                ORDER BY count DESC
            """
            
            cursor.execute(query)
            convention_stats = cursor.fetchall()
            
            # If we have validated data, use the most common PASSING combination
            if convention_stats:
                best_combo = convention_stats[0]
                predicted_conventions = {
                    'day_count': best_combo[0],
                    'business_convention': best_combo[1], 
                    'frequency': best_combo[2],
                    'prediction_confidence': 'high',
                    'based_on_validated_data': True,
                    'validated_bonds_count': best_combo[3],
                    'source': 'validated_database_fallback'
                }
            else:
                # Fallback to defaults based on bond type
                predicted_conventions = self._get_default_conventions(bond_data)
            
            # Treasury override - always use treasury conventions for treasuries
            if bond_data.get('bond_type') == 'treasury':
                predicted_conventions.update({
                    'day_count': 'ActualActual_Bond',  # Treasury standard - Bond not ISDA
                    'business_convention': 'Following',  # ✅ CORRECT: US Treasuries move payment dates to business days
                    'frequency': 'Semiannual',
                    'prediction_confidence': 'very_high',
                    'treasury_override': True,
                    'source': 'treasury_override'
                })
            
            conn.close()
            return predicted_conventions
            
        except Exception as e:
            self.logger.error(f"Failed to predict conventions: {e}")
            return self._get_default_conventions(bond_data)
    
    def _get_default_conventions(self, bond_data: Dict) -> Dict:
        """Get default conventions based on bond type"""
        bond_type = bond_data.get('bond_type', 'corporate')
        defaults = self.default_conventions.get(bond_type, self.default_conventions['corporate'])
        
        return {
            'day_count': defaults['day_count'],
            'business_convention': defaults['business_convention'],
            'frequency': defaults['frequency'],
            'prediction_confidence': 'medium',
            'based_on_validated_data': False,
            'fallback_reason': 'using_defaults'
        }
    
    def calculate_accrued_interest(self, bond_data: Dict, conventions: Dict, 
                                 settlement_date: str = None, price: float = 100.0) -> Dict:
        """Calculate using TICKER-FIRST approach - no database dependency"""
        try:
            self.logger.info(f"🎯 TICKER-FIRST APPROACH: Using ticker conventions WITHOUT database dependency")
            from google_analysis10 import process_bonds_with_weightings
            import pandas as pd
            
            if not settlement_date:
                today = datetime.now()
                first_day_current_month = today.replace(day=1)
                last_day_previous_month = first_day_current_month - timedelta(days=1)
                settlement_date = last_day_previous_month.strftime("%Y-%m-%d")
            
            # STEP 1: Extract ticker (this is the KEY to everything)
            ticker = self.extract_ticker_from_parsed_bond(bond_data)
            if not ticker:
                self.logger.warning(f"⚠️ No specific ticker extracted, using generic 'CORP' fallback")
                ticker = 'CORP'  # Use generic corporate ticker as fallback
            
            self.logger.info(f"🎯 TICKER EXTRACTED: {ticker}")
            
            # STEP 2: ONLY use ISIN if explicitly provided AND we want database enrichment
            real_isin = bond_data.get('isin')
            if real_isin:
                self.logger.info(f"🎯 ISIN PROVIDED: {real_isin} - trying database lookup first")
                
                portfolio_data = {
                    "data": [
                        {
                            "BOND_CD": real_isin,
                            "CLOSING PRICE": price,
                            "WEIGHTING": 100.0,
                            "Inventory Date": settlement_date.replace("-", "/")
                        }
                    ]
                }
                
                try:
                    # Use portfolio system for ISIN lookup
                    results = process_bonds_with_weightings(
                        portfolio_data, 
                        self.db_path, 
                        validated_db_path=self.validated_db_path
                    )
                    
                    if len(results) > 0:
                        result = results.iloc[0]
                        
                        if pd.isna(result.get('error')) and result.get('yield') is not None:
                            yield_val = float(result.get('yield', 0))
                            duration_val = float(result.get('duration', 0))
                            accrued_val = float(result.get('accrued_interest', 0))
                            
                            self.logger.info(f"✅ ISIN DATABASE SUCCESS: yield={yield_val}%, duration={duration_val}, accrued={accrued_val}")
                            
                            return {
                                'accrued_interest': accrued_val,
                                'yield_to_maturity': yield_val,
                                'duration': duration_val,
                                'calculation_successful': True,
                                'calculation_details': 'Database lookup via ISIN',
                                'processing_method': 'isin_database_lookup',
                                'bond_cd_used': real_isin
                            }
                        else:
                            self.logger.warning(f"⚠️ ISIN lookup failed, falling back to ticker conventions")
                    else:
                        self.logger.warning(f"⚠️ No results from ISIN lookup, falling back to ticker conventions")
                        
                except Exception as isin_error:
                    self.logger.warning(f"⚠️ ISIN lookup error: {isin_error}, falling back to ticker conventions")
            
            # STEP 3: CORE APPROACH - Use ticker conventions + synthetic portfolio approach
            self.logger.info(f"🎯 USING TICKER CONVENTIONS: {ticker} with conventions: {conventions}")
            
            # Create SYNTHETIC bond identifier that encodes the parsed data
            synthetic_bond_cd = f"PARSED_{ticker}_{bond_data['coupon']}_{bond_data['maturity'].replace('-', '')}"
            
            self.logger.info(f"🎯 SYNTHETIC BOND_CD: {synthetic_bond_cd}")
            
            # Create portfolio data structure for the synthetic bond
            portfolio_data = {
                "data": [
                    {
                        "BOND_CD": synthetic_bond_cd,
                        "CLOSING PRICE": price,
                        "WEIGHTING": 100.0,
                        "Inventory Date": settlement_date.replace("-", "/"),
                        
                        # INJECT PARSED DATA so portfolio system can use it
                        "_parsed_data": {
                            "issuer": bond_data.get('issuer'),
                            "coupon": bond_data.get('coupon'),
                            "maturity": bond_data.get('maturity'),
                            "bond_type": bond_data.get('bond_type'),
                            "ticker": ticker
                        },
                        
                        # INJECT TICKER CONVENTIONS so portfolio system can use them
                        "_ticker_conventions": {
                            "day_count": conventions.get('day_count'),
                            "business_convention": conventions.get('business_convention'),
                            "frequency": conventions.get('frequency'),
                            "source": conventions.get('source', 'ticker_convention_preferences')
                        }
                    }
                ]
            }
            
            self.logger.info(f"🔄 ROUTING through process_bonds_with_weightings() with PARSED DATA")
            
            # ROUTE THROUGH SAME PORTFOLIO SYSTEM
            results = process_bonds_with_weightings(
                portfolio_data, 
                self.db_path, 
                validated_db_path=self.validated_db_path
            )
            
            if len(results) > 0:
                result = results.iloc[0]
                
                if pd.isna(result.get('error')) and result.get('yield') is not None:
                    yield_val = float(result.get('yield', 0))
                    duration_val = float(result.get('duration', 0))
                    accrued_val = float(result.get('accrued_interest', 0))
                    
                    self.logger.info(f"✅ TICKER CONVENTION SUCCESS: yield={yield_val}%, duration={duration_val}, accrued={accrued_val}")
                    
                    return {
                        'accrued_interest': accrued_val,
                        'yield_to_maturity': yield_val,
                        'duration': duration_val,
                        'calculation_successful': True,
                        'calculation_details': f'Ticker conventions via portfolio system',
                        'processing_method': 'ticker_conventions_portfolio',
                        'ticker_used': ticker,
                        'conventions_used': conventions,
                        'synthetic_bond_cd': synthetic_bond_cd
                    }
                else:
                    error_msg = result.get('error', 'Unknown portfolio calculation error')
                    self.logger.error(f"❌ PORTFOLIO CALCULATION FAILED: {error_msg}")
                    return {
                        'accrued_interest': 0,
                        'yield_to_maturity': 0,
                        'duration': 0,
                        'calculation_successful': False,
                        'error': f"Portfolio calculation failed: {error_msg}",
                        'processing_method': 'portfolio_calculation_error'
                    }
            else:
                self.logger.error(f"❌ NO RESULTS from portfolio system")
                return {
                    'accrued_interest': 0,
                    'yield_to_maturity': 0,
                    'duration': 0,
                    'calculation_successful': False,
                    'error': 'No results from portfolio calculation system',
                    'processing_method': 'portfolio_no_results'
                }
            
        except Exception as e:
            self.logger.error(f"❌ TICKER-FIRST APPROACH FAILED: {e}")
            return {
                'accrued_interest': 0,
                'yield_to_maturity': 0,
                'duration': 0,
                'calculation_successful': False,
                'error': f"Ticker-first calculation error: {str(e)}",
                'processing_method': 'ticker_first_error'
            }


# Test function
def test_parser():
    """Test the parser with sample descriptions"""
    # Corrected to include the bloomberg_db_path for standalone testing
    parser = SmartBondParser("./../bonds_data.db", "./../validated_quantlib_bonds.db", "./../bloomberg_index.db")
    
    test_descriptions = [
        "T 4.1 02/15/28",
        "UST 2.5 05/31/24", 
        "AAPL 3.25 02/23/26",
        "Apple Inc 3.25% 02/23/26",
        "GERMANY 1.5 08/15/31"
    ]
    
    print("🧪 Testing Smart Bond Parser")
    print("=" * 50)
    
    for desc in test_descriptions:
        print(f"\n📋 Testing: {desc}")
        parsed = parser.parse_bond_description(desc)
        if parsed:
            conventions = parser.predict_most_likely_conventions(parsed)
            print(f"   ✅ Parsed: {parsed['issuer']} {parsed['coupon']}% {parsed['maturity']}")
            print(f"   🎯 Conventions: {conventions['day_count']}|{conventions['business_convention']}|{conventions['frequency']}")
            print(f"   📊 Confidence: {conventions['prediction_confidence']}")
        else:
            print(f"   ❌ Failed to parse")

if __name__ == "__main__":
    test_parser()
