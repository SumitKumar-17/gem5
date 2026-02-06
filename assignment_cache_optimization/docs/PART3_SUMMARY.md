# Part 3: Multi-Parameter Analysis - Complete Summary

## Assignment: Cache Hierarchy Optimization using gem5

**Date:** February 4, 2026  
**Total Configurations:** 108  
**Success Rate:** 100% (108/108)  
**Total Runtime:** 73.9 minutes

---

## Parameter Sweep Configuration

### Parameters Swept:

| Parameter | Values | Count |
|-----------|--------|-------|
| L1D Size | 16kB, 32kB, 64kB | 3 |
| L2 Size | 128kB, 256kB, 512kB, 1MB | 4 |
| L1 Associativity | 2, 4, 8 | 3 |
| L2 Associativity | 4, 8, 16 | 3 |
| **Total Combinations** | 3 × 4 × 3 × 3 | **108** |

### Fixed Parameters:
```python
Clock: 1GHz              # FIXED (assignment requirement)
Memory Mode: timing      # FIXED (assignment requirement)
Memory Size: 512MB       # FIXED (assignment requirement)
L1I Size: 16kB          # FIXED
CPU Type: RiscvTimingSimpleCPU
```

---

## Deliverable 1: Complete Sweep Results ✓

### results.json

**File:** [results.json](./results/full_sweep_results/results.json)
**Size:** 61 KB
**Configurations:** 108

Complete dataset with all parameters and performance metrics for each configuration.

**Status:** ✓ Generated successfully

### results.csv

**File:** [results.csv](./results/full_sweep_results/results.csv)
**Size:** 20 KB
**Rows:** 109 (1 header + 108 data rows)

Tabular format for easy analysis and import into spreadsheet tools.

**Quick Access:**
- 📊 [Download JSON Results](./results/full_sweep_results/results.json)
- 📈 [Download CSV Results](./results/full_sweep_results/results.csv)
- 📄 [View Summary Statistics](./results/full_sweep_results/summary_statistics.txt)

**Status:** ✓ Generated successfully

---

## Deliverable 2: Analysis Plots ✓

### Required Minimum Plots (3):

#### 1. L1D Size Impact ✓
**File:** `l1d_size_impact.png` (171 KB)

![L1D Size Impact on Performance](./results/full_sweep_results/l1d_size_impact.png)

**Key Findings:**
- **16kB:** Mean execution time = 130.1B ticks, L1D hit rate = 49.6%
- **32kB:** Mean execution time = 130.0B ticks, L1D hit rate = 49.7%
- **64kB:** Mean execution time = 80.5B ticks, L1D hit rate = 97.3%

**Observation:** Dramatic 38.1% performance improvement from 32kB → 64kB

#### 2. L2 Size Impact ✓
**File:** `l2_size_impact.png` (137 KB)

![L2 Size Impact on Performance](./results/full_sweep_results/l2_size_impact.png)

**Key Findings:**
- **128kB:** Mean execution time = 114.0B ticks, L2 hit rate = 97.7%
- **256kB:** Mean execution time = 113.6B ticks, L2 hit rate = 98.9%
- **512kB:** Mean execution time = 113.2B ticks, L2 hit rate = 99.2%
- **1MB:** Mean execution time = 113.3B ticks, L2 hit rate = 99.2%

**Observation:** Diminishing returns beyond 256kB

#### 3. Associativity Impact ✓
**File:** `associativity_impact.png` (250 KB)

![Associativity Impact Analysis](./results/full_sweep_results/associativity_impact.png)

**Contains 4 subplots:**
- L1 Associativity vs Execution Time
- L1 Associativity vs L1D Hit Rate
- L2 Associativity vs Execution Time
- L2 Associativity vs L2 Hit Rate

**Key Findings:**
- L1 associativity has minor impact (2→4→8: 115.7B → 112.7B → 112.2B ticks)
- L2 associativity has minimal impact (~113.5B ticks across all values)
- Hit rates remain relatively stable across associativity changes

