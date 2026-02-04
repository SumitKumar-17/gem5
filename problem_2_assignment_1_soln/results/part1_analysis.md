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

