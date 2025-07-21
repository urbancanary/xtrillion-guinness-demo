#!/usr/bin/env python3
"""
Create a direct Treasury API endpoint that uses Method 3
"""

from flask import Flask, request, jsonify
import sys
sys.path.append('.')
from treasury_method3_debug import calculate_treasury_with_debug

app = Flask(__name__)

@app.route('/api/v1/treasury/calculate', methods=['POST'])
def calculate_treasury_method3():
    """
    Direct Treasury calculation using Method 3
    
    Request:
    {
        "description": "US TREASURY N/B 3 15/08/2052",
        "price": 71.66,
        "settlement_date": "2025-06-30"
    }
    """
    try:
        data = request.get_json()
        
        description = data.get('description', 'US TREASURY N/B, 3%, 15-Aug-2052')
        price = data.get('price', 71.66)
        settlement_date = data.get('settlement_date', '2025-06-30')
        
        print(f"🏛️ Method 3 Treasury calculation for: {description}")
        
        result = calculate_treasury_with_debug(description, price, settlement_date)
        
        return jsonify({
            'status': 'success',
            'method': 'Method 3 - QuantLib with proper issue date',
            'bond': {
                'description': description,
                'price': price,
                'settlement_date': settlement_date
            },
            'results': {
                'yield_percent': round(result['yield'], 5),
                'duration_years': round(result['duration'], 5),
                'accrued_dollar': round(result['accrued'], 4),
                'days_accrued': result['days_accrued'],
                'accrued_per_million': round(result['accrued_per_million'], 2)
            },
            'bloomberg_comparison': {
                'expected_duration': result['expected_duration'],
                'expected_accrued_per_million': result['expected_accrued_per_million'],
                'duration_diff': round(result['duration_diff'], 8),
                'accrued_per_million_diff': round(result['accrued_per_million_diff'], 3)
            },
            'debug_info': {
                'settlement_method': 'Prior month end (institutional standard)',
                'issue_date_calculation': 'QuantLib automatic from maturity pattern',
                'schedule_method': 'From issue date (Method 3)',
                'day_count': 'ActualActual(Bond)',
                'frequency': 'Semiannual'
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Treasury Method 3 API',
        'capabilities': [
            'Method 3 Treasury calculations',
            'Proper issue date handling',
            'Debug information (days accrued, accrued per million)',
            'Bloomberg comparison metrics'
        ]
    })

if __name__ == '__main__':
    print("🏛️ Starting Treasury Method 3 API on port 8081...")
    app.run(host='0.0.0.0', port=8081, debug=False)
