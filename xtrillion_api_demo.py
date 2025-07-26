#!/usr/bin/env python3
"""
🚀 XTrillion API - Tuesday Demo Ready
===================================

Fast, context-aware bond analytics API using the blazing fast calculator.
Built for institutional-grade performance with sub-20ms response times.

DEMO ENDPOINTS:
- POST /v1/bond/calculate - Core bond calculations
- POST /v1/bond/portfolio - Portfolio-level calculations  
- GET /v1/bond/performance - Performance monitoring
- GET /v1/health - Health check

CONTEXTS SUPPORTED:
- pricing: Fast essential metrics (YTM, prices, accrued)
- risk: Risk metrics (duration, convexity)
- portfolio: Portfolio aggregation (annual basis)
- default: Balanced core metrics

PERFORMANCE TARGETS:
- pricing: <20ms
- risk: <50ms 
- portfolio: <100ms
"""

from flask import Flask, request, jsonify
import logging
import time
from datetime import datetime
from typing import Dict, Any, List

# Import our blazing fast calculator
from xtrillion_fast_calculator import XTrillionFastCalculator, BondData

# Setup Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global calculator instance (with caching)
calculator = XTrillionFastCalculator("2025-06-30")  # Prior month end

# API Statistics
api_stats = {
    "requests_total": 0,
    "requests_by_context": {},
    "average_response_times": {},
    "cache_hit_rate": 0,
    "errors": 0,
    "start_time": datetime.now().isoformat()
}

def update_api_stats(context: str, response_time_ms: float, cached: bool = False):
    """Update API performance statistics"""
    global api_stats
    
    api_stats["requests_total"] += 1
    
    if context not in api_stats["requests_by_context"]:
        api_stats["requests_by_context"][context] = 0
    api_stats["requests_by_context"][context] += 1
    
    if context not in api_stats["average_response_times"]:
        api_stats["average_response_times"][context] = []
    api_stats["average_response_times"][context].append(response_time_ms)
    
    # Keep only last 100 measurements for rolling average
    if len(api_stats["average_response_times"][context]) > 100:
        api_stats["average_response_times"][context] = api_stats["average_response_times"][context][-100:]

@app.route('/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "XTrillion API",
        "version": "1.0.0-demo",
        "timestamp": datetime.now().isoformat(),
        "calculator_ready": True,
        "caching_enabled": calculator.enable_caching
    })

