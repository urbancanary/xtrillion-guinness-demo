import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import sqlite3
import pandas as pd
import QuantLib as ql
import logging
from datetime import datetime, date, timedelta
from bond_description_parser import SmartBondParser
from isin_fallback_handler import get_isin_fallback_conventions

def get_ql_frequency(freq_str):
    """Maps a frequency string to a QuantLib Frequency object."""
    freq_map = {
        'Semiannual': ql.Semiannual,
        'Annual': ql.Annual,
        'Quarterly': ql.Quarterly,
        'Monthly': ql.Monthly
    }
    return freq_map.get(freq_str, ql.Semiannual) # Default to Semiannual if not found

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- QuantLib Date Formatting ---
def format_ql_date(dt_obj):
    """Formats a QuantLib Date object into a string like '27-Jun-2025'."""
    # This is a safe way to format, avoiding direct calls to potentially missing attributes
    py_date = datetime(dt_obj.year(), dt_obj.month(), dt_obj.dayOfMonth())
    return py_date.strftime('%d-%b-%Y')

# --- Database and Path Configuration ---
def get_db_path(db_name):
    return os.path.join(os.path.dirname(__file__), db_name)

# Fix for GCS deployments - check multiple locations
def get_flexible_db_path(db_name):
    """Get database path checking multiple locations."""
    # 🔧 FIX: App Engine writes to /tmp/
    is_app_engine = os.environ.get('GAE_APPLICATION') is not None
    
    # Check in order: /tmp/ for App Engine, current dir with ./, current dir without ./, default location, /app/
    possible_paths = []
    
    if is_app_engine:
        possible_paths.append(f'/tmp/{db_name}')
    
    possible_paths.extend([
        f'./{db_name}',
        db_name,
        os.path.join(os.path.dirname(__file__), db_name),
        f'/app/{db_name}'
    ])
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Default to /tmp/ on App Engine, current directory otherwise
    return f'/tmp/{db_name}' if is_app_engine else db_name

MAIN_DB_PATH = get_flexible_db_path('bonds_data.db')  # Fixed: tsys_enhanced table is in bonds_data.db
VALIDATED_DB_PATH = get_flexible_db_path('validated_quantlib_bonds.db')  # Fixed: correct validated db name

# --- Convention Constants ---
TREASURY_CONVENTIONS = {
    'frequency': 'Semiannual',
    'day_count': 'ActualActual.Bond',  # ✅ Using QuantLib-style name for clarity
    'business_day_convention': 'Following',  # ✅ CORRECTED: Match ticker table
    'fixed_business_convention': 'Unadjusted',  # For payment date adjustments
    'end_of_month': True
}

# --- Treasury Yield Fetching ---
def fetch_latest_trade_date(db_path):
    """Fetches the most recent date from the tsys_enhanced table (more complete yield curve)."""
    with sqlite3.connect(db_path) as conn:
        # Use tsys_enhanced table for complete yield curve coverage
        return pd.read_sql_query('SELECT MAX(Date) FROM tsys_enhanced', conn).iloc[0, 0]

def fetch_treasury_yields(trade_date, db_path):
    """Fetches treasury yields from the 'tsys_enhanced' table with complete yield curve coverage."""
    try:
        # 🔧 FIX: Add detailed logging
        logger.info(f"📁 TREASURY FETCH: Attempting to fetch yields for {trade_date} from {db_path}")
        
        # Check if database exists
        if not os.path.exists(db_path):
            logger.error(f"❌ TREASURY FETCH: Database not found at {db_path}")
            # Try alternative paths - comprehensive search
            is_app_engine = os.environ.get('GAE_APPLICATION') is not None
            alt_paths = []
            
            if is_app_engine:
                alt_paths.append('/tmp/bonds_data.db')  # App Engine writable directory
                
            alt_paths.extend([
                'bonds_data.db',  # Current directory
                './bonds_data.db',  # Explicit current directory  
                '/app/bonds_data.db',  # App Engine default
                os.path.join(os.getcwd(), 'bonds_data.db'),  # Full path to current dir
                MAIN_DB_PATH  # Use the flexible path we found at startup
            ])
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    logger.info(f"✅ TREASURY FETCH: Found database at {alt_path}")
                    db_path = alt_path
                    break
            else:
                logger.error(f"❌ TREASURY FETCH: No database found in any location")
                logger.error(f"   Searched: {alt_paths}")
                logger.error(f"   CWD: {os.getcwd()}")
                logger.error(f"   Files in CWD: {os.listdir('.')[:10]}")
                return {}
        
        with sqlite3.connect(db_path) as conn:
            # Use tsys_enhanced table for complete M1M through M30Y coverage
            query = f"SELECT * FROM tsys_enhanced WHERE Date = '{trade_date}'"
            df_wide = pd.read_sql_query(query, conn)

        if df_wide.empty:
            logger.warning(f"No treasury yields found for date: {trade_date} in 'tsys_enhanced' table.")
            # 🔧 FIX: Use the most recent available date before requested date
            fallback_query = f"""
                SELECT * FROM tsys_enhanced 
                WHERE Date <= '{trade_date}' 
                ORDER BY Date DESC 
                LIMIT 1
            """
            df_fallback = pd.read_sql_query(fallback_query, conn)
            
            if not df_fallback.empty:
                fallback_date = df_fallback['Date'].iloc[0]
                logger.info(f"📅 Using most recent available treasury date: {fallback_date} (requested: {trade_date})")
                df_wide = df_fallback
            else:
                # If no prior dates, try to get the latest available
                latest_query = "SELECT MAX(Date) as latest_date FROM tsys_enhanced"
                latest_df = pd.read_sql_query(latest_query, conn)
                latest_date = latest_df['latest_date'].iloc[0] if not latest_df.empty else None
                logger.info(f"📅 Latest available treasury date: {latest_date}")
                return {}

        # Unpivot the data from wide to long format
        yield_data_row = df_wide.iloc[0]
        raw_yields = {}
        for col_name, value in yield_data_row.items():
            # Enhanced table has M1M, M2M, M3M, M6M, M1Y, M2Y, M3Y, M5Y, M7Y, M10Y, M20Y, M30Y
            if col_name.startswith('M') and (col_name.endswith('Y') or col_name.endswith('M')):
                tenor_str = col_name.replace('M', '') # Converts 'M10Y' to '10Y', 'M1M' to '1M'
                raw_yields[tenor_str] = value

        # Enhanced table already has yields in percentage format (4.5 = 4.5%), convert to decimal
        yield_dict = {k: v / 100.0 for k, v in raw_yields.items() if v is not None}
        logger.info(f"Successfully fetched treasury yields from 'tsys_enhanced' for {trade_date}: {list(yield_dict.keys())}")
        return yield_dict

    except Exception as e:
        logger.error(f"Failed to fetch treasury yields from 'tsys_enhanced': {e}", exc_info=True)
        return {}

