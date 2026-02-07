# Part 2: Single Parameter Sweep - Complete Summary

## Assignment: Cache Hierarchy Optimization using gem5

**Date:** February 4, 2026  
**Parameter Investigated:** L1D Cache Size  
**Sweep Values:** 16kB, 32kB, 64kB, 128kB

---

## Deliverable 1: Custom Sweep Script ✓

**File:** `scripts/custom_sweep.py`

### Features:
- Automated parameter sweep for L1D cache size
- Keeps all other parameters constant (as per assignment)
- Runs gem5 simulations for each configuration
- Extracts key statistics from stats.txt files
- Generates results in both JSON and CSV formats
- Provides summary table after completion

### Fixed Parameters:
```python
Clock: 1GHz              # FIXED (assignment requirement)
Memory Mode: timing      # FIXED (assignment requirement)
Memory Size: 512MB       # FIXED (assignment requirement)
L1I Size: 16kB
L1I Associativity: 4
L2 Size: 256kB
L2 Associativity: 8
CPU Type: RiscvTimingSimpleCPU
```

### Execution:
```bash
python3 assignment_cache_optimization/scripts/custom_sweep.py
```

**Status:** ✓ Successfully executed all 4 simulations

---

## Deliverable 2: Results Table ✓

### CSV Format: [results.csv](./results/single_param_sweep/results.csv)

| L1D Size | Execution Time (ticks) | Execution Time (s) | L1D Hit Rate | L1D Misses | L2 Hit Rate |
|----------|------------------------|--------------------|--------------|-----------:|-------------|
| 16kB     | 128,830,948,000        | 0.128831          | 50.1%        | 2,137,287  | 99.8%       |
| 32kB     | 128,821,690,000        | 0.128822          | 50.1%        | 2,136,901  | 99.8%       |
| 64kB     | 80,343,964,000         | 0.080344          | 97.3%        | 116,958    | 96.3%       |
| 128kB    | 77,694,131,000         | 0.077694          | 99.8%        | 6,569      | 38.0%       |

### JSON Format: [results.json](./results/single_param_sweep/results.json)

Complete results with all statistics available in JSON format for further processing.

**Data Files:**
- 📊 [Download CSV Results](./results/single_param_sweep/results.csv)
- 📝 [Download JSON Results](./results/single_param_sweep/results.json)
- 📄 [Read Full Analysis](./results/single_param_sweep/ANALYSIS.md)

**Status:** ✓ Both formats generated successfully

---

## Deliverable 3: Plot - Parameter Value vs Execution Time ✓

**File:** `results/single_param_sweep/plot_execution_time.png`

![Execution Time vs L1D Cache Size](./results/single_param_sweep/plot_execution_time.png)

### Key Observations from Plot:
- **16kB → 32kB:** Negligible change (128.83B → 128.82B ticks, 0.01% improvement)
- **32kB → 64kB:** Dramatic drop (128.82B → 80.34B ticks, **37.6% improvement**)
- **64kB → 128kB:** Marginal improvement (80.34B → 77.69B ticks, 3.3% improvement)

### Visual Insights:
- Clear inflection point at 64kB
- Performance curve shows diminishing returns after 64kB
- Speedup annotations highlight performance gains

**Status:** ✓ High-quality plot generated (167 KB, 300 DPI)

---

## Deliverable 4: Plot - Parameter Value vs Hit Rate ✓

**File:** `results/single_param_sweep/plot_hit_rates.png`

![Hit Rates vs L1D Cache Size](./results/single_param_sweep/plot_hit_rates.png)

### Key Observations from Plot:
- **L1D Hit Rate Trend:**
  - 16kB/32kB: Plateau at ~50% (insufficient capacity)
  - 64kB: Sharp increase to 97.3% (critical threshold)
  - 128kB: Near-perfect at 99.8% (full coverage)

- **L2 Hit Rate Trend:**
  - 16kB/32kB: Very high at 99.8% (filters L1 misses)
  - 64kB: Drops to 96.3% (fewer L1 misses to filter)
  - 128kB: Plummets to 38.0% (minimal L1 misses, less reuse)

### Visual Insights:
- Dual-line plot clearly shows inverse relationship
- L1D hit rate improvement directly impacts L2 access patterns
- Percentage labels on each data point for clarity

**Status:** ✓ High-quality plot generated (194 KB, 300 DPI)

---

## Deliverable 5: Brief Analysis (200-300 words) ✓

**File:** `results/single_param_sweep/ANALYSIS.md`

### Summary of Analysis:

**Observed Trends:**
The experimental results reveal a non-linear relationship between L1D cache size and performance. At 16kB and 32kB, performance plateaus with ~50% hit rates because both are insufficient for the 192KB working set. A dramatic 37.7% performance improvement occurs at 64kB (97.3% hit rate), representing the critical inflection point. Further increase to 128kB provides only 3.3% additional improvement despite achieving 99.8% hit rate.

