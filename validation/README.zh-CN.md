# Validation 结果索引

> English: [README.md](README.md)  
> 文档地图: [../docs/README.md](../docs/README.md)  
> 根 README: [../README.zh-CN.md](../README.zh-CN.md)

本目录保存 ROCm/HIP 验证和调优实验的 case 列表、整理后的 CSV 输出，以及 Markdown 汇总说明。

## Case 列表

| 文件 | 用途 |
|---|---|
| [cases.txt](cases.txt) | 基础 validation case 列表 |
| [cases_benchmark_200m.txt](cases_benchmark_200m.txt) | 跨设备 Netlib benchmark case 列表 |
| [cases_extended_netlib.txt](cases_extended_netlib.txt) | 扩展 Netlib validation 列表 |
| [cases_medium_netlib.txt](cases_medium_netlib.txt) | 中等规模 Netlib case 列表 |
| [cases_tuning_quick.txt](cases_tuning_quick.txt) | 快速 tuning sanity-check 列表 |

## 跨设备验证汇总

| 文件 | 说明 |
|---|---|
| [cross_device_full_summary.csv](cross_device_full_summary.csv) | 跨设备 CPU/GPU/ROCm Netlib 汇总 CSV |

结果解释见 [../docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md](../docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md)，英文版见 [../docs/CROSS_DEVICE_BENCHMARKS.md](../docs/CROSS_DEVICE_BENCHMARKS.md)。

## ROCm current vs reduce-scalar-copies 重复测试对比

| 文件 | 说明 |
|---|---|
| [rocm_current_vs_reduce_27cases_repeats_comparison.md](rocm_current_vs_reduce_27cases_repeats_comparison.md) | 英文 Markdown 汇总 |
| [rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md](rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md) | 中文 Markdown 汇总 |
| [rocm_current_vs_reduce_27cases_repeats_comparison.csv](rocm_current_vs_reduce_27cases_repeats_comparison.csv) | 逐 case 对比 CSV |
| [rocm_current_vs_reduce_27cases_repeats_aggregated.csv](rocm_current_vs_reduce_27cases_repeats_aggregated.csv) | 重复运行聚合 CSV |
| [rocm_current_vs_reduce_27cases_repeats_raw.csv](rocm_current_vs_reduce_27cases_repeats_raw.csv) | 重复运行原始 CSV |

## ROCm profiling tuning milestones

| 文件 | 说明 |
|---|---|
| [rocm_prof_tuning_milestones_summary.md](rocm_prof_tuning_milestones_summary.md) | 英文 Markdown 汇总 |
| [rocm_prof_tuning_milestones_summary.zh-CN.md](rocm_prof_tuning_milestones_summary.zh-CN.md) | 中文 Markdown 汇总 |
| [rocm_prof_tuning_milestones_summary.csv](rocm_prof_tuning_milestones_summary.csv) | tuning milestone 汇总 CSV |
| [rocm_prof_tuning_milestones_deltas.csv](rocm_prof_tuning_milestones_deltas.csv) | milestone delta CSV |
| [rocm_prof_tuning_milestones_hip_api_top.csv](rocm_prof_tuning_milestones_hip_api_top.csv) | HIP API top events |
| [rocm_prof_tuning_milestones_kernel_top.csv](rocm_prof_tuning_milestones_kernel_top.csv) | kernel dispatch top events |
| [rocm_prof_tuning_milestones_memory_copy_top.csv](rocm_prof_tuning_milestones_memory_copy_top.csv) | memory-copy top events |

## ROCm tuning ablation

| 文件 | 说明 |
|---|---|
| [rocm_tuning_ablation_6cases_repeats_summary.md](rocm_tuning_ablation_6cases_repeats_summary.md) | 英文 Markdown 汇总 |
| [rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md](rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md) | 中文 Markdown 汇总 |
| [rocm_tuning_ablation_6cases_repeats_summary.csv](rocm_tuning_ablation_6cases_repeats_summary.csv) | 重复运行 summary CSV |
| [rocm_tuning_ablation_6cases_repeats_raw.csv](rocm_tuning_ablation_6cases_repeats_raw.csv) | 重复运行原始 CSV |

## W7900 / gfx1100 validation 汇总

| 文件 | 说明 |
|---|---|
| [w7900_smoke_summary_20260611.md](w7900_smoke_summary_20260611.md) | W7900 / `gfx1100` smoke validation 英文汇总 |
| [w7900_smoke_summary_20260611.zh-CN.md](w7900_smoke_summary_20260611.zh-CN.md) | W7900 / `gfx1100` smoke validation 中文汇总 |
| [w7900_smoke_summary_20260611.csv](w7900_smoke_summary_20260611.csv) | W7900 smoke validation CSV |
| [w7900_extended_netlib_summary_20260611.md](w7900_extended_netlib_summary_20260611.md) | W7900 / `gfx1100` extended Netlib validation 英文汇总 |
| [w7900_extended_netlib_summary_20260611.zh-CN.md](w7900_extended_netlib_summary_20260611.zh-CN.md) | W7900 / `gfx1100` extended Netlib validation 中文汇总 |
| [w7900_extended_netlib_summary_20260611.csv](w7900_extended_netlib_summary_20260611.csv) | W7900 extended Netlib validation CSV |

<!-- W7900_27CASE_BASELINE_20260611_BEGIN -->
## W7900 / gfx1100 27-case baseline

| 文件 | 说明 |
|---|---|
| [w7900_27cases_baseline_20260611.md](w7900_27cases_baseline_20260611.md) | W7900 / `gfx1100` 27-case repeated ROCm baseline 英文汇总 |
| [w7900_27cases_baseline_20260611.zh-CN.md](w7900_27cases_baseline_20260611.zh-CN.md) | W7900 / `gfx1100` 27-case repeated ROCm baseline 中文汇总 |
| [w7900_27cases_baseline_20260611_aggregated.csv](w7900_27cases_baseline_20260611_aggregated.csv) | 聚合 median/mean/CV baseline CSV |
| [w7900_27cases_baseline_20260611_raw.csv](w7900_27cases_baseline_20260611_raw.csv) | repeated-run raw baseline CSV |
<!-- W7900_27CASE_BASELINE_20260611_END -->

## 相关项目文档

- [../docs/VALIDATION.zh-CN.md](../docs/VALIDATION.zh-CN.md) / [English](../docs/VALIDATION.md)
- [../docs/ROCM_WORKFLOW.zh-CN.md](../docs/ROCM_WORKFLOW.zh-CN.md) / [English](../docs/ROCM_WORKFLOW.md)
- [../docs/ROCM_TUNING_HISTORY.zh-CN.md](../docs/ROCM_TUNING_HISTORY.zh-CN.md) / [English](../docs/ROCM_TUNING_HISTORY.md)
- [../docs/TUNING_GUIDE_ROCM.zh-CN.md](../docs/TUNING_GUIDE_ROCM.zh-CN.md) / [English](../docs/TUNING_GUIDE_ROCM.md)
