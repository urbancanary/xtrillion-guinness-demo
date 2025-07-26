#!/usr/bin/env python3
"""
Use PROVEN bbg_quantlib_calculations.py for full portfolio
=========================================================
Using the existing working infrastructure instead of recreating
Settlement: 2025-04-18 (the proven working date)
"""

import sys
import pandas as pd
from datetime import datetime
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9')

from bbg_quantlib_calculations import calculate_ytw_and_oad

def main(settlement_date=None):
    """Run full portfolio using a variable settlement date."""

    if settlement_date is None:
        # Default to today's date if no settlement date is provided
        settlement_date = datetime.now().strftime('%Y-%m-%d')

    # Full portfolio data
    portfolio = [
        {'isin': 'US912810TJ79', 'price': 71.66, 'coupon': 3.0, 'maturity': '2052-08-15', 'description': 'US TREASURY N/B, 3%, 15-Aug-2052', 'country': 'United States', 'rating': 'Aaa'},
        {'isin': 'XS2249741674', 'price': 77.88, 'coupon': 3.25, 'maturity': '2040-09-30', 'description': 'GALAXY PIPELINE, 3.25%, 30-Sep-2040', 'country': 'Abu Dhabi', 'rating': 'Aa2'},
        {'isin': 'XS1709535097', 'price': 89.40, 'coupon': 4.6, 'maturity': '2047-11-02', 'description': 'ABU DHABI CRUDE, 4.6%, 02-Nov-2047', 'country': 'Abu Dhabi', 'rating': 'AA'},
        {'isin': 'XS1982113463', 'price': 87.14, 'coupon': 4.25, 'maturity': '2039-04-16', 'description': 'SAUDI ARAB OIL, 4.25%, 16-Apr-2039', 'country': 'Saudi Arabia', 'rating': 'A1'},
        {'isin': 'USP37466AS18', 'price': 80.39, 'coupon': 4.7, 'maturity': '2050-05-07', 'description': 'EMPRESA METRO, 4.7%, 07-May-2050', 'country': 'Chile', 'rating': 'A3'},
        {'isin': 'USP3143NAH72', 'price': 101.63, 'coupon': 6.15, 'maturity': '2036-10-24', 'description': 'CODELCO INC, 6.15%, 24-Oct-2036', 'country': 'Chile', 'rating': 'Baa1'},
        {'isin': 'USP30179BR86', 'price': 86.42, 'coupon': 6.264, 'maturity': '2052-02-15', 'description': 'COMISION FEDERAL, 6.264%, 15-Feb-2052', 'country': 'Mexico', 'rating': 'Baa2'},
        {'isin': 'US195325DX04', 'price': 52.71, 'coupon': 3.875, 'maturity': '2061-02-15', 'description': 'COLOMBIA REP OF, 3.875%, 15-Feb-2061', 'country': 'Colombia', 'rating': 'Baa2'},
        {'isin': 'US279158AJ82', 'price': 69.31, 'coupon': 5.875, 'maturity': '2045-05-28', 'description': 'ECOPETROL SA, 5.875%, 28-May-2045', 'country': 'Colombia', 'rating': 'Ba1'},
        {'isin': 'USP37110AM89', 'price': 76.24, 'coupon': 4.5, 'maturity': '2047-09-14', 'description': 'EMPRESA NACIONAL, 4.5%, 14-Sep-2047', 'country': 'Chile', 'rating': 'A-'},
        {'isin': 'XS2542166231', 'price': 103.03, 'coupon': 6.129, 'maturity': '2038-02-23', 'description': 'GREENSAIF PIPELI, 6.129%, 23-Feb-2038', 'country': 'Saudi Arabia', 'rating': 'A1'},
        {'isin': 'XS2167193015', 'price': 64.50, 'coupon': 3.8, 'maturity': '2060-05-13', 'description': 'STATE OF ISRAEL, 3.8%, 13-May-2060', 'country': 'Israel', 'rating': 'A'},
        {'isin': 'XS1508675508', 'price': 82.42, 'coupon': 4.5, 'maturity': '2046-10-26', 'description': 'SAUDI INT BOND, 4.5%, 26-Oct-2046', 'country': 'Saudi Arabia', 'rating': 'A1'},
        {'isin': 'XS1807299331', 'price': 92.21, 'coupon': 6.375, 'maturity': '2048-10-24', 'description': 'KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048', 'country': 'Kazakhstan', 'rating': 'Baa1'},
        {'isin': 'US91086QAZ19', 'price': 78.00, 'coupon': 5.75, 'maturity': '2110-10-12', 'description': 'UNITED MEXICAN, 5.75%, 12-Oct-2110', 'country': 'Mexico', 'rating': 'Baa2'},
        {'isin': 'USP6629MAD40', 'price': 82.57, 'coupon': 5.5, 'maturity': '2047-07-31', 'description': 'MEXICO CITY ARPT, 5.5%, 31-Jul-2047', 'country': 'Mexico', 'rating': 'BBB'},
        {'isin': 'US698299BL70', 'price': 56.60, 'coupon': 3.87, 'maturity': '2060-07-23', 'description': 'PANAMA, 3.87%, 23-Jul-2060', 'country': 'Panama', 'rating': 'BBB'},
        {'isin': 'US71654QDF63', 'price': 71.42, 'coupon': 6.95, 'maturity': '2060-01-28', 'description': 'PETROLEOS MEXICA, 6.95%, 28-Jan-2060', 'country': 'Mexico', 'rating': 'BBB'},
        {'isin': 'US71654QDE98', 'price': 89.55, 'coupon': 5.95, 'maturity': '2031-01-28', 'description': 'PETROLEOS MEXICA, 5.95%, 28-Jan-2031', 'country': 'Mexico', 'rating': 'BBB'},
        {'isin': 'XS2585988145', 'price': 85.54, 'coupon': 5.125, 'maturity': '2053-02-14', 'description': 'GACI FIRST INVST, 5.125%, 14-Feb-2053', 'country': 'Saudi Arabia', 'rating': 'Aa3'},
        {'isin': 'XS1959337749', 'price': 89.97, 'coupon': 4.817, 'maturity': '2049-03-14', 'description': 'QATAR STATE OF, 4.817%, 14-Mar-2049', 'country': 'Qatar', 'rating': 'Aa2'},
        {'isin': 'XS2233188353', 'price': 99.23, 'coupon': 1.625, 'maturity': '2025-09-22', 'description': 'QNB FINANCE LTD, 1.625%, 22-Sep-2025', 'country': 'Qatar', 'rating': 'Aa3'},
        {'isin': 'XS2359548935', 'price': 73.79, 'coupon': 3.125, 'maturity': '2041-07-12', 'description': 'QATAR ENERGY, 3.125%, 12-Jul-2041', 'country': 'Qatar', 'rating': 'Aa2'},
        {'isin': 'XS0911024635', 'price': 93.29, 'coupon': 5.06, 'maturity': '2043-04-08', 'description': 'SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043', 'country': 'Saudi Arabia', 'rating': 'A1'},
        {'isin': 'USP0R80BAG79', 'price': 97.26, 'coupon': 5.375, 'maturity': '2032-04-04', 'description': 'SITIOS, 5.375%, 04-Apr-2032', 'country': 'Brazil', 'rating': 'Baa3'},
    ]
    
    print("🏦 PROVEN Bond Portfolio Analytics - Using Working System")
    print("=" * 65)
    print(f"Settlement Date: {settlement_date}")
    print("System: bbg_quantlib_calculations.py (tested on 7,787 bonds)")
    print(f"Total Bonds: {len(portfolio)}")
    print()
    
    results = []
    successful = 0
    
    for bond in portfolio:
        isin = bond['isin']
        description = bond['description']
        price = bond['price']
        
        print(f"📊 {isin[:12]}... {description[:40]:40} @ {price:6.2f}")
        
        # Use the provided settlement date
        calc_result = calculate_ytw_and_oad(bond, settlement_date=settlement_date)
        
        if calc_result['success']:
            ytw = calc_result['ytw']
            oad = calc_result['oad']
            
            # Estimate spread (simple approximation)
            if 'US912' in isin:  # Treasury
                spread_bps = 0
            elif ytw > 8:
                spread_bps = (ytw - 4.5) * 100  # High yield estimate
            elif ytw > 6:
                spread_bps = (ytw - 4.2) * 100  # IG corporate estimate
            else:
                spread_bps = (ytw - 4.0) * 100  # High grade estimate
            
            result = {
                'ISIN': isin,
                'Price': price,
                'Description': description,
                'Country': bond['country'],
                'Rating': bond['rating'],
                'Coupon_%': bond['coupon'],
                'YTW_%': round(ytw, 2),
                'OAD_Years': round(oad, 2),
                'Est_Spread_bps': round(spread_bps, 0),
                'Settlement': settlement_date,
                'Method': calc_result['method']
            }
            
            results.append(result)
            successful += 1
            
            print(f"   ✅ YTW: {ytw:6.2f}% | OAD: {oad:5.2f}y | Spr: ~{spread_bps:4.0f}bps | {bond['rating']}")
            
        else:
            print(f"   ❌ Calculation failed: {calc_result.get('method', 'unknown')}")
    
    print(f"\n📊 PROCESSING COMPLETE: {successful}/{len(portfolio)} bonds successful")
    
    if results:
        df = pd.DataFrame(results)
        
        # Portfolio statistics
        avg_ytw = df['YTW_%'].mean()
        avg_oad = df['OAD_Years'].mean()
        avg_spread = df['Est_Spread_bps'].mean()
        
        print(f"\n🎯 PORTFOLIO SUMMARY (Settlement: {settlement_date})")
        print("=" * 55)
        print(f"Average Yield (YTW):     {avg_ytw:.2f}%")
        print(f"Average Duration (OAD):  {avg_oad:.2f} years") 
        print(f"Average Spread:          {avg_spread:.0f} bps (estimated)")
        print(f"Successful Calculations: {successful}")
        print(f"System Used:             PROVEN bbg_quantlib_calculations.py")
        print(f"Settlement Date:         {settlement_date}")
        
        # Country breakdown
        print(f"\n🌍 COUNTRY BREAKDOWN:")
        country_stats = df.groupby('Country').agg({
            'YTW_%': 'mean',
            'Est_Spread_bps': 'mean',
            'Price': 'count'
        }).round(2)
        country_stats.columns = ['Avg_YTW_%', 'Avg_Est_Spread_bps', 'Count']
        country_stats = country_stats.sort_values('Avg_Est_Spread_bps', ascending=False)
        print(country_stats)
        
        # Rating breakdown  
        print(f"\n⭐ RATING BREAKDOWN:")
        rating_stats = df.groupby('Rating').agg({
            'YTW_%': 'mean', 
            'Est_Spread_bps': 'mean',
            'Price': 'count'
        }).round(2)
        rating_stats.columns = ['Avg_YTW_%', 'Avg_Est_Spread_bps', 'Count']
        rating_stats = rating_stats.sort_values('Avg_Est_Spread_bps')
        print(rating_stats)
        
        # Save results
        output_file = f"proven_bond_analytics_{settlement_date.replace('-', '')}.csv"
        df.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to: {output_file}")
        
        # Top yielding bonds
        print(f"\n🔥 TOP 10 HIGHEST YIELDING BONDS:")
        top_10 = df.nlargest(10, 'YTW_%')[['ISIN', 'Description', 'YTW_%', 'Est_Spread_bps', 'OAD_Years', 'Rating']]
        for idx, bond in top_10.iterrows():
            print(f"  {bond['ISIN'][:12]}... {bond['Description'][:25]:25} "
                  f"{bond['YTW_%']:6.2f}% ({bond['Est_Spread_bps']:4.0f}bps, {bond['OAD_Years']:4.1f}y) [{bond['Rating']}]")
        
        return df
    
    else:
        print("❌ No bonds processed successfully")
        return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run bond portfolio analytics.")
    parser.add_argument(
        '--settlement_date',
        type=str,
        help='The settlement date in YYYY-MM-DD format. Defaults to today.'
    )
    args = parser.parse_args()
    
    results_df = main(settlement_date=args.settlement_date)
