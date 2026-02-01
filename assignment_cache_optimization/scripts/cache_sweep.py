#!/usr/bin/env python3
"""
Full Multi-Parameter Cache Sweep Script
========================================

This script performs a comprehensive sweep across multiple cache parameters
to understand parameter interactions and identify optimal configurations.

Parameters Swept:
  - L1D cache size
  - L2 cache size
  - L1 associativity
  - L2 associativity

Author: Assignment 1 - Part 3
Date: February 2026
"""

import subprocess
import re
import json
import os
import sys
import argparse
from datetime import datetime
from itertools import product

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Multi-parameter cache sweep for gem5')
    parser.add_argument('--gem5', type=str, default='./build/RISCV/gem5.opt',
                        help='Path to gem5 binary')
    parser.add_argument('--config', type=str, default='configs/cache_config.py',
                        help='Path to gem5 config script')
    parser.add_argument('--binary', type=str,
                        default='assignment_cache_optimization/benchmarks/matrix_multiply',
                        help='Path to benchmark binary')
    parser.add_argument('--output', type=str, default='full_sweep_results',
                        help='Output directory name (relative to results/)')
    parser.add_argument('--quick', action='store_true',
                        help='Run quick sweep with fewer configurations')
    return parser.parse_args()

def get_sweep_space(quick=False):
    """Define parameter sweep space"""
    if quick:
        # Quick sweep for testing (16 configurations)
        return {
            'l1d_size': ['16kB', '32kB'],
            'l2_size': ['128kB', '256kB'],
            'l1_assoc': [2, 4],
            'l2_assoc': [4, 8]
        }
    else:
        # Full sweep (72 configurations)
        return {
            'l1d_size': ['16kB', '32kB', '64kB'],
            'l2_size': ['128kB', '256kB', '512kB', '1MB'],
            'l1_assoc': [2, 4, 8],
            'l2_assoc': [4, 8, 16]
        }

