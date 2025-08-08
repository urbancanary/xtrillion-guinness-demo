# Check if API might be using annual vs semi-annual modified duration

ytm_semi = 0.04890641  # 4.890641% semi-annual
ytm_annual = 0.04950437  # 4.950437% annual (from API)
macaulay = 16.952584

print("Testing different modified duration formulas:")
print(f"Macaulay Duration: {macaulay}")
print(f"YTM (semi-annual): {ytm_semi*100:.6f}%")
print(f"YTM (annual): {ytm_annual*100:.6f}%")
print()

# Standard semi-annual modified duration
mod_semi = macaulay / (1 + ytm_semi/2)
print(f"Modified (semi-annual): {mod_semi:.6f}")

# Annual modified duration
mod_annual = macaulay / (1 + ytm_annual)
print(f"Modified (annual): {mod_annual:.6f}")

# What if they're using a different Macaulay?
# Working backwards from expected 16.35
target_mod = 16.35
implied_mac = target_mod * (1 + ytm_semi/2)
print(f"\nTo get modified duration of {target_mod}:")
print(f"Implied Macaulay would be: {implied_mac:.6f}")

# Check the API's annual_duration field
api_annual_duration = 16.152942
print(f"\nAPI annual_duration field: {api_annual_duration}")
print(f"This suggests Macaulay / (1 + ytm_annual) = {macaulay} / {1 + ytm_annual:.6f} = {macaulay/(1+ytm_annual):.6f}")
