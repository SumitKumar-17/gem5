# Assignment 1: Cache Hierarchy Optimization using gem5

**Course:** CS60003 High Performance in Computer Architecture
**Authors:** Sumit Kumar(22CS30056) and Aviral Singh(22CS30015)
**Platform:** gem5 v25.1.0.0, RISCV ISA
**Benchmark:** Matrix Multiplication (64×64)

---

## Overview

This assignment investigates how different cache configurations affect processor performance using gem5 simulation. Through comprehensive parameter sweeps and data-driven analysis, we identify optimal cache configurations for different system types.

**Total Configurations Tested:** 112 (4 single-parameter + 108 multi-parameter)
**Key Finding:** L1D cache size is 10× more important than any other parameter

---

## Quick Start

### Prerequisites
- gem5 with RISCV ISA: `build/RISCV/gem5.opt`
- Python 3.x with matplotlib and numpy
- RISCV cross-compiler: `riscv64-linux-gnu-gcc`

### Run Complete Analysis
```bash
cd /home/sumitk/Desktop/gem5

# Part 1: Test configuration
./build/RISCV/gem5.opt configs/cache_config.py \
    --l1i_size=16kB --l1d_size=16kB --l2_size=256kB \
    --l1_assoc=4 --l2_assoc=8 \
    --binary=assignment_cache_optimization/benchmarks/matrix_multiply

# Part 2: Single parameter sweep
python3 assignment_cache_optimization/scripts/custom_sweep.py

# Part 3: Full parameter sweep
python3 scripts/cache_sweep.py

# Part 4: Design analysis
source venv/bin/activate
python3 scripts/part4_analysis.py
```

---

## Directory Structure

```
assignment_cache_optimization/
├── benchmarks/
│   ├── matrix_multiply.c          # Source code
│   └── matrix_multiply            # RISCV binary (716KB)
├── configs/
│   └── cache_config.py            # gem5 configuration script
├── scripts/
│   ├── custom_sweep.py            # Part 2: L2 size sweep
│   ├── plot_results.py            # Part 2: Visualization
│   ├── cache_sweep.py             # Part 3: Multi-parameter sweep
│   ├── analyze_sweep.py           # Part 3: Analysis
│   └── part4_analysis.py          # Part 4: Pareto analysis
├── results/
│   ├── single_param_sweep/        # Part 2 results
│   │   ├── results.json
│   │   ├── results.csv
│   │   ├── plot_*.png (3 plots)
│   │   └── ANALYSIS.md
│   └── full_sweep_results/        # Part 3 results
│       ├── results.json (108 configs)
│       ├── analysis_plots/
│       │   ├── l1d_size_impact.png
│       │   ├── l2_size_impact.png
│       │   ├── associativity_impact.png
│       │   ├── performance_distribution.png
│       │   ├── pareto_frontier.png
│       │   ├── performance_cost_tradeoff.png
│       │   └── ninety_percent_threshold.png
│       └── [108 simulation directories]
├── PART1_OUTPUT.txt               # Part 1 summary
├── PART1_README.md
├── PART1_config.ini
├── PART1_stats.txt
├── PART2_README.md                # Part 2 documentation
├── PART2_SUMMARY.txt
├── PART3_SUMMARY.md               # Part 3 analysis
├── PART4_DESIGN_ANALYSIS.md       # Part 4 Q&A (1,210 words)
├── PART4_RECOMMENDATION_TABLE.md  # Design recommendations
├── PART4_SUMMARY.txt
└── README.md                      # This file
```

---

## Assignment Parts Summary

### Part 1: Environment Setup 

**Deliverables:**
- Cache configuration script (`configs/cache_config.py`)
- Test run with default parameters
- Output logs and statistics

**Key Results:**
- L1I: 99.98% hit rate
- L1D: 96.56% hit rate
- L2: 93.00% hit rate
- Execution: 7.79B ticks

---

### Part 2: Single Parameter Sweep 

**Parameter Swept:** L2 Size (128kB, 256kB, 512kB, 1MB)

**Deliverables:**
- `custom_sweep.py` script
- Results (CSV, JSON)
- 3 visualization plots
- Analysis document (250 words)

