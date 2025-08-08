#!/usr/bin/env python3
"""
Test Results Endpoint
Provides API endpoint to view test results and run tests
"""

from flask import Flask, jsonify, request
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

@app.route('/test/status', methods=['GET'])
def get_test_status():
    """Get latest test results"""
    try:
        # Find most recent test results
        result_files = list(Path('.').glob('test_results_production_*.json'))
        if not result_files:
            return jsonify({
                "status": "error",
                "message": "No test results found"
            }), 404
        
        latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            test_data = json.load(f)
        
        # Add baseline comparison results if available
        baseline_file = Path('baseline_comparison_2025-08-07.json')
        if baseline_file.exists():
            with open(baseline_file, 'r') as f:
                baseline_data = json.load(f)
            test_data['baseline_comparison'] = baseline_data
        
        return jsonify(test_data)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/test/run', methods=['POST'])
def run_tests():
    """Run test suite and return results"""
    try:
        # Run the test suite
        result = subprocess.run(
            ['python3', 'daily_test_suite.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Load the results
        result_files = list(Path('.').glob('test_results_production_*.json'))
        latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            test_results = json.load(f)
        
        return jsonify({
            "status": "success",
            "test_results": test_results,
            "stdout": result.stdout[-1000:],  # Last 1000 chars of output
            "return_code": result.returncode
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "error",
            "message": "Test execution timed out"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/test/treasury', methods=['GET'])
def test_treasury():
    """Quick test of US Treasury with fixed settlement date"""
    import requests
    
    api_url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    api_key = "gax10_demo_3j5h8m9k2p6r4t7w1q"
    
    payload = {
        "description": "T 3 15/08/52",
        "price": 71.66,
        "settlement_date": "2025-06-30"
    }
    
    try:
        response = requests.post(
            api_url,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            analytics = data.get('analytics', {})
            
            # Compare with expected values
            expected = {
                "ytm": 4.898837,
                "duration": 16.350751,
                "settlement_date": "2025-06-30"
            }
            
            actual = {
                "ytm": round(analytics.get('ytm', 0), 6),
                "duration": round(analytics.get('duration', 0), 6),
                "settlement_date": analytics.get('settlement_date')
            }
            
            matches = all(
                abs(actual.get(k, 0) - expected[k]) < 0.000001 
                for k in ['ytm', 'duration']
            ) and actual['settlement_date'] == expected['settlement_date']
            
            return jsonify({
                "status": "success",
                "bond": "US Treasury 3% 15/08/52",
                "expected": expected,
                "actual": actual,
                "matches": matches,
                "full_response": data
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"API returned status {response.status_code}",
                "response": response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/test/baseline', methods=['GET'])
def get_baseline():
    """Get current baseline values"""
    try:
        baseline_file = Path('calculation_baseline.json')
        if not baseline_file.exists():
            return jsonify({
                "status": "error",
                "message": "No baseline found"
            }), 404
            
        with open(baseline_file, 'r') as f:
            baseline = json.load(f)
        
        # Format for easy reading
        formatted = []
        for key, value in baseline.items():
            formatted.append({
                "bond": value['name'],
                "settlement_date": value['request']['settlement_date'],
                "price": value['request']['price'],
                "ytm": value['metrics']['ytm'],
                "duration": value['metrics']['duration'],
                "accrued_interest": value['metrics']['accrued_interest']
            })
        
        return jsonify({
            "status": "success",
            "baseline_date": datetime.now().isoformat(),
            "settlement_date": "2025-06-30",
            "bonds": formatted
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)