# W7900 current status and documentation refresh anchor

> 中文: [W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md)

This page is the current W7900 / `gfx1100` status anchor. It should be used to replace older first-port-only wording across the repository.

## Current status

The W7900 branch is no longer only an `afiro` smoke experiment. It now has:

- W7900 first-port build and smoke validation.
- W7900 Netlib 27-case baseline.
- W7900 large-MPS `initial17_safe` baseline.
- W7900 large-MPS `non-hard23` baseline.
- Remaining large-MPS hard cases intentionally split out: `dlr1.mps`, `Dual2_5000.mps`, and `fhnw-binschedule1.mps`.

## Large-MPS non-hard23 summary

| Metric | Value |
|---|---|
| Cases | 23 |
| Termination | 23/23 OPTIMAL |
| Source groups | initial17_safe: 17, near_optimal2_1800s: 2, watchlist6_900s: 4 |
| W7900 total wall time | 2960.171 s |
| W7900 total solve time | 2742.940 s |

<!-- W7900_COMPETITIVE_CHARTS_20260614_BEGIN -->
## Per-case competitiveness highlight

The non-hard23 aggregate totals are useful, but the strongest W7900 story is per-case: W7900 can match or exceed H100 wall time on selected large-MPS cases, while the slow cases are better interpreted through convergence behavior.

![W7900 wall ratio vs H100](assets/w7900/w7900_nonhard23_wall_ratio_vs_h100.svg)

See [W7900 performance behavior analysis](W7900_PERFORMANCE_BEHAVIOR.md) for the full competitiveness and case-class discussion.
<!-- W7900_COMPETITIVE_CHARTS_20260614_END -->

## Cross-device reference on matching 23 cases

| Device | Wall time sum | Solve time sum | Wall vs W7900 | Solve vs W7900 |
|---|---|---|---|---|
| H100 / CUDA | 1701.350 | 1433.577 | 0.57x | 0.52x |
| RTX 3090 / CUDA | 1898.370 | 1513.214 | 0.64x | 0.55x |
| RTX 4090D / CUDA | 2730.760 | 1329.789 | 0.92x | 0.48x |
| W7900 / ROCm | 2960.171 | 2742.940 | 1.00x | 1.00x |
| Radeon 890M / ROCm | 5015.740 | 4842.987 | 1.69x | 1.77x |

![Non-hard23 wall comparison](assets/w7900/w7900_nonhard23_wall_compare.svg)

![Non-hard23 solve comparison](assets/w7900/w7900_nonhard23_solve_compare.svg)

## W7900 slowest non-hard cases

| Case | Source group | nIter | Wall time | Solve time | Rel gap |
|---|---|---|---|---|---|
| s100 | near_optimal2_1800s | 675400 | 1100.650 | 1098.047 | 9.986063828e-05 |
| Primal2_1000 | near_optimal2_1800s | 1203440 | 1046.038 | 1037.885 | 9.830367122e-05 |
| thk_63 | watchlist6_900s | 73960 | 288.564 | 252.165 | 4.756861046e-05 |
| square41 | watchlist6_900s | 128360 | 115.159 | 106.404 | 9.463231177e-05 |
| tpl-tub-ws1617 | watchlist6_900s | 82600 | 112.519 | 98.123 | 4.13613801e-05 |
| thk_48 | watchlist6_900s | 17720 | 110.058 | 68.336 | 5.213466659e-05 |
| rmine15 | initial17_safe | 15000 | 28.928 | 27.271 | 4.180620533e-05 |
| neos-3025225 | initial17_safe | 6080 | 23.590 | 17.538 | 7.825931282e-05 |
| set-cover-model | initial17_safe | 7480 | 26.926 | 11.464 | 9.3551367e-06 |
| irish-electricity | initial17_safe | 53680 | 9.285 | 8.229 | 1.62842043e-06 |

![W7900 slowest cases](assets/w7900/w7900_nonhard23_slowest_cases.svg)

## Theory and application value

cuPDLP/PDLP-style solvers target large-scale LP problems where the core operation is sparse matrix-vector multiplication. This is a good match for GPU acceleration, but the total time depends on both per-iteration throughput and convergence behavior.

For project reporting, this W7900 milestone demonstrates:

- A reproducible CUDA-to-ROCm migration path for a scientific computing solver.
- A large-memory AMD workstation GPU validation path for large LP/MPS workloads.
- A data-driven benchmark split between safe, slow-but-solvable, and hard-case behavior.
- A basis for future ROCm profiling and tuning with clear before-tuning baselines.

## Why W7900 can be fast on some cases and slow on others

W7900 has high FP32 throughput, large VRAM, and high memory bandwidth, so cases with enough sparse matrix-vector work and stable convergence can benefit from the hardware. However, PDLP total time is not only a hardware-throughput problem:

```text
total time ≈ per-iteration cost × number of iterations
```

For hard LP instances, small differences in sparse reductions, floating-point ordering, adaptive restart timing, step-size evolution, or residual/gap behavior can change the iteration path. That explains why W7900 can be strong on some large cases but unexpectedly slow on cases such as `s100`, `Primal2_1000`, or the excluded hard3.

<!-- W7900_PERFORMANCE_BEHAVIOR_20260614_BEGIN -->
## Related performance behavior analysis

For an explanation of why W7900 is fast on some large-MPS cases but slow on others, see:

- [W7900 performance behavior analysis](W7900_PERFORMANCE_BEHAVIOR.md)
- [W7900 性能行为分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)
<!-- W7900_PERFORMANCE_BEHAVIOR_20260614_END -->

<!-- W7900_ROCM_PROFILING_PLAN_20260614_BEGIN -->
## ROCm profiling and tuning plan

The next stage is not blind kernel editing. It starts with a fixed profiling case matrix and records wall time, solver time, `DeviceMatVecProdTime`, `nIter`, HIP/kernel trace, and GPU telemetry.

See [W7900 ROCm profiling plan](W7900_ROCM_PROFILING_PLAN.md).
<!-- W7900_ROCM_PROFILING_PLAN_20260614_END -->

## Next documentation tasks

1. Update `README.md` and `README.zh-CN.md` so W7900 is described as a validated baseline target, not merely a planned target.
2. Update `docs/README.md` and validation indexes so this page, non-hard23, initial17, watchlist6, near2, and hard3 are linked clearly.
3. Update `docs/W7900_FIRST_PORT.md` and platform notes to describe the bootstrap and volatile-machine workflow.
4. Add a hard3 note before full tuning: do not mix hard3 into the first primary baseline.
5. Start ROCm profiling/tuning only after the W7900 documentation state is consistent.