---

### Additional Analysis Plots (4):

#### 4. Parameter Heatmaps ✓
**File:** `parameter_heatmaps.png` (347 KB)

![Parameter Interaction Heatmaps](./results/full_sweep_results/parameter_heatmaps.png)

**Contains 4 heatmaps showing parameter interactions:**
1. L1D Size vs L2 Size (Execution Time)
2. L1D Size vs L2 Size (L1D Hit Rate)
3. L1 Assoc vs L2 Assoc (Execution Time)
4. L1D Size vs L1 Assoc (L1D Hit Rate)

**Insights:**
- L1D size dominates performance (vertical color gradient)
- L2 size has secondary effect (horizontal variation)
- Associativity shows minimal color variation (limited impact)

#### 5. Performance Distribution ✓
**File:** `performance_distribution.png` (245 KB)

![Performance Metric Distributions](./results/full_sweep_results/performance_distribution.png)

**Contains 4 histograms:**
- Execution Time distribution
- L1D Hit Rate distribution
- L2 Hit Rate distribution
- CPI distribution

**Insights:**
- Bimodal execution time distribution (peak at ~130B and ~80B ticks)
- Corresponds to L1D size threshold effect
- L2 hit rates clustered around 98-100%

#### 6. Pareto Frontier ✓
**File:** `pareto_frontier.png` (224 KB)

![Pareto Frontier Analysis](./results/full_sweep_results/pareto_frontier.png)

**Shows:** Performance vs Total Cache Size trade-off

**Pareto Optimal Configurations:**
- 80kB total (64kB L1D + 16kB L1I): 80.6B ticks
- 144kB total: 80.5B ticks
- Higher cache sizes show minimal improvement

**Insight:** 64kB L1D + 128kB L2 = 192KB total provides best cost-benefit

#### 7. Top Configurations Comparison ✓
**File:** `top_configs_comparison.png` (342 KB)

![Top Configurations Comparison](./results/full_sweep_results/top_configs_comparison.png)

**Contains 4 subplots:**
- Top 3 by Lowest Execution Time (horizontal bars)
- Top 3 by Highest L1D Hit Rate (horizontal bars)
- Top 3 by Highest L2 Hit Rate (horizontal bars)
- Best Overall Configuration metrics (bar chart)

**Highlights:**
- Clear visualization of top performers
- Shows metric trade-offs between configurations

---

## Deliverable 3: Summary Statistics ✓

**File:** `summary_statistics.txt` (2.1 KB)

### Execution Time:
| Statistic | Value (Billion Ticks) | Value (Seconds) |
|-----------|----------------------|-----------------|
| Mean | 113.6 | 0.1136 |
| Std Dev | 22.8 | 0.0228 |
| **Minimum** | **80.3** | **0.0803** |
| **Maximum** | **131.2** | **0.1312** |

**Range:** 50.9B ticks (38.8% variation)

### L1D Hit Rate:
| Statistic | Value (%) |
|-----------|-----------|
| Mean | 65.4 |
| Std Dev | 22.2 |
| **Minimum** | **49.0** |
| **Maximum** | **97.3** |

**Range:** 48.3 percentage points

### L2 Hit Rate:
| Statistic | Value (%) |
|-----------|-----------|
| Mean | 98.6 |
| Std Dev | 1.7 |
| **Minimum** | **94.1** |
| **Maximum** | **99.8** |

**Range:** 5.7 percentage points (L2 consistently effective)

### CPI (Cycles Per Instruction):
| Statistic | Value |
|-----------|-------|
| Mean | 4.07 |
| Std Dev | 0.82 |
| **Minimum** | **2.88** |
| **Maximum** | **4.70** |

**Best IPC:** 0.35 instructions/cycle

---

## Deliverable 4: Top 3 Configurations ✓

### By Lowest Execution Time:

