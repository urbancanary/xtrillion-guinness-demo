#!/usr/bin/env python3
"""
Improved Mac Excel Bond API Bridge
Better error handling and diagnostics
"""

import requests
import json
import time
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser

# Cloud API Configuration with fallbacks
PRIMARY_API = "https://future-footing-414610.uc.r.appspot.com"
FALLBACK_API = "https://api.x-trillion.ai"  # Alternative endpoint
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

# Global variable to store working API URL
WORKING_API = None

class ImprovedBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests with better error handling"""
        
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Send headers
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if parsed_url.path == '/':
            # Web interface
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Mac Excel Bond API Bridge</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .working {{ color: green; font-weight: bold; }}
                    .example {{ background: #f0f8ff; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
                    .code {{ background: #f5f5f5; padding: 10px; font-family: monospace; font-size: 14px; }}
                    .test-link {{ display: inline-block; margin: 5px; padding: 10px; background: #e3f2fd; border-radius: 5px; text-decoration: none; color: #1976d2; }}
                    .test-link:hover {{ background: #bbdefb; }}
                </style>
            </head>
            <body>
                <h1>🍎 Mac Excel Bond API Bridge</h1>
                <h2 class="working">✅ Bridge is Running Successfully!</h2>
                <p><strong>Local Server:</strong> http://localhost:8888</p>
                <p><strong>Cloud API:</strong> <span class="working">{WORKING_API}</span></p>
                
                <h3>📊 How to Use in Mac Excel</h3>
                <div class="example">
                    <h4>Step 1: Copy these URLs into Excel cells</h4>
                    <div class="code">
                    Treasury Yield:<br>
                    http://localhost:8888/yield?bond=T 3 15/08/52&price=71.66<br><br>
                    
                    Treasury Duration:<br>
                    http://localhost:8888/duration?bond=T 3 15/08/52&price=71.66<br><br>
                    
                    Corporate Bond Spread:<br>
                    http://localhost:8888/spread?bond=ECOPETROL SA, 5.875%, 28-May-2045&price=69.31
                    </div>
                </div>
                
                <div class="example">
                    <h4>Step 2: For Dynamic Analysis (Reference Excel Cells)</h4>
                    <div class="code">
                    ="http://localhost:8888/yield?bond=" & A2 & "&price=" & B2<br>
                    ="http://localhost:8888/duration?bond=" & A2 & "&price=" & B2<br>
                    ="http://localhost:8888/spread?bond=" & A2 & "&price=" & B2
                    </div>
                    <p>Where A2 = bond description, B2 = price</p>
                </div>
                
                <h3>🧪 Test the Bridge</h3>
                <a href="/test" class="test-link">Test Connection</a>
                <a href="/yield?bond=T 3 15/08/52&price=71.66" class="test-link">Test Treasury Yield</a>
                <a href="/duration?bond=T 3 15/08/52&price=71.66" class="test-link">Test Duration</a>
                <a href="/spread?bond=ECOPETROL SA, 5.875%, 28-May-2045&price=69.31" class="test-link">Test Spread</a>
                
                <h3>📈 Expected Results</h3>
                <ul>
                    <li><strong>Treasury Yield:</strong> ~4.899</li>
                    <li><strong>Treasury Duration:</strong> ~16.35</li>
                    <li><strong>ECOPETROL Spread:</strong> ~445</li>
                </ul>
                
                <h3>⏹️ To Stop</h3>
                <p>Press <strong>Ctrl+C</strong> in terminal</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            return
            
        elif parsed_url.path == '/test':
            response = "BRIDGE_WORKING_PERFECTLY"
            
        elif parsed_url.path == '/yield':
            response = self.get_bond_metric(query_params, 'ytm')
            
        elif parsed_url.path == '/duration':
            response = self.get_bond_metric(query_params, 'duration')
            
        elif parsed_url.path == '/spread':
            response = self.get_bond_metric(query_params, 'spread')
            
        elif parsed_url.path == '/accrued':
            response = self.get_bond_metric(query_params, 'accrued_interest')
            
        else:
            response = "UNKNOWN_ENDPOINT"
        
        self.wfile.write(str(response).encode())
    
    def get_bond_metric(self, query_params, metric):
        """Get bond metric with better error handling"""
        try:
            bond_desc = query_params.get('bond', [''])[0]
            price = float(query_params.get('price', ['100'])[0])
            
            if not bond_desc:
                return "ERROR_MISSING_BOND"
            
            # Call API with retries
            api_response = call_cloud_api_with_retry(bond_desc, price)
            
            if api_response.get('status') == 'success':
                analytics = api_response.get('analytics', {})
                value = analytics.get(metric)
                
                if value is None:
                    return "NULL"
                elif isinstance(value, (int, float)):
                    return f"{value:.6f}"
                else:
                    return str(value)
            else:
                error_msg = api_response.get('error', 'UNKNOWN_ERROR')
                return f"API_ERROR_{error_msg}".replace(' ', '_')
                
        except Exception as e:
            return f"ERROR_{str(e).replace(' ', '_')}"
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging"""
        pass

