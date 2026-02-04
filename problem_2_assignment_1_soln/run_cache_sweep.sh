#!/bin/bash

# Cache Configuration Sweep Script for Part 2
# This script runs all cache configurations for both simple and chunked merge sorts

GEM5_ROOT="/home/rtx3060/gem5"
ASSIGNMENT_DIR="$GEM5_ROOT/assignment"
RESULTS_DIR="$ASSIGNMENT_DIR/results/part2_sweep"
GEM5_BIN="$GEM5_ROOT/build/ALL/gem5.opt"
M5OUT_DIR="$GEM5_ROOT/m5out"

# Configuration parameters
L1D_SIZES=("32KiB" "64KiB" "128KiB")
L1_ASSOCS=(4 8 16)
L2_SIZES=("256KiB" "512KiB" "1024KiB")
L2_ASSOCS=(4 8 16)

# Create results directory
mkdir -p "$RESULTS_DIR"

# Log file
LOG_FILE="$RESULTS_DIR/sweep_progress.log"
echo "Cache Sweep Started: $(date)" > "$LOG_FILE"
echo "=====================================" >> "$LOG_FILE"

# Counter
total_configs=$((${#L1D_SIZES[@]} * ${#L1_ASSOCS[@]} * ${#L2_SIZES[@]} * ${#L2_ASSOCS[@]}))
total_runs=$((total_configs * 2))
current_run=0

echo "Total configurations: $total_configs" | tee -a "$LOG_FILE"
echo "Total runs (simple + chunked): $total_runs" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Function to run simulation
run_simulation() {
    local sort_type=$1
    local l1d_size=$2
    local l1_assoc=$3
    local l2_size=$4
    local l2_assoc=$5
    
    current_run=$((current_run + 1))
    
    # Create config name
    config_name="L1D${l1d_size}_L1A${l1_assoc}_L2${l2_size}_L2A${l2_assoc}"
    
    # Create output directory
    output_dir="$RESULTS_DIR/${sort_type}/${config_name}"
    mkdir -p "$output_dir"
    
    # Stats file name
    stats_file="stats.txt"
    
    # Config script
    if [ "$sort_type" == "simple" ]; then
        config_script="$ASSIGNMENT_DIR/simple-riscv_mergesort_simple_param.py"
    else
        config_script="$ASSIGNMENT_DIR/simple-riscv_mergesort_chunked_param.py"
    fi
    
    # Log start
    echo "[$current_run/$total_runs] Running: $sort_type - $config_name" | tee -a "$LOG_FILE"
    echo "  L1D: $l1d_size, L1 Assoc: ${l1_assoc}-way" | tee -a "$LOG_FILE"
    echo "  L2: $l2_size, L2 Assoc: ${l2_assoc}-way" | tee -a "$LOG_FILE"
    echo "  Started: $(date)" | tee -a "$LOG_FILE"
    
    # IMPORTANT: Clean m5out directory before each run
    echo "  Cleaning m5out directory..." | tee -a "$LOG_FILE"
    rm -rf "$M5OUT_DIR"/*
    
    # Run gem5
    cd "$GEM5_ROOT"
    "$GEM5_BIN" \
        --stats-file="$stats_file" \
        "$config_script" \
        --l1d-size="$l1d_size" \
        --l1-assoc=$l1_assoc \
        --l2-size="$l2_size" \
        --l2-assoc=$l2_assoc \
        > "$output_dir/console_output.txt" 2>&1
    
    exit_code=$?
    
    # Copy results immediately after simulation
    if [ -f "$M5OUT_DIR/$stats_file" ]; then
        cp "$M5OUT_DIR/$stats_file" "$output_dir/"
        cp "$M5OUT_DIR/config.ini" "$output_dir/" 2>/dev/null
        cp "$M5OUT_DIR/config.json" "$output_dir/" 2>/dev/null
        echo "  Status: SUCCESS" | tee -a "$LOG_FILE"
    else
        echo "  Status: FAILED (exit code: $exit_code)" | tee -a "$LOG_FILE"
    fi
    
    echo "  Completed: $(date)" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# Main sweep loop
echo "Starting cache configuration sweep..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

for l1d_size in "${L1D_SIZES[@]}"; do
    for l1_assoc in "${L1_ASSOCS[@]}"; do
        for l2_size in "${L2_SIZES[@]}"; do
            for l2_assoc in "${L2_ASSOCS[@]}"; do
                # Run for simple merge sort
                run_simulation "simple" "$l1d_size" "$l1_assoc" "$l2_size" "$l2_assoc"
                
                # Run for chunked merge sort
                run_simulation "chunked" "$l1d_size" "$l1_assoc" "$l2_size" "$l2_assoc"
            done
        done
    done
done

echo "=====================================" | tee -a "$LOG_FILE"
echo "Cache Sweep Completed: $(date)" | tee -a "$LOG_FILE"
echo "Results saved in: $RESULTS_DIR" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Directory structure:" | tee -a "$LOG_FILE"
echo "  $RESULTS_DIR/simple/L1D*_L1A*_L2*_L2A*/" | tee -a "$LOG_FILE"
echo "  $RESULTS_DIR/chunked/L1D*_L1A*_L2*_L2A*/" | tee -a "$LOG_FILE"
