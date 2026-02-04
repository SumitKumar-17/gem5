#!/usr/bin/env python3
"""
Analysis Script for Multi-Parameter Sweep Results
==================================================

This script analyzes the results from a full parameter sweep and generates:
- Multiple plots showing impact of each parameter
- Parameter interaction heatmaps
- Performance distribution plots
- Pareto frontier analysis
- Summary statistics
- Top configurations by various metrics

Author: gem5 Assignment
Date: February 4, 2026
"""

import json
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

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


def plot_l1d_impact(df, output_dir):
    """Plot impact of L1D cache size on performance"""

    # Group by L1D size
    grouped = df.groupby('l1d_size').agg({
        'simTicks': ['mean', 'std', 'min', 'max'],
        'l1d_hit_rate': ['mean', 'std', 'min', 'max']
    })

    # Convert sizes to numeric for plotting
    sizes = [convert_size_to_kb(s) for s in grouped.index]
    exec_mean = grouped['simTicks']['mean'].values / 1e9
    exec_std = grouped['simTicks']['std'].values / 1e9
    hit_mean = grouped['l1d_hit_rate']['mean'].values * 100

    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Execution Time
    ax1.errorbar(sizes, exec_mean, yerr=exec_std, marker='o', markersize=10,
                linewidth=2.5, capsize=5, color=COLORS[0], label='Mean ± Std')
    ax1.set_xlabel('L1D Cache Size (KB)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Execution Time (Billion Ticks)', fontsize=12, fontweight='bold')
    ax1.set_title('L1D Size Impact on Execution Time', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(sizes)
    ax1.set_xticklabels([f'{s}KB' for s in sizes])

    # Plot 2: Hit Rate
    ax2.bar(sizes, hit_mean, color=COLORS[1], alpha=0.7, width=[s*0.1 for s in sizes])
    ax2.set_xlabel('L1D Cache Size (KB)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('L1D Hit Rate (%)', fontsize=12, fontweight='bold')
    ax2.set_title('L1D Size Impact on Hit Rate', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_xticks(sizes)
    ax2.set_xticklabels([f'{s}KB' for s in sizes])
    ax2.set_ylim([0, 105])

    # Add value labels
    for i, (x, y) in enumerate(zip(sizes, hit_mean)):
        ax2.text(x, y + 2, f'{y:.1f}%', ha='center', fontweight='bold')

    plt.tight_layout()
    output_file = os.path.join(output_dir, 'l1d_size_impact.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved: {output_file}")
    plt.close()


def plot_l2_impact(df, output_dir):
    """Plot impact of L2 cache size on performance"""

    # Group by L2 size
    grouped = df.groupby('l2_size').agg({
        'simTicks': ['mean', 'std'],
        'l2_hit_rate': ['mean', 'std']
    })

    # Convert sizes to numeric for plotting
    sizes = [convert_size_to_kb(s) for s in grouped.index]
    exec_mean = grouped['simTicks']['mean'].values / 1e9
    exec_std = grouped['simTicks']['std'].values / 1e9
    hit_mean = grouped['l2_hit_rate']['mean'].values * 100

    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Execution Time
    ax1.errorbar(sizes, exec_mean, yerr=exec_std, marker='s', markersize=10,
                linewidth=2.5, capsize=5, color=COLORS[2], label='Mean ± Std')
    ax1.set_xlabel('L2 Cache Size (KB)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Execution Time (Billion Ticks)', fontsize=12, fontweight='bold')
    ax1.set_title('L2 Size Impact on Execution Time', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(sizes)
    ax1.set_xticklabels([f'{s}KB' if s < 1024 else f'{s//1024}MB' for s in sizes])

    # Plot 2: Hit Rate
    ax2.bar(range(len(sizes)), hit_mean, color=COLORS[3], alpha=0.7)
    ax2.set_xlabel('L2 Cache Size (KB)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('L2 Hit Rate (%)', fontsize=12, fontweight='bold')
    ax2.set_title('L2 Size Impact on Hit Rate', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_xticks(range(len(sizes)))
    ax2.set_xticklabels([f'{s}KB' if s < 1024 else f'{s//1024}MB' for s in sizes])
    ax2.set_ylim([0, 105])

    # Add value labels
    for i, y in enumerate(hit_mean):
        ax2.text(i, y + 2, f'{y:.1f}%', ha='center', fontweight='bold')

    plt.tight_layout()
    output_file = os.path.join(output_dir, 'l2_size_impact.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved: {output_file}")
    plt.close()


def plot_associativity_impact(df, output_dir):
    """Plot impact of cache associativity on performance"""

    # Create figure with 2x2 subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

    # L1 Associativity - Execution Time
    grouped = df.groupby('l1_assoc').agg({'simTicks': 'mean'})
    assoc = grouped.index.values
    exec_time = grouped['simTicks'].values / 1e9
    ax1.bar(assoc, exec_time, color=COLORS[4], alpha=0.7)
    ax1.set_xlabel('L1 Associativity', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Execution Time (Billion Ticks)', fontsize=11, fontweight='bold')
    ax1.set_title('L1 Associativity Impact on Execution Time', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_xticks(assoc)
    for i, (x, y) in enumerate(zip(assoc, exec_time)):
        ax1.text(x, y + max(exec_time)*0.02, f'{y:.1f}B', ha='center', fontsize=9, fontweight='bold')

    # L1 Associativity - Hit Rate
    grouped = df.groupby('l1_assoc').agg({'l1d_hit_rate': 'mean'})
    hit_rate = grouped['l1d_hit_rate'].values * 100
    ax2.bar(assoc, hit_rate, color=COLORS[5], alpha=0.7)
    ax2.set_xlabel('L1 Associativity', fontsize=11, fontweight='bold')
    ax2.set_ylabel('L1D Hit Rate (%)', fontsize=11, fontweight='bold')
    ax2.set_title('L1 Associativity Impact on L1D Hit Rate', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_xticks(assoc)
    ax2.set_ylim([0, 105])
    for i, (x, y) in enumerate(zip(assoc, hit_rate)):
        ax2.text(x, y + 2, f'{y:.1f}%', ha='center', fontsize=9, fontweight='bold')

    # L2 Associativity - Execution Time
    grouped = df.groupby('l2_assoc').agg({'simTicks': 'mean'})
    assoc = grouped.index.values
    exec_time = grouped['simTicks'].values / 1e9
    ax3.bar(assoc, exec_time, color=COLORS[4], alpha=0.7)
    ax3.set_xlabel('L2 Associativity', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Execution Time (Billion Ticks)', fontsize=11, fontweight='bold')
    ax3.set_title('L2 Associativity Impact on Execution Time', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_xticks(assoc)
    for i, (x, y) in enumerate(zip(assoc, exec_time)):
        ax3.text(x, y + max(exec_time)*0.02, f'{y:.1f}B', ha='center', fontsize=9, fontweight='bold')

    # L2 Associativity - Hit Rate
    grouped = df.groupby('l2_assoc').agg({'l2_hit_rate': 'mean'})
    hit_rate = grouped['l2_hit_rate'].values * 100
    ax4.bar(assoc, hit_rate, color=COLORS[5], alpha=0.7)
    ax4.set_xlabel('L2 Associativity', fontsize=11, fontweight='bold')
    ax4.set_ylabel('L2 Hit Rate (%)', fontsize=11, fontweight='bold')
    ax4.set_title('L2 Associativity Impact on L2 Hit Rate', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.set_xticks(assoc)
    ax4.set_ylim([0, 105])
    for i, (x, y) in enumerate(zip(assoc, hit_rate)):
        ax4.text(x, y + 2, f'{y:.1f}%', ha='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    output_file = os.path.join(output_dir, 'associativity_impact.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved: {output_file}")
    plt.close()


def plot_parameter_heatmaps(df, output_dir):
    """Create heatmaps showing parameter interactions"""

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Heatmap 1: L1D Size vs L2 Size (Execution Time)
    pivot = df.pivot_table(values='simTicks', index='l1d_size', columns='l2_size', aggfunc='mean')
    pivot = pivot / 1e9  # Convert to billions
    im1 = ax1.imshow(pivot.values, cmap='RdYlGn_r', aspect='auto')
    ax1.set_xticks(range(len(pivot.columns)))
    ax1.set_yticks(range(len(pivot.index)))
    ax1.set_xticklabels([f'{convert_size_to_kb(s)}KB' if convert_size_to_kb(s) < 1024 else f'{convert_size_to_kb(s)//1024}MB' for s in pivot.columns])
    ax1.set_yticklabels([f'{convert_size_to_kb(s)}KB' for s in pivot.index])
    ax1.set_xlabel('L2 Size', fontsize=11, fontweight='bold')
    ax1.set_ylabel('L1D Size', fontsize=11, fontweight='bold')
    ax1.set_title('Execution Time: L1D vs L2 Size\n(Billion Ticks)', fontsize=12, fontweight='bold')

    # Add text annotations
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            text = ax1.text(j, i, f'{pivot.values[i, j]:.1f}',
                           ha="center", va="center", color="black", fontsize=8)

    plt.colorbar(im1, ax=ax1, label='Billion Ticks')

    # Heatmap 2: L1D Size vs L2 Size (L1D Hit Rate)
    pivot = df.pivot_table(values='l1d_hit_rate', index='l1d_size', columns='l2_size', aggfunc='mean')
    pivot = pivot * 100  # Convert to percentage
    im2 = ax2.imshow(pivot.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
    ax2.set_xticks(range(len(pivot.columns)))
    ax2.set_yticks(range(len(pivot.index)))
    ax2.set_xticklabels([f'{convert_size_to_kb(s)}KB' if convert_size_to_kb(s) < 1024 else f'{convert_size_to_kb(s)//1024}MB' for s in pivot.columns])
    ax2.set_yticklabels([f'{convert_size_to_kb(s)}KB' for s in pivot.index])
    ax2.set_xlabel('L2 Size', fontsize=11, fontweight='bold')
    ax2.set_ylabel('L1D Size', fontsize=11, fontweight='bold')
    ax2.set_title('L1D Hit Rate: L1D vs L2 Size\n(%)', fontsize=12, fontweight='bold')

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            text = ax2.text(j, i, f'{pivot.values[i, j]:.1f}',
                           ha="center", va="center", color="black", fontsize=8)

    plt.colorbar(im2, ax=ax2, label='Hit Rate (%)')

    # Heatmap 3: L1 Assoc vs L2 Assoc (Execution Time)
    pivot = df.pivot_table(values='simTicks', index='l1_assoc', columns='l2_assoc', aggfunc='mean')
    pivot = pivot / 1e9
    im3 = ax3.imshow(pivot.values, cmap='RdYlGn_r', aspect='auto')
    ax3.set_xticks(range(len(pivot.columns)))
    ax3.set_yticks(range(len(pivot.index)))
    ax3.set_xticklabels(pivot.columns)
    ax3.set_yticklabels(pivot.index)
    ax3.set_xlabel('L2 Associativity', fontsize=11, fontweight='bold')
    ax3.set_ylabel('L1 Associativity', fontsize=11, fontweight='bold')
    ax3.set_title('Execution Time: L1 vs L2 Associativity\n(Billion Ticks)', fontsize=12, fontweight='bold')

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            text = ax3.text(j, i, f'{pivot.values[i, j]:.1f}',
                           ha="center", va="center", color="black", fontsize=8)

    plt.colorbar(im3, ax=ax3, label='Billion Ticks')

    # Heatmap 4: L1D Size vs L1 Assoc (L1D Hit Rate)
    pivot = df.pivot_table(values='l1d_hit_rate', index='l1d_size', columns='l1_assoc', aggfunc='mean')
    pivot = pivot * 100
    im4 = ax4.imshow(pivot.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
    ax4.set_xticks(range(len(pivot.columns)))
    ax4.set_yticks(range(len(pivot.index)))
    ax4.set_xticklabels(pivot.columns)
    ax4.set_yticklabels([f'{convert_size_to_kb(s)}KB' for s in pivot.index])
    ax4.set_xlabel('L1 Associativity', fontsize=11, fontweight='bold')
    ax4.set_ylabel('L1D Size', fontsize=11, fontweight='bold')
    ax4.set_title('L1D Hit Rate: L1D Size vs Associativity\n(%)', fontsize=12, fontweight='bold')

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            text = ax4.text(j, i, f'{pivot.values[i, j]:.1f}',
                           ha="center", va="center", color="black", fontsize=8)

    plt.colorbar(im4, ax=ax4, label='Hit Rate (%)')

    plt.tight_layout()
    output_file = os.path.join(output_dir, 'parameter_heatmaps.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved: {output_file}")
    plt.close()


def plot_performance_distribution(df, output_dir):
    """Plot performance distribution histogram"""

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

    # Execution time distribution
    exec_times = df['simTicks'].values / 1e9
    ax1.hist(exec_times, bins=20, color=COLORS[0], alpha=0.7, edgecolor='black')
    ax1.axvline(exec_times.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {exec_times.mean():.1f}B')
    ax1.axvline(exec_times.min(), color='green', linestyle='--', linewidth=2, label=f'Best: {exec_times.min():.1f}B')
    ax1.set_xlabel('Execution Time (Billion Ticks)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax1.set_title('Distribution of Execution Times', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')

    # L1D hit rate distribution
    l1d_hits = df['l1d_hit_rate'].values * 100
    ax2.hist(l1d_hits, bins=20, color=COLORS[1], alpha=0.7, edgecolor='black')
    ax2.axvline(l1d_hits.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {l1d_hits.mean():.1f}%')
    ax2.set_xlabel('L1D Hit Rate (%)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax2.set_title('Distribution of L1D Hit Rates', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    # L2 hit rate distribution
    l2_hits = df['l2_hit_rate'].values * 100
    ax3.hist(l2_hits, bins=20, color=COLORS[2], alpha=0.7, edgecolor='black')
    ax3.axvline(l2_hits.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {l2_hits.mean():.1f}%')
    ax3.set_xlabel('L2 Hit Rate (%)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax3.set_title('Distribution of L2 Hit Rates', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')

    # CPI distribution
    if 'cpi' in df.columns:
        cpi = df['cpi'].values
        ax4.hist(cpi, bins=20, color=COLORS[3], alpha=0.7, edgecolor='black')
        ax4.axvline(cpi.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {cpi.mean():.2f}')
        ax4.set_xlabel('CPI (Cycles Per Instruction)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax4.set_title('Distribution of CPI', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = os.path.join(output_dir, 'performance_distribution.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved: {output_file}")
    plt.close()


def plot_pareto_frontier(df, output_dir):
    """Plot Pareto frontier for performance vs cache size"""

    # Calculate total cache size
    df['total_cache_kb'] = df.apply(
        lambda row: convert_size_to_kb(row['l1d_size']) + convert_size_to_kb(row['l2_size']),
        axis=1
    )

    # Normalize execution time (lower is better)
    exec_time = df['simTicks'].values / 1e9

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Color by L1D hit rate
    scatter = ax.scatter(df['total_cache_kb'], exec_time,
                        c=df['l1d_hit_rate']*100, cmap='RdYlGn',
                        s=100, alpha=0.6, edgecolors='black', linewidth=0.5)

    # Find Pareto frontier (minimize exec time, minimize cache size)
    # Sort by cache size
    sorted_df = df.sort_values('total_cache_kb')
    pareto_points = []
    min_exec = float('inf')

    for idx, row in sorted_df.iterrows():
        if row['simTicks']/1e9 < min_exec:
            pareto_points.append((row['total_cache_kb'], row['simTicks']/1e9))
            min_exec = row['simTicks']/1e9

    if pareto_points:
        pareto_x, pareto_y = zip(*pareto_points)
        ax.plot(pareto_x, pareto_y, 'r-', linewidth=2.5, label='Pareto Frontier', zorder=5)
        ax.scatter(pareto_x, pareto_y, c='red', s=200, marker='*',
                  edgecolors='black', linewidth=1.5, label='Pareto Optimal', zorder=6)

    ax.set_xlabel('Total Cache Size (KB)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Execution Time (Billion Ticks)', fontsize=12, fontweight='bold')
    ax.set_title('Pareto Frontier: Performance vs Cache Size\n(Color = L1D Hit Rate)',
                fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=10)

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('L1D Hit Rate (%)', fontsize=11, fontweight='bold')

    plt.tight_layout()
    output_file = os.path.join(output_dir, 'pareto_frontier.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved: {output_file}")
    plt.close()


def plot_top_configs_comparison(df, top_configs, output_dir):
    """Create comparison plot for top configurations"""

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Top 3 by execution time
    top_exec = top_configs['lowest_exec_time']
    configs = top_exec['config_name'].values
    exec_times = top_exec['simTicks'].values
    l1d_rates = top_exec['l1d_hit_rate'].values * 100
    l2_rates = top_exec['l2_hit_rate'].values * 100

    x = range(len(configs))
    ax1.barh(x, exec_times, color=COLORS[0], alpha=0.7)
    ax1.set_yticks(x)
    ax1.set_yticklabels([c.replace('_', '\n') for c in configs], fontsize=9)
    ax1.set_xlabel('Execution Time (Billion Ticks)', fontsize=11, fontweight='bold')
    ax1.set_title('Top 3: Lowest Execution Time', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')
    for i, v in enumerate(exec_times):
        ax1.text(v + 0.5, i, f'{v:.2f}B', va='center', fontweight='bold')

    # Top 3 by L1D hit rate
    top_l1d = top_configs['highest_l1d_hit_rate']
    configs = top_l1d['config_name'].values
    l1d_rates = top_l1d['l1d_hit_rate'].values * 100

    x = range(len(configs))
    ax2.barh(x, l1d_rates, color=COLORS[1], alpha=0.7)
    ax2.set_yticks(x)
    ax2.set_yticklabels([c.replace('_', '\n') for c in configs], fontsize=9)
    ax2.set_xlabel('L1D Hit Rate (%)', fontsize=11, fontweight='bold')
    ax2.set_title('Top 3: Highest L1D Hit Rate', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    ax2.set_xlim([0, 105])
    for i, v in enumerate(l1d_rates):
        ax2.text(v + 1, i, f'{v:.2f}%', va='center', fontweight='bold')

    # Top 3 by L2 hit rate
    top_l2 = top_configs['highest_l2_hit_rate']
    configs = top_l2['config_name'].values
    l2_rates = top_l2['l2_hit_rate'].values * 100

    x = range(len(configs))
    ax3.barh(x, l2_rates, color=COLORS[2], alpha=0.7)
    ax3.set_yticks(x)
    ax3.set_yticklabels([c.replace('_', '\n') for c in configs], fontsize=9)
    ax3.set_xlabel('L2 Hit Rate (%)', fontsize=11, fontweight='bold')
    ax3.set_title('Top 3: Highest L2 Hit Rate', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')
    ax3.set_xlim([0, 105])
    for i, v in enumerate(l2_rates):
        ax3.text(v + 1, i, f'{v:.2f}%', va='center', fontweight='bold')

    # Metrics comparison for best overall config
    best_config = df.nsmallest(1, 'simTicks').iloc[0]
    metrics = ['Exec Time\n(B ticks)', 'L1D Hit\nRate (%)', 'L2 Hit\nRate (%)', 'CPI']
    values = [
        best_config['simTicks'] / 1e9,
        best_config['l1d_hit_rate'] * 100,
        best_config['l2_hit_rate'] * 100,
        best_config['cpi']
    ]

    ax4.bar(metrics, values, color=COLORS[3], alpha=0.7)
    ax4.set_ylabel('Value', fontsize=11, fontweight='bold')
    ax4.set_title(f'Best Overall Configuration\n{best_config["config_name"]}',
                 fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(values):
        ax4.text(i, v + max(values)*0.02, f'{v:.2f}', ha='center', fontweight='bold')

    plt.tight_layout()
    output_file = os.path.join(output_dir, 'top_configs_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Plot saved: {output_file}")
    plt.close()


def calculate_summary_stats(df):
    """Calculate summary statistics for key metrics"""

    metrics = {
        'Execution Time (ticks)': 'simTicks',
        'Execution Time (seconds)': 'simSeconds',
        'L1D Hit Rate (%)': 'l1d_hit_rate',
        'L2 Hit Rate (%)': 'l2_hit_rate',
        'CPI': 'cpi',
        'IPC': 'ipc'
    }

    summary = {}

    for metric_name, column in metrics.items():
        if column in df.columns and df[column].notna().any():
            if 'Rate' in metric_name:
                # Convert to percentage
                summary[metric_name] = {
                    'mean': df[column].mean() * 100,
                    'std': df[column].std() * 100,
                    'min': df[column].min() * 100,
                    'max': df[column].max() * 100
                }
            else:
                summary[metric_name] = {
                    'mean': df[column].mean(),
                    'std': df[column].std(),
                    'min': df[column].min(),
                    'max': df[column].max()
                }

    return summary


def find_top_configurations(df):
    """Find top 3 configurations by different metrics"""

    # Top 3 by lowest execution time
    top_exec_time = df.nsmallest(3, 'simTicks')[
        ['config_name', 'l1d_size', 'l2_size', 'l1_assoc', 'l2_assoc',
         'simTicks', 'l1d_hit_rate', 'l2_hit_rate']
    ].copy()
    top_exec_time['simTicks'] = top_exec_time['simTicks'] / 1e9  # Convert to billions

    # Top 3 by highest L1D hit rate
    top_l1d_hit = df.nlargest(3, 'l1d_hit_rate')[
        ['config_name', 'l1d_size', 'l2_size', 'l1_assoc', 'l2_assoc',
         'simTicks', 'l1d_hit_rate', 'l2_hit_rate']
    ].copy()
    top_l1d_hit['simTicks'] = top_l1d_hit['simTicks'] / 1e9

    # Top 3 by highest L2 hit rate
    top_l2_hit = df.nlargest(3, 'l2_hit_rate')[
        ['config_name', 'l1d_size', 'l2_size', 'l1_assoc', 'l2_assoc',
         'simTicks', 'l1d_hit_rate', 'l2_hit_rate']
    ].copy()
    top_l2_hit['simTicks'] = top_l2_hit['simTicks'] / 1e9

    return {
        'lowest_exec_time': top_exec_time,
        'highest_l1d_hit_rate': top_l1d_hit,
        'highest_l2_hit_rate': top_l2_hit
    }


def print_summary_stats(summary, top_configs, output_dir):
    """Print and save summary statistics"""

    output_file = os.path.join(output_dir, 'summary_statistics.txt')

    with open(output_file, 'w') as f:
        content = []

        content.append("="*70)
        content.append("SUMMARY STATISTICS")
        content.append("="*70)
        content.append("")

        for metric, stats in summary.items():
            content.append(f"{metric}:")
            if 'ticks' in metric.lower():
                content.append(f"  Mean: {stats['mean']:,.0f}")
                content.append(f"  Std:  {stats['std']:,.0f}")
                content.append(f"  Min:  {stats['min']:,.0f}")
                content.append(f"  Max:  {stats['max']:,.0f}")
            elif 'seconds' in metric.lower():
                content.append(f"  Mean: {stats['mean']:.6f}")
                content.append(f"  Std:  {stats['std']:.6f}")
                content.append(f"  Min:  {stats['min']:.6f}")
                content.append(f"  Max:  {stats['max']:.6f}")
            else:
                content.append(f"  Mean: {stats['mean']:.2f}")
                content.append(f"  Std:  {stats['std']:.2f}")
                content.append(f"  Min:  {stats['min']:.2f}")
                content.append(f"  Max:  {stats['max']:.2f}")
            content.append("")

        content.append("="*70)
        content.append("TOP 3 CONFIGURATIONS")
        content.append("="*70)
        content.append("")

        # Lowest Execution Time
        content.append("By Lowest Execution Time:")
        content.append("-"*70)
        for idx, row in top_configs['lowest_exec_time'].iterrows():
            content.append(f"  {row['config_name']}")
            content.append(f"    Exec Time: {row['simTicks']:.2f}B ticks")
            content.append(f"    L1D Hit Rate: {row['l1d_hit_rate']*100:.2f}%")
            content.append(f"    L2 Hit Rate: {row['l2_hit_rate']*100:.2f}%")
            content.append("")

        # Highest L1D Hit Rate
        content.append("By Highest L1D Hit Rate:")
        content.append("-"*70)
        for idx, row in top_configs['highest_l1d_hit_rate'].iterrows():
            content.append(f"  {row['config_name']}")
            content.append(f"    L1D Hit Rate: {row['l1d_hit_rate']*100:.2f}%")
            content.append(f"    Exec Time: {row['simTicks']:.2f}B ticks")
            content.append(f"    L2 Hit Rate: {row['l2_hit_rate']*100:.2f}%")
            content.append("")

        # Highest L2 Hit Rate
        content.append("By Highest L2 Hit Rate:")
        content.append("-"*70)
        for idx, row in top_configs['highest_l2_hit_rate'].iterrows():
            content.append(f"  {row['config_name']}")
            content.append(f"    L2 Hit Rate: {row['l2_hit_rate']*100:.2f}%")
            content.append(f"    Exec Time: {row['simTicks']:.2f}B ticks")
            content.append(f"    L1D Hit Rate: {row['l1d_hit_rate']*100:.2f}%")
            content.append("")

        content.append("="*70)

        # Write to file and print
        output_text = "\n".join(content)
        f.write(output_text)
        print(output_text)

    print(f"\n✓ Summary statistics saved to: {output_file}")


def main():
    """Main execution function"""

    parser = argparse.ArgumentParser(
        description="Analyze multi-parameter sweep results"
    )
    parser.add_argument(
        "results_json",
        help="Path to results.json file"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output directory for plots and statistics"
    )

    args = parser.parse_args()

    # Set output directory
    if args.output is None:
        args.output = os.path.dirname(args.results_json)

    os.makedirs(args.output, exist_ok=True)

    print("\n" + "="*70)
    print("Multi-Parameter Sweep Analysis")
    print("="*70)
    print(f"\nInput: {args.results_json}")
    print(f"Output: {args.output}")
    print()

    # Load results
    print("Loading results...")
    results = load_results(args.results_json)
    df = pd.DataFrame(results)
    print(f"✓ Loaded {len(df)} configurations\n")

    # Generate plots
    print("Generating plots...")
    print("  [1/7] L1D size impact...")
    plot_l1d_impact(df, args.output)
    print("  [2/7] L2 size impact...")
    plot_l2_impact(df, args.output)
    print("  [3/7] Associativity impact...")
    plot_associativity_impact(df, args.output)
    print("  [4/7] Parameter heatmaps...")
    plot_parameter_heatmaps(df, args.output)
    print("  [5/7] Performance distribution...")
    plot_performance_distribution(df, args.output)
    print("  [6/7] Pareto frontier...")
    plot_pareto_frontier(df, args.output)

    # Calculate top configs first for the comparison plot
    top_configs = find_top_configurations(df)
    print("  [7/7] Top configs comparison...")
    plot_top_configs_comparison(df, top_configs, args.output)
    print()

    # Calculate summary statistics
    print("Calculating summary statistics...")
    summary = calculate_summary_stats(df)
    print()

    # Print and save summary
    print_summary_stats(summary, top_configs, args.output)

    print("\n" + "="*70)
    print("✓ Analysis complete!")
    print("="*70)
    print(f"\nGenerated {7} plots:")
    print("  - l1d_size_impact.png")
    print("  - l2_size_impact.png")
    print("  - associativity_impact.png")
    print("  - parameter_heatmaps.png")
    print("  - performance_distribution.png")
    print("  - pareto_frontier.png")
    print("  - top_configs_comparison.png")
    print()


if __name__ == "__main__":
    main()
