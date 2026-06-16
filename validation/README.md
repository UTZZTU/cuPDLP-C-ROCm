# Validation results index

> 中文: [README.zh-CN.md](README.zh-CN.md)  
> Main documentation map: [../docs/README.md](../docs/README.md)  
> Root README: [../README.md](../README.md)

This directory contains validation case lists, curated CSV outputs, and Markdown summaries for ROCm/HIP validation and tuning experiments.

## Case lists

| File | Purpose |
|---|---|
| [cases.txt](cases.txt) | Basic validation case list |
| [cases_benchmark_200m.txt](cases_benchmark_200m.txt) | Cross-device Netlib benchmark case list |
| [cases_extended_netlib.txt](cases_extended_netlib.txt) | Extended Netlib validation list |
| [cases_medium_netlib.txt](cases_medium_netlib.txt) | Medium Netlib case list |
| [cases_tuning_quick.txt](cases_tuning_quick.txt) | Short tuning sanity-check list |

## Cross-device validation summary

| File | Description |
|---|---|
| [cross_device_full_summary.csv](cross_device_full_summary.csv) | Cross-device CPU/GPU/ROCm Netlib summary CSV |

The interpretation of these results is documented in [../docs/CROSS_DEVICE_BENCHMARKS.md](../docs/CROSS_DEVICE_BENCHMARKS.md) and [../docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md](../docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md).

## ROCm current vs reduce-scalar-copies repeated comparison

| File | Description |
|---|---|
| [rocm_current_vs_reduce_27cases_repeats_comparison.md](rocm_current_vs_reduce_27cases_repeats_comparison.md) | English Markdown summary |
| [rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md](rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md) | Chinese Markdown summary |
| [rocm_current_vs_reduce_27cases_repeats_comparison.csv](rocm_current_vs_reduce_27cases_repeats_comparison.csv) | Per-case comparison CSV |
| [rocm_current_vs_reduce_27cases_repeats_aggregated.csv](rocm_current_vs_reduce_27cases_repeats_aggregated.csv) | Aggregated repeated-run CSV |
| [rocm_current_vs_reduce_27cases_repeats_raw.csv](rocm_current_vs_reduce_27cases_repeats_raw.csv) | Raw repeated-run CSV |

## ROCm profiling tuning milestones

| File | Description |
|---|---|
| [rocm_prof_tuning_milestones_summary.md](rocm_prof_tuning_milestones_summary.md) | English Markdown summary |
| [rocm_prof_tuning_milestones_summary.zh-CN.md](rocm_prof_tuning_milestones_summary.zh-CN.md) | Chinese Markdown summary |
| [rocm_prof_tuning_milestones_summary.csv](rocm_prof_tuning_milestones_summary.csv) | Milestone summary CSV |
| [rocm_prof_tuning_milestones_deltas.csv](rocm_prof_tuning_milestones_deltas.csv) | Per-milestone delta CSV |
| [rocm_prof_tuning_milestones_hip_api_top.csv](rocm_prof_tuning_milestones_hip_api_top.csv) | Top HIP API calls |
| [rocm_prof_tuning_milestones_kernel_top.csv](rocm_prof_tuning_milestones_kernel_top.csv) | Top kernel dispatches |
| [rocm_prof_tuning_milestones_memory_copy_top.csv](rocm_prof_tuning_milestones_memory_copy_top.csv) | Top memory-copy events |

## ROCm tuning ablation

| File | Description |
|---|---|
| [rocm_tuning_ablation_6cases_repeats_summary.md](rocm_tuning_ablation_6cases_repeats_summary.md) | English Markdown summary |
| [rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md](rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md) | Chinese Markdown summary |
| [rocm_tuning_ablation_6cases_repeats_summary.csv](rocm_tuning_ablation_6cases_repeats_summary.csv) | Repeated-run summary CSV |
| [rocm_tuning_ablation_6cases_repeats_raw.csv](rocm_tuning_ablation_6cases_repeats_raw.csv) | Raw repeated-run CSV |

