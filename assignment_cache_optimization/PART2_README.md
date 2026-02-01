# Part 2: Single Parameter Sweep - README

## Overview

This document describes the single parameter sweep analysis for the L2 cache size parameter, completed as part of Assignment 1 - Cache Hierarchy Optimization.

**Parameter Investigated:** L2 Cache Size
**Values Tested:** 128kB, 256kB, 512kB, 1MB
**Benchmark:** Matrix Multiplication (64×64 matrices)
**Date:** February 1, 2026

---

## Files and Directory Structure

```
assignment_cache_optimization/
├── benchmarks/
│   ├── matrix_multiply.c           # Source code for benchmark
│   └── matrix_multiply              # Compiled RISCV binary (716KB)
├── scripts/
│   ├── custom_sweep.py              # Parameter sweep automation script
│   └── plot_results.py              # Plotting and analysis script
└── results/
    └── single_param_sweep/
        ├── l2_128kB/                # Results for 128kB L2
        │   ├── stats.txt
        │   ├── config.ini
        │   └── config.json
        ├── l2_256kB/                # Results for 256kB L2
        ├── l2_512kB/                # Results for 512kB L2
        ├── l2_1MB/                  # Results for 1MB L2
        ├── results.json             # All results in JSON format
        ├── results.csv              # All results in CSV format
        ├── plot_execution_time.png  # Execution time vs L2 size
        ├── plot_hit_rates.png       # Hit rates vs L2 size
        ├── plot_combined.png        # Combined metrics view
        └── ANALYSIS.md              # Detailed analysis (this file)
```

---

## Part 2 Deliverables Checklist

- [x] **custom_sweep.py script** - Automated parameter sweep
- [x] **Results table (CSV)** - results.csv with all metrics
- [x] **Results table (JSON)** - results.json for programmatic access
- [x] **Plot: Parameter vs Execution Time** - plot_execution_time.png
- [x] **Plot: Parameter vs Hit Rate** - plot_hit_rates.png
- [x] **Additional Plot** - plot_combined.png (bonus visualization)
- [x] **Brief analysis (250 words)** - Included in ANALYSIS.md

---

## How to Reproduce

### Step 1: Compile the Benchmark

```bash
cd /home/sumitk/Desktop/gem5/assignment_cache_optimization/benchmarks
riscv64-linux-gnu-gcc -O2 -static matrix_multiply.c -o matrix_multiply
```

**Verify compilation:**
```bash
file matrix_multiply
# Should show: ELF 64-bit LSB executable, UCB RISC-V
```

### Step 2: Run Single Test (Optional)

Test with one configuration before running full sweep:

```bash
cd /home/sumitk/Desktop/gem5

./build/RISCV/gem5.opt configs/cache_config.py \
    --l1i_size=16kB \
    --l1d_size=16kB \
    --l2_size=256kB \
    --l1_assoc=4 \
    --l2_assoc=8 \
    --binary=assignment_cache_optimization/benchmarks/matrix_multiply
```

Expected output: "Matrix multiplication complete!" with checksum

### Step 3: Run Parameter Sweep

```bash
cd /home/sumitk/Desktop/gem5
python3 assignment_cache_optimization/scripts/custom_sweep.py
```

**Expected runtime:** ~1 minute (4 simulations)

This will:
- Run 4 simulations (L2 = 128kB, 256kB, 512kB, 1MB)
- Save results to `results/single_param_sweep/`
- Generate results.json and results.csv
- Display summary table

### Step 4: Generate Plots

```bash
cd /home/sumitk/Desktop/gem5
source venv/bin/activate  # Activate venv with matplotlib
python3 assignment_cache_optimization/scripts/plot_results.py
```

This generates three PNG plots and displays statistical analysis.

---

## Benchmark Description

### Matrix Multiplication Algorithm

```c
void matrix_multiply(int A[N][N], int B[N][N], int C[N][N]) {
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) {
            C[i][j] = 0;
            for (k = 0; k < N; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}
```

### Memory Characteristics

- **Matrix Size:** 64×64 = 4,096 elements per matrix
- **Data Type:** `int` (4 bytes)
- **Memory per Matrix:** 16,384 bytes (16KB)
- **Total Memory:** 49,152 bytes (~48KB for 3 matrices)
- **Access Pattern:** Row-major for A, column-major for B (causes cache misses)

