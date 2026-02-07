#!/usr/bin/env python3
"""
Custom Parameter Sweep Script for gem5 Cache Optimization
==========================================================

This script performs a single-parameter sweep to understand the impact
of one cache parameter on performance.

Parameter Under Investigation: L1D Cache Size
Sweep Values: 16kB, 32kB, 64kB, 128kB

Fixed Parameters:
- Clock: 1GHz
- Memory Mode: timing
- Memory Size: 512MB
- L1I: 16kB, assoc=4
- L2: 256kB, assoc=8
- CPU: RiscvTimingSimpleCPU

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
from pathlib import Path

# Configuration
GEM5_BINARY = "./build/RISCV/gem5.opt"
CONFIG_SCRIPT = "assignment_cache_optimization/configs/cache_config.py"
BENCHMARK_BINARY = "assignment_cache_optimization/benchmarks/matrix_multiply"
OUTPUT_BASE_DIR = "assignment_cache_optimization/results/single_param_sweep"

# Parameter to sweep: L1D Cache Size
PARAMETER_NAME = "l1d_size"
PARAMETER_VALUES = ["16kB", "32kB", "64kB", "128kB"]

# Fixed parameters
FIXED_PARAMS = {
    "l1i_size": "16kB",
    "l2_size": "256kB",
    "l1_assoc": 4,
    "l2_assoc": 8,
    "cpu_type": "timing"
}


def run_simulation(param_value, output_dir):
    """
    Run a single gem5 simulation with the specified parameter value.

    Args:
        param_value: Value for the parameter being swept
        output_dir: Directory to store simulation outputs

    Returns:
        True if simulation succeeded, False otherwise
    """
    # Construct command
    cmd = [
        GEM5_BINARY,
        f"--outdir={output_dir}",
        CONFIG_SCRIPT,
        f"--{PARAMETER_NAME}={param_value}",
        f"--binary={BENCHMARK_BINARY}"
    ]

    # Add fixed parameters
    for param, value in FIXED_PARAMS.items():
        cmd.append(f"--{param}={value}")

    print(f"\n{'='*70}")
    print(f"Running simulation: {PARAMETER_NAME}={param_value}")
    print(f"Output directory: {output_dir}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*70}\n")

    try:
        # Run simulation
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        end_time = time.time()

        if result.returncode != 0:
            print(f"ERROR: Simulation failed with return code {result.returncode}")
            print(f"STDERR: {result.stderr}")
            return False

        print(f"✓ Simulation completed successfully in {end_time - start_time:.1f} seconds")
        return True

    except subprocess.TimeoutExpired:
        print(f"ERROR: Simulation timed out after 600 seconds")
        return False
    except Exception as e:
        print(f"ERROR: Exception during simulation: {e}")
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

            # Extract simulation time metrics
            match = re.search(r'simTicks\s+(\d+)', content)
            if match:
                stats["simTicks"] = int(match.group(1))

            match = re.search(r'simSeconds\s+([\d.]+)', content)
            if match:
                stats["simSeconds"] = float(match.group(1))

            match = re.search(r'system\.cpu\.numCycles\s+(\d+)', content)
            if match:
                stats["numCycles"] = int(match.group(1))

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
        print(f"ERROR: Failed to extract statistics: {e}")
        return stats


def main():
    """Main execution function"""

    print("\n" + "="*70)
    print("Custom Parameter Sweep Script")
    print("="*70)
    print(f"\nParameter: {PARAMETER_NAME}")
    print(f"Values: {', '.join(PARAMETER_VALUES)}")
    print(f"\nFixed Parameters:")
    for param, value in FIXED_PARAMS.items():
        print(f"  {param}: {value}")
    print("="*70 + "\n")

    # Create output directory
    os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

    # Results storage
    results = []

    # Run simulations for each parameter value
    for param_value in PARAMETER_VALUES:
        # Create output directory for this configuration
        output_dir = os.path.join(OUTPUT_BASE_DIR, f"{PARAMETER_NAME}_{param_value}")
        os.makedirs(output_dir, exist_ok=True)

        # Run simulation
        success = run_simulation(param_value, output_dir)

        if not success:
            print(f"⚠ Skipping {param_value} due to simulation failure")
            continue

        # Extract statistics
        stats_file = os.path.join(output_dir, "stats.txt")
        if not os.path.exists(stats_file):
            print(f"⚠ Stats file not found: {stats_file}")
            continue

        stats = extract_statistics(stats_file)

        # Add parameter value to results
        result = {
            "parameter": PARAMETER_NAME,
            "value": param_value,
            **stats
        }
        results.append(result)

        # Print summary
        print(f"\n{'-'*70}")
        print(f"Results for {PARAMETER_NAME}={param_value}:")
        print(f"  Execution Time: {stats['simTicks']:,} ticks ({stats['simSeconds']:.6f} seconds)")
        print(f"  L1D Hit Rate: {stats['l1d_hit_rate']*100:.2f}%")
        print(f"  L1D Misses: {stats['l1d_misses']:,}")
        print(f"  L2 Hit Rate: {stats['l2_hit_rate']*100:.2f}%")
        print(f"{'-'*70}\n")

    # Save results to JSON
    json_file = os.path.join(OUTPUT_BASE_DIR, "results.json")
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✓ Results saved to: {json_file}")

    # Save results to CSV
    csv_file = os.path.join(OUTPUT_BASE_DIR, "results.csv")
    if results:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"✓ Results saved to: {csv_file}")

    # Print summary table
    print("\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    print(f"{'L1D Size':<12} {'Exec Time (ticks)':<20} {'L1D Hit Rate':<15} {'L2 Hit Rate':<15}")
    print("-"*70)
    for result in results:
        print(f"{result['value']:<12} {result['simTicks']:<20,} "
              f"{result['l1d_hit_rate']*100:<14.2f}% {result['l2_hit_rate']*100:<14.2f}%")
    print("="*70 + "\n")

    print("✓ Custom parameter sweep complete!")
    print(f"\nNext steps:")
    print(f"  1. Review results in: {OUTPUT_BASE_DIR}/")
    print(f"  2. Generate plots using the results")
    print(f"  3. Analyze trends and write summary\n")


if __name__ == "__main__":
    main()