## W7900 / gfx1100 validation summaries

| File | Description |
|---|---|
| [w7900_smoke_summary_20260611.md](w7900_smoke_summary_20260611.md) | W7900 / `gfx1100` smoke validation summary |
| [w7900_smoke_summary_20260611.zh-CN.md](w7900_smoke_summary_20260611.zh-CN.md) | Chinese W7900 / `gfx1100` smoke validation summary |
| [w7900_smoke_summary_20260611.csv](w7900_smoke_summary_20260611.csv) | W7900 smoke validation CSV |
| [w7900_extended_netlib_summary_20260611.md](w7900_extended_netlib_summary_20260611.md) | W7900 / `gfx1100` extended Netlib validation summary |
| [w7900_extended_netlib_summary_20260611.zh-CN.md](w7900_extended_netlib_summary_20260611.zh-CN.md) | Chinese W7900 / `gfx1100` extended Netlib validation summary |
| [w7900_extended_netlib_summary_20260611.csv](w7900_extended_netlib_summary_20260611.csv) | W7900 extended Netlib validation CSV |

<!-- W7900_27CASE_BASELINE_20260611_BEGIN -->
## W7900 / gfx1100 27-case baseline

| File | Description |
|---|---|
| [w7900_27cases_baseline_20260611.md](w7900_27cases_baseline_20260611.md) | W7900 / `gfx1100` 27-case repeated ROCm baseline |
| [w7900_27cases_baseline_20260611.zh-CN.md](w7900_27cases_baseline_20260611.zh-CN.md) | Chinese W7900 / `gfx1100` 27-case repeated ROCm baseline |
| [w7900_27cases_baseline_20260611_aggregated.csv](w7900_27cases_baseline_20260611_aggregated.csv) | Aggregated median/mean/CV baseline CSV |
| [w7900_27cases_baseline_20260611_raw.csv](w7900_27cases_baseline_20260611_raw.csv) | Raw repeated-run baseline CSV |
<!-- W7900_27CASE_BASELINE_20260611_END -->

<!-- W7900_CROSS_DEVICE_20260611_BEGIN -->
## W7900 vs existing cross-device reference

| File | Description |
|---|---|
| [w7900_vs_cross_device_27cases_20260611.md](w7900_vs_cross_device_27cases_20260611.md) | W7900 / `gfx1100` vs existing RTX 3090, RTX 4090D, and Radeon 890M cross-device Netlib reference |
| [w7900_vs_cross_device_27cases_20260611.zh-CN.md](w7900_vs_cross_device_27cases_20260611.zh-CN.md) | Chinese W7900 cross-device reference comparison |
| [w7900_vs_cross_device_27cases_20260611.csv](w7900_vs_cross_device_27cases_20260611.csv) | Per-case cross-device comparison CSV |
<!-- W7900_CROSS_DEVICE_20260611_END -->

<!-- W7900_LARGE_MPS_INITIAL17_20260613_BEGIN -->
## W7900 / gfx1100 large-MPS initial17 safe baseline

| File | Description |
|---|---|
| [w7900_large_mps_initial17_safe_20260613.md](w7900_large_mps_initial17_safe_20260613.md) | W7900 / `gfx1100` large-MPS initial17 safe baseline summary |
| [w7900_large_mps_initial17_safe_20260613.zh-CN.md](w7900_large_mps_initial17_safe_20260613.zh-CN.md) | Chinese W7900 large-MPS initial17 safe baseline summary |
| [w7900_large_mps_initial17_safe_20260613.csv](w7900_large_mps_initial17_safe_20260613.csv) | Parsed solver summary CSV |
| [w7900_large_mps_initial17_safe_20260613_runtime.csv](w7900_large_mps_initial17_safe_20260613_runtime.csv) | Runtime wall-time summary CSV |
| [cases_w7900_large_mps_initial17_safe.txt](cases_w7900_large_mps_initial17_safe.txt) | Completed safe first-batch large-MPS case list |
| [cases_w7900_large_mps_watchlist6.txt](cases_w7900_large_mps_watchlist6.txt) | Medium-risk large-MPS follow-up case list |
| [cases_w7900_large_mps_hard3.txt](cases_w7900_large_mps_hard3.txt) | Hard-case follow-up list |
<!-- W7900_LARGE_MPS_INITIAL17_20260613_END -->