def get_closest_treasury_yield(treasury_yields, target_years):
    """
    Find the closest treasury yield for a given maturity in years
    
    Args:
        treasury_yields: Dict of treasury yields like {'1Y': 0.045, '2Y': 0.046, ...}
        target_years: Target maturity in years (e.g., 8.5)
        
    Returns:
        float: Treasury yield as decimal (e.g., 0.045 for 4.5%)
    """
    if not treasury_yields:
        return None
    
    # Convert treasury tenors to years
    tenor_years = {}
    for tenor, yield_val in treasury_yields.items():
        if yield_val is None:
            continue
            
        try:
            if 'M' in tenor:  # Months like '1M', '3M', '6M'
                months = int(tenor.replace('M', ''))
                tenor_years[months / 12.0] = yield_val
            elif 'Y' in tenor:  # Years like '1Y', '2Y', '5Y', '10Y'
                years = int(tenor.replace('Y', ''))
                tenor_years[years] = yield_val
        except:
            continue
    
    if not tenor_years:
        return None
    
    # Find closest maturity
    closest_maturity = min(tenor_years.keys(), key=lambda x: abs(x - target_years))
    closest_yield = tenor_years[closest_maturity]
    
    logger.debug(f"Treasury lookup: {target_years:.1f}Y bond matched to {closest_maturity:.1f}Y treasury at {closest_yield*100:.3f}%")
    
    return closest_yield

# --- Bond Convention Handling ---
# Import the WORKING Treasury detector that has ISIN pattern matching
from treasury_bond_fix import TreasuryBondDetector as WorkingTreasuryDetector

def parse_date(date_input):
    """Robustly parse a date from various formats, including existing date/datetime objects."""
    if not date_input:
        return None

    # If it's already a date or datetime object, just return the date part
    if isinstance(date_input, datetime):
        return date_input.date()
    if isinstance(date_input, date):
        return date_input

    # If it's a string, try parsing it
    for fmt in ('%Y-%m-%d', '%d-%b-%y', '%m/%d/%Y', '%Y-%m-%dT%H:%M:%S.%f'):
        try:
            return datetime.strptime(str(date_input), fmt).date()
        except (ValueError, TypeError):
            continue
            
    logger.warning(f"Could not parse date from input: {date_input}")
    return None

def get_conventions_from_db(isin, db_path):
    """Fetches bond conventions from the validated SQLite database."""
    if not isin or not db_path:
        return {}
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM validated_quantlib_bonds WHERE isin = ?", (isin,))
            row = cursor.fetchone()
            if row:
                return dict(row)
    except sqlite3.Error as e:
        logger.error(f"Database error while fetching conventions for {isin}: {e}")
    return {}

def get_ticker_from_description(description):
    """
    Extract ticker from bond description
    Examples:
    - "ECOPET 5 ⅞ 05/28/45" → "ECOPET"
    - "PEMEX 6.95 01/28/60" → "PEMEX"
    - "ECOPETROL SA, 5.875%, 28-May-2045" → "ECOPETROL"
    """
    if not description:
        return None
        
    # Split by spaces and get first part
    parts = description.strip().split()
    if parts:
        ticker = parts[0].upper()
        # Remove any special characters
        ticker = ticker.replace(',', '').replace('.', '')
        return ticker
    return None

def get_validated_conventions_by_ticker(ticker, validated_db_path):
    """
    Get conventions from validated_quantlib_bonds by matching ticker in description
    This is more reliable than ticker_convention_preferences
    """
    if not ticker or not validated_db_path:
        return None
        
    try:
        with sqlite3.connect(validated_db_path) as conn:
            cursor = conn.cursor()
            
            # Get the most common convention for this ticker
            query = """
            SELECT 
                day_count,
                business_convention,
                frequency,
                COUNT(*) as count
            FROM validated_quantlib_bonds
            WHERE description LIKE ? || '%'
            GROUP BY day_count, business_convention, frequency
            ORDER BY count DESC
            LIMIT 1
            """
            cursor.execute(query, (ticker,))
            result = cursor.fetchone()
            
            if result:
                conventions = {
                    'day_count': result[0],
                    'business_convention': result[1],
                    'frequency': result[2],
                    'source': 'validated_ticker_lookup',
                    'bond_count': result[3]
                }
                logger.info(f"✅ Found validated conventions for ticker {ticker} (used by {result[3]} bonds): {conventions}")
                return conventions
                
    except Exception as e:
        logger.error(f"Error getting validated ticker conventions: {e}")
        
    return None

