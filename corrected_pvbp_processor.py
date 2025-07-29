#!/usr/bin/env python3
"""
CORRECTED: User Portfolio Processor with Proper PVBP Scaling
=========================================================

Fixes PVBP calculation to show actual dollar impact for holding sizes
rather than per $100 face value convention.
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

# Import proven components
from bloomberg_accrued_calculator import BloombergAccruedCalculator
from bond_master_hierarchy_enhanced import calculate_bond_master

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_individual_bond_corrected(bond_data: Dict[str, Any], settlement_date: str = "2025-07-28") -> Dict[str, Any]:
    """
    Process individual bond with CORRECTED PVBP scaling for actual holding size
    """
    try:
        # Extract bond identification
        isin = bond_data.get("BOND_CD", "")
        description = bond_data.get("BOND_ENAME", "")
        price = bond_data.get("CLOSING_PRICE", 0)
        face_amount = bond_data.get("FACE_AMOUNT", 0)
        
        logger.info(f"Processing bond: {isin} - {description} @ {price}, Face: ${face_amount:,}")
        
        # Database paths
        bonds_db = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db"
        quantlib_db = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/validated_quantlib_bonds.db"
        bloomberg_db = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bloomberg_index.db"
        
        # Call proven calculation function
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
            # CORRECTED PVBP CALCULATION
            pvbp_per_100 = result.get('pvbp', 0)
            pvbp_for_holding = pvbp_per_100 * (face_amount / 100)  # Scale to actual holding
            
            # Calculate additional position-sized metrics
            duration_contribution = result.get('duration', 0) * bond_data.get("Market_Value", 0) / 100
            
            bond_result = {
                "bond_identifier": {
                    "isin": isin,
                    "description": description,
                    "bond_name": bond_data.get("BOND_ENAME", "")
                },
                "portfolio_data": {
                    "face_amount": face_amount,
                    "closing_price": price,
                    "total_cost": bond_data.get("TOTAL_COST", 0),
                    "market_value": bond_data.get("Market_Value", 0),
                    "weighting": bond_data.get("WEIGHTING", 0),
                    "currency": bond_data.get("CURRENCY", "USD"),
                    "with_dividend_p": bond_data.get("WithDividendP", 0)
                },
                "analytics": {
                    "yield_to_maturity": result.get('yield', None),
                    "duration": result.get('duration', None),
                    "convexity": result.get('convexity', None),
                    "spread": result.get('spread', None),
                    "accrued_interest": result.get('accrued_interest', None),
                    "pvbp_per_100": pvbp_per_100,  # Original per $100 face value
                    "pvbp_for_holding": pvbp_for_holding,  # CORRECTED for actual holding size
                    "clean_price": result.get('clean_price', None),
                    "dirty_price": result.get('dirty_price', None)
                },
                "position_metrics": {
                    "duration_contribution_dollars": duration_contribution,
                    "annual_coupon_dollars": (result.get('accrued_interest', 0) * face_amount / 100) if result.get('accrued_interest') else 0,
                    "market_value_dollars": bond_data.get("Market_Value", 0)
                },
                "metadata": {
                    "calculation_date": datetime.now().isoformat(),
                    "settlement_date": settlement_date,
                    "calculation_success": True,
                    "conventions": result.get('conventions', {}),
                    "pvbp_scaling_note": f"PVBP scaled from per $100 ({pvbp_per_100:.6f}) to holding size ${face_amount:,} = ${pvbp_for_holding:.2f}"
                }
            }
            
            return bond_result
            
        else:
            logger.warning(f"Calculation failed for {isin} - {description}")
            return {
                "bond_identifier": {"isin": isin, "description": description},
                "portfolio_data": {
                    "face_amount": face_amount,
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

def main():
    """Process a sample of bonds to demonstrate corrected PVBP calculation"""
    
    logger.info("🔧 Processing Sample Bonds with CORRECTED PVBP Scaling")
    
    # Sample bonds from user's portfolio
    sample_bonds = [
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
        }
    ]
    
    corrected_results = []
    
    for i, bond_data in enumerate(sample_bonds, 1):
        logger.info(f"🔍 Processing sample bond {i}/{len(sample_bonds)}: {bond_data.get('BOND_CD', 'Unknown')}")
        bond_result = process_individual_bond_corrected(bond_data)
        corrected_results.append(bond_result)
    
    # Save corrected results
    output_file = f"corrected_pvbp_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    complete_results = {
        "corrected_analysis": corrected_results,
        "pvbp_correction_notes": {
            "issue_identified": "Original PVBP was per $100 face value",
            "correction_applied": "PVBP now scaled to actual holding size",
            "formula_used": "PVBP_for_holding = PVBP_per_100 × (Face_Amount / 100)",
            "example": "QNBK bond: 0.0076 × (700,000/100) = $53.20"
        },
        "metadata": {
            "correction_date": datetime.now().isoformat(),
            "bonds_analyzed": len(corrected_results)
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(complete_results, f, indent=2)
    
    logger.info(f"✅ Corrected PVBP analysis complete!")
    logger.info(f"📄 Results saved to: {output_file}")
    
    # Display comparison for first bond
    if corrected_results and corrected_results[0].get('metadata', {}).get('calculation_success'):
        bond = corrected_results[0]
        analytics = bond.get('analytics', {})
        logger.info(f"\n📊 PVBP CORRECTION EXAMPLE:")
        logger.info(f"Bond: {bond['bond_identifier']['description']}")
        logger.info(f"Face Amount: ${bond['portfolio_data']['face_amount']:,}")
        logger.info(f"PVBP per $100: {analytics.get('pvbp_per_100', 0):.6f}")
        logger.info(f"PVBP for Holding: ${analytics.get('pvbp_for_holding', 0):.2f}")
        logger.info(f"Scaling Factor: {bond['portfolio_data']['face_amount']/100:,.0f}x")
    
    return corrected_results

if __name__ == "__main__":
    results = main()
