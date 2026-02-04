#!/usr/bin/env python3
"""
Full Parameter Sweep Script for gem5 Cache Optimization
========================================================

This script performs a comprehensive multi-parameter sweep to understand
cache hierarchy behavior and parameter interactions.

Parameters Under Investigation:
- L1D cache size: 16kB, 32kB, 64kB
- L2 cache size: 128kB, 256kB, 512kB, 1MB
- L1 associativity: 2, 4, 8
- L2 associativity: 4, 8, 16

Fixed Parameters:
- Clock: 1GHz
- Memory Mode: timing
- Memory Size: 512MB
- L1I: 16kB (fixed)
- CPU: RiscvTimingSimpleCPU

Total Configurations: 3 × 4 × 3 × 3 = 108 simulations

Author: gem5 Assignment
Date: February 4, 2026
"""

import subprocess
import json
import csv
import os
import re
import sys
import time
import argparse
import itertools
from pathlib import Path

# Parameter sweep configurations
SWEEP_PARAMS = {
    "l1d_size": ["16kB", "32kB", "64kB"],
    "l2_size": ["128kB", "256kB", "512kB", "1MB"],
    "l1_assoc": [2, 4, 8],
    "l2_assoc": [4, 8, 16]
}

# Fixed parameters
FIXED_PARAMS = {
    "l1i_size": "16kB",
    "cpu_type": "timing"
}


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Full Parameter Sweep for gem5 Cache Optimization"
    )

    parser.add_argument(
        "--gem5",
        type=str,
        default="./build/RISCV/gem5.opt",
        help="Path to gem5 binary"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="assignment_cache_optimization/configs/cache_config.py",
        help="Path to gem5 config script"
    )

    parser.add_argument(
        "--binary",
        type=str,
        default="assignment_cache_optimization/benchmarks/matrix_multiply",
        help="Path to benchmark binary"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="assignment_cache_optimization/results/full_sweep_results",
        help="Output directory for results"
    )

    parser.add_argument(
        "--max-sims",
        type=int,
        default=None,
        help="Maximum number of simulations to run (for testing)"
    )

    return parser.parse_args()


def run_simulation(gem5_binary, config_script, binary, params, output_dir):
    """
    Run a single gem5 simulation with the specified parameters.

    Args:
        gem5_binary: Path to gem5 executable
        config_script: Path to gem5 config script
        binary: Path to benchmark binary
        params: Dictionary of parameters for this configuration
        output_dir: Directory to store simulation outputs

    Returns:
        True if simulation succeeded, False otherwise
    """
    # Construct command
    cmd = [
        gem5_binary,
        f"--outdir={output_dir}",
        config_script,
        f"--binary={binary}"
    ]

    # Add all parameters
    for param, value in params.items():
        cmd.append(f"--{param}={value}")

    try:
        # Run simulation
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per simulation
        )

        if result.returncode != 0:
            print(f"    ERROR: Return code {result.returncode}")
            return False

        return True

    except subprocess.TimeoutExpired:
        print(f"    ERROR: Timeout (600s)")
        return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def extract_statistics(stats_file):
    """
    Extract relevant statistics from gem5 stats.txt file.

    Args:
        stats_file: Path to stats.txt file

    Returns:
        Dictionary with extracted statistics
    """
    stats = {
        "simTicks": None,
        "simSeconds": None,
        "numCycles": None,
        "numInsts": None,
        "cpi": None,
        "ipc": None,
        "l1d_accesses": None,
        "l1d_hits": None,
        "l1d_misses": None,
        "l1d_miss_rate": None,
        "l1d_hit_rate": None,
        "l2_accesses": None,
        "l2_hits": None,
        "l2_misses": None,
        "l2_miss_rate": None,
        "l2_hit_rate": None
    }

    try:
        with open(stats_file, 'r') as f:
            content = f.read()

            # Extract simulation metrics
            match = re.search(r'simTicks\s+(\d+)', content)
            if match:
                stats["simTicks"] = int(match.group(1))

            match = re.search(r'simSeconds\s+([\d.]+)', content)
            if match:
                stats["simSeconds"] = float(match.group(1))

            match = re.search(r'system\.cpu\.numCycles\s+(\d+)', content)
            if match:
                stats["numCycles"] = int(match.group(1))

            match = re.search(r'simInsts\s+(\d+)', content)
            if match:
                stats["numInsts"] = int(match.group(1))

            match = re.search(r'system\.cpu\.cpi\s+([\d.]+)', content)
            if match:
                stats["cpi"] = float(match.group(1))

            match = re.search(r'system\.cpu\.ipc\s+([\d.]+)', content)
            if match:
                stats["ipc"] = float(match.group(1))

            # Extract L1 D-cache statistics
            match = re.search(r'system\.cpu\.dcache\.overallAccesses::total\s+(\d+)', content)
            if match:
                stats["l1d_accesses"] = int(match.group(1))

            match = re.search(r'system\.cpu\.dcache\.overallHits::total\s+(\d+)', content)
            if match:
                stats["l1d_hits"] = int(match.group(1))

            match = re.search(r'system\.cpu\.dcache\.overallMisses::total\s+(\d+)', content)
            if match:
                stats["l1d_misses"] = int(match.group(1))

            match = re.search(r'system\.cpu\.dcache\.overallMissRate::total\s+([\d.]+)', content)
            if match:
                stats["l1d_miss_rate"] = float(match.group(1))
                stats["l1d_hit_rate"] = 1.0 - stats["l1d_miss_rate"]

            # Extract L2 cache statistics
            match = re.search(r'system\.l2cache\.overallAccesses::total\s+(\d+)', content)
            if match:
                stats["l2_accesses"] = int(match.group(1))

            match = re.search(r'system\.l2cache\.overallHits::total\s+(\d+)', content)
            if match:
                stats["l2_hits"] = int(match.group(1))

            match = re.search(r'system\.l2cache\.overallMisses::total\s+(\d+)', content)
            if match:
                stats["l2_misses"] = int(match.group(1))

            match = re.search(r'system\.l2cache\.overallMissRate::total\s+([\d.]+)', content)
            if match:
                stats["l2_miss_rate"] = float(match.group(1))
                stats["l2_hit_rate"] = 1.0 - stats["l2_miss_rate"]

        return stats

    except Exception as e:
        print(f"    ERROR extracting stats: {e}")
        return stats


