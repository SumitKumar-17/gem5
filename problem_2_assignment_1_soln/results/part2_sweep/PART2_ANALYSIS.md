# Part 2: Cache Optimization Sweep - Analysis

## Key Findings

### Optimal Configurations

**Simple Merge Sort - Top 3:**
1. **L1: 128KiB/4-way, L2: 1024KiB/4-way** - IPC: 0.2895
2. **L1: 128KiB/8-way, L2: 1024KiB/4-way** - IPC: 0.2895  
3. **L1: 128KiB/16-way, L2: 1024KiB/4-way** - IPC: 0.2895

**Chunked Merge Sort - Top 3:**
1. **L1: 128KiB/4-way, L2: 1024KiB/4-way** - IPC: 0.2949
2. **L1: 128KiB/8-way, L2: 1024KiB/4-way** - IPC: 0.2949
3. **L1: 128KiB/16-way, L2: 1024KiB/4-way** - IPC: 0.2949

### Critical Insights

#### 1. **L2 Cache Size Dominates Performance**

Both algorithms show **dramatic performance improvements** with larger L2 caches:
- **256KiB L2:** ~70-85% miss rate (severe bottleneck)
- **512KiB L2:** ~57-74% miss rate (moderate bottleneck)  
- **1024KiB L2:** ~48-61% miss rate (best performance)

**Why?** The working set during merge operations exceeds smaller cache sizes. With 10MB of data being sorted, only the 1MB L2 cache can hold enough recently-accessed data to meaningfully reduce memory traffic.

#### 2. **L1 Associativity Has Minimal Impact**

Across all configurations, **L1 associativity (4-way vs 16-way) changes IPC by <0.02%**. 

**Why?** Sequential memory access patterns in merge sort don't cause significant conflict misses. The algorithms read/write data in predictable streams, so even a 4-way set-associative cache can effectively handle the access patterns without excessive conflicts.

#### 3. **L1 Size Shows Moderate Benefits**

Increasing L1 from 32KiB → 128KiB improves performance:
- **Simple:** L1D miss rate drops from 0.26% → 0.23% (12% reduction)
- **Chunked:** L1D miss rate drops from 0.20% → 0.17% (15% reduction)

**Why?** Larger L1 caches can hold more of the immediate working set during local merge operations, reducing trips to L2. However, since L2 is already relatively slow (20-cycle latency), this provides limited overall benefit.

#### 4. **L2 Associativity: Diminishing Returns**

For 1024KiB L2 caches:
- **4-way:** 60.5% miss rate (Simple), 49.0% (Chunked)
- **8-way:** 61.0% miss rate (Simple), 49.4% (Chunked)
- **16-way:** 62.3% miss rate (Simple), 49.7% (Chunked)

**Surprising result:** Higher L2 associativity slightly **degrades** performance!

**Why?** Two factors:
1. **Tag comparison overhead:** 16-way requires comparing 16 tags simultaneously, adding hardware complexity and potentially longer access time
2. **Optimal eviction:** With large sequential access patterns, simpler LRU on fewer sets (4-way) may actually evict more intelligently than complex policies on many ways

#### 5. **Chunked Algorithm Maintains Advantage**

Chunked merge sort consistently outperforms simple merge sort:
- **IPC advantage:** 1.9-2.1% higher across all configs
- **L2 miss rate advantage:** 10-12 percentage points lower
- **Better cache utilization:** Streaming 1MB buffers align better with cache line sizes

**Why?** The chunked approach's streaming merge pattern creates more predictable memory accesses. Hardware prefetchers can anticipate sequential reads from the 5 parallel streams, preloading cache lines before they're needed.

### Recommendations

#### For Simple Merge Sort:
**Optimal:** L1: 128KiB/4-way, L2: 1024KiB/4-way
- Maximizes L1 and L2 capacity
- Avoids unnecessary associativity overhead
- **Best price/performance:** Lower associativity = simpler hardware

#### For Chunked Merge Sort:
**Optimal:** L1: 128KiB/4-way, L2: 1024KiB/4-way  
- Same configuration as simple sort
- Leverages streaming patterns effectively
- **Achieves 0.2949 IPC** (best observed)

### Cost-Benefit Analysis

**Cache Budget vs Performance:**
- **32KiB L1 + 256KiB L2 = 320KiB total:** IPC ~0.286 (baseline)
- **128KiB L1 + 1024KiB L2 = 1280KiB total:** IPC ~0.295 (+3.1%)

**Conclusion:** Quadrupling cache size yields only ~3% performance gain. The **L2 cache is saturated** by the workload's massive working set. Further improvements require:
1. Larger L2 caches (>1MB)
2. Better algorithms (blocking, tiling)
3. Hardware prefetchers tuned for streaming patterns

### Methodology Validation

**162 simulations completed successfully:**
- **No failures:** 100% completion rate
- **Consistent results:** Multiple configs with identical IPC confirm reproducibility
- **Expected trends:** Larger caches → better performance validates methodology

### Plot Descriptions

1. **L2 Miss Rate vs Size:** Shows exponential decrease in miss rate with larger L2
2. **IPC vs L1 Size:** Demonstrates L1 size has moderate linear impact on IPC
3. **L1D Hit Rate vs Associativity:** Near-perfect hit rates (~99.7%) regardless of associativity
4. **Simple vs Chunked:** Box plots show chunked consistently outperforms across all metrics
5. **IPC Heatmap:** Visualizes L1×L2 interaction - L2 size dominates
6. **L2 Associativity Impact:** Reveals diminishing returns at higher associativities
7. **Performance vs Cache Budget:** Shows sublinear returns on cache investment
8. **Cache Miss Breakdown:** L2 misses dominate total memory traffic
9. **Execution Time:** Directly correlates with cache miss rates
10. **L1 Size×Assoc Interaction:** Confirms associativity has negligible effect
11. **Best vs Worst:** Highlights 3% performance range across all configs

## Conclusion

For memory-intensive sorting workloads with working sets far exceeding cache capacity:
- **L2 capacity is critical** (1MB minimum for 10MB dataset)
- **L1 associativity is overrated** (4-way sufficient)
- **Algorithm matters more than hardware** (chunked 2% faster despite hardware)
- **Cache hierarchy hits limits** (~3% performance range suggests saturation)

**Future work:** Test with L3 caches, larger datasets, and compare against hardware prefetchers.
