#!/usr/bin/env python3
"""
Google Analysis 10 - DEV API with Batch Processing
================================================

Development version of the XTrillion Core API with new batch processing capabilities.

NEW IN DEV:
✅ BATCH PROCESSING: New /api/v1/bonds/batch endpoint for parallel bond processing
✅ PARALLEL EXECUTION: Multi-threaded bond calculations for improved performance
✅ ARRAY VALIDATION: Comprehensive validation for batch bond arrays
✅ PERFORMANCE TRACKING: Detailed timing and performance metrics
✅ ENHANCED ERROR HANDLING: Robust error handling for batch operations

BACKWARDS COMPATIBLE:
✅ All existing endpoints maintained for compatibility
✅ Individual bond analysis unchanged
✅ Portfolio analysis enhanced with batch capabilities
"""

from flask import Flask, request, jsonify
import sys
import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import traceback
from functools import wraps

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.append('.')

# Import existing production modules
try:
    from bond_master_hierarchy_enhanced import calculate_bond_master
    from google_analysis10 import process_bond_portfolio
    from gcs_database_manager import ensure_databases_available
    PRODUCTION_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Production modules not available: {e}")
    PRODUCTION_MODULES_AVAILABLE = False

app = Flask(__name__)

# Add environment identification endpoints
try:
    from environment_info import add_environment_endpoints
    add_environment_endpoints(app)
    logger.info("🏷️ Environment identification endpoints added")
except ImportError:
    logger.warning("⚠️ Environment info endpoints not available")

# API Key configuration
VALID_API_KEYS = {
    "gax10_demo_3j5h8m9k2p6r4t7w1q": "demo",
    "gax10_dev_4n8s6k2x7p9v5m8p1z": "development", 
    "gax10_test_9r4t7w2k5m8p1z6x3v": "testing"
}

