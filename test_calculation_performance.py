#!/usr/bin/env python3
"""
Test to determine if calculating only 3 metrics (yield, duration, spread) 
vs all metrics affects performance materially.
"""

import time
import QuantLib as ql
from datetime import datetime
import statistics

def setup_bond():
    """Setup a standard US Treasury bond"""
    # T 3 15/08/52
    settlement_date = ql.Date(1, 8, 2025)
    ql.Settings.instance().evaluationDate = settlement_date
    
    maturity_date = ql.Date(15, 8, 2052)
    issue_date = ql.Date(15, 8, 2022)
    
    schedule = ql.Schedule(
        issue_date,
        maturity_date,
        ql.Period(ql.Semiannual),
        ql.UnitedStates(ql.UnitedStates.GovernmentBond),
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward,
        True
    )
    
    bond = ql.FixedRateBond(
        0,  # settlement days
        100.0,  # face amount
        schedule,
        [0.03],  # coupon rate
        ql.ActualActual(ql.ActualActual.Bond)
    )
    
    return bond, settlement_date

def calculate_all_metrics(bond, price, settlement_date):
    """Calculate all 13+ metrics (current behavior)"""
    
    # Setup
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    compounding = ql.Compounded
    frequency = ql.Semiannual
    
    # Clean and dirty price
    clean_price = price
    accrued = bond.accruedAmount(settlement_date)
    dirty_price = clean_price + accrued
    
    # Yield calculation
    ytm = bond.bondYield(clean_price, day_count, compounding, frequency)
    
    # Duration (Modified)
    duration = ql.BondFunctions.duration(
        bond, ytm, day_count, compounding, frequency, 
        ql.Duration.Modified
    )
    
    # Macaulay Duration
    macaulay_duration = ql.BondFunctions.duration(
        bond, ytm, day_count, compounding, frequency,
        ql.Duration.Macaulay
    )
    
    # Convexity
    convexity = ql.BondFunctions.convexity(
        bond, ytm, day_count, compounding, frequency
    )
    
    # PVBP (DV01)
    basis_point = 0.0001
    pvbp = ql.BondFunctions.basisPointValue(
        bond, ytm, day_count, compounding, frequency
    )
    
    # Annual versions
    annual_compounding = ql.Compounded
    annual_frequency = ql.Annual
    
    # Annual yield
    ytm_annual = bond.bondYield(clean_price, day_count, annual_compounding, annual_frequency)
    
    # Annual duration
    duration_annual = ql.BondFunctions.duration(
        bond, ytm_annual, day_count, annual_compounding, annual_frequency,
        ql.Duration.Modified
    )
    
    # Annual Macaulay
    macaulay_annual = ql.BondFunctions.duration(
        bond, ytm_annual, day_count, annual_compounding, annual_frequency,
        ql.Duration.Macaulay
    )
    
    # Spread calculation (simplified - would need treasury curve)
    spread = None  # Would require treasury curve lookup
    z_spread = None  # Would require full curve bootstrapping
    
    return {
        'ytm': ytm * 100,
        'duration': duration,
        'macaulay_duration': macaulay_duration,
        'convexity': convexity,
        'pvbp': pvbp,
        'clean_price': clean_price,
        'dirty_price': dirty_price,
        'accrued_interest': accrued,
        'ytm_annual': ytm_annual * 100,
        'duration_annual': duration_annual,
        'macaulay_annual': macaulay_annual,
        'spread': spread,
        'z_spread': z_spread
    }

def calculate_minimal_metrics(bond, price, settlement_date):
    """Calculate only 3 metrics (yield, duration, spread)"""
    
    # Setup
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    compounding = ql.Compounded
    frequency = ql.Semiannual
    
    # Yield calculation (REQUIRED - needed for duration)
    clean_price = price
    ytm = bond.bondYield(clean_price, day_count, compounding, frequency)
    
    # Duration (Modified) - depends on yield
    duration = ql.BondFunctions.duration(
        bond, ytm, day_count, compounding, frequency,
        ql.Duration.Modified
    )
    
    # Spread (simplified - would need treasury curve)
    spread = None
    
    return {
        'ytm': ytm * 100,
        'duration': duration,
        'spread': spread
    }

