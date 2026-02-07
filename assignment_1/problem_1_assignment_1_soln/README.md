## Directory Structure

```
assignment_cache_optimization/
├── benchmarks/
│   └── matrix_multiply           # RISCV compiled binary (128×128)
├── configs/
│   └── cache_config.py          # gem5 configuration script
├── scripts/
│   ├── custom_sweep.py          # Part 2: Single parameter sweep
│   ├── plot_results.py          # Part 2: Plot generation
│   ├── cache_sweep.py           # Part 3: Full multi-parameter sweep
│   ├── analyze_sweep.py         # Part 3: Analysis and visualization
│   └── part4_analysis.py        # Part 4: Pareto analysis
├── results/
|   ├── analysis_plots/
|   |   ├── plot_execution_time.png
│   │   ├── plot_hit_rates.png
│   │   ├── plot_combined.png
|   |   ├── l1d_size_impact.png
│   |   ├── l2_size_impact.png
│   |   ├── associativity_impact.png
│   |   ├── parameter_heatmaps.png
│   |   ├── performance_distribution.png
│   |   ├── pareto_frontier.png
│   |   ├── top_configs_comparison.png
│   |   ├── pareto_optimal_comparison.png
│   |   └── design_recommendations_comparison.png
|   |
│   ├── part1_test/              # Part 1: Baseline results
│   │   ├── stats.txt
│   │   ├── config.ini
│   │   └── config.json
|   |
│   ├── single_param_sweep/      # Part 2: Single parameter results
│   │   ├── results.csv
│   │   ├── results.json
│   │   └── ANALYSIS.md
|   |
│   |── full_sweep_results/      # Part 3: Full sweep results
|   |    ├── results.json         # All 108 configurations
|   |    ├── results.csv
|   |    └── summary_statistics.txt
|   |  
└── figs/
    ├── version_info.png         # gem5 version verification
    └── run.png                  # Baseline simulation run
```