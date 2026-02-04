# Part 2: Updated Configuration - L1I and L1D Vary Together

## Parameter Structure (Updated)

### L1 Caches (Instruction and Data):
- **L1I and L1D Size:** 32 KiB, 64 KiB, 128 KiB (both get SAME size)
- **L1I and L1D Associativity:** 4-way, 8-way, 16-way (both get SAME associativity)

### L2 Cache (Unified):
- **L2 Size:** 256 KiB, 512 KiB, 1024 KiB
- **L2 Associativity:** 4-way, 8-way, 16-way

**Total: 3 × 3 × 3 × 3 = 81 configurations × 2 algorithms = 162 simulations**

## Configuration Examples:

| Config Name | L1I | L1D | L2 |
|-------------|-----|-----|-----|
| L132KiB_L1A4_L2256KiB_L2A4 | 32KiB, 4-way | 32KiB, 4-way | 256KiB, 4-way |
| L164KiB_L1A8_L2512KiB_L2A8 | 64KiB, 8-way | 64KiB, 8-way | 512KiB, 8-way |
| L1128KiB_L1A16_L21024KiB_L2A16 | 128KiB, 16-way | 128KiB, 16-way | 1024KiB, 16-way |

## Rationale:

Traditional cache hierarchies maintain **symmetric L1 caches** where instruction and data caches have the same capacity and organization. This updated configuration:

1. **Reflects common CPU designs** - Most processors use equal-sized L1I and L1D caches
2. **Simplifies parameter space** - 162 runs instead of 729 if varied independently
3. **Focuses on meaningful comparisons** - Tests different total L1 cache budgets

## Execution Plan:

- **20 parallel simulations** (optimized for 28-core CPU)
- **Direct output to folders** (no m5out copying)
- **Estimated time: ~4.5-5 hours**