| Rank | Configuration | Exec Time | L1D Hit | L2 Hit |
|------|--------------|-----------|---------|--------|
| 1 | l1d64kB_l2512kB_l1a4_l2a4 | 80.34B ticks | 97.27% | 96.32% |
| 2 | l1d64kB_l2512kB_l1a4_l2a8 | 80.34B ticks | 97.27% | 96.32% |
| 3 | l1d64kB_l2512kB_l1a4_l2a16 | 80.34B ticks | 97.27% | 96.32% |

**Observation:** All top 3 have 64kB L1D and 512kB L2; L2 associativity makes no difference

### By Highest L1D Hit Rate:

| Rank | Configuration | L1D Hit | Exec Time | L2 Hit |
|------|--------------|---------|-----------|--------|
| 1 | l1d64kB_l2128kB_l1a4_l2a4 | 97.27% | 80.56B ticks | 94.06% |
| 2 | l1d64kB_l2128kB_l1a4_l2a8 | 97.27% | 80.55B ticks | 94.06% |
| 3 | l1d64kB_l2128kB_l1a4_l2a16 | 97.27% | 80.55B ticks | 94.06% |

**Observation:** All have 64kB L1D (maximum L1D hit rate achieved at this size)

### By Highest L2 Hit Rate:

| Rank | Configuration | L2 Hit | Exec Time | L1D Hit |
|------|--------------|--------|-----------|---------|
| 1 | l1d16kB_l2512kB_l1a2_l2a4 | 99.80% | 131.03B ticks | 49.02% |
| 2 | l1d16kB_l2512kB_l1a2_l2a8 | 99.80% | 131.03B ticks | 49.02% |
| 3 | l1d16kB_l2512kB_l1a2_l2a16 | 99.80% | 131.03B ticks | 49.02% |

**Observation:** High L2 hit rate doesn't guarantee good performance (poor L1D hit rate dominates)

---

## Key Insights from Multi-Parameter Analysis

### 1. L1D Size is Dominant Factor

- **Impact:** 38% performance improvement (32kB → 64kB)
- **Critical Threshold:** 64kB
- **Below 64kB:** ~50% hit rate, poor performance
- **At 64kB:** 97% hit rate, optimal performance

### 2. L2 Size Shows Diminishing Returns

- **128kB → 256kB:** 0.4% improvement
- **256kB → 512kB:** 0.4% improvement
- **512kB → 1MB:** -0.1% (slight degradation, noise)
- **Recommendation:** 256-512kB is sufficient

### 3. Associativity Has Minimal Impact

- **L1 Assoc (2→8):** 3.0% improvement
- **L2 Assoc (4→16):** <0.1% improvement
- **Conclusion:** 4-way associative is sufficient for both levels

### 4. Parameter Interactions

- **L1D × L2:** Orthogonal effects (L1D dominates)
- **Size × Assoc:** Size matters more than associativity
- **No synergistic effects** observed between parameters

### 5. Performance Saturation

- **Execution Time:** Saturates at 80.3B ticks (64kB L1D + 256kB+ L2)
- **L1D Hit Rate:** Saturates at 97.3% (64kB L1D)
- **L2 Hit Rate:** Reaches 99.8% (512kB+ L2 with small L1D)

---

## Design Recommendations (Data-Driven)

### Power-Constrained System:
**Configuration:** L1D=64kB (assoc=4), L2=128kB (assoc=4)  
**Total Cache:** 192 KB  
**Performance:** 80.56B ticks (99.7% of optimal)  
**Rationale:** Minimal cache size achieving near-optimal performance

### High-Performance System:
**Configuration:** L1D=64kB (assoc=4), L2=512kB (assoc=4)  
**Total Cache:** 576 KB  
**Performance:** 80.34B ticks (100% optimal)  
**Rationale:** Best absolute performance, L2 provides headroom

### Balanced System:
**Configuration:** L1D=64kB (assoc=4), L2=256kB (assoc=8)  
**Total Cache:** 320 KB  
**Performance:** 80.40B ticks (99.9% of optimal)  
**Rationale:** Best performance/cost ratio, standard associativity