**Key Finding:** L2 size has minimal impact (0.0048% variation) because working set (48KB) fits in all tested sizes. Performance saturates at 256kB.

---

### Part 3: Multi-Parameter Analysis 

**Parameters Swept:**
- L1D Size: 16kB, 32kB, 64kB
- L2 Size: 128kB, 256kB, 512kB, 1MB
- L1 Associativity: 2, 4, 8
- L2 Associativity: 4, 8, 16
- **Total:** 108 configurations

**Deliverables:**
- `results.json` (108 configs)
- 4 analysis plots
- Summary statistics
- Top 3 configurations by each metric

**Key Finding:** L1D size dominates performance (13.1% range), L1 associativity matters (3%), L2 config irrelevant (<0.1%).

**Best Configuration:** 64kB L1D / 128kB L2 / 4-way / 4-way
- Time: 7.148B ticks
- L1D Hit: 99.80%

---

### Part 4: Design Analysis & Recommendations 

**Deliverables:**
- Answers to 4 design questions 
- 3 Pareto analysis plots
- Design recommendation table (4 system types)
- Comprehensive justifications

**Key Findings:**

**Question A (Performance Bottlenecks):**
- L1D misses dominate execution time (13.1% impact)
- Only 0.0029% of memory requests reach main memory
- L2 and memory stalls are NOT bottlenecks

**Question B (Cache Efficiency):**
- L1I has best hit rate (99.98%) due to tight loops
- L2 size and associativity don't matter for this workload
- High L2 hit rate paradoxically indicates poor performance

**Question C (Cost-Benefit):**
- Smallest @ 90% peak: 144KB (16kB/128kB/2/4)
- Best balanced: 160KB (32kB/128kB/4/4) at 99.7% peak
- Estimated direct-mapped penalty: 6-9%

**Question D (Design Recommendations):**
Three optimal configurations identified:
1. **Balanced** (64kB/128kB/4/4): Best overall ⭐
2. **Power** (32kB/128kB/2/4): 96% perf, 40% power savings
3. **High-Perf** (64kB/256kB/4/4): Peak perf with safety margin

---

## Key Results Summary

### Parameter Impact Ranking

1. **L1D Size** ⭐⭐⭐⭐⭐ (13.1% impact)
   - 16kB → 64kB: 1.08B ticks faster
   - Dominant factor in all experiments

2. **L1 Associativity** ⭐⭐⭐ (3-4% impact)
   - 2-way → 4-way: Significant improvement
   - 8-way: Actually slower (latency penalty)

3. **L2 Size** ⭐ (<0.1% impact)
   - Minimal effect for this workload
   - Working set fits in smallest L2

4. **L2 Associativity** (Negligible)
   - No measurable performance difference

### Pareto-Optimal Configurations

Three configurations lie on the Pareto frontier:

| Rank | Config | Cache | Performance | Status |
|------|--------|-------|-------------|--------|
| 1 | 64kB/128kB/4/4 | 192KB | 7.148B ticks | **Recommended** ⭐ |
| 2 | 32kB/128kB/4/4 | 160KB | 7.172B ticks | Power option |
| 3 | 16kB/128kB/2/16 | 144KB | 7.736B ticks | Ultra-low power |

All other 105 configurations are dominated (suboptimal).

---

## Recommended Configurations

### 🎯 Balanced System (Default Recommendation)
```
L1D: 64kB, 4-way
L2:  128kB, 4-way
Performance: 100% (best possible)
Cost: Moderate (192KB total)
Use For: General-purpose, servers, desktops
```

### 🔋 Power-Constrained System
```
L1D: 32kB, 2-way
L2:  128kB, 4-way
Performance: 96.1% of peak
Power Savings: ~40%
Use For: Mobile, IoT, battery-powered
```

### ⚡ High-Performance System
```
L1D: 64kB, 4-way
L2:  256kB, 4-way
Performance: 100% with safety margin
Cost: Higher (320KB total)
Use For: HPC, real-time, mission-critical
```

---

## Key Insights

