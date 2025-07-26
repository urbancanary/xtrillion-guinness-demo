import streamlit as st
import pandas as pd
import sqlite3
import glob
import os

# --- Data Loading and Processing ---

def get_fixed_results_db():
    """Uses a single fixed database file for consistent results."""
    # Use the fixed database file
    fixed_db = 'bond_analytics_fixed.db'
    if os.path.exists(fixed_db):
        return fixed_db
    return None

def load_results_data(db_path):
    """Loads the test results from the specified database."""
    if not db_path or not os.path.exists(db_path):
        return pd.DataFrame()
    
    # Try to load from yield_comparison table which has all 6 methods
    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query("SELECT * FROM yield_comparison", conn)
        return df
    except:
        # Fallback to old structure
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query("SELECT * FROM results_summary", conn)
        return df

def get_bloomberg_baseline():
    """Returns the HIGH PRECISION Bloomberg baseline results from user's actual Bloomberg Terminal data.
    
    Updated: 2025-07-22 with 6+ decimal place precision
    Source: Bloomberg Terminal export with actual market data
    """
    return {
        "US912810TJ79": {"yield": 4.898453, "duration": 16.357839, "spread": None},
        "XS2249741674": {"yield": 5.637570, "duration": 10.097620, "spread": 118},
        "XS1709535097": {"yield": 5.717451, "duration": 9.815219, "spread": 123},
        "XS1982113463": {"yield": 5.599746, "duration": 9.927596, "spread": 111},
        "USP37466AS18": {"yield": 6.265800, "duration": 13.189567, "spread": 144},
        "USP3143NAH72": {"yield": 5.949058, "duration": 8.024166, "spread": 160},
        "USP30179BR86": {"yield": 7.442306, "duration": 11.583500, "spread": 261},
        "US195325DX04": {"yield": 7.836133, "duration": 12.975798, "spread": 301},
        "US279158AJ82": {"yield": 9.282266, "duration": 9.812703, "spread": 445},
        "USP37110AM89": {"yield": 6.542351, "duration": 12.389556, "spread": 171},
        "XS2542166231": {"yield": 5.720213, "duration": 7.207705, "spread": 146},
        "XS2167193015": {"yield": 6.337460, "duration": 15.269052, "spread": 151},
        "XS1508675508": {"yield": 5.967150, "duration": 12.598517, "spread": 114},
        "XS1807299331": {"yield": 7.059957, "duration": 11.446459, "spread": 223},
        "US91086QAZ19": {"yield": 7.374879, "duration": 13.370728, "spread": 255},
        "USP6629MAD40": {"yield": 7.070132, "duration": 11.382487, "spread": 224},
        "US698299BL70": {"yield": 7.362747, "duration": 13.488582, "spread": 253},
        "US71654QDF63": {"yield": 9.875691, "duration": 9.719713, "spread": 505},
        "US71654QDE98": {"yield": 8.324595, "duration": 4.469801, "spread": 444},
        "XS2585988145": {"yield": 6.228001, "duration": 13.327227, "spread": 140},
        "XS1959337749": {"yield": 5.584981, "duration": 13.261812, "spread": 76},
        "XS2233188353": {"yield": 5.015259, "duration": 0.225205, "spread": 71},
        "XS2359548935": {"yield": 5.628065, "duration": 11.512115, "spread": 101},
        "XS0911024635": {"yield": 5.663334, "duration": 11.237819, "spread": 95},
        "USP0R80BAG79": {"yield": 5.870215, "duration": 5.514383, "spread": 187}
    }

