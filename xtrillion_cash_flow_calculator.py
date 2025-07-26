#!/usr/bin/env python3
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
            r'(\d+)\s*([⅛¼⅜½⅝¾⅞]|\d/\d)',
            r'(\d+\.\d+)%?',
            r'(\d+)%',
            r'\b(\d+\.?\d*)\s*(?=%|$)',
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
                r'(\d{1,2})/(\d{1,2})/(\d{2,4})',
                r'(\d{1,2})-(\d{1,2})-(\d{2,4})',
                r'(\d{2})(\d{2})(\d{2})',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, description)
                if match:
                    if len(match.groups()) == 3:
                        if pattern.startswith(r'(\d{4})'):
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
            print(f"\n{ft.upper()} ({days} days):")
        else:
            result = calculate_bond_cash_flows(bonds, filter_type=filter_type)
            print(f"\n{filter_type.upper()}:")
        
        if result.get("portfolio_cash_flows"):
            cf_count = len(result["portfolio_cash_flows"])
            print(f"  Cash flows: {cf_count}")
            print(f"  Filter: {result.get('filter_applied', {}).get('filter_description')}")
