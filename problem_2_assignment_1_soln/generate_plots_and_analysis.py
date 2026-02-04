#!/usr/bin/env python3
"""
Comprehensive plots and analysis for Part 2 cache sweep
Includes 10+ plots for thorough cache performance analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def load_data(csv_file):
    """Load and preprocess the results CSV"""
    df = pd.read_csv(csv_file)
    
    # Convert numeric columns
    numeric_cols = ['sim_ticks', 'sim_insts', 'ipc', 'l1d_miss_rate', 'l2_miss_rate',
                   'l1d_accesses', 'l1d_hits', 'l1d_misses',
                   'l2_accesses', 'l2_hits', 'l2_misses']
    
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calculate hit rates and additional metrics
    df['l1d_hit_rate'] = (1 - df['l1d_miss_rate']) * 100
    df['l2_hit_rate'] = (1 - df['l2_miss_rate']) * 100
    
    # Extract numeric values from size strings
    df['l1_size_kb'] = df['l1_size'].str.replace('KiB', '').astype(int)
    df['l2_size_kb'] = df['l2_size'].str.replace('KiB', '').astype(int)
    
    # Calculate performance metrics
    df['execution_time_sec'] = df['sim_ticks'] / 1e12  # Assuming 1GHz = 1e12 ticks/sec
    df['total_cache_kb'] = df['l1_size_kb'] * 2 + df['l2_size_kb']  # L1I + L1D + L2
    
    return df

# ========== REQUIRED PLOTS ==========

def plot_l2_miss_rate_vs_size(df, output_dir):
    """Plot 1: L2 miss rate vs L2 size (REQUIRED)"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    for idx, sort_type in enumerate(['simple', 'chunked']):
        data = df[df['sort_type'] == sort_type]
        grouped = data.groupby('l2_size_kb')['l2_miss_rate'].mean() * 100
        
        axes[idx].bar(grouped.index.astype(str), grouped.values, color='skyblue', edgecolor='black')
        axes[idx].set_xlabel('L2 Cache Size (KiB)', fontsize=12)
        axes[idx].set_ylabel('L2 Miss Rate (%)', fontsize=12)
        axes[idx].set_title(f'L2 Miss Rate vs L2 Size - {sort_type.capitalize()}', fontsize=14)
        axes[idx].grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(grouped.values):
            axes[idx].text(i, v + 1, f'{v:.1f}%', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'plot1_l2_miss_rate_vs_size.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: plot1_l2_miss_rate_vs_size.png")
    plt.close()

def plot_ipc_vs_l1_size(df, output_dir):
    """Plot 2: IPC vs L1 size (REQUIRED)"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    for idx, sort_type in enumerate(['simple', 'chunked']):
        data = df[df['sort_type'] == sort_type]
        grouped = data.groupby('l1_size_kb')['ipc'].mean()
        
        axes[idx].plot(grouped.index, grouped.values, marker='o', linewidth=2, markersize=10, color='green')
        axes[idx].set_xlabel('L1 Cache Size (KiB)', fontsize=12)
        axes[idx].set_ylabel('IPC (Instructions Per Cycle)', fontsize=12)
        axes[idx].set_title(f'IPC vs L1 Size - {sort_type.capitalize()}', fontsize=14)
        axes[idx].grid(alpha=0.3)
        axes[idx].set_xticks([32, 64, 128])
        
        for x, y in zip(grouped.index, grouped.values):
            axes[idx].text(x, y + 0.001, f'{y:.4f}', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'plot2_ipc_vs_l1_size.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: plot2_ipc_vs_l1_size.png")
    plt.close()

def plot_l1d_hit_rate_vs_assoc(df, output_dir):
    """Plot 3: L1D hit rate vs associativity (REQUIRED)"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    for idx, sort_type in enumerate(['simple', 'chunked']):
        data = df[df['sort_type'] == sort_type]
        grouped = data.groupby('l1_assoc')['l1d_hit_rate'].mean()
        
        axes[idx].bar(grouped.index.astype(str), grouped.values, color='coral', edgecolor='black')
        axes[idx].set_xlabel('L1 Associativity (way)', fontsize=12)
        axes[idx].set_ylabel('L1D Hit Rate (%)', fontsize=12)
        axes[idx].set_title(f'L1D Hit Rate vs Associativity - {sort_type.capitalize()}', fontsize=14)
        axes[idx].grid(axis='y', alpha=0.3)
        axes[idx].set_ylim([99.6, 100])
        
        for i, v in enumerate(grouped.values):
            axes[idx].text(i, v - 0.02, f'{v:.3f}%', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'plot3_l1d_hit_rate_vs_assoc.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: plot3_l1d_hit_rate_vs_assoc.png")
    plt.close()

def plot_simple_vs_chunked_comparison(df, output_dir):
    """Plot 4: Simple vs Chunked comparison (REQUIRED)"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    metrics = [
        ('ipc', 'IPC'),
        ('l1d_miss_rate', 'L1D Miss Rate (%)'),
        ('l2_miss_rate', 'L2 Miss Rate (%)'),
        ('execution_time_sec', 'Execution Time (seconds)')
    ]
    
    for idx, (metric, label) in enumerate(metrics):
        ax = axes[idx // 2, idx % 2]
        
        simple_data = df[df['sort_type'] == 'simple'][metric].values
        chunked_data = df[df['sort_type'] == 'chunked'][metric].values
        
        if 'rate' in metric:
            simple_data = simple_data * 100
            chunked_data = chunked_data * 100
        
        positions = [1, 2]
        bp = ax.boxplot([simple_data, chunked_data], positions=positions, widths=0.6,
                        patch_artist=True, showmeans=True)
        
        for patch, color in zip(bp['boxes'], ['lightblue', 'lightgreen']):
            patch.set_facecolor(color)
        
        ax.set_xticks(positions)
        ax.set_xticklabels(['Simple', 'Chunked'])
        ax.set_ylabel(label, fontsize=12)
        ax.set_title(f'{label} Comparison', fontsize=14)
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'plot4_simple_vs_chunked_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: plot4_simple_vs_chunked_comparison.png")
    plt.close()

# ========== ADDITIONAL INSIGHTFUL PLOTS ==========

def plot_ipc_heatmap(df, output_dir):
    """Plot 5: IPC heatmap showing L1 vs L2 size interaction"""
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    
    for idx, sort_type in enumerate(['simple', 'chunked']):
        data = df[df['sort_type'] == sort_type]
        pivot = data.pivot_table(values='ipc', index='l2_size_kb', columns='l1_size_kb', aggfunc='mean')
        
        sns.heatmap(pivot, annot=True, fmt='.4f', cmap='RdYlGn', ax=axes[idx], 
                   cbar_kws={'label': 'IPC'})
        axes[idx].set_xlabel('L1 Cache Size (KiB)', fontsize=12)
        axes[idx].set_ylabel('L2 Cache Size (KiB)', fontsize=12)
        axes[idx].set_title(f'IPC Heatmap: L1 vs L2 Size - {sort_type.capitalize()}', fontsize=14)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'plot5_ipc_heatmap.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: plot5_ipc_heatmap.png")
    plt.close()

def plot_l2_assoc_impact(df, output_dir):
    """Plot 6: L2 associativity impact on miss rate"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    for idx, sort_type in enumerate(['simple', 'chunked']):
        data = df[df['sort_type'] == sort_type]
        
        for l2_size in [256, 512, 1024]:
            subset = data[data['l2_size_kb'] == l2_size]
            grouped = subset.groupby('l2_assoc')['l2_miss_rate'].mean() * 100
            axes[idx].plot(grouped.index, grouped.values, marker='o', label=f'L2 {l2_size}KiB', linewidth=2)
        
        axes[idx].set_xlabel('L2 Associativity (way)', fontsize=12)
        axes[idx].set_ylabel('L2 Miss Rate (%)', fontsize=12)
        axes[idx].set_title(f'L2 Associativity Impact - {sort_type.capitalize()}', fontsize=14)
        axes[idx].legend()
        axes[idx].grid(alpha=0.3)
        axes[idx].set_xticks([4, 8, 16])
    
    plt.tight_layout()
    plt.savefig(output_dir / 'plot6_l2_assoc_impact.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: plot6_l2_assoc_impact.png")
    plt.close()

def plot_performance_vs_cache_budget(df, output_dir):
    """Plot 7: IPC vs total cache budget (cost-benefit analysis)"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for sort_type, color, marker in [('simple', 'blue', 'o'), ('chunked', 'green', 's')]:
        data = df[df['sort_type'] == sort_type]
        grouped = data.groupby('total_cache_kb')['ipc'].mean()
        ax.plot(grouped.index, grouped.values, marker=marker, label=sort_type.capitalize(), 
               linewidth=2, markersize=8, color=color)
    
    ax.set_xlabel('Total Cache Size (L1I + L1D + L2) in KiB', fontsize=12)
    ax.set_ylabel('IPC', fontsize=12)
    ax.set_title('Performance vs Cache Budget', fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'plot7_performance_vs_cache_budget.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: plot7_performance_vs_cache_budget.png")
    plt.close()

def plot_cache_miss_breakdown(df, output_dir):
    """Plot 8: Cache miss breakdown (L1D vs L2)"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    for idx, sort_type in enumerate(['simple', 'chunked']):
        data = df[df['sort_type'] == sort_type]
        
        l1d_misses = data['l1d_misses'].mean() / 1e6  # Convert to millions
        l2_misses = data['l2_misses'].mean() / 1e6
        
        categories = ['L1D Misses\n(to L2)', 'L2 Misses\n(to Memory)']
        values = [l1d_misses, l2_misses]
        colors = ['#ff9999', '#ff4444']
        
        bars = axes[idx].bar(categories, values, color=colors, edgecolor='black')
        axes[idx].set_ylabel('Cache Misses (Millions)', fontsize=12)
        axes[idx].set_title(f'Cache Miss Breakdown - {sort_type.capitalize()}', fontsize=14)
        axes[idx].grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            axes[idx].text(bar.get_x() + bar.get_width()/2., height,
                          f'{height:.2f}M', ha='center', va='bottom', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'plot8_cache_miss_breakdown.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: plot8_cache_miss_breakdown.png")
    plt.close()

def plot_execution_time_comparison(df, output_dir):
    """Plot 9: Execution time for different cache configurations"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    for idx, sort_type in enumerate(['simple', 'chunked']):
        data = df[df['sort_type'] == sort_type]
        
        # Group by L2 size
        grouped = data.groupby('l2_size_kb')['execution_time_sec'].mean()
        
        axes[idx].bar(grouped.index.astype(str), grouped.values, color='purple', 
                     alpha=0.7, edgecolor='black')
        axes[idx].set_xlabel('L2 Cache Size (KiB)', fontsize=12)
        axes[idx].set_ylabel('Execution Time (seconds)', fontsize=12)
        axes[idx].set_title(f'Execution Time vs L2 Size - {sort_type.capitalize()}', fontsize=14)
        axes[idx].grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(grouped.values):
            axes[idx].text(i, v + 50, f'{v:.0f}s', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'plot9_execution_time_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: plot9_execution_time_comparison.png")
    plt.close()

def plot_l1_size_vs_assoc_interaction(df, output_dir):
    """Plot 10: L1 size and associativity interaction on IPC"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    for idx, sort_type in enumerate(['simple', 'chunked']):
        data = df[df['sort_type'] == sort_type]
        
        for l1_assoc in [4, 8, 16]:
            subset = data[data['l1_assoc'] == l1_assoc]
            grouped = subset.groupby('l1_size_kb')['ipc'].mean()
            axes[idx].plot(grouped.index, grouped.values, marker='o', label=f'{l1_assoc}-way', linewidth=2)
        
        axes[idx].set_xlabel('L1 Cache Size (KiB)', fontsize=12)
        axes[idx].set_ylabel('IPC', fontsize=12)
        axes[idx].set_title(f'L1 Size × Associativity Interaction - {sort_type.capitalize()}', fontsize=14)
        axes[idx].legend(title='L1 Associativity')
        axes[idx].grid(alpha=0.3)
        axes[idx].set_xticks([32, 64, 128])
    
    plt.tight_layout()
    plt.savefig(output_dir / 'plot10_l1_size_assoc_interaction.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: plot10_l1_size_assoc_interaction.png")
    plt.close()

def plot_best_vs_worst_configs(df, output_dir):
    """Plot 11: Best vs Worst configurations comparison"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    metrics = ['ipc', 'l1d_miss_rate', 'l2_miss_rate']
    metric_labels = ['IPC\n(higher better)', 'L1D Miss Rate %\n(lower better)', 'L2 Miss Rate %\n(lower better)']
    
    for idx, sort_type in enumerate(['simple', 'chunked']):
        data = df[df['sort_type'] == sort_type]
        
        best_config = data.nlargest(1, 'ipc').iloc[0]
        worst_config = data.nsmallest(1, 'ipc').iloc[0]
        
        best_vals = [best_config['ipc'], best_config['l1d_miss_rate']*100, best_config['l2_miss_rate']*100]
        worst_vals = [worst_config['ipc'], worst_config['l1d_miss_rate']*100, worst_config['l2_miss_rate']*100]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        axes[idx].bar(x - width/2, best_vals, width, label='Best Config', color='green', alpha=0.7)
        axes[idx].bar(x + width/2, worst_vals, width, label='Worst Config', color='red', alpha=0.7)
        
        axes[idx].set_ylabel('Value', fontsize=12)
        axes[idx].set_title(f'Best vs Worst Config - {sort_type.capitalize()}', fontsize=14)
        axes[idx].set_xticks(x)
        axes[idx].set_xticklabels(metric_labels, fontsize=10)
        axes[idx].legend()
        axes[idx].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'plot11_best_vs_worst_configs.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: plot11_best_vs_worst_configs.png")
    plt.close()

def find_top_configs(df, output_file):
    """Find top 3 configurations by IPC for each workload"""
    results = []
    
    for sort_type in ['simple', 'chunked']:
        data = df[df['sort_type'] == sort_type].copy()
        top3 = data.nlargest(3, 'ipc')
        
        results.append(f"\n{'='*80}\n")
        results.append(f"TOP 3 CONFIGURATIONS - {sort_type.upper()} MERGE SORT\n")
        results.append(f"{'='*80}\n\n")
        
        for rank, (idx, row) in enumerate(top3.iterrows(), 1):
            results.append(f"Rank {rank}: {row['config_name']}\n")
            results.append(f"  L1 Cache: {row['l1_size']} (both I & D), {row['l1_assoc']}-way\n")
            results.append(f"  L2 Cache: {row['l2_size']}, {row['l2_assoc']}-way\n")
            results.append(f"  IPC: {row['ipc']:.6f}\n")
            results.append(f"  L1D Miss Rate: {row['l1d_miss_rate']*100:.3f}%\n")
            results.append(f"  L2 Miss Rate: {row['l2_miss_rate']*100:.2f}%\n")
            results.append(f"  Execution Time: {row['execution_time_sec']:.2f} seconds\n")
            results.append(f"  Sim Ticks: {row['sim_ticks']:,.0f}\n")
            results.append(f"\n")
    
    # Write to file
    with open(output_file, 'w') as f:
        f.writelines(results)
    
    print(f"✓ Saved: {output_file.name}")
    return ''.join(results)

def main():
    # Setup paths
    results_dir = Path('results/part2_sweep')
    csv_file = results_dir / 'all_results.csv'
    plots_dir = results_dir / 'plots'
    plots_dir.mkdir(exist_ok=True)
    
    print("="*80)
    print("PART 2: CACHE OPTIMIZATION SWEEP - PLOT GENERATION")
    print("="*80)
    
    print("\nLoading data...")
    df = load_data(csv_file)
    
    print(f"Loaded {len(df)} configurations")
    print(f"  Simple: {len(df[df['sort_type']=='simple'])}")
    print(f"  Chunked: {len(df[df['sort_type']=='chunked'])}")
    
    print("\n" + "="*80)
    print("GENERATING REQUIRED PLOTS (4)")
    print("="*80)
    plot_l2_miss_rate_vs_size(df, plots_dir)
    plot_ipc_vs_l1_size(df, plots_dir)
    plot_l1d_hit_rate_vs_assoc(df, plots_dir)
    plot_simple_vs_chunked_comparison(df, plots_dir)
    
    print("\n" + "="*80)
    print("GENERATING ADDITIONAL ANALYSIS PLOTS (7)")
    print("="*80)
    plot_ipc_heatmap(df, plots_dir)
    plot_l2_assoc_impact(df, plots_dir)
    plot_performance_vs_cache_budget(df, plots_dir)
    plot_cache_miss_breakdown(df, plots_dir)
    plot_execution_time_comparison(df, plots_dir)
    plot_l1_size_vs_assoc_interaction(df, plots_dir)
    plot_best_vs_worst_configs(df, plots_dir)
    
    print("\n" + "="*80)
    print("FINDING TOP CONFIGURATIONS")
    print("="*80)
    top_configs_text = find_top_configs(df, plots_dir / 'top_3_configs.txt')
    
    print("\n" + top_configs_text)
    
    print("="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"Total plots generated: 11")
    print(f"All outputs saved in: {plots_dir}")
    print(f"\nPlots generated:")
    print("  [Required]")
    print("    1. L2 miss rate vs L2 size")
    print("    2. IPC vs L1 size")
    print("    3. L1D hit rate vs associativity")
    print("    4. Simple vs Chunked comparison")
    print("  [Additional Analysis]")
    print("    5. IPC heatmap (L1 vs L2 interaction)")
    print("    6. L2 associativity impact")
    print("    7. Performance vs cache budget")
    print("    8. Cache miss breakdown")
    print("    9. Execution time comparison")
    print("   10. L1 size × associativity interaction")
    print("   11. Best vs worst configurations")

if __name__ == "__main__":
    main()
