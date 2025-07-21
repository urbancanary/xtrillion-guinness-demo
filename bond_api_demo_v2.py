# To run this Streamlit app on a different port (e.g., 8502),
# use the following command in your terminal:
# streamlit run your_script_name.py --server.port 8502

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# --- Configuration ---
# The application is now hardcoded to use the local API for the demo.
ACTUAL_API_URL = "http://localhost:8080"

# Sample bond data for the demo.
SAMPLE_BONDS = {
    "US TREASURY N/B, 3% 08/15/2052": {
        "isin": "US912810TJ79",
        "price": 71.66,
        "maturity": "2052-08-15",
        "coupon": 3.0
    },
    "GENERIC GOVT BOND, 2.5% 12/31/2045": {
        "isin": None, # Intentionally missing ISIN
        "price": 95.50,
        "maturity": "2045-12-31",
        "coupon": 2.5
    },
    "GALAXY PIPELINE, 3.25% 09/30/2040": {
        "isin": "XS2249741674",
        "price": 77.88,
        "maturity": "2040-09-30",
        "coupon": 3.25
    },
    "ABU DHABI CRUDE, 4.6% 11/02/2047": {
        "isin": "XS1709535097",
        "price": 89.40,
        "maturity": "2047-11-02",
        "coupon": 4.6
    },
}

def format_metric(value, prefix="", suffix="", precision=2, is_na_value="N/A"):
    """Helper function to format metrics, handling potential None or non-numeric values."""
    if value is None or not isinstance(value, (int, float)):
        return is_na_value
    return f"{prefix}{value:.{precision}f}{suffix}"

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(
        page_title="🏛️ Bond Analysis API Demo",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- Custom CSS for larger fonts ---
    st.markdown("""
    <style>
    /* Increase base font size for better readability */
    html, body, [class*="st-"] {
        font-size: 1.25rem;
    }
    /* Increase header sizes for presentation */
    h1 {
        font-size: 3.5rem !important;
    }
    h2 {
        font-size: 2.75rem !important;
    }
    h3 {
        font-size: 2.25rem !important;
    }
    /* Increase metric label and value sizes */
    .stMetric .st-emotion-cache-1g8m5k5 { /* Metric Label */
        font-size: 1.5rem !important;
        font-weight: bold;
    }
    .stMetric .st-emotion-cache-1d3w3z3 { /* Metric Value */
        font-size: 3.0rem !important;
    }
    /* Increase font size for dataframes */
    .stDataFrame {
        font-size: 1.2rem;
    }
    /* Increase font size for json and code blocks */
    pre, code {
        font-size: 1.2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)


    st.title("🏛️ Bond Analysis API Demo")
    st.markdown("**Institutional-Grade QuantLib Calculations via API**")

    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("##### API URL:")
        st.code(ACTUAL_API_URL, language="text")
        
        st.markdown("---")
        
        st.header("📋 Bond Selection")
        selected_bond_name = st.selectbox(
            "Select a Bond:",
            options=list(SAMPLE_BONDS.keys()),
            index=0
        )
        
        bond_info = SAMPLE_BONDS[selected_bond_name]
        st.markdown("##### Bond Details:")
        st.dataframe(pd.DataFrame([{
            "ISIN": bond_info["isin"] if bond_info["isin"] else "N/A",
            "Price": f"${bond_info['price']}",
            "Maturity": bond_info["maturity"],
            "Coupon": f"{bond_info['coupon']}%"
        }]), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.header("🔧 Payload Options")
        force_no_isin = st.checkbox(
            "Force ISIN-less Request", 
            help="Send a null ISIN to test the API's parsing capabilities, even if an ISIN is available."
        )

        st.markdown("---")
        st.info(f"This demo is configured to call the local API.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📋 Request Details")
        
        payload_isin = bond_info["isin"] if not force_no_isin else None
        
        api_payload = {
            "description": selected_bond_name,
            "isin": payload_isin,
            "price": bond_info["price"],
            "request_id": f"demo_{int(datetime.now().timestamp())}"
        }
        
        st.markdown("##### API Payload (Request Body):")
        st.json(api_payload)

        st.markdown("##### API Request Example:")
        curl_command = f"""curl -X POST {ACTUAL_API_URL}/api/v1/bond/parse-and-calculate \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(api_payload, indent=2)}'"""
        st.code(curl_command, language="bash")


    with col2:
        st.header("🚀 API Interaction & Results")
        
        if st.button("Analyze Bond", type="primary", use_container_width=True):
            api_call_url = f"{ACTUAL_API_URL}/api/v1/bond/parse-and-calculate"
            with st.spinner(f"Calling local API at {ACTUAL_API_URL}..."):
                try:
                    response = requests.post(
                        api_call_url,
                        json=api_payload,
                        timeout=30,
                        headers={"Content-Type": "application/json"}
                    )
                    st.session_state.response = response
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error to {ACTUAL_API_URL}: {e}")
                    st.info("Please ensure your local API server is running.")
                    st.session_state.response = None
        
        if 'response' in st.session_state and st.session_state.response is not None:
            response = st.session_state.response
            if response.status_code == 200:
                st.success("API Call Successful!")
                result = response.json()
                
                # --- REMOVED KEY METRICS AND TABS ---
                st.markdown("##### Raw JSON Response:")
                st.json(result)

            else:
                st.error(f"API Error: {response.status_code}")
                st.code(response.text, language="text")

if __name__ == "__main__":
    main()
