#!/usr/bin/env python3
"""
Plot Generation Script for Cache Parameter Sweep Results
=========================================================

Generates visualization plots for L2 cache size sweep analysis:
1. L2 Cache Size vs Execution Time
2. L2 Cache Size vs Cache Hit Rates

 * Team Members: Sumit Kumar(22CS30056) and Aviral Singh(22CS30015)
 * Assignment 1 - Cache Hierarchy Optimization Part 2
"""

import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import numpy as np
import os

# Configuration
RESULTS_FILE = "assignment_cache_optimization/results/single_param_sweep/results.json"
OUTPUT_DIR = "assignment_cache_optimization/results/single_param_sweep"

def load_results():
    """Load results from JSON file"""
    with open(RESULTS_FILE, 'r') as f:
        return json.load(f)

def convert_size_to_kb(size_str):
    """Convert size string to KB for plotting"""
    size_str = size_str.replace('kB', '').replace('KB', '').replace('KiB', '')
    if 'MB' in size_str or 'MiB' in size_str:
        size_str = size_str.replace('MB', '').replace('MiB', '')
        return int(size_str) * 1024
    return int(size_str)

def plot_execution_time(results):
    """Plot L2 Cache Size vs Execution Time"""

    l2_sizes = [convert_size_to_kb(r['l2_size']) for r in results]
    exec_times = [r['sim_ticks'] / 1e9 for r in results]  # Convert to billions of ticks

    plt.figure(figsize=(10, 6))
    plt.plot(l2_sizes, exec_times, 'bo-', linewidth=2, markersize=10, label='Execution Time')
    plt.xlabel('L2 Cache Size (KB)', fontsize=12, fontweight='bold')
    plt.ylabel('Execution Time (Billion Ticks)', fontsize=12, fontweight='bold')
    plt.title('L2 Cache Size vs Execution Time\nMatrix Multiplication (64x64)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xticks(l2_sizes, [r['l2_size'] for r in results])

    # Add value labels on points
    for i, (x, y) in enumerate(zip(l2_sizes, exec_times)):
        plt.annotate(f'{y:.3f}B', (x, y), textcoords="offset points",
                     xytext=(0, 10), ha='center', fontsize=9)

    # Calculate and show improvement
    if len(exec_times) > 1:
        improvement = ((exec_times[0] - exec_times[-1]) / exec_times[0]) * 100
        plt.text(0.5, 0.95, f'Performance improvement (128kB→1MB): {improvement:.3f}%',
                 transform=plt.gca().transAxes, ha='center', va='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    output_file = f"{OUTPUT_DIR}/plot_execution_time.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_hit_rates(results):
    """Plot L2 Cache Size vs Cache Hit Rates"""

    l2_sizes = [convert_size_to_kb(r['l2_size']) for r in results]
    l1i_rates = [r['l1i_hit_rate'] for r in results]
    l1d_rates = [r['l1d_hit_rate'] for r in results]
    l2_rates = [r['l2_hit_rate'] for r in results]

    plt.figure(figsize=(12, 7))

    # Plot each cache level
    plt.plot(l2_sizes, l1i_rates, 'gs-', linewidth=2, markersize=8, label='L1I Hit Rate')
    plt.plot(l2_sizes, l1d_rates, 'r^-', linewidth=2, markersize=8, label='L1D Hit Rate')
    plt.plot(l2_sizes, l2_rates, 'bo-', linewidth=2, markersize=8, label='L2 Hit Rate')

    plt.xlabel('L2 Cache Size (KB)', fontsize=12, fontweight='bold')
    plt.ylabel('Hit Rate (%)', fontsize=12, fontweight='bold')
    plt.title('L2 Cache Size vs Cache Hit Rates\nMatrix Multiplication (64x64)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xticks(l2_sizes, [r['l2_size'] for r in results])
    plt.ylim([85, 100.5])  # Focus on the relevant range
    plt.legend(loc='lower right', fontsize=11)

    # Add value labels for L2 hit rate (most interesting)
    for i, (x, y) in enumerate(zip(l2_sizes, l2_rates)):
        plt.annotate(f'{y:.2f}%', (x, y), textcoords="offset points",
                     xytext=(0, -15), ha='center', fontsize=8)

    plt.tight_layout()
    output_file = f"{OUTPUT_DIR}/plot_hit_rates.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_combined_metrics(results):
    """Create a combined plot showing multiple metrics"""

    l2_sizes = [convert_size_to_kb(r['l2_size']) for r in results]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Left plot: Execution time
    exec_times = [r['sim_ticks'] / 1e9 for r in results]
    ax1.plot(l2_sizes, exec_times, 'bo-', linewidth=2, markersize=10)
    ax1.set_xlabel('L2 Cache Size (KB)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Execution Time (Billion Ticks)', fontsize=12, fontweight='bold')
    ax1.set_title('Execution Time vs L2 Size', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(l2_sizes)
    ax1.set_xticklabels([r['l2_size'] for r in results])

    for i, (x, y) in enumerate(zip(l2_sizes, exec_times)):
        ax1.annotate(f'{y:.3f}', (x, y), textcoords="offset points",
                     xytext=(0, 10), ha='center', fontsize=9)

    # Right plot: L2 hit rate
    l2_rates = [r['l2_hit_rate'] for r in results]
    l2_misses = [r['l2_misses'] for r in results]

    ax2_twin = ax2.twinx()

    # Bar chart for L2 misses
    bars = ax2.bar(l2_sizes, l2_misses, color='coral', alpha=0.6, width=80, label='L2 Misses')
    ax2.set_xlabel('L2 Cache Size (KB)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('L2 Cache Misses', fontsize=12, fontweight='bold', color='coral')
    ax2.tick_params(axis='y', labelcolor='coral')
    ax2.set_xticks(l2_sizes)
    ax2.set_xticklabels([r['l2_size'] for r in results])

    # Line plot for L2 hit rate
    line = ax2_twin.plot(l2_sizes, l2_rates, 'go-', linewidth=2, markersize=10, label='L2 Hit Rate')
    ax2_twin.set_ylabel('L2 Hit Rate (%)', fontsize=12, fontweight='bold', color='green')
    ax2_twin.tick_params(axis='y', labelcolor='green')
    ax2_twin.set_ylim([90, 94])

    ax2.set_title('L2 Misses and Hit Rate vs L2 Size', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')

    # Add value labels
    for i, (x, y) in enumerate(zip(l2_sizes, l2_rates)):
        ax2_twin.annotate(f'{y:.2f}%', (x, y), textcoords="offset points",
                          xytext=(0, 10), ha='center', fontsize=9, color='green')

    plt.tight_layout()
    output_file = f"{OUTPUT_DIR}/plot_combined.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def print_analysis_data(results):
    """Print statistical analysis of the results"""

    print("\n" + "="*70)
    print("STATISTICAL ANALYSIS")
    print("="*70)

    exec_times = [r['sim_ticks'] for r in results]
    l2_hit_rates = [r['l2_hit_rate'] for r in results]

    print(f"\nExecution Time Statistics:")
    print(f"  Minimum: {min(exec_times):,} ticks ({results[exec_times.index(min(exec_times))]['l2_size']})")
    print(f"  Maximum: {max(exec_times):,} ticks ({results[exec_times.index(max(exec_times))]['l2_size']})")
    print(f"  Difference: {max(exec_times) - min(exec_times):,} ticks")
    print(f"  % Improvement (128kB→1MB): {((exec_times[0] - exec_times[-1]) / exec_times[0]) * 100:.4f}%")

    print(f"\nL2 Hit Rate Statistics:")
    print(f"  Minimum: {min(l2_hit_rates):.2f}% ({results[l2_hit_rates.index(min(l2_hit_rates))]['l2_size']})")
    print(f"  Maximum: {max(l2_hit_rates):.2f}% ({results[l2_hit_rates.index(max(l2_hit_rates))]['l2_size']})")
    print(f"  Range: {max(l2_hit_rates) - min(l2_hit_rates):.2f}%")

    print(f"\nPerformance Saturation Analysis:")
    # Check where performance saturates
    for i in range(len(exec_times) - 1):
        diff = exec_times[i] - exec_times[i+1]
        pct_diff = (diff / exec_times[i]) * 100
        print(f"  {results[i]['l2_size']} → {results[i+1]['l2_size']}: {diff:,} ticks ({pct_diff:.4f}% improvement)")

    if exec_times[1] == exec_times[-1]:
        print(f"\n✓ Performance saturates at {results[1]['l2_size']}")

    print("="*70)

def main():
    print("="*70)
    print("Generating plots for L2 cache size sweep...")
    print("="*70)

    # Load results
    results = load_results()
    print(f"✓ Loaded {len(results)} results from {RESULTS_FILE}")

    # Generate plots
    plot_execution_time(results)
    plot_hit_rates(results)
    plot_combined_metrics(results)

    # Print analysis
    print_analysis_data(results)

    print("\n✓ All plots generated successfully!")
    print(f"Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
