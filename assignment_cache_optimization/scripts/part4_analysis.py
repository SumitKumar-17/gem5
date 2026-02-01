#!/usr/bin/env python3
"""
Part 4: Design Analysis & Recommendations
==========================================

Generates Pareto-optimal analysis and comparison visualizations.

 * Team Members: Sumit Kumar(22CS30056) and Aviral Singh(22CS30015)
 * Assignment 1 - Cache Hierarchy Optimization Part 4
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Load results
def load_results(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def is_pareto_optimal(costs, return_mask=True):
    """
    Find Pareto-optimal points.
    costs: array of shape (n_points, n_costs)
    """
    is_efficient = np.ones(costs.shape[0], dtype=bool)
    for i, c in enumerate(costs):
        if is_efficient[i]:
            # Keep points that are not dominated
            is_efficient[is_efficient] = np.any(costs[is_efficient] < c, axis=1)
            is_efficient[i] = True
    return is_efficient if return_mask else np.where(is_efficient)[0]

def plot_pareto_frontier(results, output_dir):
    """Plot Pareto frontier: Performance vs Cost"""

    # Define cost metric (cache size in KB)
    def get_cache_size(r):
        l1d = int(r['l1d_size'].replace('kB', '').replace('MB', '000'))
        l2 = int(r['l2_size'].replace('kB', '').replace('MB', '000'))
        return l1d + l2

    # Extract data
    exec_times = np.array([r['sim_ticks'] for r in results])
    cache_sizes = np.array([get_cache_size(r) for r in results])

    # Find Pareto-optimal configs (minimize both time and cost)
    costs = np.column_stack([exec_times, cache_sizes])
    pareto_mask = is_pareto_optimal(costs)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 7))

    # Non-Pareto points
    ax.scatter(cache_sizes[~pareto_mask], exec_times[~pareto_mask] / 1e9,
               c='lightgray', s=50, alpha=0.5, label='Sub-optimal')

    # Pareto points
    ax.scatter(cache_sizes[pareto_mask], exec_times[pareto_mask] / 1e9,
               c='red', s=100, marker='*', label='Pareto-optimal', zorder=5)

    # Annotate top Pareto points
    pareto_results = [results[i] for i in range(len(results)) if pareto_mask[i]]
    pareto_results_sorted = sorted(pareto_results, key=lambda x: x['sim_ticks'])[:5]

    for r in pareto_results_sorted:
        size = get_cache_size(r)
        time = r['sim_ticks'] / 1e9
        label = f"{r['l1d_size']}/{r['l2_size']}\n{r['l1_assoc']}/{r['l2_assoc']}"
        ax.annotate(label, (size, time), xytext=(5, 5),
                   textcoords='offset points', fontsize=8,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

    ax.set_xlabel('Total Cache Size (L1D + L2) [KB]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Execution Time (Billion Ticks)', fontsize=12, fontweight='bold')
    ax.set_title('Pareto Frontier: Performance vs Cache Size\nMatrix Multiplication (64×64)',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_file = f"{output_dir}/pareto_frontier.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()

    return pareto_mask

def plot_performance_vs_cost(results, output_dir):
    """Plot normalized performance vs normalized cost"""

    def get_cache_size(r):
        l1d = int(r['l1d_size'].replace('kB', '').replace('MB', '000'))
        l2 = int(r['l2_size'].replace('kB', '').replace('MB', '000'))
        return l1d + l2

    exec_times = np.array([r['sim_ticks'] for r in results])
    cache_sizes = np.array([get_cache_size(r) for r in results])

    # Normalize (lower is better for both)
    norm_perf = (exec_times - exec_times.min()) / (exec_times.max() - exec_times.min())
    norm_cost = (cache_sizes - cache_sizes.min()) / (cache_sizes.max() - cache_sizes.min())

    # Efficiency metric (lower is better)
    efficiency = norm_perf + norm_cost

    # Find Pareto-optimal
    costs = np.column_stack([exec_times, cache_sizes])
    pareto_mask = is_pareto_optimal(costs)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Plot 1: Normalized performance vs cost
    ax1.scatter(norm_cost[~pareto_mask], norm_perf[~pareto_mask],
                c='lightblue', s=50, alpha=0.6, label='Sub-optimal')
    ax1.scatter(norm_cost[pareto_mask], norm_perf[pareto_mask],
                c='red', s=100, marker='*', label='Pareto-optimal', zorder=5)

    # Ideal point
    ax1.scatter(0, 0, c='green', s=200, marker='X',
                label='Ideal (min cost, max perf)', zorder=10)

    ax1.set_xlabel('Normalized Cost (Cache Size)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Normalized Performance Loss', fontsize=11, fontweight='bold')
    ax1.set_title('Performance vs Cost Trade-off', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Efficiency distribution
    colors = ['red' if p else 'lightblue' for p in pareto_mask]
    ax2.bar(range(len(efficiency)), sorted(efficiency), color=colors, alpha=0.7)
    ax2.axhline(y=0.5, color='green', linestyle='--', linewidth=2,
                label='50% efficiency threshold')
    ax2.set_xlabel('Configuration (sorted by efficiency)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Efficiency Score (lower=better)', fontsize=11, fontweight='bold')
    ax2.set_title('Configuration Efficiency Rankings', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = f"{output_dir}/performance_cost_tradeoff.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()

def plot_90_percent_threshold(results, output_dir):
    """Find configurations achieving 90% of peak performance"""

    exec_times = np.array([r['sim_ticks'] for r in results])
    best_time = exec_times.min()
    threshold_time = best_time * 1.111  # 10% slower = 90% of peak

    def get_cache_size(r):
        l1d = int(r['l1d_size'].replace('kB', '').replace('MB', '000'))
        l2 = int(r['l2_size'].replace('kB', '').replace('MB', '000'))
        return l1d + l2

    cache_sizes = np.array([get_cache_size(r) for r in results])

    # Find configs within threshold
    within_threshold = exec_times <= threshold_time

    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot all points
    ax.scatter(cache_sizes[~within_threshold], exec_times[~within_threshold] / 1e9,
               c='lightcoral', s=50, alpha=0.5, label='<90% peak perf')
    ax.scatter(cache_sizes[within_threshold], exec_times[within_threshold] / 1e9,
               c='lightgreen', s=100, alpha=0.7, label='≥90% peak perf')

    # Mark best config
    best_idx = exec_times.argmin()
    ax.scatter(cache_sizes[best_idx], exec_times[best_idx] / 1e9,
               c='gold', s=300, marker='*', label='Best config', zorder=10,
               edgecolors='black', linewidth=2)

    # Mark smallest config achieving 90%
    within_idx = np.where(within_threshold)[0]
    smallest_idx = within_idx[cache_sizes[within_idx].argmin()]
    ax.scatter(cache_sizes[smallest_idx], exec_times[smallest_idx] / 1e9,
               c='blue', s=200, marker='D', label='Smallest @ 90%', zorder=10,
               edgecolors='black', linewidth=2)

    # Annotate
    r_best = results[best_idx]
    r_small = results[smallest_idx]

    ax.annotate(f"Best: {r_best['l1d_size']}/{r_best['l2_size']}\n"
                f"{r_best['l1_assoc']}-way/{r_best['l2_assoc']}-way\n"
                f"{exec_times[best_idx]/1e9:.3f}B ticks",
                (cache_sizes[best_idx], exec_times[best_idx]/1e9),
                xytext=(15, 15), textcoords='offset points',
                bbox=dict(boxstyle='round', facecolor='gold', alpha=0.8),
                fontsize=9, fontweight='bold')

    ax.annotate(f"Min @ 90%: {r_small['l1d_size']}/{r_small['l2_size']}\n"
                f"{r_small['l1_assoc']}-way/{r_small['l2_assoc']}-way\n"
                f"{cache_sizes[smallest_idx]}KB total\n"
                f"{exec_times[smallest_idx]/1e9:.3f}B ticks",
                (cache_sizes[smallest_idx], exec_times[smallest_idx]/1e9),
                xytext=(15, -50), textcoords='offset points',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                fontsize=9)

    # Draw threshold line
    ax.axhline(y=threshold_time/1e9, color='red', linestyle='--', linewidth=2,
               label=f'90% threshold ({threshold_time/1e9:.3f}B)')

    ax.set_xlabel('Total Cache Size (KB)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Execution Time (Billion Ticks)', fontsize=12, fontweight='bold')
    ax.set_title('Finding Minimum Cache Size for 90% Peak Performance',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_file = f"{output_dir}/ninety_percent_threshold.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()

    print(f"\n90% Threshold Analysis:")
    print(f"  Best performance: {best_time:,} ticks")
    print(f"  90% threshold: {threshold_time:,} ticks")
    print(f"  Configs meeting threshold: {within_threshold.sum()} / {len(results)}")
    print(f"  Smallest config @ 90%: {r_small['config_name']}")
    print(f"    Size: {cache_sizes[smallest_idx]} KB")
    print(f"    Time: {exec_times[smallest_idx]:,} ticks")

def main():
    print("="*80)
    print("Part 4: Design Analysis & Recommendations")
    print("="*80)

    # Load results
    results_file = "assignment_cache_optimization/results/full_sweep_results/results.json"
    print(f"\nLoading: {results_file}")
    results = load_results(results_file)
    print(f"✓ Loaded {len(results)} configurations")

    output_dir = "assignment_cache_optimization/results/full_sweep_results/analysis_plots"

    print("\n" + "="*80)
    print("GENERATING PARETO ANALYSIS PLOTS")
    print("="*80)

    pareto_mask = plot_pareto_frontier(results, output_dir)
    plot_performance_vs_cost(results, output_dir)
    plot_90_percent_threshold(results, output_dir)

    print("\n" + "="*80)
    print("PARETO-OPTIMAL CONFIGURATIONS")
    print("="*80)

    pareto_configs = [results[i] for i in range(len(results)) if pareto_mask[i]]
    pareto_sorted = sorted(pareto_configs, key=lambda x: x['sim_ticks'])

    print(f"\nFound {len(pareto_configs)} Pareto-optimal configurations:")
    for i, config in enumerate(pareto_sorted[:10], 1):
        def get_size(r):
            l1d = int(r['l1d_size'].replace('kB', '').replace('MB', '000'))
            l2 = int(r['l2_size'].replace('kB', '').replace('MB', '000'))
            return l1d + l2

        print(f"\n[{i}] {config['config_name']}")
        print(f"    L1D: {config['l1d_size']}, L2: {config['l2_size']}")
        print(f"    L1A: {config['l1_assoc']}, L2A: {config['l2_assoc']}")
        print(f"    Time: {config['sim_ticks']:,} ticks")
        print(f"    Total Size: {get_size(config)} KB")
        print(f"    L1D Hit: {config['l1d_hit_rate']:.2f}%")

    print("\n" + "="*80)
    print("✓ Part 4 analysis complete!")
    print("="*80)

if __name__ == "__main__":
    main()
