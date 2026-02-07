import m5
from m5.objects import *
import sys
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--l1-size', type=str, default='64KiB', help='L1 cache size (both I and D)')
parser.add_argument('--l1-assoc', type=int, default=8, help='L1 cache associativity')
parser.add_argument('--l2-size', type=str, default='512KiB', help='L2 cache size')
parser.add_argument('--l2-assoc', type=int, default=16, help='L2 cache associativity')
args = parser.parse_args()

system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]
system.cpu = RiscvTimingSimpleCPU()

system.cpu.createInterruptController()

system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]

class L1Cache(Cache):
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

class L2Cache(Cache):
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12

# Create caches + buses
system.membus = SystemXBar()
system.l2_xbar = SystemXBar()

# Apply command-line parameters - L1I and L1D get SAME size and associativity
system.cpu.icache = L1Cache(size=args.l1_size, assoc=args.l1_assoc)
system.cpu.dcache = L1Cache(size=args.l1_size, assoc=args.l1_assoc)
system.l2cache = L2Cache(size=args.l2_size, assoc=args.l2_assoc)

# L1 → L2_XBar
system.cpu.icache_port = system.cpu.icache.cpu_side
system.cpu.dcache_port = system.cpu.dcache.cpu_side
system.cpu.icache.mem_side = system.l2_xbar.cpu_side_ports
system.cpu.dcache.mem_side = system.l2_xbar.cpu_side_ports

# L2 → Main bus
system.l2cache.cpu_side = system.l2_xbar.mem_side_ports
system.l2cache.mem_side = system.membus.cpu_side_ports

# Main bus → DRAM
system.mem_ctrl.port = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports

thispath = os.path.dirname(os.path.realpath(__file__))
binary = os.path.join(thispath, "mergesort_s")

system.workload = SEWorkload.init_compatible(binary)

process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()
m5.simulate.maxmem = '512MiB'
m5.stats.reset()
root = Root(full_system=False, system=system)
m5.instantiate()

print(f"Configuration: L1I={args.l1_size}/{args.l1_assoc}-way, L1D={args.l1_size}/{args.l1_assoc}-way, L2={args.l2_size}/{args.l2_assoc}-way")
print(f"Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