def require_api_key(f):
    """API key authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key not in VALID_API_KEYS:
            return jsonify({
                "status": "error",
                "code": 401,
                "message": "Valid API key required in X-API-Key header"
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def mock_bond_calculation(description, price, settlement_date=None):
    """
    Mock bond calculation for DEV environment
    Returns realistic bond analytics for testing batch processing logic
    """
    import random
    import hashlib
    
    # Create deterministic results based on bond description for consistent testing
    seed_string = f"{description}_{price}"
    seed = int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    # Simulate processing time
    time.sleep(random.uniform(0.1, 0.3))
    
    # Generate realistic mock data
    base_yield = random.uniform(2.0, 8.0)
    duration = random.uniform(5.0, 25.0)
    
    return {
        "status": "success",
        "bond": {
            "description": description,
            "isin": None,
            "conventions": {
                "fixed_frequency": "Semiannual",
                "day_count": "ActualActual_Bond",
                "business_day_convention": "Following"
            },
            "route_used": "mock_calculation"
        },
        "analytics": {
            "ytm": round(base_yield, 6),
            "duration": round(duration, 6),
            "accrued_interest": round(random.uniform(0.5, 3.0), 6),
            "clean_price": price,
            "dirty_price": round(price + random.uniform(0.5, 2.0), 6),
            "macaulay_duration": round(duration + random.uniform(0.2, 1.0), 6),
            "annual_duration": round(duration * 0.97, 6),
            "ytm_annual": round(base_yield * 1.02, 6),
            "convexity": round(random.uniform(100, 500), 6),
            "pvbp": round(duration / 10000, 6),
            "settlement_date": settlement_date or "2025-08-02",
            "spread": random.randint(0, 500) if "treasury" not in description.lower() else 0,
            "z_spread": None
        },
        "calculations": {
            "basis": "Semi-annual compounding",
            "day_count": "ActualActual_Bond",
            "business_day_convention": "Following"
        },
        "metadata": {
            "api_version": "v1.2_dev",
            "calculation_engine": "mock_dev_engine",
            "enhanced_metrics_count": 13
        }
    }

def calculate_single_bond(bond_data):
    """
    Calculate analytics for a single bond with error handling
    
    Args:
        bond_data: List/Tuple in format [description, price, settlement_date]
    
    Returns:
        Dict with calculation results and metadata
    """
    start_time = time.time()
    
    try:
        # Validate bond data format
        if not isinstance(bond_data, (list, tuple)) or len(bond_data) < 2:
            return {
                "status": "error",
                "error": "Bond data must be array with [description, price] or [description, price, settlement_date]",
                "calculation_time": 0
            }
        
        description = bond_data[0]
        price = float(bond_data[1])
        settlement_date = bond_data[2] if len(bond_data) > 2 else None
        
        # Use production calculation if available, otherwise use mock
        if PRODUCTION_MODULES_AVAILABLE:
            result = calculate_bond_master(description, price, settlement_date)
        else:
            result = mock_bond_calculation(description, price, settlement_date)
        
        # Add timing information
        calculation_time = round((time.time() - start_time) * 1000, 2)  # milliseconds
        result["calculation_time_ms"] = calculation_time
        
        return result
        
    except Exception as e:
        calculation_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Bond calculation error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "calculation_time_ms": calculation_time,
            "bond_input": bond_data[:2] if len(bond_data) >= 2 else bond_data
        }

def validate_batch_request(data):
    """
    Validate batch processing request format
    
    Args:
        data: Request JSON data
    
    Returns:
        Tuple (is_valid, error_message, validated_bonds)
    """
    if not isinstance(data, dict):
        return False, "Request must be JSON object", None
    
    if "bonds" not in data:
        return False, "Missing 'bonds' field in request", None
    
    bonds = data["bonds"]
    if not isinstance(bonds, list):
        return False, "'bonds' must be an array", None
    
    if len(bonds) == 0:
        return False, "Bonds array cannot be empty", None
    
    if len(bonds) > 100:  # Reasonable limit for DEV
        return False, "Maximum 100 bonds per batch request", None
    
    # Validate each bond entry
    validated_bonds = []
    for i, bond in enumerate(bonds):
        if not isinstance(bond, (list, tuple)):
            return False, f"Bond {i}: Must be array format [description, price] or [description, price, settlement_date]", None
        
        if len(bond) < 2:
            return False, f"Bond {i}: Must have at least [description, price]", None
        
        if len(bond) > 3:
            return False, f"Bond {i}: Maximum 3 elements [description, price, settlement_date]", None
        
        # Validate description
        if not isinstance(bond[0], str) or not bond[0].strip():
            return False, f"Bond {i}: Description must be non-empty string", None
        
        # Validate price
        try:
            price = float(bond[1])
            if price <= 0:
                return False, f"Bond {i}: Price must be positive number", None
        except (ValueError, TypeError):
            return False, f"Bond {i}: Price must be valid number", None
        
        # Validate settlement_date if provided
        if len(bond) > 2 and bond[2] is not None:
            if not isinstance(bond[2], str):
                return False, f"Bond {i}: Settlement date must be string in YYYY-MM-DD format", None
        
        validated_bonds.append(bond)
    
    return True, None, validated_bonds

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check with batch processing capabilities"""
    try:
        ensure_databases_available() if PRODUCTION_MODULES_AVAILABLE else None
        
        return jsonify({
            "status": "healthy",
            "version": "10.0.0-dev",
            "service": "XTrillion Core Bond Analytics API - DEV with Batch Processing",
            "timestamp": datetime.now().isoformat(),
            "environment": "development",
            "api_status": "operational",
            "batch_processing": {
                "available": True,
                "max_bonds_per_request": 100,
                "parallel_execution": True
            },
            "capabilities": [
                "Professional bond calculation engine powered by QuantLib",
                "🆕 NEW: Batch processing endpoint (/api/v1/bonds/batch)",
                "🆕 NEW: Parallel bond calculations for improved performance", 
                "🆕 NEW: Array validation and comprehensive error handling",
                "🆕 NEW: Performance tracking and timing metrics",
                "Universal bond parser supporting ISIN and text descriptions",
                "Real-time yield, duration, and accrued interest calculations",
                "Individual bond analytics with institutional-grade precision",
                "Portfolio analysis with weighted-average risk metrics",
                "Bloomberg-compatible calculation accuracy",
                "Backwards compatible with all existing endpoints"
            ],
            "production_modules": PRODUCTION_MODULES_AVAILABLE
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/bonds/batch', methods=['POST'])
@require_api_key
def batch_bond_analysis():
    """
    🆕 NEW: Batch bond analysis endpoint with parallel processing
    
    Processes multiple bonds in parallel for improved performance.
    
    Request format:
    {
        "bonds": [
            ["T 3 15/08/52", 71.66, "2025-08-01"],
            ["PANAMA, 3.87%, 23-Jul-2060", 56.60, "2025-08-01"]
        ],
        "parallel": true,  // optional, default true
        "max_workers": 4   // optional, default 4
    }
    
    Response includes individual results plus batch performance metrics.
    """
    batch_start_time = time.time()
    
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "status": "error",
                "code": 400,
                "message": "Request must be JSON"
            }), 400
        
        data = request.get_json()
        
        # Validate batch request format
        is_valid, error_msg, validated_bonds = validate_batch_request(data)
        if not is_valid:
            return jsonify({
                "status": "error",
                "code": 400,
                "message": error_msg
            }), 400
        
        # Extract processing options
        use_parallel = data.get("parallel", True)
        max_workers = min(data.get("max_workers", 4), 8)  # Cap at 8 workers
        
        logger.info(f"Processing batch of {len(validated_bonds)} bonds (parallel={use_parallel}, workers={max_workers})")
        
        results = []
        
        if use_parallel and len(validated_bonds) > 1:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all bond calculations
                future_to_index = {
                    executor.submit(calculate_single_bond, bond): i 
                    for i, bond in enumerate(validated_bonds)
                }
                
                # Collect results as they complete
                temp_results = [None] * len(validated_bonds)
                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        result = future.result()
                        temp_results[index] = result
                    except Exception as e:
                        logger.error(f"Parallel calculation error for bond {index}: {e}")
                        temp_results[index] = {
                            "status": "error",
                            "error": f"Parallel processing error: {str(e)}",
                            "calculation_time_ms": 0
                        }
                
                results = temp_results
        else:
            # Sequential processing
            for bond in validated_bonds:
                result = calculate_single_bond(bond)
                results.append(result)
        
        # Calculate batch performance metrics
        batch_time = round((time.time() - batch_start_time) * 1000, 2)
        successful_calculations = sum(1 for r in results if r.get("status") == "success")
        failed_calculations = len(results) - successful_calculations
        
        avg_calc_time = 0
        if successful_calculations > 0:
            total_calc_time = sum(r.get("calculation_time_ms", 0) for r in results if r.get("status") == "success")
            avg_calc_time = round(total_calc_time / successful_calculations, 2)
        
        # Prepare response
        response = {
            "status": "success",
            "batch_results": results,
            "batch_performance": {
                "total_bonds": len(validated_bonds),
                "successful_calculations": successful_calculations,
                "failed_calculations": failed_calculations,
                "success_rate": round((successful_calculations / len(validated_bonds)) * 100, 1),
                "batch_processing_time_ms": batch_time,
                "average_calculation_time_ms": avg_calc_time,
                "parallel_processing": use_parallel,
                "max_workers_used": max_workers if use_parallel else 1
            },
            "metadata": {
                "api_version": "v1.2_dev",
                "endpoint": "/api/v1/bonds/batch",
                "timestamp": datetime.now().isoformat(),
                "calculation_engine": "xtrillion_core_quantlib_engine" if PRODUCTION_MODULES_AVAILABLE else "mock_dev_engine"
            }
        }
        
        logger.info(f"Batch processing complete: {successful_calculations}/{len(validated_bonds)} successful in {batch_time}ms")
        
        return jsonify(response)
        
    except Exception as e:
        batch_time = round((time.time() - batch_start_time) * 1000, 2)
        logger.error(f"Batch processing error: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "status": "error",
            "code": 500,
            "message": f"Batch processing failed: {str(e)}",
            "batch_processing_time_ms": batch_time,
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/batch/status', methods=['GET'])
def batch_status():
    """Get batch processing capabilities and status"""
    return jsonify({
        "status": "operational",
        "batch_processing": {
            "available": True,
            "max_bonds_per_request": 100,
            "max_workers": 8,
            "parallel_execution": True,
            "supported_formats": [
                "[[description, price]]",
                "[[description, price, settlement_date]]"
            ]
        },
        "endpoints": {
            "batch_analysis": "/api/v1/bonds/batch",
            "batch_status": "/api/v1/batch/status"
        },
        "performance": {
            "average_calculation_time_ms": "100-300ms per bond",
            "batch_overhead_ms": "10-50ms",
            "parallel_speedup": "2-4x for batches > 4 bonds"
        },
        "timestamp": datetime.now().isoformat()
    })

# Include existing individual bond endpoint for backwards compatibility
@app.route('/api/v1/bond/analysis', methods=['POST'])
@require_api_key
def individual_bond_analysis():
    """
    ✅ EXISTING: Individual bond analysis endpoint (backwards compatible)
    """
    try:
        if not request.is_json:
            return jsonify({
                "status": "error",
                "code": 400,
                "message": "Request must be JSON"
            }), 400
        
        data = request.get_json()
        
        # Extract parameters
        description = data.get('description')
        isin = data.get('isin') 
        price = data.get('price', 100.0)
        settlement_date = data.get('settlement_date')
        
        # Use description or ISIN
        bond_identifier = description or isin
        if not bond_identifier:
            return jsonify({
                "status": "error",
                "code": 400,
                "message": "Either 'description' or 'isin' must be provided"
            }), 400
        
        # Calculate bond analytics
        if PRODUCTION_MODULES_AVAILABLE:
            # Use named parameters to match production API
            result = calculate_bond_master(
                isin=isin,
                description=description,
                price=float(price),
                settlement_date=settlement_date
            )
        else:
            result = mock_bond_calculation(bond_identifier, float(price), settlement_date)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Individual bond analysis error: {e}")
        return jsonify({
            "status": "error",
            "code": 500,
            "message": f"Calculation failed: {str(e)}"
        }), 500

# Include existing portfolio endpoint for backwards compatibility
@app.route('/api/v1/treasury/status', methods=['GET'])
@require_api_key
def treasury_status():
    """Check treasury data status - DEV version"""
    return jsonify({
        'status': 'success',
        'message': 'Treasury status endpoint not yet implemented in DEV',
        'info': 'Use production endpoint for treasury data status'
    })

@app.route('/test/status', methods=['GET'])
@require_api_key
def get_test_status():
    """Get latest test results"""
    try:
        from pathlib import Path
        import json
        
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
        logger.error(f"Test status error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/test/run', methods=['POST'])
@require_api_key
def run_tests():
    """Run test suite and return results"""
    try:
        import subprocess
        from pathlib import Path
        import json
        
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
        logger.error(f"Test run error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/test/treasury', methods=['GET'])
@require_api_key
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
        logger.error(f"Treasury test error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/test/baseline', methods=['GET'])
@require_api_key
def get_baseline():
    """Get current baseline values"""
    try:
        from pathlib import Path
        import json
        from datetime import datetime
        
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
        logger.error(f"Baseline error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/v1/portfolio/analysis', methods=['POST'])
@require_api_key
def portfolio_analysis():
    """
    ✅ EXISTING: Portfolio analysis endpoint (backwards compatible)
    """
    try:
        if not request.is_json:
            return jsonify({
                "status": "error",
                "code": 400,
                "message": "Request must be JSON"
            }), 400
        
        data = request.get_json()
        
        if PRODUCTION_MODULES_AVAILABLE:
            result = process_bond_portfolio(data)
        else:
            # Mock portfolio response for DEV
            portfolio_data = data.get('data', [])
            mock_results = []
            
            for bond in portfolio_data:
                bond_cd = bond.get('BOND_CD', 'Unknown')
                price = bond.get('CLOSING PRICE', 100.0)
                weight = bond.get('WEIGHTING', 0.0)
                
                mock_calc = mock_bond_calculation(bond_cd, price)
                mock_results.append({
                    "status": "success",
                    "name": bond_cd,
                    "yield": f"{mock_calc['analytics']['ytm']:.2f}%",
                    "duration": f"{mock_calc['analytics']['duration']:.1f} years",
                    "price": price,
                    "weight": weight
                })
            
            # Calculate portfolio metrics
            avg_yield = sum(float(r['yield'].replace('%', '')) for r in mock_results) / len(mock_results)
            avg_duration = sum(float(r['duration'].replace(' years', '')) for r in mock_results) / len(mock_results)
            
            result = {
                "status": "success",
                "format": "YAS",
                "bond_data": mock_results,
                "portfolio_metrics": {
                    "portfolio_yield": f"{avg_yield:.2f}%",
                    "portfolio_duration": f"{avg_duration:.1f} years",
                    "portfolio_spread": "150 bps",
                    "total_bonds": len(mock_results),
                    "success_rate": "100.0%"
                },
                "metadata": {
                    "api_version": "v1.2_dev",
                    "processing_type": "portfolio_optimized_dev"
                }
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Portfolio analysis error: {e}")
        return jsonify({
            "status": "error",
            "code": 500,
            "message": f"Portfolio analysis failed: {str(e)}"
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Starting XTrillion Core API - DEV with Batch Processing")
    logger.info("🆕 NEW: Batch processing endpoint available at /api/v1/bonds/batch")
    logger.info("✅ Backwards compatible with all existing endpoints")
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
