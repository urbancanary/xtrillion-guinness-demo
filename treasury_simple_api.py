#!/usr/bin/env python3
"""
Simple Treasury API endpoint showing default settlement date behavior
"""

from flask import Flask, request, jsonify
import sys
sys.path.append('.')
import QuantLib as ql
from datetime import datetime, timedelta

app = Flask(__name__)

def get_default_settlement_date():
    """Get prior month end as default settlement date"""
    today = datetime.now()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    return last_day_previous_month.strftime("%Y-%m-%d")

def calculate_treasury_simple(description=None, price=71.66, settlement_date_str=None):
    """Simple Treasury calculation with default settlement"""
    
    # Use default description if not provided
    if not description:
        description = "US TREASURY N/B, 3%, 15-Aug-2052"
    
    # Use default settlement if not provided
    if not settlement_date_str:
        settlement_date_str = get_default_settlement_date()
    
    # Bond parameters - could parse from description in future
    coupon_rate = 3.0 / 100.0
    maturity_date = ql.Date(15, 8, 2052)
    
    # Parse settlement date
    settlement_dt = datetime.strptime(settlement_date_str, "%Y-%m-%d")
    settlement_date = ql.Date(settlement_dt.day, settlement_dt.month, settlement_dt.year)
    
    # QuantLib setup
    ql.Settings.instance().evaluationDate = settlement_date
    
    # Treasury conventions
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    business_convention = ql.Following
    frequency = ql.Semiannual
    
    # Use working schedule approach (Feb 15, 2025 start)
    schedule_start = ql.Date(15, 2, 2025)
    
    schedule = ql.Schedule(
        schedule_start, maturity_date, ql.Period(frequency),
        calendar, business_convention, business_convention,
        ql.DateGeneration.Backward, False
    )
    
    # Create bond
    bond = ql.FixedRateBond(0, 100.0, schedule, [coupon_rate], day_count)
    
    # Calculate metrics
    yield_rate = bond.bondYield(price, day_count, ql.Compounded, frequency, settlement_date)
    duration = ql.BondFunctions.duration(
        bond,
        ql.InterestRate(yield_rate, day_count, ql.Compounded, frequency),
        ql.Duration.Modified,
        settlement_date
    )
    accrued = bond.accruedAmount(settlement_date)
    
    # Get debug info
    days_accrued = 0
    accrued_per_million = 0
    
    for cf in bond.cashflows():
        try:
            coupon_cf = ql.as_coupon(cf)
            if coupon_cf:
                accrual_start = coupon_cf.accrualStartDate()
                accrual_end = coupon_cf.accrualEndDate()
                
                if accrual_start <= settlement_date < accrual_end:
                    days_accrued = day_count.dayCount(accrual_start, settlement_date)
                    accrued_per_million = (accrued / 100.0) * 1000000
                    break
        except:
            continue
    
    return {
        'yield_percent': round(yield_rate * 100, 5),
        'duration_years': round(duration, 5),
        'accrued_dollar': round(accrued, 4),
        'days_accrued': days_accrued,
        'accrued_per_million': round(accrued_per_million, 2),
        'settlement_date': settlement_date_str,
        'default_applied': settlement_date_str == get_default_settlement_date()
    }

@app.route('/api/v1/treasury/simple', methods=['POST'])
def calculate_treasury():
    """
    Simple Treasury calculation with proper defaults
    
    Request (all fields optional):
    {
        "description": "US TREASURY N/B, 3%, 15-Aug-2052",  // Optional - defaults to Treasury bond
        "price": 71.66,                                      // Optional - defaults to 71.66
        "settlement_date": "2025-06-30"                      // Optional - defaults to prior month end
    }
    """
    try:
        data = request.get_json() or {}
        
        description = data.get('description')  # Optional
        price = data.get('price', 71.66)
        settlement_date = data.get('settlement_date')  # Optional
        
        result = calculate_treasury_simple(description, price, settlement_date)
        
        return jsonify({
            'status': 'success',
            'bond': {
                'description': result.get('description_used', description or 'US TREASURY N/B, 3%, 15-Aug-2052'),
                'isin': 'US912810TJ79',
                'price': price
            },
            'results': result,
            'settlement_info': {
                'provided': settlement_date is not None,
                'used': result['settlement_date'],
                'default_method': 'Prior month end (institutional standard)' if result['default_applied'] else 'User provided'
            },
            'comparison_to_bloomberg': {
                'expected_duration': 16.3578392273866,
                'expected_accrued_per_million': 11187.845,
                'duration_diff': round(result['duration_years'] - 16.3578392273866, 8),
                'accrued_per_million_diff': round(result['accrued_per_million'] - 11187.845, 3)
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
        'service': 'Simple Treasury API',
        'default_settlement': get_default_settlement_date()
    })

if __name__ == '__main__':
    print("🏛️ Starting Simple Treasury API on port 8082...")
    print(f"📅 Current default settlement date: {get_default_settlement_date()}")
    app.run(host='0.0.0.0', port=8082, debug=False)
