#!/usr/bin/env python3
"""
🔍 Google Analysis 10 - Database Inspector
Comprehensive inspection of all bond databases to understand ISIN coverage
"""

import sqlite3
import os
import pandas as pd
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path

class DatabaseInspector:
    """Inspect all Google Analysis 10 databases for bond coverage"""
    
    def __init__(self, base_path: str = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"):
        self.base_path = Path(base_path)
        self.databases = {
            'bonds_data': self.base_path / 'bonds_data.db',
            'bloomberg_index': self.base_path / 'bloomberg_index.db', 
            'bloomberg_index_ticker': self.base_path / 'bloomberg_index_ticker.db',
            'portfolio_database': self.base_path / 'portfolio_database.db',
            'validated_quantlib_bonds': self.base_path / 'validated_quantlib_bonds.db',
            'tsys_enhanced': self.base_path / 'tsys_enhanced.db'
        }
        
        # Bloomberg baseline test bonds (from API spec)
        self.bloomberg_test_bonds = [
            {"ISIN": "US912810TJ79", "PX_MID": 71.66, "Name": "US TREASURY N/B, 3%, 15-Aug-2052"},
            {"ISIN": "XS2249741674", "PX_MID": 77.88, "Name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
            {"ISIN": "XS1709535097", "PX_MID": 89.40, "Name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"},
            {"ISIN": "XS1982113463", "PX_MID": 87.14, "Name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"},
            {"ISIN": "USP37466AS18", "PX_MID": 80.39, "Name": "EMPRESA METRO, 4.7%, 07-May-2050"},
            {"ISIN": "USP3143NAH72", "PX_MID": 101.63, "Name": "CODELCO INC, 6.15%, 24-Oct-2036"},
            {"ISIN": "USP30179BR86", "PX_MID": 86.42, "Name": "COMISION FEDERAL, 6.264%, 15-Feb-2052"},
            {"ISIN": "US195325DX04", "PX_MID": 52.71, "Name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061"},
            {"ISIN": "US279158AJ82", "PX_MID": 69.31, "Name": "ECOPETROL SA, 5.875%, 28-May-2045"},
            {"ISIN": "USP37110AM89", "PX_MID": 76.24, "Name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047"},
            {"ISIN": "XS2542166231", "PX_MID": 103.03, "Name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038"},
            {"ISIN": "XS2167193015", "PX_MID": 64.50, "Name": "STATE OF ISRAEL, 3.8%, 13-May-2060"},
            {"ISIN": "XS1508675508", "PX_MID": 82.42, "Name": "SAUDI INT BOND, 4.5%, 26-Oct-2046"},
            {"ISIN": "XS1807299331", "PX_MID": 92.21, "Name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048"},
            {"ISIN": "US91086QAZ19", "PX_MID": 78.00, "Name": "UNITED MEXICAN, 5.75%, 12-Oct-2110"},
            {"ISIN": "USP6629MAD40", "PX_MID": 82.57, "Name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047"},
            {"ISIN": "US698299BL70", "PX_MID": 56.60, "Name": "PANAMA, 3.87%, 23-Jul-2060"},
            {"ISIN": "US71654QDF63", "PX_MID": 71.42, "Name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060"},
            {"ISIN": "US71654QDE98", "PX_MID": 89.55, "Name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031"},
            {"ISIN": "XS2585988145", "PX_MID": 85.54, "Name": "GACI FIRST INVST, 5.125%, 14-Feb-2053"},
            {"ISIN": "XS1959337749", "PX_MID": 89.97, "Name": "QATAR STATE OF, 4.817%, 14-Mar-2049"},
            {"ISIN": "XS2233188353", "PX_MID": 99.23, "Name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025"},
            {"ISIN": "XS2359548935", "PX_MID": 73.79, "Name": "QATAR ENERGY, 3.125%, 12-Jul-2041"},
            {"ISIN": "XS0911024635", "PX_MID": 93.29, "Name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043"},
            {"ISIN": "USP0R80BAG79", "PX_MID": 97.26, "Name": "SITIOS, 5.375%, 04-Apr-2032"}
        ]
    
    def inspect_database_file(self, db_name: str, db_path: Path) -> Dict:
        """Inspect a single database file"""
        inspection_result = {
            'database': db_name,
            'path': str(db_path),
            'exists': False,
            'accessible': False,
            'size_mb': 0,
            'tables': [],
            'total_records': 0,
            'isin_columns': [],
            'sample_isins': [],
            'bloomberg_test_coverage': {},
            'error': None
        }
        
        if not db_path.exists():
            inspection_result['error'] = 'Database file does not exist'
            return inspection_result
        
        inspection_result['exists'] = True
        inspection_result['size_mb'] = round(db_path.stat().st_size / (1024 * 1024), 2)
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            inspection_result['accessible'] = True
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            inspection_result['tables'] = tables
            
            # For each table, check for ISIN-like columns and count records
            total_records = 0
            isin_columns = []
            sample_isins = []
            bloomberg_coverage = {}
            
            for table in tables:
                try:
                    # Get table info
                    cursor.execute(f"PRAGMA table_info({table});")
                    columns = [(col[1], col[2]) for col in cursor.fetchall()]
                    
                    # Count records
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    record_count = cursor.fetchone()[0]
                    total_records += record_count
                    
                    # Look for ISIN-like columns
                    isin_like_columns = [col[0] for col in columns if 
                                       'isin' in col[0].lower() or 
                                       'id' in col[0].lower() or
                                       'code' in col[0].lower() or
                                       'identifier' in col[0].lower()]
                    
                    if isin_like_columns:
                        isin_columns.extend([(table, col) for col in isin_like_columns])
                        
                        # Get sample ISINs from this table
                        for col in isin_like_columns:
                            cursor.execute(f"SELECT DISTINCT {col} FROM {table} WHERE {col} IS NOT NULL LIMIT 5;")
                            samples = [row[0] for row in cursor.fetchall() if row[0]]
                            sample_isins.extend([(table, col, sample) for sample in samples])
                        
                        # Check Bloomberg test bond coverage
                        for bond in self.bloomberg_test_bonds:
                            isin = bond['ISIN']
                            for col in isin_like_columns:
                                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} = ?;", (isin,))
                                count = cursor.fetchone()[0]
                                if count > 0:
                                    if isin not in bloomberg_coverage:
                                        bloomberg_coverage[isin] = []
                                    bloomberg_coverage[isin].append(f"{table}.{col}")
                
                except Exception as e:
                    print(f"Error inspecting table {table} in {db_name}: {e}")
                    continue
            
            inspection_result['total_records'] = total_records
            inspection_result['isin_columns'] = isin_columns
            inspection_result['sample_isins'] = sample_isins[:20]  # Limit to first 20
            inspection_result['bloomberg_test_coverage'] = bloomberg_coverage
            
            conn.close()
            
        except Exception as e:
            inspection_result['error'] = str(e)
        
        return inspection_result
    
    def inspect_all_databases(self) -> Dict:
        """Inspect all databases and compile comprehensive report"""
        print("🔍 Google Analysis 10 - Database Inspector")
        print("=" * 80)
        print(f"Base path: {self.base_path}")
        print(f"Inspecting {len(self.databases)} databases...")
        print()
        
        inspection_results = {}
        total_databases = 0
        accessible_databases = 0
        total_size_mb = 0
        total_records = 0
        
        for db_name, db_path in self.databases.items():
            print(f"📊 Inspecting {db_name}...")
            result = self.inspect_database_file(db_name, db_path)
            inspection_results[db_name] = result
            
            total_databases += 1
            if result['accessible']:
                accessible_databases += 1
                total_size_mb += result['size_mb']
                total_records += result['total_records']
        
        # Compile Bloomberg test coverage summary
        bloomberg_coverage_summary = {}
        for db_name, result in inspection_results.items():
            for isin, locations in result['bloomberg_test_coverage'].items():
                if isin not in bloomberg_coverage_summary:
                    bloomberg_coverage_summary[isin] = []
                bloomberg_coverage_summary[isin].extend(locations)
        
        summary = {
            'inspection_timestamp': pd.Timestamp.now().isoformat(),
            'total_databases': total_databases,
            'accessible_databases': accessible_databases,
            'total_size_mb': total_size_mb,
            'total_records': total_records,
            'database_results': inspection_results,
            'bloomberg_test_coverage_summary': bloomberg_coverage_summary,
            'bloomberg_test_bonds_found': len(bloomberg_coverage_summary),
            'bloomberg_test_bonds_total': len(self.bloomberg_test_bonds)
        }
        
        return summary
    
    def print_detailed_report(self, inspection_summary: Dict):
        """Print detailed inspection report"""
        print("\n" + "=" * 80)
        print("📊 DATABASE INSPECTION DETAILED REPORT")
        print("=" * 80)
        
        # Overall summary
        print(f"🗄️  Total Databases: {inspection_summary['total_databases']}")
        print(f"✅ Accessible: {inspection_summary['accessible_databases']}")
        print(f"💾 Total Size: {inspection_summary['total_size_mb']:.1f} MB")
        print(f"📊 Total Records: {inspection_summary['total_records']:,}")
        
        # Database-by-database breakdown
        print(f"\n📋 DATABASE BREAKDOWN:")
        for db_name, result in inspection_summary['database_results'].items():
            print(f"\n🗄️  {db_name.upper()}:")
            print(f"   Path: {result['path']}")
            print(f"   Exists: {'✅' if result['exists'] else '❌'}")
            print(f"   Accessible: {'✅' if result['accessible'] else '❌'}")
            
            if result['accessible']:
                print(f"   Size: {result['size_mb']} MB")
                print(f"   Tables: {len(result['tables'])}")
                print(f"   Total Records: {result['total_records']:,}")
                print(f"   ISIN Columns: {len(result['isin_columns'])}")
                
                if result['tables']:
                    print(f"   Table Names: {', '.join(result['tables'])}")
                
                if result['isin_columns']:
                    print(f"   ISIN-like Columns:")
                    for table, col in result['isin_columns']:
                        print(f"     - {table}.{col}")
                
                if result['sample_isins']:
                    print(f"   Sample ISINs:")
                    for table, col, isin in result['sample_isins'][:5]:
                        print(f"     - {table}.{col}: {isin}")
                
                bloomberg_found = len(result['bloomberg_test_coverage'])
                if bloomberg_found > 0:
                    print(f"   📈 Bloomberg Test Bonds Found: {bloomberg_found}/25")
            
            if result['error']:
                print(f"   ❌ Error: {result['error']}")
        
        # Bloomberg test coverage summary
        print(f"\n📈 BLOOMBERG TEST COVERAGE SUMMARY:")
        print(f"Bonds found in databases: {inspection_summary['bloomberg_test_bonds_found']}/25")
        
        found_bonds = inspection_summary['bloomberg_test_coverage_summary']
        missing_bonds = []
        
        for bond in self.bloomberg_test_bonds:
            isin = bond['ISIN']
            if isin in found_bonds:
                locations = found_bonds[isin]
                print(f"✅ {isin}: Found in {len(locations)} location(s)")
                for location in locations:
                    print(f"   - {location}")
            else:
                missing_bonds.append(bond)
                print(f"❌ {isin}: NOT FOUND")
        
        if missing_bonds:
            print(f"\n⚠️  MISSING BLOOMBERG TEST BONDS ({len(missing_bonds)}):")
            for bond in missing_bonds:
                print(f"   - {bond['ISIN']}: {bond['Name'][:50]}...")
        
        print(f"\n✅ COVERAGE RATE: {inspection_summary['bloomberg_test_bonds_found']}/25 = {inspection_summary['bloomberg_test_bonds_found']/25*100:.1f}%")
    
    def save_inspection_report(self, inspection_summary: Dict, filename: str = None):
        """Save inspection report to JSON file"""
        if not filename:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_inspection_{timestamp}.json"
        
        filepath = self.base_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(inspection_summary, f, indent=2, default=str)
        
        print(f"\n💾 Inspection report saved to: {filepath}")
        return filepath

def main():
    """Main inspection function"""
    # Create inspector
    inspector = DatabaseInspector()
    
    # Run comprehensive inspection
    inspection_summary = inspector.inspect_all_databases()
    
    # Print detailed report
    inspector.print_detailed_report(inspection_summary)
    
    # Save report
    report_file = inspector.save_inspection_report(inspection_summary)
    
    print(f"\n🎯 INSPECTION COMPLETE")
    print(f"📊 Total databases inspected: {inspection_summary['total_databases']}")
    print(f"📈 Bloomberg test coverage: {inspection_summary['bloomberg_test_bonds_found']}/25")
    print(f"💾 Report saved to: {report_file}")

if __name__ == "__main__":
    main()
