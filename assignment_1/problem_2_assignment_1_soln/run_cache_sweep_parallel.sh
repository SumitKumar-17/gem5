#!/bin/bash

# Parallel Cache Configuration Sweep Script
# L1I and L1D vary together (same size, same associativity)

GEM5_ROOT="/home/rtx3060/gem5"
ASSIGNMENT_DIR="$GEM5_ROOT/assignment"
RESULTS_DIR="$ASSIGNMENT_DIR/results/part2_sweep"
GEM5_BIN="$GEM5_ROOT/build/ALL/gem5.opt"

# Parallel execution settings
MAX_PARALLEL_JOBS=20

# Configuration parameters - L1I and L1D vary together
L1_SIZES=("32KiB" "64KiB" "128KiB")
L1_ASSOCS=(4 8 16)
L2_SIZES=("256KiB" "512KiB" "1024KiB")
L2_ASSOCS=(4 8 16)

# Create results directory
mkdir -p "$RESULTS_DIR"

# Log file
LOG_FILE="$RESULTS_DIR/sweep_progress.log"
echo "Parallel Cache Sweep Started: $(date)" > "$LOG_FILE"
echo "L1I and L1D vary together (same size, same associativity)" >> "$LOG_FILE"
echo "CPU Cores: 28, Using: $MAX_PARALLEL_JOBS parallel jobs" >> "$LOG_FILE"
echo "=====================================" >> "$LOG_FILE"

# Counter
total_configs=$((${#L1_SIZES[@]} * ${#L1_ASSOCS[@]} * ${#L2_SIZES[@]} * ${#L2_ASSOCS[@]}))
total_runs=$((total_configs * 2))

echo "Total configurations: $total_configs" | tee -a "$LOG_FILE"
echo "Total runs (simple + chunked): $total_runs" | tee -a "$LOG_FILE"
echo "Parallel jobs: $MAX_PARALLEL_JOBS" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Function to run simulation
run_simulation() {
    local sort_type=$1
    local l1_size=$2
    local l1_assoc=$3
    local l2_size=$4
    local l2_assoc=$5
    local run_id=$6
    
    # Create config name - L1 applies to both I and D
    config_name="L1${l1_size}_L1A${l1_assoc}_L2${l2_size}_L2A${l2_assoc}"
    
    # Output directory
    output_dir="$RESULTS_DIR/${sort_type}/${config_name}"
    mkdir -p "$output_dir"
    
    # Config script
    if [ "$sort_type" == "simple" ]; then
        config_script="$ASSIGNMENT_DIR/simple-riscv_mergesort_simple_param.py"
    else
        config_script="$ASSIGNMENT_DIR/simple-riscv_mergesort_chunked_param.py"
    fi
    
    # Log start
    echo "[Job $run_id/$total_runs] Started: $sort_type - $config_name at $(date)" >> "$LOG_FILE"
    
    # Run gem5 - output directly to final folder
    cd "$GEM5_ROOT"
    "$GEM5_BIN" \
        --outdir="$output_dir" \
        --stats-file="stats.txt" \
        "$config_script" \
        --l1-size="$l1_size" \
        --l1-assoc=$l1_assoc \
        --l2-size="$l2_size" \
        --l2-assoc=$l2_assoc \
        > "$output_dir/console_output.txt" 2>&1
    
    exit_code=$?
    
    # Check if successful
    if [ -f "$output_dir/stats.txt" ]; then
        echo "[Job $run_id/$total_runs] SUCCESS: $sort_type - $config_name at $(date)" >> "$LOG_FILE"
    else
        echo "[Job $run_id/$total_runs] FAILED: $sort_type - $config_name (exit: $exit_code) at $(date)" >> "$LOG_FILE"
    fi
}

# Export function and variables
export -f run_simulation
export GEM5_ROOT ASSIGNMENT_DIR RESULTS_DIR GEM5_BIN LOG_FILE total_runs

# Generate all job parameters
job_list=()
run_id=0

for l1_size in "${L1_SIZES[@]}"; do
    for l1_assoc in "${L1_ASSOCS[@]}"; do
        for l2_size in "${L2_SIZES[@]}"; do
            for l2_assoc in "${L2_ASSOCS[@]}"; do
                run_id=$((run_id + 1))
                job_list+=("simple $l1_size $l1_assoc $l2_size $l2_assoc $run_id")
                
                run_id=$((run_id + 1))
                job_list+=("chunked $l1_size $l1_assoc $l2_size $l2_assoc $run_id")
            done
        done
    done
done

# Run jobs in parallel
echo "Starting parallel execution with $MAX_PARALLEL_JOBS jobs..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

if command -v parallel &> /dev/null; then
    # Use GNU Parallel
    printf "%s\n" "${job_list[@]}" | parallel -j $MAX_PARALLEL_JOBS --colsep ' ' run_simulation {1} {2} {3} {4} {5} {6}
else
    # Fallback: Use background jobs
    echo "GNU Parallel not found, using background jobs..." | tee -a "$LOG_FILE"
    
    active_jobs=0
    for job_params in "${job_list[@]}"; do
        read -r sort_type l1_size l1_assoc l2_size l2_assoc run_id <<< "$job_params"
        
        run_simulation "$sort_type" "$l1_size" "$l1_assoc" "$l2_size" "$l2_assoc" "$run_id" &
        
        active_jobs=$((active_jobs + 1))
        
        if [ $active_jobs -ge $MAX_PARALLEL_JOBS ]; then
            wait -n
            active_jobs=$((active_jobs - 1))
        fi
    done
    
    wait
fi

echo "" | tee -a "$LOG_FILE"
echo "=====================================" | tee -a "$LOG_FILE"
echo "Parallel Cache Sweep Completed: $(date)" | tee -a "$LOG_FILE"
echo "Results saved in: $RESULTS_DIR" | tee -a "$LOG_FILE"

# Count results
success_count=$(find "$RESULTS_DIR" -name "stats.txt" | wc -l)
echo "Successful simulations: $success_count / $total_runs" | tee -a "$LOG_FILE"
