# Problem 2 Assignment 1: Gem5 MergeSort Cache Analysis
## COMPLETE SUBMISSION PACKAGE

---

## ✅ PART 1: BASELINE COMPARISON - COMPLETED

### Deliverables:
- ✅ **Baseline comparison table** with all metrics
- ✅ **283-word analysis** explaining cache locality differences
- ✅ **All stats files** organized in baseline_simple/ and baseline_chunked/

### Location:
```
/home/rtx3060/gem5/assignment/results/
├── PART1_DELIVERABLE.md
├── baseline_simple/
│   └── sim_simple.txt (132KB)
└── baseline_chunked/
    └── sim_chunked.txt (132KB)
```

### Key Results:
- **Chunked shows 21.4% lower L1D miss rate**
- **Chunked shows 30.6% fewer L2 misses**
- **Chunked achieves 2.0% higher IPC** (0.294 vs 0.288)

---

## ✅ PART 2: CACHE OPTIMIZATION SWEEP - COMPLETED

### Simulations Completed:
- **162 simulations** (81 configs × 2 algorithms)
- **100% success rate** (no failures)
- **Runtime:** ~4.5 hours (20 parallel jobs)

### Cache Configurations Tested:
- **L1 Sizes:** 32KiB, 64KiB, 128KiB (L1I and L1D same size)
- **L1 Associativity:** 4-way, 8-way, 16-way
- **L2 Sizes:** 256KiB, 512KiB, 1024KiB
- **L2 Associativity:** 4-way, 8-way, 16-way

### Deliverables:

#### 1. Results Table ✅
- `all_results.csv` (162 rows, 20 columns)
- Contains: IPC, miss rates, execution times, cache hits/misses

#### 2. Plots (11 total) ✅
**Required (4):**
1. L2 miss rate vs L2 size
2. IPC vs L1 size  
3. L1D hit rate vs associativity
4. Simple vs Chunked comparison

**Additional Analysis (7):**
5. IPC heatmap (L1 vs L2 interaction)
6. L2 associativity impact
7. Performance vs cache budget
8. Cache miss breakdown
9. Execution time comparison
10. L1 size × associativity interaction
11. Best vs worst configurations

#### 3. Top 3 Configurations ✅

**Simple Merge Sort:**
1. L1: 128KiB/4-way, L2: 1024KiB/4-way → **IPC: 0.2895**
2. L1: 128KiB/8-way, L2: 1024KiB/4-way → **IPC: 0.2895**
3. L1: 128KiB/16-way, L2: 1024KiB/4-way → **IPC: 0.2895**

**Chunked Merge Sort:**
1. L1: 128KiB/4-way, L2: 1024KiB/4-way → **IPC: 0.2949**
2. L1: 128KiB/8-way, L2: 1024KiB/4-way → **IPC: 0.2949**
3. L1: 128KiB/16-way, L2: 1024KiB/4-way → **IPC: 0.2949**

#### 4. Comprehensive Analysis ✅
**Key Findings:**
- **L2 cache size dominates performance** (1MB optimal)
- **L1 associativity has minimal impact** (<0.02% IPC change)
- **Higher L2 associativity degrades performance** (surprising!)
- **Chunked maintains 2% advantage** across all configs
- **Cache hierarchy saturates** (~3% total performance range)

### Location:
```
/home/rtx3060/gem5/assignment/results/part2_sweep/
├── all_results.csv
├── PART2_ANALYSIS.md
├── sweep_progress.log
├── plots/
│   ├── plot1_l2_miss_rate_vs_size.png
│   ├── plot2_ipc_vs_l1_size.png
│   ├── plot3_l1d_hit_rate_vs_assoc.png
│   ├── plot4_simple_vs_chunked_comparison.png
│   ├── plot5_ipc_heatmap.png
│   ├── plot6_l2_assoc_impact.png
│   ├── plot7_performance_vs_cache_budget.png
│   ├── plot8_cache_miss_breakdown.png
│   ├── plot9_execution_time_comparison.png
│   ├── plot10_l1_size_assoc_interaction.png
│   ├── plot11_best_vs_worst_configs.png
│   └── top_3_configs.txt
├── simple/ (81 config directories)
└── chunked/ (81 config directories)
```

---

## 📁 SOURCE CODE AND BINARIES

### C Programs:
```
/home/rtx3060/gem5/assignment/
├── mergesort_simple.c (120 lines) - In-memory merge sort
└── mergesort_chunked.c (278 lines) - 5-way parallel merge with streaming
```

### RISC-V Binaries:
```
├── mergesort_s (497KB) - Simple merge sort binary
└── mergesort_c (502KB) - Chunked merge sort binary
```

### Gem5 Configuration Scripts:
```
├── simple-riscv_mergesort_simple_param.py
├── simple-riscv_mergesort_chunked_param.py
├── run_cache_sweep_parallel.sh (automation script)
└── parse_results.py (stats parser)
```

---

## 📊 STATISTICS SUMMARY

### Total Simulations: 164
- 2 baseline runs (Part 1)
- 162 configuration sweep runs (Part 2)

### Data Generated:
- **Stats files:** 164 × 132KB = ~21MB
- **Plots:** 11 × 180KB avg = ~2MB
- **CSV data:** 1 file, 162 rows
- **Total storage:** ~24MB

### Execution Time:
- **Part 1:** ~40 minutes (2 runs)
- **Part 2:** ~4.5 hours (162 parallel runs)
- **Total:** ~5 hours

---

## 🎯 KEY INSIGHTS

### 1. Algorithmic Advantage
Chunked merge sort consistently outperforms simple merge sort across ALL 81 cache configurations, demonstrating that **algorithm design trumps cache tuning** for memory-intensive workloads.

### 2. Cache Hierarchy Bottleneck
Even the best cache configuration (L1:128KB + L2:1MB) achieves only **3% performance improvement** over worst configuration, indicating the working set far exceeds cache capacity.

### 3. Design Recommendations
- **Optimal:** L1: 128KiB/4-way, L2: 1024KiB/4-way
- **Rationale:** Maximizes capacity, avoids associativity overhead
- **Cost-effective:** 4-way simpler than 16-way with equal performance

### 4. Surprising Result
Higher L2 associativity (16-way) slightly degrades performance compared to 4-way, likely due to increased tag comparison overhead without benefit for streaming access patterns.

---

## 📦 READY FOR SUBMISSION

### Checklist:
- ✅ Part 1 baseline comparison + analysis
- ✅ Part 2 full sweep results table
- ✅ Part 2 minimum 4 plots (delivered 11)
- ✅ Top 3 configs for each workload
- ✅ Comprehensive analysis
- ✅ All stats files organized
- ✅ Source code and binaries included
- ✅ Documentation complete

### To Create Submission ZIP:
```bash
cd /home/rtx3060/gem5/assignment
zip -r problem_2_assignment_1_soln.zip \
    results/ \
    mergesort_simple.c \
    mergesort_chunked.c \
    mergesort_s \
    mergesort_c \
    *.py \
    random_numbers.bin
```

---

## 📝 DOCUMENTATION

Additional documentation provided:
- `PART2_PARAMETERS_JUSTIFICATION.md` - Why L1I=L1D
- `PART2_UPDATED_CONFIG.md` - Configuration details
- `PART2_SETUP_README.md` - Methodology
- `sweep_progress.log` - Execution log

---

**Assignment Status: COMPLETE AND READY FOR SUBMISSION** ✅