def run_simulation(gem5_bin, config_script, binary, params, output_dir):
    """Run a single gem5 simulation"""

    # Create unique run name
    run_name = f"l1d_{params['l1d_size']}_l2_{params['l2_size']}_" \
               f"l1a{params['l1_assoc']}_l2a{params['l2_assoc']}"
    run_dir = f"{output_dir}/{run_name}"

    os.makedirs(run_dir, exist_ok=True)

    # Build command
    cmd = [
        gem5_bin,
        f"--outdir={run_dir}",
        config_script,
        f"--l1i_size=16kB",  # Keep L1I constant
        f"--l1d_size={params['l1d_size']}",
        f"--l2_size={params['l2_size']}",
        f"--l1_assoc={params['l1_assoc']}",
        f"--l2_assoc={params['l2_assoc']}",
        f"--binary={binary}"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            return None, run_name

        return run_dir, run_name

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None, run_name

def parse_stats(stats_file):
    """Parse gem5 statistics file"""
    stats = {
        'sim_ticks': 0,
        'sim_seconds': 0.0,
        'sim_insts': 0,
        'l1i_hits': 0, 'l1i_misses': 0, 'l1i_accesses': 0,
        'l1d_hits': 0, 'l1d_misses': 0, 'l1d_accesses': 0,
        'l2_hits': 0, 'l2_misses': 0, 'l2_accesses': 0
    }

    try:
        with open(stats_file, 'r') as f:
            content = f.read()

            # Simulation metrics
            match = re.search(r'simTicks\s+(\d+)', content)
            if match: stats['sim_ticks'] = int(match.group(1))

            match = re.search(r'simSeconds\s+([\d.]+)', content)
            if match: stats['sim_seconds'] = float(match.group(1))

            match = re.search(r'simInsts\s+(\d+)', content)
            if match: stats['sim_insts'] = int(match.group(1))

            # L1I stats
            match = re.search(r'system\.cpu\.icache\.demandHits::total\s+(\d+)', content)
            if match: stats['l1i_hits'] = int(match.group(1))

            match = re.search(r'system\.cpu\.icache\.demandMisses::total\s+(\d+)', content)
            if match: stats['l1i_misses'] = int(match.group(1))

            stats['l1i_accesses'] = stats['l1i_hits'] + stats['l1i_misses']

            # L1D stats
            match = re.search(r'system\.cpu\.dcache\.demandHits::total\s+(\d+)', content)
            if match: stats['l1d_hits'] = int(match.group(1))

            match = re.search(r'system\.cpu\.dcache\.demandMisses::total\s+(\d+)', content)
            if match: stats['l1d_misses'] = int(match.group(1))

            stats['l1d_accesses'] = stats['l1d_hits'] + stats['l1d_misses']

            # L2 stats
            match = re.search(r'system\.l2cache\.demandHits::total\s+(\d+)', content)
            if match: stats['l2_hits'] = int(match.group(1))

            match = re.search(r'system\.l2cache\.demandMisses::total\s+(\d+)', content)
            if match: stats['l2_misses'] = int(match.group(1))

            stats['l2_accesses'] = stats['l2_hits'] + stats['l2_misses']

    except Exception as e:
        print(f"WARNING: Error parsing stats: {e}")

    return stats

def main():
    args = parse_args()

    print("="*80)
    print("gem5 Multi-Parameter Cache Sweep")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nGem5 binary: {args.gem5}")
    print(f"Config script: {args.config}")
    print(f"Benchmark: {args.binary}")

    # Get sweep space
    sweep_space = get_sweep_space(args.quick)

    print(f"\nParameter Space:")
    for param, values in sweep_space.items():
        print(f"  {param}: {values}")

    # Calculate total configurations
    total_configs = 1
    for values in sweep_space.values():
        total_configs *= len(values)

    print(f"\nTotal configurations: {total_configs}")
    print(f"Estimated time: {total_configs * 15 / 60:.1f} minutes")

    # Create output directory
    output_dir = f"assignment_cache_optimization/results/{args.output}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    print("="*80)

    # Generate all parameter combinations
    param_names = list(sweep_space.keys())
    param_values = [sweep_space[name] for name in param_names]
    combinations = list(product(*param_values))

    print(f"\nRunning {len(combinations)} simulations...")

    # Results storage
    results = []

    # Run simulations
    for i, combo in enumerate(combinations, 1):
        params = dict(zip(param_names, combo))

        print(f"\n[{i}/{len(combinations)}] Running: L1D={params['l1d_size']}, "
              f"L2={params['l2_size']}, L1A={params['l1_assoc']}, L2A={params['l2_assoc']}")

        run_dir, run_name = run_simulation(
            args.gem5, args.config, args.binary, params, output_dir
        )

        if run_dir is None:
            print(f"  ⚠ Simulation failed, skipping...")
            continue

        # Parse stats
        stats_file = f"{run_dir}/stats.txt"
        if not os.path.exists(stats_file):
            print(f"  ⚠ Stats file not found")
            continue

        stats = parse_stats(stats_file)

        # Calculate hit rates
        l1i_hit_rate = (stats['l1i_hits'] / stats['l1i_accesses'] * 100) if stats['l1i_accesses'] > 0 else 0
        l1d_hit_rate = (stats['l1d_hits'] / stats['l1d_accesses'] * 100) if stats['l1d_accesses'] > 0 else 0
        l2_hit_rate = (stats['l2_hits'] / stats['l2_accesses'] * 100) if stats['l2_accesses'] > 0 else 0

        # Store result
        result = {
            'config_name': run_name,
            'l1d_size': params['l1d_size'],
            'l2_size': params['l2_size'],
            'l1_assoc': params['l1_assoc'],
            'l2_assoc': params['l2_assoc'],
            'sim_ticks': stats['sim_ticks'],
            'sim_seconds': stats['sim_seconds'],
            'sim_insts': stats['sim_insts'],
            'l1i_hit_rate': l1i_hit_rate,
            'l1d_hit_rate': l1d_hit_rate,
            'l2_hit_rate': l2_hit_rate,
            'l1i_hits': stats['l1i_hits'],
            'l1i_misses': stats['l1i_misses'],
            'l1d_hits': stats['l1d_hits'],
            'l1d_misses': stats['l1d_misses'],
            'l2_hits': stats['l2_hits'],
            'l2_misses': stats['l2_misses']
        }

        results.append(result)

        print(f"  ✓ Ticks: {stats['sim_ticks']:,}, L1D: {l1d_hit_rate:.2f}%, L2: {l2_hit_rate:.2f}%")

    if not results:
        print("\n⚠ No results collected!")
        return 1

    # Save results
    results_file = f"{output_dir}/results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*80}")
    print(f"✓ Sweep complete! {len(results)} configurations tested")
    print(f"✓ Results saved to: {results_file}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Quick summary
    print("\nQuick Summary:")
    print(f"  Configurations tested: {len(results)}")

    exec_times = [r['sim_ticks'] for r in results]
    print(f"  Execution time range: {min(exec_times):,} - {max(exec_times):,} ticks")

    best_perf = min(results, key=lambda x: x['sim_ticks'])
    print(f"\n  Best performance: {best_perf['config_name']}")
    print(f"    Time: {best_perf['sim_ticks']:,} ticks")
    print(f"    L1D hit: {best_perf['l1d_hit_rate']:.2f}%")

    return 0

if __name__ == "__main__":
    sys.exit(main())
