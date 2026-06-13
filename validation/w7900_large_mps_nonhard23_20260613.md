# W7900 large-MPS non-hard23 baseline 20260613

> 中文: [w7900_large_mps_nonhard23_20260613.zh-CN.md](w7900_large_mps_nonhard23_20260613.zh-CN.md)

> Validation index: [README.md](README.md)

CSV sources: [solver summary](w7900_large_mps_nonhard23_20260613.csv), [runtime summary](w7900_large_mps_nonhard23_20260613_runtime.csv)

## Scope

This document records the W7900 / `gfx1100` large-MPS baseline for the 23 non-hard cases.

It combines:

- `initial17_safe`: 17 safe cases, all `OPTIMAL`.
- `watchlist6_900s`: 4 watchlist cases that reached `OPTIMAL` within the 900-second diagnostic run.
- `near_optimal2_1800s`: `Primal2_1000` and `s100`, which were near-optimal at 900 seconds and reached `OPTIMAL` in the 1800-second follow-up.

The remaining 3 cases are intentionally excluded from this non-hard baseline and should be documented separately as hard-case behavior:

- `dlr1.mps`
- `Dual2_5000.mps`
- `fhnw-binschedule1.mps`

## Configuration

```text
Platform: AMD Radeon PRO W7900 / gfx1100
Backend: ROCm/HIP
Run date: 2026-06-13
Main limits: nIterLim=1000000000, dTimeLim=7200 seconds where applicable
Short diagnostic limits: 900 seconds for watchlist6, 1800 seconds for near_optimal2
Primary metrics: external wall time and solver JSON dSolvingTime
```

## Summary

| Metric | Value |
|---|---|
| Cases | 23 |
| Runtime status | DONE: 23 |
| Termination status | OPTIMAL: 23 |
| Source groups | initial17_safe: 17, near_optimal2_1800s: 2, watchlist6_900s: 4 |
| Total wall time | 2960.171115 s |
| Total solve time | 2742.940418 s |
| Total DeviceMatVecProdTime | 10.176142 s |

## Cross-device reference on the same 23 cases

The existing cross-device large-MPS baseline is used only as a reference. This table sums only the matching 23 non-hard cases.

| Device | Wall time sum | Solve time sum | Wall vs W7900 | Solve vs W7900 |
|---|---|---|---|---|
| W7900 / ROCm | 2960.171115 | 2742.940418 | 1.00x | 1.00x |
| H100 | 1701.350000 | 1433.576957 | 0.57x | 0.52x |
| RTX 3090 | 1898.370000 | 1513.213945 | 0.64x | 0.55x |
| RTX 4090D | 2730.760000 | 1329.788798 | 0.92x | 0.48x |
| Radeon 890M | 5015.740000 | 4842.987397 | 1.69x | 1.77x |

## Slowest W7900 non-hard cases by solve time

| Case | Source group | Termination | nIter | Wall time | Solve time | Matvec time | Rel gap |
|---|---|---|---|---|---|---|---|
| s100 | near_optimal2_1800s | OPTIMAL | 675400 | 1100.65 | 1098.05 | 2.707097 | 9.986063828e-05 |
| Primal2_1000 | near_optimal2_1800s | OPTIMAL | 1203440 | 1046.04 | 1037.89 | 4.981328 | 9.830367122e-05 |
| thk_63 | watchlist6_900s | OPTIMAL | 73960 | 288.56 | 252.16 | 0.302975 | 4.756861046e-05 |
| square41 | watchlist6_900s | OPTIMAL | 128360 | 115.16 | 106.40 | 0.484935 | 9.463231177e-05 |
| tpl-tub-ws1617 | watchlist6_900s | OPTIMAL | 82600 | 112.52 | 98.123 | 0.442642 | 4.13613801e-05 |
| thk_48 | watchlist6_900s | OPTIMAL | 17720 | 110.06 | 68.336 | 0.101641 | 5.213466659e-05 |
| rmine15 | initial17_safe | OPTIMAL | 15000 | 28.928 | 27.271 | 0.086937 | 4.180620533e-05 |
| neos-3025225 | initial17_safe | OPTIMAL | 6080 | 23.590 | 17.538 | 0.059906 | 7.825931282e-05 |
| set-cover-model | initial17_safe | OPTIMAL | 7480 | 26.926 | 11.464 | 0.156154 | 9.3551367e-06 |
| irish-electricity | initial17_safe | OPTIMAL | 53680 | 9.285425 | 8.229117 | 0.260075 | 1.62842043e-06 |

