# Part 1: Environment Setup - Complete Summary

## Assignment: Cache Hierarchy Optimization using gem5

**Date:** February 4, 2026  
**gem5 Build:** build/RISCV/gem5.opt  
**gem5 Version:** 25.1.0.0  
**Compiled:** Jan 31 2026 19:03:12  
**ISA:** RISCV

---

## Deliverable 1: gem5 RISCV Build Verification ✓

**Command:**
```bash
./build/RISCV/gem5.opt --build-info
```

**Result:**
- **gem5 version:** 25.1.0.0
- **Compiled:** Jan 31 2026 19:03:12
- **Build:** RISCV-specific build
- **Status:** ✓ Verified and working

---

## Deliverable 2: Cache Configuration Script ✓

**File:** `assignment_cache_optimization/configs/cache_config.py`

### Fixed Parameters (As Per Assignment):
```python
system.clk_domain.clock = "1GHz"      # FIXED
system.mem_mode = "timing"             # FIXED  
system.mem_ranges = [AddrRange("512MB")]  # FIXED
```

### Configurable Parameters:
- `--l1i_size`: L1 Instruction Cache size (default: 16kB)
- `--l1d_size`: L1 Data Cache size (default: 16kB)
- `--l2_size`: L2 Cache size (default: 256kB)
- `--l1_assoc`: L1 Cache associativity (default: 4)
- `--l2_assoc`: L2 Cache associativity (default: 8)
- `--cpu_type`: CPU type - 'timing' or 'o3' (default: timing)
- `--binary`: Path to benchmark binary (required)

### Cache Hierarchy:
```
RiscvTimingSimpleCPU
  ├── L1 Instruction Cache (16 KiB, 4-way)
  │     └── Connected to cpu.icache_port
  ├── L1 Data Cache (16 KiB, 4-way)
  │     └── Connected to cpu.dcache_port
  │           ↓
  │     L2 Bus (L2XBar)
  │           ↓
  │     L2 Cache (256 KiB, 8-way)
  │           ↓
  │     Memory Bus (SystemXBar)
  │           ↓
  │     DDR4 Memory Controller
```

---

## Deliverable 3: Successful Test Run ✓

### Command Executed:
```bash
./build/RISCV/gem5.opt \
  --outdir=assignment_cache_optimization/results/part1_test \
  assignment_cache_optimization/configs/cache_config.py \
  --l1i_size=16kB \
  --l1d_size=16kB \
  --l2_size=256kB \
  --l1_assoc=4 \
  --l2_assoc=8 \
  --binary=assignment_cache_optimization/benchmarks/matrix_multiply
```

### Default Configuration:
| Parameter | Value |
|-----------|-------|
| **CPU Type** | RiscvTimingSimpleCPU |
| **Clock** | 1 GHz (FIXED) |
| **Memory Mode** | timing (FIXED) |
| **Memory Size** | 512 MB (FIXED) |
| **Memory Type** | DDR4_2400_8x8 |
| **L1 I-Cache** | 16 KiB, 4-way associative |
| **L1 D-Cache** | 16 KiB, 4-way associative |
| **L2 Cache** | 256 KiB, 8-way associative |
| **Benchmark** | Matrix Multiply (128×128) |

### Benchmark Execution Output:
```
Matrix Multiply Benchmark (RISCV)
Matrix Size: 128x128
Initializing matrices...
Starting matrix multiplication...
Verifying results...
C[0][0] = 335280
C[127][127] = 465424
Benchmark complete!
```

**Status:** ✓ Simulation completed successfully  
**Exit Status:** Exiting @ tick 128830948000 because exiting with last active thread context

---

## Deliverable 4: Output Logs with Cache Statistics ✓

### Output Files Generated:
| File | Size | Description |
|------|------|-------------|
| **[stats.txt](./results/part1_test/stats.txt)** | 147 KB | Detailed simulation statistics |
| **[config.ini](./results/part1_test/config.ini)** | 14 KB | System configuration (INI format) |
| **[config.json](./results/part1_test/config.json)** | 35 KB | System configuration (JSON format) |
| **[citations.bib](./results/part1_test/citations.bib)** | 5 KB | gem5 citations |

Location: `assignment_cache_optimization/results/part1_test/`

**Quick Access Links:**
- 📊 [View Detailed Statistics](./results/part1_test/stats.txt)
- ⚙️ [View System Configuration (INI)](./results/part1_test/config.ini)
- 📝 [View System Configuration (JSON)](./results/part1_test/config.json)

---

## Cache Statistics Analysis (from stats.txt)

### Overall Execution Summary:

| Metric | Value | Unit |
|--------|-------|------|
| **Simulation Time** | 0.128831 | seconds |
| **Total Ticks** | 128,830,948,000 | ticks |
| **CPU Cycles** | 128,830,948 | cycles |
| **Instructions** | 27,912,698 | instructions |
| **CPI** | 4.615 | cycles/instruction |
| **IPC** | 0.217 | instructions/cycle |

### L1 Instruction Cache:

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Total Accesses | 34,320,464 | All instruction fetches |
| Hits | 34,320,059 | Successfully served from L1 I-cache |
| Misses | 405 | Had to go to L2 |
| **Hit Rate** | **99.9988%** | ✓ Excellent |
| **Miss Rate** | **0.0012%** | ✓ Very low |
| Avg Miss Latency | 99,511 ticks | L2 access latency |

