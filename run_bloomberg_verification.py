#!/usr/bin/env python3
"""
Quick Bloomberg Accrued Interest Verification
Run this to verify all 2,057 bonds from your Excel file
"""

import pandas as pd
from datetime import datetime, date
import re

def quick_parse_bond(description):
    """Quick bond parsing for accrued interest calculation"""
    desc = str(description).strip()
    
    # Handle fractions
    fractions = {'⅛': 0.125, '¼': 0.25, '⅜': 0.375, '½': 0.5, '⅝': 0.625, '¾': 0.75, '⅞': 0.875}
    
    coupon = 0
    maturity = None
    
    # Extract coupon
    for frac, decimal in fractions.items():
        if frac in desc:
            parts = desc.split(frac)[0].strip().split()
            if parts and parts[-1].replace('.', '').isdigit():
                coupon = float(parts[-1]) + decimal
                break
    
    if coupon == 0:
        # Look for decimal coupon
        match = re.search(r'(\d+\.?\d*)', desc)
        if match:
            candidate = float(match.group(1))
            if 0 <= candidate <= 20:
                coupon = candidate
    
    # Extract maturity date
    date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', desc)
    if date_match:
        month, day, year = date_match.groups()
        if len(year) == 2:
            year = '20' + year if int(year) < 50 else '19' + year
        try:
            maturity = date(int(year), int(month), int(day))
        except:
            pass
    
    return coupon, maturity

def calculate_simple_accrued(coupon, maturity_date, settlement_date=None):
    """Simple accrued interest calculation"""
    if not settlement_date:
        settlement_date = date(2025, 7, 29)
    
    if not maturity_date or coupon == 0:
        return 0.0
    
    # Estimate last payment (6 months before maturity, adjusted)
    try:
        last_payment = maturity_date.replace(month=maturity_date.month-6 if maturity_date.month > 6 else maturity_date.month+6, 
                                           year=maturity_date.year-1 if maturity_date.month <= 6 else maturity_date.year)
        
        # If still after settlement, go back another 6 months
        if last_payment > settlement_date:
            last_payment = last_payment.replace(month=last_payment.month-6 if last_payment.month > 6 else last_payment.month+6,
                                              year=last_payment.year-1 if last_payment.month <= 6 else last_payment.year)
        
        # Calculate accrued (30/360 convention)
        days_accrued = (settlement_date - last_payment).days
        days_in_period = 180  # Semi-annual
        period_coupon = coupon / 2
        
        accrued = period_coupon * (days_accrued / days_in_period)
        return max(0, accrued)
        
    except:
        return 0.0

def main():
    print("🧮 Bloomberg Accrued Interest Quick Verification")
    print("=" * 60)
    
    try:
        # Read the Excel file
        df = pd.read_excel('EMUSTRUU Index as of Jul 29 20251.xlsx')
        print(f"✅ Loaded {len(df)} bonds from Bloomberg file")
        
        # Process all bonds
        results = []
        successful = 0
        
        print("🔄 Processing bonds...")
        
        for index, row in df.iterrows():
            if index % 500 == 0:
                print(f"   Progress: {index}/{len(df)}")
            
            isin = row.get('ISIN', '')
            description = row.get('Description', '')
            price = row.get('Price', 0)
            
            coupon, maturity = quick_parse_bond(description)
            accrued = calculate_simple_accrued(coupon, maturity)
            
            if coupon > 0 and maturity:
                successful += 1
            
            results.append({
                'ISIN': isin,
                'Description': description,
                'Price': price,
                'Coupon_Parsed': coupon,
                'Maturity_Parsed': maturity,
                'Accrued_Interest_Calculated': accrued,
                'Parse_Success': 'YES' if coupon > 0 and maturity else 'NO'
            })
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"bloomberg_accrued_verification_{timestamp}.csv"
        results_df.to_csv(output_file, index=False)
        
        print(f"\n✅ Verification Complete!")
        print(f"   Total bonds: {len(df)}")
        print(f"   Successfully parsed: {successful}")
        print(f"   Success rate: {successful/len(df)*100:.1f}%")
        print(f"   Output file: {output_file}")
        
        # Show sample results
        print(f"\n🔍 Sample Results:")
        print("-" * 70)
        success_df = results_df[results_df['Parse_Success'] == 'YES'].head(10)
        
        for _, row in success_df.iterrows():
            print(f"{row['ISIN'][:12]:12} | {row['Description'][:25]:25} | "
                  f"{row['Coupon_Parsed']:5.2f}% | {row['Accrued_Interest_Calculated']:6.3f}%")
        
        print(f"\n💡 Next Steps:")
        print(f"1. Open '{output_file}' in Excel")
        print(f"2. Compare 'Accrued_Interest_Calculated' with Bloomberg's accrued interest")
        print(f"3. Look for bonds where 'Parse_Success' = NO for manual review")
        
        return results_df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    results = main()