### Why This Benchmark?

This benchmark is ideal for cache analysis because:
1. **Memory-intensive:** Performs 262,144 multiply-add operations
2. **Predictable access patterns:** Regular stride patterns
3. **Fits in L2:** Working set (~48KB) tests L2 effectiveness
4. **Cache-sensitive:** Performance depends on cache hierarchy

---

## Sweep Configuration Details

### Constant Parameters

All simulations used these fixed parameters:

| Parameter | Value | Description |
|-----------|-------|-------------|
| L1I Size | 16kB | L1 instruction cache size |
| L1D Size | 16kB | L1 data cache size |
| L1 Associativity | 4-way | Both L1I and L1D |
| L2 Associativity | 8-way | L2 cache |
| CPU | RiscvTimingSimpleCPU | Simple in-order CPU |
| Clock | 1 GHz | System clock frequency |
| Memory | DDR3_1600_8x8 | Memory controller |

### Swept Parameter: L2 Cache Size

| Configuration | L2 Size | Working Set Ratio |
|--------------|---------|-------------------|
| 1 | 128kB | 2.6× working set |
| 2 | 256kB | 5.2× working set |
| 3 | 512kB | 10.4× working set |
| 4 | 1MB | 20.8× working set |

---

## Results Summary

### Performance Metrics

| Metric | 128kB | 256kB | 512kB | 1MB |
|--------|-------|-------|-------|-----|
| **Execution Time (ticks)** | 7,793,604,000 | 7,793,233,000 | 7,793,233,000 | 7,793,233,000 |
| **Simulated Time (ms)** | 7.794 | 7.793 | 7.793 | 7.793 |
| **Instructions** | 2,327,387 | 2,327,387 | 2,327,387 | 2,327,387 |
| **IPC** | 0.299 | 0.299 | 0.299 | 0.299 |

### Cache Hit Rates

| Cache Level | 128kB | 256kB | 512kB | 1MB |
|-------------|-------|-------|-------|-----|
| **L1I Hit Rate** | 99.98% | 99.98% | 99.98% | 99.98% |
| **L1D Hit Rate** | 96.56% | 96.56% | 96.56% | 96.56% |
| **L2 Hit Rate** | 92.99% | 93.00% | 93.00% | 93.00% |

### Cache Misses

| Cache Level | 128kB | 256kB | 512kB | 1MB |
|-------------|-------|-------|-------|-----|
| **L1I Misses** | 408 | 408 | 408 | 408 |
| **L1D Misses** | 28,564 | 28,564 | 28,564 | 28,564 |
| **L2 Misses** | 2,032 | 2,029 | 2,029 | 2,029 |

---

## Key Findings

### 1. Performance Saturation

Performance saturates at **256kB L2 cache**:
- 128kB → 256kB: 0.0048% improvement (371,000 ticks)
- 256kB → 512kB: 0% improvement
- 512kB → 1MB: 0% improvement

### 2. Working Set Analysis

The 64×64 matrix multiplication has a **48KB working set**:
- Even 128kB L2 (2.6× working set) provides excellent performance
- 256kB L2 (5.2× working set) completely eliminates capacity misses
- Larger caches provide no additional benefit

### 3. L1 Cache Effectiveness

L1D cache (16kB) achieves 96.56% hit rate:
- Can hold ~1/3 of a single matrix
- Good temporal locality within row/column operations
- 28,564 misses are primarily conflict/capacity misses

### 4. Compulsory Misses Dominate L2

~2,000 L2 misses are unavoidable:
- Cold-start misses when first loading data
- Cannot be eliminated by increasing cache size
- Represent only 7% of L1D misses

---

## Interpretation & Insights

### Why Such Small Improvement?

The minimal performance gain from larger L2 caches occurs because:

1. **Small Working Set:** 48KB fits comfortably even in 128kB L2
2. **High L1 Hit Rate:** 96.56% of data accesses hit in L1D
3. **Excellent Locality:** Regular access patterns maximize cache effectiveness
4. **Compulsory Misses:** Remaining misses are cold-start, not capacity-related

### When Would Larger L2 Help?

Larger L2 caches would be beneficial for:
- **Larger matrices** (e.g., 256×256 = 768KB working set)
- **Multiple concurrent workloads**
- **Poor temporal locality** (random access patterns)
- **Multi-threaded applications** with shared data

