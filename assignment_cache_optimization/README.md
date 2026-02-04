# Cache Hierarchy Optimization using gem5 - Assignment Submission

## Overview
This submission contains a complete analysis of cache hierarchy optimization using gem5 simulation. The assignment investigates how different cache configurations (size, associativity) affect processor performance on a matrix multiplication benchmark.

**Completion Status:** ✓ All 4 parts completed successfully
**Total Configurations Tested:** 112 (4 in Part 2 + 108 in Part 3)
**Total Plots Generated:** 12 high-quality visualizations
**Documentation:** 4 comprehensive markdown analysis reports

---

## Directory Structure

```
assignment_cache_optimization/
├── benchmarks/
│   └── matrix_multiply           # RISCV compiled binary (128×128 matrix)
├── configs/
│   └── cache_config.py          # Main gem5 configuration script
├── scripts/
│   ├── custom_sweep.py          # Part 2: Single parameter sweep (L1D size)
│   ├── plot_results.py          # Part 2: Plot generation
│   ├── cache_sweep.py           # Part 3: Full multi-parameter sweep
│   ├── analyze_sweep.py         # Part 3: Analysis and visualization
│   └── part4_analysis.py        # Part 4: Pareto analysis and recommendations
├── results/
│   ├── part1_test/              # Part 1: Baseline results
│   │   ├── stats.txt            # Detailed simulation statistics
│   │   ├── config.ini           # System configuration (INI)
│   │   └── config.json          # System configuration (JSON)
│   ├── single_param_sweep/      # Part 2: Single parameter results
│   │   ├── results.csv          # Results table (CSV)
│   │   ├── results.json         # Results table (JSON)
│   │   ├── ANALYSIS.md          # 200-word analysis
│   │   ├── plot_execution_time.png
│   │   ├── plot_hit_rates.png
│   │   └── plot_combined.png
│   └── full_sweep_results/      # Part 3: Full sweep results
│       ├── results.json         # All 108 configurations
│       ├── results.csv          # Tabular format
│       ├── summary_statistics.txt
│       ├── l1d_size_impact.png
│       ├── l2_size_impact.png
│       ├── associativity_impact.png
│       ├── parameter_heatmaps.png
│       ├── performance_distribution.png
│       ├── pareto_frontier.png
│       ├── top_configs_comparison.png
│       ├── pareto_optimal_comparison.png
│       └── design_recommendations_comparison.png
├── PART1_SUMMARY.md             # Part 1: Complete analysis
├── PART2_SUMMARY.md             # Part 2: Complete analysis
├── PART3_SUMMARY.md             # Part 3: Complete analysis
├── PART4_ANALYSIS.md            # Part 4: Design recommendations
└── README.md                     # This file
```

---

## Quick Start: Reproduce All Results

### Prerequisites
- gem5 installed with RISCV build: `build/RISCV/gem5.opt`
- Python 3.7+ with matplotlib, numpy, pandas
- RISCV cross-compiler (for recompiling benchmark)

### Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install matplotlib numpy pandas
```

---

## Part 1: Environment Setup & Baseline

### Verify gem5 Build
```bash
./build/RISCV/gem5.opt --version
```

Expected output: gem5 version 25.1.0.0 (or similar)

### Run Baseline Configuration
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

**Expected Runtime:** ~40 seconds
**Output Files:** `stats.txt`, `config.ini`, `config.json`

### Verify Results
```bash
cat assignment_cache_optimization/results/part1_test/stats.txt | grep -A 5 "simTicks"
```

**Expected Result:** simTicks around 128,830,948,000 (128.8 billion ticks)

**Deliverables:**
- ✓ [View Part 1 Summary](./PART1_SUMMARY.md) - Complete baseline analysis
- ✓ [stats.txt](./results/part1_test/stats.txt) - Detailed statistics
- ✓ [config.json](./results/part1_test/config.json) - System configuration

---

## Part 2: Single Parameter Sweep (L1D Cache Size)

### Run Custom Sweep
```bash
cd assignment_cache_optimization
python3 scripts/custom_sweep.py
```

**Parameters Swept:** L1D Size = [16kB, 32kB, 64kB, 128kB]
**Fixed Parameters:** L1I=16kB, L2=256kB, L1_assoc=4, L2_assoc=8
**Expected Runtime:** ~3 minutes (4 simulations)

### Generate Plots
```bash
source venv/bin/activate
python scripts/plot_results.py
```

**Generated Files:**
- `results/single_param_sweep/results.csv`
- `results/single_param_sweep/results.json`
- `results/single_param_sweep/plot_execution_time.png`
- `results/single_param_sweep/plot_hit_rates.png`
- `results/single_param_sweep/plot_combined.png`

### View Results
```bash
cat results/single_param_sweep/results.csv
cat results/single_param_sweep/ANALYSIS.md
```

**Key Finding:** 37.7% performance improvement when increasing L1D from 32kB to 64kB

**Deliverables:**
- ✓ [View Part 2 Summary](./PART2_SUMMARY.md) - Complete analysis with embedded plots
- ✓ [custom_sweep.py](./scripts/custom_sweep.py) - Custom sweep script
- ✓ [results.csv](./results/single_param_sweep/results.csv) - Results table
- ✓ [ANALYSIS.md](./results/single_param_sweep/ANALYSIS.md) - 200-word analysis

---

## Part 3: Multi-Parameter Analysis

### Run Full Parameter Sweep
```bash
cd assignment_cache_optimization

