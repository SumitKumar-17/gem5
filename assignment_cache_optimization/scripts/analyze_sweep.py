#!/usr/bin/env python3
"""
Multi-Parameter Sweep Analysis Script
======================================

Analyzes results from full parameter sweep to identify:
  - Parameter impacts on performance
  - Best configurations for different metrics
  - Parameter interactions
  - Summary statistics

Author: Assignment 1 - Part 3
Date: February 2026
"""

import json
import argparse
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Analyze cache sweep results')
    parser.add_argument('results_file', type=str,
                        help='Path to results.json file')
    parser.add_argument('--output', type=str, default='analysis_plots',
                        help='Output directory for plots')
    return parser.parse_args()

def load_results(filename):
    """Load results from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def compute_summary_stats(results):
    """Compute summary statistics"""
    metrics = ['sim_ticks', 'l1d_hit_rate', 'l2_hit_rate', 'l1d_misses', 'l2_misses']

    stats = {}
    for metric in metrics:
        values = [r[metric] for r in results]
        stats[metric] = {
            'mean': np.mean(values),
            'min': np.min(values),
            'max': np.max(values),
            'std': np.std(values),
            'median': np.median(values)
        }

    return stats

def find_top_configs(results, metric, n=3, minimize=True):
    """Find top N configurations by metric"""
    sorted_results = sorted(results, key=lambda x: x[metric], reverse=not minimize)
    return sorted_results[:n]

def plot_l1d_size_impact(results, output_dir):
    """Plot impact of L1D cache size on performance"""

    # Group by L1D size
    l1d_sizes = sorted(set(r['l1d_size'] for r in results))

    exec_times = []
    hit_rates = []

    for size in l1d_sizes:
        configs = [r for r in results if r['l1d_size'] == size]
        exec_times.append([c['sim_ticks'] for c in configs])
        hit_rates.append([c['l1d_hit_rate'] for c in configs])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Execution time
    positions = range(len(l1d_sizes))
    bp1 = ax1.boxplot(exec_times, positions=positions, labels=l1d_sizes, patch_artist=True)
    for patch in bp1['boxes']:
        patch.set_facecolor('lightblue')

    ax1.set_xlabel('L1D Cache Size', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Execution Time (ticks)', fontsize=12, fontweight='bold')
    ax1.set_title('L1D Size Impact on Execution Time', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.ticklabel_format(style='plain', axis='y')

    # Hit rate
    bp2 = ax2.boxplot(hit_rates, positions=positions, labels=l1d_sizes, patch_artist=True)
    for patch in bp2['boxes']:
        patch.set_facecolor('lightgreen')

    ax2.set_xlabel('L1D Cache Size', fontsize=12, fontweight='bold')
    ax2.set_ylabel('L1D Hit Rate (%)', fontsize=12, fontweight='bold')
    ax2.set_title('L1D Size Impact on L1D Hit Rate', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = f"{output_dir}/l1d_size_impact.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()

def plot_l2_size_impact(results, output_dir):
    """Plot impact of L2 cache size on performance"""

    l2_sizes = sorted(set(r['l2_size'] for r in results), key=lambda x: int(x.replace('kB', '').replace('MB', '000')))

    exec_times = []
    hit_rates = []

    for size in l2_sizes:
        configs = [r for r in results if r['l2_size'] == size]
        exec_times.append([c['sim_ticks'] for c in configs])
        hit_rates.append([c['l2_hit_rate'] for c in configs])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Execution time
    positions = range(len(l2_sizes))
    bp1 = ax1.boxplot(exec_times, positions=positions, labels=l2_sizes, patch_artist=True)
    for patch in bp1['boxes']:
        patch.set_facecolor('lightcoral')

    ax1.set_xlabel('L2 Cache Size', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Execution Time (ticks)', fontsize=12, fontweight='bold')
    ax1.set_title('L2 Size Impact on Execution Time', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.ticklabel_format(style='plain', axis='y')

    # Hit rate
    bp2 = ax2.boxplot(hit_rates, positions=positions, labels=l2_sizes, patch_artist=True)
    for patch in bp2['boxes']:
        patch.set_facecolor('lightyellow')

    ax2.set_xlabel('L2 Cache Size', fontsize=12, fontweight='bold')
    ax2.set_ylabel('L2 Hit Rate (%)', fontsize=12, fontweight='bold')
    ax2.set_title('L2 Size Impact on L2 Hit Rate', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = f"{output_dir}/l2_size_impact.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()

def plot_associativity_impact(results, output_dir):
    """Plot impact of associativity on performance"""

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

    # L1 Associativity impact on execution time
    l1_assocs = sorted(set(r['l1_assoc'] for r in results))
    exec_times_l1 = []
    for assoc in l1_assocs:
        configs = [r for r in results if r['l1_assoc'] == assoc]
        exec_times_l1.append([c['sim_ticks'] for c in configs])

    bp1 = ax1.boxplot(exec_times_l1, labels=l1_assocs, patch_artist=True)
    for patch in bp1['boxes']:
        patch.set_facecolor('lightblue')
    ax1.set_xlabel('L1 Associativity', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Execution Time (ticks)', fontsize=11, fontweight='bold')
    ax1.set_title('L1 Associativity Impact on Performance', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.ticklabel_format(style='plain', axis='y')

    # L2 Associativity impact on execution time
    l2_assocs = sorted(set(r['l2_assoc'] for r in results))
    exec_times_l2 = []
    for assoc in l2_assocs:
        configs = [r for r in results if r['l2_assoc'] == assoc]
        exec_times_l2.append([c['sim_ticks'] for c in configs])

    bp2 = ax2.boxplot(exec_times_l2, labels=l2_assocs, patch_artist=True)
    for patch in bp2['boxes']:
        patch.set_facecolor('lightcoral')
    ax2.set_xlabel('L2 Associativity', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Execution Time (ticks)', fontsize=11, fontweight='bold')
    ax2.set_title('L2 Associativity Impact on Performance', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.ticklabel_format(style='plain', axis='y')

    # L1 Associativity impact on L1D hit rate
    hit_rates_l1 = []
    for assoc in l1_assocs:
        configs = [r for r in results if r['l1_assoc'] == assoc]
        hit_rates_l1.append([c['l1d_hit_rate'] for c in configs])

    bp3 = ax3.boxplot(hit_rates_l1, labels=l1_assocs, patch_artist=True)
    for patch in bp3['boxes']:
        patch.set_facecolor('lightgreen')
    ax3.set_xlabel('L1 Associativity', fontsize=11, fontweight='bold')
    ax3.set_ylabel('L1D Hit Rate (%)', fontsize=11, fontweight='bold')
    ax3.set_title('L1 Associativity Impact on L1D Hit Rate', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')

    # L2 Associativity impact on L2 hit rate
    hit_rates_l2 = []
    for assoc in l2_assocs:
        configs = [r for r in results if r['l2_assoc'] == assoc]
        hit_rates_l2.append([c['l2_hit_rate'] for c in configs])

    bp4 = ax4.boxplot(hit_rates_l2, labels=l2_assocs, patch_artist=True)
    for patch in bp4['boxes']:
        patch.set_facecolor('lightyellow')
    ax4.set_xlabel('L2 Associativity', fontsize=11, fontweight='bold')
    ax4.set_ylabel('L2 Hit Rate (%)', fontsize=11, fontweight='bold')
    ax4.set_title('L2 Associativity Impact on L2 Hit Rate', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = f"{output_dir}/associativity_impact.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()

def plot_performance_distribution(results, output_dir):
    """Plot overall performance distribution"""

    exec_times = [r['sim_ticks'] for r in results]
    l1d_rates = [r['l1d_hit_rate'] for r in results]
    l2_rates = [r['l2_hit_rate'] for r in results]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Execution time histogram
    axes[0].hist(exec_times, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    axes[0].axvline(np.mean(exec_times), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(exec_times):,.0f}')
    axes[0].axvline(np.median(exec_times), color='green', linestyle='--', linewidth=2, label=f'Median: {np.median(exec_times):,.0f}')
    axes[0].set_xlabel('Execution Time (ticks)', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0].set_title('Execution Time Distribution', fontsize=12, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, axis='y')
    axes[0].ticklabel_format(style='plain', axis='x')

    # L1D hit rate histogram
    axes[1].hist(l1d_rates, bins=20, color='lightgreen', edgecolor='black', alpha=0.7)
    axes[1].axvline(np.mean(l1d_rates), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(l1d_rates):.2f}%')
    axes[1].set_xlabel('L1D Hit Rate (%)', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[1].set_title('L1D Hit Rate Distribution', fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis='y')

    # L2 hit rate histogram
    axes[2].hist(l2_rates, bins=20, color='lightcoral', edgecolor='black', alpha=0.7)
    axes[2].axvline(np.mean(l2_rates), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(l2_rates):.2f}%')
    axes[2].set_xlabel('L2 Hit Rate (%)', fontsize=11, fontweight='bold')
    axes[2].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[2].set_title('L2 Hit Rate Distribution', fontsize=12, fontweight='bold')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = f"{output_dir}/performance_distribution.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()

def main():
    args = parse_args()

    print("="*80)
    print("Multi-Parameter Sweep Analysis")
    print("="*80)

    # Load results
    print(f"\nLoading results from: {args.results_file}")
    results = load_results(args.results_file)
    print(f"✓ Loaded {len(results)} configurations")

    # Create output directory
    output_dir = args.output
    if not os.path.isabs(output_dir):
        # Make relative to results file location
        results_dir = os.path.dirname(args.results_file)
        output_dir = os.path.join(results_dir, args.output)

    os.makedirs(output_dir, exist_ok=True)
    print(f"✓ Output directory: {output_dir}")

    # Compute summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)

    stats = compute_summary_stats(results)

    for metric, values in stats.items():
        print(f"\n{metric}:")
        print(f"  Mean:   {values['mean']:,.2f}")
        print(f"  Median: {values['median']:,.2f}")
        print(f"  Min:    {values['min']:,.2f}")
        print(f"  Max:    {values['max']:,.2f}")
        print(f"  Std:    {values['std']:,.2f}")

    # Find top configurations
    print("\n" + "="*80)
    print("TOP 3 CONFIGURATIONS")
    print("="*80)

    print("\n1. Lowest Execution Time:")
    top_perf = find_top_configs(results, 'sim_ticks', n=3, minimize=True)
    for i, config in enumerate(top_perf, 1):
        print(f"  [{i}] {config['config_name']}")
        print(f"      Time: {config['sim_ticks']:,} ticks")
        print(f"      L1D: {config['l1d_size']}, L2: {config['l2_size']}, "
              f"L1A: {config['l1_assoc']}, L2A: {config['l2_assoc']}")
        print(f"      L1D Hit: {config['l1d_hit_rate']:.2f}%, L2 Hit: {config['l2_hit_rate']:.2f}%")

    print("\n2. Highest L1D Hit Rate:")
    top_l1d = find_top_configs(results, 'l1d_hit_rate', n=3, minimize=False)
    for i, config in enumerate(top_l1d, 1):
        print(f"  [{i}] {config['config_name']}")
        print(f"      L1D Hit Rate: {config['l1d_hit_rate']:.2f}%")
        print(f"      Time: {config['sim_ticks']:,} ticks")
        print(f"      L1D: {config['l1d_size']}, L2: {config['l2_size']}")

    print("\n3. Highest L2 Hit Rate:")
    top_l2 = find_top_configs(results, 'l2_hit_rate', n=3, minimize=False)
    for i, config in enumerate(top_l2, 1):
        print(f"  [{i}] {config['config_name']}")
        print(f"      L2 Hit Rate: {config['l2_hit_rate']:.2f}%")
        print(f"      Time: {config['sim_ticks']:,} ticks")
        print(f"      L2: {config['l2_size']}, L2A: {config['l2_assoc']}")

    # Generate plots
    print("\n" + "="*80)
    print("GENERATING PLOTS")
    print("="*80)

    plot_l1d_size_impact(results, output_dir)
    plot_l2_size_impact(results, output_dir)
    plot_associativity_impact(results, output_dir)
    plot_performance_distribution(results, output_dir)

    print("\n✓ All plots generated successfully!")
    print("="*80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
