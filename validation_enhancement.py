#!/usr/bin/env python3
"""
XTrillion API Validation Enhancement
Adds bond validation status and confidence levels to API responses
This addresses the critical need for data quality transparency in professional use
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import json

class BondValidationEnhancer:
    """Enhances bond analysis responses with validation information"""
    
    # Map existing routes to validation levels
    ROUTE_TO_VALIDATION = {
        "primary_database_isin": {
            "status": "validated",
            "confidence": "high",
            "source": "primary_database",
            "description": "Bond found in primary validated database"
        },
        "secondary_database_isin": {
            "status": "validated", 
            "confidence": "medium",
            "source": "secondary_database",
            "description": "Bond found in secondary reference database"
        },
        "bloomberg_index_isin": {
            "status": "validated",
            "confidence": "high", 
            "source": "bloomberg_reference",
            "description": "Bond found in Bloomberg reference index"
        },
        "parse_hierarchy": {
            "status": "parsed",
            "confidence": "medium",
            "source": "description_parsing",
            "description": "Bond identified through smart description parsing"
        },
        "universal_parser": {
            "status": "parsed",
            "confidence": "medium",
            "source": "universal_parser", 
            "description": "Bond processed through universal parser system"
        },
        "csv_fallback": {
            "status": "estimated",
            "confidence": "low",
            "source": "csv_fallback",
            "description": "Bond conventions estimated from CSV fallback"
        },
        "manual_override": {
            "status": "manual",
            "confidence": "variable",
            "source": "manual_entry",
            "description": "Bond parameters manually specified"
        }
    }
    
    @classmethod
    def enhance_bond_response(cls, original_response: Dict, route_used: str = None) -> Dict:
        """
        Enhance existing bond response with validation information
        
        Args:
            original_response: Current API response
            route_used: Route used for bond identification
            
        Returns:
            Enhanced response with validation section
        """
        enhanced_response = original_response.copy()
        
        # Extract route from existing response if not provided
        if not route_used and "bond" in enhanced_response:
            route_used = enhanced_response["bond"].get("route_used", "unknown")
        
        # Get validation info for this route
        validation_info = cls.ROUTE_TO_VALIDATION.get(route_used, {
            "status": "unknown",
            "confidence": "low",
            "source": "unknown",
            "description": "Validation method not identified"
        })
        
        # Add enhanced validation section to bond data
        if "bond" in enhanced_response:
            enhanced_response["bond"]["validation"] = {
                **validation_info,
                "route_used": route_used,
                "timestamp": datetime.utcnow().isoformat(),
                "api_version": "enhanced_v1.1"
            }
            
            # Add field-level validation if we can determine it
            enhanced_response["bond"]["validation"]["field_validation"] = cls._get_field_validation(
                enhanced_response, route_used
            )
        
        return enhanced_response
    
    @classmethod
    def _get_field_validation(cls, response: Dict, route_used: str) -> Dict:
        """Determine which fields are validated vs estimated"""
        
        if route_used in ["primary_database_isin", "secondary_database_isin", "bloomberg_index_isin"]:
            # Database sources - most fields validated
            return {
                "validated_fields": [
                    "coupon_rate", "maturity_date", "frequency", "day_count",
                    "business_day_convention", "issuer", "currency"
                ],
                "estimated_fields": [],
                "derived_fields": ["accrued_interest", "dirty_price", "settlement_date"]
            }
        elif route_used in ["parse_hierarchy", "universal_parser"]:
            # Parsed sources - some fields validated, some estimated
            return {
                "validated_fields": [
                    "coupon_rate", "maturity_date", "issuer"
                ],
                "estimated_fields": [
                    "frequency", "day_count", "business_day_convention"
                ],
                "derived_fields": ["accrued_interest", "dirty_price", "settlement_date"]
            }
        else:
            # Fallback sources - most fields estimated
            return {
                "validated_fields": [],
                "estimated_fields": [
                    "coupon_rate", "maturity_date", "frequency", "day_count",
                    "business_day_convention"
                ],
                "derived_fields": ["accrued_interest", "dirty_price", "settlement_date"]
            }

def create_enhanced_response_example():
    """Create example of enhanced response with validation info"""
    
    # Original response (current format)
    original_response = {
        "status": "success",
        "bond": {
            "description": "T 3 15/08/52",
            "isin": None,
            "conventions": {
                "fixed_frequency": "Semiannual",
                "day_count": "ActualActual_Bond", 
                "business_day_convention": "Following",
                "end_of_month": True
            },
            "route_used": "parse_hierarchy"
        },
        "analytics": {
            "ytm": 4.89906406402588,
            "duration": 16.351196293083248,
            "accrued_interest": 1.1123595505617923,
            "clean_price": 71.66,
            "dirty_price": 72.77236,
            "macaulay_duration": 16.751724,
            "annual_duration": 15.960245,
            "ytm_annual": 4.959066,
            "convexity": 370.2138302186875,
            "pvbp": 0.11717267263623456,
            "settlement_date": "2025-06-30",
            "spread": None,
            "z_spread": None
        },
        "calculations": {
            "basis": "Semi-annual compounding",
            "day_count": "ActualActual_Bond",
            "business_day_convention": "Following"
        },
        "metadata": {
            "api_version": "v1.2",
            "calculation_engine": "xtrillion_core_quantlib_engine"
        }
    }
    
    # Enhanced response with validation
    enhanced_response = BondValidationEnhancer.enhance_bond_response(
        original_response, "parse_hierarchy"
    )
    
    return enhanced_response

def create_portfolio_validation_example():
    """Create example of portfolio response with validation summary"""
    
    portfolio_response = {
        "status": "success",
        "format": "YAS",
        "bond_data": [
            {
                "status": "success",
                "name": "T 3 15/08/52",
                "yield": "4.90%",
                "duration": "16.4 years", 
                "price": 71.66,
                "validation": {
                    "status": "parsed",
                    "confidence": "medium",
                    "source": "description_parsing"
                }
            },
            {
                "status": "success",
                "name": "PANAMA, 3.87%, 23-Jul-2060",
                "yield": "7.33%", 
                "duration": "13.6 years",
                "price": 56.60,
                "validation": {
                    "status": "validated",
                    "confidence": "high", 
                    "source": "primary_database"
                }
            }
        ],
        "portfolio_metrics": {
            "portfolio_yield": "5.87%",
            "portfolio_duration": "15.3 years",
            "portfolio_spread": "0 bps",
            "total_bonds": 2,
            "success_rate": "100.0%",
            "data_quality": {
                "validated_bonds": 1,
                "parsed_bonds": 1,
                "estimated_bonds": 0,
                "overall_confidence": "medium-high",
                "confidence_weighted_by_size": "high"
            }
        }
    }
    
    return portfolio_response

def create_excel_validation_functions():
    """Create Excel function specifications for validation"""
    
    excel_functions = {
        "xt_validation_status": {
            "syntax": "=xt_validation_status(ISIN, Description, Price)",
            "returns": "String: 'validated' | 'parsed' | 'estimated' | 'unknown'",
            "description": "Returns validation status for bond data quality",
            "example": "=xt_validation_status(A2, B2, C2) → 'validated'"
        },
        "xt_confidence": {
            "syntax": "=xt_confidence(ISIN, Description, Price)", 
            "returns": "String: 'high' | 'medium' | 'low'",
            "description": "Returns confidence level in bond data accuracy",
            "example": "=xt_confidence(A2, B2, C2) → 'high'"
        },
        "xt_data_source": {
            "syntax": "=xt_data_source(ISIN, Description, Price)",
            "returns": "String: Source of bond data",
            "description": "Returns data source for transparency",
            "example": "=xt_data_source(A2, B2, C2) → 'primary_database'"
        },
        "xt_validation_score": {
            "syntax": "=xt_validation_score(ISIN, Description, Price)",
            "returns": "Number: 0-100 validation score",
            "description": "Numeric score for data quality (100=highest)",
            "example": "=xt_validation_score(A2, B2, C2) → 85"
        }
    }
    
    return excel_functions

def main():
    """Demonstrate validation enhancement"""
    print("🎯 XTrillion API Validation Enhancement")
    print("="*60)
    
    # Show enhanced individual bond response
    print("\n📊 Enhanced Individual Bond Response:")
    enhanced_response = create_enhanced_response_example()
    print(json.dumps(enhanced_response, indent=2))
    
    # Show portfolio validation summary
    print("\n📋 Enhanced Portfolio Response:")
    portfolio_example = create_portfolio_validation_example()
    print(json.dumps(portfolio_example, indent=2))
    
    # Show Excel function specifications
    print("\n📝 New Excel Validation Functions:")
    excel_functions = create_excel_validation_functions()
    for func_name, func_spec in excel_functions.items():
        print(f"\n🔧 {func_name}:")
        print(f"   Syntax: {func_spec['syntax']}")
        print(f"   Returns: {func_spec['returns']}")
        print(f"   Example: {func_spec['example']}")
    
    print("\n✅ Validation enhancement ready for implementation!")
    print("   Professional transparency for institutional users")

if __name__ == "__main__":
    main()