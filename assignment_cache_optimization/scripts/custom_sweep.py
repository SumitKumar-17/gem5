#!/usr/bin/env python3
"""
Custom Parameter Sweep Script for gem5 Cache Analysis
======================================================

This script performs a parameter sweep on L2 cache size while keeping
other cache parameters constant. It collects execution time and cache
statistics for analysis.

Parameter Swept: L2 Cache Size (128kB, 256kB, 512kB, 1MB)

 * Team Members: Sumit Kumar(22CS30056) and Aviral Singh(22CS30015)
 * Assignment 1 - Cache Hierarchy Optimization Part 2
"""

import subprocess
import re
import json
import csv
import os
import sys
from datetime import datetime

# Configuration
GEM5_BINARY = "./build/RISCV/gem5.opt"
CONFIG_SCRIPT = "configs/cache_config.py"
BENCHMARK_BINARY = "assignment_cache_optimization/benchmarks/matrix_multiply"
OUTPUT_DIR = "assignment_cache_optimization/results/single_param_sweep"

# Default parameters (kept constant)
DEFAULT_PARAMS = {
    'l1i_size': '16kB',
    'l1d_size': '16kB',
    'l1_assoc': 4,
    'l2_assoc': 8
}

# Parameter to sweep: L2 Cache Size
SWEEP_PARAMETER = 'l2_size'
SWEEP_VALUES = ['128kB', '256kB', '512kB', '1MB']

def run_simulation(l2_size, output_subdir):
    """Run a single gem5 simulation with specified L2 cache size"""

    print(f"\n{'='*70}")
    print(f"Running simulation with L2 size = {l2_size}")
    print(f"{'='*70}")

    # Create output directory for this run
    run_output_dir = f"{output_subdir}/l2_{l2_size}"
    os.makedirs(run_output_dir, exist_ok=True)

    # Build command
    cmd = [
        GEM5_BINARY,
        f"--outdir={run_output_dir}",
        CONFIG_SCRIPT,
        f"--l1i_size={DEFAULT_PARAMS['l1i_size']}",
        f"--l1d_size={DEFAULT_PARAMS['l1d_size']}",
        f"--l2_size={l2_size}",
        f"--l1_assoc={DEFAULT_PARAMS['l1_assoc']}",
        f"--l2_assoc={DEFAULT_PARAMS['l2_assoc']}",
        f"--binary={BENCHMARK_BINARY}"
    ]

    print(f"Command: {' '.join(cmd)}")

    try:
        # Run simulation
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode != 0:
            print(f"ERROR: Simulation failed with return code {result.returncode}")
            print(f"STDERR: {result.stderr}")
            return None

        print(f"✓ Simulation completed successfully")
        return run_output_dir

    except subprocess.TimeoutExpired:
        print(f"ERROR: Simulation timed out after 10 minutes")
        return None
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None

def parse_stats(stats_file):
    """Parse gem5 stats.txt file to extract key metrics"""

    stats = {
        'sim_ticks': 0,
        'sim_seconds': 0.0,
        'sim_insts': 0,
        'l1i_hits': 0,
        'l1i_misses': 0,
        'l1i_accesses': 0,
        'l1i_miss_rate': 0.0,
        'l1d_hits': 0,
        'l1d_misses': 0,
        'l1d_accesses': 0,
        'l1d_miss_rate': 0.0,
        'l2_hits': 0,
        'l2_misses': 0,
        'l2_accesses': 0,
        'l2_miss_rate': 0.0
    }

    try:
        with open(stats_file, 'r') as f:
            content = f.read()

            # Extract simulation time
            match = re.search(r'simTicks\s+(\d+)', content)
            if match:
                stats['sim_ticks'] = int(match.group(1))

            match = re.search(r'simSeconds\s+([\d.]+)', content)
            if match:
                stats['sim_seconds'] = float(match.group(1))

            match = re.search(r'simInsts\s+(\d+)', content)
            if match:
                stats['sim_insts'] = int(match.group(1))

            # L1I cache stats
            match = re.search(r'system\.cpu\.icache\.demandHits::total\s+(\d+)', content)
            if match:
                stats['l1i_hits'] = int(match.group(1))

            match = re.search(r'system\.cpu\.icache\.demandMisses::total\s+(\d+)', content)
            if match:
                stats['l1i_misses'] = int(match.group(1))

            match = re.search(r'system\.cpu\.icache\.demandMissRate::total\s+([\d.]+)', content)
            if match:
                stats['l1i_miss_rate'] = float(match.group(1))

            stats['l1i_accesses'] = stats['l1i_hits'] + stats['l1i_misses']

            # L1D cache stats
            match = re.search(r'system\.cpu\.dcache\.demandHits::total\s+(\d+)', content)
            if match:
                stats['l1d_hits'] = int(match.group(1))

            match = re.search(r'system\.cpu\.dcache\.demandMisses::total\s+(\d+)', content)
            if match:
                stats['l1d_misses'] = int(match.group(1))

            match = re.search(r'system\.cpu\.dcache\.demandMissRate::total\s+([\d.]+)', content)
            if match:
                stats['l1d_miss_rate'] = float(match.group(1))

            stats['l1d_accesses'] = stats['l1d_hits'] + stats['l1d_misses']

            # L2 cache stats
            match = re.search(r'system\.l2cache\.demandHits::total\s+(\d+)', content)
            if match:
                stats['l2_hits'] = int(match.group(1))

            match = re.search(r'system\.l2cache\.demandMisses::total\s+(\d+)', content)
            if match:
                stats['l2_misses'] = int(match.group(1))

            match = re.search(r'system\.l2cache\.demandMissRate::total\s+([\d.]+)', content)
            if match:
                stats['l2_miss_rate'] = float(match.group(1))

            stats['l2_accesses'] = stats['l2_hits'] + stats['l2_misses']

    except Exception as e:
        print(f"ERROR parsing stats: {str(e)}")

    return stats

