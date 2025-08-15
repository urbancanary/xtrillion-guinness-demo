#!/usr/bin/env python3
"""
Verify which ISIN is correct for T 3 15/08/52
"""

print("Verifying correct ISIN for T 3 15/08/52")
print("=" * 60)

print("\nBased on database lookup:")
print("- US912810TJ79 = 'US TREASURY N/B, 3%, 15-Aug-2052' ✅ CORRECT")
print("- US91282CJZ59 = 'T 4 02/15/34' ❌ WRONG")

print("\nThe description parser is finding the wrong ISIN!")
print("When parsing 'T 3 15/08/52', it incorrectly returns US91282CJZ59")
print("which is actually a 4% bond maturing in 2034, not a 3% bond maturing in 2052.")

print("\nIMPLICATIONS:")
print("1. The ISIN route (US912810TJ79) is giving the CORRECT results")
print("2. The description route is using the WRONG bond (US91282CJZ59)")
print("3. This explains the small differences in YTM and duration")

print("\nRECOMMENDATION:")
print("The parser needs to be fixed to return the correct ISIN for 'T 3 15/08/52'")