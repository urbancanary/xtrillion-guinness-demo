#!/usr/bin/env python3
"""
Process User's 25-Bond Portfolio Using Proven Google Analysis 10 Infrastructure
==============================================================================

Leverages existing proven components:
- bloomberg_accrued_calculator.py (390 lines of tested calculations)
- Universal Parser integration
- calculate_bond_master function (Bloomberg-validated)
- Existing API patterns

Input: User's 25-bond portfolio dataset
Output: Individual bond characteristics + Portfolio summary
"""

import sys
import os
import json
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add current directory to path
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

# Import proven components (following reuse strategy)
from bloomberg_accrued_calculator import BloombergAccruedCalculator
from bond_master_hierarchy_enhanced import calculate_bond_master

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_user_portfolio_dataset():
    """Create the user's 25-bond portfolio dataset"""
    
    # User's portfolio data (exactly as provided)
    portfolio_data = [
        {
            "BOND_CD": "XS2233188353",
            "FACE_AMOUNT": 700000,
            "CLOSING_PRICE": 99.529,
            "TOTAL_COST": 703690.91,
            "WEIGHTING": 4.87,
            "CURRENCY": "USD",
            "Market_Value": 696703,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "QNBK 1 5/8 09/22/25",
            "WithDividendP": 7.381,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "US279158AJ82",
            "FACE_AMOUNT": 600000,
            "CLOSING_PRICE": 70.804,
            "TOTAL_COST": 406900,
            "WEIGHTING": 2.97,
            "CURRENCY": "USD",
            "Market_Value": 424824,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "ECOPET 5 7/8 05/28/45",
            "WithDividendP": 40.6884,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "US71654QDE98",
            "FACE_AMOUNT": 200000,
            "CLOSING_PRICE": 91.655,
            "TOTAL_COST": 166500,
            "WEIGHTING": 1.28,
            "CURRENCY": "USD",
            "Market_Value": 183310,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "PEMEX 5.95 01/28/31",
            "WithDividendP": 95.2984,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "US71654QDF63",
            "FACE_AMOUNT": 750000,
            "CLOSING_PRICE": 74.422,
            "TOTAL_COST": 592500,
            "WEIGHTING": 3.9,
            "CURRENCY": "USD",
            "Market_Value": 558165,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "PEMEX 6.95 01/28/60",
            "WithDividendP": 84.7963,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "USP0R80BAG79",
            "FACE_AMOUNT": 450000,
            "CLOSING_PRICE": 98.336,
            "TOTAL_COST": 402750,
            "WEIGHTING": 3.09,
            "CURRENCY": "USD",
            "Market_Value": 442512,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "AMXLMM 5 3/8 04/04/32",
            "WithDividendP": 32.4591,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "USP30179BR86",
            "FACE_AMOUNT": 1000000,
            "CLOSING_PRICE": 87.251,
            "TOTAL_COST": 843050,
            "WEIGHTING": 6.1,
            "CURRENCY": "USD",
            "Market_Value": 872510,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "CFELEC 6.264 02/15/52",
            "WithDividendP": 23.648,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "USP3143NAH72",
            "FACE_AMOUNT": 800000,
            "CLOSING_PRICE": 102.094,
            "TOTAL_COST": 872414.21,
            "WEIGHTING": 5.71,
            "CURRENCY": "USD",
            "Market_Value": 816752,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "CDEL 6.15 10/24/36",
            "WithDividendP": 13.7672,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "USP37110AM89",
            "FACE_AMOUNT": 500000,
            "CLOSING_PRICE": 77.461,
            "TOTAL_COST": 379375,
            "WEIGHTING": 2.71,
            "CURRENCY": "USD",
            "Market_Value": 387305,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "ENAPCL 4 1/2 09/14/47",
            "WithDividendP": 16.858,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "USP37466AS18",
            "FACE_AMOUNT": 800000,
            "CLOSING_PRICE": 80.902,
            "TOTAL_COST": 659199.99,
            "WEIGHTING": 4.52,
            "CURRENCY": "USD",
            "Market_Value": 647216,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "BMETR 4.7 05/07/50",
            "WithDividendP": 4.7238,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "USP6629MAD40",
            "FACE_AMOUNT": 650000,
            "CLOSING_PRICE": 84.093,
            "TOTAL_COST": 472730,
            "WEIGHTING": 3.82,
            "CURRENCY": "USD",
            "Market_Value": 546604.5,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "MEXCAT 5 1/2 07/31/47",
            "WithDividendP": 31.9231,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "XS0911024635",
            "FACE_AMOUNT": 500000,
            "CLOSING_PRICE": 93.47,
            "TOTAL_COST": 583267.14,
            "WEIGHTING": 3.27,
            "CURRENCY": "USD",
            "Market_Value": 467350,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "SECO 5.06 04/08/43",
            "WithDividendP": 8.2153,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "XS1709535097",
            "FACE_AMOUNT": 600000,
            "CLOSING_PRICE": 89.881,
            "TOTAL_COST": 685655.02,
            "WEIGHTING": 3.77,
            "CURRENCY": "USD",
            "Market_Value": 539286,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "ADNOUH 4.6 11/02/47",
            "WithDividendP": 1.5131,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "XS1807299331",
            "FACE_AMOUNT": 1000000,
            "CLOSING_PRICE": 93.481,
            "TOTAL_COST": 882500,
            "WEIGHTING": 6.54,
            "CURRENCY": "USD",
            "Market_Value": 934810,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "KZOKZ 6 3/8 10/24/48",
            "WithDividendP": 21.4648,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "XS1982113463",
            "FACE_AMOUNT": 600000,
            "CLOSING_PRICE": 87.982,
            "TOTAL_COST": 663000,
            "WEIGHTING": 3.69,
            "CURRENCY": "USD",
            "Market_Value": 527892,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "ARAMCO 4 1/4 04/16/39",
            "WithDividendP": 3.1859,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "XS2249741674",
            "FACE_AMOUNT": 700000,
            "CLOSING_PRICE": 78.43,
            "TOTAL_COST": 617990,
            "WEIGHTING": 3.84,
            "CURRENCY": "USD",
            "Market_Value": 549010,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "ADGLXY 3 1/4 09/30/40",
            "WithDividendP": 1.0262,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "XS2359548935",
            "FACE_AMOUNT": 700000,
            "CLOSING_PRICE": 74.468,
            "TOTAL_COST": 506625,
            "WEIGHTING": 3.64,
            "CURRENCY": "USD",
            "Market_Value": 521276,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "QPETRO 3 1/8 07/12/41",
            "WithDividendP": 11.9074,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "XS2542166231",
            "FACE_AMOUNT": 400000,
            "CLOSING_PRICE": 103.757,
            "TOTAL_COST": 412800,
            "WEIGHTING": 2.9,
            "CURRENCY": "USD",
            "Market_Value": 415028,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "GASBCM 6.129 02/23/38",
            "WithDividendP": 14.675,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "XS2585988145",
            "FACE_AMOUNT": 450000,
            "CLOSING_PRICE": 85.78,
            "TOTAL_COST": 391500,
            "WEIGHTING": 2.7,
            "CURRENCY": "USD",
            "Market_Value": 386010,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "PIFKSA 5 1/8 02/14/53",
            "WithDividendP": 6.8902,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "US195325DX04",
            "FACE_AMOUNT": 1000000,
            "CLOSING_PRICE": 55.068,
            "TOTAL_COST": 587249.99,
            "WEIGHTING": 3.85,
            "CURRENCY": "USD",
            "Market_Value": 550680,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "COLOM 3 7/8 02/15/61",
            "WithDividendP": 16.5473,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "US698299BL70",
            "FACE_AMOUNT": 1000000,
            "CLOSING_PRICE": 57.888,
            "TOTAL_COST": 607400,
            "WEIGHTING": 4.05,
            "CURRENCY": "USD",
            "Market_Value": 578880,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "PANAMA 3.87 07/23/60",
            "WithDividendP": 0.2725,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "US91086QAZ19",
            "FACE_AMOUNT": 300000,
            "CLOSING_PRICE": 77.789,
            "TOTAL_COST": 270750,
            "WEIGHTING": 1.63,
            "CURRENCY": "USD",
            "Market_Value": 233367,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "MEX 5 3/4 10/12/2110",
            "WithDividendP": 7.6741,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "US912810TJ79",
            "FACE_AMOUNT": 200000,
            "CLOSING_PRICE": 70.53125,
            "TOTAL_COST": 154665.36,
            "WEIGHTING": 0.99,
            "CURRENCY": "USD",
            "Market_Value": 141062.5,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "T 3 08/15/52",
            "WithDividendP": -1.415,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "XS1508675508",
            "FACE_AMOUNT": 700000,
            "CLOSING_PRICE": 82.462,
            "TOTAL_COST": 730548.49,
            "WEIGHTING": 4.03,
            "CURRENCY": "USD",
            "Market_Value": 577234,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "KSA 4 1/2 10/26/46",
            "WithDividendP": 0.1889,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "XS1959337749",
            "FACE_AMOUNT": 700000,
            "CLOSING_PRICE": 91.462,
            "TOTAL_COST": 693070,
            "WEIGHTING": 4.48,
            "CURRENCY": "USD",
            "Market_Value": 640234,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "QATAR 4.817 03/14/49",
            "WithDividendP": 11.5634,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        },
        {
            "BOND_CD": "XS2167193015",
            "FACE_AMOUNT": 900000,
            "CLOSING_PRICE": 64.591,
            "TOTAL_COST": 649874.99,
            "WEIGHTING": 4.06,
            "CURRENCY": "USD",
            "Market_Value": 581319,
            "Inventory_Date": "25/07/2025",
            "BOND_ENAME": "ISRAEL 3.8 05/13/60",
            "WithDividendP": 0.494,
            "Fund_Name": "Shin Kong Emerging Wealthy Nations Bond Fund"
        }
    ]
    
    return portfolio_data