def main():
    print("="*70)
    print("gem5 Cache Parameter Sweep - L2 Cache Size Analysis")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nSweeping parameter: {SWEEP_PARAMETER}")
    print(f"Values: {SWEEP_VALUES}")
    print(f"\nConstant parameters:")
    for key, val in DEFAULT_PARAMS.items():
        print(f"  {key}: {val}")
    print(f"\nBenchmark: {BENCHMARK_BINARY}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*70)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Results storage
    results = []

    # Run simulations for each L2 size
    for l2_size in SWEEP_VALUES:
        run_dir = run_simulation(l2_size, OUTPUT_DIR)

        if run_dir is None:
            print(f"⚠ Skipping {l2_size} due to simulation failure")
            continue

        # Parse statistics
        stats_file = f"{run_dir}/stats.txt"
        if not os.path.exists(stats_file):
            print(f"⚠ Stats file not found: {stats_file}")
            continue

        stats = parse_stats(stats_file)

        # Calculate hit rates
        l1i_hit_rate = (stats['l1i_hits'] / stats['l1i_accesses'] * 100) if stats['l1i_accesses'] > 0 else 0
        l1d_hit_rate = (stats['l1d_hits'] / stats['l1d_accesses'] * 100) if stats['l1d_accesses'] > 0 else 0
        l2_hit_rate = (stats['l2_hits'] / stats['l2_accesses'] * 100) if stats['l2_accesses'] > 0 else 0

        result = {
            'l2_size': l2_size,
            'l2_size_kb': int(l2_size.replace('kB', '').replace('MB', '000').replace('KB', '').replace('KiB', '').replace('MiB', '024')),
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

        print(f"\n{'─'*70}")
        print(f"Results for L2 size = {l2_size}:")
        print(f"  Execution time: {stats['sim_ticks']:,} ticks ({stats['sim_seconds']:.6f} seconds)")
        print(f"  Instructions: {stats['sim_insts']:,}")
        print(f"  L1I hit rate: {l1i_hit_rate:.2f}%")
        print(f"  L1D hit rate: {l1d_hit_rate:.2f}%")
        print(f"  L2 hit rate: {l2_hit_rate:.2f}%")
        print(f"{'─'*70}")

    if not results:
        print("\n⚠ No results collected. Exiting.")
        return 1

    # Save results to JSON
    json_file = f"{OUTPUT_DIR}/results.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Results saved to JSON: {json_file}")

    # Save results to CSV
    csv_file = f"{OUTPUT_DIR}/results.csv"
    with open(csv_file, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    print(f"✓ Results saved to CSV: {csv_file}")

    # Print summary table
    print("\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    print(f"{'L2 Size':<10} {'Ticks':>15} {'L1I Hit%':>10} {'L1D Hit%':>10} {'L2 Hit%':>10}")
    print("─"*70)
    for r in results:
        print(f"{r['l2_size']:<10} {r['sim_ticks']:>15,} {r['l1i_hit_rate']:>9.2f}% {r['l1d_hit_rate']:>9.2f}% {r['l2_hit_rate']:>9.2f}%")
    print("="*70)

    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("✓ Sweep complete!")

    return 0

if __name__ == "__main__":
    sys.exit(main())