python3 scripts/cache_sweep.py \
  --gem5=../../build/RISCV/gem5.opt \
  --config=configs/cache_config.py \
  --binary=benchmarks/matrix_multiply \
  --output=results/full_sweep_results
```

**Parameters Swept:**
- L1D Size: [16kB, 32kB, 64kB]
- L2 Size: [128kB, 256kB, 512kB, 1MB]
- L1 Associativity: [2, 4, 8]
- L2 Associativity: [4, 8, 16]

**Total Configurations:** 3 × 4 × 3 × 3 = 108
**Expected Runtime:** ~74 minutes
**Success Rate:** 100% (108/108 successful)

### Generate Analysis Plots
```bash
source venv/bin/activate

python scripts/analyze_sweep.py \
  results/full_sweep_results/results.json \
  --output=results/full_sweep_results
```

**Generated Plots (7 total):**
1. `l1d_size_impact.png` - L1D size effect on performance
2. `l2_size_impact.png` - L2 size effect on performance
3. `associativity_impact.png` - Associativity analysis (4 subplots)
4. `parameter_heatmaps.png` - Parameter interaction heatmaps
5. `performance_distribution.png` - Statistical distributions
6. `pareto_frontier.png` - Pareto-optimal configurations
7. `top_configs_comparison.png` - Top 3 configurations comparison

### View Summary Statistics
```bash
cat results/full_sweep_results/summary_statistics.txt
```

**Key Findings:**
- Best execution time: 80.34B ticks (64kB L1D + 512kB L2)
- L1D size has dominant impact (38% performance range)
- L2 associativity has minimal impact (<0.1%)

**Deliverables:**
- ✓ [View Part 3 Summary](./PART3_SUMMARY.md) - Complete analysis with embedded plots
- ✓ [results.json](./results/full_sweep_results/results.json) - All 108 configurations
- ✓ [results.csv](./results/full_sweep_results/results.csv) - Tabular format
- ✓ [summary_statistics.txt](./results/full_sweep_results/summary_statistics.txt) - Statistics
- ✓ 7 analysis plots (all embedded in PART3_SUMMARY.md)

---

## Part 4: Design Analysis & Recommendations

### Generate Pareto Analysis
```bash
source venv/bin/activate

