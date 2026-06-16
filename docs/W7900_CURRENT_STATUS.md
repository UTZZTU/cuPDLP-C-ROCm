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
<!-- W7900_OPTIMIZATION_BASELINES_20260614_BEGIN -->
## Optimization baseline interpretation

The current W7900 non-hard23 result is not an unoptimized first-port baseline. It is a validation of the current post-890M-tuning ROCm/HIP engineering branch on W7900 / `gfx1100`.

See [W7900 optimization baselines](W7900_OPTIMIZATION_BASELINES.md).
<!-- W7900_OPTIMIZATION_BASELINES_20260614_END -->

## ROCm profiling and tuning plan

The next stage is not blind kernel editing. It starts with a fixed profiling case matrix and records wall time, solver time, `DeviceMatVecProdTime`, `nIter`, HIP/kernel trace, and GPU telemetry.

See [W7900 ROCm profiling plan](W7900_ROCM_PROFILING_PLAN.md).
<!-- W7900_ROCM_PROFILING_PLAN_20260614_END -->

## Next actions

The P2--P9 W7900 validation, profiling, batch-throughput, and derived-metric
summaries are now committed. The next stage should move from evidence
collection to W7900-specific tuning triage:

1. Use the derived fast-core6 metrics to investigate why `L2CTA3D`,
   `set-cover-model`, and `tpl-tub-ws1617` require more iterations under
   current even though ms/iter improved.
2. Run targeted profiling only on representative cases rather than expanding
   the benchmark matrix blindly:
   - positive execution sample: `thk_48`
   - stable iteration-count sample: `square41`
   - convergence-regression samples: `L2CTA3D`, `set-cover-model`,
     `tpl-tub-ws1617`
3. Prioritize changes that preserve current's per-iteration execution gains
   while recovering pre_tuning-like convergence behavior.
4. Continue copy-reduction and rocSPARSE/SpMV profiling, but avoid changing
   residual, restart, termination, or scaling logic without explicit
   numerical validation.
5. Keep the 8-card fast8 batch-throughput result as an independent-MPS
   throughput highlight, not as evidence that one MPS is solved jointly by
   eight GPUs.
## Latest W7900 experiment status / 2026-06-16

The W7900 / `gfx1100` experiment set has been updated with four committed compact summaries:

- [rocprof starter3](../validation/w7900_rocprof_starter3_summary_20260616.md)
- [hard3 probe2 600s](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.md)
- [before/current fast-core6](../validation/w7900_before_current_core6_fast_summary_20260616.md)
- [8-card fast8 batch throughput](../validation/w7900_8card_batch_fast8_summary_20260616.md)

The 8-card fast8 experiment solved all 8 cases to `OPTIMAL` in both concurrent and single-GPU sequential modes, with 146s concurrent makespan versus 558s single-GPU sequential makespan.
<!-- W7900_LATEST_EXPERIMENTS_20260616_END -->

<!-- W7900_LATEST_FIGURES_20260616_BEGIN -->
## Latest W7900 figures / 2026-06-16

The latest W7900 figure index is available here:

- [W7900 latest experiment figures](../validation/w7900_latest_experiment_figures_20260616.md)

The strongest visual result is the 8-card fast8 batch throughput figure: 8 independent MPS tasks completed in 146s concurrently on 8 W7900 GPUs versus 558s sequentially on one W7900 GPU.
<!-- W7900_LATEST_FIGURES_20260616_END -->

## Derived before/current analysis / 2026-06-17

The latest fast-core6 derived metrics split total solve time into
iteration count and per-iteration execution time:

- [Derived metrics summary](../validation/w7900_before_current_core6_fast_derived_metrics_20260617.md)
- [Derived metrics CSV](../validation/w7900_before_current_core6_fast_derived_metrics_20260617.csv)
- [Chinese summary](../validation/w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md)

![W7900 fast-core6 ms/iter ratio](assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)

![W7900 fast-core6 iteration ratio](assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

The derived result is important for tuning interpretation: current
improves per-iteration execution time on all six fast-core6 cases, but
total solve time remains mixed because several cases require more
iterations. Future W7900-specific tuning should therefore optimize
execution efficiency and convergence behavior together.

## P10 targeted rocprof summary / 2026-06-17

P10 adds targeted rocprofv3 profiling for five representative cases from
the P9 derived-metric analysis:

- positive execution-efficiency sample: `thk_48`
- stable iteration-count sample: `square41`
- convergence-regression samples: `L2CTA3D`, `set-cover-model`,
  `tpl-tub-ws1617`

Links:

- [P10 summary](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.md)
- [P10 runtime CSV](../validation/w7900_p10_current_targeted_rocprof_20260617_runtime.csv)
- [P10 kernel top CSV](../validation/w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv)
- [P10 HIP API top CSV](../validation/w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv)
- [P10 memory copy top CSV](../validation/w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv)

All five targeted cases finish successfully under current. The compact
traces show that rocSPARSE CSR SpMV kernels dominate several GPU kernel
profiles, while `hipMemcpy`, `hipMemcpyAsync`, and `hipLaunchKernel`
remain important HIP API costs. This supports the next tuning direction:
focus on SpMV behavior, kernel-launch volume, and host-device copy
reduction without changing solver numerical logic blindly.

## P11 runtime callsite inventory / 2026-06-17

P11 adds a source-level callsite inventory before making tuning patches.

Links:

- [P11 runtime callsite inventory](../validation/w7900_p11_runtime_callsite_inventory_20260617.md)
- [P11 inventory CSV](../validation/w7900_p11_runtime_callsite_inventory_20260617.csv)
- [P11 Chinese summary](../validation/w7900_p11_runtime_callsite_inventory_20260617.zh-CN.md)

This inventory connects the P10 trace findings to source code locations.
The next optimization patch should be execution-layer only and must not
blindly change residual, restart, termination, scaling, or floating-point
update order.

## P11 first patch candidates / 2026-06-17

P11 first-patch candidate analysis ranks the next safe tuning directions
after P10 profiling and P11 callsite inventory.

Links:

- [P11 first patch candidates](../validation/w7900_p11_first_patch_candidates_20260617.md)
- [P11 first patch candidates CSV](../validation/w7900_p11_first_patch_candidates_20260617.csv)
- [P11 Chinese summary](../validation/w7900_p11_first_patch_candidates_20260617.zh-CN.md)

The current recommendation is to avoid blind `hipMemcpy` removal. The
first real code change should be an opt-in experiment, preferably either
an SpMV algorithm-selection/profiling switch or a narrowly guarded
scalar-copy experiment with explicit fast-core6 and P10 validation.