def test_api_endpoint(api_url, timeout=10):
    """Test if an API endpoint is working"""
    try:
        print(f"🔍 Testing {api_url}...")
        response = requests.get(f"{api_url}/health", timeout=timeout)
        
        if response.status_code == 200:
            health_data = response.json()
            service_name = health_data.get('service', 'Unknown')
            version = health_data.get('version', 'Unknown')
            print(f"✅ {api_url} is working!")
            print(f"   Service: {service_name}")
            print(f"   Version: {version}")
            return True
        else:
            print(f"❌ {api_url} returned status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ {api_url} timed out (slow connection)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"🔌 {api_url} connection failed (network issue)")
        return False
    except Exception as e:
        print(f"❌ {api_url} error: {e}")
        return False

def find_working_api():
    """Test API endpoints and find one that works"""
    global WORKING_API
    
    print("🔍 Finding working API endpoint...")
    
    # Test primary API
    if test_api_endpoint(PRIMARY_API):
        WORKING_API = PRIMARY_API
        return True
    
    # Test fallback API
    print("\n🔄 Trying fallback endpoint...")
    if test_api_endpoint(FALLBACK_API):
        WORKING_API = FALLBACK_API
        return True
    
    # If both fail, wait and retry primary
    print("\n⏳ Both endpoints failed. Waiting 5 seconds and retrying...")
    time.sleep(5)
    
    if test_api_endpoint(PRIMARY_API, timeout=15):
        WORKING_API = PRIMARY_API
        return True
    
    print("❌ All API endpoints failed")
    return False

def call_cloud_api_with_retry(description, price, max_retries=3):
    """Call cloud API with retry logic"""
    for attempt in range(max_retries):
        try:
            url = f"{WORKING_API}/api/v1/bond/analysis"
            
            payload = {
                "description": description,
                "price": price
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": API_KEY
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️  API call failed (attempt {attempt + 1}), retrying...")
                time.sleep(2)
            else:
                return {"status": "error", "error": str(e)}

def test_bond_calculation():
    """Test a bond calculation"""
    try:
        print("🧪 Testing bond calculation...")
        api_response = call_cloud_api_with_retry("T 3 15/08/52", 71.66)
        
        if api_response.get('status') == 'success':
            analytics = api_response.get('analytics', {})
            yield_val = analytics.get('ytm', 0)
            duration_val = analytics.get('duration', 0)
            
            print(f"✅ Bond calculation working perfectly!")
            print(f"   Treasury Yield: {yield_val:.6f}%")
            print(f"   Treasury Duration: {duration_val:.6f} years")
            return True
        else:
            print(f"❌ Bond calculation failed: {api_response.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Bond calculation error: {e}")
        return False

def start_server():
    """Start the bridge server"""
    server = HTTPServer(('localhost', 8888), ImprovedBridgeHandler)
    
    print("\n🌉 Mac Excel Bond API Bridge Starting...")
    print("📍 Local Server: http://localhost:8888")
    print(f"🌐 Cloud API: {WORKING_API}")
    print("\n📊 Ready for Mac Excel!")
    print("   Copy these URLs into Excel cells:")
    print("   • http://localhost:8888/yield?bond=T 3 15/08/52&price=71.66")
    print("   • http://localhost:8888/duration?bond=T 3 15/08/52&price=71.66")
    print("\n🌐 Opening web interface...")
    print("⏹️  Press Ctrl+C to stop")
    
    # Open browser
    try:
        time.sleep(1)
        webbrowser.open("http://localhost:8888")
    except:
        print("   (Could not auto-open browser)")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Bridge server stopped")
        server.shutdown()

if __name__ == "__main__":
    print("🍎 Mac Excel Bond API Bridge")
    print("=" * 50)
    
    # Find working API
    if find_working_api():
        print(f"\n✅ Using API: {WORKING_API}")
        
        # Test bond calculation
        if test_bond_calculation():
            print("\n🚀 Starting bridge server...")
            start_server()
        else:
            print("⚠️  Bridge ready but bond calculations need attention")
            print("   Starting server anyway for testing...")
            start_server()
    else:
        print("\n❌ Cannot connect to any API endpoint")
        print("   Possible issues:")
        print("   • Internet connection problems")
        print("   • API servers temporarily down")
        print("   • Firewall blocking requests")
        print("\n🔄 You can try running the script again in a few minutes")
        sys.exit(1)