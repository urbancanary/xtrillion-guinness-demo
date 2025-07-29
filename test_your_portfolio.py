#!/usr/bin/env python3
"""
Test Your Portfolio - Direct Local Testing
=========================================
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_test():
    """Quick test of your portfolio bonds"""
    
    # Your portfolio data (add more bonds here)
    your_bonds = [
        {"BOND_CD": "XS2233188353", "CLOSING PRICE": 99.529, "WEIGHTING": 4.87, "NAME": "QNBK 1 5/8 09/22/25"},
        {"BOND_CD": "US279158AJ82", "CLOSING PRICE": 70.804, "WEIGHTING": 2.97, "NAME": "ECOPET 5 7/8 05/28/45"},
        {"BOND_CD": "US912810TJ79", "CLOSING PRICE": 70.53125, "WEIGHTING": 0.99, "NAME": "T 3 08/15/52"},
        {"BOND_CD": "US71654QDE98", "CLOSING PRICE": 91.655, "WEIGHTING": 1.28, "NAME": "PEMEX 5.95 01/28/31"},
        {"BOND_CD": "XS2249741674", "CLOSING PRICE": 78.43, "WEIGHTING": 3.84, "NAME": "ADGLXY 3 1/4 09/30/40"}
    ]
    
    print("🌸 Testing Your Portfolio Bonds Locally")
    print("=" * 50)
    
    try:
        # Test individual bonds
        from bond_master_hierarchy_enhanced import calculate_bond_master
        
        bonds_db = "bonds_data.db"
        validated_db = "validated_quantlib_bonds.db"
        bloomberg_db = "bloomberg_index.db"
        
        print(f"📂 Database files:")
        print(f"   bonds_data.db: {'✅' if os.path.exists(bonds_db) else '❌'}")
        print(f"   validated_quantlib_bonds.db: {'✅' if os.path.exists(validated_db) else '❌'}")
        print(f"   bloomberg_index.db: {'✅' if os.path.exists(bloomberg_db) else '❌'}")
        
        print(f"\n🔍 Testing individual bonds:")
        successful_bonds = []
        
        for i, bond in enumerate(your_bonds[:3]):  # Test first 3 bonds
            print(f"   {i+1}. {bond['BOND_CD']} ({bond['NAME'][:20]}...)")
            
            try:
                result = calculate_bond_master(
                    bond["BOND_CD"], 
                    bond["CLOSING PRICE"], 
                    bonds_db, 
                    validated_db, 
                    bloomberg_db
                )
                
                if "error" not in result:
                    print(f"      ✅ Yield: {result.get('yield', 'N/A')}%, Duration: {result.get('duration', 'N/A')}")
                    successful_bonds.append(result)
                else:
                    print(f"      ❌ Error: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"      ❌ Exception: {str(e)}")
        
        print(f"\n📊 Results Summary:")
        print(f"   Successful calculations: {len(successful_bonds)}/{len(your_bonds[:3])}")
        
        if successful_bonds:
            avg_yield = sum(b.get('yield', 0) for b in successful_bonds) / len(successful_bonds)
            avg_duration = sum(b.get('duration', 0) for b in successful_bonds) / len(successful_bonds)
            print(f"   Average yield: {avg_yield:.2f}%")
            print(f"   Average duration: {avg_duration:.2f}")
        
        # Test portfolio function
        print(f"\n📈 Testing portfolio function:")
        try:
            from google_analysis10 import process_bond_portfolio
            
            portfolio_data = {"data": []}
            for bond in your_bonds[:3]:
                portfolio_data["data"].append({
                    "BOND_CD": bond["BOND_CD"],
                    "CLOSING PRICE": bond["CLOSING PRICE"], 
                    "WEIGHTING": bond["WEIGHTING"]
                })
            
            portfolio_results = process_bond_portfolio(portfolio_data, bonds_db, validated_db, bloomberg_db)
            
            if isinstance(portfolio_results, list):
                portfolio_successful = [b for b in portfolio_results if 'error' not in b]
                print(f"   ✅ Portfolio processed: {len(portfolio_successful)}/{len(portfolio_results)} bonds successful")
                
                if portfolio_successful:
                    total_weight = sum(b.get('weightings', 0) for b in portfolio_successful)
                    if total_weight > 0:
                        weighted_yield = sum(b.get('yield', 0) * b.get('weightings', 0) for b in portfolio_successful) / total_weight
                        weighted_duration = sum(b.get('duration', 0) * b.get('weightings', 0) for b in portfolio_successful) / total_weight
                        print(f"   📊 Portfolio yield: {weighted_yield:.2f}%")
                        print(f"   📊 Portfolio duration: {weighted_duration:.2f}")
            else:
                print(f"   ❌ Portfolio error: {portfolio_results}")
                
        except Exception as e:
            print(f"   ❌ Portfolio function error: {str(e)}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the google_analysis10 directory")
    except Exception as e:
        print(f"❌ General error: {e}")

if __name__ == "__main__":
    quick_test()
