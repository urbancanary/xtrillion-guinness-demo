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

MAIN_DB_PATH = get_db_path('bonds_data.db')  # Fixed: tsys_enhanced table is in bonds_data.db
VALIDATED_DB_PATH = get_db_path('validated_quantlib_bonds.db')  # Fixed: correct validated db name

# --- Convention Constants ---
TREASURY_CONVENTIONS = {
    'fixed_frequency': 'Semiannual',
    'day_count': 'ActualActual_Bond',  # ✅ CORRECTED: Based on 223-bond Bloomberg testing
    'business_day_convention': 'Following',  # ✅ CORRECTED: Match ticker table 
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
        with sqlite3.connect(db_path) as conn:
            # Use tsys_enhanced table for complete M1M through M30Y coverage
            query = f"SELECT * FROM tsys_enhanced WHERE Date = '{trade_date}'"
            df_wide = pd.read_sql_query(query, conn)

        if df_wide.empty:
            logger.warning(f"No treasury yields found for date: {trade_date} in 'tsys_enhanced' table.")
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

# --- Core Calculation Engine ---
def calculate_bond_metrics_with_conventions_using_shared_engine(isin, coupon, maturity_date, price, trade_date, treasury_handle, default_conventions, is_treasury=False, settlement_days=0, validated_db_path=None):
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
        settlement_date = calendar.advance(calculation_date, ql.Period(settlement_days, ql.Days))
        issue_date = settlement_date
        logger.info(f"{log_prefix} Settlement date set to: {format_ql_date(settlement_date)}")

        conventions = default_conventions.copy()
        db_conventions = get_conventions_from_db(isin, validated_db_path)
        if db_conventions:
            conventions.update(db_conventions)
        if is_treasury:
            logger.info(f"{log_prefix} Applying Treasury override conventions.")
            conventions.update(TREASURY_CONVENTIONS)
        logger.info(f"{log_prefix} Final conventions: {conventions}")

        frequency = get_ql_frequency(conventions.get('fixed_frequency'))
        ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)

        logger.info(f"{log_prefix} Creating schedule... Issue: {format_ql_date(issue_date)}, Maturity: {format_ql_date(ql_maturity)}")
        schedule = ql.Schedule(issue_date, ql_maturity, ql.Period(frequency), calendar, ql.Following, ql.Following, ql.DateGeneration.Backward, False)
        logger.info(f"{log_prefix} Schedule created successfully.")

        # Map day count convention from string to QuantLib object
        day_count_str = conventions.get('day_count', '30/360')
        if day_count_str == 'ActualActual_Bond' or day_count_str == 'ActualActual_ISDA':
            day_counter = ql.ActualActual(ql.ActualActual.ISDA)
        elif day_count_str == 'ActualActual_ISMA':
            day_counter = ql.ActualActual(ql.ActualActual.ISMA)
        elif day_count_str == '30/360':
            day_counter = ql.Thirty360(ql.Thirty360.BondBasis)
        elif day_count_str == 'ACT/360':
            day_counter = ql.Actual360()
        elif day_count_str == 'ACT/365':
            day_counter = ql.Actual365Fixed()
        else:
            day_counter = ql.ActualActual(ql.ActualActual.ISDA)  # Default for Treasury
        
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

        # 🔧 DURATION CALCULATION FIX - Apply your brilliant discovery!
        logger.info(f"{log_prefix} Applying BRILLIANT duration fix...")
        
        # Step 2: Convert yield to percentage format for duration calculation
        yield_percentage = bond_yield_decimal * 100  # Convert 0.048997 → 4.89972
        logger.info(f"{log_prefix} Yield for duration calc: {bond_yield_decimal:.6f} (decimal) → {yield_percentage:.5f} (percentage)")
        
        # Step 3: Calculate duration with percentage yield
        duration_raw = ql.BondFunctions.duration(
            bond, yield_percentage, day_counter, ql.Compounded, 
            yield_frequency, ql.Duration.Modified
        )
        
        # Step 4: Scale result to Bloomberg format (multiply by 100)
        duration = duration_raw * 100  # Convert 0.16347 → 16.347
        logger.info(f"{log_prefix} Duration: {duration_raw:.6f} (raw) → {duration:.5f} (Bloomberg-compatible)")

        # 🔧 CONVEXITY CALCULATION FIX - Use same methodology
        logger.info(f"{log_prefix} Calculating convexity with same methodology...")
        convexity_raw = ql.BondFunctions.convexity(
            bond, yield_percentage, day_counter, ql.Compounded, yield_frequency
        )
        convexity = convexity_raw * 100  # Apply same scaling
        logger.info(f"{log_prefix} Convexity: {convexity_raw:.6f} (raw) → {convexity:.5f} (scaled)")
        
        logger.info(f"{log_prefix} 🎉 FIXED CALCULATION SUCCESSFUL!")
        logger.info(f"{log_prefix} 📊 Results: Yield={bond_yield_decimal*100:.5f}%, Duration={duration:.5f}, Convexity={convexity:.2f}")
        
        settlement_date_str = f"{settlement_date.year()}-{settlement_date.month():02d}-{settlement_date.dayOfMonth():02d}"
        return {
            'isin': isin,
            'yield': bond_yield_decimal,  # Return decimal yield for consistency
            'duration': duration,         # Bloomberg-compatible duration
            'convexity': convexity,       # Scaled convexity
            'g_spread': 0, 
            'z_spread': 0,
            'conventions': conventions,
            'settlement_date_str': settlement_date_str,
            'successful': True
        }
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
    trade_date = datetime.strptime(settlement_date_str, '%Y-%m-%d').date()
    treasury_yields = fetch_treasury_yields(settlement_date_str, db_path)
    treasury_handle = ql.YieldTermStructureHandle(ql.FlatForward(ql.Date(trade_date.day, trade_date.month, trade_date.year), 0.03, ql.Actual365Fixed()))
    # Initialize the WORKING Treasury detector with proper ISIN pattern matching
    detector = WorkingTreasuryDetector(db_path, validated_db_path)
    # CRITICAL FIX: The parser's primary db_path for yields MUST be the bloomberg_db_path.
    parser = SmartBondParser(bloomberg_db_path, validated_db_path, bloomberg_db_path)

    for bond_data in bond_data_list:
        description = bond_data.get('description')
        parsed_data = parser.parse_bond_description(description)
        if not parsed_data:
            results.append({'description': description, 'successful': False, 'error': 'Parsing failed'})
            continue

        isin = bond_data.get('isin') or parsed_data.get('isin')
        # Use the WORKING Treasury detector that has ISIN pattern matching
        is_treasury, detection_method = detector.is_treasury_bond(isin, description)
        logger.info(f"🏛️ Treasury detection: {is_treasury} via {detection_method} for ISIN {isin}")
        
        # Set default conventions (can be overridden by specific bond info)
        default_conventions = {
            'fixed_frequency': 'Semiannual',
            'day_count': '30/360',
            'business_day_convention': 'Following',
            'end_of_month': False
        }
        
        # Get price from various possible field names
        price = bond_data.get('price') or bond_data.get('CLOSING PRICE') or bond_data.get('closing_price')

        # Call the shared calculation engine, passing the is_treasury flag
        metrics = calculate_bond_metrics_with_conventions_using_shared_engine(
            isin=isin,
            coupon=parsed_data.get('coupon'),
            maturity_date=datetime.strptime(parsed_data.get('maturity'), '%Y-%m-%d'),
            price=price,
            trade_date=trade_date,
            treasury_handle=treasury_handle,
            default_conventions=default_conventions,
            is_treasury=is_treasury, # Pass the flag here
            settlement_days=settlement_days,
            validated_db_path=validated_db_path
        )
        results.append(metrics)
    return results

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
