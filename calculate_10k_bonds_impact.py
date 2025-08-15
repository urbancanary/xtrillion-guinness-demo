#!/usr/bin/env python3
"""
Calculate the performance impact for processing 10,000 bonds
comparing full metrics vs minimal (yield, spread, duration only)
"""

# Data from our performance tests
FULL_RESPONSE_SIZE = 1427  # bytes per bond
PORTFOLIO_CONTEXT_SIZE = 704  # bytes per bond  
MINIMAL_RESPONSE_SIZE = 123  # bytes per bond (estimated)

FULL_RESPONSE_TIME = 72.74  # ms average
PORTFOLIO_RESPONSE_TIME = 67.31  # ms average

# Network assumptions
NETWORK_BANDWIDTH_MBPS = 100  # Typical enterprise connection
NETWORK_LATENCY_MS = 20  # Typical latency to cloud API

def calculate_impact(num_bonds=10000):
    print("=" * 80)
    print(f"Performance Impact Analysis for {num_bonds:,} Bonds")
    print("=" * 80)
    
    # Calculate total data sizes
    full_total_mb = (FULL_RESPONSE_SIZE * num_bonds) / (1024 * 1024)
    portfolio_total_mb = (PORTFOLIO_CONTEXT_SIZE * num_bonds) / (1024 * 1024)
    minimal_total_mb = (MINIMAL_RESPONSE_SIZE * num_bonds) / (1024 * 1024)
    
    print(f"\n📊 TOTAL RESPONSE SIZE for {num_bonds:,} bonds:")
    print(f"  Full metrics (15 fields):     {full_total_mb:.1f} MB")
    print(f"  Portfolio context (12 fields): {portfolio_total_mb:.1f} MB")
    print(f"  Minimal (3 fields):           {minimal_total_mb:.1f} MB")
    
    print(f"\n💾 DATA SAVINGS with minimal response:")
    data_saved_mb = full_total_mb - minimal_total_mb
    print(f"  Data saved: {data_saved_mb:.1f} MB ({(data_saved_mb/full_total_mb)*100:.1f}% reduction)")
    
    # Calculate network transfer time
    network_speed_bytes_per_ms = (NETWORK_BANDWIDTH_MBPS * 1024 * 1024) / (8 * 1000)  # Convert Mbps to bytes/ms
    
    full_transfer_time_ms = (FULL_RESPONSE_SIZE * num_bonds) / network_speed_bytes_per_ms
    portfolio_transfer_time_ms = (PORTFOLIO_CONTEXT_SIZE * num_bonds) / network_speed_bytes_per_ms
    minimal_transfer_time_ms = (MINIMAL_RESPONSE_SIZE * num_bonds) / network_speed_bytes_per_ms
    
    print(f"\n⏱️  NETWORK TRANSFER TIME @ {NETWORK_BANDWIDTH_MBPS} Mbps:")
    print(f"  Full metrics:      {full_transfer_time_ms/1000:.2f} seconds")
    print(f"  Portfolio context: {portfolio_transfer_time_ms/1000:.2f} seconds")
    print(f"  Minimal:          {minimal_transfer_time_ms/1000:.2f} seconds")
    
    transfer_time_saved = (full_transfer_time_ms - minimal_transfer_time_ms) / 1000
    print(f"  Time saved: {transfer_time_saved:.2f} seconds")
    
    # Processing scenarios
    print(f"\n🔄 PROCESSING SCENARIOS:")
    
    # Scenario 1: Sequential processing (one by one)
    print(f"\n  1️⃣  Sequential Processing (one bond at a time):")
    full_sequential_time = (FULL_RESPONSE_TIME * num_bonds) / 1000  # Convert to seconds
    minimal_sequential_time = (FULL_RESPONSE_TIME * num_bonds) / 1000  # Calculation time same
    
    # Add transfer time
    full_sequential_total = full_sequential_time + (full_transfer_time_ms / 1000)
    minimal_sequential_total = minimal_sequential_time + (minimal_transfer_time_ms / 1000)
    
    print(f"     Full metrics total:  {full_sequential_total:.1f} seconds")
    print(f"     Minimal total:       {minimal_sequential_total:.1f} seconds")
    print(f"     Time saved:          {full_sequential_total - minimal_sequential_total:.1f} seconds")
    
    # Scenario 2: Batch processing (100 bonds per request)
    batch_size = 100
    num_batches = num_bonds // batch_size
    
    print(f"\n  2️⃣  Batch Processing ({batch_size} bonds per request, {num_batches} requests):")
    
    # Assume batch processing is more efficient (80ms base + 5ms per bond)
    batch_process_time = (80 + (5 * batch_size)) * num_batches / 1000  # seconds
    
    full_batch_total = batch_process_time + (full_transfer_time_ms / 1000)
    minimal_batch_total = batch_process_time + (minimal_transfer_time_ms / 1000)
    
    print(f"     Full metrics total:  {full_batch_total:.1f} seconds")
    print(f"     Minimal total:       {minimal_batch_total:.1f} seconds")
    print(f"     Time saved:          {full_batch_total - minimal_batch_total:.1f} seconds")
    
    # Scenario 3: Parallel processing (10 concurrent connections)
    concurrent_connections = 10
    bonds_per_connection = num_bonds // concurrent_connections
    
    print(f"\n  3️⃣  Parallel Processing ({concurrent_connections} concurrent connections):")
    
    # Each connection processes its share
    parallel_process_time = (FULL_RESPONSE_TIME * bonds_per_connection) / 1000
    
    # Network is shared, so transfer time doesn't improve as much
    effective_bandwidth_per_connection = NETWORK_BANDWIDTH_MBPS / concurrent_connections
    parallel_network_speed = (effective_bandwidth_per_connection * 1024 * 1024) / (8 * 1000)
    
    full_parallel_transfer = (FULL_RESPONSE_SIZE * bonds_per_connection) / parallel_network_speed / 1000
    minimal_parallel_transfer = (MINIMAL_RESPONSE_SIZE * bonds_per_connection) / parallel_network_speed / 1000
    
    full_parallel_total = parallel_process_time + full_parallel_transfer
    minimal_parallel_total = parallel_process_time + minimal_parallel_transfer
    
    print(f"     Full metrics total:  {full_parallel_total:.1f} seconds")
    print(f"     Minimal total:       {minimal_parallel_total:.1f} seconds")
    print(f"     Time saved:          {full_parallel_total - minimal_parallel_total:.1f} seconds")
    
    # JSON parsing overhead
    print(f"\n📋 CLIENT-SIDE JSON PARSING:")
    
    # Approximate parsing speed: 50 MB/s for JSON
    json_parse_speed_bytes_per_ms = 50 * 1024 * 1024 / 1000  # 50 MB/s
    
    full_parse_time = (FULL_RESPONSE_SIZE * num_bonds) / json_parse_speed_bytes_per_ms / 1000
    minimal_parse_time = (MINIMAL_RESPONSE_SIZE * num_bonds) / json_parse_speed_bytes_per_ms / 1000
    
    print(f"  Full metrics:    {full_parse_time:.2f} seconds")
    print(f"  Minimal:         {minimal_parse_time:.2f} seconds")
    print(f"  Time saved:      {full_parse_time - minimal_parse_time:.2f} seconds")
    
    # Memory usage
    print(f"\n💻 CLIENT MEMORY USAGE:")
    print(f"  Full metrics:    {full_total_mb:.1f} MB in memory")
    print(f"  Minimal:         {minimal_total_mb:.1f} MB in memory")
    print(f"  Memory saved:    {full_total_mb - minimal_total_mb:.1f} MB")
    
    # Cost implications (assuming cloud egress pricing)
    egress_cost_per_gb = 0.09  # Typical cloud egress cost
    
    print(f"\n💰 BANDWIDTH COST (at ${egress_cost_per_gb}/GB egress):")
    full_cost = (full_total_mb / 1024) * egress_cost_per_gb
    minimal_cost = (minimal_total_mb / 1024) * egress_cost_per_gb
    
    print(f"  Full metrics:    ${full_cost:.4f}")
    print(f"  Minimal:         ${minimal_cost:.4f}")
    print(f"  Cost saved:      ${full_cost - minimal_cost:.4f} ({((full_cost-minimal_cost)/full_cost)*100:.1f}% reduction)")
    
    # Daily/Monthly projections
    print(f"\n📈 USAGE PROJECTIONS:")
    
    # If processing 10,000 bonds multiple times per day
    runs_per_day = 10  # e.g., every 2-3 hours
    
    daily_data_saved_gb = (data_saved_mb * runs_per_day) / 1024
    monthly_data_saved_gb = daily_data_saved_gb * 22  # Business days
    
    daily_cost_saved = (full_cost - minimal_cost) * runs_per_day
    monthly_cost_saved = daily_cost_saved * 22
    
    print(f"  If processing {num_bonds:,} bonds {runs_per_day}x per day:")
    print(f"    Daily data saved:    {daily_data_saved_gb:.1f} GB")
    print(f"    Monthly data saved:  {monthly_data_saved_gb:.1f} GB")
    print(f"    Daily cost saved:    ${daily_cost_saved:.2f}")
    print(f"    Monthly cost saved:  ${monthly_cost_saved:.2f}")
    print(f"    Annual cost saved:   ${monthly_cost_saved * 12:.2f}")
    
    # Summary
    print(f"\n" + "=" * 80)
    print("SUMMARY: Minimal Response (3 fields) vs Full Response (15 fields)")
    print("=" * 80)
    
    print(f"\n✅ KEY BENEFITS for {num_bonds:,} bonds:")
    print(f"  • {(data_saved_mb/full_total_mb)*100:.0f}% less data transferred ({data_saved_mb:.1f} MB saved)")
    print(f"  • {transfer_time_saved:.1f} seconds faster network transfer")
    print(f"  • {(full_parse_time - minimal_parse_time):.1f} seconds faster JSON parsing")
    print(f"  • {full_total_mb - minimal_total_mb:.1f} MB less memory usage")
    print(f"  • ${(full_cost - minimal_cost):.4f} saved per run in bandwidth costs")
    
    if runs_per_day > 1:
        print(f"\n💡 At {runs_per_day} runs per day:")
        print(f"  • ${monthly_cost_saved:.0f}/month in bandwidth savings")
        print(f"  • {monthly_data_saved_gb:.0f} GB/month less data transfer")

