# Part 2: Single Parameter Sweep - Analysis

## Parameter Investigated: L2 Cache Size

**Date:** February 1, 2026
**Benchmark:** Matrix Multiplication (64×64)
**Parameter Range:** 128kB, 256kB, 512kB, 1MB
**Constant Parameters:** L1I=16kB (4-way), L1D=16kB (4-way), L2 assoc=8-way

---

## Experimental Results Summary

| L2 Size | Execution Time (ticks) | L1I Hit Rate | L1D Hit Rate | L2 Hit Rate | L2 Misses |
|---------|------------------------|--------------|--------------|-------------|-----------|
| 128kB   | 7,793,604,000         | 99.98%       | 96.56%       | 92.99%      | 2,032     |
| 256kB   | 7,793,233,000         | 99.98%       | 96.56%       | 93.00%      | 2,029     |
| 512kB   | 7,793,233,000         | 99.98%       | 96.56%       | 93.00%      | 2,029     |
| 1MB     | 7,793,233,000         | 99.98%       | 96.56%       | 93.00%      | 2,029     |

**Performance Improvement:** 0.0048% (128kB → 256kB), 0% beyond 256kB

---

## Analysis (250 words)

### Trends Observed

The experimental results reveal a **minimal performance impact** from varying L2 cache size for this workload. Execution time decreased marginally from 7.794 billion ticks (128kB) to 7.793 billion ticks (256kB and above), representing only a 0.0048% improvement. The L2 hit rate improved negligibly from 92.99% to 93.00%, with L2 misses reducing by just 3 (from 2,032 to 2,029). Notably, L1I and L1D hit rates remained completely constant across all configurations, indicating that L1 caches are handling the majority of memory accesses effectively.

### Why This Parameter Has This Effect

The **64×64 matrix multiplication** has a working set size of approximately 49KB (three 64×64 integer matrices). Since even the smallest L2 configuration (128kB) is 2.6× larger than the working set, the entire computation fits comfortably in the L2 cache. The L1D cache (16kB) can only hold about one-third of a single matrix, explaining the 96.56% L1D hit rate and why some accesses spill to L2. However, the L2 cache easily accommodates all data that misses in L1, resulting in high L2 hit rates (>92%) across all sizes.

The minimal L2 misses (approximately 2,000) are primarily **compulsory misses** (cold-start) and occur regardless of L2 size, as they represent the initial data loading before any cache can help.

### Performance Saturation Point

Performance **saturates at 256kB L2 cache**. Beyond this size, there is absolutely zero performance improvement because the working set is fully contained. The results demonstrate the **law of diminishing returns** in cache sizing: once the cache is large enough to hold the active working set, additional capacity provides no benefit.

---

## Key Insights

1. **Working Set Matters:** For this 49KB working set, L2 cache size beyond 256kB is wasted
2. **L1 Effectiveness:** 96.56% L1D hit rate shows good spatial/temporal locality
3. **Compulsory Misses Dominate:** The ~2,000 L2 misses are unavoidable cold-start misses
4. **Cost-Performance Trade-off:** A 128kB L2 provides 99.995% of the performance of a 1MB L2

---

## Recommendations

- **For this workload:** Use 256kB L2 cache (saturation point)
- **For larger matrices:** Would likely benefit from larger L2 (e.g., 256×256 needs ~768KB)
- **General principle:** Size L2 cache based on expected working set, not arbitrarily large

---

## Visualizations

Three plots have been generated:

1. **plot_execution_time.png** - L2 Size vs Execution Time
2. **plot_hit_rates.png** - L2 Size vs Cache Hit Rates (all levels)
3. **plot_combined.png** - Combined view of execution time and L2 metrics

All plots clearly show the saturation behavior at 256kB.