**Why This Effect Occurs:**
L1D cache size directly impacts capacity misses. The matrix multiplication benchmark exhibits poor spatial locality when accessing matrix B (column-wise traversal). Smaller caches (16kB/32kB) cannot retain multiple matrix rows simultaneously, resulting in ~50% miss rates. The 64kB cache crosses a critical threshold, enabling it to buffer multiple rows and exploit reuse patterns. At 128kB, nearly all frequently accessed data fits.

**Performance Saturation Point:**
Performance saturates at 64kB for practical purposes. While 128kB achieves better hit rate (99.8% vs 97.3%), the marginal execution time improvement (3.3%) does not justify doubling the cache size. The 64kB L1D cache offers the best performance-per-area ratio, providing 94% of maximum achievable performance improvement while using half the silicon area of the 128kB design.

**Word Count:** 200 words (main analysis sections)

**Status:** ✓ Complete analysis provided

---

## Additional Deliverable: Combined Plot

**File:** `results/single_param_sweep/plot_combined.png`

![Combined Analysis: Execution Time and Hit Rates](./results/single_param_sweep/plot_combined.png)

### Features:
- Dual y-axis plot showing both execution time and hit rate
- Single visualization for comprehensive understanding
- Clearly demonstrates correlation between hit rate and performance

**Status:** ✓ Bonus plot generated (226 KB, 300 DPI)

---

## Results Summary

### Performance Improvements:

| Configuration | Speedup | Absolute Time Reduction |
|---------------|---------|-------------------------|
| 16kB → 32kB   | 0.01%   | 9 million ticks         |
| 16kB → 64kB   | **37.7%** | **48.5 billion ticks**  |
| 16kB → 128kB  | **39.7%** | **51.1 billion ticks**  |

### Cache Efficiency:

| L1D Size | Capacity | Working Set Coverage | Hit Rate | Misses     |
|----------|----------|----------------------|----------|------------|
| 16kB     | 16 KB    | 8.3%                 | 50.1%    | 2,137,287  |
| 32kB     | 32 KB    | 16.7%                | 50.1%    | 2,136,901  |
| 64kB     | 64 KB    | 33.3%                | 97.3%    | 116,958    |
| 128kB    | 128 KB   | 66.7%                | 99.8%    | 6,569      |

**Working Set:** 3 matrices × 128×128 × 4 bytes = 192 KB

---

## Key Findings

1. **Critical Threshold Identified:** 64kB represents the inflection point where performance improves dramatically

2. **Non-Linear Behavior:** Performance does not scale linearly with cache size; doubling from 32kB to 64kB yields 37.6% speedup, but doubling again to 128kB yields only 3.3% additional gain

3. **Diminishing Returns:** Beyond 64kB, the cost-benefit ratio becomes unfavorable for this workload

4. **Working Set Insight:** Cache needs to hold ~33% of working set to achieve 97%+ hit rate, not 100%

5. **L2 Behavior Change:** As L1D hit rate improves, L2 sees fewer accesses but with different access patterns, reducing its hit rate (99.8% → 38.0%)

---

## Design Recommendations

### For Power-Constrained Systems:
**Recommendation:** 64kB L1D cache
- Provides 94% of maximum performance
- Uses 50% less area than 128kB
- Best performance-per-watt ratio

### For High-Performance Systems:
**Recommendation:** 128kB L1D cache
- Achieves maximum performance (39.7% improvement)
- 99.8% hit rate minimizes variance
- Worth the additional area for peak performance

### For Balanced Systems:
**Recommendation:** 64kB L1D cache
- Optimal cost-benefit trade-off
- 37.7% speedup is substantial
- Minimal performance left on the table (2% vs 128kB)

---

## Part 2 Deliverables Checklist

| Deliverable | Status | Location |
|-------------|--------|----------|
| ✓ custom_sweep.py script | Complete | `scripts/custom_sweep.py` |
| ✓ Results table (CSV) | Complete | `results/single_param_sweep/results.csv` |
| ✓ Results table (JSON) | Complete | `results/single_param_sweep/results.json` |
| ✓ Plot: Execution Time vs Parameter | Complete | `plot_execution_time.png` |
| ✓ Plot: Hit Rate vs Parameter | Complete | `plot_hit_rates.png` |
| ✓ Combined plot (bonus) | Complete | `plot_combined.png` |
| ✓ Analysis (200-300 words) | Complete | `ANALYSIS.md` |

---

## Reproducibility

To reproduce these results:

```bash
# 1. Run the custom sweep
python3 assignment_cache_optimization/scripts/custom_sweep.py

# 2. Generate plots (requires matplotlib in venv)
source venv/bin/activate
python assignment_cache_optimization/scripts/plot_results.py

# 3. View results
cat assignment_cache_optimization/results/single_param_sweep/results.csv
```

---

## Next Steps

Proceed to **Part 3: Multi-Parameter Analysis** where we will:
- Run full parameter sweep across multiple dimensions
- Analyze parameter interactions
- Compare configurations across L1D size, L2 size, and associativity
- Identify Pareto-optimal configurations

**Part 2 Complete!** ✓

All deliverables generated with clean code, comprehensive analysis, and high-quality visualizations.
