# Part 1: Environment Setup - README

## Overview
This document describes how to set up and run the gem5 cache configuration for Assignment 1.

## Prerequisites
- gem5 built with RISCV ISA: `build/RISCV/gem5.opt`
- Python 3.x
- Test binary (included with gem5)

## Demo Runs Screenshots
- [Version Check](./PART1/version_check.png)
- [Cache Config Script](./PART1/Part_1_run_terminal_capture.png)

## Files Included

### Configuration Script
- **Location**: `configs/cache_config.py`
- **Description**: Main gem5 configuration script with configurable cache parameters

### Output Files
- **PART1_OUTPUT.txt**: Complete summary of Part 1 execution
- **PART1/PART1_stats.txt**: Detailed gem5 statistics from test run
- **PART1/PART1_config.ini**: System configuration used in test run

## How to Run

### Step 1: Verify gem5 Build
```bash
cd /home/sumitk/Desktop/gem5
ls -lh build/RISCV/gem5.opt
# Should show a ~954MB executable
```

### Step 2: Run with Default Configuration
```bash
./build/RISCV/gem5.opt configs/cache_config.py \
    --l1i_size=16kB \
    --l1d_size=16kB \
    --l2_size=256kB \
    --l1_assoc=4 \
    --l2_assoc=8 \
    --binary=tests/test-progs/hello/bin/riscv/linux/hello
```

### Step 3: View Results
```bash
# View complete statistics
cat m5out/stats.txt

# View cache-specific statistics
grep -E "system\.cpu\.(icache|dcache)|system\.l2cache" m5out/stats.txt | \
    grep -E "(Hits|Misses|MissRate)" | head -20
```

## Configuration Parameters

The `cache_config.py` script accepts the following command-line arguments:

| Parameter | Description | Default | Example Values |
|-----------|-------------|---------|----------------|
| `--l1i_size` | L1 instruction cache size | 16kB | 16kB, 32kB, 64kB |
| `--l1d_size` | L1 data cache size | 16kB | 16kB, 32kB, 64kB |
| `--l2_size` | L2 cache size | 256kB | 128kB, 256kB, 512kB, 1MB |
| `--l1_assoc` | L1 cache associativity | 4 | 2, 4, 8 |
| `--l2_assoc` | L2 cache associativity | 8 | 4, 8, 16 |
| `--binary` | Path to executable | tests/test-progs/hello/bin/riscv/linux/hello | Any RISCV binary |

## System Architecture

The configuration creates the following memory hierarchy:

```
┌─────────────────────────────────┐
│   RISCV Timing Simple CPU       │
│   (1 GHz clock)                 │
└──────────┬──────────┬───────────┘
           │          │
           │          │
    ┌──────▼─────┐  ┌─▼──────────┐
    │  L1 I-Cache│  │  L1 D-Cache│
    │  16kB, 4-way  │  16kB, 4-way
    └──────┬─────┘  └─┬──────────┘
           │          │
           └────┬─────┘
                │
           ┌────▼─────┐
           │  L2 Bus  │
           │ (L2XBar) │
           └────┬─────┘
                │
           ┌────▼──────┐
           │ L2 Cache  │
           │ 256kB, 8-way
           └────┬──────┘
                │
           ┌────▼──────┐
           │ Memory Bus│
           │(SystemXBar)│
           └────┬──────┘
                │
         ┌──────▼──────┐
         │   DDR3      │
         │   512 MiB   │
         └─────────────┘
```

## Test Results Summary

### Configuration Used
- L1I: 16kB, 4-way associative
- L1D: 16kB, 4-way associative
- L2: 256kB, 8-way associative

### Performance Metrics
- **Simulation Time**: 57,093,000 ticks (0.000057 seconds simulated)
- **Instructions**: 5,862
- **L1I Hit Rate**: 96.73%
- **L1D Hit Rate**: 93.34%
- **L2 Hit Rate**: 0.27% (cold start effect)

## Testing with Different Configurations

### Example 1: Larger L1 Caches
```bash
./build/RISCV/gem5.opt configs/cache_config.py \
    --l1i_size=32kB \
    --l1d_size=64kB \
    --l2_size=256kB \
    --l1_assoc=4 \
    --l2_assoc=8 \
    --binary=tests/test-progs/hello/bin/riscv/linux/hello
```

### Example 2: Higher Associativity
```bash
./build/RISCV/gem5.opt configs/cache_config.py \
    --l1i_size=16kB \
    --l1d_size=16kB \
    --l2_size=256kB \
    --l1_assoc=8 \
    --l2_assoc=16 \
    --binary=tests/test-progs/hello/bin/riscv/linux/hello
```

### Example 3: Larger L2 Cache
```bash
./build/RISCV/gem5.opt configs/cache_config.py \
    --l1i_size=16kB \
    --l1d_size=16kB \
    --l2_size=1MB \
    --l1_assoc=4 \
    --l2_assoc=8 \
    --binary=tests/test-progs/hello/bin/riscv/linux/hello
```

## Extracting Key Statistics

### Get Simulation Time
```bash
grep "simSeconds\|simTicks\|simInsts" m5out/stats.txt
```

### Get Cache Hit Rates
```bash
grep -E "system\.cpu\.(icache|dcache)\..*MissRate" m5out/stats.txt
```

### Get Cache Misses
```bash
grep -E "system\.(cpu\.(icache|dcache)|l2cache)\.demandMisses::total" m5out/stats.txt
```

### Get Cache Hits
```bash
grep -E "system\.(cpu\.(icache|dcache)|l2cache)\.demandHits::total" m5out/stats.txt
```
