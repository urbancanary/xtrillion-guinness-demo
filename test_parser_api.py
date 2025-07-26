#!/usr/bin/env python3
"""
Simple Test API to verify enhanced bond parsing works
"""

from flask import Flask, request, jsonify
from bond_description_parser import SmartBondParser
import traceback

app = Flask(__name__)

# Initialize parser
parser = SmartBondParser(
    db_path='bonds_data.db',
    validated_db_path='validated_quantlib_bonds.db'
)

@app.route('/test/parse', methods=['POST'])
def test_parse():
    """Simple test endpoint for parsing only"""
    try:
        data = request.get_json()
        description = data.get('description', '')
        
        print(f"🧪 Testing description: {description}")
        
        # Test parsing
        parsed = parser.parse_bond_description(description)
        print(f"📋 Parsed result: {parsed}")
        
        if not parsed:
            return jsonify({
                'error': 'Parsing failed',
                'description': description,
                'status': 'parse_failed'
            })
        
        # Test ticker extraction
        ticker = parser.extract_ticker_from_parsed_bond(parsed)
        print(f"🎯 Ticker: {ticker}")
        
        # Test conventions
        conventions = parser.predict_most_likely_conventions(parsed)
        print(f"⚙️ Conventions: {conventions}")
        
        return jsonify({
            'description': description,
            'parsed': parsed,
            'ticker': ticker,
            'conventions': conventions,
            'status': 'success'
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'status': 'error'
        })

@app.route('/test/health', methods=['GET'])
def health():
    return jsonify({'status': 'Test API running', 'parser': 'SmartBondParser loaded'})

if __name__ == '__main__':
    print("🧪 Starting Test Bond Parser API on port 8082...")
    app.run(host='0.0.0.0', port=8082, debug=True)