### Cost-Performance Trade-off

| L2 Size | Relative Cost | Relative Performance | Efficiency |
|---------|---------------|----------------------|------------|
| 128kB | 1.0× | 99.995% | Best cost |
| 256kB | 2.0× | 100.000% | Saturation point |
| 512kB | 4.0× | 100.000% | Diminishing returns |
| 1MB | 8.0× | 100.000% | Wasted capacity |

**Recommendation:** Use 256kB L2 for this workload class.

---

## Script Documentation

### custom_sweep.py

**Purpose:** Automate parameter sweep experiments

**Features:**
- Configurable sweep parameter and values
- Automatic gem5 execution with different configurations
- Stats parsing and data extraction
- JSON and CSV output generation
- Summary table display

**Usage:**
```bash
python3 assignment_cache_optimization/scripts/custom_sweep.py
```

**Customization:**
Edit these variables in the script:
```python
SWEEP_PARAMETER = 'l2_size'  # Parameter to vary
SWEEP_VALUES = ['128kB', '256kB', '512kB', '1MB']  # Values to test
DEFAULT_PARAMS = {...}  # Parameters to keep constant
```

### plot_results.py

**Purpose:** Generate visualizations and statistical analysis

**Features:**
- Execution time vs parameter plot
- Hit rates vs parameter plot
- Combined metrics visualization
- Statistical analysis (min, max, saturation point)

**Requirements:**
- matplotlib (installed in venv)
- numpy (installed in venv)

**Usage:**
```bash
source venv/bin/activate
python3 assignment_cache_optimization/scripts/plot_results.py
```

---

## Plots Description

### plot_execution_time.png

- **X-axis:** L2 Cache Size (128kB to 1MB)
- **Y-axis:** Execution Time (billion ticks)
- **Shows:** Minimal performance improvement, saturation at 256kB
- **Annotations:** Performance improvement percentage

### plot_hit_rates.png

- **X-axis:** L2 Cache Size
- **Y-axis:** Hit Rate (%)
- **Lines:** L1I (green), L1D (red), L2 (blue)
- **Shows:** L1 rates constant, L2 rate minimal variation

### plot_combined.png

Two subplots:
1. **Left:** Execution time vs L2 size
2. **Right:** L2 misses (bars) and L2 hit rate (line) vs L2 size

---

## Troubleshooting

### Issue: Simulation Timeout

**Symptom:** Simulation runs for >10 minutes
**Solution:** Check binary is compiled correctly for RISCV

### Issue: Missing matplotlib

**Symptom:** `ModuleNotFoundError: No module named 'matplotlib'`
**Solution:** Use venv: `source venv/bin/activate`

### Issue: Different Results

**Symptom:** Your results don't match documented values
**Possible Causes:**
- Different matrix size (check `#define N` in matrix_multiply.c)
- Different compiler optimization (should be `-O2`)
- Different cache configuration

---

## Extending This Analysis

### Test Different Matrix Sizes

Edit `matrix_multiply.c`:
```c
#define N 128  // Change from 64 to 128
```

Recompile and re-run sweep. Larger matrices will show more benefit from larger L2.

### Test Different Parameters

Modify `custom_sweep.py`:

**Example: Sweep L1D size instead:**
```python
SWEEP_PARAMETER = 'l1d_size'
SWEEP_VALUES = ['16kB', '32kB', '64kB']
DEFAULT_PARAMS = {
    'l1i_size': '16kB',
    'l2_size': '256kB',  # Keep L2 constant
    'l1_assoc': 4,
    'l2_assoc': 8
}
```

---

## Conclusion

This single parameter sweep demonstrates that:
1. L2 cache size has **minimal impact** for workloads smaller than cache capacity
2. Performance **saturates quickly** once working set fits in cache
3. **Cost-effective sizing** requires understanding working set characteristics
4. The matrix multiplication benchmark is an excellent vehicle for cache analysis

---

## Next Steps

Proceed to **Part 3: Multi-Parameter Analysis** which will:
- Sweep multiple parameters simultaneously
- Identify parameter interactions
- Find Pareto-optimal configurations
- Analyze trade-offs between multiple cache dimensions

---

**Author:** Assignment 1 - Cache Hierarchy Optimization
**Date:** February 1, 2026
**Platform:** gem5 v25.1.0.0, RISCV ISA
