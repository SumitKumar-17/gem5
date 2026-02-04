#!/usr/bin/env python3
"""
Parse gem5 statistics from cache sweep and generate CSV
L1I and L1D are same size (varied together)
"""

import os
import re
import csv
import sys
from pathlib import Path

def parse_stats_file(stats_file):
    """Extract key metrics from a gem5 stats file"""
    metrics = {}
    
    try:
        with open(stats_file, 'r') as f:
            content = f.read()
            
            # Extract metrics using regex
            patterns = {
                'sim_ticks': r'simTicks\s+(\d+)',
                'sim_insts': r'simInsts\s+(\d+)',
                'ipc': r'system\.cpu\.ipc\s+([\d.]+)',
                
                # L1D Cache
                'l1d_accesses': r'system\.cpu\.dcache\.demandAccesses::total\s+(\d+)',
                'l1d_hits': r'system\.cpu\.dcache\.demandHits::total\s+(\d+)',
                'l1d_misses': r'system\.cpu\.dcache\.demandMisses::total\s+(\d+)',
                'l1d_miss_rate': r'system\.cpu\.dcache\.demandMissRate::total\s+([\d.]+)',
                
                # L1I Cache
                'l1i_accesses': r'system\.cpu\.icache\.demandAccesses::total\s+(\d+)',
                'l1i_hits': r'system\.cpu\.icache\.demandHits::total\s+(\d+)',
                'l1i_misses': r'system\.cpu\.icache\.demandMisses::total\s+(\d+)',
                'l1i_miss_rate': r'system\.cpu\.icache\.demandMissRate::total\s+([\d.]+)',
                
                # L2 Cache
                'l2_accesses': r'system\.l2cache\.demandAccesses::total\s+(\d+)',
                'l2_hits': r'system\.l2cache\.demandHits::total\s+(\d+)',
                'l2_misses': r'system\.l2cache\.demandMisses::total\s+(\d+)',
                'l2_miss_rate': r'system\.l2cache\.demandMissRate::total\s+([\d.]+)',
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, content)
                if match:
                    metrics[key] = match.group(1)
                else:
                    metrics[key] = 'N/A'
                    
    except Exception as e:
        print(f"Error parsing {stats_file}: {e}")
        return None
    
    return metrics

def parse_config_name(config_name):
    """Extract cache parameters from config directory name"""
    # Format: L132KiB_L1A4_L2256KiB_L2A4
    match = re.match(r'L1(\w+)_L1A(\d+)_L2(\w+)_L2A(\d+)', config_name)
    if match:
        return {
            'l1_size': match.group(1),
            'l1_assoc': match.group(2),
            'l2_size': match.group(3),
            'l2_assoc': match.group(4)
        }
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_results.py <results_directory>")
        sys.exit(1)
    
    results_dir = Path(sys.argv[1])
    
    if not results_dir.exists():
        print(f"Error: Directory {results_dir} does not exist")
        sys.exit(1)
    
    # Output CSV file
    output_csv = results_dir / "all_results.csv"
    
    all_results = []
    
    # Process both simple and chunked
    for sort_type in ['simple', 'chunked']:
        sort_dir = results_dir / sort_type
        
        if not sort_dir.exists():
            print(f"Warning: {sort_dir} does not exist, skipping...")
            continue
        
        # Iterate through all config directories
        for config_dir in sorted(sort_dir.iterdir()):
            if not config_dir.is_dir():
                continue
            
            config_name = config_dir.name
            stats_file = config_dir / "stats.txt"
            
            if not stats_file.exists():
                print(f"Warning: {stats_file} not found, skipping...")
                continue
            
            # Parse config parameters
            config_params = parse_config_name(config_name)
            if not config_params:
                print(f"Warning: Could not parse config name {config_name}")
                continue
            
            # Parse stats
            metrics = parse_stats_file(stats_file)
            if not metrics:
                continue
            
            # Combine all data
            result = {
                'sort_type': sort_type,
                'config_name': config_name,
                **config_params,
                **metrics
            }
            
            all_results.append(result)
            print(f"Processed: {sort_type}/{config_name}")
    
    # Write to CSV
    if all_results:
        fieldnames = [
            'sort_type', 'config_name', 
            'l1_size', 'l1_assoc', 'l2_size', 'l2_assoc',
            'sim_ticks', 'sim_insts', 'ipc',
            'l1d_accesses', 'l1d_hits', 'l1d_misses', 'l1d_miss_rate',
            'l1i_accesses', 'l1i_hits', 'l1i_misses', 'l1i_miss_rate',
            'l2_accesses', 'l2_hits', 'l2_misses', 'l2_miss_rate'
        ]
        
        with open(output_csv, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"\nResults written to: {output_csv}")
        print(f"Total configurations processed: {len(all_results)}")
    else:
        print("No results found!")

if __name__ == "__main__":
    main()