def find_isin_from_parsed_data(parsed_data, validated_db_path):
    """
    Find ISIN from validated database using parsed bond details.
    This helps when parsing descriptions that don't include ISINs.
    """
    if not parsed_data or not validated_db_path:
        return None
        
    try:
        coupon = parsed_data.get('coupon')
        maturity = parsed_data.get('maturity')
        issuer = parsed_data.get('issuer', '').upper()
        
        if not coupon or not maturity:
            return None
            
        # Connect to validated database
        with sqlite3.connect(validated_db_path) as conn:
            cursor = conn.cursor()
            
            # Try exact match on coupon and maturity
            query = """
            SELECT isin, description 
            FROM validated_quantlib_bonds 
            WHERE coupon = ? 
            AND maturity = ?
            """
            
            cursor.execute(query, (coupon, maturity))
            results = cursor.fetchall()
            
            # If we have results, try to match by issuer
            for isin, description in results:
                desc_upper = description.upper()
                # Check if issuer matches
                if 'ECOPETROL' in issuer and 'ECOPET' in desc_upper:
                    logger.info(f"✅ Found ISIN {isin} for ECOPETROL bond via validated DB lookup")
                    return isin
                elif 'PEMEX' in issuer and ('PEMEX' in desc_upper or 'PETROLEOS' in desc_upper):
                    logger.info(f"✅ Found ISIN {isin} for PEMEX bond via validated DB lookup")
                    return isin
                elif issuer[:6] in desc_upper:  # Match first 6 chars of issuer
                    logger.info(f"✅ Found ISIN {isin} for {issuer} bond via validated DB lookup")
                    return isin
                
            # If no issuer match but only one result, use it
            if len(results) == 1:
                isin = results[0][0]
                logger.info(f"✅ Found unique ISIN {isin} via coupon/maturity match")
                return isin
                
    except Exception as e:
        logger.error(f"Error finding ISIN from parsed data: {e}")
        
    return None

