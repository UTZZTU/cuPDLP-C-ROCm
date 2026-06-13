# W7900 large-MPS initial17 safe baseline 20260613

> 中文: [w7900_large_mps_initial17_safe_20260613.zh-CN.md](w7900_large_mps_initial17_safe_20260613.zh-CN.md)

> Validation index: [README.md](README.md)

CSV sources: [solver summary](w7900_large_mps_initial17_safe_20260613.csv), [runtime summary](w7900_large_mps_initial17_safe_20260613_runtime.csv)

## Scope

This document records the first W7900 / `gfx1100` large-MPS initial baseline on the conservative `initial17_safe` subset.

The full downloaded large-MPS dataset contains 26 cases. For this first W7900 baseline, the run intentionally excludes the known or suspected long-running cases and records only the safer first batch:

- `initial17_safe`: completed in this document.
- `watchlist6`: to be tested later with short 600/900-second diagnostics before full runs.
- `hard3`: to be documented separately as hard-case behavior.

## Configuration

```text
Platform: AMD Radeon PRO W7900 / gfx1100
Backend: ROCm/HIP
Case list: validation/cases_w7900_large_mps_initial17_safe.txt
Run date: 2026-06-13
nIterLim: 1000000000
dTimeLim: 7200 seconds
External timeout: 7500 seconds per case
Primary metrics: external wall time and solver JSON dSolvingTime
```

## Summary

| Metric | Value |
|---|---|
| Cases | 17 |
| Runtime status | DONE: 17 |
| Termination status | OPTIMAL: 17 |
| Total wall time | 187.182254 s |
| Total solve time | 81.979907 s |
| Total DeviceMatVecProdTime | 1.155524 s |

## Cross-device reference on the same 17 cases

The existing cross-device large-MPS baseline is used only as a reference. It was produced on the full 26-case dataset, while this table sums the matching 17 `initial17_safe` cases only.

| Device | Wall time sum | Solve time sum | Wall vs W7900 | Solve vs W7900 |
|---|---|---|---|---|
| W7900 / ROCm | 187.182254 | 81.979907 | 1.00x | 1.00x |
| H100 | 181.410000 | 49.206929 | 0.97x | 0.60x |
| RTX 3090 | 229.740000 | 37.961569 | 1.23x | 0.46x |
| Radeon 890M | 378.280000 | 299.242965 | 2.02x | 3.65x |
| RTX 4090D | 794.010000 | 30.036136 | 4.24x | 0.37x |

## Slowest W7900 cases by solve time

| Case | Termination | nIter | Wall time | Solve time | Matvec time | Rel gap |
|---|---|---|---|---|---|---|
| rmine15 | OPTIMAL | 15000 | 28.928 | 27.271 | 0.086937 | 4.180620533e-05 |
| neos-3025225 | OPTIMAL | 6080 | 23.590 | 17.538 | 0.059906 | 7.825931282e-05 |
| set-cover-model | OPTIMAL | 7480 | 26.926 | 11.464 | 0.156154 | 9.3551367e-06 |
| irish-electricity | OPTIMAL | 53680 | 9.285425 | 8.229117 | 0.260075 | 1.62842043e-06 |
| s250r10 | OPTIMAL | 5240 | 7.133462 | 5.121119 | 0.052024 | 5.357990561e-05 |
| supportcase10 | OPTIMAL | 23800 | 5.471572 | 4.481321 | 0.138871 | 9.776586066e-05 |
| neos-5052403-cygnet | OPTIMAL | 8640 | 5.779473 | 2.775727 | 0.059856 | 9.375217334e-05 |
| a2864 | OPTIMAL | 1400 | 14.315 | 1.576788 | 0.036547 | 2.844014065e-05 |

## Full W7900 per-case results

| Case | Runtime | Termination | Primal | Dual | nIter | Wall time | Solve time | Matvec time | Rel primal | Rel dual | Rel gap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L2CTA3D | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 80 | 44.850 | 0.497367 | 0.029599 | 5.995868384e-05 | 0.0 | 1.005417564e-05 |
| a2864 | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 1400 | 14.315 | 1.576788 | 0.036547 | 8.6176792e-06 | 0.0 | 2.844014065e-05 |
| datt256_lp | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 520 | 2.494235 | 0.730319 | 0.032350 | 4.1147546e-05 | 0.0 | 5.77976796e-05 |
| ex10 | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 280 | 1.337554 | 0.126792 | 0.025626 | 2.207382237e-05 | 0.0 | 4.524774349e-05 |
| graph40-40 | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 80 | 2.266596 | 0.105098 | 0.032334 | 6.005565161e-05 | 0.0 | 3.326118142e-05 |
| irish-electricity | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 53680 | 9.285425 | 8.229117 | 0.260075 | 3.62272119e-06 | 9.903143995e-05 | 1.62842043e-06 |
| neos-3025225 | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 6080 | 23.590 | 17.538 | 0.059906 | 8.360963292e-05 | 0.0 | 7.825931282e-05 |
| neos-5052403-cygnet | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 8640 | 5.779473 | 2.775727 | 0.059856 | 2.97698177e-05 | 0.0 | 9.375217334e-05 |
| neos-5251015 | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 800 | 2.673135 | 0.363022 | 0.033420 | 6.7531628e-07 | 1.9465832e-07 | 5.393595963e-05 |
| qap15 | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 2840 | 0.978814 | 0.448982 | 0.050713 | 9.716282542e-05 | 4.24715715e-06 | 4.56259611e-06 |
| rmine15 | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 15000 | 28.928 | 27.271 | 0.086937 | 9.815790163e-05 | 0.0 | 4.180620533e-05 |
| s250r10 | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 5240 | 7.133462 | 5.121119 | 0.052024 | 3.50595512e-06 | 0.0 | 5.357990561e-05 |
| savsched1 | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 520 | 2.510747 | 0.238349 | 0.032854 | 3.001023691e-05 | 5.408788e-08 | 7.879146734e-05 |
| scpm1 | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 1320 | 5.669620 | 0.706959 | 0.036786 | 3.909060984e-05 | 0.0 | 9.490131535e-05 |
| set-cover-model | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 7480 | 26.926 | 11.464 | 0.156154 | 9.810081718e-05 | 0.0 | 9.3551367e-06 |
| supportcase10 | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 23800 | 5.471572 | 4.481321 | 0.138871 | 9.965405e-08 | 0.0 | 9.776586066e-05 |
| woodlands09 | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 800 | 2.972432 | 0.306416 | 0.031472 | 2.54176316e-06 | 0.0 | 7.699777596e-05 |

## Follow-up plan

The `initial17_safe` subset is now a usable W7900 large-MPS baseline for the first-port stage. It should be used as the stable reference before ROCm/gfx1100 tuning.

Next large-MPS work is split into two follow-up groups:

- `validation/cases_w7900_large_mps_watchlist6.txt`: medium-risk cases that should first be run with shorter diagnostics to check the gap trajectory.
- `validation/cases_w7900_large_mps_hard3.txt`: hard cases that should be run and documented separately, not mixed into the first safe baseline.

## Interpretation

All 17 safe large-MPS cases completed successfully on W7900 with `OPTIMAL` termination.

The total W7900 wall time is close to the H100 reference on the same 17 cases, while W7900 solve time is still higher than the CUDA high-end references. This suggests the first-port W7900 path is already usable for the safe subset, but ROCm/gfx1100 kernel, reduction, data movement, and solver-path tuning still have room for improvement.
