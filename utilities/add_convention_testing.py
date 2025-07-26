#!/usr/bin/env python3
"""
🎯 ADD CONVENTION TESTING TO bb_quantlib_loop.py
This script adds the convention testing functionality from scattered files
"""

# Read the current bb_quantlib_loop.py content
with open('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9/bb_quantlib_loop.py', 'r') as f:
    content = f.read()

# Find the insertion point (before the command line interface)
insertion_point = content.find('# 🔄 ENHANCED COMMAND LINE INTERFACE with Loop Options')

if insertion_point == -1:
    print("❌ Could not find insertion point")
    exit(1)

# Convention testing code to insert
convention_code = '''
# 🎯 NEW: CONVENTION TESTING AND OPTIMIZATION

class ConventionTester:
    """
    🚀 CONVENTION TESTING FOR 12K+ BONDS
    
    Tests different QuantLib conventions to find optimal match rates
    Uses proper maturity_fixed column and performs actual calculations
    """
    
    def __init__(self, db_path: str = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9/bloomberg_index.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        
        # Settlement date
        self.settlement_date = ql.Date(18, 4, 2025)  # April 18, 2025
        ql.Settings.instance().evaluationDate = self.settlement_date
        
        # Convention options (optimized order)
        self.day_count_options = [
            ('Thirty360_BondBasis', ql.Thirty360(ql.Thirty360.BondBasis)),
            ('Thirty360_European', ql.Thirty360(ql.Thirty360.European)),
            ('Actual360', ql.Actual360()),
            ('ActualActual_ISDA', ql.ActualActual(ql.ActualActual.ISDA)),
        ]
        
        self.business_convention_options = [
            ('Unadjusted', ql.Unadjusted),
            ('Following', ql.Following),
            ('ModifiedFollowing', ql.ModifiedFollowing),
        ]
        
        self.payment_frequency_options = [
            ('Semiannual', ql.Semiannual),
            ('Annual', ql.Annual),
        ]
        
        # Zero tolerance for institutional-grade accuracy
        self.tolerance = 0.01
        
        logger.info(f"🎯 Convention Tester initialized - Zero tolerance: ≤{self.tolerance}")
    
    def get_test_bonds(self, table_name: str, limit: int = 500) -> List[Dict]:
        """Get bonds for testing with proper date format"""
        
        query = f"""
        SELECT 
            isin,
            coupon,
            maturity_fixed as maturity,
            bloomberg_accrued,
            description
        FROM {table_name}
        WHERE bloomberg_accrued IS NOT NULL 
          AND bloomberg_accrued > 0
          AND maturity_fixed IS NOT NULL
          AND coupon IS NOT NULL
        LIMIT ?
        """
        
        cursor = self.conn.execute(query, (limit,))
        columns = [description[0] for description in cursor.description]
        
        bonds = []
        for row in cursor.fetchall():
            bond_dict = dict(zip(columns, row))
            bonds.append(bond_dict)
        
        logger.info(f"📊 Loaded {len(bonds):,} bonds from {table_name} for convention testing")
        return bonds
    
    def calculate_quantlib_accrued_with_conventions(self, isin: str, coupon: float, maturity_str: str,
                                                   day_count, business_conv, payment_freq) -> Tuple[float, str]:
        """Calculate QuantLib accrued with specific conventions"""
        try:
            # Parse maturity date (YYYY-MM-DD format from maturity_fixed)
            try:
                mat_parts = maturity_str.split('-')
                maturity_date = ql.Date(int(mat_parts[2]), int(mat_parts[1]), int(mat_parts[0]))
            except Exception as e:
                return 0.0, f"date_parse_error: {str(e)}"
            
            # Validate maturity is after settlement
            if maturity_date <= self.settlement_date:
                return 0.0, "maturity_before_settlement"
            
            # Calculate issue date
            years_to_maturity = (maturity_date - self.settlement_date) / 365.25
            
            if years_to_maturity > 10:
                lookback_years = 10
            elif years_to_maturity > 5:
                lookback_years = 5
            else:
                lookback_years = max(1, int(years_to_maturity * 0.8))
            
            issue_date = maturity_date - ql.Period(lookback_years, ql.Years)
            
            # Ensure issue date is before settlement
            if issue_date >= self.settlement_date:
                issue_date = self.settlement_date - ql.Period(1, ql.Years)
            
            # Create schedule
            schedule = ql.Schedule(
                issue_date,
                maturity_date,
                ql.Period(payment_freq),
                ql.UnitedStates(ql.UnitedStates.GovernmentBond),
                business_conv,
                business_conv,
                ql.DateGeneration.Backward,
                False
            )
            
            # Create bond
            bond = ql.FixedRateBond(
                2,  # Settlement days
                100.0,  # Face value
                schedule,
                [coupon / 100.0],  # Coupon rate as decimal
                day_count
            )
            
            # Calculate accrued interest
            accrued = bond.accruedAmount(self.settlement_date)
            accrued_per_million = accrued * 10000  # Convert to per million format
            
            return accrued_per_million, "success"
            
        except Exception as e:
            return 0.0, f"quantlib_error: {str(e)}"
    
    def test_convention_combination(self, bonds_sample: List[Dict], 
                                  day_count_name: str, day_count,
                                  business_conv_name: str, business_conv,
                                  payment_freq_name: str, payment_freq) -> Dict:
        """Test a specific convention combination"""
        
        perfect_matches = 0
        calculation_failures = 0
        total_difference = 0.0
        max_difference = 0.0
        results = []
        
        for bond in bonds_sample:
            isin = bond['isin']
            bloomberg_accrued = float(bond['bloomberg_accrued'])
            
            # Calculate with specific conventions
            quantlib_accrued, calc_status = self.calculate_quantlib_accrued_with_conventions(
                isin=isin,
                coupon=float(bond['coupon']),
                maturity_str=bond['maturity'],
                day_count=day_count,
                business_conv=business_conv,
                payment_freq=payment_freq
            )
            
            if calc_status == "success" and quantlib_accrued > 0:
                difference = abs(bloomberg_accrued - quantlib_accrued)
                
                if difference <= self.tolerance:
                    perfect_matches += 1
                
                total_difference += difference
                max_difference = max(max_difference, difference)
                
                results.append({
                    'isin': isin,
                    'bloomberg': bloomberg_accrued,
                    'quantlib': quantlib_accrued,
                    'difference': difference,
                    'perfect': difference <= self.tolerance
                })
            else:
                calculation_failures += 1
        
        # Calculate statistics
        successful_calcs = len(results)
        total_tested = len(bonds_sample)
        
        perfect_rate = (perfect_matches / total_tested) * 100 if total_tested > 0 else 0
        success_rate = (successful_calcs / total_tested) * 100 if total_tested > 0 else 0
        avg_difference = total_difference / successful_calcs if successful_calcs > 0 else float('inf')
        
        return {
            'combination': f"{day_count_name}|{business_conv_name}|{payment_freq_name}",
            'perfect_matches': perfect_matches,
            'total_tested': total_tested,
            'successful_calculations': successful_calcs,
            'calculation_failures': calculation_failures,
            'perfect_rate_pct': perfect_rate,
            'success_rate_pct': success_rate,
            'avg_difference': avg_difference,
            'max_difference': max_difference,
            'sample_results': results[:3]  # First 3 for inspection
        }
    
    def find_optimal_conventions(self, table_name: str = "all_bonds_calculations", sample_size: int = 500) -> Dict:
        """Find optimal conventions for the specified table"""
        
        logger.info(f"🚀 Starting convention optimization for {table_name}")
        logger.info(f"🎯 Sample size: {sample_size} bonds")
        logger.info(f"🎯 Zero tolerance: ≤{self.tolerance} per million")
        
        # Get test bonds
        bonds_sample = self.get_test_bonds(table_name, sample_size)
        
        if len(bonds_sample) == 0:
            logger.warning("⚠️ No bonds found for testing!")
            return {'error': 'no_bonds_found'}
        
        # Test all combinations
        results = []
        total_combinations = len(self.day_count_options) * len(self.business_convention_options) * len(self.payment_frequency_options)
        
        combination_count = 0
        
        for dc_name, dc in self.day_count_options:
            for bc_name, bc in self.business_convention_options:
                for pf_name, pf in self.payment_frequency_options:
                    combination_count += 1
                    
                    logger.info(f"🔄 Testing {combination_count}/{total_combinations}: {dc_name}|{bc_name}|{pf_name}")
                    
                    result = self.test_convention_combination(
                        bonds_sample, dc_name, dc, bc_name, bc, pf_name, pf
                    )
                    
                    results.append(result)
                    
                    logger.info(f"   ✅ Perfect: {result['perfect_matches']}/{len(bonds_sample)} ({result['perfect_rate_pct']:.1f}%)")
                    
                    # Early termination if we find excellent results
                    if result['perfect_rate_pct'] >= 90.0:
                        logger.info(f"🎯 EXCELLENT RESULT FOUND: {result['perfect_rate_pct']:.1f}% perfect!")
        
        # Sort by perfect rate
        results.sort(key=lambda x: x['perfect_rate_pct'], reverse=True)
        
        # Summary
        best_result = results[0] if results else None
        
        summary = {
            'table_name': table_name,
            'sample_size': len(bonds_sample),
            'total_combinations_tested': len(results),
            'best_combination': best_result['combination'] if best_result else None,
            'best_perfect_rate': best_result['perfect_rate_pct'] if best_result else 0,
            'best_success_rate': best_result['success_rate_pct'] if best_result else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        final_results = {
            'summary': summary,
            'all_results': results,
            'top_5_combinations': results[:5]
        }
        
        logger.info("🏆 CONVENTION OPTIMIZATION COMPLETE")
        logger.info(f"🥇 Best: {summary['best_combination']} ({summary['best_perfect_rate']:.1f}% perfect)")
        
        return final_results

def run_convention_optimization(table_name: str = "all_bonds_calculations", sample_size: int = 500):
    """🎯 Run convention optimization on specified table"""
    
    print(f"🎯 CONVENTION OPTIMIZATION - {table_name.upper()}")
    print(f"✅ Sample size: {sample_size} bonds")
    print(f"✅ Zero tolerance: ≤0.01 per million")
    print("=" * 70)
    
    # Initialize tester
    tester = ConventionTester()
    
    # Find optimal conventions
    results = tester.find_optimal_conventions(table_name, sample_size)
    
    # Print summary
    if 'summary' in results:
        summary = results['summary']
        print(f"\\n🏆 OPTIMIZATION COMPLETE")
        print(f"📊 Tested: {summary['total_combinations_tested']} combinations")
        print(f"🎯 Best: {summary['best_combination']}")
        print(f"✅ Perfect Rate: {summary['best_perfect_rate']:.1f}%")
        print(f"📈 Success Rate: {summary['best_success_rate']:.1f}%")
        
        if summary['best_perfect_rate'] >= 80:
            print("🎉 EXCELLENT RESULT!")
        elif summary['best_perfect_rate'] >= 50:
            print("🚀 GOOD RESULT - PROMISING DIRECTION")
        else:
            print("⚠️ NEEDS FURTHER INVESTIGATION")
            
        # Show top 3 results
        print("\\n📊 TOP 3 COMBINATIONS:")
        for i, result in enumerate(results['top_5_combinations'][:3], 1):
            print(f"   {i}. {result['combination']}: {result['perfect_rate_pct']:.1f}% perfect")
    
    return results

'''

# Insert the convention testing code
new_content = content[:insertion_point] + convention_code + "\n" + content[insertion_point:]

# Write the updated content
with open('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9/bb_quantlib_loop.py', 'w') as f:
    f.write(new_content)

print("✅ Convention testing functionality added to bb_quantlib_loop.py")
