#!/usr/bin/env python3
"""
Enhanced XTrillion API Cash Flow Extension - Google Analysis 10
==============================================================

ENHANCED with advanced filtering capabilities:
- Next cash flow filter (?filter=next)
- Period-based filtering (?filter=period&days=90)
- New convenience endpoints
- Enhanced response metadata
"""

from flask import Flask, request, jsonify
import logging
from datetime import datetime

from xtrillion_cash_flow_calculator import calculate_bond_cash_flows

logger = logging.getLogger(__name__)

def add_cash_flow_endpoints(app: Flask):
    """Add ENHANCED cash flow endpoints with filtering to existing Flask app"""
    
    @app.route('/api/v1/bond/cashflow', methods=['POST'])
    def calculate_cash_flows():
        """Calculate bond cash flows with ADVANCED filtering capabilities"""
        try:
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json", "status": "error"}), 400
            
            data = request.get_json()
            
            if 'bonds' not in data:
                return jsonify({"error": "Missing required field: bonds", "status": "error"}), 400
            
            bonds = data['bonds']
            if not bonds or not isinstance(bonds, list):
                return jsonify({"error": "bonds must be a non-empty list", "status": "error"}), 400
            
            # Validate each bond
            for i, bond in enumerate(bonds):
                if not isinstance(bond, dict):
                    return jsonify({"error": f"Bond {i+1} must be an object", "status": "error"}), 400
                
                required_fields = ['description', 'nominal']
                for field in required_fields:
                    if field not in bond:
                        return jsonify({"error": f"Bond {i+1} missing required field: {field}", "status": "error"}), 400
                
                try:
                    bond['nominal'] = float(bond['nominal'])
                except (ValueError, TypeError):
                    return jsonify({"error": f"Bond {i+1} nominal must be a number", "status": "error"}), 400
            
            # Get parameters
            context = data.get('context', request.args.get('context', 'portfolio'))
            settlement_date = data.get('settlement_date', request.args.get('settlement_date'))
            filter_type = data.get('filter', request.args.get('filter', 'all'))
            filter_days = data.get('days', request.args.get('days'))
            
            # Validate parameters
            valid_contexts = ['portfolio', 'individual', 'combined']
            if context not in valid_contexts:
                return jsonify({"error": f"context must be one of: {', '.join(valid_contexts)}", "status": "error"}), 400
            
            valid_filters = ['all', 'next', 'period']
            if filter_type not in valid_filters:
                return jsonify({"error": f"filter must be one of: {', '.join(valid_filters)}", "status": "error"}), 400
            
            if filter_type == 'period':
                if not filter_days:
                    return jsonify({"error": "days parameter required when filter=period", "status": "error"}), 400
                try:
                    filter_days = int(filter_days)
                    if filter_days <= 0:
                        return jsonify({"error": "days must be a positive integer", "status": "error"}), 400
                except (ValueError, TypeError):
                    return jsonify({"error": "days must be a valid integer", "status": "error"}), 400
            else:
                filter_days = None
            
            if settlement_date:
                try:
                    datetime.strptime(settlement_date, "%Y-%m-%d")
                except ValueError:
                    return jsonify({"error": "settlement_date must be in YYYY-MM-DD format", "status": "error"}), 400
            
            # Calculate with ENHANCED filtering
            logger.info(f"GA10 Enhanced: Calculating for {len(bonds)} bonds, filter: {filter_type}, days: {filter_days}")
            
            result = calculate_bond_cash_flows(
                bonds_data=bonds,
                context=context,
                settlement_date=settlement_date,
                filter_type=filter_type,
                filter_days=filter_days
            )
            
            if 'error' in result:
                logger.error(f"Calculation error: {result['error']}")
                return jsonify({"error": f"Calculation failed: {result['error']}", "status": "error"}), 500
            
            result['status'] = 'success'
            result['calculation_method'] = 'quantlib_professional_ga10_enhanced'
            result['api_version'] = 'v1'
            
            logger.info(f"Enhanced calculation successful with filter: {filter_type}")
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return jsonify({"error": "Internal server error", "status": "error", "timestamp": datetime.now().isoformat()}), 500
    
    @app.route('/api/v1/bond/cashflow/next', methods=['POST'])
    def calculate_next_cash_flow():
        """Convenience endpoint for NEXT cash flow only"""
        try:
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json", "status": "error"}), 400
            
            data = request.get_json()
            
            if 'bonds' not in data:
                return jsonify({"error": "Missing required field: bonds", "status": "error"}), 400
            
            bonds = data['bonds']
            context = data.get('context', 'portfolio')
            settlement_date = data.get('settlement_date')
            
            result = calculate_bond_cash_flows(
                bonds_data=bonds,
                context=context,
                settlement_date=settlement_date,
                filter_type='next',
                filter_days=None
            )
            
            if 'error' in result:
                return jsonify({"error": f"Calculation failed: {result['error']}", "status": "error"}), 500
            
            result['status'] = 'success'
            result['endpoint'] = 'next_cash_flow_convenience'
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error in next cash flow endpoint: {e}")
            return jsonify({"error": "Internal server error", "status": "error"}), 500
    
    @app.route('/api/v1/bond/cashflow/period/<int:days>', methods=['POST'])
    def calculate_period_cash_flow(days):
        """Convenience endpoint for PERIOD filtering"""
        try:
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json", "status": "error"}), 400
            
            data = request.get_json()
            
            if 'bonds' not in data:
                return jsonify({"error": "Missing required field: bonds", "status": "error"}), 400
            
            if days <= 0:
                return jsonify({"error": "days must be a positive integer", "status": "error"}), 400
            
            bonds = data['bonds']
            context = data.get('context', 'portfolio')
            settlement_date = data.get('settlement_date')
            
            result = calculate_bond_cash_flows(
                bonds_data=bonds,
                context=context,
                settlement_date=settlement_date,
                filter_type='period',
                filter_days=days
            )
            
            if 'error' in result:
                return jsonify({"error": f"Calculation failed: {result['error']}", "status": "error"}), 500
            
            result['status'] = 'success'
            result['endpoint'] = f'period_cash_flow_convenience_{days}_days'
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error in period cash flow endpoint: {e}")
            return jsonify({"error": "Internal server error", "status": "error"}), 500

    logger.info("✅ GA10 Enhanced cash flow endpoints with filtering added successfully")
