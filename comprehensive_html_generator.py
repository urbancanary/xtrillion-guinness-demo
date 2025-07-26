#!/usr/bin/env python3
"""
Comprehensive Multi-Metric HTML Report Generator - Google Analysis 10
====================================================================

Creates a single comprehensive HTML report showing ALL metrics for all 25 bonds:
- Yield to Maturity (with Bloomberg comparison)
- Modified Duration (with Bloomberg comparison where available)
- Treasury Spread (with Bloomberg comparison where available)  
- Accrued Interest
- Additional metrics (conventions, frequencies, etc.)

Professional institutional-grade styling with clear metric separation.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class ComprehensiveHTMLReportGenerator:
    """Generate comprehensive multi-metric HTML reports"""
    
    def __init__(self, results_data: Dict[str, Any]):
        self.results_data = results_data
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def generate_html_report(self, output_filename: Optional[str] = None) -> str:
        """Generate comprehensive HTML report with all metrics"""
        
        if output_filename is None:
            output_filename = f"comprehensive_multi_metric_report_{self.timestamp}.html"
        
        html_content = self._build_complete_html()
        
        # Write HTML file
        filepath = os.path.join(os.getcwd(), output_filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📊 Comprehensive HTML report generated: {filepath}")
        return filepath
    
    def _build_complete_html(self) -> str:
        """Build the complete HTML document"""
        
        metadata = self.results_data.get('test_metadata', {})
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Comprehensive Bond Analytics Report - Google Analysis 10</title>
    {self._get_css_styles()}
</head>
<body>
    <div class="container">
        {self._generate_header(metadata)}
        {self._generate_executive_summary(metadata)}
        {self._generate_yield_section()}
        {self._generate_duration_section()}
        {self._generate_spread_section()}
        {self._generate_accrued_section()}
        {self._generate_conventions_section()}
        {self._generate_footer(metadata)}
    </div>
</body>
</html>"""
        
        return html
    
    def _get_css_styles(self) -> str:
        """Professional institutional CSS styles"""
        return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin: -30px -30px 30px -30px;
        }
        
        .header h1 {
            font-size: 2.4em;
            margin-bottom: 15px;
            font-weight: 700;
        }
        
        .subtitle {
            font-size: 1.2em;
            opacity: 0.95;
        }
        
        .executive-summary {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            border: 3px solid #28a745;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        }
        
        .summary-title {
            color: #155724;
            font-size: 1.6em;
            font-weight: 700;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: 700;
            margin-bottom: 5px;
            color: #1e3c72;
        }
        
        .stat-label {
            color: #6c757d;
            font-weight: 600;
        }
        
        .metric-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin: 30px 0;
        }
        
        .metric-title {
            color: #2c3e50;
            font-size: 1.8em;
            font-weight: 700;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 3px solid #1e3c72;
            padding-bottom: 10px;
        }
        
        .metric-description {
            color: #6c757d;
            text-align: center;
            margin-bottom: 25px;
            font-size: 1.1em;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        
        th {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 15px 10px;
            text-align: center;
            font-weight: 600;
            font-size: 0.95em;
        }
        
        td {
            padding: 12px 10px;
            text-align: center;
            border-bottom: 1px solid #eee;
            font-size: 0.9em;
        }
        
        .bond-name {
            text-align: left !important;
            font-weight: 600;
            color: #2c3e50;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .isin {
            font-family: 'Courier New', monospace;
            font-weight: 600;
            color: #495057;
            font-size: 0.85em;
        }
        
        .excellent {
            background: #d4edda !important;
            color: #155724;
            font-weight: 600;
        }
        
        .good {
            background: #d1ecf1 !important;
            color: #0c5460;
            font-weight: 600;
        }
        
        .fair {
            background: #fff3cd !important;
            color: #856404;
            font-weight: 600;
        }
        
        .poor {
            background: #f8d7da !important;
            color: #721c24;
            font-weight: 600;
        }
        
        .no-data {
            color: #6c757d;
            font-style: italic;
        }
        
        .treasury-highlight {
            background: #e3f2fd !important;
            border-left: 4px solid #2196f3 !important;
        }
        
        .treasury-highlight .bond-name {
            color: #1565c0 !important;
            font-weight: 700 !important;
        }
        
        .treasury-highlight .isin {
            color: #1565c0 !important;
            font-weight: 700 !important;
        }
        
        .methodology {
            background: #e3f2fd;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .methodology h3 {
            color: #1565c0;
            margin-bottom: 10px;
        }
        
        .footer {
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .metric-separator {
            height: 3px;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            margin: 40px 0;
            border-radius: 5px;
        }
        
        .bloomberg-column {
            background: #fff3cd !important;
        }
        
        .calculated-column {
            background: #e8f5e8 !important;
        }
        
        .difference-column {
            background: #f8f9fa !important;
        }
    </style>"""
    
    def _generate_header(self, metadata: Dict[str, Any]) -> str:
        """Generate HTML header section"""
        settlement_date = metadata.get('settlement_date', 'N/A')
        timestamp = metadata.get('completed_timestamp', 'N/A')
        
        return f"""
        <div class="header">
            <h1>📊 Comprehensive Bond Analytics Report</h1>
            <div class="subtitle">
                Google Analysis 10 - Multi-Metric Analysis<br>
                Settlement: {settlement_date} | Generated: {timestamp}
            </div>
        </div>"""
    
    def _generate_executive_summary(self, metadata: Dict[str, Any]) -> str:
        """Generate executive summary section"""
        total_bonds = metadata.get('total_bonds', 0)
        successful_tests = metadata.get('successful_tests', 0)
        success_rate = metadata.get('success_rate', 0)
        
        # Calculate Bloomberg comparison stats
        yield_comparisons = len([r for r in self.results_data.get('yield_results', []) 
                               if r.get('bloomberg') is not None and r.get('calculated') is not None])
        
        duration_comparisons = len([r for r in self.results_data.get('duration_results', [])
                                  if r.get('bloomberg') is not None and r.get('calculated') is not None])
        
        spread_comparisons = len([r for r in self.results_data.get('spread_results', [])
                                if r.get('bloomberg') is not None and r.get('calculated') is not None])
        
        return f"""
        <div class="executive-summary">
            <div class="summary-title">📈 Executive Summary</div>
            <div class="summary-stats">
                <div class="stat-card">
                    <div class="stat-number">{total_bonds}</div>
                    <div class="stat-label">Total Bonds</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{successful_tests}</div>
                    <div class="stat-label">Successful Calculations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{success_rate:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{yield_comparisons}</div>
                    <div class="stat-label">Yield vs Bloomberg</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{duration_comparisons}</div>
                    <div class="stat-label">Duration vs Bloomberg</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{spread_comparisons}</div>
                    <div class="stat-label">Spread vs Bloomberg</div>
                </div>
            </div>
        </div>"""
    
    def _generate_yield_section(self) -> str:
        """Generate yield analysis section"""
        yield_results = self.results_data.get('yield_results', [])
        
        table_rows = ""
        for result in yield_results:
            # Determine row styling
            row_class = ""
            if result.get('isin') == 'US912810TJ79':  # Treasury
                row_class = 'treasury-highlight'
            
            # Format values
            calculated = f"{result.get('calculated', 0):.3f}%" if result.get('calculated') else "N/A"
            bloomberg = f"{result.get('bloomberg', 0):.3f}%" if result.get('bloomberg') else "N/A"
            difference = f"{result.get('difference_bps', 0):.1f}" if result.get('difference_bps') else "N/A"
            accuracy = result.get('accuracy_rating', 'N/A')
            
            # Apply accuracy styling to difference cell
            diff_class = ""
            if 'EXCELLENT' in accuracy:
                diff_class = 'excellent'
            elif 'GOOD' in accuracy:
                diff_class = 'good'
            elif 'FAIR' in accuracy:
                diff_class = 'fair'
            elif 'POOR' in accuracy:
                diff_class = 'poor'
            
            table_rows += f"""
                <tr class="{row_class}">
                    <td>{result.get('bond_num', '')}</td>
                    <td class="isin">{result.get('isin', '')}</td>
                    <td class="bond-name">{result.get('description', '')}</td>
                    <td class="bloomberg-column">{bloomberg}</td>
                    <td class="calculated-column">{calculated}</td>
                    <td class="difference-column {diff_class}">{difference}</td>
                    <td class="{diff_class}">{accuracy}</td>
                </tr>"""
        
        return f"""
        <div class="metric-section">
            <div class="metric-title">💰 Yield to Maturity Analysis</div>
            <div class="metric-description">
                Comparison of calculated yields vs Bloomberg terminal baselines (where available)
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>ISIN</th>
                        <th>Bond Description</th>
                        <th>Bloomberg<br>Yield (%)</th>
                        <th>Calculated<br>Yield (%)</th>
                        <th>Difference<br>(bps)</th>
                        <th>Accuracy</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        
        <div class="metric-separator"></div>"""
    
    def _generate_duration_section(self) -> str:
        """Generate duration analysis section"""
        duration_results = self.results_data.get('duration_results', [])
        
        table_rows = ""
        for result in duration_results:
            # Determine row styling
            row_class = ""
            if result.get('isin') == 'US912810TJ79':  # Treasury
                row_class = 'treasury-highlight'
            
            # Format values
            calculated = f"{result.get('calculated', 0):.2f}" if result.get('calculated') else "N/A"
            bloomberg = f"{result.get('bloomberg', 0):.2f}" if result.get('bloomberg') else "N/A"
            difference = f"{result.get('difference_years', 0):.3f}" if result.get('difference_years') else "N/A"
            accuracy = result.get('accuracy_rating', 'N/A')
            
            # Apply accuracy styling to difference cell
            diff_class = ""
            if 'EXCELLENT' in accuracy:
                diff_class = 'excellent'
            elif 'GOOD' in accuracy:
                diff_class = 'good'
            elif 'FAIR' in accuracy:
                diff_class = 'fair'
            elif 'POOR' in accuracy:
                diff_class = 'poor'
            
            table_rows += f"""
                <tr class="{row_class}">
                    <td>{result.get('bond_num', '')}</td>
                    <td class="isin">{result.get('isin', '')}</td>
                    <td class="bond-name">{result.get('description', '')}</td>
                    <td class="bloomberg-column">{bloomberg}</td>
                    <td class="calculated-column">{calculated}</td>
                    <td class="difference-column {diff_class}">{difference}</td>
                    <td class="{diff_class}">{accuracy}</td>
                </tr>"""
        
        return f"""
        <div class="metric-section">
            <div class="metric-title">⏱️ Modified Duration Analysis</div>
            <div class="metric-description">
                Comparison of calculated modified duration vs Bloomberg baselines (where available)
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>ISIN</th>
                        <th>Bond Description</th>
                        <th>Bloomberg<br>Duration (years)</th>
                        <th>Calculated<br>Duration (years)</th>
                        <th>Difference<br>(years)</th>
                        <th>Accuracy</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        
        <div class="metric-separator"></div>"""
    
    def _generate_spread_section(self) -> str:
        """Generate spread analysis section"""
        spread_results = self.results_data.get('spread_results', [])
        
        table_rows = ""
        for result in spread_results:
            # Determine row styling
            row_class = ""
            if result.get('isin') == 'US912810TJ79':  # Treasury
                row_class = 'treasury-highlight'
            
            # Format values
            calculated = f"{result.get('calculated', 0):.1f}" if result.get('calculated') else "N/A"
            bloomberg = f"{result.get('bloomberg', 0):.0f}" if result.get('bloomberg') else "N/A"
            difference = f"{result.get('difference_bps', 0):.1f}" if result.get('difference_bps') else "N/A"
            accuracy = result.get('accuracy_rating', 'N/A')
            
            # Apply accuracy styling to difference cell
            diff_class = ""
            if 'EXCELLENT' in accuracy:
                diff_class = 'excellent'
            elif 'GOOD' in accuracy:
                diff_class = 'good'
            elif 'FAIR' in accuracy:
                diff_class = 'fair'
            elif 'POOR' in accuracy:
                diff_class = 'poor'
            
            table_rows += f"""
                <tr class="{row_class}">
                    <td>{result.get('bond_num', '')}</td>
                    <td class="isin">{result.get('isin', '')}</td>
                    <td class="bond-name">{result.get('description', '')}</td>
                    <td class="bloomberg-column">{bloomberg}</td>
                    <td class="calculated-column">{calculated}</td>
                    <td class="difference-column {diff_class}">{difference}</td>
                    <td class="{diff_class}">{accuracy}</td>
                </tr>"""
        
        return f"""
        <div class="metric-section">
            <div class="metric-title">📈 Treasury Spread Analysis</div>
            <div class="metric-description">
                Comparison of calculated treasury spreads vs Bloomberg baselines (where available)
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>ISIN</th>
                        <th>Bond Description</th>
                        <th>Bloomberg<br>Spread (bps)</th>
                        <th>Calculated<br>Spread (bps)</th>
                        <th>Difference<br>(bps)</th>
                        <th>Accuracy</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        
        <div class="metric-separator"></div>"""
    
    def _generate_accrued_section(self) -> str:
        """Generate accrued interest section"""
        accrued_results = self.results_data.get('accrued_results', [])
        
        table_rows = ""
        for result in accrued_results:
            # Determine row styling
            row_class = ""
            if result.get('isin') == 'US912810TJ79':  # Treasury
                row_class = 'treasury-highlight'
            
            # Format values
            calculated = f"${result.get('calculated', 0):.2f}" if result.get('calculated') else "N/A"
            price = f"${result.get('price', 0):.2f}" if result.get('price') else "N/A"
            
            table_rows += f"""
                <tr class="{row_class}">
                    <td>{result.get('bond_num', '')}</td>
                    <td class="isin">{result.get('isin', '')}</td>
                    <td class="bond-name">{result.get('description', '')}</td>
                    <td>{price}</td>
                    <td class="calculated-column">{calculated}</td>
                </tr>"""
        
        return f"""
        <div class="metric-section">
            <div class="metric-title">💵 Accrued Interest Analysis</div>
            <div class="metric-description">
                Calculated accrued interest for settlement date (per $100 face value)
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>ISIN</th>
                        <th>Bond Description</th>
                        <th>Clean Price</th>
                        <th>Accrued Interest</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        
        <div class="metric-separator"></div>"""
    
    def _generate_conventions_section(self) -> str:
        """Generate conventions and additional metrics section"""
        additional_metrics = self.results_data.get('additional_metrics', [])
        
        table_rows = ""
        for result in additional_metrics:
            # Determine row styling
            row_class = ""
            if result.get('isin') == 'US912810TJ79':  # Treasury
                row_class = 'treasury-highlight'
            
            # Format values
            frequency = result.get('payment_frequency', 'N/A')
            day_count = str(result.get('day_count', 'N/A'))[:20] + "..." if len(str(result.get('day_count', 'N/A'))) > 20 else str(result.get('day_count', 'N/A'))
            calendar = str(result.get('calendar', 'N/A'))[:15] + "..." if len(str(result.get('calendar', 'N/A'))) > 15 else str(result.get('calendar', 'N/A'))
            is_treasury = "✅ Yes" if result.get('is_treasury') else "❌ No"
            
            table_rows += f"""
                <tr class="{row_class}">
                    <td>{result.get('bond_num', '')}</td>
                    <td class="isin">{result.get('isin', '')}</td>
                    <td class="bond-name">{result.get('description', '')}</td>
                    <td>{frequency}</td>
                    <td>{day_count}</td>
                    <td>{calendar}</td>
                    <td>{is_treasury}</td>
                </tr>"""
        
        return f"""
        <div class="metric-section">
            <div class="metric-title">🔧 Bond Conventions & Technical Details</div>
            <div class="metric-description">
                Technical conventions used in bond calculations (QuantLib parameters)
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>ISIN</th>
                        <th>Bond Description</th>
                        <th>Payment<br>Frequency</th>
                        <th>Day Count<br>Convention</th>
                        <th>Calendar</th>
                        <th>Treasury<br>Bond</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>"""
    
    def _generate_footer(self, metadata: Dict[str, Any]) -> str:
        """Generate report footer"""
        timestamp = metadata.get('completed_timestamp', 'N/A')
        settlement_date = metadata.get('settlement_date', 'N/A')
        
        return f"""
        <div class="methodology">
            <h3>🔧 Technical Implementation</h3>
            <p><strong>Calculation Engine:</strong> QuantLib Professional Implementation</p>
            <p><strong>Function:</strong> calculate_bond_master (ISIN hierarchy + parse hierarchy)</p>
            <p><strong>Settlement:</strong> {settlement_date} (institutional prior month end)</p>
            <p><strong>Conventions:</strong> Bloomberg-compatible day count and calendar settings</p>
        </div>
        
        <div class="footer">
            📊 Comprehensive Multi-Metric Bond Analytics Report<br>
            🕒 Generated: {timestamp}<br>
            🏛️ Google Analysis 10 - Professional Bond Calculation Engine<br>
            💎 Institutional-grade accuracy with Bloomberg validation
        </div>"""


def generate_html_from_json(json_filepath: str, output_filename: Optional[str] = None) -> str:
    """Generate HTML report from JSON results file"""
    
    print(f"📊 Loading results from: {json_filepath}")
    
    with open(json_filepath, 'r') as f:
        results_data = json.load(f)
    
    # Create HTML generator
    generator = ComprehensiveHTMLReportGenerator(results_data)
    
    # Generate HTML report
    html_filepath = generator.generate_html_report(output_filename)
    
    return html_filepath


def main():
    """Main function for testing HTML generation"""
    print("🎨 Comprehensive Multi-Metric HTML Report Generator")
    print("📋 This module generates HTML reports from JSON test results")
    print("💡 Usage: Run comprehensive_multi_metric_tester.py first to generate JSON data")
    

if __name__ == "__main__":
    main()