def prepare_comparison_data(results_df):
    """Processes the yield_comparison table data to show all 6 methods."""
    if results_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    # Get Bloomberg baseline for comparison
    baseline_data = get_bloomberg_baseline()
    
    # Create comparison tables using the yield_comparison structure
    # Build yield table using new database column names
    yield_pivot = results_df[['isin', 'description', 'bbg_baseline',
                             'local_isin', 'local_desc', 'local_api_isin', 
                             'local_api_desc', 'cloud_api_isin', 'cloud_api_desc']].copy()
    yield_pivot = yield_pivot.rename(columns={
        'isin': 'ISIN',
        'description': 'Description',
        'bbg_baseline': 'Bloomberg Baseline',
        'local_isin': 'Method 1: Local+ISIN',
        'local_desc': 'Method 2: Local-ISIN',
        'local_api_isin': 'Method 3: API+ISIN',
        'local_api_desc': 'Method 4: API-ISIN',
        'cloud_api_isin': 'Method 5: Cloud+ISIN',
        'cloud_api_desc': 'Method 6: Cloud-ISIN'
    })
    
    # Build duration table using new database column names
    duration_pivot = results_df[['isin', 'description', 'bbg_baseline',
                               'local_isin', 'local_desc', 'local_api_isin', 
                               'local_api_desc', 'cloud_api_isin', 'cloud_api_desc']].copy()
    duration_pivot = duration_pivot.rename(columns={
        'isin': 'ISIN',
        'description': 'Description',
        'bbg_baseline': 'Bloomberg Baseline',
        'local_isin': 'Method 1: Local+ISIN',
        'local_desc': 'Method 2: Local-ISIN',
        'local_api_isin': 'Method 3: API+ISIN',
        'local_api_desc': 'Method 4: API-ISIN',
        'cloud_api_isin': 'Method 5: Cloud+ISIN',
        'cloud_api_desc': 'Method 6: Cloud-ISIN'
    })
    
    # Build spread table using new database column names
    spread_pivot = results_df[['isin', 'description', 'bbg_baseline',
                              'local_isin', 'local_desc', 'local_api_isin', 
                              'local_api_desc', 'cloud_api_isin', 'cloud_api_desc']].copy()
    spread_pivot = spread_pivot.rename(columns={
        'isin': 'ISIN',
        'description': 'Description',
        'bbg_baseline': 'Bloomberg Baseline',
        'local_isin': 'Method 1: Local+ISIN',
        'local_desc': 'Method 2: Local-ISIN',
        'local_api_isin': 'Method 3: API+ISIN',
        'local_api_desc': 'Method 4: API-ISIN',
        'cloud_api_isin': 'Method 5: Cloud+ISIN',
        'cloud_api_desc': 'Method 6: Cloud-ISIN'
    })

    # Ensure TSTs appear at the top by sorting (US912... bonds are Treasury bonds)
    def sort_priority(row):
        isin = row['ISIN']
        if isin.startswith('US912'):
            return (0, isin)  # Treasury bonds first
        elif isin.startswith('US'):
            return (1, isin)  # Other US bonds
        else:
            return (2, isin)  # International bonds
    
    for pivot in [yield_pivot, duration_pivot, spread_pivot]:
        pivot['sort_key'] = pivot.apply(sort_priority, axis=1)
        pivot.sort_values('sort_key', inplace=True)
        pivot.drop('sort_key', axis=1, inplace=True)
        pivot.reset_index(drop=True, inplace=True)

    # Reorder columns to have baseline first, then all 6 methods
    method_order = ['Bloomberg Baseline', 'Method 1: Local+ISIN', 'Method 2: Local-ISIN', 'Method 3: API+ISIN', 'Method 4: API-ISIN', 'Method 5: Cloud+ISIN', 'Method 6: Cloud-ISIN']
    
    def reorder_pivot_columns(df, order):
        id_cols = ['ISIN', 'Description']
        present_methods = [m for m in order if m in df.columns]
        other_methods = [m for m in df.columns if m not in id_cols and m not in present_methods]
        return df[id_cols + present_methods + other_methods]

    yield_pivot = reorder_pivot_columns(yield_pivot, method_order)
    duration_pivot = reorder_pivot_columns(duration_pivot, method_order)
    spread_pivot = reorder_pivot_columns(spread_pivot, method_order)
    
    return yield_pivot, duration_pivot, spread_pivot

