import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Configuration - CLOUD DEPLOYMENT
API_BASE_URL = "https://xtrillion-ga10-44056503414.us-central1.run.app"  # Your actual Cloud Run URL

# Alternative URLs for testing:
# API_BASE_URL = "http://localhost:8080"              # For local testing only

# Sample bonds from your documents
SAMPLE_BONDS = {
    "US TREASURY N/B, 3%": {
        "isin": "US912810TJ79",
        "price": 71.66,
        "maturity": "2052-08-15",
        "coupon": 3.0
    },
    "GALAXY PIPELINE, 3.25%": {
        "isin": "XS2249741674", 
        "price": 77.88,
        "maturity": "2040-09-30",
        "coupon": 3.25
    },
    "ABU DHABI CRUDE, 4.6%": {
        "isin": "XS1709535097",
        "price": 89.40,
        "maturity": "2047-11-02", 
        "coupon": 4.6
    },
    "SAUDI ARAB OIL, 4.25%": {
        "isin": "XS1982113463",
        "price": 87.14,
        "maturity": "2039-04-16",
        "coupon": 4.25
    },
    "EMPRESA METRO, 4.7%": {
        "isin": "USP37466AS18",
        "price": 80.39,
        "maturity": "2050-05-07",
        "coupon": 4.7
    }
}

