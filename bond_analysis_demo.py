import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# --- Configuration ---
DEFAULT_API_URL = "https://future-footing-414610.ue.r.appspot.com"  # 🌐 LIVE APP ENGINE API

SAMPLE_BONDS = {
    "US TREASURY N/B, 3% 08/15/2052": {
        "isin": "US912810TJ79",
        "price": 71.66,
        "maturity": "2052-08-15",
        "coupon": 3.0,
        "issue_date": "2022-08-15"
    },
    "GENERIC GOVT BOND, 2.5% 12/31/2045": {
        "isin": None, # Intentionally missing ISIN
        "price": 95.50,
        "maturity": "2045-12-31",
        "coupon": 2.5,
        "issue_date": "2015-12-31"
    },
    "GALAXY PIPELINE, 3.25% 09/30/2040": {
        "isin": "XS2249741674",
        "price": 77.88,
        "maturity": "2040-09-30",
        "coupon": 3.25,
        "issue_date": "2020-09-30"
    },
    "ABU DHABI CRUDE, 4.6% 11/02/2047": {
        "isin": "XS1709535097",
        "price": 89.40,
        "maturity": "2047-11-02",
        "coupon": 4.6,
        "issue_date": "2017-11-02"
    },
    "COLOMBIA REP OF, 3.875% 02/15/2061": {
        "isin": "US195325DX04",
        "price": 52.71,
        "maturity": "2061-02-15",
        "coupon": 3.875,
        "issue_date": "2021-02-15"
    }
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
    </style>
    """, unsafe_allow_html=True)


    st.title("🏛️ Bond Analysis API Demo - LOCAL")
    st.markdown("**Institutional-Grade QuantLib Calculations via LOCAL API**")

    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_url = st.text_input("API Base URL", value=DEFAULT_API_URL)
        trade_date = st.date_input("Trade Date (T)", value=datetime(2025, 6, 30))
        
        # API Health Check
        if st.button("🔍 Check API Health"):
            try:
                health_response = requests.get(f"{api_url}/health", timeout=5)
                if health_response.status_code == 200:
                    st.success("✅ API is running!")
                    st.json(health_response.json())
                else:
                    st.error(f"❌ API Error: {health_response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection Error: {e}")
                st.info("💡 Make sure to run: ./start_ga10_portfolio_api.sh")
        
        st.markdown("---")
        
        st.header("📋 Bond Selection")
        selected_bond_name = st.selectbox(
            "Select a Bond:",
            options=list(SAMPLE_BONDS.keys()),
            index=0
        )
        
        # --- Bond Details moved to sidebar ---
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
        st.markdown("**Available Endpoints:**")
        st.code("/api/v1/bond/parse-and-calculate\n/health\n/api/v1/portfolio/analyze", language="text")
        st.info("🏠 This demo uses the LOCAL API server. Make sure it's running!")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📋 Request Details")
        
        # Determine the ISIN for the payload based on the checkbox
        payload_isin = bond_info["isin"] if not force_no_isin else None
        
        api_payload = {
            "description": selected_bond_name,
            "isin": payload_isin,
            "price": bond_info["price"],
            "trade_date": trade_date.strftime("%Y-%m-%d"),
            "issue_date": bond_info["issue_date"],
            "request_id": f"demo_{int(datetime.now().timestamp())}"
        }
        
        st.markdown("##### API Payload (Request Body):")
        st.json(api_payload)

        st.markdown("##### Curl Command:")
        curl_command = f"""curl -X POST {api_url}/api/v1/bond/parse-and-calculate \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(api_payload, indent=2)}'"""
        st.code(curl_command, language="bash")


    with col2:
        st.header("🚀 API Interaction & Results")
        
        if st.button("🔬 Analyze Bond", type="primary", use_container_width=True):
            with st.spinner(f"Calling LOCAL API at {api_url}..."):
                try:
                    response = requests.post(
                        f"{api_url}/api/v1/bond/parse-and-calculate",
                        json=api_payload,
                        timeout=30,
                        headers={"Content-Type": "application/json"}
                    )
                    st.session_state.response = response
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: {e}")
                    st.error("💡 Make sure the API is running: ./start_ga10_portfolio_api.sh")
                    st.session_state.response = None
        
        if st.button("📊 Test Portfolio Analysis", use_container_width=True):
            portfolio_payload = {
                "bonds": [
                    {
                        "isin": "US912810TJ79",
                        "price": 71.66,
                        "weight": 0.4,
                        "description": "US TREASURY N/B, 3% 08/15/2052"
                    },
                    {
                        "isin": "XS2249741674", 
                        "price": 77.88,
                        "weight": 0.3,
                        "description": "GALAXY PIPELINE, 3.25% 09/30/2040"
                    },
                    {
                        "isin": "US195325DX04",
                        "price": 52.71,
                        "weight": 0.3,
                        "description": "COLOMBIA REP OF, 3.875% 02/15/2061"
                    }
                ],
                "trade_date": trade_date.strftime("%Y-%m-%d"),
                "request_id": f"portfolio_demo_{int(datetime.now().timestamp())}"
            }
            
            with st.spinner("Analyzing Portfolio..."):
                try:
                    response = requests.post(
                        f"{api_url}/api/v1/portfolio/analyze",
                        json=portfolio_payload,
                        timeout=60,
                        headers={"Content-Type": "application/json"}
                    )
                    st.session_state.portfolio_response = response
                except requests.exceptions.RequestException as e:
                    st.error(f"Portfolio Analysis Error: {e}")
                    st.session_state.portfolio_response = None
        
        # Display individual bond results
        if 'response' in st.session_state and st.session_state.response is not None:
            response = st.session_state.response
            if response.status_code == 200:
                st.success("✅ API Call Successful!")
                result = response.json()
                
                tab1, tab2 = st.tabs(["📊 Key Metrics", "📋 Raw JSON Response"])
                
                with tab1:
                    bond_data = result.get('bond_data', {})
                    metrics_col1, metrics_col2 = st.columns(2)
                    with metrics_col1:
                        st.metric("Yield to Maturity", format_metric(bond_data.get('yield'), suffix="%"))
                        st.metric("Modified Duration", format_metric(bond_data.get('duration'), suffix=" years"))
                    with metrics_col2:
                        st.metric("Spread", format_metric(bond_data.get('spread'), suffix=" bps", precision=0))
                        st.metric("Accrued Interest", format_metric(bond_data.get('accrued_interest'), prefix="$", precision=4))
                    
                    metadata = result.get('metadata', {})
                    st.markdown("**Calculation Info:**")
                    st.dataframe(pd.DataFrame([{
                        "ISIN Used": result.get('isin', 'N/A'),
                        "Data Source": metadata.get('data_source', 'N/A'),
                        "Settlement Date": metadata.get('settlement_date', 'N/A')
                    }]), use_container_width=True, hide_index=True)
                
                with tab2:
                    st.json(result)
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.code(response.text, language="text")
        
        # Display portfolio results
        if 'portfolio_response' in st.session_state and st.session_state.portfolio_response is not None:
            response = st.session_state.portfolio_response
            st.markdown("---")
            st.subheader("📊 Portfolio Analysis Results")
            if response.status_code == 200:
                st.success("✅ Portfolio Analysis Successful!")
                result = response.json()
                
                portfolio_metrics = result.get('portfolio_metrics', {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Portfolio Yield", format_metric(portfolio_metrics.get('weighted_yield'), suffix="%"))
                with col2:
                    st.metric("Portfolio Duration", format_metric(portfolio_metrics.get('weighted_duration'), suffix=" years"))
                with col3:
                    st.metric("Total Value", format_metric(portfolio_metrics.get('total_market_value'), prefix="$", precision=0))
                
                st.json(result)
            else:
                st.error(f"❌ Portfolio API Error: {response.status_code}")
                st.code(response.text, language="text")

if __name__ == "__main__":
    main()