@app.route('/v1/bond/calculate', methods=['POST'])
def calculate_bond():
    """
    🚀 Core bond calculation endpoint - optimized for Tuesday demo
    
    Request:
    {
        "description": "US TREASURY N/B, 3%, 15-Aug-2052",
        "price": 71.66,
        "context": "pricing",  // Optional: pricing, risk, portfolio, default
        "isin": "US912810TJ79"  // Optional
    }
    
    Response: Context-optimized bond metrics with performance timing
    """
    start_time = time.perf_counter()
    
    try:
        # Validate request
        if not request.is_json:
            api_stats["errors"] += 1
            return jsonify({
                "error": "Content-Type must be application/json",
                "status": "error"
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'description' not in data:
            api_stats["errors"] += 1
            return jsonify({
                "error": "Missing required field: description",
                "status": "error"
            }), 400
        
        # Extract parameters
        description = data['description']
        price = float(data.get('price', 100.0))
        context = data.get('context', 'default')
        isin = data.get('isin')
        
        # Validate context
        valid_contexts = ['pricing', 'risk', 'portfolio', 'spreads', 'default']
        if context not in valid_contexts:
            api_stats["errors"] += 1
            return jsonify({
                "error": f"Invalid context. Must be one of: {', '.join(valid_contexts)}",
                "status": "error"
            }), 400
        
        # Calculate using fast calculator
        logger.info(f"📊 Calculating: {description[:50]}... | Context: {context}")
        
        result = calculator.calculate_from_description(
            description=description,
            price=price,
            context=context,
            isin=isin
        )
        
        # Calculate API response time
        api_response_time = (time.perf_counter() - start_time) * 1000
        
        # Check for calculation errors
        if 'error' in result:
            api_stats["errors"] += 1
            logger.error(f"❌ Calculation error: {result['error']}")
            return jsonify({
                "error": f"Calculation failed: {result['error']}",
                "status": "error",
                "bond_info": result.get('bond_info', {}),
                "api_response_time_ms": round(api_response_time, 2)
            }), 500
        
        # Add API metadata
        result["api_metadata"] = {
            "api_response_time_ms": round(api_response_time, 2),
            "calculation_time_ms": result["calculation_metadata"]["calculation_time_ms"],
            "total_time_ms": round(api_response_time, 2),
            "cached": result["calculation_metadata"].get("cached", False),
            "context": context,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
        # Update statistics
        calc_time = result["calculation_metadata"]["calculation_time_ms"]
        cached = result["calculation_metadata"].get("cached", False)
        update_api_stats(context, calc_time, cached)
        
        # Performance logging
        target_ms = calculator.context_configs[context]["target_ms"]
        status = "✅" if calc_time <= target_ms else "⚠️"
        logger.info(f"{status} API response: {api_response_time:.1f}ms | Calc: {calc_time:.1f}ms | Target: {target_ms}ms")
        
        return jsonify(result)
        
    except ValueError as e:
        api_stats["errors"] += 1
        logger.error(f"❌ Validation error: {e}")
        return jsonify({
            "error": f"Invalid input: {str(e)}",
            "status": "error",
            "api_response_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }), 400
        
    except Exception as e:
        api_stats["errors"] += 1
        logger.error(f"❌ Unexpected error: {e}")
        return jsonify({
            "error": "Internal server error",
            "status": "error",
            "api_response_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }), 500

@app.route('/v1/bond/portfolio', methods=['POST'])
def calculate_portfolio():
    """
    Portfolio-level bond calculations with aggregation
    
    Request:
    {
        "bonds": [
            {
                "description": "US TREASURY N/B, 3%, 15-Aug-2052",
                "price": 71.66,
                "nominal": 1000000,
                "isin": "US912810TJ79"
            }
        ],
        "context": "portfolio"
    }
    
    Response: Individual bond calculations + portfolio aggregations
    """
    start_time = time.perf_counter()
    
    try:
        if not request.is_json:
            api_stats["errors"] += 1
            return jsonify({
                "error": "Content-Type must be application/json",
                "status": "error"
            }), 400
        
        data = request.get_json()
        
        if 'bonds' not in data:
            api_stats["errors"] += 1
            return jsonify({
                "error": "Missing required field: bonds",
                "status": "error"
            }), 400
        
        bonds = data['bonds']
        context = data.get('context', 'portfolio')
        
        if not bonds or not isinstance(bonds, list):
            api_stats["errors"] += 1
            return jsonify({
                "error": "bonds must be a non-empty list",
                "status": "error"
            }), 400
        
        logger.info(f"📈 Portfolio calculation: {len(bonds)} bonds | Context: {context}")
        
        # Calculate each bond
        portfolio_results = []
        portfolio_errors = []
        total_nominal = 0
        
        for i, bond in enumerate(bonds):
            try:
                # Validate bond data
                if 'description' not in bond:
                    portfolio_errors.append(f"Bond {i+1} missing description")
                    continue
                
                description = bond['description']
                price = float(bond.get('price', 100.0))
                nominal = float(bond.get('nominal', 1000000.0))
                isin = bond.get('isin')
                
                # Calculate individual bond
                bond_result = calculator.calculate_from_description(
                    description=description,
                    price=price,
                    context=context,
                    isin=isin
                )
                
                if 'error' not in bond_result:
                    bond_result['portfolio_data'] = {
                        'nominal': nominal,
                        'weight': None  # Will be calculated after all bonds processed
                    }
                    portfolio_results.append(bond_result)
                    total_nominal += nominal
                else:
                    portfolio_errors.append(f"Bond {i+1}: {bond_result['error']}")
                
            except Exception as e:
                portfolio_errors.append(f"Bond {i+1}: {str(e)}")
        
        # Calculate portfolio weights
        for result in portfolio_results:
            nominal = result['portfolio_data']['nominal']
            weight = nominal / total_nominal if total_nominal > 0 else 0
            result['portfolio_data']['weight'] = round(weight, 6)
        
        # Portfolio aggregations (if we have valid results)
        portfolio_aggregations = {}
        if portfolio_results:
            # Weighted average calculations for annual basis (safe for aggregation)
            total_weight = sum(r['portfolio_data']['weight'] for r in portfolio_results)
            
            if total_weight > 0:
                # Weighted average YTM (annual basis)
                weighted_ytm = sum(
                    r.get('pricing', {}).get('ytm_annual', r.get('pricing', {}).get('ytm_semi', 0)) * 
                    r['portfolio_data']['weight']
                    for r in portfolio_results
                )
                
                # Weighted average duration (annual basis) 
                weighted_duration = sum(
                    r.get('risk', {}).get('mod_dur_annual', r.get('risk', {}).get('mod_dur_semi', 0)) * 
                    r['portfolio_data']['weight']
                    for r in portfolio_results
                )
                
                portfolio_aggregations = {
                    "portfolio_ytm_annual": round(weighted_ytm, 6),
                    "portfolio_duration_annual": round(weighted_duration, 6),
                    "total_nominal": total_nominal,
                    "bond_count": len(portfolio_results),
                    "total_weight": round(total_weight, 6)
                }
        
        # API response time
        api_response_time = (time.perf_counter() - start_time) * 1000
        
        response = {
            "portfolio_results": portfolio_results,
            "portfolio_aggregations": portfolio_aggregations,
            "portfolio_errors": portfolio_errors,
            "api_metadata": {
                "api_response_time_ms": round(api_response_time, 2),
                "bonds_requested": len(bonds),
                "bonds_calculated": len(portfolio_results),
                "bonds_failed": len(portfolio_errors),
                "context": context,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Update statistics
        update_api_stats(f"portfolio_{len(bonds)}_bonds", api_response_time)
        
        logger.info(f"✅ Portfolio complete: {len(portfolio_results)}/{len(bonds)} bonds | {api_response_time:.1f}ms")
        
        return jsonify(response)
        
    except Exception as e:
        api_stats["errors"] += 1
        logger.error(f"❌ Portfolio calculation error: {e}")
        return jsonify({
            "error": "Portfolio calculation failed",
            "status": "error",
            "api_response_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }), 500

@app.route('/v1/bond/performance', methods=['GET'])
def get_performance():
    """Get API performance statistics"""
    global api_stats
    
    # Calculate average response times
    avg_times = {}
    for context, times in api_stats["average_response_times"].items():
        if times:
            avg_times[context] = {
                "average_ms": round(sum(times) / len(times), 2),
                "min_ms": round(min(times), 2),
                "max_ms": round(max(times), 2),
                "sample_size": len(times)
            }
    
    # Get calculator performance stats
    calc_stats = calculator.get_performance_stats()
    
    response = {
        "api_statistics": {
            **api_stats,
            "average_response_times": avg_times
        },
        "calculator_statistics": calc_stats,
        "performance_targets": {
            context: config["target_ms"] 
            for context, config in calculator.context_configs.items()
        },
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(response)

@app.route('/v1/bond/demo', methods=['GET'])
def demo_endpoint():
    """
    🚀 Demo endpoint for Tuesday presentation
    
    Returns pre-calculated examples showing different contexts
    """
    demo_bonds = [
        {
            "name": "US Treasury Long Bond",
            "description": "US TREASURY N/B, 3%, 15-Aug-2052",
            "price": 71.66,
            "isin": "US912810TJ79"
        },
        {
            "name": "Investment Grade Corporate",
            "description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", 
            "price": 87.14,
            "isin": "XS1982113463"
        },
        {
            "name": "Emerging Market",
            "description": "PANAMA, 3.87%, 23-Jul-2060",
            "price": 56.60,
            "isin": "US698299BL70"
        }
    ]
    
    demo_results = {}
    
    for bond in demo_bonds:
        bond_results = {}
        
        # Test different contexts
        for context in ['pricing', 'risk', 'portfolio']:
            start_time = time.perf_counter()
            
            result = calculator.calculate_from_description(
                description=bond["description"],
                price=bond["price"],
                context=context,
                isin=bond["isin"]
            )
            
            calc_time = (time.perf_counter() - start_time) * 1000
            
            bond_results[context] = {
                "calculation_time_ms": round(calc_time, 2),
                "result": result
            }
        
        demo_results[bond["name"]] = bond_results
    
    return jsonify({
        "demo_results": demo_results,
        "performance_summary": {
            "calculator_ready": True,
            "caching_enabled": calculator.enable_caching,
            "contexts_available": list(calculator.context_configs.keys()),
            "performance_targets": {
                context: config["target_ms"] 
                for context, config in calculator.context_configs.items()
            }
        },
        "demo_metadata": {
            "bonds_tested": len(demo_bonds),
            "contexts_tested": 3,
            "total_calculations": len(demo_bonds) * 3,
            "timestamp": datetime.now().isoformat()
        }
    })

if __name__ == '__main__':
    print("🚀 XTrillion API - Tuesday Demo Ready")
    print("=" * 45)
    print(f"📅 Settlement Date: {calculator.settlement_date}")
    print(f"🔄 Caching: {'✅ Enabled' if calculator.enable_caching else '❌ Disabled'}")
    print(f"🎯 Performance Targets:")
    
    for context, config in calculator.context_configs.items():
        target = config.get("target_ms", "N/A")
        print(f"   {context:12}: {target}ms")
    
    print(f"\n📊 Available Endpoints:")
    print(f"   POST /v1/bond/calculate   - Individual bond calculations")
    print(f"   POST /v1/bond/portfolio   - Portfolio-level calculations")
    print(f"   GET  /v1/bond/performance - Performance monitoring")
    print(f"   GET  /v1/bond/demo        - Demo examples")
    print(f"   GET  /v1/health           - Health check")
    
    print(f"\n🚀 Starting server...")
    app.run(host='0.0.0.0', port=8080, debug=False)