def style_diff_from_baseline(df, baseline_col='Bloomberg Baseline', threshold=0.01):
    """Styles the dataframe to highlight differences from the baseline."""
    # Create a clean copy of the dataframe with proper numeric types
    clean_df = df.copy()
    
    # Identify numeric columns
    numeric_cols = [col for col in clean_df.columns 
                   if col not in ['ISIN', 'Description', baseline_col]]
    
    # Convert all columns to numeric, handling empty strings and None values
    for col in numeric_cols + [baseline_col]:
        if col in clean_df.columns:
            clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce')
    
    # Create a simple styled dataframe without complex formatting
    styled_df = clean_df.style
    
    # Format all numeric columns with 3+ decimal places for precision
    format_dict = {}
    for col in numeric_cols + [baseline_col]:
        if col in clean_df.columns:
            if 'yield' in str(col).lower() or baseline_col.lower() == 'bloomberg baseline':
                format_dict[col] = '{:.6f}'  # 6 decimal places for yield
            else:
                format_dict[col] = '{:.3f}'  # 3 decimal places for duration/spread
    
    styled_df = styled_df.format(format_dict, na_rep="N/A")
    
    # Simple highlighting without complex lambda functions
    def highlight_diff(val, baseline_vals, threshold):
        if pd.isna(val) or pd.isna(baseline_vals):
            return ''
        try:
            diff = abs(float(val) - float(baseline_vals))
            return 'background-color: #FFCCCB; color: black' if diff > threshold else ''
        except (ValueError, TypeError):
            return ''
    
    # Apply highlighting
    for col in numeric_cols:
        if col in clean_df.columns and baseline_col in clean_df.columns:
            styled_df = styled_df.apply(
                lambda x: [highlight_diff(val, clean_df[baseline_col].iloc[i], threshold) 
                          for i, val in enumerate(x)],
                subset=[col]
            )
    
    return styled_df


# --- UI Layout ---
st.set_page_config(layout="wide")
st.title("Bond Analytics 6-Way Comparison Dashboard")

st.markdown("""
This dashboard provides a comprehensive overview of bond analytics, comparing results from up to six different calculation methods against the Bloomberg baseline. 
The tables below show **Yield**, **Duration**, and **Spread** for T+0 settlement. 
- Cells highlighted in <span style='background-color: #FFCCCB; padding: 2px;'>red</span> indicate a deviation from the Bloomberg baseline greater than the defined threshold.
""", unsafe_allow_html=True)

# --- Main App Logic ---
db_path = get_fixed_results_db()

if db_path and os.path.exists(db_path):
    st.success(f"Loaded results from: `{db_path}`")
    results_df = load_results_data(db_path)
    
    if results_df.empty:
        st.warning("The results database is empty or could not be read.")
    else:
        # Check for Treasury bond
        treasury_isin = "US912810TJ79"
        if treasury_isin not in results_df['isin'].values:
            st.error(f"CRITICAL: Treasury bond `{treasury_isin}` is missing from the results set. Please re-run the tests.")
        else:
            st.info(f"Treasury bond `{treasury_isin}` found in the results.")

        yield_pivot, duration_pivot, spread_pivot = prepare_comparison_data(results_df)

        # --- Display Tables ---
        st.header("Yield Comparison (T+0)")
        st.dataframe(style_diff_from_baseline(yield_pivot, threshold=0.1), use_container_width=True) # 10 bps threshold

        st.header("Duration Comparison (T+0)")
        st.dataframe(style_diff_from_baseline(duration_pivot, threshold=0.1), use_container_width=True) # 0.1 years threshold

        st.header("Spread Comparison (T+0)")
        st.dataframe(style_diff_from_baseline(spread_pivot, threshold=10), use_container_width=True) # 10 bps threshold

else:
    st.error("No `six_way_analysis_FIXED_*.db` database found. Please run the comprehensive test script first.")