def main():
    """Main execution function"""

    args = parse_arguments()

    print("\n" + "="*70)
    print("Full Parameter Sweep - gem5 Cache Optimization")
    print("="*70)
    print(f"\ngem5 Binary: {args.gem5}")
    print(f"Config Script: {args.config}")
    print(f"Benchmark: {args.binary}")
    print(f"Output Directory: {args.output}")

    print(f"\nSweep Parameters:")
    for param, values in SWEEP_PARAMS.items():
        print(f"  {param}: {values}")

    print(f"\nFixed Parameters:")
    for param, value in FIXED_PARAMS.items():
        print(f"  {param}: {value}")

    # Calculate total configurations
    total_configs = 1
    for values in SWEEP_PARAMS.values():
        total_configs *= len(values)

    if args.max_sims:
        total_configs = min(total_configs, args.max_sims)
        print(f"\n⚠ Limited to {args.max_sims} simulations for testing")

    print(f"\nTotal Configurations: {total_configs}")
    print("="*70 + "\n")

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # Generate all parameter combinations
    param_names = list(SWEEP_PARAMS.keys())
    param_values = [SWEEP_PARAMS[name] for name in param_names]

    all_combinations = list(itertools.product(*param_values))

    if args.max_sims:
        all_combinations = all_combinations[:args.max_sims]

    # Results storage
    results = []
    successful = 0
    failed = 0

    start_time = time.time()

    # Run simulations
    for idx, combo in enumerate(all_combinations, 1):
        # Create parameter dictionary
        params = dict(zip(param_names, combo))
        params.update(FIXED_PARAMS)

        # Create configuration name
        config_name = f"l1d{params['l1d_size']}_l2{params['l2_size']}_" \
                     f"l1a{params['l1_assoc']}_l2a{params['l2_assoc']}"

        # Create output directory for this configuration
        output_dir = os.path.join(args.output, config_name)
        os.makedirs(output_dir, exist_ok=True)

        print(f"[{idx}/{len(all_combinations)}] {config_name}...", end=" ", flush=True)

        # Run simulation
        success = run_simulation(args.gem5, args.config, args.binary, params, output_dir)

        if not success:
            failed += 1
            print("✗ FAILED")
            continue

        # Extract statistics
        stats_file = os.path.join(output_dir, "stats.txt")
        if not os.path.exists(stats_file):
            failed += 1
            print("✗ NO STATS")
            continue

        stats = extract_statistics(stats_file)

        # Add configuration to results
        result = {
            "config_name": config_name,
            "l1d_size": params["l1d_size"],
            "l2_size": params["l2_size"],
            "l1_assoc": params["l1_assoc"],
            "l2_assoc": params["l2_assoc"],
            **stats
        }
        results.append(result)

        successful += 1
        print(f"✓ {stats['simTicks']/1e9:.1f}B ticks, L1D:{stats['l1d_hit_rate']*100:.1f}%")

        # Periodic save
        if successful % 10 == 0:
            temp_json = os.path.join(args.output, "results_temp.json")
            with open(temp_json, 'w') as f:
                json.dump(results, f, indent=2)

    end_time = time.time()
    elapsed = end_time - start_time

    # Save final results
    json_file = os.path.join(args.output, "results.json")
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Results saved to: {json_file}")

    # Save as CSV
    csv_file = os.path.join(args.output, "results.csv")
    if results:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"✓ Results saved to: {csv_file}")

    # Print summary
    print("\n" + "="*70)
    print("SWEEP SUMMARY")
    print("="*70)
    print(f"Total Configurations: {len(all_combinations)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total Time: {elapsed/60:.1f} minutes ({elapsed:.0f} seconds)")
    print(f"Avg Time per Sim: {elapsed/len(all_combinations):.1f} seconds")
    print("="*70 + "\n")

    print("Next steps:")
    print(f"  python scripts/analyze_sweep.py {json_file} --output={args.output}")
    print()


if __name__ == "__main__":
    main()
