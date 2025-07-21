#!/usr/bin/env python3
"""
Dual Database Manager for Google Analysis 9
==========================================

Intelligent bond data lookup across multiple databases:
1. Primary: bonds_data.db (static table) - Comprehensive bond data with enrichment
2. Secondary: bloomberg_index.db (all_bonds table) - Bloomberg reference data
3. Fallback: CSV parsing for bonds not in either database

This maximizes bond coverage by checking all available data sources.
"""

import sqlite3
import logging
import os

logger = logging.getLogger(__name__)

class DualDatabaseManager:
    """
    Manages lookup across multiple bond databases with intelligent fallback
    """
    
    def __init__(self, primary_db_path, secondary_db_path=None):
        self.primary_db_path = primary_db_path
        self.secondary_db_path = secondary_db_path
        
        # Verify database availability
        self.primary_available = os.path.exists(primary_db_path)
        self.secondary_available = secondary_db_path and os.path.exists(secondary_db_path)
        
        logger.info(f"🗄️  Dual Database Manager initialized:")
        logger.info(f"   Primary DB: {primary_db_path} {'✅' if self.primary_available else '❌'}")
        if secondary_db_path:
            logger.info(f"   Secondary DB: {secondary_db_path} {'✅' if self.secondary_available else '❌'}")
        else:
            logger.info(f"   Secondary DB: Not configured")
    
    def fetch_bond_data(self, isin, csv_row=None):
        """
        Intelligent bond data lookup with multiple fallback sources
        
        Lookup order:
        1. CSV parsing (if csv_row provided)
        2. Primary database (bonds_data.db/static table)
        3. Secondary database (bloomberg_index.db/all_bonds table)
        4. Return None if not found anywhere
        
        Returns:
            tuple: (coupon, maturity_date, name, country, region, emdm, nfa, esg, msci) or None
        """
        logger.debug(f"🔍 Looking up bond data for ISIN: {isin}")
        
        # 1. Try CSV parsing first (if available)
        if csv_row is not None:
            csv_data = self._parse_bond_data_from_csv(csv_row)
            if csv_data is not None:
                logger.info(f"✅ Found bond data in CSV for {isin}")
                return csv_data
        
        # 2. Try primary database (bonds_data.db/static)
        if self.primary_available:
            primary_data = self._fetch_from_primary_db(isin)
            if primary_data is not None:
                logger.info(f"✅ Found bond data in primary DB for {isin}")
                return primary_data
        
        # 3. Try secondary database (bloomberg_index.db/all_bonds)
        if self.secondary_available:
            secondary_data = self._fetch_from_secondary_db(isin)
            if secondary_data is not None:
                logger.info(f"✅ Found bond data in secondary DB for {isin}")
                return secondary_data
        
        # 4. Not found in any source
        logger.warning(f"❌ Bond data not found for {isin} in any source")
        return None
    
    def _fetch_from_primary_db(self, isin):
        """
        Fetch from primary database (bonds_data.db/static table)
        """
        try:
            conn = sqlite3.connect(self.primary_db_path)
            query = """
            SELECT coupon, maturity, name, country, region, emdm, 
                   nfa_star_rating, esg_country_star_rating, msci_esg_rating 
            FROM static 
            WHERE isin = ?
            """
            cursor = conn.cursor()
            cursor.execute(query, (isin,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                coupon, maturity, name, country, region, emdm, nfa, esg, msci = result
                logger.debug(f"📊 Primary DB data for {isin}: {name}")
                return (coupon, maturity, name, country, region, emdm, nfa, esg, msci)
            
            return None
            
        except Exception as e:
            logger.error(f"Error querying primary database for {isin}: {e}")
            return None
    
    def _fetch_from_secondary_db(self, isin):
        """
        Fetch from secondary database (bloomberg_index.db/all_bonds table)
        """
        try:
            conn = sqlite3.connect(self.secondary_db_path)
            query = """
            SELECT coupon, maturity, description, country 
            FROM all_bonds 
            WHERE isin = ?
            """
            cursor = conn.cursor()
            cursor.execute(query, (isin,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                coupon, maturity, description, country = result
                
                # Map secondary DB format to primary DB format
                # Convert coupon from string to float if needed
                if isinstance(coupon, str):
                    try:
                        coupon = float(coupon) / 100.0  # Convert percentage to decimal
                    except ValueError:
                        coupon = None
                elif isinstance(coupon, (int, float)):
                    coupon = float(coupon) / 100.0  # Ensure decimal format
                
                # Map to expected format
                name = description
                region = self._map_country_to_region(country)
                emdm = self._classify_market(country)
                
                # Secondary DB doesn't have enrichment data
                nfa = None
                esg = None  
                msci = None
                
                logger.debug(f"📊 Secondary DB data for {isin}: {name}")
                return (coupon, maturity, name, country, region, emdm, nfa, esg, msci)
            
            return None
            
        except Exception as e:
            logger.error(f"Error querying secondary database for {isin}: {e}")
            return None
    
    def _parse_bond_data_from_csv(self, row):
        """
        Parse bond information directly from CSV data
        
        Extracts coupon, maturity, and other info from BOND_ENAME field
        """
        import re
        
        bond_name = row.get('BOND_ENAME', '') or row.get('Bond Name', '') or ''
        isin = row.get('BOND_CD', '') or row.get('ISIN', '')
        
        if not bond_name:
            return None
        
        logger.debug(f"🔍 Parsing CSV data for {isin}: {bond_name}")
        
        # Extract coupon from bond name using regex patterns
        coupon = None
        maturity_date = None
        
        # Pattern 1: "CFELEC 6.264 02/15/52" (decimal coupon)
        decimal_match = re.search(r'\s+(\d{1,2}\.\d{1,3})\s+\d{2}/\d{2}/\d{2,4}', bond_name)
        if decimal_match:
            coupon = float(decimal_match.group(1)) / 100.0  # Convert to decimal
        
        # Pattern 2: "T 4 1/4 11/15/34" (Treasury style)
        if not coupon:
            treasury_match = re.search(r'T\s+(\d+)\s+(\d+)/(\d+)', bond_name)
            if treasury_match:
                whole = int(treasury_match.group(1))
                numerator = int(treasury_match.group(2))
                denominator = int(treasury_match.group(3))
                coupon = (whole + (numerator / denominator)) / 100.0  # Convert to decimal
        
        # Pattern 3: "QNBK 1 5/8 09/22/25" (fractional coupon)
        if not coupon:
            fraction_match = re.search(r'(\d+)\s+(\d+)/(\d+)', bond_name)
            if fraction_match:
                whole = int(fraction_match.group(1))
                numerator = int(fraction_match.group(2))
                denominator = int(fraction_match.group(3))
                coupon = (whole + (numerator / denominator)) / 100.0  # Convert to decimal
        
        # Extract maturity date
        date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', bond_name)
        if date_match:
            month = int(date_match.group(1))
            day = int(date_match.group(2))
            year = int(date_match.group(3))
            
            # Handle 2-digit years (assume all are 20xx for bonds)
            if year < 100:
                year += 2000
                
            try:
                maturity_date = f"{year}-{month:02d}-{day:02d}"
            except ValueError:
                logger.warning(f"Invalid date extracted: {month}/{day}/{year}")
        
        # Extract country/issuer information
        country = self._extract_country_from_bond_name(bond_name)
        region = self._map_country_to_region(country)
        emdm = self._classify_market(country)
        
        # Create bond data tuple if essential data extracted
        if coupon is not None and maturity_date is not None:
            parsed_data = (
                coupon,         # Already in decimal format
                maturity_date,  # ISO format date
                bond_name,      # Bond name
                country,        # Country
                region,         # Region  
                emdm,          # Developed/Emerging market
                None,          # NFA rating (not available)
                None,          # ESG rating (not available)
                None           # MSCI rating (not available)
            )
            logger.debug(f"✅ Successfully parsed CSV data for {isin}")
            return parsed_data
        
        logger.debug(f"❌ Failed to extract essential data from CSV for {isin}")
        return None
    
    def _extract_country_from_bond_name(self, bond_name):
        """
        Extract country information from bond name patterns
        """
        # Country mapping based on common issuer patterns
        country_patterns = {
            'QNBK': 'Qatar',
            'ECOPET': 'Colombia', 
            'MEXCAT': 'Mexico',
            'PEMEX': 'Mexico',
            'AMXLMM': 'Mexico',
            'CDEL': 'Chile',
            'BMETR': 'Brazil',
            'CFELEC': 'Chile',
            'T ': 'United States',  # US Treasury
            'UST': 'United States',  # US Treasury
            'COLOM': 'Colombia',
            'MEX': 'Mexico',
            'ARAMCO': 'Saudi Arabia',
            'KSA': 'Saudi Arabia',
            'QATAR': 'Qatar',
            'ISRAEL': 'Israel',
            'PANAMA': 'Panama'
        }
        
        for pattern, country in country_patterns.items():
            if pattern in bond_name.upper():
                return country
        
        return 'Unknown'
    
    def _map_country_to_region(self, country):
        """
        Map country to region
        """
        region_mapping = {
            'United States': 'North America',
            'Mexico': 'Latin America',
            'Colombia': 'Latin America', 
            'Chile': 'Latin America',
            'Brazil': 'Latin America',
            'Panama': 'Latin America',
            'Qatar': 'Middle East',
            'Saudi Arabia': 'Middle East',
            'Israel': 'Middle East',
            'Unknown': 'Unknown'
        }
        
        return region_mapping.get(country, 'Unknown')
    
    def _classify_market(self, country):
        """
        Classify as Developed Market (DM) or Emerging Market (EM)
        """
        developed_markets = ['United States', 'Israel']
        
        if country in developed_markets:
            return 'DM'
        else:
            return 'EM'
    
    def get_database_status(self):
        """
        Get status of both databases
        """
        status = {
            'primary': {
                'path': self.primary_db_path,
                'available': self.primary_available,
                'size_mb': 0
            },
            'secondary': {
                'path': self.secondary_db_path,
                'available': self.secondary_available,
                'size_mb': 0
            }
        }
        
        if self.primary_available:
            status['primary']['size_mb'] = round(os.path.getsize(self.primary_db_path) / (1024*1024), 1)
        
        if self.secondary_available:
            status['secondary']['size_mb'] = round(os.path.getsize(self.secondary_db_path) / (1024*1024), 1)
        
        return status