## Full W7900 per-case results

| Case | Source group | Runtime | Termination | Primal | Dual | nIter | Wall time | Solve time | Rel primal | Rel dual | Rel gap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L2CTA3D | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 80 | 44.850 | 0.497367 | 5.995868384e-05 | 0.0 | 1.005417564e-05 |
| Primal2_1000 | near_optimal2_1800s | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 1203440 | 1046.04 | 1037.89 | 4.5198752e-07 | 8.7016e-10 | 9.830367122e-05 |
| a2864 | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 1400 | 14.315 | 1.576788 | 8.6176792e-06 | 0.0 | 2.844014065e-05 |
| datt256_lp | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 520 | 2.494235 | 0.730319 | 4.1147546e-05 | 0.0 | 5.77976796e-05 |
| ex10 | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 280 | 1.337554 | 0.126792 | 2.207382237e-05 | 0.0 | 4.524774349e-05 |
| graph40-40 | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 80 | 2.266596 | 0.105098 | 6.005565161e-05 | 0.0 | 3.326118142e-05 |
| irish-electricity | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 53680 | 9.285425 | 8.229117 | 3.62272119e-06 | 9.903143995e-05 | 1.62842043e-06 |
| neos-3025225 | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 6080 | 23.590 | 17.538 | 8.360963292e-05 | 0.0 | 7.825931282e-05 |
| neos-5052403-cygnet | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 8640 | 5.779473 | 2.775727 | 2.97698177e-05 | 0.0 | 9.375217334e-05 |
| neos-5251015 | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 800 | 2.673135 | 0.363022 | 6.7531628e-07 | 1.9465832e-07 | 5.393595963e-05 |
| qap15 | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 2840 | 0.978814 | 0.448982 | 9.716282542e-05 | 4.24715715e-06 | 4.56259611e-06 |
| rmine15 | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 15000 | 28.928 | 27.271 | 9.815790163e-05 | 0.0 | 4.180620533e-05 |
| s100 | near_optimal2_1800s | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 675400 | 1100.65 | 1098.05 | 3.40354e-09 | 0.0 | 9.986063828e-05 |
| s250r10 | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 5240 | 7.133462 | 5.121119 | 3.50595512e-06 | 0.0 | 5.357990561e-05 |
| savsched1 | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 520 | 2.510747 | 0.238349 | 3.001023691e-05 | 5.408788e-08 | 7.879146734e-05 |
| scpm1 | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 1320 | 5.669620 | 0.706959 | 3.909060984e-05 | 0.0 | 9.490131535e-05 |
| set-cover-model | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 7480 | 26.926 | 11.464 | 9.810081718e-05 | 0.0 | 9.3551367e-06 |
| square41 | watchlist6_900s | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 128360 | 115.16 | 106.40 | 1.996319354e-05 | 7.6541079e-07 | 9.463231177e-05 |
| supportcase10 | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 23800 | 5.471572 | 4.481321 | 9.965405e-08 | 0.0 | 9.776586066e-05 |
| thk_48 | watchlist6_900s | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 17720 | 110.06 | 68.336 | 9.849918903e-05 | 0.0 | 5.213466659e-05 |
| thk_63 | watchlist6_900s | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 73960 | 288.56 | 252.16 | 9.765185012e-05 | 0.0 | 4.756861046e-05 |
| tpl-tub-ws1617 | watchlist6_900s | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 82600 | 112.52 | 98.123 | 5.347390611e-05 | 0.0 | 4.13613801e-05 |
| woodlands09 | initial17_safe | DONE | OPTIMAL | FEASIBLE | FEASIBLE | 800 | 2.972432 | 0.306416 | 2.54176316e-06 | 0.0 | 7.699777596e-05 |

## Interpretation

All 23 non-hard large-MPS cases reached `OPTIMAL` on W7900.

The two 900-second near-optimal cases, `Primal2_1000` and `s100`, both reached `OPTIMAL` when rerun with the 1800-second follow-up limit. Therefore they should be treated as slow but solvable non-hard cases, not as hard-case failures.

The remaining hard3 cases should stay outside the primary large-MPS baseline until they are analyzed separately.
