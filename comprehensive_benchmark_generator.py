#!/usr/bin/env python3
"""
6-Way Method Benchmark Generator vs Bloomberg
============================================

Creates comprehensive benchmark tables comparing all 6 calculation methods
against Bloomberg baseline data for the 25-bond portfolio.

Outputs:
1. Markdown tables for quick scanning
2. Excel files for detailed analysis
3. Summary statistics and accuracy metrics
4. Treasury fix validation results

Methods Tested:
1. Direct Local + ISIN (Database lookup)
2. Direct Local - ISIN (Parser fallback) 
3. Local API + ISIN
4. Local API - ISIN
5. Cloud API + ISIN (if available)
6. Cloud API - ISIN (if available)
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging

# Add project paths
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis10 import process_bonds_with_weightings
from bond_description_parser import SmartBondParser

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BenchmarkGenerator:
    """Generate comprehensive benchmark tables vs Bloomberg"""
    
    def __init__(self):
        self.db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db'
        self.validated_db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/validated_quantlib_bonds.db'
        self.settlement_date = '2025-06-30'
        
        # 25-bond test portfolio (from your documents)
        self.test_portfolio = [
            {'isin': 'US912810TJ79', 'price': 71.66, 'name': 'US TREASURY N/B, 3%, 15-Aug-2052'},
            {'isin': 'XS2249741674', 'price': 77.88, 'name': 'GALAXY PIPELINE, 3.25%, 30-Sep-2040'},
            {'isin': 'XS1709535097', 'price': 89.40, 'name': 'ABU DHABI CRUDE, 4.6%, 02-Nov-2047'},
            {'isin': 'XS1982113463', 'price': 87.14, 'name': 'SAUDI ARAB OIL, 4.25%, 16-Apr-2039'},
            {'isin': 'USP37466AS18', 'price': 80.39, 'name': 'EMPRESA METRO, 4.7%, 07-May-2050'},
            {'isin': 'USP3143NAH72', 'price': 101.63, 'name': 'CODELCO INC, 6.15%, 24-Oct-2036'},
            {'isin': 'USP30179BR86', 'price': 86.42, 'name': 'COMISION FEDERAL, 6.264%, 15-Feb-2052'},
            {'isin': 'US195325DX04', 'price': 52.71, 'name': 'COLOMBIA REP OF, 3.875%, 15-Feb-2061'},
            {'isin': 'US279158AJ82', 'price': 69.31, 'name': 'ECOPETROL SA, 5.875%, 28-May-2045'},
            {'isin': 'USP37110AM89', 'price': 76.24, 'name': 'EMPRESA NACIONAL, 4.5%, 14-Sep-2047'},
            {'isin': 'XS2542166231', 'price': 103.03, 'name': 'GREENSAIF PIPELI, 6.129%, 23-Feb-2038'},
            {'isin': 'XS2167193015', 'price': 64.50, 'name': 'STATE OF ISRAEL, 3.8%, 13-May-2060'},
            {'isin': 'XS1508675508', 'price': 82.42, 'name': 'SAUDI INT BOND, 4.5%, 26-Oct-2046'},
            {'isin': 'XS1807299331', 'price': 92.21, 'name': 'KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048'},
            {'isin': 'US91086QAZ19', 'price': 78.00, 'name': 'UNITED MEXICAN, 5.75%, 12-Oct-2110'},
            {'isin': 'USP6629MAD40', 'price': 82.57, 'name': 'MEXICO CITY ARPT, 5.5%, 31-Jul-2047'},
            {'isin': 'US698299BL70', 'price': 56.60, 'name': 'PANAMA, 3.87%, 23-Jul-2060'},
            {'isin': 'US71654QDF63', 'price': 71.42, 'name': 'PETROLEOS MEXICA, 6.95%, 28-Jan-2060'},
            {'isin': 'US71654QDE98', 'price': 89.55, 'name': 'PETROLEOS MEXICA, 5.95%, 28-Jan-2031'},
            {'isin': 'XS2585988145', 'price': 85.54, 'name': 'GACI FIRST INVST, 5.125%, 14-Feb-2053'},
            {'isin': 'XS1959337749', 'price': 89.97, 'name': 'QATAR STATE OF, 4.817%, 14-Mar-2049'},
            {'isin': 'XS2233188353', 'price': 99.23, 'name': 'QNB FINANCE LTD, 1.625%, 22-Sep-2025'},
            {'isin': 'XS2359548935', 'price': 73.79, 'name': 'QATAR ENERGY, 3.125%, 12-Jul-2041'},
            {'isin': 'XS0911024635', 'price': 93.29, 'name': 'SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043'},
            {'isin': 'USP0R80BAG79', 'price': 97.26, 'name': 'SITIOS, 5.375%, 04-Apr-2032'}
        ]
        
        # Bloomberg baseline data (from your 25-Bond Portfolio Analytics Table)
        self.bloomberg_baseline = {
            'US912810TJ79': {'yield': 4.89916, 'duration': 16.35658, 'spread': 39.91632},
            'XS2249741674': {'yield': 5.39556, 'duration': 11.22303, 'spread': 89.55584},
            'XS1709535097': {'yield': 5.42359, 'duration': 13.21138, 'spread': 92.35907},
            'XS1982113463': {'yield': 5.59944, 'duration': 9.93052, 'spread': 109.94388},
            'USP37466AS18': {'yield': 6.26618, 'duration': 13.18176, 'spread': 176.61783},
            'USP3143NAH72': {'yield': 5.94874, 'duration': 8.01689, 'spread': 144.87434},
            'USP30179BR86': {'yield': 7.44217, 'duration': 11.58710, 'spread': 294.21683},
            'US195325DX04': {'yield': 7.83636, 'duration': 12.97993, 'spread': 333.63631},
            'US279158AJ82': {'yield': 9.28195, 'duration': 9.80447, 'spread': 478.19491},
            'USP37110AM89': {'yield': 6.54274, 'duration': 12.38229, 'spread': 204.27423},
            'XS2542166231': {'yield': 5.78691, 'duration': 8.61427, 'spread': 128.69067},
            'XS2167193015': {'yield': 6.33756, 'duration': 15.26825, 'spread': 183.75586},
            'XS1508675508': {'yield': 5.96747, 'duration': 12.60204, 'spread': 146.74727},
            'XS1807299331': {'yield': 7.05978, 'duration': 11.44784, 'spread': 255.97846},
            'US91086QAZ19': {'yield': 7.37494, 'duration': 13.36798, 'spread': 287.49419},
            'USP6629MAD40': {'yield': 7.07038, 'duration': 11.37892, 'spread': 257.03820},
            'US698299BL70': {'yield': 7.32679, 'duration': 13.57604, 'spread': 282.67859},
            'US71654QDF63': {'yield': 9.87572, 'duration': 9.71461, 'spread': 537.57173},
            'US71654QDE98': {'yield': 8.32733, 'duration': 4.46458, 'spread': 382.73346},
            'XS2585988145': {'yield': 6.22763, 'duration': 13.33263, 'spread': 172.76259},
            'XS1959337749': {'yield': 5.58469, 'duration': 13.26146, 'spread': 108.46879},
            'XS2233188353': {'yield': 5.02106, 'duration': 0.22450, 'spread': 52.10619},
            'XS2359548935': {'yield': 5.62805, 'duration': 11.51499, 'spread': 112.80529},
            'XS0911024635': {'yield': 5.66298, 'duration': 11.23839, 'spread': 116.29823},
            'USP0R80BAG79': {'yield': 5.86969, 'duration': 5.51011, 'spread': 136.96853}
        }
    
    def run_method_1_direct_local_with_isin(self):
        """Method 1: Direct Local + ISIN (Database lookup)"""
        logger.info("Running Method 1: Direct Local + ISIN")
        
        portfolio_data = {
            "data": [
                {
                    "BOND_CD": bond['isin'],
                    "CLOSING PRICE": bond['price'],
                    "WEIGHTING": 100.0,
                    "Inventory Date": self.settlement_date.replace("-", "/")
                }
                for bond in self.test_portfolio
            ]
        }
        
        try:
            results = process_bonds_with_weightings(
                portfolio_data, 
                self.db_path, 
                validated_db_path=self.validated_db_path
            )
            return self.format_results(results, "Method_1_Direct_Local_ISIN")
        except Exception as e:
            logger.error(f"Method 1 failed: {e}")
            return pd.DataFrame()
    
    def run_method_2_direct_local_without_isin(self):
        """Method 2: Direct Local - ISIN (Parser fallback)"""
        logger.info("Running Method 2: Direct Local - ISIN")
        
        parser = SmartBondParser(self.db_path, self.validated_db_path)
        results = []
        
        for bond in self.test_portfolio:
            try:
                # Parse bond description
                parsed_bond = parser.parse_bond_description(bond['name'])
                
                if parsed_bond:
                    # Predict conventions
                    conventions = parser.predict_most_likely_conventions(parsed_bond)
                    
                    # Calculate metrics
                    calculation_result = parser.calculate_accrued_interest(
                        parsed_bond, 
                        conventions, 
                        settlement_date=self.settlement_date,
                        price=bond['price']
                    )
                    
                    if calculation_result.get('calculation_successful'):
                        results.append({
                            'isin': bond['isin'],
                            'yield': calculation_result.get('yield_to_maturity', 0),
                            'duration': calculation_result.get('duration', 0),
                            'spread': 0,  # Spread calculation may vary
                            'method': 'Method_2_Direct_Local_Parser'
                        })
                    else:
                        results.append({
                            'isin': bond['isin'],
                            'yield': 0,
                            'duration': 0,
                            'spread': 0,
                            'method': 'Method_2_Failed'
                        })
                else:
                    results.append({
                        'isin': bond['isin'],
                        'yield': 0,
                        'duration': 0,
                        'spread': 0,
                        'method': 'Method_2_Parse_Failed'
                    })
                    
            except Exception as e:
                logger.error(f"Method 2 failed for {bond['isin']}: {e}")
                results.append({
                    'isin': bond['isin'],
                    'yield': 0,
                    'duration': 0,
                    'spread': 0,
                    'method': 'Method_2_Error'
                })
        
        return pd.DataFrame(results)
    
    def run_method_3_local_api_with_isin(self):
        """Method 3: Local API + ISIN"""
        logger.info("Running Method 3: Local API + ISIN")
        # Placeholder - implement actual API calls
        return self.create_placeholder_results("Method_3_Local_API_ISIN")
    
    def run_method_4_local_api_without_isin(self):
        """Method 4: Local API - ISIN"""
        logger.info("Running Method 4: Local API - ISIN")
        # Placeholder - implement actual API calls
        return self.create_placeholder_results("Method_4_Local_API_Parser")
    
    def run_method_5_cloud_api_with_isin(self):
        """Method 5: Cloud API + ISIN"""
        logger.info("Running Method 5: Cloud API + ISIN")
        # Placeholder - implement actual API calls
        return self.create_placeholder_results("Method_5_Cloud_API_ISIN")
    
    def run_method_6_cloud_api_without_isin(self):
        """Method 6: Cloud API - ISIN"""
        logger.info("Running Method 6: Cloud API - ISIN")
        # Placeholder - implement actual API calls
        return self.create_placeholder_results("Method_6_Cloud_API_Parser")
    
    def create_placeholder_results(self, method_name):
        """Create placeholder results for API methods"""
        results = []
        for bond in self.test_portfolio:
            results.append({
                'isin': bond['isin'],
                'yield': 0,
                'duration': 0,
                'spread': 0,
                'method': f'{method_name}_NotImplemented'
            })
        return pd.DataFrame(results)
    
    def format_results(self, results_df, method_name):
        """Format results DataFrame for comparison"""
        if results_df.empty:
            return self.create_placeholder_results(method_name)
        
        formatted = []
        for _, row in results_df.iterrows():
            formatted.append({
                'isin': row.get('isin', ''),
                'yield': float(row.get('yield', 0)) if pd.notna(row.get('yield')) else 0,
                'duration': float(row.get('duration', 0)) if pd.notna(row.get('duration')) else 0,
                'spread': float(row.get('spread', 0)) if pd.notna(row.get('spread')) else 0,
                'method': method_name
            })
        
        return pd.DataFrame(formatted)
    
    def calculate_accuracy_metrics(self, results_df, method_name):
        """Calculate accuracy metrics vs Bloomberg baseline"""
        metrics = {
            'method': method_name,
            'total_bonds': len(results_df),
            'successful_calculations': 0,
            'yield_mae': 0,
            'duration_mae': 0,
            'yield_rmse': 0,
            'duration_rmse': 0,
            'within_1bp_yield': 0,
            'within_0_1yr_duration': 0
        }
        
        yield_errors = []
        duration_errors = []
        
        for _, row in results_df.iterrows():
            isin = row['isin']
            if isin in self.bloomberg_baseline:
                bloomberg = self.bloomberg_baseline[isin]
                
                if row['yield'] > 0 and row['duration'] > 0:
                    metrics['successful_calculations'] += 1
                    
                    # Calculate errors
                    yield_error = abs(row['yield'] - bloomberg['yield'])
                    duration_error = abs(row['duration'] - bloomberg['duration'])
                    
                    yield_errors.append(yield_error)
                    duration_errors.append(duration_error)
                    
                    # Count bonds within tolerance
                    if yield_error <= 0.01:  # 1 basis point
                        metrics['within_1bp_yield'] += 1
                    
                    if duration_error <= 0.1:  # 0.1 years
                        metrics['within_0_1yr_duration'] += 1
        
        if yield_errors:
            metrics['yield_mae'] = np.mean(yield_errors)
            metrics['yield_rmse'] = np.sqrt(np.mean([e**2 for e in yield_errors]))
        
        if duration_errors:
            metrics['duration_mae'] = np.mean(duration_errors)
            metrics['duration_rmse'] = np.sqrt(np.mean([e**2 for e in duration_errors]))
        
        return metrics
    
    def create_combined_comparison_table(self, all_results):
        """Create comprehensive comparison table"""
        combined_data = []
        
        for bond in self.test_portfolio:
            isin = bond['isin']
            bloomberg = self.bloomberg_baseline.get(isin, {'yield': 0, 'duration': 0, 'spread': 0})
            
            row = {
                'ISIN': isin,
                'Name': bond['name'][:40] + '...' if len(bond['name']) > 40 else bond['name'],
                'Price': bond['price'],
                'Bloomberg_Yield': bloomberg['yield'],
                'Bloomberg_Duration': bloomberg['duration'],
                'Bloomberg_Spread': bloomberg['spread']
            }
            
            # Add results from each method
            for method_results in all_results:
                method_name = method_results['method'].iloc[0] if not method_results.empty else 'Unknown'
                bond_result = method_results[method_results['isin'] == isin]
                
                if not bond_result.empty:
                    result = bond_result.iloc[0]
                    row[f'{method_name}_Yield'] = result['yield']
                    row[f'{method_name}_Duration'] = result['duration']
                    row[f'{method_name}_YieldDiff'] = abs(result['yield'] - bloomberg['yield']) if result['yield'] > 0 else 999
                    row[f'{method_name}_DurationDiff'] = abs(result['duration'] - bloomberg['duration']) if result['duration'] > 0 else 999
                else:
                    row[f'{method_name}_Yield'] = 0
                    row[f'{method_name}_Duration'] = 0
                    row[f'{method_name}_YieldDiff'] = 999
                    row[f'{method_name}_DurationDiff'] = 999
            
            combined_data.append(row)
        
        return pd.DataFrame(combined_data)
    
    def generate_markdown_tables(self, combined_df, accuracy_metrics):
        """Generate markdown tables for quick scanning"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        markdown = f"""# 6-Way Method Benchmark vs Bloomberg