def process_individual_bond(bond_data: Dict[str, Any], settlement_date: str = "2025-07-28") -> Dict[str, Any]:
    """
    Process individual bond using proven Google Analysis 10 infrastructure
    
    Uses the same proven patterns as the existing API and 25-bond test framework
    """
    try:
        # Extract bond identification (try ISIN first, fall back to description)
        isin = bond_data.get("BOND_CD", "")
        description = bond_data.get("BOND_ENAME", "")
        price = bond_data.get("CLOSING_PRICE", 0)
        
        # Use proven calculate_bond_master function (Bloomberg-validated)
        logger.info(f"Processing bond: {isin} - {description} @ {price}")
        
        # Database paths (using existing proven setup)
        bonds_db = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db"
        quantlib_db = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/validated_quantlib_bonds.db"
        bloomberg_db = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bloomberg_index.db"
        
        # Call proven calculation function (using correct parameter names)
        result = calculate_bond_master(
            isin=isin,
            description=description,
            price=price,
            settlement_date=settlement_date,
            db_path=bonds_db,
            validated_db_path=quantlib_db,
            bloomberg_db_path=bloomberg_db
        )
        
        if result and result.get('success', False):
            # Combine user portfolio data with calculated analytics
            bond_result = {
                # User's original data
                "bond_identifier": {
                    "isin": isin,
                    "description": description,
                    "bond_name": bond_data.get("BOND_ENAME", "")
                },
                "portfolio_data": {
                    "face_amount": bond_data.get("FACE_AMOUNT", 0),
                    "closing_price": price,
                    "total_cost": bond_data.get("TOTAL_COST", 0),
                    "market_value": bond_data.get("Market_Value", 0),
                    "weighting": bond_data.get("WEIGHTING", 0),
                    "currency": bond_data.get("CURRENCY", "USD"),
                    "with_dividend_p": bond_data.get("WithDividendP", 0)
                },
                # Calculated analytics (using proven infrastructure)
                "analytics": {
                    "yield_to_maturity": result.get('yield', None),
                    "duration": result.get('duration', None),
                    "convexity": result.get('convexity', None),
                    "spread": result.get('spread', None),
                    "accrued_interest": result.get('accrued_interest', None),
                    "pvbp": result.get('pvbp', None),
                    "clean_price": result.get('clean_price', None),
                    "dirty_price": result.get('dirty_price', None)
                },
                "metadata": {
                    "calculation_date": datetime.now().isoformat(),
                    "settlement_date": settlement_date,
                    "calculation_success": True,
                    "conventions": result.get('conventions', {})
                }
            }
            
            return bond_result
            
        else:
            # Handle calculation failure
            logger.warning(f"Calculation failed for {isin} - {description}")
            return {
                "bond_identifier": {"isin": isin, "description": description},
                "portfolio_data": {
                    "face_amount": bond_data.get("FACE_AMOUNT", 0),
                    "closing_price": price,
                    "market_value": bond_data.get("Market_Value", 0)
                },
                "analytics": {},
                "metadata": {
                    "calculation_success": False,
                    "error": result.get('error', 'Unknown calculation error')
                }
            }
            
    except Exception as e:
        logger.error(f"Error processing bond {bond_data.get('BOND_CD', 'Unknown')}: {str(e)}")
        return {
            "bond_identifier": {"isin": bond_data.get("BOND_CD", ""), "error": str(e)},
            "metadata": {"calculation_success": False, "error": str(e)}
        }