if __name__ == "__main__":
    # Analyze for 10,000 bonds
    calculate_impact(10000)
    
    print("\n" * 2)
    
    # Also show impact for other common portfolio sizes
    print("=" * 80)
    print("QUICK COMPARISON - Time Saved (Network Transfer Only)")
    print("=" * 80)
    
    portfolio_sizes = [100, 500, 1000, 5000, 10000, 25000, 50000]
    
    print(f"\n{'Portfolio Size':<20} {'Full Response':<15} {'Minimal':<15} {'Time Saved':<15} {'% Faster':<10}")
    print("-" * 75)
    
    for size in portfolio_sizes:
        full_mb = (FULL_RESPONSE_SIZE * size) / (1024 * 1024)
        minimal_mb = (MINIMAL_RESPONSE_SIZE * size) / (1024 * 1024)
        
        # Transfer time at 100 Mbps
        network_speed_bytes_per_ms = (100 * 1024 * 1024) / (8 * 1000)
        full_time = (FULL_RESPONSE_SIZE * size) / network_speed_bytes_per_ms / 1000
        minimal_time = (MINIMAL_RESPONSE_SIZE * size) / network_speed_bytes_per_ms / 1000
        time_saved = full_time - minimal_time
        percent_faster = (time_saved / full_time) * 100
        
        print(f"{size:,} bonds{' ':<10} {full_time:>8.2f}s      {minimal_time:>8.2f}s      {time_saved:>8.2f}s      {percent_faster:>6.1f}%")