Generated: {timestamp}
Settlement Date: {self.settlement_date}

## Executive Summary

**Treasury Fix Validation**: Method 1 vs Method 2 comparison for Treasury bonds
**Total Bonds Tested**: 25
**Bloomberg Baseline**: Professional QuantLib calculations with ActualActual(ISDA)

## 📊 Accuracy Summary Table

| Method | Success Rate | Yield MAE (%) | Duration MAE (yrs) | Within 1bp | Within 0.1yr |
|--------|--------------|---------------|-------------------|------------|--------------|
"""
        
        for metric in accuracy_metrics:
            success_rate = f"{metric['successful_calculations']}/{metric['total_bonds']}"
            markdown += f"| {metric['method']} | {success_rate} | {metric['yield_mae']:.4f} | {metric['duration_mae']:.4f} | {metric['within_1bp_yield']} | {metric['within_0_1yr_duration']} |\n"
        
        markdown += """
## 🎯 Treasury Bond Focus (Validation of Fix)

**Key Bond**: US912810TJ79 (US TREASURY N/B, 3%, 15-Aug-2052)
- **Bloomberg**: 4.89916% yield, 16.35658 years duration
- **Expected**: Both Method 1 and Method 2 should match closely after Treasury fix

"""
        
        # Treasury bond specific comparison
        treasury_isin = 'US912810TJ79'
        treasury_row = combined_df[combined_df['ISIN'] == treasury_isin]
        
        if not treasury_row.empty:
            row = treasury_row.iloc[0]
            markdown += f"""
