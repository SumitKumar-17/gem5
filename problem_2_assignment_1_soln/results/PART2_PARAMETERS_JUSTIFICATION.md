# Part 2: Cache Parameter Space - Design Decision

## Parameter Configuration

### Fixed Parameters:
- **L1I (Instruction Cache):** 32 KiB, 8-way associative (CONSTANT)
  
### Variable Parameters:
- **L1D Size:** 32 KiB, 64 KiB, 128 KiB (3 options)
- **L1D Associativity:** 4-way, 8-way, 16-way (3 options)
- **L2 Size:** 256 KiB, 512 KiB, 1024 KiB (3 options)
- **L2 Associativity:** 4-way, 8-way, 16-way (3 options)

**Total: 3 × 3 × 3 × 3 = 81 configurations per algorithm**
**Total Simulations: 81 × 2 algorithms = 162 runs**

## Justification for Keeping L1I Constant

### Evidence from Part 1 Baseline Analysis:

**Simple Merge Sort:**
- L1I Accesses: 5,772,498,057
- L1I Misses: 453
- **L1I Miss Rate: 0.000000078 (~0%)**

**Chunked Merge Sort:**
- L1I Accesses: 6,112,641,646
- L1I Misses: 514
- **L1I Miss Rate: 0.000000084 (~0%)**

### Key Observations:

1. **Instruction Cache is NOT a Bottleneck:**
   - Both algorithms achieve near-perfect L1I hit rates (>99.99999%)
   - Only ~500 instruction cache misses across billions of accesses
   - Sorting algorithms have predictable, loop-based instruction patterns

2. **Data Cache IS the Bottleneck:**
   - L1D Miss Rate: 0.20-0.26% (10,000× higher than L1I)
   - L2 Miss Rate: 57-66% (major performance impact)
   - Data access patterns vary significantly with array traversal

3. **Practical Considerations:**
   - Varying L1I would add 3× more configurations (729 configs = 1,458 runs)
   - Would take 3× longer (~60-120 hours instead of ~20-40 hours)
   - Minimal performance impact given near-zero miss rate

### Conclusion:

**Focus optimization efforts on L1D and L2 caches** where the actual performance bottlenecks exist. Keeping L1I constant at 32KiB/8-way (baseline configuration) is both scientifically justified and practically efficient.

This approach allows thorough exploration of the parameters that actually impact performance while maintaining reasonable simulation time.
