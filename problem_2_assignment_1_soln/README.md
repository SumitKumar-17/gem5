# Problem 2 Assignment 1: Gem5 MergeSort Cache Analysis

**Course:** CS60003 - High Performance in Computer Architecture
**Submitted by:** Sumit Kumar (22CS30056), Aviral Singh (22CS30015), Group 48

## Directory Structure

```
problem_2_assignment_1_soln/
│
├── README.md                                   # This file
├── Problem_2_Assignment_1.pdf                  # Assignment instructions
│
├── mergesort_simple.c                          # Simple merge sort source code
├── mergesort_chunked.c                         # Chunked merge sort source code
├── random_numbers.bin                          # 10MB random input data
├── simple-riscv_mergesort_simple.py            # Gem5 config for simple (baseline)
├── simple-riscv_mergesort_chunked.py           # Gem5 config for chunked (baseline)
├── simple-riscv_mergesort_simple_param.py      # Gem5 config for simple with modifiable cache params (parameterized)
├── simple-riscv_mergesort_chunked_param.py     # Gem5 config for chunked with modifiable cache params (parameterized)
│
|── scripts/                                         # All scripts used
│    ├── run_cache_sweep_parallel.sh                 # Automation script for 162 simulations in parallel
│    ├── parse_results.py                            # Parser to extract metrics to CSV
│    └── generate_plots_and_analysis.py              # Script to generate all 11 plots
|── docs/                                           
│    ├── PART1_Readme.md                             # Readme for PART1
│    ├── PART2_Readme.md                             # Readme for PART1
│    └── top_3_configs.txt                          # The top three configs

│
└── results/                                    # All simulation results
    │
    |── part_1_results/  
    |        ├── baseline_simple/                        # Part 1: Simple merge sort baseline
    |        │   ├── sim_simple.txt                      # Gem5 statistics 
    |        │   ├── config.ini                          
    |        │   ├── config.json                         
    |        │   └── citations.bib                       
    |        │
    |        ├── baseline_chunked/                       # Part 1: Chunked merge sort baseline
    |        │   ├── sim_chunked.txt                     # Gem5 statistics (132 KB)
    |        │   ├── config.ini
    |        │   ├── config.json
    |        │   └── citations.bib
    |        │
    └── part2_sweep/                            # Part 2: Cache optimization sweep
        │
        ├── all_results.csv                     # Consolidated results (162 rows × 20 columns)
        ├── sweep_progress.log                  # Execution log
        │
        ├── plots/                              # All visualizations
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
        │   └── plot11_best_vs_worst_configs.png
        │   
        │
        ├── simple/                             # 81 configurations for simple merge sort
        │   ├── L132KiB_L1A4_L2256KiB_L2A4/
        │   │   ├── stats.txt                   # Gem5 statistics
        │   │   ├── config.json                 # Configuration parameters
        │   │   └── console_output.txt          # Console output
        │   ├── L132KiB_L1A4_L2256KiB_L2A8/
        │   ├── ... (79 more configurations)
        │   └── L1128KiB_L1A16_L21024KiB_L2A16/
        │
        └── chunked/                            # 81 configurations for chunked merge sort
            ├── L132KiB_L1A4_L2256KiB_L2A4/
            │   ├── stats.txt
            │   ├── config.json
            │   └── console_output.txt
            ├── L132KiB_L1A4_L2256KiB_L2A8/
            ├── ... (79 more configurations)
            └── L1128KiB_L1A16_L21024KiB_L2A16/
```

## Key Files

| File | Description |
|------|-------------|
| `all_results.csv` | All 162 simulation results (20 metrics each) |
| `PART1_Readme.md` | 283-word analysis on cache locality |
| `PART1_Readme.md` | Comprehensive Part 2 findings |
| `top_3_configs.txt` | Best 3 configurations per algorithm |