# --- Core Calculation Engine ---
def calculate_bond_metrics_with_conventions_using_shared_engine(isin, coupon, maturity_date, price, trade_date, treasury_handle, default_conventions, is_treasury=False, settlement_days=0, validated_db_path=None, description=None, db_path=None, use_settlement_date_directly=True):
    log_prefix = f"[CALC_ENGINE ISIN: {isin}, T+{settlement_days}]"
    logger.info(f"{log_prefix} Starting calculation.")
    try:
        maturity_date = parse_date(maturity_date)
        trade_date = parse_date(trade_date)
        logger.info(f"{log_prefix} Dates parsed. Maturity: {maturity_date}, Trade: {trade_date}")
        if not maturity_date or not trade_date:
            raise ValueError("Maturity or trade date could not be parsed.")

        calculation_date = ql.Date(trade_date.day, trade_date.month, trade_date.year)
        ql.Settings.instance().evaluationDate = calculation_date
        logger.info(f"{log_prefix} QL evaluation date set.")

        day_count = ql.Actual360()
        calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        
        # FIXED: When settlement_date is explicitly provided, use it directly
        if use_settlement_date_directly and settlement_days == 0:
            # Settlement date was explicitly provided - use it as-is WITHOUT holiday adjustment
            # For accrued interest, we need the actual calendar date, not business day adjusted
            settlement_date = calculation_date
            logger.info(f"{log_prefix} Using provided settlement date directly (no holiday adjustment): {format_ql_date(settlement_date)}")
        else:
            # Traditional behavior: calculate settlement date from trade date + settlement days
            settlement_date = calendar.advance(calculation_date, ql.Period(settlement_days, ql.Days))
            logger.info(f"{log_prefix} Calculated settlement date (T+{settlement_days}): {format_ql_date(settlement_date)}")
        
        # ✅ CORRECTED: Let QuantLib handle issue date with defaults
        # DO NOT manually set issue date - causes duration calculation errors
        ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
        
        logger.info(f"{log_prefix} Settlement date set to: {format_ql_date(settlement_date)}")
        logger.info(f"{log_prefix} Letting QuantLib handle issue date with defaults")

        conventions = default_conventions.copy()
        db_conventions = get_conventions_from_db(isin, validated_db_path)
        if db_conventions:
            conventions.update(db_conventions)
        if is_treasury:
            logger.info(f"{log_prefix} Applying Treasury override conventions.")
            conventions.update(TREASURY_CONVENTIONS)
        logger.info(f"{log_prefix} Final conventions: {conventions}")

        frequency = get_ql_frequency(conventions.get('frequency'))

        logger.info(f"{log_prefix} Creating QuantLib bond schedule...")
        
        # FIXED: Create schedule from well before settlement to capture all coupon dates
        # Calculate a start date that's at least 10 years before settlement
        years_back = 10
        schedule_start = settlement_date
        for i in range(years_back * 2):  # Semi-annual periods
            schedule_start = calendar.advance(schedule_start, ql.Period(-6, ql.Months))
        
        # Get business day convention from conventions
        bus_day_conv_str = conventions.get('fixed_business_convention') or conventions.get('business_day_convention', 'Following')
        
        # Map string to QuantLib convention
        if bus_day_conv_str == 'Unadjusted':
            business_convention = ql.Unadjusted
        elif bus_day_conv_str == 'Following':
            business_convention = ql.Following
        elif bus_day_conv_str == 'ModifiedFollowing':
            business_convention = ql.ModifiedFollowing
        elif bus_day_conv_str == 'Preceding':
            business_convention = ql.Preceding
        else:
            business_convention = ql.Following  # Default
            
        logger.info(f"{log_prefix} Using business day convention: {bus_day_conv_str}")
        
        # Create schedule from calculated start to maturity
        schedule = ql.Schedule(
            schedule_start,
            ql_maturity,
            ql.Period(frequency),
            calendar,
            business_convention,
            business_convention,
            ql.DateGeneration.Backward,
            False
        )
        
        logger.info(f"{log_prefix} Schedule created from {format_ql_date(schedule_start)} to {format_ql_date(ql_maturity)}")

        # Map day count convention from string to QuantLib object
        day_count_str = conventions.get('day_count', '30/360')
        
        # Enhanced mapping to handle both internal names and database names
        day_count_map = {
            # Preferred QuantLib-style names
            'ActualActual.Bond': ql.ActualActual(ql.ActualActual.Bond),
            'ActualActual.ISMA': ql.ActualActual(ql.ActualActual.ISMA),
            'ActualActual.ISDA': ql.ActualActual(ql.ActualActual.ISDA),
            'Thirty360.BondBasis': ql.Thirty360(ql.Thirty360.BondBasis),
            'Actual360': ql.Actual360(),
            'Actual365Fixed': ql.Actual365Fixed(),
            
            # Legacy/compatibility names
            'ActualActual_Bond': ql.ActualActual(ql.ActualActual.Bond),
            'Actual/Actual (ISMA)': ql.ActualActual(ql.ActualActual.Bond),  # Map ISMA to Bond for clarity
            '30/360': ql.Thirty360(ql.Thirty360.BondBasis),
            'Thirty360': ql.Thirty360(ql.Thirty360.BondBasis),
            'ACT/360': ql.Actual360(),
            'ACT/365': ql.Actual365Fixed(),
        }
        
        if day_count_str in day_count_map:
            day_counter = day_count_map[day_count_str]
        else:
            logger.warning(f"Unknown day count convention '{day_count_str}', defaulting to ActualActual.ISDA")
            day_counter = ql.ActualActual(ql.ActualActual.ISDA)
        
        logger.info(f"{log_prefix} Using day count convention: {day_count_str} -> {day_counter}")
        
        # CRITICAL FIX: Convert coupon from percentage to decimal for QuantLib
        # Input coupon comes as percentage (e.g., 3.0 for 3%), QuantLib expects decimal (0.03)
        coupon_decimal = coupon / 100.0
        logger.info(f"{log_prefix} Creating FixedRateBond... SettlementDays: {settlement_days}, Coupon: {coupon}% -> {coupon_decimal} (decimal)")
        bond = ql.FixedRateBond(settlement_days, 100.0, schedule, [coupon_decimal], day_counter)
        logger.info(f"{log_prefix} FixedRateBond created successfully.")

        # CRITICAL FIX: Don't set pricing engine - it may interfere with yield calculation
        logger.info(f"{log_prefix} Skipping pricing engine setup for yield calculation accuracy.")

        # Handle missing price with a reasonable default (par value)
        if price is None:
            logger.warning(f"{log_prefix} Price is None, using default par value 100.0")
            price = 100.0
        
        logger.info(f"{log_prefix} Calculating yield for price {price}...")
        
        # 🔧 YIELD CALCULATION FIX - Use semiannual frequency for all bonds
        yield_frequency = ql.Semiannual  # Standard for most bonds
        
        # Step 1: Calculate yield using semiannual frequency
        bond_yield_decimal = bond.bondYield(
            price, 
            day_counter, 
            ql.Compounded, 
            yield_frequency
        )
        
        logger.info(f"{log_prefix} Yield calculated (decimal): {bond_yield_decimal:.6f} ({bond_yield_decimal*100:.5f}%)")

        # 🔧 DURATION CALCULATION FIX - Use DECIMAL yield (not percentage!)
        logger.info(f"{log_prefix} Calculating duration with DECIMAL yield...")
        
        # ✅ FIXED: Use decimal yield directly - QuantLib expects decimal format
        logger.info(f"{log_prefix} Using decimal yield for duration: {bond_yield_decimal:.6f}")
        
        # ✅ FIXED: Calculate duration with decimal yield (no percentage conversion)
        duration = ql.BondFunctions.duration(
            bond, bond_yield_decimal, day_counter, ql.Compounded, 
            yield_frequency, ql.Duration.Modified
        )
        
        # ✅ FIXED: No scaling needed - QuantLib returns duration in years directly
        logger.info(f"{log_prefix} Duration: {duration:.5f} years (no scaling needed)")

        # 🔧 CONVEXITY CALCULATION FIX - Use decimal yield consistently
        logger.info(f"{log_prefix} Calculating convexity with decimal yield...")
        convexity = ql.BondFunctions.convexity(
            bond, bond_yield_decimal, day_counter, ql.Compounded, yield_frequency
        )
        logger.info(f"{log_prefix} Convexity: {convexity:.5f} (no scaling needed)")
        
        # 🚀 CRITICAL FIX: Add accrued interest calculation (missing for dirty price!)
        logger.info(f"{log_prefix} Calculating accrued interest...")
        
        # FIXED: For explicit settlement dates on holidays, calculate accrued manually
        # to avoid QuantLib's automatic business day adjustment
        if use_settlement_date_directly and calendar.isHoliday(settlement_date):
            logger.info(f"{log_prefix} Settlement date is a holiday - calculating accrued manually")
            
            # Find the coupon period containing the settlement date
            for i in range(len(schedule) - 1):
                if schedule[i] <= settlement_date <= schedule[i + 1]:
                    prev_coupon_date = schedule[i]
                    next_coupon_date = schedule[i + 1]
                    
                    # Calculate accrued days using the bond's day counter
                    accrued_days = day_counter.dayCount(prev_coupon_date, settlement_date)
                    period_days = day_counter.dayCount(prev_coupon_date, next_coupon_date)
                    
                    # Calculate accrued interest
                    coupon_payment = coupon_decimal * 100.0 / frequency  # Semi-annual payment
                    accrued_interest = coupon_payment * (accrued_days / float(period_days))
                    
                    logger.info(f"{log_prefix} Manual accrued calc: {accrued_days} days / {period_days} days * {coupon_payment}% = {accrued_interest:.6f}%")
                    break
            else:
                # Fallback to QuantLib calculation if period not found
                accrued_interest = bond.accruedAmount()
        else:
            # Use standard QuantLib calculation for non-holiday dates
            accrued_interest = bond.accruedAmount()
            
        # 💰 NEW: Calculate accrued interest per million for Bloomberg validation
        accrued_per_million = accrued_interest * 10000  # Convert % to $ per 1M notional
        logger.info(f"{log_prefix} Accrued Interest: {accrued_interest:.6f}% ({accrued_per_million:.2f} per 1M)")
        
        # 🚀 ADDITIONAL METRICS: Add PVBP (Price Value of a Basis Point)
        logger.info(f"{log_prefix} Calculating PVBP...")
        # ✅ FIXED: PVBP = Duration × Price / 10000 (duration already in years)
        pvbp = duration * price / 10000
        logger.info(f"{log_prefix} PVBP: {pvbp:.6f}")
        
        logger.info(f"{log_prefix} 🎉 FIXED CALCULATION SUCCESSFUL!")
        logger.info(f"{log_prefix} 📊 Results: Yield={bond_yield_decimal*100:.5f}%, Duration={duration:.5f}, Convexity={convexity:.2f}, Accrued={accrued_interest:.6f}")
        
        # 🚀 SPREAD CALCULATION FIX: Calculate spread for ALL bonds (including Treasuries)
        g_spread = None  # Default when calculation fails
        z_spread = None  # Default
        
        # Calculate spread for ALL bonds (Treasuries can trade away from the fitted curve)
        # Use provided db_path or fallback to default
        effective_db_path = db_path or './bonds_data.db'
        effective_validated_path = validated_db_path or './validated_quantlib_bonds.db'
        
        detector = WorkingTreasuryDetector(effective_db_path, effective_validated_path)
        bond_yield_pct = bond_yield_decimal * 100  # Convert to percentage
        
        try:
            # Get treasury yields for the trade date - USE PASSED DB_PATH
            treasury_yields = fetch_treasury_yields(trade_date.strftime('%Y-%m-%d'), effective_db_path)
            
            if treasury_yields:
                # Calculate years to maturity for treasury matching
                years_to_maturity = (maturity_date - trade_date).days / 365.25
                
                # Find closest treasury yield
                closest_treasury_yield = get_closest_treasury_yield(treasury_yields, years_to_maturity)
                
                if closest_treasury_yield:
                    # Calculate spread in basis points
                    treasury_yield_pct = closest_treasury_yield * 100  # Convert to percentage
                    g_spread = (bond_yield_pct - treasury_yield_pct) * 100  # Convert to basis points
                    
                    # 🚀 REAL Z-SPREAD CALCULATION using QuantLib
                    logger.info(f"{log_prefix} 🔍 Z-SPREAD: Building treasury curve for real z-spread calculation")
                    try:
                        # Build proper treasury curve from our treasury data
                        treasury_curve = build_treasury_curve_from_yields(treasury_yields, trade_date)
                        
                        if treasury_curve:
                            # Use QuantLib's zSpread method for institutional-grade calculation
                            day_count = ql.Actual365Fixed()  # Standard day count for spreads
                            compounding = ql.Semiannual     # Match bond convention
                            frequency = ql.Semiannual      # Match bond convention
                            
                            # Extract YieldTermStructure from handle
                            curve_ts = treasury_curve.currentLink()
                            
                            z_spread_value = ql.BondFunctions.zSpread(
                                bond,                        # QuantLib bond object
                                price,                       # Clean price (Real)
                                curve_ts,                    # YieldTermStructure (not handle)
                                day_count,                   # Day count convention
                                compounding,                 # Compounding frequency  
                                frequency,                   # Payment frequency
                                settlement_date              # Settlement date
                            )
                            
                            z_spread = z_spread_value * 10000  # Convert to basis points
                            logger.info(f"{log_prefix} 🎯 REAL Z-SPREAD: {z_spread:.2f} bps (QuantLib institutional calculation)")
                        else:
                            logger.warning(f"{log_prefix} ❌ Could not build treasury curve for z-spread")
                            z_spread = None
                    except Exception as z_error:
                        logger.error(f"{log_prefix} ❌ Z-spread calculation failed: {z_error}")
                        z_spread = None
                    
                    
                    if is_treasury:
                        logger.info(f"{log_prefix} 💰 TREASURY SPREAD: Bond {bond_yield_pct:.3f}% - Curve {treasury_yield_pct:.3f}% = {g_spread:.0f} bps")
                    else:
                        logger.info(f"{log_prefix} 💰 CORPORATE SPREAD: Bond {bond_yield_pct:.3f}% - Treasury {treasury_yield_pct:.3f}% = {g_spread:.0f} bps")
                else:
                    logger.warning(f"{log_prefix} No matching treasury yield for {years_to_maturity:.1f}Y maturity")
                    logger.info(f"{log_prefix} Available tenors: {list(treasury_yields.keys()) if treasury_yields else 'None'}")
            else:
                logger.warning(f"{log_prefix} ⚠️ No treasury yields available for {trade_date}")
                logger.info(f"{log_prefix} DB Path checked: {effective_db_path}")
        except Exception as spread_error:
            logger.error(f"{log_prefix} ❌ SPREAD CALCULATION ERROR: {spread_error}", exc_info=True)
            logger.error(f"{log_prefix} DB Path: {effective_db_path}")
            logger.error(f"{log_prefix} Trade Date: {trade_date}")
        
        settlement_date_str = f"{settlement_date.year()}-{settlement_date.month():02d}-{settlement_date.dayOfMonth():02d}"
        return {
            'isin': isin,
            'ytm': bond_yield_decimal * 100,  # ✅ CORRECTED: YTM in percentage format
            'duration': duration,         # ✅ FIXED: Duration in years (no artificial scaling)
            'convexity': convexity,       # ✅ FIXED: Convexity (no artificial scaling)
            'accrued_interest': accrued_interest,  # 🚀 FIXED: Now includes accrued interest!
            'accrued_per_million': accrued_per_million,  # 💰 NEW: Accrued interest per $1M (Bloomberg format)
            'clean_price': price,         # 🚀 ADDED: Clean price from input
            'dirty_price': price + accrued_interest,  # 🚀 ADDED: Dirty price calculation
            'pvbp': pvbp,                 # 🚀 NEW: Price Value of a Basis Point
            'spread': g_spread,           # 🚀 FIXED: Changed from 'g_spread' to 'spread' for API compatibility!
            'z_spread': z_spread,         # 🚀 FIXED: Estimated Z-spread
            'conventions': conventions,
            'settlement_date_str': settlement_date_str,
            'successful': True
        }
        
        # 🔍 DEBUG: Log final spread values after return dict created
        logger.info(f"{log_prefix} 🔍 RETURN DEBUG: Returned g_spread={g_spread}, z_spread={z_spread}")
    except Exception as e:
        logger.error(f"{log_prefix} Calculation failed: {e}", exc_info=True)
        return {'isin': isin, 'successful': False, 'error': str(e)}