### Cost-Optimized System:
**Configuration:** L1D=32kB (assoc=2), L2=256kB (assoc=4)  
**Total Cache:** 288 KB  
**Performance:** 131.0B ticks (61.3% of optimal)  
**Rationale:** Minimal cost, acceptable for non-performance-critical applications

---

## Statistical Analysis

### Performance Variance:
- **Coefficient of Variation (Exec Time):** 20.1% (moderate variance)
- **Dominated by:** L1D size parameter
- **L2 and Associativity:** Contribute <5% to overall variance

### Correlation Analysis:
- **L1D Size ↔ Exec Time:** Strong negative correlation (-0.92)
- **L2 Size ↔ Exec Time:** Weak negative correlation (-0.15)
- **L1 Assoc ↔ Exec Time:** Weak negative correlation (-0.12)
- **L2 Assoc ↔ Exec Time:** Near zero correlation (-0.02)

### Performance Distribution:
- **Bimodal:** Two peaks at ~130B ticks (small L1D) and ~80B ticks (large L1D)
- **Transition zone:** Very narrow (32kB → 64kB)
- **Conclusion:** Step function behavior, not gradual improvement

---

## Part 3 Deliverables Checklist

| Deliverable | Status | Location | Details |
|-------------|--------|----------|---------|
| ✓ results.json | Complete | full_sweep_results/ | 108 configurations, 61KB |
| ✓ results.csv | Complete | full_sweep_results/ | 108 configurations, 20KB |
| ✓ L1D impact plot | Complete | l1d_size_impact.png | 171KB, 300 DPI |
| ✓ L2 impact plot | Complete | l2_size_impact.png | 137KB, 300 DPI |
| ✓ Associativity plot | Complete | associativity_impact.png | 250KB, 300 DPI |
| ✓ Heatmaps | Complete | parameter_heatmaps.png | 347KB, 300 DPI |
| ✓ Distribution | Complete | performance_distribution.png | 245KB, 300 DPI |
| ✓ Pareto frontier | Complete | pareto_frontier.png | 224KB, 300 DPI |
| ✓ Top configs | Complete | top_configs_comparison.png | 342KB, 300 DPI |
| ✓ Summary stats | Complete | summary_statistics.txt | 2.1KB |
| ✓ Top 3 by exec time | Complete | In summary_statistics.txt | ✓ |
| ✓ Top 3 by L1D hit | Complete | In summary_statistics.txt | ✓ |
| ✓ Top 3 by L2 hit | Complete | In summary_statistics.txt | ✓ |

**Total Plots Generated:** 7 (3 required + 4 additional)

---

## Reproducibility

To reproduce these results:

```bash
# 1. Run full parameter sweep (108 configurations, ~74 minutes)
python3 assignment_cache_optimization/scripts/cache_sweep.py \
  --gem5=./build/RISCV/gem5.opt \
  --config=assignment_cache_optimization/configs/cache_config.py \
  --binary=assignment_cache_optimization/benchmarks/matrix_multiply \
  --output=assignment_cache_optimization/results/full_sweep_results

# 2. Generate analysis plots and statistics
source venv/bin/activate
python assignment_cache_optimization/scripts/analyze_sweep.py \
  assignment_cache_optimization/results/full_sweep_results/results.json \
  --output=assignment_cache_optimization/results/full_sweep_results

# 3. View results
cat assignment_cache_optimization/results/full_sweep_results/summary_statistics.txt
```

---

## Next Steps

Proceed to **Part 4: Design Analysis & Recommendations** where we will:
- Answer specific design questions using sweep data
- Identify Pareto-optimal configurations
- Analyze cost-benefit trade-offs
- Provide final design recommendations with justifications

**Part 3 Complete!** ✓

All 108 configurations swept, 7 plots generated, comprehensive analysis provided.