def main():
    st.set_page_config(
        page_title="🏛️ Bond Analysis API Demo",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("🏛️ Bond Analysis API Demo")
    st.markdown("**Professional QuantLib Bond Calculations**")
    
    # Sidebar for API settings
    with st.sidebar:
        st.header("⚙️ API Configuration")
        
        # Cloud URL configuration
        st.markdown("**Cloud Deployment URLs:**")
        default_urls = [
            "https://xtrillion-ga10-YOUR-PROJECT-ID.a.run.app",
            "https://api.urbancanary.com/bonds", 
            "http://localhost:8000"
        ]
        
        selected_url = st.selectbox(
            "Select API URL:",
            options=default_urls,
            index=0
        )
        
        # Allow custom URL input
        use_custom = st.checkbox("Use custom URL")
        if use_custom:
            api_url = st.text_input("Custom API URL", value=selected_url)
        else:
            api_url = selected_url
            
        settlement_date = st.date_input("Settlement Date", value=datetime(2025, 6, 30))
        
        st.markdown("---")
        st.markdown("**Available Endpoints:**")
        st.code("/api/v1/bond/parse-and-calculate")
        st.code("/health")
        st.code("/test")
        
        # Show current API URL
        st.markdown("---")
        st.markdown("**Current API:**")
        st.code(api_url, language="text")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📋 Bond Selection")
        
        # Bond dropdown
        selected_bond_name = st.selectbox(
            "Select a Bond:",
            options=list(SAMPLE_BONDS.keys()),
            index=0
        )
        
        # Show bond details
        bond_info = SAMPLE_BONDS[selected_bond_name]
        
        st.markdown("**Bond Details:**")
        details_df = pd.DataFrame([{
            "ISIN": bond_info["isin"],
            "Current Price": f"${bond_info['price']}",
            "Maturity": bond_info["maturity"], 
            "Coupon": f"{bond_info['coupon']}%"
        }])
        st.dataframe(details_df, use_container_width=True)
        
        # API payload for google_analysis9
        api_payload = {
            "description": f"{selected_bond_name}, {bond_info['maturity']}",
            "isin": bond_info["isin"],
            "price": bond_info["price"],
            "settlement_date": settlement_date.strftime("%Y-%m-%d"),
            "request_id": f"demo_{int(datetime.now().timestamp())}"
        }
        
        st.markdown("**API Payload:**")
        st.json(api_payload)
    
    with col2:
        st.header("🔧 API Testing")
        
        # Show curl command for cloud API (uses your actual URL)
        st.markdown("**Curl Command:**")
        curl_command = f"""curl -X POST {api_url}/api/v1/bond/parse-and-calculate \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(api_payload, indent=2)}'"""
        
        st.code(curl_command, language="bash")
        
        # Show the actual URL being used
        st.success(f"✅ Using API: {api_url}")
        
        # API call button
        if st.button("🚀 Analyze Bond", type="primary", use_container_width=True):
            with st.spinner("Calling Cloud API..."):
                try:
                    # Make API call to cloud endpoint
                    response = requests.post(
                        f"{api_url}/api/v1/bond/parse-and-calculate",
                        json=api_payload,
                        timeout=30,  # Longer timeout for cloud API
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ API Call Successful!")
                        result = response.json()
                        
                        # Display results in tabs
                        tab1, tab2, tab3 = st.tabs(["📊 Key Metrics", "📋 Raw Response", "🔍 Details"])
                        
                        with tab1:
                            # Handle google_analysis9 response format
                            if 'bond_data' in result:
                                bond_data = result['bond_data']
                                
                                # Key metrics display
                                metrics_col1, metrics_col2 = st.columns(2)
                                
                                with metrics_col1:
                                    ytm = bond_data.get('yield_to_maturity', bond_data.get('ytm', 'N/A'))
                                    duration = bond_data.get('modified_duration', bond_data.get('duration', 'N/A'))
                                    
                                    if ytm != 'N/A':
                                        st.metric("Yield to Maturity", f"{float(ytm):.2f}%")
                                    else:
                                        st.metric("Yield to Maturity", "N/A")
                                        
                                    if duration != 'N/A':
                                        st.metric("Modified Duration", f"{float(duration):.2f} years")
                                    else:
                                        st.metric("Modified Duration", "N/A")
                                
                                with metrics_col2:
                                    convexity = bond_data.get('convexity', 'N/A')
                                    accrued = bond_data.get('accrued_interest', 'N/A')
                                    
                                    if convexity != 'N/A':
                                        st.metric("Convexity", f"{float(convexity):.0f}")
                                    else:
                                        st.metric("Convexity", "N/A")
                                        
                                    if accrued != 'N/A':
                                        st.metric("Accrued Interest", f"${float(accrued):.2f}")
                                    else:
                                        st.metric("Accrued Interest", "N/A")
                                
                                # Show additional data
                                if 'metadata' in result:
                                    st.markdown("**Calculation Details:**")
                                    metadata = result['metadata']
                                    st.write(f"Convention: {metadata.get('day_count_convention', 'N/A')}")
                                    st.write(f"Settlement: {metadata.get('settlement_date', 'N/A')}")
                                    st.write(f"Data Source: {metadata.get('data_source', 'N/A')}")
                                    
                            elif 'yield_to_maturity' in result and 'duration' in result:
                                # Fallback for direct response format
                                metrics_col1, metrics_col2 = st.columns(2)
                                
                                with metrics_col1:
                                    st.metric(
                                        "Yield to Maturity",
                                        f"{result.get('yield_to_maturity', 'N/A'):.2f}%"
                                    )
                                    st.metric(
                                        "Modified Duration", 
                                        f"{result.get('duration', 'N/A'):.2f} years"
                                    )
                                
                                with metrics_col2:
                                    st.metric(
                                        "Convexity",
                                        f"{result.get('convexity', 'N/A'):.0f}"
                                    )
                                    st.metric(
                                        "Accrued Interest",
                                        f"${result.get('accrued_interest', 'N/A'):.2f}"
                                    )
                            else:
                                # Show whatever came back
                                st.json(result)
                        
                        with tab2:
                            st.json(result)
                        
                        with tab3:
                            if isinstance(result, dict):
                                details_df = pd.DataFrame([result])
                                st.dataframe(details_df, use_container_width=True)
                            else:
                                st.write("No detailed data available")
                    
                    else:
                        st.error(f"❌ API Error: {response.status_code}")
                        st.code(response.text)
                
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Connection Error: {str(e)}")
                    st.info("Make sure your API server is running!")
                except Exception as e:
                    st.error(f"❌ Unexpected Error: {str(e)}")
    
    # Health check and test section
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🏥 Health Check", use_container_width=True):
            try:
                response = requests.get(f"{api_url}/health", timeout=10)
                if response.status_code == 200:
                    st.success("✅ API is healthy!")
                    if response.text:
                        try:
                            st.json(response.json())
                        except:
                            st.text(response.text)
                else:
                    st.warning(f"⚠️ Health check returned: {response.status_code}")
            except:
                st.error("❌ API is not responding")
    
    with col2:
        if st.button("🧪 Test Endpoint", use_container_width=True):
            try:
                response = requests.get(f"{api_url}/test", timeout=10)
                if response.status_code == 200:
                    st.success("✅ Test endpoint working!")
                    if response.text:
                        try:
                            st.json(response.json())
                        except:
                            st.text(response.text)
                else:
                    st.warning(f"⚠️ Test returned: {response.status_code}")
            except:
                st.error("❌ Test endpoint not responding")
                
    with col3:
        if st.button("📊 API Version", use_container_width=True):
            try:
                response = requests.get(f"{api_url}/api/v1/version", timeout=10)
                if response.status_code == 200:
                    st.success("✅ Version info!")
                    if response.text:
                        try:
                            st.json(response.json())
                        except:
                            st.text(response.text)
                else:
                    st.warning(f"⚠️ Version returned: {response.status_code}")
            except:
                st.info("ℹ️ Version endpoint not available")

if __name__ == "__main__":
    main()