### Treasury Bond Results:
- **Bloomberg**: {row['Bloomberg_Yield']:.5f}% yield, {row['Bloomberg_Duration']:.5f} years
- **Method 1**: {row.get('Method_1_Direct_Local_ISIN_Yield', 0):.5f}% yield, {row.get('Method_1_Direct_Local_ISIN_Duration', 0):.5f} years
- **Method 2**: {row.get('Method_2_Direct_Local_Parser_Yield', 0):.5f}% yield, {row.get('Method_2_Direct_Local_Parser_Duration', 0):.5f} years

### Method 1 vs Method 2 Differences:
- **Yield Difference**: {abs(row.get('Method_1_Direct_Local_ISIN_Yield', 0) - row.get('Method_2_Direct_Local_Parser_Yield', 0)):.5f}% ({abs(row.get('Method_1_Direct_Local_ISIN_Yield', 0) - row.get('Method_2_Direct_Local_Parser_Yield', 0))*100:.2f} bps)
- **Duration Difference**: {abs(row.get('Method_1_Direct_Local_ISIN_Duration', 0) - row.get('Method_2_Direct_Local_Parser_Duration', 0)):.5f} years

"""
        
        markdown += """
## 📋 Complete Results Table

| # | ISIN | Name | Bloomberg Yield | M1 Yield | M2 Yield | Bloomberg Duration | M1 Duration | M2 Duration |
|---|------|------|----------------|----------|----------|-------------------|-------------|-------------|
"""
        
        for i, (_, row) in enumerate(combined_df.iterrows(), 1):
            markdown += f"| {i} | {row['ISIN']} | {row['Name']} | {row['Bloomberg_Yield']:.3f} | {row.get('Method_1_Direct_Local_ISIN_Yield', 0):.3f} | {row.get('Method_2_Direct_Local_Parser_Yield', 0):.3f} | {row['Bloomberg_Duration']:.3f} | {row.get('Method_1_Direct_Local_ISIN_Duration', 0):.3f} | {row.get('Method_2_Direct_Local_Parser_Duration', 0):.3f} |\n"
        
        markdown += """