**Analysis:** Nearly perfect hit rate. The instruction working set fits completely in the 16 KB L1 I-cache.

### L1 Data Cache:

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Total Accesses | 4,283,142 | All data reads/writes |
| Hits | 2,145,855 | Successfully served from L1 D-cache |
| Misses | 2,137,287 | Had to go to L2 |
| **Hit Rate** | **50.1%** | ⚠ Bottleneck |
| **Miss Rate** | **49.9%** | ⚠ High |
| Avg Miss Latency | 26,135 ticks | L2 access latency |
| **Total Miss Latency** | 55,858,522,000 ticks | **43.4% of total execution time** |

**Analysis:** The L1 D-cache has ~50% hit rate because the working set (192 KB for 3 matrices) greatly exceeds the 16 KB cache capacity. This is the **primary performance bottleneck**.

### L2 Cache:

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Total Accesses | 2,137,695 | From L1 misses |
| Hits | 2,133,369 | Served from L2 |
| Misses | 4,326 | Had to go to memory |
| **Hit Rate** | **99.8%** | ✓ Excellent |
| **Miss Rate** | **0.2%** | ✓ Very low |
| Avg Miss Latency | 94,736 ticks | Memory access latency |

**Breakdown:**
- Instruction misses: 397 (from 405 L1 I-cache misses)
- Data misses: 2,137,290 (from 2.1M L1 D-cache misses)
- L2 captures 99.82% of L1 D-cache misses

**Analysis:** The L2 cache (256 KB) successfully holds the entire working set (192 KB), resulting in only 4,326 memory accesses out of 4.3 million total memory operations.

---

## Memory Hierarchy Flow Analysis

### Access Pattern:
```
Total Memory Operations: 4,283,142
    ↓
L1 D-Cache (16 KB)
    ├─ Hits: 2,145,855 (50.1%) ← Served immediately
    └─ Misses: 2,137,287 (49.9%)
          ↓
    L2 Cache (256 KB)
        ├─ Hits: 2,133,361 (99.82%) ← Served from L2
        └─ Misses: 3,929 (0.18%)
              ↓
          Main Memory (DDR4)
              └─ 3,929 accesses (0.09% of total)
```

### Key Metrics:
- **Cache Filtering Effectiveness:** 99.91% of memory requests filtered by cache hierarchy
- **Memory Traffic:** Only 0.09% of operations reach main memory
- **L1 D-cache Bottleneck:** 43.4% of execution time spent on L1 D-cache misses

---

## Performance Bottleneck Identification

### Analysis:

1. **L1 I-Cache:** ✓ Not a bottleneck (99.9988% hit rate)

2. **L1 D-Cache:** ⚠ **PRIMARY BOTTLENECK**
   - Only 50.1% hit rate
   - Working set (192 KB) >> Cache size (16 KB)
   - Causes 2.1M misses to L2
   - Accounts for 43.4% of execution time

3. **L2 Cache:** ✓ Highly effective
   - 99.8% hit rate
   - Successfully captures entire working set
   - Reduces 2.1M L1 misses to only 4,326 memory accesses

4. **Main Memory:** ✓ Not saturated
   - Only 4,326 accesses total
   - Minimal impact on overall performance

### Working Set Analysis:
```
Matrix Multiply: 3 matrices × 128×128 elements × 4 bytes = 192 KB

L1 D-cache: 16 KB  → Can hold 8.3% of working set  → 50% hit rate
L2 Cache:   256 KB → Can hold 133% of working set → 99.8% hit rate
```

---

## Summary

### Part 1 Deliverables Status:

| Deliverable | Status | Location |
|-------------|--------|----------|
| ✓ gem5 RISCV build verification | Complete | `build/RISCV/gem5.opt` |
| ✓ Cache configuration script | Complete | `configs/cache_config.py` |
| ✓ Successful test run | Complete | Simulation completed |
| ✓ Output logs with cache stats | Complete | `results/part1_test/` |

### Key Findings:

1. **Baseline Established:** Successfully ran matrix multiply with default cache configuration
2. **Bottleneck Identified:** L1 D-cache with 50% hit rate is the primary bottleneck
3. **L2 Effectiveness:** L2 cache successfully captures working set (99.8% hit rate)
4. **Optimization Target:** L1 D-cache size is the most promising parameter to sweep

### Execution Time Breakdown:
- Computation + L1 hits: ~72.9 billion ticks (56.6%)
- L1 D-cache misses: ~55.9 billion ticks (43.4%)
- Memory accesses: minimal (<1%)

---

## Recommendations for Part 2

Based on Part 1 analysis, recommended parameter for **single sweep**:

### Option 1: L1 D-Cache Size (Recommended)
**Rationale:** 
- Currently 50% hit rate (significant room for improvement)
- Primary bottleneck (43.4% of execution time)
- Sweep values: 16kB, 32kB, 64kB, 128kB
- Expected impact: Large performance improvement

### Option 2: L2 Cache Size (Alternative)
**Rationale:**
- Currently 99.8% hit rate (already very good)
- Understand minimum L2 size needed for this working set
- Sweep values: 128kB, 256kB, 512kB, 1MB
- Expected impact: Minimal (already optimal)

---

**Part 1 Complete!** ✓

All deliverables generated with correct **build/RISCV/gem5.opt** build.  
Ready to proceed to Part 2: Single Parameter Sweep.
