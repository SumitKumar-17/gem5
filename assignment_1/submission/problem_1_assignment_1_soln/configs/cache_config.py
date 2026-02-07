"""
Cache Configuration Script for gem5 Assignment
==============================================
This script creates a RISCV system with configurable cache hierarchy
for cache optimization experiments.

FIXED PARAMETERS (DO NOT MODIFY):
- system.clk_domain.clock = "1GHz"
- system.mem_mode = "timing"
- system.mem_ranges = [AddrRange("512MB")]

CONFIGURABLE PARAMETERS:
- L1 Instruction Cache size and associativity
- L1 Data Cache size and associativity
- L2 Cache size and associativity
- CPU type (RiscvTimingSimpleCPU or RiscvO3CPU)

Usage:
    ./build/ALL/gem5.opt configs/cache_config.py \
        --l1i_size=16kB --l1d_size=16kB --l2_size=256kB \
        --l1_assoc=4 --l2_assoc=8 \
        --binary=benchmarks/matrix_multiply
"""

import m5
from m5.objects import *
from m5.util import addToPath
import argparse
import sys
import os

# Add common config paths
addToPath("../../configs")


class L1ICache(Cache):
    """L1 Instruction Cache"""

    def __init__(self, size="16kB", assoc=4):
        super(L1ICache, self).__init__()
        self.size = size
        self.assoc = assoc
        self.tag_latency = 2
        self.data_latency = 2
        self.response_latency = 2
        self.mshrs = 4
        self.tgts_per_mshr = 20
        self.writeback_clean = False

    def connectCPU(self, cpu):
        """Connect this cache to a CPU instruction port"""
        self.cpu_side = cpu.icache_port

    def connectBus(self, bus):
        """Connect this cache to the L2 bus"""
        self.mem_side = bus.cpu_side_ports


class L1DCache(Cache):
    """L1 Data Cache"""

    def __init__(self, size="16kB", assoc=4):
        super(L1DCache, self).__init__()
        self.size = size
        self.assoc = assoc
        self.tag_latency = 2
        self.data_latency = 2
        self.response_latency = 2
        self.mshrs = 4
        self.tgts_per_mshr = 20
        self.writeback_clean = False

    def connectCPU(self, cpu):
        """Connect this cache to a CPU data port"""
        self.cpu_side = cpu.dcache_port

    def connectBus(self, bus):
        """Connect this cache to the L2 bus"""
        self.mem_side = bus.cpu_side_ports


class L2Cache(Cache):
    """L2 Unified Cache"""

    def __init__(self, size="256kB", assoc=8):
        super(L2Cache, self).__init__()
        self.size = size
        self.assoc = assoc
        self.tag_latency = 20
        self.data_latency = 20
        self.response_latency = 20
        self.mshrs = 20
        self.tgts_per_mshr = 12
        self.writeback_clean = False

    def connectCPUSideBus(self, bus):
        """Connect this cache to the L2 bus on the CPU side"""
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        """Connect this cache to the memory bus on the memory side"""
        self.mem_side = bus.cpu_side_ports


def parse_arguments():
    """Parse command line arguments for cache configuration"""
    parser = argparse.ArgumentParser(
        description="gem5 Cache Configuration Script for RISCV"
    )

    # Cache size arguments
    parser.add_argument(
        "--l1i_size",
        type=str,
        default="16kB",
        help="L1 Instruction Cache size (e.g., 16kB, 32kB, 64kB)"
    )
    parser.add_argument(
        "--l1d_size",
        type=str,
        default="16kB",
        help="L1 Data Cache size (e.g., 16kB, 32kB, 64kB)"
    )
    parser.add_argument(
        "--l2_size",
        type=str,
        default="256kB",
        help="L2 Cache size (e.g., 128kB, 256kB, 512kB, 1MB)"
    )

    # Associativity arguments
    parser.add_argument(
        "--l1_assoc",
        type=int,
        default=4,
        help="L1 Cache associativity (e.g., 2, 4, 8)"
    )
    parser.add_argument(
        "--l2_assoc",
        type=int,
        default=8,
        help="L2 Cache associativity (e.g., 4, 8, 16)"
    )

    # CPU type argument
    parser.add_argument(
        "--cpu_type",
        type=str,
        default="timing",
        choices=["timing", "o3"],
        help="CPU type: 'timing' for RiscvTimingSimpleCPU, 'o3' for RiscvO3CPU"
    )

    # Binary argument
    parser.add_argument(
        "--binary",
        type=str,
        required=True,
        help="Path to the benchmark binary to run"
    )

    return parser.parse_args()


