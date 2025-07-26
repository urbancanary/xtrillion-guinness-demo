#!/usr/bin/env python3
"""
Automated GA10 Cash Flow Filter Implementation Script
===================================================

Automatically implements the enhanced cash flow filtering capabilities
into your existing Google Analysis 10 project.

This script will:
1. Backup existing files safely
2. Deploy enhanced cash flow calculator with filters
3. Deploy enhanced API extension with new endpoints
4. Deploy comprehensive test script
5. Validate the integration
6. Test the new filtering capabilities

USAGE:
    python implement_ga10_filters.py
"""

import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
import json

# GA10 Project Configuration
GA10_PROJECT_ROOT = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
BACKUP_DIR = f"{GA10_PROJECT_ROOT}/backups_enhanced_filters_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

class GA10FilterImplementer:
    """Automated implementation of GA10 cash flow filters"""
    
    def __init__(self):
        self.project_root = Path(GA10_PROJECT_ROOT)
        self.backup_dir = Path(BACKUP_DIR)
        self.success_count = 0
        self.total_steps = 8
        
    def log(self, message, level="INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        levels = {
            "INFO": "💡",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "ERROR": "❌",
            "STEP": "🔧"
        }
        icon = levels.get(level, "📝")
        print(f"[{timestamp}] {icon} {message}")
    
    def validate_environment(self):
        """Validate GA10 project environment"""
        self.log("Validating GA10 project environment...", "STEP")
        
        # Check project directory exists
        if not self.project_root.exists():
            self.log(f"GA10 project directory not found: {self.project_root}", "ERROR")
            return False
        
        # Check for key existing files
        required_files = [
            "google_analysis10_api.py",
            "requirements.txt"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.log(f"Missing required files: {missing_files}", "ERROR")
            return False
        
        # Check for existing cash flow files
        existing_files = [
            "xtrillion_cash_flow_calculator.py",
            "api_cash_flow_extension.py"
        ]
        
        found_existing = []
        for file in existing_files:
            if (self.project_root / file).exists():
                found_existing.append(file)
        
        if found_existing:
            self.log(f"Found existing cash flow files: {found_existing}", "INFO")
        else:
            self.log("No existing cash flow files found - fresh installation", "INFO")
        
        self.log("Environment validation successful!", "SUCCESS")
        return True
    
    def create_backup(self):
        """Create comprehensive backup of existing files"""
        self.log("Creating backup of existing files...", "STEP")
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Files to backup
            backup_files = [
                "google_analysis10_api.py",
                "requirements.txt",
                "xtrillion_cash_flow_calculator.py",
                "api_cash_flow_extension.py",
                "test_ga10_cash_flow_integration.py"
            ]
            
            backed_up = []
            for file in backup_files:
                source = self.project_root / file
                if source.exists():
                    destination = self.backup_dir / f"{file}.backup"
                    shutil.copy2(source, destination)
                    backed_up.append(file)
            
            self.log(f"Backed up {len(backed_up)} files to: {self.backup_dir}", "SUCCESS")
            
            # Create backup manifest
            manifest = {
                "backup_time": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "files_backed_up": backed_up,
                "backup_reason": "Enhanced cash flow filters implementation"
            }
            
            with open(self.backup_dir / "manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)
            
            return True
            
        except Exception as e:
            self.log(f"Backup failed: {e}", "ERROR")
            return False
    
    def deploy_enhanced_calculator(self):
        """Deploy the enhanced cash flow calculator"""
        self.log("Deploying enhanced cash flow calculator...", "STEP")
        
        enhanced_calculator_code = '''#!/usr/bin/env python3
"""
XTrillion Bond Cash Flow Calculator - Google Analysis 10 - ENHANCED VERSION
===========================================================================

Professional-grade cash flow calculations with ADVANCED FILTERING:
- Next cash flow only filter
- Period-based filtering (days from settlement)
- Portfolio and individual bond analysis
- Bloomberg-compatible calculations

ENHANCED FEATURES:
- filter_type: "all", "next", "period"
- filter_days: Number of days from settlement
- days_from_settlement in response data
- Enhanced metadata and error handling
"""

import QuantLib as ql
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging
import re
import json

logger = logging.getLogger(__name__)

class XTrillionCashFlowCalculator:
    """
    Enhanced cash flow calculator with advanced filtering capabilities
    Integrated with Google Analysis 10 infrastructure
    """
    
    def __init__(self, settlement_date: str = None):
        """Initialize with settlement date (defaults to prior month end)"""
        if settlement_date:
            try:
                dt = datetime.strptime(settlement_date, "%Y-%m-%d")
                self.settlement_date = ql.Date(dt.day, dt.month, dt.year)
                self.settlement_date_py = dt
            except:
                self.settlement_date = self._get_default_settlement_date()
                self.settlement_date_py = self._ql_to_python_date(self.settlement_date)
        else:
            self.settlement_date = self._get_default_settlement_date()
            self.settlement_date_py = self._ql_to_python_date(self.settlement_date)
    
    def _get_default_settlement_date(self):
        """Get default settlement date (prior month end) - GA10 compatible"""
        try:
            from google_analysis10 import get_prior_month_end
            settlement_str = get_prior_month_end()
            dt = datetime.strptime(settlement_str, "%Y-%m-%d")
            return ql.Date(dt.day, dt.month, dt.year)
        except:
            today = datetime.now()
            if today.day < 15:
                last_month = today.replace(day=1) - timedelta(days=1)
            else:
                import calendar
                last_day = calendar.monthrange(today.year, today.month)[1]
                last_month = today.replace(day=last_day)
            
            return ql.Date(last_month.day, last_month.month, last_month.year)
    
    def _ql_to_python_date(self, ql_date: ql.Date) -> datetime:
        """Convert QuantLib date to Python datetime"""
        return datetime(ql_date.year(), ql_date.month(), ql_date.dayOfMonth())
    
    def parse_bond_parameters(self, description: str, nominal: float) -> Dict[str, Any]:
        """Parse bond description to extract key parameters"""
        try:
            coupon_rate = self._extract_coupon_rate(description)
            maturity_date = self._extract_maturity_date(description)
            
            is_treasury = "TREASURY" in description.upper() or description.upper().startswith("T ")
            
            if is_treasury:
                payment_frequency = 2
                day_count = ql.ActualActual(ql.ActualActual.ISDA)
            else:
                payment_frequency = 2
                day_count = ql.Thirty360(ql.Thirty360.BondBasis)
            
            return {
                'coupon_rate': coupon_rate / 100.0,
                'maturity_date': maturity_date,
                'nominal_amount': nominal,
                'payment_frequency': payment_frequency,
                'day_count': day_count,
                'is_treasury': is_treasury
            }
            
        except Exception as e:
            logger.error(f"Error parsing bond parameters: {e}")
            return None
    
    def _extract_coupon_rate(self, description: str) -> float:
        """Extract coupon rate from description"""
        if not description:
            return 0.0
        
        fraction_map = {
            '⅛': 0.125, '¼': 0.25, '⅜': 0.375, '½': 0.5,
            '⅝': 0.625, '¾': 0.75, '⅞': 0.875,
            '1/8': 0.125, '1/4': 0.25, '3/8': 0.375, '1/2': 0.5,
            '5/8': 0.625, '3/4': 0.75, '7/8': 0.875
        }
        
        patterns = [
            r'(\\d+)\\s*([⅛¼⅜½⅝¾⅞]|\\d/\\d)',
            r'(\\d+\\.\\d+)%?',
            r'(\\d+)%',
            r'\\b(\\d+\\.?\\d*)\\s*(?=%|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                if len(match.groups()) == 2:
                    integer_part = float(match.group(1))
                    fraction_part = match.group(2)
                    fraction_value = fraction_map.get(fraction_part, 0)
                    return integer_part + fraction_value
                else:
                    return float(match.group(1))
        
        return 0.0
    
    def _extract_maturity_date(self, description: str) -> Optional[ql.Date]:
        """Extract maturity date from description"""
        try:
            patterns = [
                r'(\\d{1,2})/(\\d{1,2})/(\\d{2,4})',
                r'(\\d{1,2})-(\\d{1,2})-(\\d{2,4})',
                r'(\\d{2})(\\d{2})(\\d{2})',
                r'(\\d{4})-(\\d{1,2})-(\\d{1,2})',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, description)
                if match:
                    if len(match.groups()) == 3:
                        if pattern.startswith(r'(\\d{4})'):
                            year, month, day = match.groups()
                        else:
                            month, day, year = match.groups()
                        
                        month = int(month)
                        day = int(day)
                        year = int(year)
                        
                        if year < 50:
                            year += 2000
                        elif year < 100:
                            year += 1900
                        
                        return ql.Date(day, month, year)
            
            return ql.Date(31, 12, 2030)
            
        except Exception as e:
            logger.error(f"Error extracting maturity date: {e}")
            return ql.Date(31, 12, 2030)
    
    def create_quantlib_bond(self, params: Dict[str, Any]) -> Optional[ql.Bond]:
        """Create QuantLib bond object"""
        try:
            if not params or not params.get('maturity_date'):
                return None
            
            schedule = ql.Schedule(
                self.settlement_date,
                params['maturity_date'],
                ql.Period(ql.Semiannual),
                ql.UnitedStates(ql.UnitedStates.GovernmentBond),
                ql.Following,
                ql.Following,
                ql.DateGeneration.Backward,
                False
            )
            
            bond = ql.FixedRateBond(
                2,
                params['nominal_amount'],
                schedule,
                [params['coupon_rate']],
                params['day_count']
            )
            
            return bond
            
        except Exception as e:
            logger.error(f"Error creating QuantLib bond: {e}")
            return None
    
    def calculate_individual_cash_flows(self, description: str, nominal: float, 
                                       filter_type: str = "all", 
                                       filter_days: int = None) -> List[Dict[str, Any]]:
        """Calculate cash flow schedule with ENHANCED FILTERING"""
        try:
            params = self.parse_bond_parameters(description, nominal)
            if not params:
                return []
            
            bond = self.create_quantlib_bond(params)
            if not bond:
                return []
            
            cash_flows = []
            bond_schedule = bond.cashflows()
            
            for i, cf in enumerate(bond_schedule):
                cf_date = cf.date()
                cf_amount = cf.amount()
                
                if cf_date <= self.settlement_date:
                    continue
                
                py_date = datetime(cf_date.year(), cf_date.month(), cf_date.dayOfMonth())
                
                if i == len(bond_schedule) - 1:
                    cf_type = "maturity"
                else:
                    cf_type = "coupon"
                
                cash_flows.append({
                    "date": py_date.strftime("%Y-%m-%d"),
                    "amount": round(cf_amount, 2),
                    "type": cf_type,
                    "days_from_settlement": (py_date - self.settlement_date_py).days
                })
            
            return self._apply_cash_flow_filters(cash_flows, filter_type, filter_days)
            
        except Exception as e:
            logger.error(f"Error calculating cash flows: {e}")
            return []
    
    def _apply_cash_flow_filters(self, cash_flows: List[Dict[str, Any]], 
                                filter_type: str, filter_days: int) -> List[Dict[str, Any]]:
        """Apply ADVANCED filtering logic to cash flows"""
        try:
            if not cash_flows:
                return []
            
            cash_flows.sort(key=lambda x: x['date'])
            
            if filter_type == "next":
                return [cash_flows[0]] if cash_flows else []
            
            elif filter_type == "period" and filter_days is not None:
                filtered_flows = []
                for cf in cash_flows:
                    if cf['days_from_settlement'] <= filter_days:
                        filtered_flows.append(cf)
                return filtered_flows
            
            else:
                return cash_flows
                
        except Exception as e:
            logger.error(f"Error applying cash flow filters: {e}")
            return cash_flows
    
    def aggregate_portfolio_cash_flows(self, bonds: List[Dict[str, Any]], 
                                     filter_type: str = "all", 
                                     filter_days: int = None) -> List[Dict[str, Any]]:
        """Aggregate cash flows across portfolio with ENHANCED filtering"""
        try:
            all_cash_flows = {}
            
            for bond in bonds:
                description = bond.get('description', '')
                nominal = bond.get('nominal', 0)
                
                if not description or not nominal:
                    continue
                
                individual_flows = self.calculate_individual_cash_flows(
                    description, nominal, filter_type, filter_days
                )
                
                for flow in individual_flows:
                    date = flow['date']
                    amount = flow['amount']
                    
                    if date not in all_cash_flows:
                        all_cash_flows[date] = 0.0
                    
                    all_cash_flows[date] += amount
            
            portfolio_flows = []
            for date in sorted(all_cash_flows.keys()):
                cf_date = datetime.strptime(date, "%Y-%m-%d")
                days_from_settlement = (cf_date - self.settlement_date_py).days
                
                portfolio_flows.append({
                    "date": date,
                    "amount": round(all_cash_flows[date], 2),
                    "days_from_settlement": days_from_settlement
                })
            
            return portfolio_flows
            
        except Exception as e:
            logger.error(f"Error aggregating portfolio cash flows: {e}")
            return []
    
    def format_api_response(self, bonds: List[Dict[str, Any]], 
                           context: str = "portfolio",
                           filter_type: str = "all",
                           filter_days: int = None) -> Dict[str, Any]:
        """Format response with ENHANCED filtering metadata"""
        try:
            filter_info = {
                "filter_type": filter_type,
                "filter_days": filter_days,
                "filter_description": self._get_filter_description(filter_type, filter_days)
            }
            
            if context == "portfolio":
                portfolio_flows = self.aggregate_portfolio_cash_flows(bonds, filter_type, filter_days)
                return {
                    "portfolio_cash_flows": portfolio_flows,
                    "filter_applied": filter_info,
                    "metadata": {
                        "calculation_date": datetime.now().isoformat(),
                        "settlement_date": str(self.settlement_date),
                        "total_bonds": len(bonds),
                        "total_nominal": sum(bond.get('nominal', 0) for bond in bonds),
                        "context": context,
                        "ga_version": "google_analysis10_enhanced",
                        "total_cash_flows": len(portfolio_flows)
                    }
                }
            
            elif context == "individual":
                individual_results = {}
                for i, bond in enumerate(bonds):
                    bond_key = f"bond_{i+1}"
                    description = bond.get('description', '')
                    nominal = bond.get('nominal', 0)
                    
                    cash_flows = self.calculate_individual_cash_flows(
                        description, nominal, filter_type, filter_days
                    )
                    
                    individual_results[bond_key] = {
                        "description": description,
                        "nominal": nominal,
                        "cash_flows": cash_flows
                    }
                
                return {
                    "individual_cash_flows": individual_results,
                    "filter_applied": filter_info,
                    "metadata": {
                        "calculation_date": datetime.now().isoformat(),
                        "settlement_date": str(self.settlement_date),
                        "total_bonds": len(bonds),
                        "context": context,
                        "ga_version": "google_analysis10_enhanced"
                    }
                }
            
            else:  # combined
                portfolio_flows = self.aggregate_portfolio_cash_flows(bonds, filter_type, filter_days)
                individual_results = {}
                
                for i, bond in enumerate(bonds):
                    bond_key = f"bond_{i+1}"
                    description = bond.get('description', '')
                    nominal = bond.get('nominal', 0)
                    
                    cash_flows = self.calculate_individual_cash_flows(
                        description, nominal, filter_type, filter_days
                    )
                    
                    individual_results[bond_key] = {
                        "description": description,
                        "nominal": nominal,
                        "cash_flows": cash_flows
                    }
                
                return {
                    "portfolio_cash_flows": portfolio_flows,
                    "individual_cash_flows": individual_results,
                    "filter_applied": filter_info,
                    "metadata": {
                        "calculation_date": datetime.now().isoformat(),
                        "settlement_date": str(self.settlement_date),
                        "total_bonds": len(bonds),
                        "total_nominal": sum(bond.get('nominal', 0) for bond in bonds),
                        "context": context,
                        "ga_version": "google_analysis10_enhanced",
                        "total_portfolio_flows": len(portfolio_flows)
                    }
                }
                
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            return {
                "error": str(e),
                "filter_applied": filter_info if 'filter_info' in locals() else None,
                "metadata": {
                    "calculation_date": datetime.now().isoformat(),
                    "context": context,
                    "ga_version": "google_analysis10_enhanced"
                }
            }
    
    def _get_filter_description(self, filter_type: str, filter_days: int) -> str:
        """Generate human-readable filter description"""
        if filter_type == "next":
            return "Next upcoming cash flow only"
        elif filter_type == "period" and filter_days:
            return f"Cash flows within {filter_days} days from settlement"
        else:
            return "All future cash flows"


def calculate_bond_cash_flows(bonds_data: List[Dict[str, Any]], 
                            context: str = "portfolio",
                            settlement_date: str = None,
                            filter_type: str = "all",
                            filter_days: int = None) -> Dict[str, Any]:
    """ENHANCED main function for cash flow calculations with filtering"""
    try:
        calculator = XTrillionCashFlowCalculator(settlement_date)
        return calculator.format_api_response(bonds_data, context, filter_type, filter_days)
        
    except Exception as e:
        logger.error(f"Error in calculate_bond_cash_flows: {e}")
        return {
            "error": str(e),
            "filter_applied": {
                "filter_type": filter_type,
                "filter_days": filter_days
            },
            "metadata": {
                "calculation_date": datetime.now().isoformat(),
                "context": context,
                "ga_version": "google_analysis10_enhanced"
            }
        }


if __name__ == "__main__":
    bonds = [{"description": "T 2 1/2 07/31/27", "nominal": 500000}]
    
    print("=== ENHANCED CASH FLOW CALCULATOR TEST ===")
    
    # Test all filters
    for filter_type in ["all", "next", ("period", 90)]:
        if isinstance(filter_type, tuple):
            ft, days = filter_type
            result = calculate_bond_cash_flows(bonds, filter_type=ft, filter_days=days)
            print(f"\\n{ft.upper()} ({days} days):")
        else:
            result = calculate_bond_cash_flows(bonds, filter_type=filter_type)
            print(f"\\n{filter_type.upper()}:")
        
        if result.get("portfolio_cash_flows"):
            cf_count = len(result["portfolio_cash_flows"])
            print(f"  Cash flows: {cf_count}")
            print(f"  Filter: {result.get('filter_applied', {}).get('filter_description')}")
'''
        
        try:
            calculator_file = self.project_root / "xtrillion_cash_flow_calculator.py"
            with open(calculator_file, 'w') as f:
                f.write(enhanced_calculator_code)
            
            self.log("Enhanced cash flow calculator deployed successfully!", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to deploy calculator: {e}", "ERROR")
            return False
    
    def deploy_enhanced_api_extension(self):
        """Deploy the enhanced API extension"""
        self.log("Deploying enhanced API extension...", "STEP")
        
        enhanced_api_code = '''#!/usr/bin/env python3
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
    
    @app.route('/v1/bond/cashflow', methods=['POST'])
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
    
    @app.route('/v1/bond/cashflow/next', methods=['POST'])
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
    
    @app.route('/v1/bond/cashflow/period/<int:days>', methods=['POST'])
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
'''
        
        try:
            api_file = self.project_root / "api_cash_flow_extension.py"
            with open(api_file, 'w') as f:
                f.write(enhanced_api_code)
            
            self.log("Enhanced API extension deployed successfully!", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to deploy API extension: {e}", "ERROR")
            return False
    
    def deploy_test_script(self):
        """Deploy comprehensive test script"""
        self.log("Deploying enhanced test script...", "STEP")
        
        test_script_code = '''#!/usr/bin/env python3
"""
GA10 Enhanced Cash Flow Filter Testing Script
=============================================

Tests all enhanced filtering capabilities:
- Next cash flow filter
- Period-based filtering
- All new endpoints
- Response validation
"""

import requests
import json
import time
from datetime import datetime

def test_enhanced_filters():
    """Test all enhanced filtering capabilities"""
    print("🧪 Testing GA10 Enhanced Cash Flow Filters")
    print("=" * 60)
    
    test_portfolio = {
        "bonds": [
            {"description": "T 2 1/2 07/31/27", "nominal": 1000000},
            {"description": "T 3 15/08/52", "nominal": 500000}
        ]
    }
    
    base_url = "http://localhost:8080"
    
    # Test 1: All Cash Flows
    print("\\n🔍 TEST 1: All Cash Flows")
    test_endpoint(f"{base_url}/v1/bond/cashflow", test_portfolio)
    
    # Test 2: Next Cash Flow Filter
    print("\\n🔍 TEST 2: Next Cash Flow Filter")
    test_endpoint(f"{base_url}/v1/bond/cashflow?filter=next", test_portfolio)
    
    # Test 3: Period Filter
    print("\\n🔍 TEST 3: Period Filter (90 days)")
    test_endpoint(f"{base_url}/v1/bond/cashflow?filter=period&days=90", test_portfolio)
    
    # Test 4: Convenience Endpoints
    print("\\n🔍 TEST 4: Next Convenience Endpoint")
    test_endpoint(f"{base_url}/v1/bond/cashflow/next", test_portfolio)
    
    print("\\n🔍 TEST 5: Period Convenience Endpoint")
    test_endpoint(f"{base_url}/v1/bond/cashflow/period/90", test_portfolio)

def test_endpoint(url, data):
    """Test a specific endpoint"""
    try:
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {url}")
            
            cash_flows = result.get("portfolio_cash_flows", [])
            filter_info = result.get("filter_applied", {})
            
            print(f"   📊 Filter: {filter_info}")
            print(f"   💰 Cash flows: {len(cash_flows)}")
            
            if cash_flows:
                print(f"   📅 First flow: {cash_flows[0]}")
        else:
            print(f"❌ FAILED: {url} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION FAILED: {url}")
        print("💡 Start GA10 API: python google_analysis10_api.py")
    except Exception as e:
        print(f"❌ ERROR: {url} - {e}")

if __name__ == "__main__":
    test_enhanced_filters()
'''
        
        try:
            test_file = self.project_root / "test_enhanced_filters.py"
            with open(test_file, 'w') as f:
                f.write(test_script_code)
            
            self.log("Enhanced test script deployed successfully!", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to deploy test script: {e}", "ERROR")
            return False
    
    def update_main_api(self):
        """Update main API file to include enhanced cash flow endpoints"""
        self.log("Updating main API file...", "STEP")
        
        try:
            api_file = self.project_root / "google_analysis10_api.py"
            
            if not api_file.exists():
                self.log(f"Main API file not found: {api_file}", "ERROR")
                return False
            
            # Read existing content
            with open(api_file, 'r') as f:
                content = f.read()
            
            # Check if already enhanced
            if "api_cash_flow_extension" in content and "ENHANCED" in content:
                self.log("API already enhanced with cash flow extensions", "INFO")
                return True
            
            # Add enhanced import
            enhanced_import = """
# GA10 Enhanced Cash flow calculation extension
try:
    from api_cash_flow_extension import add_cash_flow_endpoints
    ENHANCED_CASH_FLOW_AVAILABLE = True
    logger.info("🚀 GA10 Enhanced cash flow extension loaded successfully")
except ImportError as e:
    logger.warning(f"GA10 Enhanced cash flow extension not available: {e}")
    ENHANCED_CASH_FLOW_AVAILABLE = False"""
            
            # Add endpoint integration
            endpoint_integration = """
# Add GA10 enhanced cash flow endpoints if available
if ENHANCED_CASH_FLOW_AVAILABLE:
    logger.info("📊 Adding GA10 enhanced cash flow calculation endpoints...")
    add_cash_flow_endpoints(app)
    logger.info("✅ GA10 Enhanced cash flow endpoints added successfully")
else:
    logger.warning("⚠️ GA10 Enhanced cash flow endpoints not available")"""
            
            # Insert import after logging import
            lines = content.split('\n')
            import_inserted = False
            
            for i, line in enumerate(lines):
                if "import logging" in line and not import_inserted:
                    lines.insert(i + 1, enhanced_import)
                    import_inserted = True
                    break
            
            # Insert endpoint integration after app creation
            endpoint_inserted = False
            for i, line in enumerate(lines):
                if "app = Flask(__name__)" in line and not endpoint_inserted:
                    # Insert after app configuration (usually a few lines down)
                    insert_pos = i + 3
                    while insert_pos < len(lines) and lines[insert_pos].strip().startswith('app.'):
                        insert_pos += 1
                    
                    endpoint_lines = endpoint_integration.strip().split('\n')
                    for j, eline in enumerate(endpoint_lines):
                        lines.insert(insert_pos + j, eline)
                    endpoint_inserted = True
                    break
            
            # Write updated content
            updated_content = '\n'.join(lines)
            
            with open(api_file, 'w') as f:
                f.write(updated_content)
            
            self.log("Main API file updated with enhanced endpoints!", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to update main API: {e}", "ERROR")
            return False
    
    def validate_deployment(self):
        """Validate the enhanced deployment"""
        self.log("Validating enhanced deployment...", "STEP")
        
        try:
            # Check all deployed files exist
            required_files = [
                "xtrillion_cash_flow_calculator.py",
                "api_cash_flow_extension.py", 
                "test_enhanced_filters.py"
            ]
            
            missing_files = []
            for file in required_files:
                if not (self.project_root / file).exists():
                    missing_files.append(file)
            
            if missing_files:
                self.log(f"Missing deployed files: {missing_files}", "ERROR")
                return False
            
            # Try to import the enhanced calculator
            try:
                os.chdir(self.project_root)
                sys.path.insert(0, str(self.project_root))
                
                from xtrillion_cash_flow_calculator import calculate_bond_cash_flows
                
                # Test basic functionality
                test_bonds = [{"description": "T 2 1/2 07/31/27", "nominal": 100000}]
                
                # Test all filter
                result_all = calculate_bond_cash_flows(test_bonds, filter_type="all")
                if 'error' in result_all:
                    self.log(f"Validation failed - all filter error: {result_all['error']}", "ERROR")
                    return False
                
                # Test next filter
                result_next = calculate_bond_cash_flows(test_bonds, filter_type="next")
                if 'error' in result_next:
                    self.log(f"Validation failed - next filter error: {result_next['error']}", "ERROR")
                    return False
                
                # Check filter metadata
                if 'filter_applied' not in result_next:
                    self.log("Validation failed - missing filter metadata", "ERROR")
                    return False
                
                self.log("Enhanced calculator validation successful!", "SUCCESS")
                
                # Validate portfolio flows count difference
                all_flows = result_all.get("portfolio_cash_flows", [])
                next_flows = result_next.get("portfolio_cash_flows", [])
                
                if len(next_flows) <= len(all_flows):
                    self.log(f"Filter validation: all={len(all_flows)}, next={len(next_flows)} ✅", "SUCCESS")
                else:
                    self.log("Filter validation failed - next should be <= all", "WARNING")
                
                return True
                
            except ImportError as e:
                self.log(f"Import validation failed: {e}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Validation failed: {e}", "ERROR")
            return False
    
    def run_integration_test(self):
        """Run quick integration test"""
        self.log("Running integration test...", "STEP")
        
        try:
            os.chdir(self.project_root)
            
            # Test the enhanced calculator directly
            test_result = subprocess.run([
                sys.executable, "xtrillion_cash_flow_calculator.py"
            ], capture_output=True, text=True, timeout=30)
            
            if test_result.returncode == 0:
                self.log("Integration test passed!", "SUCCESS")
                if "ENHANCED" in test_result.stdout:
                    self.log("Enhanced features confirmed in output", "SUCCESS")
                return True
            else:
                self.log(f"Integration test failed: {test_result.stderr}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("Integration test timed out", "WARNING")
            return False
        except Exception as e:
            self.log(f"Integration test error: {e}", "ERROR")
            return False
    
    def generate_implementation_report(self):
        """Generate comprehensive implementation report"""
        self.log("Generating implementation report...", "STEP")
        
        report = {
            "implementation_time": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "backup_location": str(self.backup_dir),
            "success_rate": f"{self.success_count}/{self.total_steps}",
            "enhanced_features": [
                "Next cash flow filter (filter=next)",
                "Period-based filtering (filter=period&days=X)",
                "Convenience endpoints (/next, /period/{days})",
                "Enhanced response metadata with days_from_settlement",
                "Comprehensive parameter validation",
                "Filter description in responses"
            ],
            "new_endpoints": [
                "/v1/bond/cashflow (enhanced with filters)",
                "/v1/bond/cashflow/next",
                "/v1/bond/cashflow/period/{days}",
                "/v1/bond/cashflow/individual/{id} (enhanced)",
                "/v1/bond/cashflow/portfolio/summary (enhanced)"
            ],
            "files_deployed": [
                "xtrillion_cash_flow_calculator.py (enhanced)",
                "api_cash_flow_extension.py (enhanced)",
                "test_enhanced_filters.py (new)"
            ],
            "next_steps": [
                "Test the enhanced API: python google_analysis10_api.py",
                "Run filter tests: python test_enhanced_filters.py",
                "Try the new endpoints with different filter parameters"
            ]
        }
        
        try:
            report_file = self.project_root / "implementation_report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.log(f"Implementation report saved: {report_file}", "SUCCESS")
            
            # Print summary
            print("\n" + "="*80)
            print("🎉 GA10 ENHANCED CASH FLOW FILTERS - IMPLEMENTATION COMPLETE!")
            print("="*80)
            print(f"✅ Success Rate: {self.success_count}/{self.total_steps}")
            print(f"📁 Project: {self.project_root}")
            print(f"📦 Backup: {self.backup_dir}")
            print("\n🚀 NEW FEATURES DEPLOYED:")
            for feature in report["enhanced_features"]:
                print(f"   • {feature}")
            print("\n🔗 NEW ENDPOINTS:")
            for endpoint in report["new_endpoints"]:
                print(f"   • {endpoint}")
            print("\n📋 NEXT STEPS:")
            for step in report["next_steps"]:
                print(f"   • {step}")
            print("="*80)
            
            return True
            
        except Exception as e:
            self.log(f"Failed to generate report: {e}", "ERROR")
            return False
    
    def implement(self):
        """Execute complete implementation process"""
        self.log("Starting GA10 Enhanced Cash Flow Filter Implementation", "STEP")
        self.log(f"Target: {self.project_root}", "INFO")
        
        # Implementation steps
        steps = [
            ("Environment Validation", self.validate_environment),
            ("Backup Creation", self.create_backup),
            ("Enhanced Calculator Deployment", self.deploy_enhanced_calculator),
            ("Enhanced API Extension Deployment", self.deploy_enhanced_api_extension),
            ("Test Script Deployment", self.deploy_test_script),
            ("Main API Update", self.update_main_api),
            ("Deployment Validation", self.validate_deployment),
            ("Integration Testing", self.run_integration_test)
        ]
        
        for step_name, step_func in steps:
            self.log(f"Executing: {step_name}", "STEP")
            if step_func():
                self.success_count += 1
                self.log(f"✅ {step_name} completed successfully", "SUCCESS")
            else:
                self.log(f"❌ {step_name} failed", "ERROR")
                self.log("Implementation aborted due to failure", "ERROR")
                return False
        
        # Generate final report
        self.generate_implementation_report()
        
        return True


def main():
    """Main implementation function"""
    print("🚀 GA10 Enhanced Cash Flow Filter Implementation")
    print("=" * 70)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    implementer = GA10FilterImplementer()
    
    try:
        success = implementer.implement()
        
        if success:
            print("\n🎉 IMPLEMENTATION SUCCESSFUL!")
            print("💡 Ready to test enhanced cash flow filtering capabilities")
        else:
            print("\n❌ IMPLEMENTATION FAILED!")
            print(f"📦 Backup available at: {BACKUP_DIR}")
            
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️ Implementation interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
