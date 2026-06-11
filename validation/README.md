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

## Related project docs

- [../docs/VALIDATION.md](../docs/VALIDATION.md) / [中文](../docs/VALIDATION.zh-CN.md)
- [../docs/ROCM_WORKFLOW.md](../docs/ROCM_WORKFLOW.md) / [中文](../docs/ROCM_WORKFLOW.zh-CN.md)
- [../docs/ROCM_TUNING_HISTORY.md](../docs/ROCM_TUNING_HISTORY.md) / [中文](../docs/ROCM_TUNING_HISTORY.zh-CN.md)
- [../docs/TUNING_GUIDE_ROCM.md](../docs/TUNING_GUIDE_ROCM.md) / [中文](../docs/TUNING_GUIDE_ROCM.zh-CN.md)