## 🔍 Error Analysis

### Yield Differences (vs Bloomberg)

| ISIN | Bloomberg | Method 1 | Method 2 | M1 Error (bps) | M2 Error (bps) |
|------|-----------|----------|----------|----------------|----------------|
"""
        
        for _, row in combined_df.iterrows():
            m1_error = row.get('Method_1_Direct_Local_ISIN_YieldDiff', 999) * 100
            m2_error = row.get('Method_2_Direct_Local_Parser_YieldDiff', 999) * 100
            markdown += f"| {row['ISIN']} | {row['Bloomberg_Yield']:.3f} | {row.get('Method_1_Direct_Local_ISIN_Yield', 0):.3f} | {row.get('Method_2_Direct_Local_Parser_Yield', 0):.3f} | {m1_error:.1f} | {m2_error:.1f} |\n"
        
        markdown += """
## 💡 Key Insights

1. **Treasury Fix Validation**: Methods 1 and 2 should now show identical results for Treasury bonds
2. **Best Performing Method**: Look for lowest MAE values
3. **Production Readiness**: Methods with >90% success rate and <1bp average error
4. **Implementation Priority**: Focus on methods with proven accuracy

## ⚠️ Notes

- **Method 3-6**: May show placeholder results if API endpoints not available
- **Spread Calculations**: May vary between methods due to different Treasury curve implementations
- **Settlement Date**: All calculations use {self.settlement_date} for consistency
"""
        
        return markdown
    
    def run_comprehensive_benchmark(self):
        """Run all 6 methods and generate benchmark tables"""
        print("🚀 STARTING 6-WAY COMPREHENSIVE BENCHMARK vs BLOOMBERG")
        print("=" * 80)
        
        # Run all methods
        method_results = [
            self.run_method_1_direct_local_with_isin(),
            self.run_method_2_direct_local_without_isin(),
            self.run_method_3_local_api_with_isin(),
            self.run_method_4_local_api_without_isin(),
            self.run_method_5_cloud_api_with_isin(),
            self.run_method_6_cloud_api_without_isin()
        ]
        
        # Calculate accuracy metrics
        accuracy_metrics = []
        for results in method_results:
            if not results.empty:
                method_name = results['method'].iloc[0]
                metrics = self.calculate_accuracy_metrics(results, method_name)
                accuracy_metrics.append(metrics)
        
        # Create combined comparison table
        combined_df = self.create_combined_comparison_table(method_results)
        
        # Generate markdown
        markdown_content = self.generate_markdown_tables(combined_df, accuracy_metrics)
        
        # Save files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save markdown
        markdown_file = f'/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/6way_benchmark_vs_bloomberg_{timestamp}.md'
        with open(markdown_file, 'w') as f:
            f.write(markdown_content)
        
        # Save Excel
        excel_file = f'/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/6way_benchmark_vs_bloomberg_{timestamp}.xlsx'
        
        try:
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                combined_df.to_excel(writer, sheet_name='Complete_Comparison', index=False)
                
                # Individual method sheets
                for results in method_results:
                    if not results.empty:
                        method_name = results['method'].iloc[0].replace('_', ' ')
                        results.to_excel(writer, sheet_name=method_name[:31], index=False)
                
                # Accuracy metrics sheet
                accuracy_df = pd.DataFrame(accuracy_metrics)
                accuracy_df.to_excel(writer, sheet_name='Accuracy_Metrics', index=False)
        except Exception as e:
            logger.error(f"Excel write failed: {e}")
            print(f"⚠️ Excel file creation failed: {e}")
        
        print(f"✅ Markdown report saved: {markdown_file}")
        print(f"✅ Excel report saved: {excel_file}")
        print("\n🎯 BENCHMARK COMPLETE!")
        
        return combined_df, accuracy_metrics, markdown_file, excel_file

if __name__ == "__main__":
    generator = BenchmarkGenerator()
    combined_df, accuracy_metrics, markdown_file, excel_file = generator.run_comprehensive_benchmark()
    
    print("\n📊 QUICK SUMMARY:")
    print("-" * 40)
    for metric in accuracy_metrics:
        print(f"{metric['method']}: {metric['successful_calculations']}/{metric['total_bonds']} success, "
              f"Yield MAE: {metric['yield_mae']:.4f}%, Duration MAE: {metric['duration_mae']:.4f}yr")
