# Part 2: Single Parameter Sweep Analysis

## Parameter Investigated: L1D Cache Size

**Sweep Values:** 16kB, 32kB, 64kB, 128kB  
**Fixed Configuration:** L1I=16kB (assoc=4), L2=256kB (assoc=8), CPU=RiscvTimingSimpleCPU

---

## Observed Trends

The experimental results reveal a **non-linear relationship** between L1D cache size and performance. At smaller cache sizes (16kB and 32kB), performance remains nearly identical with execution times of 128.8 billion ticks and hit rates hovering around 50%. This plateau occurs because both configurations are insufficient to capture the 192KB working set of the matrix multiplication benchmark.

A **dramatic performance improvement** occurs at 64kB, where execution time drops to 80.3 billion ticks (37.7% reduction) and the L1D hit rate jumps to 97.3%. This represents the critical inflection point where the cache becomes large enough to exploit temporal and spatial locality effectively. The 64kB cache can hold approximately one-third of the working set, which significantly reduces costly L2 accesses.

Further increasing the cache to 128kB provides diminishing returns, with execution time decreasing only slightly to 77.7 billion ticks (3.3% additional improvement) despite achieving a 99.8% hit rate. While the hit rate improvement is substantial, the marginal performance gain suggests that the remaining misses (6,569 accesses) have minimal impact compared to the original 2.1 million misses.

---

## Why This Effect Occurs

L1D cache size directly impacts **capacity misses**. The matrix multiplication benchmark exhibits poor spatial locality when accessing matrix B (column-wise traversal), causing frequent cache line evictions. Smaller caches (16kB/32kB) cannot retain multiple matrix rows simultaneously, resulting in ~50% miss rates. The 64kB cache crosses a critical threshold, enabling it to buffer multiple rows and exploit reuse patterns in the inner loop multiplication. At 128kB, nearly all frequently accessed data fits, approaching optimal performance.

---

## Performance Saturation Point

Performance **saturates at 64kB** for practical purposes. While 128kB achieves a slightly better hit rate (99.8% vs 97.3%), the marginal execution time improvement (3.3%) does not justify doubling the cache size. The cost-benefit analysis clearly favors 64kB as the optimal configuration, providing 94% of the maximum achievable performance improvement while using half the silicon area of the 128kB design.

**Recommendation:** For this workload, a 64kB L1D cache offers the best performance-per-area ratio, delivering substantial gains without over-provisioning resources.

---

## Summary Statistics

| L1D Size | Execution Time | Speedup vs 16kB | L1D Hit Rate | L2 Hit Rate |
|----------|---------------|-----------------|--------------|-------------|
| 16kB     | 128.83B ticks | Baseline        | 50.1%        | 99.8%       |
| 32kB     | 128.82B ticks | 0.01%           | 50.1%        | 99.8%       |
| 64kB     | 80.34B ticks  | **37.7%**       | 97.3%        | 96.3%       |
| 128kB    | 77.69B ticks  | **39.7%**       | 99.8%        | 38.0%       |

**Key Finding:** The transition from 32kB to 64kB represents the most significant performance improvement, delivering a 37.6% speedup with a 47 percentage point increase in hit rate.

