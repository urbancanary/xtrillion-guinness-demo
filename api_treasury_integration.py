"""
API Integration for Treasury Yield Updates
==========================================

Add this code to google_analysis10_api.py to enable intelligent yield updates.
"""

import threading
from flask import request, jsonify
from datetime import datetime
import logging

from treasury_yield_update_strategy import TreasuryYieldUpdater
from update_treasury_yields import update_treasury_yields, get_current_yields

logger = logging.getLogger(__name__)


def add_treasury_yield_endpoints(app):
    """
    Add treasury yield endpoints to Flask app.
    
    Usage:
        # In google_analysis10_api.py after app creation:
        from api_treasury_integration import add_treasury_yield_endpoints
        add_treasury_yield_endpoints(app)
    """
    
    @app.route('/api/v1/treasury/yields', methods=['GET'])
    def get_treasury_yields():
        """
        Get current treasury yields with intelligent caching.
        
        Query Parameters:
            - date: Specific date (YYYY-MM-DD) to fetch
            - force_update: Force refresh of yield data
            - check_freshness: Return data freshness info
        """
        try:
            # Check if forced update requested
            force_update = request.args.get('force_update', '').lower() == 'true'
            check_freshness = request.args.get('check_freshness', '').lower() == 'true'
            specific_date = request.args.get('date')
            
            # Check data freshness
            updater = TreasuryYieldUpdater()
            recommendation = updater.get_update_recommendation()
            
            # Perform update if needed (in background to avoid blocking)
            if force_update or recommendation['needs_update']:
                if force_update:
                    logger.info("Forced treasury yield update requested")
                else:
                    logger.info(f"Auto-updating stale yields: {recommendation['reason']}")
                
                # Update in background thread
                update_thread = threading.Thread(
                    target=update_treasury_yields,
                    args=(force_update,)
                )
                update_thread.daemon = True
                update_thread.start()
                
                # For forced updates, wait briefly for completion
                if force_update:
                    update_thread.join(timeout=5.0)
            
            # Get current yields
            yields = get_current_yields(specific_date)
            
            response = {
                'status': 'success',
                'data': yields,
                'data_date': specific_date or recommendation.get('latest_data_date', '').strftime('%Y-%m-%d') if recommendation.get('latest_data_date') else None,
                'last_update': recommendation.get('last_update_time', '').isoformat() if recommendation.get('last_update_time') else None
            }
            
            if check_freshness:
                response['freshness'] = {
                    'is_fresh': not recommendation['needs_update'],
                    'reason': recommendation['reason'],
                    'cache_age_hours': (
                        (datetime.now() - recommendation['last_update_time']).total_seconds() / 3600
                        if recommendation.get('last_update_time') else None
                    )
                }
            
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error in treasury yields endpoint: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    @app.route('/api/v1/treasury/update', methods=['POST'])
    def update_treasury_yields_endpoint():
        """
        Manually trigger treasury yield update.
        
        Requires API key for security.
        """
        try:
            # Check API key
            api_key = request.headers.get('X-API-Key')
            if not api_key or api_key not in app.config.get('VALID_API_KEYS', []):
                return jsonify({'error': 'Unauthorized'}), 401
            
            # Perform update
            result = update_treasury_yields(force=True)
            
            return jsonify(result), 200 if result['status'] == 'success' else 500
            
        except Exception as e:
            logger.error(f"Error updating treasury yields: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500


# Example integration into existing bond calculation
def enhance_bond_calculation_with_fresh_yields(calculate_function):
    """
    Decorator to ensure fresh yield data for bond calculations.
    
    Usage:
        @enhance_bond_calculation_with_fresh_yields
        def calculate_bond_analytics(bond_data):
            # existing calculation logic
    """
    def wrapper(*args, **kwargs):
        # Check yield freshness before calculation
        updater = TreasuryYieldUpdater()
        recommendation = updater.get_update_recommendation()
        
        if recommendation['needs_update']:
            logger.info(f"Updating stale yields before calculation: {recommendation['reason']}")
            # Update synchronously for calculations
            update_treasury_yields(force=False)
        
        # Proceed with calculation
        return calculate_function(*args, **kwargs)
    
    return wrapper


# Configuration for scheduled updates
TREASURY_UPDATE_CONFIG = {
    'cache_duration_hours': 4,          # Normal market hours
    'weekend_cache_hours': 72,          # Weekends
    'auto_update_enabled': True,        # Enable automatic updates
    'update_times': ['06:00', '12:00', '16:00', '20:00'],  # Daily update times
    'max_concurrent_updates': 1,        # Prevent multiple simultaneous updates
}