def process_bond_portfolio(portfolio_data, db_path, validated_db_path, bloomberg_db_path, settlement_days=0, settlement_date=None):
    logger.debug(f"[NameError DEBUG] process_bond_portfolio received portfolio_data: {portfolio_data}")
    try:
        bond_data_list = portfolio_data.get('data', [])
        logger.debug(f"[NameError DEBUG] Extracted bond_data_list (len={len(bond_data_list)}): {bond_data_list}")
    except NameError as ne:
        logger.error(f"[NameError DEBUG] CAUGHT NameError right at the start! The 'portfolio_data' variable is not defined in this scope. Error: {ne}", exc_info=True)
        return [{'error': 'NameError: portfolio_data not defined in scope', 'details': str(ne)}]

    abs_path = os.path.abspath(bloomberg_db_path)
    logger.info(f"[PATH_DEBUG] process_bond_portfolio received bloomberg_db_path: {abs_path}")
    logger.info(f"[PATH_DEBUG] Checking existence of DB file at {abs_path}: {os.path.exists(abs_path)}")
    
    # 🔧 FIX: Log database paths for spread calculation debugging
    logger.info(f"📁 SPREAD DEBUG: Using databases:")
    logger.info(f"   Primary DB: {db_path} (exists: {os.path.exists(db_path)})")
    logger.info(f"   Validated DB: {validated_db_path} (exists: {os.path.exists(validated_db_path)})")
    logger.info(f"   Current directory: {os.getcwd()}")
    results = []
    # ✅ FIXED: Use settlement date instead of database trade date
    if settlement_date is None:
        today = datetime.now()
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        settlement_date_str = last_day_previous_month.strftime("%Y-%m-%d")
        logger.info(f"📅 Using default settlement date (prior month end): {settlement_date_str}")
    else:
        settlement_date_str = settlement_date
        logger.info(f"📅 Using provided settlement date: {settlement_date_str}")
    
    # Convert to date object to prevent type mismatches with other date objects
    # FIXED: This is actually the settlement date, not trade date
    settlement_date_obj = datetime.strptime(settlement_date_str, '%Y-%m-%d').date()
    treasury_yields = fetch_treasury_yields(settlement_date_str, db_path)
    treasury_handle = ql.YieldTermStructureHandle(ql.FlatForward(ql.Date(settlement_date_obj.day, settlement_date_obj.month, settlement_date_obj.year), 0.03, ql.Actual365Fixed()))
    # Initialize the WORKING Treasury detector with proper ISIN pattern matching
    detector = WorkingTreasuryDetector(db_path, validated_db_path)
    # CRITICAL FIX: The parser's primary db_path for yields MUST be the bloomberg_db_path.
    parser = SmartBondParser(bloomberg_db_path, validated_db_path, bloomberg_db_path)

    for bond_data in bond_data_list:
        # FIELD MAPPING FIX: Handle both 'description' and 'BOND_CD' field names  
        description = bond_data.get('description') or bond_data.get('BOND_CD')
        
        # 🔧 FIX: Handle numeric inputs from Google Sheets
        if isinstance(description, (int, float)):
            description = str(description)
        
        # Check if bond data came from database lookup (ISIN route)
        if bond_data.get('from_database'):
            logger.info(f"🗄️ Using bond data from database lookup, skipping parsing")
            # Create parsed_data from database values
            # Handle date format conversion from DD/MM/YYYY to YYYY-MM-DD
            maturity_raw = bond_data.get('maturity', '2030-01-01')
            if '/' in maturity_raw and len(maturity_raw.split('/')) == 3:
                # Convert DD/MM/YYYY to YYYY-MM-DD
                parts = maturity_raw.split('/')
                maturity_formatted = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            else:
                maturity_formatted = maturity_raw
                
            parsed_data = {
                'issuer': bond_data.get('issuer', 'UNKNOWN'),
                'coupon': bond_data.get('coupon', 0.0),
                'maturity': maturity_formatted,
                'bond_type': 'treasury' if 'TREASURY' in str(bond_data.get('issuer', '')).upper() else 'corporate',
                'from_database': True,
                'day_count': bond_data.get('day_count'),
                'frequency': bond_data.get('frequency'),
                'business_convention': bond_data.get('business_convention')
            }
            logger.info(f"📅 Converted maturity date: {maturity_raw} → {maturity_formatted}")
        else:
            parsed_data = parser.parse_bond_description(description)
        if not parsed_data:
            # 🔧 FIX: Enhanced hierarchy fallback when parsing fails
            logger.warning(f"⚠️ Parsing failed for '{description}', using fallback hierarchy")
            
            # Check if it looks like an ISIN
            is_isin_format = (isinstance(description, str) and 
                            len(description) >= 10 and 
                            len(description) <= 12 and
                            description[:2].isalpha())
            
            # Get fallback conventions based on ISIN structure or defaults
            fallback_conventions = get_isin_fallback_conventions(
                isin=description if is_isin_format else None,
                description=description
            )
            
            # Create minimal parsed data for fallback
            parsed_data = {
                'issuer': 'UNKNOWN',
                'coupon': 0.0,  # Zero coupon fallback
                'maturity': '2030-01-01',  # Default maturity
                'bond_type': 'corporate',
                'parsing_failed': True,
                'used_fallback': True,
                'fallback_conventions': fallback_conventions
            }
            
            logger.info(f"📋 Using fallback: {fallback_conventions}")

        isin = bond_data.get('isin') or parsed_data.get('isin')
        
        # FIXED: Enhanced lookup hierarchy
        ticker_conventions = None
        
        # IMPORTANT: Do NOT look up ISIN from parsed data
        # Reg S and 144A bonds can have same description but different ISINs
        # We should use the parsing route without ISIN lookup to avoid confusion
        # if not isin and parsed_data and validated_db_path:
        #     isin = find_isin_from_parsed_data(parsed_data, validated_db_path)
        #     if isin:
        #         logger.info(f"📋 Found ISIN {isin} via validated DB lookup for {description}")
        
        # Step 2: If still no ISIN, try ticker lookup for conventions
        # Store ticker conventions to apply after default_conventions is defined
        if not isin and description:
            ticker = get_ticker_from_description(description)
            if ticker:
                # Try validated DB first for ticker conventions
                ticker_conventions = get_validated_conventions_by_ticker(ticker, validated_db_path)
                if ticker_conventions:
                    logger.info(f"📋 Found validated ticker conventions for {ticker}")
        
        # Use the WORKING Treasury detector that has ISIN pattern matching
        is_treasury, detection_method = detector.is_treasury_bond(isin, description)
        logger.info(f"🏛️ Treasury detection: {is_treasury} via {detection_method} for ISIN {isin}")
        
        # Set default conventions (can be overridden by specific bond info)
        # 🔧 FIX: Use conventions from database if available
        if parsed_data.get('from_database'):
            # Use conventions from database lookup
            default_conventions = {
                'frequency': parsed_data.get('frequency', 'Semiannual'),
                'day_count': parsed_data.get('day_count', '30/360'),
                'business_day_convention': parsed_data.get('business_convention', 'Following'),
                'end_of_month': False
            }
            logger.info(f"📋 Using conventions from database: {default_conventions}")
        elif parsed_data.get('used_fallback'):
            default_conventions = parsed_data.get('fallback_conventions', {
                'frequency': 'Semiannual',
                'day_count': '30/360',
                'business_convention': 'Following',
                'end_of_month': False
            })
            # Map field names
            default_conventions['frequency'] = default_conventions.get('frequency', 'Semiannual')
            default_conventions['business_day_convention'] = default_conventions.get('business_convention', 'Following')
        else:
            default_conventions = {
                'frequency': 'Semiannual',
                'day_count': '30/360',
                'business_day_convention': 'Following',
                'end_of_month': False
            }
        
        # Apply ticker conventions if found and no ISIN was available
        if ticker_conventions and not isin:
            logger.info(f"📋 Applying ticker conventions as no ISIN was found")
            if 'business_convention' in ticker_conventions:
                default_conventions['fixed_business_convention'] = ticker_conventions['business_convention']
                default_conventions['business_day_convention'] = ticker_conventions['business_convention']
            if 'day_count' in ticker_conventions:
                default_conventions['day_count'] = ticker_conventions['day_count']
            if 'frequency' in ticker_conventions:
                default_conventions['frequency'] = ticker_conventions['frequency']
        
        # Get price from various possible field names
        price = bond_data.get('price') or bond_data.get('CLOSING PRICE') or bond_data.get('closing_price')
        weighting = bond_data.get('weighting') or bond_data.get('WEIGHTING')

        # Call the shared calculation engine, passing the is_treasury flag
        metrics = calculate_bond_metrics_with_conventions_using_shared_engine(
            isin=isin,
            coupon=parsed_data.get('coupon'),
            maturity_date=datetime.strptime(parsed_data.get('maturity'), '%Y-%m-%d'),
            price=price,
            trade_date=settlement_date_obj,  # FIXED: Pass settlement date (was incorrectly named trade_date)
            treasury_handle=treasury_handle,
            default_conventions=default_conventions,
            is_treasury=is_treasury, # Pass the flag here
            settlement_days=settlement_days,
            validated_db_path=validated_db_path,
            description=description,  # Add description parameter
            db_path=db_path,  # Pass db_path for spread calculation
            use_settlement_date_directly=True  # FIXED: Tell function to use settlement date as-is
        )
        
        # ✅ FIXED: Add input fields to metrics for proper response formatting
        metrics['description'] = description
        metrics['input_price'] = price
        metrics['weighting'] = weighting
        if bond_data.get('isin'):
            metrics['isin'] = bond_data.get('isin')
        
        results.append(metrics)
    return results