python scripts/part4_analysis.py
```

**Generated Files:**
- `pareto_optimal_comparison.png` - Pareto frontier visualization
- `design_recommendations_comparison.png` - Design recommendations

### View Analysis
```bash
cat PART4_ANALYSIS.md
```

**Questions Answered:**
- **Question A:** Performance bottlenecks (L1D miss-dominated)
- **Question B:** Cache efficiency (L2 has 99.8% hit rate)
- **Question C:** Cost-benefit trade-off (208KB minimum for 99.7% peak)
- **Question D:** Design recommendations for 3 system types

**Key Recommendations:**
1. **Power-Constrained:** L1D=64kB, L2=128kB (208KB total, 99.7% peak)
2. **High-Performance:** L1D=64kB, L2=512kB (592KB total, 100% peak)
3. **Balanced:** L1D=64kB, L2=256kB (336KB total, 99.9% peak)

**Deliverables:**
- ✓ [View Part 4 Analysis](./PART4_ANALYSIS.md) - Complete analysis with embedded plots
- ✓ Answers to all 4 questions (750 words)
- ✓ Pareto-optimal comparison graph
- ✓ Design recommendations graph
- ✓ Design recommendation table with justifications

---

## Key Results Summary

### Execution Time Range
| Metric | Value |
|--------|-------|
| Best (64kB L1D + 512kB L2) | 80.34B ticks (0.0803s) |
| Worst (16kB L1D + 128kB L2) | 131.25B ticks (0.1312s) |
| Performance Range | 38.8% improvement |

### Cache Hit Rates
| Cache | Mean | Range | Best Config |
|-------|------|-------|-------------|
| L1D | 65.4% | 49.0% - 97.3% | 64kB L1D |
| L2 | 98.6% | 94.1% - 99.8% | 512kB L2 with 16kB L1D |

### Top 3 Configurations (by execution time)
1. **l1d64kB_l2512kB_l1a4_l2a4:** 80.34B ticks, L1D=97.3%, L2=96.3%
2. **l1d64kB_l2512kB_l1a4_l2a8:** 80.34B ticks, L1D=97.3%, L2=96.3%
3. **l1d64kB_l2512kB_l1a4_l2a16:** 80.34B ticks, L1D=97.3%, L2=96.3%

**Key Insight:** L2 associativity makes no difference for this workload

---

## Performance Insights

### Dominant Factor: L1D Size
- **Impact:** 38% performance improvement (32kB → 64kB)
- **Critical Threshold:** 64kB
- **Reason:** Working set (192KB for 3×128×128 matrices) requires larger L1D

### Secondary Factor: L2 Size
- **Impact:** Diminishing returns beyond 256kB
- **128KB → 256KB:** 0.4% improvement
- **256KB → 512KB:** 0.4% improvement
- **512KB → 1MB:** -0.1% (noise)

### Minimal Factor: Associativity
- **L1 Associativity (2→8):** 3.0% improvement
- **L2 Associativity (4→16):** <0.1% improvement
- **Conclusion:** 4-way associative sufficient

---

## Verification Checklist

### Part 1: Environment Setup ✓
- [✓] gem5 RISCV build verified
- [✓] cache_config.py created and tested
- [✓] Successful test run completed
- [✓] Output logs with cache statistics
- [✓] PART1_SUMMARY.md with complete analysis

### Part 2: Single Parameter Sweep ✓
- [✓] custom_sweep.py script (265 lines, well-commented)
- [✓] Results table in CSV and JSON format
- [✓] Plot: Parameter value vs Execution Time
- [✓] Plot: Parameter value vs Hit Rate
- [✓] Plot: Combined analysis (bonus)
- [✓] 200-word analysis (ANALYSIS.md)
- [✓] PART2_SUMMARY.md with embedded plots

### Part 3: Multi-Parameter Analysis ✓
- [✓] Full sweep results.json (108 configurations)
- [✓] Full sweep results.csv
- [✓] 7 analysis plots (3 required + 4 bonus):
  - [✓] L1D size impact
  - [✓] L2 size impact
  - [✓] Associativity impact
  - [✓] Parameter heatmaps
  - [✓] Performance distribution
  - [✓] Pareto frontier
  - [✓] Top configs comparison
- [✓] Summary statistics
- [✓] Top 3 configurations by 3 metrics
- [✓] PART3_SUMMARY.md with embedded plots

### Part 4: Design Analysis & Recommendations ✓
- [✓] Question A answered (Performance Bottlenecks)
- [✓] Question B answered (Cache Efficiency)
- [✓] Question C answered (Cost-Benefit Trade-off)
- [✓] Question D answered (Design Recommendations)
- [✓] Total: 750 words (within 500-800 requirement)
- [✓] Pareto-optimal comparison graph
- [✓] Design recommendations graph
- [✓] Design recommendation table with justifications
- [✓] PART4_ANALYSIS.md with embedded plots

### Code Quality ✓
- [✓] All scripts properly commented
- [✓] Clear documentation strings
- [✓] Consistent coding style
- [✓] Error handling implemented

### Documentation ✓
- [✓] README.md with reproduction instructions
- [✓] 4 comprehensive markdown analysis files
- [✓] All images embedded in markdown files
- [✓] All data files linked in markdown files

---

## Troubleshooting

### Issue: ModuleNotFoundError for matplotlib/pandas
**Solution:**
```bash
source venv/bin/activate
pip install matplotlib numpy pandas
```

### Issue: gem5 simulation fails
**Solution:**
1. Verify gem5 build: `./build/RISCV/gem5.opt --version`
2. Check binary path: `ls -lh assignment_cache_optimization/benchmarks/matrix_multiply`
3. Use absolute paths if needed

### Issue: Plots not generating
**Solution:**
1. Activate venv: `source venv/bin/activate`
2. Check results.json exists
3. Verify matplotlib installed: `pip list | grep matplotlib`

---

## Recompiling Benchmark (Optional)

If you need to recompile the matrix multiplication benchmark:

```bash
# Requires RISCV cross-compiler
riscv64-unknown-linux-gnu-gcc -O2 -static \
  assignment_cache_optimization/benchmarks/matrix_multiply.c \
  -o assignment_cache_optimization/benchmarks/matrix_multiply
```

---

## Assignment Completion Summary

**All Required Deliverables:** ✓ COMPLETE

| Part | Required | Delivered | Status |
|------|----------|-----------|--------|
| Part 1 | 3 items | 3 items + comprehensive analysis | ✓ |
| Part 2 | 5 items | 6 items + comprehensive analysis | ✓ |
| Part 3 | 5 items | 8 items + comprehensive analysis | ✓ |
| Part 4 | 3 items | 3 items + comprehensive analysis | ✓ |

**Total Simulations:** 112
**Total Plots:** 12 high-quality visualizations (300 DPI)
**Total Documentation:** ~11,000 words across 4 markdown files
**Code Quality:** All scripts well-commented and documented
**Reproducibility:** Complete step-by-step instructions provided

---

## Contact & Notes

**Assignment:** Problem-1 (Assignment-1): Cache Hierarchy Optimization using gem5
**Completion Date:** February 4, 2026
**gem5 Version:** 25.1.0.0
**gem5 Build:** build/RISCV/gem5.opt

All analysis files contain embedded images and clickable links to data files for easy navigation and review.

---

## License & Attribution

This assignment uses the gem5 simulator. Please cite gem5 if using these results:

```bibtex
@misc{gem5,
  author = {gem5 Development Team},
  title = {gem5 Simulator},
  url = {https://www.gem5.org/},
  year = {2024}
}
```

---

**END OF README**
