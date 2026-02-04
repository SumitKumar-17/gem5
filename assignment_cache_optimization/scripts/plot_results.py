#!/usr/bin/env python3
"""
Plot Generation Script for Parameter Sweep Results
==================================================

This script generates plots from the parameter sweep results:
1. Execution Time vs Parameter Value
2. Hit Rate vs Parameter Value

Author: gem5 Assignment
Date: February 4, 2026
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import os

# Configuration
RESULTS_FILE = "assignment_cache_optimization/results/single_param_sweep/results.json"
OUTPUT_DIR = "assignment_cache_optimization/results/single_param_sweep"

# Plot styling
plt.style.use('seaborn-v0_8-darkgrid')
COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']


def load_results():
    """Load results from JSON file"""
    with open(RESULTS_FILE, 'r') as f:
        return json.load(f)


def convert_size_to_kb(size_str):
    """Convert size string to numeric KB value"""
    if size_str.endswith('kB'):
        return int(size_str[:-2])
    elif size_str.endswith('KB'):
        return int(size_str[:-2])
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024
    return int(size_str)


def plot_execution_time(results):
    """Generate plot: Execution Time vs L1D Cache Size"""

    # Extract data
    sizes = [convert_size_to_kb(r['value']) for r in results]
    ticks = [r['simTicks'] / 1e9 for r in results]  # Convert to billions

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot data
    ax.plot(sizes, ticks, marker='o', linewidth=2.5, markersize=10,
            color=COLORS[0], label='Execution Time')

    # Add value labels
    for i, (x, y) in enumerate(zip(sizes, ticks)):
        ax.annotate(f'{y:.1f}B',
                   xy=(x, y),
                   xytext=(0, 10),
                   textcoords='offset points',
                   ha='center',
                   fontsize=10,
                   fontweight='bold')

    # Styling
    ax.set_xlabel('L1D Cache Size (KB)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Execution Time (Billion Ticks)', fontsize=12, fontweight='bold')
    ax.set_title('Impact of L1D Cache Size on Execution Time\n(Matrix Multiply 128×128)',
                fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(sizes)
    ax.set_xticklabels([f'{s}KB' for s in sizes])

    # Add speedup annotations
    baseline = ticks[0]
    for i in range(1, len(ticks)):
        speedup = ((baseline - ticks[i]) / baseline) * 100
        if speedup > 1:  # Only show significant speedups
            ax.annotate(f'↓{speedup:.1f}%',
                       xy=(sizes[i], ticks[i]),
                       xytext=(0, -25),
                       textcoords='offset points',
                       ha='center',
                       fontsize=9,
                       color='green',
                       fontweight='bold')

    plt.tight_layout()

    # Save plot
    output_file = os.path.join(OUTPUT_DIR, 'plot_execution_time.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved: {output_file}")

    plt.close()


def plot_hit_rates(results):
    """Generate plot: Hit Rates vs L1D Cache Size"""

    # Extract data
    sizes = [convert_size_to_kb(r['value']) for r in results]
    l1d_hit_rates = [r['l1d_hit_rate'] * 100 for r in results]
    l2_hit_rates = [r['l2_hit_rate'] * 100 for r in results]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot data
    line1 = ax.plot(sizes, l1d_hit_rates, marker='o', linewidth=2.5, markersize=10,
                    color=COLORS[1], label='L1D Hit Rate')
    line2 = ax.plot(sizes, l2_hit_rates, marker='s', linewidth=2.5, markersize=10,
                    color=COLORS[2], label='L2 Hit Rate', linestyle='--')

    # Add value labels for L1D
    for i, (x, y) in enumerate(zip(sizes, l1d_hit_rates)):
        ax.annotate(f'{y:.1f}%',
                   xy=(x, y),
                   xytext=(0, 10),
                   textcoords='offset points',
                   ha='center',
                   fontsize=9,
                   fontweight='bold',
                   color=COLORS[1])

    # Add value labels for L2
    for i, (x, y) in enumerate(zip(sizes, l2_hit_rates)):
        ax.annotate(f'{y:.1f}%',
                   xy=(x, y),
                   xytext=(0, -20),
                   textcoords='offset points',
                   ha='center',
                   fontsize=9,
                   fontweight='bold',
                   color=COLORS[2])

    # Styling
    ax.set_xlabel('L1D Cache Size (KB)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Hit Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Impact of L1D Cache Size on Cache Hit Rates\n(Matrix Multiply 128×128)',
                fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(sizes)
    ax.set_xticklabels([f'{s}KB' for s in sizes])
    ax.set_ylim([0, 105])
    ax.legend(loc='best', fontsize=11, frameon=True, shadow=True)

    plt.tight_layout()

    # Save plot
    output_file = os.path.join(OUTPUT_DIR, 'plot_hit_rates.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved: {output_file}")

    plt.close()


def plot_combined(results):
    """Generate combined plot with dual y-axes"""

    # Extract data
    sizes = [convert_size_to_kb(r['value']) for r in results]
    ticks = [r['simTicks'] / 1e9 for r in results]
    l1d_hit_rates = [r['l1d_hit_rate'] * 100 for r in results]

    # Create figure with dual y-axes
    fig, ax1 = plt.subplots(figsize=(12, 7))

    # Plot execution time on left axis
    color1 = COLORS[0]
    ax1.set_xlabel('L1D Cache Size (KB)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Execution Time (Billion Ticks)', fontsize=12, fontweight='bold', color=color1)
    line1 = ax1.plot(sizes, ticks, marker='o', linewidth=2.5, markersize=12,
                    color=color1, label='Execution Time')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3)

    # Create second y-axis for hit rate
    ax2 = ax1.twinx()
    color2 = COLORS[1]
    ax2.set_ylabel('L1D Hit Rate (%)', fontsize=12, fontweight='bold', color=color2)
    line2 = ax2.plot(sizes, l1d_hit_rates, marker='s', linewidth=2.5, markersize=12,
                    color=color2, label='L1D Hit Rate', linestyle='--')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim([0, 105])

    # Title
    ax1.set_title('L1D Cache Size Impact: Execution Time vs Hit Rate\n(Matrix Multiply 128×128)',
                 fontsize=14, fontweight='bold', pad=20)

    # X-axis
    ax1.set_xticks(sizes)
    ax1.set_xticklabels([f'{s}KB' for s in sizes])

    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center right', fontsize=11, frameon=True, shadow=True)

    plt.tight_layout()

    # Save plot
    output_file = os.path.join(OUTPUT_DIR, 'plot_combined.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved: {output_file}")

    plt.close()


def main():
    """Main execution function"""

    print("\n" + "="*70)
    print("Plot Generation Script")
    print("="*70 + "\n")

    # Load results
    print(f"Loading results from: {RESULTS_FILE}")
    results = load_results()
    print(f"✓ Loaded {len(results)} data points\n")

    # Generate plots
    print("Generating plots...")
    plot_execution_time(results)
    plot_hit_rates(results)
    plot_combined(results)

    print("\n" + "="*70)
    print("✓ All plots generated successfully!")
    print("="*70 + "\n")

    print(f"Output directory: {OUTPUT_DIR}/")
    print("Generated files:")
    print("  - plot_execution_time.png")
    print("  - plot_hit_rates.png")
    print("  - plot_combined.png\n")


if __name__ == "__main__":
    main()