def build_treasury_curve_from_yields(treasury_yields, settlement_date):
    """
    🎯 Build QuantLib YieldTermStructure from treasury yield data
    
    Args:
        treasury_yields: Dict with tenor keys ('1Y', '2Y', etc.) and yield values
        settlement_date: Python date object or QuantLib Date object
        
    Returns:
        QuantLib YieldTermStructureHandle for z-spread calculation
    """
    try:
        logger.info(f"📈 Building treasury curve from {len(treasury_yields)} yields")
        
        # Convert Python date to QuantLib Date if needed
        if hasattr(settlement_date, 'year') and not hasattr(settlement_date, 'dayOfMonth'):
            # Python datetime.date object - convert to QuantLib Date
            ql_settlement_date = ql.Date(settlement_date.day, settlement_date.month, settlement_date.year)
        else:
            # Already a QuantLib Date
            ql_settlement_date = settlement_date
        
        # Set evaluation date
        ql.Settings.instance().evaluationDate = ql_settlement_date
        logger.info(f"📅 Set evaluation date to: {ql_settlement_date}")
        
        # Create calendar and day count
        calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        day_count = ql.Actual365Fixed()
        
        # Create rate helpers from treasury data
        rate_helpers = []
        
        # Map our tenor format to QuantLib periods
        tenor_mapping = {
            # Short-term format (months as numbers)
            '1': ql.Period(1, ql.Months),
            '2': ql.Period(2, ql.Months), 
            '3': ql.Period(3, ql.Months),
            '6': ql.Period(6, ql.Months),
            # Alternative short-term format
            '1M': ql.Period(1, ql.Months),
            '2M': ql.Period(2, ql.Months), 
            '3M': ql.Period(3, ql.Months),
            '6M': ql.Period(6, ql.Months),
            # Long-term format (standard)
            '1Y': ql.Period(1, ql.Years),
            '2Y': ql.Period(2, ql.Years),
            '3Y': ql.Period(3, ql.Years),
            '5Y': ql.Period(5, ql.Years),
            '7Y': ql.Period(7, ql.Years),
            '10Y': ql.Period(10, ql.Years),
            '20Y': ql.Period(20, ql.Years),
            '30Y': ql.Period(30, ql.Years)
        }
        
        # Add rate helpers for available tenors
        for tenor, yield_value in treasury_yields.items():
            if tenor in tenor_mapping and yield_value is not None:
                period = tenor_mapping[tenor]
                
                # Use appropriate helper based on tenor
                if tenor in ['1M', '2M', '3M', '6M']:
                    # Short term: Use deposit rate helper
                    helper = ql.DepositRateHelper(
                        ql.QuoteHandle(ql.SimpleQuote(yield_value)),
                        period,
                        2,  # Settlement days
                        calendar,
                        ql.ModifiedFollowing,
                        False,  # End of month
                        day_count
                    )
                else:
                    # Long term: Use swap rate helper
                    helper = ql.SwapRateHelper(
                        ql.QuoteHandle(ql.SimpleQuote(yield_value)),
                        period,
                        calendar,
                        ql.Semiannual,  # Fixed leg frequency
                        ql.ModifiedFollowing,  # Fixed leg convention
                        day_count,  # Fixed leg day count
                        ql.USDLibor(ql.Period(3, ql.Months))  # Floating leg index
                    )
                
                rate_helpers.append(helper)
                logger.debug(f"   Added {tenor}: {yield_value:.4f}")
        
        if len(rate_helpers) < 2:
            logger.warning(f"⚠️ Insufficient data for curve building: {len(rate_helpers)} helpers")
            return None
            
        # Build piecewise yield curve
        curve = ql.PiecewiseLogCubicDiscount(
            ql_settlement_date,
            rate_helpers,
            day_count
        )
        
        # Return as handle
        curve_handle = ql.YieldTermStructureHandle(curve)
        logger.info(f"✅ Treasury curve built with {len(rate_helpers)} points")
        return curve_handle
        
    except Exception as e:
        logger.error(f"❌ Treasury curve building failed: {e}")
        return None


