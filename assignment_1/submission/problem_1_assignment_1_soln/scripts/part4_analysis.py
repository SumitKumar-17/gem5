#!/usr/bin/env python3
"""
Part 4: Design Analysis & Recommendations
==========================================

This script generates additional analysis and visualizations for Part 4,
including Pareto-optimal configuration identification and comparison plots.

Author: gem5 Assignment
Date: February 4, 2026
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

# Plot styling
plt.style.use('seaborn-v0_8-darkgrid')
COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4B51']


def load_results(json_file):
    """Load results from JSON file"""
    with open(json_file, 'r') as f:
        return json.load(f)


def convert_size_to_kb(size_str):
    """Convert size string to numeric KB value"""
    if size_str.endswith('kB') or size_str.endswith('KB'):
        return int(size_str[:-2])
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024
    return int(size_str)


def identify_pareto_optimal(df):
    """
    Identify Pareto-optimal configurations based on:
    - Minimize execution time
    - Minimize total cache size
    """
    # Calculate total cache size
    df['total_cache_kb'] = df.apply(
        lambda row: convert_size_to_kb(row['l1d_size']) +
                    convert_size_to_kb(row['l2_size']) + 16,  # +16 for L1I
        axis=1
    )

    # Sort by cache size
    sorted_df = df.sort_values('total_cache_kb').copy()

    pareto_configs = []
    min_exec_time = float('inf')

    for idx, row in sorted_df.iterrows():
        exec_time = row['simTicks']
        if exec_time < min_exec_time:
            pareto_configs.append(idx)
            min_exec_time = exec_time

    df['is_pareto'] = False
    df.loc[pareto_configs, 'is_pareto'] = True

    return df, df[df['is_pareto']].copy()


def plot_pareto_comparison(df, pareto_df, output_dir):
    """Plot Pareto-optimal vs suboptimal configurations"""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Plot 1: Execution Time vs Total Cache Size (Pareto frontier)
    exec_times = df['simTicks'].values / 1e9
    cache_sizes = df['total_cache_kb'].values

    # Non-Pareto configs
    non_pareto = df[~df['is_pareto']]
    ax1.scatter(non_pareto['total_cache_kb'], non_pareto['simTicks']/1e9,
               c='lightgray', s=80, alpha=0.5, label='Suboptimal', zorder=1)

    # Pareto configs
    ax1.scatter(pareto_df['total_cache_kb'], pareto_df['simTicks']/1e9,
               c=COLORS[0], s=200, marker='*', edgecolors='black',
               linewidth=1.5, label='Pareto Optimal', zorder=3)

    # Connect Pareto points
    pareto_sorted = pareto_df.sort_values('total_cache_kb')
    ax1.plot(pareto_sorted['total_cache_kb'], pareto_sorted['simTicks']/1e9,
            'r--', linewidth=2.5, alpha=0.7, zorder=2)

    ax1.set_xlabel('Total Cache Size (KB)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Execution Time (Billion Ticks)', fontsize=12, fontweight='bold')
    ax1.set_title('Pareto Frontier: Performance vs Cache Size', fontsize=13, fontweight='bold')
    ax1.legend(loc='best', fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Annotate Pareto points
    for idx, row in pareto_df.iterrows():
        ax1.annotate(f"{row['total_cache_kb']}KB\n{row['simTicks']/1e9:.1f}B",
                    xy=(row['total_cache_kb'], row['simTicks']/1e9),
                    xytext=(10, -15), textcoords='offset points',
                    fontsize=8, bbox=dict(boxstyle='round,pad=0.3',
                    facecolor='yellow', alpha=0.7))

    # Plot 2: Performance improvement vs Cache size increase
    baseline = df['simTicks'].max()
    df['speedup'] = ((baseline - df['simTicks']) / baseline) * 100
    pareto_df['speedup'] = ((baseline - pareto_df['simTicks']) / baseline) * 100

    pareto_sorted = pareto_df.sort_values('total_cache_kb')
    cache_sizes_pareto = pareto_sorted['total_cache_kb'].values
    speedups = pareto_sorted['speedup'].values

    ax2.plot(cache_sizes_pareto, speedups, marker='o', linewidth=2.5,
            markersize=10, color=COLORS[1], label='Pareto Optimal Configs')

    # Mark 90% of peak performance
    peak_speedup = speedups.max()
    target_90 = peak_speedup * 0.9
    ax2.axhline(target_90, color='green', linestyle='--', linewidth=2,
               label=f'90% of Peak ({target_90:.1f}%)')

    # Find config achieving 90%
    idx_90 = np.where(speedups >= target_90)[0][0] if any(speedups >= target_90) else -1
    if idx_90 >= 0:
        ax2.scatter([cache_sizes_pareto[idx_90]], [speedups[idx_90]],
                   c='green', s=300, marker='*', edgecolors='black',
                   linewidth=2, zorder=5, label=f'90% Target: {cache_sizes_pareto[idx_90]}KB')

    ax2.set_xlabel('Total Cache Size (KB)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Speedup over Baseline (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Speedup vs Cache Size (Pareto Optimal)', fontsize=13, fontweight='bold')
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    output_file = os.path.join(output_dir, 'pareto_optimal_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved: {output_file}")
    plt.close()


def plot_design_recommendations(df, output_dir):
    """Create visualization of recommended configurations"""

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Get recommended configurations
    # Power-constrained: Smallest cache achieving near-optimal performance
    df['total_cache_kb'] = df.apply(
        lambda row: convert_size_to_kb(row['l1d_size']) +
                    convert_size_to_kb(row['l2_size']) + 16,
        axis=1
    )

    best_time = df['simTicks'].min()
    threshold_90 = best_time * 1.11  # Within 10% of best (inverse)

    candidates_90 = df[df['simTicks'] <= threshold_90].copy()
    power_config = candidates_90.nsmallest(1, 'total_cache_kb').iloc[0]

    # High-performance: Best execution time
    perf_config = df.nsmallest(1, 'simTicks').iloc[0]

    # Balanced: Best performance/cost ratio
    df['perf_per_kb'] = (1 / df['simTicks']) / df['total_cache_kb']
    balanced_config = df.nlargest(1, 'perf_per_kb').iloc[0]

    # Cost-optimized: Smallest total cache
    cost_config = df.nsmallest(1, 'total_cache_kb').iloc[0]

    configs = [power_config, perf_config, balanced_config, cost_config]
    labels = ['Power-\nConstrained', 'High-\nPerformance', 'Balanced', 'Cost-\nOptimized']

    # Plot 1: Execution Time Comparison
    exec_times = [c['simTicks']/1e9 for c in configs]
    bars1 = ax1.bar(labels, exec_times, color=[COLORS[0], COLORS[1], COLORS[2], COLORS[3]], alpha=0.7)
    ax1.set_ylabel('Execution Time (Billion Ticks)', fontsize=11, fontweight='bold')
    ax1.set_title('Execution Time by Design Type', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')

    for i, (bar, val) in enumerate(zip(bars1, exec_times)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val:.2f}B', ha='center', va='bottom', fontweight='bold')

    # Plot 2: Cache Size Comparison
    cache_sizes = [c['total_cache_kb'] for c in configs]
    bars2 = ax2.bar(labels, cache_sizes, color=[COLORS[0], COLORS[1], COLORS[2], COLORS[3]], alpha=0.7)
    ax2.set_ylabel('Total Cache Size (KB)', fontsize=11, fontweight='bold')
    ax2.set_title('Cache Size by Design Type', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    for i, (bar, val) in enumerate(zip(bars2, cache_sizes)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 10,
                f'{int(val)}KB', ha='center', va='bottom', fontweight='bold')

    # Plot 3: L1D Hit Rate Comparison
    l1d_hits = [c['l1d_hit_rate']*100 for c in configs]
    bars3 = ax3.bar(labels, l1d_hits, color=[COLORS[0], COLORS[1], COLORS[2], COLORS[3]], alpha=0.7)
    ax3.set_ylabel('L1D Hit Rate (%)', fontsize=11, fontweight='bold')
    ax3.set_title('L1D Hit Rate by Design Type', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_ylim([0, 105])

    for i, (bar, val) in enumerate(zip(bars3, l1d_hits)):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')

    # Plot 4: Performance per KB (efficiency)
    efficiency = [(1/c['simTicks']) / c['total_cache_kb'] * 1e12 for c in configs]
    bars4 = ax4.bar(labels, efficiency, color=[COLORS[0], COLORS[1], COLORS[2], COLORS[3]], alpha=0.7)
    ax4.set_ylabel('Performance per KB (×10¹²)', fontsize=11, fontweight='bold')
    ax4.set_title('Cache Efficiency by Design Type', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')

    for i, (bar, val) in enumerate(zip(bars4, efficiency)):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + max(efficiency)*0.02,
                f'{val:.1f}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    output_file = os.path.join(output_dir, 'design_recommendations_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved: {output_file}")
    plt.close()

    return {
        'power': power_config,
        'performance': perf_config,
        'balanced': balanced_config,
        'cost': cost_config
    }


def main():
    """Main execution function"""

    # Load full sweep results
    full_results_file = "assignment_cache_optimization/results/full_sweep_results/results.json"
    output_dir = "assignment_cache_optimization/results/full_sweep_results"

    print("\n" + "="*70)
    print("Part 4: Design Analysis & Recommendations")
    print("="*70 + "\n")

    print("Loading results...")
    results = load_results(full_results_file)
    df = pd.DataFrame(results)
    print(f"✓ Loaded {len(df)} configurations\n")

    # Identify Pareto-optimal configurations
    print("Identifying Pareto-optimal configurations...")
    df, pareto_df = identify_pareto_optimal(df)
    print(f"✓ Found {len(pareto_df)} Pareto-optimal configurations\n")

    print("Pareto-Optimal Configurations:")
    print("-" * 70)
    for idx, row in pareto_df.sort_values('total_cache_kb').iterrows():
        print(f"  {row['config_name']}")
        print(f"    Total Cache: {row['total_cache_kb']}KB")
        print(f"    Exec Time: {row['simTicks']/1e9:.2f}B ticks")
        print(f"    L1D Hit: {row['l1d_hit_rate']*100:.1f}%, L2 Hit: {row['l2_hit_rate']*100:.1f}%")
        print()

    # Generate plots
    print("Generating plots...")
    plot_pareto_comparison(df, pareto_df, output_dir)
    recommended_configs = plot_design_recommendations(df, output_dir)

    print("\n" + "="*70)
    print("✓ Part 4 analysis complete!")
    print("="*70 + "\n")

    print("Recommended Configurations:")
    print("-" * 70)
    for design_type, config in recommended_configs.items():
        print(f"\n{design_type.upper()}:")
        print(f"  Config: {config['config_name']}")
        print(f"  Total Cache: {config['total_cache_kb']}KB")
        print(f"  Exec Time: {config['simTicks']/1e9:.2f}B ticks")
        print(f"  L1D Hit Rate: {config['l1d_hit_rate']*100:.1f}%")
        print(f"  L2 Hit Rate: {config['l2_hit_rate']*100:.1f}%")


if __name__ == "__main__":
    main()
