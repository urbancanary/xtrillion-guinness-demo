#!/usr/bin/env python3
"""
Mac Excel Bond API Bridge
Creates simple local server that Mac Excel can access easily
Run this script, then use simple HTTP calls in Excel
"""

import requests
import json
import csv
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import threading
import webbrowser
import time
from datetime import datetime

# Cloud API Configuration
CLOUD_API = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

class MacExcelBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests from Mac Excel or browser"""
        
        # Parse URL and query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Add CORS headers for Mac Excel
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')  # Plain text for Mac Excel
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if parsed_url.path == '/':
            # Home page with Mac Excel instructions
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Mac Excel Bond API Bridge</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .code {{ background: #f5f5f5; padding: 10px; font-family: monospace; }}
                    .example {{ background: #e8f4fd; padding: 15px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <h1>🍎 Mac Excel Bond API Bridge</h1>
                <h2>✅ Bridge is Running!</h2>
                <p><strong>Local Server:</strong> http://localhost:8888</p>
                <p><strong>Cloud API:</strong> {CLOUD_API}</p>
                
                <h3>📊 Excel Usage (Mac Compatible)</h3>
                <div class="example">
                    <h4>Simple Bond Yield:</h4>
                    <div class="code">
                    Copy this URL into Excel cell or browser:<br>
                    http://localhost:8888/yield?bond=T 3 15/08/52&price=71.66
                    </div>
                    <p>Expected result: <strong>4.898453</strong></p>
                </div>
                
                <div class="example">
                    <h4>Bond Duration:</h4>
                    <div class="code">
                    http://localhost:8888/duration?bond=T 3 15/08/52&price=71.66
                    </div>
                    <p>Expected result: <strong>16.357839</strong></p>
                </div>
                
                <div class="example">
                    <h4>Bond Spread:</h4>
                    <div class="code">
                    http://localhost:8888/spread?bond=ECOPETROL SA, 5.875%, 28-May-2045&price=69.31
                    </div>
                    <p>Expected result: <strong>445</strong></p>
                </div>
                
                <h3>🔗 Quick Test Links</h3>
                <p><a href="/test">Test Connection</a></p>
                <p><a href="/yield?bond=T 3 15/08/52&price=71.66">Treasury Yield</a></p>
                <p><a href="/duration?bond=T 3 15/08/52&price=71.66">Treasury Duration</a></p>
                <p><a href="/spread?bond=ECOPETROL SA, 5.875%, 28-May-2045&price=69.31">ECOPETROL Spread</a></p>
                
                <h3>📋 Bloomberg Comparison CSV</h3>
                <p><a href="/csv">Download Bloomberg Comparison Results</a></p>
                
                <h3>⏹️ To Stop Server</h3>
                <p>Press <strong>Ctrl+C</strong> in the terminal where you started this script</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            return
            
        elif parsed_url.path == '/test':
            # Simple test endpoint
            response = "API_BRIDGE_WORKING"
            
        elif parsed_url.path == '/yield':
            # Get bond yield
            response = self.get_bond_metric(query_params, 'ytm')
            
        elif parsed_url.path == '/duration':
            # Get bond duration
            response = self.get_bond_metric(query_params, 'duration')
            
        elif parsed_url.path == '/spread':
            # Get bond spread
            response = self.get_bond_metric(query_params, 'spread')
            
        elif parsed_url.path == '/accrued':
            # Get accrued interest
            response = self.get_bond_metric(query_params, 'accrued_interest')
            
        elif parsed_url.path == '/csv':
            # Generate Bloomberg comparison CSV
            response = self.generate_bloomberg_csv()
            self.send_header('Content-type', 'text/csv')
            self.send_header('Content-Disposition', 'attachment; filename="bloomberg_comparison.csv"')
            
        else:
            response = "UNKNOWN_ENDPOINT"
        
        # Send response
        self.wfile.write(str(response).encode())
    
    def get_bond_metric(self, query_params, metric):
        """Get specific bond metric from cloud API"""
        try:
            # Extract parameters
            bond_desc = query_params.get('bond', [''])[0]
            price = float(query_params.get('price', ['100'])[0])
            
            if not bond_desc:
                return "ERROR_MISSING_BOND"
            
            # Call cloud API
            cloud_response = call_cloud_api(bond_desc, price)
            
            if cloud_response.get('status') == 'success':
                analytics = cloud_response.get('analytics', {})
                
                # Return specific metric
                value = analytics.get(metric)
                
                if value is None:
                    return "NULL"
                elif isinstance(value, (int, float)):
                    return f"{value:.6f}"
                else:
                    return str(value)
            else:
                return "API_ERROR"
                
        except Exception as e:
            return f"ERROR_{str(e).replace(' ', '_')}"
    
    def generate_bloomberg_csv(self):
        """Generate Bloomberg comparison CSV"""
        bloomberg_bonds = [
            {"bond": "T 3 15/08/52", "price": 71.66, "bbg_yield": 4.898453, "bbg_duration": 16.357839, "bbg_spread": 0},
            {"bond": "ECOPETROL SA, 5.875%, 28-May-2045", "price": 69.31, "bbg_yield": 9.282266, "bbg_duration": 9.812703, "bbg_spread": 445},
            {"bond": "PANAMA, 3.87%, 23-Jul-2060", "price": 56.60, "bbg_yield": 7.362747, "bbg_duration": 13.488582, "bbg_spread": 253},
        ]
        
        csv_data = "Bond,Price,BBG_Yield,API_Yield,Yield_Diff,BBG_Duration,API_Duration,Duration_Diff,BBG_Spread,API_Spread,Spread_Diff,Status\n"
        
        for bond_data in bloomberg_bonds:
            try:
                # Get API data
                api_response = call_cloud_api(bond_data["bond"], bond_data["price"])
                
                if api_response.get('status') == 'success':
                    analytics = api_response.get('analytics', {})
                    
                    api_yield = analytics.get('ytm', 0)
                    api_duration = analytics.get('duration', 0)
                    api_spread = analytics.get('spread') or 0
                    
                    yield_diff = api_yield - bond_data["bbg_yield"]
                    duration_diff = api_duration - bond_data["bbg_duration"]
                    spread_diff = api_spread - bond_data["bbg_spread"]
                    
                    status = "PERFECT" if abs(yield_diff) < 0.001 and abs(duration_diff) < 0.001 else "DIFFERENCE"
                    
                    csv_data += f'"{bond_data["bond"]}",{bond_data["price"]},{bond_data["bbg_yield"]:.6f},{api_yield:.6f},{yield_diff:.6f},{bond_data["bbg_duration"]:.6f},{api_duration:.6f},{duration_diff:.6f},{bond_data["bbg_spread"]},{api_spread},{spread_diff},{status}\n'
                else:
                    csv_data += f'"{bond_data["bond"]}",{bond_data["price"]},{bond_data["bbg_yield"]},ERROR,ERROR,{bond_data["bbg_duration"]},ERROR,ERROR,{bond_data["bbg_spread"]},ERROR,ERROR,API_ERROR\n'
                    
            except Exception as e:
                csv_data += f'"{bond_data["bond"]}",{bond_data["price"]},{bond_data["bbg_yield"]},ERROR,ERROR,{bond_data["bbg_duration"]},ERROR,ERROR,{bond_data["bbg_spread"]},ERROR,ERROR,CALC_ERROR\n'
        
        return csv_data
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def call_cloud_api(description, price):
    """Call the cloud API"""
    try:
        url = f"{CLOUD_API}/api/v1/bond/analysis"
        
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
        return {"status": "error", "error": str(e)}

def test_cloud_connection():
    """Test cloud API connection"""
    try:
        print("🔍 Testing cloud API connection...")
        response = requests.get(f"{CLOUD_API}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Cloud API is healthy: {health_data.get('service', 'Unknown service')}")
            print(f"   Version: {health_data.get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ Cloud API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to cloud API: {e}")
        return False

def test_bond_calculation():
    """Test a simple bond calculation"""
    try:
        print("🧪 Testing bond calculation...")
        api_response = call_cloud_api("T 3 15/08/52", 71.66)
        
        if api_response.get('status') == 'success':
            analytics = api_response.get('analytics', {})
            yield_val = analytics.get('ytm', 'N/A')
            duration_val = analytics.get('duration', 'N/A')
            print(f"✅ Bond calculation working:")
            print(f"   US Treasury Yield: {yield_val:.6f}%")
            print(f"   US Treasury Duration: {duration_val:.6f} years")
            return True
        else:
            print(f"❌ Bond calculation failed: {api_response.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Bond calculation error: {e}")
        return False

def start_bridge_server():
    """Start the local bridge server"""
    server = HTTPServer(('localhost', 8888), MacExcelBridgeHandler)
    
    print("\n🌉 Mac Excel Bond API Bridge Starting...")
    print("📍 Local Server: http://localhost:8888")
    print(f"🌐 Cloud API: {CLOUD_API}")
    print("\n📊 Mac Excel Usage:")
    print("   In Excel, you can reference these URLs directly:")
    print("   • Yield: http://localhost:8888/yield?bond=T 3 15/08/52&price=71.66")
    print("   • Duration: http://localhost:8888/duration?bond=T 3 15/08/52&price=71.66")
    print("   • Spread: http://localhost:8888/spread?bond=ECOPETROL SA, 5.875%, 28-May-2045&price=69.31")
    print("\n🌐 Opening web interface...")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Bridge server stopped")
        server.shutdown()

if __name__ == "__main__":
    print("🍎 Starting Mac Excel Bond API Bridge")
    print("=" * 50)
    
    # Test cloud connection first
    if test_cloud_connection():
        # Test a bond calculation
        if test_bond_calculation():
            print("\n🚀 Starting local bridge server...")
            
            # Start server in background thread
            server_thread = threading.Thread(target=start_bridge_server, daemon=True)
            server_thread.start()
            
            # Open browser to show instructions
            time.sleep(2)
            try:
                webbrowser.open("http://localhost:8888")
            except:
                print("   (Could not auto-open browser - manually visit http://localhost:8888)")
            
            # Keep main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
        else:
            print("⚠️  Cannot start bridge - bond calculations not working")
    else:
        print("⚠️  Cannot start bridge - cloud API not accessible")
        print("   Check internet connection and try again")