def create_system(args):
    """Create and configure the gem5 system"""

    # Create the system
    system = System()

    # FIXED PARAMETERS (As per assignment requirements)
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = "1GHz"  # FIXED
    system.clk_domain.voltage_domain = VoltageDomain()

    system.mem_mode = "timing"  # FIXED
    system.mem_ranges = [AddrRange("512MB")]  # FIXED

    # Create CPU based on type
    if args.cpu_type == "timing":
        system.cpu = RiscvTimingSimpleCPU()
        print(f"Using RiscvTimingSimpleCPU")
    elif args.cpu_type == "o3":
        system.cpu = RiscvO3CPU()
        print(f"Using RiscvO3CPU")

    # Create L1 Instruction Cache
    system.cpu.icache = L1ICache(size=args.l1i_size, assoc=args.l1_assoc)
    print(f"L1 I-Cache: size={args.l1i_size}, assoc={args.l1_assoc}")

    # Create L1 Data Cache
    system.cpu.dcache = L1DCache(size=args.l1d_size, assoc=args.l1_assoc)
    print(f"L1 D-Cache: size={args.l1d_size}, assoc={args.l1_assoc}")

    # Create L2 Bus (connects L1 caches to L2)
    system.l2bus = L2XBar()

    # Connect L1 caches to CPU and L2 bus
    system.cpu.icache.connectCPU(system.cpu)
    system.cpu.icache.connectBus(system.l2bus)
    system.cpu.dcache.connectCPU(system.cpu)
    system.cpu.dcache.connectBus(system.l2bus)

    # Create L2 Cache
    system.l2cache = L2Cache(size=args.l2_size, assoc=args.l2_assoc)
    system.l2cache.connectCPUSideBus(system.l2bus)
    print(f"L2 Cache: size={args.l2_size}, assoc={args.l2_assoc}")

    # Create memory bus
    system.membus = SystemXBar()

    # Connect L2 cache to memory bus
    system.l2cache.connectMemSideBus(system.membus)

    # Create interrupt controller (required for RISCV)
    system.cpu.createInterruptController()

    # Connect system port to memory bus
    system.system_port = system.membus.cpu_side_ports

    # Create memory controller with DDR4 memory
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR4_2400_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    return system


def setup_workload(system, binary_path):
    """Setup the workload (benchmark) to run"""

    # Check if binary exists
    if not os.path.isfile(binary_path):
        print(f"ERROR: Binary not found at {binary_path}")
        sys.exit(1)

    # Create a process for the benchmark
    process = Process()
    process.cmd = [binary_path]

    # Set up the workload
    system.workload = SEWorkload.init_compatible(binary_path)
    system.cpu.workload = process
    system.cpu.createThreads()

    print(f"Binary: {binary_path}")


def main():
    """Main simulation function"""

    # Parse command line arguments
    args = parse_arguments()

    print("="*70)
    print("Cache Configuration Script - gem5 Assignment")
    print("="*70)
    print(f"\nFIXED PARAMETERS:")
    print(f"  Clock: 1GHz")
    print(f"  Memory Mode: timing")
    print(f"  Memory Range: 512MB")
    print(f"\nCONFIGURABLE PARAMETERS:")

    # Create the system
    system = create_system(args)

    # Setup the workload
    setup_workload(system, args.binary)

    # Create the root object and instantiate
    root = Root(full_system=False, system=system)
    m5.instantiate()

    print("\n" + "="*70)
    print("Starting Simulation...")
    print("="*70 + "\n")

    # Run the simulation
    exit_event = m5.simulate()

    # Dump statistics
    m5.stats.dump()

    # Print simulation results
    print("\n" + "="*70)
    print("Simulation Complete")
    print("="*70)
    print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
    print(f"\nResults saved to output directory:")
    print(f"  - stats.txt: Detailed statistics")
    print(f"  - config.ini: System configuration")
    print(f"  - config.json: JSON system configuration")
    print("="*70)


if __name__ == "__m5_main__":
    main()
