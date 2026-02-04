# Part 2: Cache Optimization Sweep - Setup Complete

## Automated Sweep Configuration

### Scripts Created:
1. **simple-riscv_mergesort_simple_param.py** - Parameterized config for simple merge sort
2. **simple-riscv_mergesort_chunked_param.py** - Parameterized config for chunked merge sort
3. **run_cache_sweep.sh** - Automated sweep script (runs all 162 simulations)
4. **parse_results.py** - Results parser (extracts metrics to CSV)

### Cache Configurations to Test:
- **L1D Sizes:** 32KiB, 64KiB, 128KiB (3 options)
- **L1 Associativity:** 4-way, 8-way, 16-way (3 options)
- **L2 Sizes:** 256KiB, 512KiB, 1024KiB (3 options)
- **L2 Associativity:** 4-way, 8-way, 16-way (3 options)

**Total Configurations:** 3 × 3 × 3 × 3 = 81 configs
**Total Simulations:** 81 configs × 2 algorithms = **162 runs**

### How the Sweep Works:

1. **For each configuration:**
   - Cleans m5out directory (prevents result mixing)
   - Runs gem5 with specified cache parameters
   - Saves results to: `results/part2_sweep/<sort_type>/<config_name>/`

2. **Directory Structure:**
   ```
   results/part2_sweep/
   ├── simple/
   │   ├── L1D32KiB_L1A4_L2256KiB_L2A4/
   │   │   ├── stats.txt
   │   │   ├── config.ini
   │   │   └── console_output.txt
   │   ├── L1D32KiB_L1A4_L2256KiB_L2A8/
   │   └── ... (81 configs)
   ├── chunked/
   │   ├── L1D32KiB_L1A4_L2256KiB_L2A4/
   │   └── ... (81 configs)
   └── sweep_progress.log
   ```

3. **Progress Logging:**
   - Real-time progress in `sweep_progress.log`
   - Shows [X/162] completion status
   - Timestamps for each run

### To Start the Sweep:

```bash
cd /home/rtx3060/gem5/assignment
./run_cache_sweep.sh
```

**Estimated Time:** ~20-40 hours (depends on server)
- Each simulation takes ~20-40 minutes
- 162 simulations total
- Runs sequentially to avoid resource conflicts

### After Sweep Completes:

```bash
# Parse all results into CSV
python3 parse_results.py results/part2_sweep/

# This creates: results/part2_sweep/all_results.csv
```

### Metrics Extracted:
- sim_ticks (execution cycles)
- sim_insts (instruction count)
- IPC (instructions per cycle)
- L1D: accesses, hits, misses, miss_rate
- L1I: accesses, hits, misses, miss_rate
- L2: accesses, hits, misses, miss_rate

### Next Steps After Data Collection:
1. Generate plots (L2 miss rate vs size, IPC vs L1D size, etc.)
2. Identify top 3 configs for each workload
3. Write analysis explaining optimal configurations
