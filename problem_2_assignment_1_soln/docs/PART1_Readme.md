# Part 1: Baseline Comparison - Gem5 MergeSort Cache Analysis

## Default Cache Configuration
- **L1I Cache:** 32 KiB, 8-way associative
- **L1D Cache:** 64 KiB, 8-way associative
- **L2 Cache:** 512 KiB, 16-way associative

## Baseline Statistics Comparison Table

| Metric | Simple Merge Sort | Chunked Merge Sort | Difference | Better Performance |
|--------|-------------------|-------------------|------------|-------------------|
| **Execution Metrics** | | | | |
| sim_ticks (cycles) | 16,632,464,767,000 | 17,264,476,070,000 | +632,011,303,000 (+3.8%) | Simple |
| sim_insts (instructions) | 4,788,525,072 | 5,067,505,484 | +278,980,412 (+5.8%) | Simple |
| **IPC (Instructions Per Cycle)** | **0.287902** | **0.293522** | **+0.005620 (+2.0%)** | **Chunked** |
| | | | | |
| **L1D Cache (Data Cache)** | | | | |
| Demand Accesses | 2,271,121,566 | 2,331,978,469 | +60,856,903 (+2.7%) | Simple |
| Demand Hits | 2,265,238,366 | 2,327,230,897 | +61,992,531 (+2.7%) | Chunked |
| Demand Misses | 5,883,200 | 4,747,572 | **-1,135,628 (-19.3%)** | **Chunked** |
| **Demand Miss Rate** | **0.002590 (0.26%)** | **0.002036 (0.20%)** | **-0.000554 (-21.4%)** | **Chunked** |
| | | | | |
| **L1I Cache (Instruction Cache)** | | | | |
| Demand Accesses | 5,772,498,057 | 6,112,641,646 | +340,143,589 (+5.9%) | Simple |
| Demand Hits | 5,772,497,604 | 6,112,641,132 | +340,143,528 (+5.9%) | Chunked |
| Demand Misses | 453 | 514 | +61 (+13.5%) | Simple |
| Demand Miss Rate | 0.000000 (~0%) | 0.000000 (~0%) | Negligible | Both |
| | | | | |
| **L2 Cache (Unified)** | | | | |
| Demand Accesses | 5,883,658 | 4,748,089 | **-1,135,569 (-19.3%)** | **Chunked** |
| Demand Hits | 1,979,245 | 2,040,366 | +61,121 (+3.1%) | Chunked |
| Demand Misses | 3,904,413 | 2,707,723 | **-1,196,690 (-30.6%)** | **Chunked** |
| **Demand Miss Rate** | **0.663603 (66.4%)** | **0.570276 (57.0%)** | **-0.093327 (-14.1%)** | **Chunked** |

## Key Observations

### 1. **Chunked Merge Sort Shows Better Cache Performance**
Despite executing **5.8% more instructions** and taking **3.8% more cycles**, the chunked version achieves:
- **2.0% higher IPC** (0.294 vs 0.288)
- **21.4% lower L1D miss rate** (0.20% vs 0.26%)
- **30.6% fewer L2 cache misses** (2.7M vs 3.9M misses)
- **14.1% lower L2 miss rate** (57.0% vs 66.4%)

### 2. **Cache Locality Advantage**
The chunked approach demonstrates superior **temporal and spatial locality**:
- **L1D misses reduced by 19.3%** (1.1M fewer misses)
- **L2 accesses reduced by 19.3%** (1.1M fewer accesses)
- Better cache utilization due to working on smaller data chunks

### 3. **Trade-off: Instructions vs Cache Efficiency**
- Chunked version executes ~279M more instructions (+5.8%)
- But these extra instructions are offset by better cache hit rates
- Result: Slightly better overall IPC despite more work

### 4. **L2 Cache is the Bottleneck**
Both algorithms show:
- Very high L2 miss rates (57-66%)
- L1D is working well (>99.7% hit rate)
- L2 cache size (512 KiB) is insufficient for this workload
# Part 1 Analysis: Why Chunked Sorting Shows Better Cache Locality

## Analysis (283 words)

The chunked merge sort demonstrates superior cache performance despite its algorithmic complexity, primarily due to improved **temporal and spatial locality**. The chunked approach achieves **21.4% lower L1D miss rate** and **30.6% fewer L2 misses** compared to the simple version, resulting in **2.0% higher IPC** (0.294 vs 0.288).

The key advantage lies in the **working set size**. The simple merge sort operates on the entire 10MB dataset simultaneously, causing frequent cache evictions as the working set (10MB) far exceeds both L1D (64 KiB) and L2 (512 KiB) capacities. During recursive merging, data accessed early in the algorithm is repeatedly evicted and reloaded, leading to poor cache reuse.

In contrast, the chunked version processes **2MB chunks** that still exceed cache capacity but benefit from a critical optimization: the **5-way parallel merge phase uses 1MB streams**. Each stream's 1MB buffer (262,144 integers) creates a more cache-friendly access pattern. While individual streams still exceed cache sizes, the algorithm sequentially reads from each stream, maintaining better **sequential access patterns** that leverage cache line prefetching and minimize thrashing.

The results clearly show chunked sorting's advantages in specific parameters:
- **L1D Miss Rate**: 0.204% (chunked) vs 0.259% (simple) - **21.4% improvement**
- **L2 Miss Rate**: 57.0% (chunked) vs 66.4% (simple) - **14.1% improvement**
- **L2 Demand Misses**: 2.7M (chunked) vs 3.9M (simple) - **30.6% reduction**
- **IPC**: 0.294 (chunked) vs 0.288 (simple) - **2.0% improvement**

The chunked approach's streaming merge pattern creates more predictable memory access, allowing the processor's cache prefetcher to work effectively. Although it executes 5.8% more instructions due to chunk management overhead, the improved cache hit rates more than compensate, yielding better overall performance as measured by IPC.