### 1. L1D Dominance
**Finding:** L1D cache size is 10× more important than any other parameter.
**Implication:** Prioritize L1D in silicon budget allocation.

### 2. Associativity Sweet Spot
**Finding:** 4-way L1 associativity is optimal; 8-way performs worse.
**Implication:** More isn't always better—find the balance point.

### 3. L2 Irrelevance
**Finding:** L2 configuration has <0.1% impact for this workload.
**Implication:** Don't waste silicon on oversized L2 when working set fits L1D.

### 4. Hit Rate Paradox
**Finding:** Highest L2 hit rate (95.7%) = worst performance (8.23B ticks).
**Implication:** High L2 hits indicate poor L1D, not good L2. Optimize total time, not individual metrics.

### 5. Multi-Parameter Essential
**Finding:** Single-parameter sweep missed the dominant factor (L1D size).
**Implication:** Always vary suspected bottlenecks to avoid catastrophic oversight.

---

## Benchmark Details

**Program:** Matrix Multiplication (standard triple-nested loop)
**Matrix Size:** 64×64 elements (4,096 elements per matrix)
**Data Type:** int (4 bytes)
**Working Set:** 49,152 bytes (~48KB for 3 matrices)
**Memory Pattern:** Row-major for A, column-major for B (creates cache misses)

**Compilation:**
```bash
riscv64-linux-gnu-gcc -O2 -static matrix_multiply.c -o matrix_multiply
```

**Expected Output:**
```
Matrix size: 64 x 64
Checksum: 28895516160
Sample results:
  C[0][0] = 85344
  C[32][32] = 8472928
  C[63][63] = 13576488
```

---

## Reproduction Instructions

### Complete Assignment from Scratch

```bash
# 1. Navigate to gem5 directory
cd /home/sumitk/Desktop/gem5

# 2. Verify gem5 build
ls -lh build/RISCV/gem5.opt  # Should exist (~954MB)

# 3. Compile benchmark
cd assignment_cache_optimization/benchmarks
riscv64-linux-gnu-gcc -O2 -static matrix_multiply.c -o matrix_multiply
cd ../..

# 4. Test configuration (Part 1)
./build/RISCV/gem5.opt configs/cache_config.py \
    --l1i_size=16kB --l1d_size=16kB --l2_size=256kB \
    --l1_assoc=4 --l2_assoc=8 \
    --binary=assignment_cache_optimization/benchmarks/matrix_multiply

# 5. Run single parameter sweep (Part 2, ~60 seconds)
python3 assignment_cache_optimization/scripts/custom_sweep.py

# 6. Generate Part 2 plots
source venv/bin/activate
python3 assignment_cache_optimization/scripts/plot_results.py

# 7. Run full parameter sweep (Part 3, ~18 minutes)
python3 scripts/cache_sweep.py \
    --gem5=build/RISCV/gem5.opt \
    --config=configs/cache_config.py \
    --binary=assignment_cache_optimization/benchmarks/matrix_multiply \
    --output=full_sweep_results

# 8. Analyze full sweep (Part 3)
python3 scripts/analyze_sweep.py \
    assignment_cache_optimization/results/full_sweep_results/results.json \
    --output=analysis_plots

# 9. Generate Pareto analysis (Part 4)
python3 scripts/part4_analysis.py

# 10. Review all documentation
ls assignment_cache_optimization/PART*.md
```
---

## Validation

### Expected Results for Optimal Configuration

Run:
```bash
./build/RISCV/gem5.opt configs/cache_config.py \
    --l1i_size=16kB --l1d_size=64kB --l2_size=128kB \
    --l1_assoc=4 --l2_assoc=4 \
    --binary=assignment_cache_optimization/benchmarks/matrix_multiply
```

Expected:
```
Execution: 7,147,636,000 ticks
L1I Hit Rate: 99.98%
L1D Hit Rate: 99.80%
L2 Hit Rate: 1.46%
L1D Misses: 1,639
L2 Misses: 24
```

If your results differ:
- Check matrix size is N=64 in matrix_multiply.c
- Verify -O2 optimization flag in compilation
- Confirm gem5 version matches (v25.1.0.0)
- Check cache parameters exactly match



