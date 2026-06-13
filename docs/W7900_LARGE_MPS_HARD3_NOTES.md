# W7900 large-MPS hard3 notes

> 中文: [W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md](W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md)

This note records why the remaining three large-MPS cases are intentionally separated from the W7900 non-hard23 baseline.

## Hard3 cases

- `dlr1.mps`
- `Dual2_5000.mps`
- `fhnw-binschedule1.mps`

## Current policy

These cases should not be mixed into the primary W7900 large-MPS baseline until they have separate convergence-trajectory analysis.

The primary baseline is now:

- `initial17_safe`: 17/17 `OPTIMAL`
- `watchlist6`: 4/6 `OPTIMAL` under 900 seconds
- `near_optimal2`: the remaining 2/6 watchlist cases reached `OPTIMAL` under 1800 seconds
- Combined `non-hard23`: 23/23 `OPTIMAL`

## Why hard3 is separated

PDLP total runtime depends on both per-iteration cost and iteration count:

```text
total time ≈ per-iteration cost × number of iterations
```

For difficult LP/MPS instances, a GPU may be fast per iteration while still requiring many iterations or showing unstable gap trajectories. Hard3 should therefore be reported as numerical/convergence behavior, not as ordinary benchmark failures.

## Next use

Before ROCm/gfx1100 tuning, use hard3 only for short diagnostic runs and convergence-trajectory notes. After tuning stabilizes, rerun hard3 as a separate final stress-test group.
