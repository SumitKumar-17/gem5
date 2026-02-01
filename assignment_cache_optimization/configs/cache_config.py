"""
Cache Configuration Script for gem5 Assignment
==============================================
This script creates a RISCV system with configurable two-level cache hierarchy.

Usage:
    ./build/RISCV/gem5.opt configs/cache_config.py \
        --l1i_size=16kB --l1d_size=16kB --l2_size=256kB \
        --l1_assoc=4 --l2_assoc=8 \
        --binary=<path_to_binary>

 * Team Members: Sumit Kumar(22CS30056) and Aviral Singh(22CS30015)
 * Assignment 1 - Cache Hierarchy Optimization
"""

import m5
from m5.objects import *
import argparse
import os

# Parse command line arguments
parser = argparse.ArgumentParser(description='Cache configuration for gem5')

# Cache size parameters
parser.add_argument('--l1i_size', type=str, default='16kB',
                    help='L1 instruction cache size (default: 16kB)')
parser.add_argument('--l1d_size', type=str, default='16kB',
                    help='L1 data cache size (default: 16kB)')
parser.add_argument('--l2_size', type=str, default='256kB',
                    help='L2 cache size (default: 256kB)')

# Associativity parameters
parser.add_argument('--l1_assoc', type=int, default=4,
                    help='L1 cache associativity (default: 4)')
parser.add_argument('--l2_assoc', type=int, default=8,
                    help='L2 cache associativity (default: 8)')

# Binary to execute
parser.add_argument('--binary', type=str,
                    default='tests/test-progs/hello/bin/riscv/linux/hello',
                    help='Binary to execute')

args = parser.parse_args()

print("="*70)
print("Cache Configuration:")
print(f"  L1I Size: {args.l1i_size}, Associativity: {args.l1_assoc}")
print(f"  L1D Size: {args.l1d_size}, Associativity: {args.l1_assoc}")
print(f"  L2  Size: {args.l2_size}, Associativity: {args.l2_assoc}")
print(f"  Binary: {args.binary}")
print("="*70)

# Create the system
system = System()

# Set the clock frequency (1GHz)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Set up memory mode and range
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MiB')]

# Create a RISCV Timing Simple CPU
system.cpu = RiscvTimingSimpleCPU()

# Create L1 Instruction Cache
system.cpu.icache = Cache()
system.cpu.icache.size = args.l1i_size
system.cpu.icache.assoc = args.l1_assoc
system.cpu.icache.tag_latency = 2
system.cpu.icache.data_latency = 2
system.cpu.icache.response_latency = 2
system.cpu.icache.mshrs = 4
system.cpu.icache.tgts_per_mshr = 20

# Create L1 Data Cache
system.cpu.dcache = Cache()
system.cpu.dcache.size = args.l1d_size
system.cpu.dcache.assoc = args.l1_assoc
system.cpu.dcache.tag_latency = 2
system.cpu.dcache.data_latency = 2
system.cpu.dcache.response_latency = 2
system.cpu.dcache.mshrs = 4
system.cpu.dcache.tgts_per_mshr = 20

# Connect caches to CPU
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

# Create L2 bus (connects L1 caches to L2 cache)
system.l2bus = L2XBar()

# Connect L1 caches to L2 bus
system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports

# Create L2 Cache
system.l2cache = Cache()
system.l2cache.size = args.l2_size
system.l2cache.assoc = args.l2_assoc
system.l2cache.tag_latency = 20
system.l2cache.data_latency = 20
system.l2cache.response_latency = 20
system.l2cache.mshrs = 20
system.l2cache.tgts_per_mshr = 12

# Connect L2 cache to L2 bus
system.l2cache.cpu_side = system.l2bus.mem_side_ports

# Create memory bus
system.membus = SystemXBar()

# Connect L2 cache to memory bus
system.l2cache.mem_side = system.membus.cpu_side_ports

# Create interrupt controller for RISCV CPU
system.cpu.createInterruptController()

# For RISCV, we don't need the interrupt controller connections to the bus
# (unlike x86). Just connect the system port.
system.system_port = system.membus.cpu_side_ports

# Create DDR3 memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Set up the workload
system.workload = SEWorkload.init_compatible(args.binary)

# Create a process
process = Process()
process.cmd = [args.binary]
system.cpu.workload = process
system.cpu.createThreads()

# Set up root and instantiate
root = Root(full_system=False, system=system)
m5.instantiate()

# Run simulation
print("Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
print("="*70)
print("Simulation completed successfully!")
print("Check m5out/stats.txt for detailed cache statistics")
print("="*70)