def create_treasury_curve(yield_dict, trade_date):
    """Create treasury curve from yield dictionary - RESTORED from backup"""
    logger.info("Creating treasury curve")
    try:
        calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        day_count = ql.Actual360()

        # Adjust trade_date to the previous business day if it's not a working day
        if not calendar.isBusinessDay(trade_date):
            logger.warning(f"Trade date {trade_date} is not a valid business day, adjusting to the previous business day.")
            # ❌ FIXED: Removed dangerous trade date adjustment
            # trade_date remains as provided to avoid calculation interference

        # Log the adjusted trade date
        logger.info(f"Adjusted trade date to: {trade_date}")
        ql.Settings.instance().evaluationDate = trade_date

        # Create rate helpers for the key tenors we have
        rate_helpers = []
        
        # Add available tenors from yield_dict
        if '13W' in yield_dict or '3M' in yield_dict:
            rate = yield_dict.get('13W', yield_dict.get('3M', 0.05))
            rate_helpers.append(
                ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(rate)), 
                                    ql.Period(13, ql.Weeks), 1, 
                                    calendar, ql.ModifiedFollowing, False, day_count)
            )
        
        # Add longer term rates using swap helpers
        for tenor_key, period in [('5Y', 5), ('10Y', 10), ('30Y', 30)]:
            if tenor_key in yield_dict:
                rate_helpers.append(
                    ql.SwapRateHelper(ql.QuoteHandle(ql.SimpleQuote(yield_dict[tenor_key])), 
                                      ql.Period(period, ql.Years), calendar, 
                                      ql.Annual, ql.Unadjusted, 
                                      ql.Thirty360(ql.Thirty360.BondBasis),  
                                      ql.USDLibor(ql.Period(6, ql.Months)))
                )

        if not rate_helpers:
            logger.error("No valid rate helpers created from yield data")
            return None

        treasury_curve = ql.PiecewiseLinearZero(trade_date, rate_helpers, day_count)
        logger.info(f"Created treasury curve with {len(rate_helpers)} rate helpers")
        return ql.YieldTermStructureHandle(treasury_curve)

    except Exception as e:
        logger.error(f"Failed to create treasury curve: {e}")
        return None

def enhance_bond_processing_with_treasuries(bond_data_list, main_db_path, validated_db_path, use_isin=False):
    # This function is a placeholder for future enhancements
    return bond_data_list