<!-- W7900_LARGE_MPS_NONHARD23_20260613_BEGIN -->
## W7900 / gfx1100 large-MPS non-hard23 baseline

| File | Description |
|---|---|
| [w7900_large_mps_nonhard23_20260613.md](w7900_large_mps_nonhard23_20260613.md) | W7900 / `gfx1100` 23-case non-hard large-MPS baseline |
| [w7900_large_mps_nonhard23_20260613.zh-CN.md](w7900_large_mps_nonhard23_20260613.zh-CN.md) | Chinese W7900 23-case non-hard large-MPS baseline |
| [w7900_large_mps_nonhard23_20260613.csv](w7900_large_mps_nonhard23_20260613.csv) | Combined parsed solver summary CSV |
| [w7900_large_mps_nonhard23_20260613_runtime.csv](w7900_large_mps_nonhard23_20260613_runtime.csv) | Combined runtime wall-time CSV |
| [w7900_large_mps_watchlist6_diag_900s_20260613.csv](w7900_large_mps_watchlist6_diag_900s_20260613.csv) | 900-second watchlist diagnostic CSV |
| [w7900_large_mps_near_optimal2_1800s_20260613.csv](w7900_large_mps_near_optimal2_1800s_20260613.csv) | 1800-second near-optimal follow-up CSV |
<!-- W7900_LARGE_MPS_NONHARD23_20260613_END -->

<!-- W7900_DOC_SWEEP_20260614_BEGIN -->
## W7900 hard3 follow-up

| File | Description |
|---|---|
| [../docs/W7900_LARGE_MPS_HARD3_NOTES.md](../docs/W7900_LARGE_MPS_HARD3_NOTES.md) | Hard3 policy and convergence-behavior notes for `dlr1`, `Dual2_5000`, and `fhnw-binschedule1` |
<!-- W7900_DOC_SWEEP_20260614_END -->

## Related project docs

- [../docs/VALIDATION.md](../docs/VALIDATION.md) / [中文](../docs/VALIDATION.zh-CN.md)
- [../docs/ROCM_WORKFLOW.md](../docs/ROCM_WORKFLOW.md) / [中文](../docs/ROCM_WORKFLOW.zh-CN.md)
- [../docs/ROCM_TUNING_HISTORY.md](../docs/ROCM_TUNING_HISTORY.md) / [中文](../docs/ROCM_TUNING_HISTORY.zh-CN.md)
- [../docs/TUNING_GUIDE_ROCM.md](../docs/TUNING_GUIDE_ROCM.md) / [中文](../docs/TUNING_GUIDE_ROCM.zh-CN.md)

<!-- W7900_LATEST_EXPERIMENTS_20260616_BEGIN -->
## W7900 latest experiment summaries / 2026-06-16

These compact summaries record the latest W7900 / `gfx1100` experiment milestones. Raw MPS files, raw profiler traces, and large run directories stay outside Git.