def run_performance_test(iterations=1000):
    """Compare performance of full vs minimal calculations"""
    
    print("=" * 80)
    print("QuantLib Calculation Performance: All Metrics vs Minimal (3 metrics)")
    print("=" * 80)
    
    # Setup bond once
    bond, settlement_date = setup_bond()
    price = 71.66
    
    # Warm up
    for _ in range(10):
        calculate_all_metrics(bond, price, settlement_date)
        calculate_minimal_metrics(bond, price, settlement_date)
    
    print(f"\nRunning {iterations} iterations for each test...\n")
    
    # Test all metrics
    all_metrics_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = calculate_all_metrics(bond, price, settlement_date)
        end = time.perf_counter()
        all_metrics_times.append((end - start) * 1000)  # Convert to ms
    
    # Test minimal metrics
    minimal_metrics_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = calculate_minimal_metrics(bond, price, settlement_date)
        end = time.perf_counter()
        minimal_metrics_times.append((end - start) * 1000)  # Convert to ms
    
    # Calculate statistics
    all_avg = statistics.mean(all_metrics_times)
    all_median = statistics.median(all_metrics_times)
    all_p95 = statistics.quantiles(all_metrics_times, n=20)[18]
    
    minimal_avg = statistics.mean(minimal_metrics_times)
    minimal_median = statistics.median(minimal_metrics_times)
    minimal_p95 = statistics.quantiles(minimal_metrics_times, n=20)[18]
    
    # Results
    print("📊 CALCULATION TIME RESULTS:")
    print("-" * 50)
    
    print("\nAll Metrics (13 calculations):")
    print(f"  Average:   {all_avg:.4f} ms")
    print(f"  Median:    {all_median:.4f} ms")
    print(f"  P95:       {all_p95:.4f} ms")
    
    print("\nMinimal Metrics (3 calculations):")
    print(f"  Average:   {minimal_avg:.4f} ms")
    print(f"  Median:    {minimal_median:.4f} ms")
    print(f"  P95:       {minimal_p95:.4f} ms")
    
    # Performance improvement
    time_saved = all_avg - minimal_avg
    percent_faster = (time_saved / all_avg) * 100
    
    print("\n⚡ PERFORMANCE IMPROVEMENT:")
    print(f"  Time saved per calculation: {time_saved:.4f} ms")
    print(f"  Percentage faster: {percent_faster:.1f}%")
    print(f"  Speedup factor: {all_avg/minimal_avg:.2f}x")
    
    # Impact on large portfolios
    print("\n📈 IMPACT ON PORTFOLIO PROCESSING:")
    print("-" * 50)
    
    portfolio_sizes = [100, 1000, 10000, 50000]
    
    print(f"\n{'Portfolio Size':<15} {'All Metrics':<15} {'Minimal':<15} {'Time Saved':<15}")
    print("-" * 60)
    
    for size in portfolio_sizes:
        all_time = (all_avg * size) / 1000  # Convert to seconds
        minimal_time = (minimal_avg * size) / 1000
        saved = all_time - minimal_time
        
        print(f"{size:,} bonds{' ':<5} {all_time:>8.2f}s      {minimal_time:>8.2f}s      {saved:>8.2f}s")
    
    # Key insights
    print("\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    
    if percent_faster > 50:
        print("✅ SIGNIFICANT performance improvement from calculating only required metrics")
        print(f"   Calculating only 3 metrics is {percent_faster:.0f}% faster!")
    elif percent_faster > 20:
        print("⚡ MODERATE performance improvement from calculating only required metrics")
        print(f"   Calculating only 3 metrics is {percent_faster:.0f}% faster")
    else:
        print("ℹ️  MINIMAL performance difference between full and minimal calculations")
        print(f"   Only {percent_faster:.0f}% faster - most time is in core yield calculation")
    
    print("\n💡 RECOMMENDATION:")
    if percent_faster > 30:
        print("   Implement selective metric calculation for significant performance gains")
        print("   Especially beneficial for high-frequency/large portfolio use cases")
    else:
        print("   Performance gain is modest - focus on network/response size optimization")
        print("   The main benefit would be reduced bandwidth, not calculation speed")

if __name__ == "__main__":
    run_performance_test(iterations=1000)