def calculate_portfolio_summary(portfolio_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate portfolio-level summary statistics"""
    
    total_face_amount = 0
    total_market_value = 0
    total_cost = 0
    successful_calculations = 0
    failed_calculations = 0
    
    # Weighted averages
    total_weighted_yield = 0
    total_weighted_duration = 0
    total_weights = 0
    
    for bond_result in portfolio_results:
        if bond_result.get('metadata', {}).get('calculation_success', False):
            successful_calculations += 1
            
            # Portfolio aggregation
            portfolio_data = bond_result.get('portfolio_data', {})
            total_face_amount += portfolio_data.get('face_amount', 0)
            total_market_value += portfolio_data.get('market_value', 0)
            total_cost += portfolio_data.get('total_cost', 0)
            
            # Weighted averages (by market value)
            market_value = portfolio_data.get('market_value', 0)
            if market_value > 0:
                analytics = bond_result.get('analytics', {})
                ytm = analytics.get('yield_to_maturity', 0)
                duration = analytics.get('duration', 0)
                
                if ytm and duration:
                    total_weighted_yield += ytm * market_value
                    total_weighted_duration += duration * market_value
                    total_weights += market_value
        else:
            failed_calculations += 1
    
    # Calculate weighted averages
    portfolio_yield = total_weighted_yield / total_weights if total_weights > 0 else 0
    portfolio_duration = total_weighted_duration / total_weights if total_weights > 0 else 0
    
    return {
        "portfolio_totals": {
            "total_bonds": len(portfolio_results),
            "successful_calculations": successful_calculations,
            "failed_calculations": failed_calculations,
            "total_face_amount": total_face_amount,
            "total_market_value": total_market_value,
            "total_cost": total_cost
        },
        "portfolio_analytics": {
            "weighted_average_yield": portfolio_yield,
            "weighted_average_duration": portfolio_duration,
            "portfolio_return": ((total_market_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
        },
        "metadata": {
            "calculation_date": datetime.now().isoformat(),
            "portfolio_name": "Shin Kong Emerging Wealthy Nations Bond Fund",
            "base_currency": "USD"
        }
    }

def main():
    """Main execution function - process user's portfolio using proven infrastructure"""
    
    logger.info("🚀 Starting User Portfolio Processing using Google Analysis 10 Infrastructure")
    logger.info("📊 Leveraging: Bloomberg Calculator + Universal Parser + Proven API patterns")
    
    # Create user's portfolio dataset
    portfolio_data = create_user_portfolio_dataset()
    logger.info(f"📋 Processing {len(portfolio_data)} bonds from user portfolio")
    
    # Process each bond individually using proven infrastructure
    portfolio_results = []
    
    for i, bond_data in enumerate(portfolio_data, 1):
        logger.info(f"🔍 Processing bond {i}/{len(portfolio_data)}: {bond_data.get('BOND_CD', 'Unknown')}")
        bond_result = process_individual_bond(bond_data)
        portfolio_results.append(bond_result)
    
    # Calculate portfolio summary
    portfolio_summary = calculate_portfolio_summary(portfolio_results)
    
    # Combine results
    complete_analysis = {
        "individual_bonds": portfolio_results,
        "portfolio_summary": portfolio_summary,
        "metadata": {
            "processing_date": datetime.now().isoformat(),
            "infrastructure_used": "Google Analysis 10 - Proven Bloomberg Calculations",
            "total_bonds_processed": len(portfolio_results)
        }
    }
    
    # Save results
    output_file = f"user_portfolio_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(complete_analysis, f, indent=2)
    
    logger.info(f"✅ Portfolio analysis complete!")
    logger.info(f"📄 Results saved to: {output_file}")
    logger.info(f"📊 Summary: {portfolio_summary['portfolio_totals']['successful_calculations']}/{len(portfolio_data)} bonds processed successfully")
    
    return complete_analysis

if __name__ == "__main__":
    results = main()