| Milestone | Summary | Compact CSV outputs |
|---|---|---|
| P2: rocprof starter3 | [W7900 rocprof starter3 summary](w7900_rocprof_starter3_summary_20260616.md) | [runtime](w7900_rocprof_starter3_runtime_20260616.csv), [solver](w7900_rocprof_starter3_solver_20260616.csv), [HIP API top](w7900_rocprof_starter3_hip_api_top_20260616.csv), [kernel top](w7900_rocprof_starter3_kernel_top_20260616.csv) |
| P3: hard3 probe2 600s | [W7900 hard3 probe2 600s summary](w7900_large_mps_hard3_probe2_600s_summary_20260616.md) | [runtime](w7900_large_mps_hard3_probe2_600s_runtime_20260616.csv), [solver](w7900_large_mps_hard3_probe2_600s_solver_20260616.csv), [case list](cases_w7900_large_mps_hard3_probe2.txt) |
| P4: before/current fast-core6 | [W7900 before/current fast-core6 summary](w7900_before_current_core6_fast_summary_20260616.md) | [comparison](w7900_before_current_core6_fast_comparison_20260616.csv), [current solver](w7900_before_current_core6_fast_current_solver_20260616.csv), [pre-tuning solver](w7900_before_current_core6_fast_pre_tuning_solver_20260616.csv), [case list](cases_w7900_large_mps_before_after_core6_fast.txt) |
| P5: 8-card fast8 batch throughput | [W7900 8-card fast8 batch summary](w7900_8card_batch_fast8_summary_20260616.md) | [comparison](w7900_8card_batch_fast8_comparison_20260616.csv), [concurrent solver](w7900_8card_batch_fast8_concurrent_solver_20260616.csv), [single-GPU sequential solver](w7900_8card_batch_fast8_single_gpu_seq_solver_20260616.csv), [case list](cases_w7900_8card_batch_fast8.txt) |

Key result highlights:

- P2 records compact W7900 `rocprof` starter3 evidence; raw trace files are intentionally not committed.
- P3 confirms `dlr1` and `fhnw-binschedule1` remain hard under a 600-second diagnostic budget.
- P4 shows both `ae3b683 / pre_tuning` and current `rocm-w7900-gfx1100` reach 6/6 `OPTIMAL` on fast-core6, with mixed performance rather than a blanket speedup claim.
- P5 shows 8 independent MPS tasks complete in 146s on 8 W7900 GPUs versus 558s sequentially on one W7900 GPU, giving about 3.82x measured batch makespan speedup.
<!-- W7900_LATEST_EXPERIMENTS_20260616_END -->

<!-- W7900_LATEST_FIGURES_20260616_BEGIN -->
## W7900 latest experiment figures / 2026-06-16

| Figure index | Description |
|---|---|
| [W7900 latest experiment figures](w7900_latest_experiment_figures_20260616.md) | SVG figures for 8-card fast8 throughput, before/current fast-core6, hard3 probe2, and rocprof kernel share |
<!-- W7900_LATEST_FIGURES_20260616_END -->

## W7900 before/current derived metrics / 2026-06-17

The fast-core6 derived analysis separates total solve time into iteration
count and per-iteration execution time.

- Summary: [w7900_before_current_core6_fast_derived_metrics_20260617.md](w7900_before_current_core6_fast_derived_metrics_20260617.md)
- CSV: [w7900_before_current_core6_fast_derived_metrics_20260617.csv](w7900_before_current_core6_fast_derived_metrics_20260617.csv)
- Chinese summary: [w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md](w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md)
- ms/iter ratio figure: [w7900_before_current_fast_core6_ms_per_iter_ratio.svg](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)
- iteration ratio figure: [w7900_before_current_fast_core6_iter_ratio.svg](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

Key interpretation: current improves per-iteration execution time on all
six fast-core6 cases, but total solve time remains mixed because several
cases require more iterations.

## W7900 P10 targeted rocprof / 2026-06-17

P10 profiles the current W7900/gfx1100 branch on five representative
cases selected from the P9 derived metrics.

- Summary: [w7900_p10_current_targeted_rocprof_20260617_summary.md](w7900_p10_current_targeted_rocprof_20260617_summary.md)
- Chinese summary: [w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md](w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md)
- Runtime CSV: [w7900_p10_current_targeted_rocprof_20260617_runtime.csv](w7900_p10_current_targeted_rocprof_20260617_runtime.csv)
- Kernel top CSV: [w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv](w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv)
- HIP API top CSV: [w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv](w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv)
- Memory copy top CSV: [w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv](w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv)

Key interpretation: all five targeted cases complete successfully under
current. The traces confirm that rocSPARSE CSR SpMV kernels are major GPU
hotspots, while `hipMemcpy`, `hipMemcpyAsync`, and `hipLaunchKernel` are
prominent HIP API costs on the longer cases.
