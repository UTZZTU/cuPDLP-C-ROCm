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

<!-- W7900_CROSS_DEVICE_20260611_BEGIN -->
## W7900 vs 既有跨设备 reference

| 文件 | 说明 |
|---|---|
| [w7900_vs_cross_device_27cases_20260611.md](w7900_vs_cross_device_27cases_20260611.md) | W7900 / `gfx1100` 与既有 RTX 3090、RTX 4090D、Radeon 890M Netlib 跨设备 reference 的英文对比 |
| [w7900_vs_cross_device_27cases_20260611.zh-CN.md](w7900_vs_cross_device_27cases_20260611.zh-CN.md) | W7900 跨设备 reference 中文对比 |
| [w7900_vs_cross_device_27cases_20260611.csv](w7900_vs_cross_device_27cases_20260611.csv) | per-case 跨设备对比 CSV |
<!-- W7900_CROSS_DEVICE_20260611_END -->

<!-- W7900_LARGE_MPS_INITIAL17_20260613_BEGIN -->
## W7900 / gfx1100 large-MPS initial17 safe baseline

| 文件 | 说明 |
|---|---|
| [w7900_large_mps_initial17_safe_20260613.md](w7900_large_mps_initial17_safe_20260613.md) | W7900 / `gfx1100` large-MPS initial17 safe baseline 英文汇总 |
| [w7900_large_mps_initial17_safe_20260613.zh-CN.md](w7900_large_mps_initial17_safe_20260613.zh-CN.md) | W7900 large-MPS initial17 safe baseline 中文汇总 |
| [w7900_large_mps_initial17_safe_20260613.csv](w7900_large_mps_initial17_safe_20260613.csv) | parsed solver summary CSV |
| [w7900_large_mps_initial17_safe_20260613_runtime.csv](w7900_large_mps_initial17_safe_20260613_runtime.csv) | runtime wall-time summary CSV |
| [cases_w7900_large_mps_initial17_safe.txt](cases_w7900_large_mps_initial17_safe.txt) | 已完成的 safe 第一批 large-MPS case list |
| [cases_w7900_large_mps_watchlist6.txt](cases_w7900_large_mps_watchlist6.txt) | 后续中等风险 large-MPS case list |
| [cases_w7900_large_mps_hard3.txt](cases_w7900_large_mps_hard3.txt) | hard-case 后续列表 |
<!-- W7900_LARGE_MPS_INITIAL17_20260613_END -->

<!-- W7900_LARGE_MPS_NONHARD23_20260613_BEGIN -->
## W7900 / gfx1100 large-MPS non-hard23 baseline

| 文件 | 说明 |
|---|---|
| [w7900_large_mps_nonhard23_20260613.md](w7900_large_mps_nonhard23_20260613.md) | W7900 / `gfx1100` 23-case non-hard large-MPS baseline 英文汇总 |
| [w7900_large_mps_nonhard23_20260613.zh-CN.md](w7900_large_mps_nonhard23_20260613.zh-CN.md) | W7900 23-case non-hard large-MPS baseline 中文汇总 |
| [w7900_large_mps_nonhard23_20260613.csv](w7900_large_mps_nonhard23_20260613.csv) | 合并后的 parsed solver summary CSV |
| [w7900_large_mps_nonhard23_20260613_runtime.csv](w7900_large_mps_nonhard23_20260613_runtime.csv) | 合并后的 runtime wall-time CSV |
| [w7900_large_mps_watchlist6_diag_900s_20260613.csv](w7900_large_mps_watchlist6_diag_900s_20260613.csv) | 900 秒 watchlist 诊断 CSV |
| [w7900_large_mps_near_optimal2_1800s_20260613.csv](w7900_large_mps_near_optimal2_1800s_20260613.csv) | 1800 秒 near-optimal follow-up CSV |
<!-- W7900_LARGE_MPS_NONHARD23_20260613_END -->

<!-- W7900_DOC_SWEEP_20260614_BEGIN -->
## W7900 hard3 后续说明

| 文件 | 说明 |
|---|---|
| [../docs/W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md](../docs/W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md) | `dlr1`、`Dual2_5000`、`fhnw-binschedule1` 的 hard3 策略与收敛行为说明 |
<!-- W7900_DOC_SWEEP_20260614_END -->

## 相关项目文档

- [../docs/VALIDATION.zh-CN.md](../docs/VALIDATION.zh-CN.md) / [English](../docs/VALIDATION.md)
- [../docs/ROCM_WORKFLOW.zh-CN.md](../docs/ROCM_WORKFLOW.zh-CN.md) / [English](../docs/ROCM_WORKFLOW.md)
- [../docs/ROCM_TUNING_HISTORY.zh-CN.md](../docs/ROCM_TUNING_HISTORY.zh-CN.md) / [English](../docs/ROCM_TUNING_HISTORY.md)
- [../docs/TUNING_GUIDE_ROCM.zh-CN.md](../docs/TUNING_GUIDE_ROCM.zh-CN.md) / [English](../docs/TUNING_GUIDE_ROCM.md)

<!-- W7900_LATEST_EXPERIMENTS_20260616_BEGIN -->
## W7900 最新实验摘要 / 2026-06-16

这些 compact summary 记录最新的 W7900 / `gfx1100` 实验里程碑。raw MPS 文件、raw profiler traces 和大型运行目录均保存在 Git 外部。

| 里程碑 | 摘要 | Compact CSV 输出 |
|---|---|---|
| P2: rocprof starter3 | [W7900 rocprof starter3 摘要](w7900_rocprof_starter3_summary_20260616.zh-CN.md) | [runtime](w7900_rocprof_starter3_runtime_20260616.csv), [solver](w7900_rocprof_starter3_solver_20260616.csv), [HIP API top](w7900_rocprof_starter3_hip_api_top_20260616.csv), [kernel top](w7900_rocprof_starter3_kernel_top_20260616.csv) |
| P3: hard3 probe2 600s | [W7900 hard3 probe2 600s 摘要](w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md) | [runtime](w7900_large_mps_hard3_probe2_600s_runtime_20260616.csv), [solver](w7900_large_mps_hard3_probe2_600s_solver_20260616.csv), [case list](cases_w7900_large_mps_hard3_probe2.txt) |
| P4: before/current fast-core6 | [W7900 before/current fast-core6 摘要](w7900_before_current_core6_fast_summary_20260616.zh-CN.md) | [comparison](w7900_before_current_core6_fast_comparison_20260616.csv), [current solver](w7900_before_current_core6_fast_current_solver_20260616.csv), [pre-tuning solver](w7900_before_current_core6_fast_pre_tuning_solver_20260616.csv), [case list](cases_w7900_large_mps_before_after_core6_fast.txt) |
| P5: 8-card fast8 batch throughput | [W7900 8-card fast8 batch 摘要](w7900_8card_batch_fast8_summary_20260616.zh-CN.md) | [comparison](w7900_8card_batch_fast8_comparison_20260616.csv), [concurrent solver](w7900_8card_batch_fast8_concurrent_solver_20260616.csv), [single-GPU sequential solver](w7900_8card_batch_fast8_single_gpu_seq_solver_20260616.csv), [case list](cases_w7900_8card_batch_fast8.txt) |

关键结果：

- P2 记录 W7900 `rocprof` starter3 的 compact profiling 证据；raw trace 文件不进入 Git。
- P3 确认 `dlr1` 和 `fhnw-binschedule1` 在 600 秒诊断预算下仍属于 hard case。
- P4 显示 `ae3b683 / pre_tuning` 与当前 `rocm-w7900-gfx1100` 在 fast-core6 上均达到 6/6 `OPTIMAL`，但性能结果是混合的，不能写成笼统加速结论。
- P5 显示 8 个独立 MPS 任务在 8 张 W7900 上并发完成时间为 146s，而单张 W7900 顺序运行需要 558s，实测 batch makespan speedup 约为 3.82x。
<!-- W7900_LATEST_EXPERIMENTS_20260616_END -->

<!-- W7900_LATEST_FIGURES_20260616_BEGIN -->
## W7900 最新实验图表 / 2026-06-16

| 图表索引 | 说明 |
|---|---|
| [W7900 最新实验图表](w7900_latest_experiment_figures_20260616.zh-CN.md) | 包含 8-card fast8 吞吐、before/current fast-core6、hard3 probe2、rocprof kernel 占比等 SVG 图 |
<!-- W7900_LATEST_FIGURES_20260616_END -->

## W7900 before/current 派生指标 / 2026-06-17

fast-core6 派生分析把总求解时间拆分为迭代次数和单迭代执行耗时，
用于避免只看 solve time 得出片面结论。

- 汇总：[w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md](w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md)
- CSV：[w7900_before_current_core6_fast_derived_metrics_20260617.csv](w7900_before_current_core6_fast_derived_metrics_20260617.csv)
- 英文汇总：[w7900_before_current_core6_fast_derived_metrics_20260617.md](w7900_before_current_core6_fast_derived_metrics_20260617.md)
- 单迭代耗时比图：[w7900_before_current_fast_core6_ms_per_iter_ratio.svg](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)
- 迭代次数比图：[w7900_before_current_fast_core6_iter_ratio.svg](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

关键结论：current 在 6 个 fast-core6 case 上均降低了单迭代执行耗时，
但由于部分 case 迭代次数增加，总 solve time 仍呈 mixed pattern。

## W7900 P10 targeted rocprof / 2026-06-17

P10 基于 P9 派生指标选择 5 个代表 case，对 current W7900/gfx1100
分支做 targeted profiling。

- 汇总：[w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md](w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md)
- 英文汇总：[w7900_p10_current_targeted_rocprof_20260617_summary.md](w7900_p10_current_targeted_rocprof_20260617_summary.md)
- 运行 CSV：[w7900_p10_current_targeted_rocprof_20260617_runtime.csv](w7900_p10_current_targeted_rocprof_20260617_runtime.csv)
- Kernel top CSV：[w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv](w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv)
- HIP API top CSV：[w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv](w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv)
- Memory copy top CSV：[w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv](w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv)

关键结论：5 个 targeted case 在 current 下均成功完成。trace 结果确认
rocSPARSE CSR SpMV kernel 是主要 GPU 热点之一；较长 case 中
`hipMemcpy`、`hipMemcpyAsync` 和 `hipLaunchKernel` 也是突出的 HIP API 成本。

## W7900 P11 runtime 调用点清单 / 2026-06-17

P11 先从源码级 runtime callsite inventory 开始，再决定是否做优化 patch。
这是有意设计的 pre-patch triage 步骤。

- 汇总：[w7900_p11_runtime_callsite_inventory_20260617.zh-CN.md](w7900_p11_runtime_callsite_inventory_20260617.zh-CN.md)
- 英文汇总：[w7900_p11_runtime_callsite_inventory_20260617.md](w7900_p11_runtime_callsite_inventory_20260617.md)
- CSV：[w7900_p11_runtime_callsite_inventory_20260617.csv](w7900_p11_runtime_callsite_inventory_20260617.csv)

关键结论：P10 显示 targeted cases 中 rank-1 HIP API 成本是 `hipMemcpy`，
rank-1 GPU kernel 是 `rocsparse::csrmvn_general_kernel`。因此 P11 先定位
copy、synchronization、sparse-BLAS、BLAS 和 kernel-launch 调用点，再决定是否改代码。

## W7900 P11 第一轮优化候选 / 2026-06-17

P11 first-patch candidate analysis 把 P10 targeted rocprof 结果和
P11 runtime 调用点清单结合起来，在真正改 solver 代码前，对下一步安全
优化方向进行排序。

- 汇总：[w7900_p11_first_patch_candidates_20260617.zh-CN.md](w7900_p11_first_patch_candidates_20260617.zh-CN.md)
- 英文汇总：[w7900_p11_first_patch_candidates_20260617.md](w7900_p11_first_patch_candidates_20260617.md)
- CSV：[w7900_p11_first_patch_candidates_20260617.csv](w7900_p11_first_patch_candidates_20260617.csv)

关键结论：copy reduction 很诱人，因为 P10 显示 `hipMemcpy` 是 rank-1
HIP API 成本；但如果这些 copy 绑定 residual、restart 或 termination 逻辑，
就具有数值风险。因此第一个代码 patch 应该是 opt-in 且必须经过验证。

## W7900 P11 SpMV algorithm switch smoke / 2026-06-17

本次 smoke validation 检查第一个真正的 P11 tuning patch：
opt-in HIP SpMV algorithm switch。

- 汇总：[w7900_p11_spmv_alg_switch_smoke_20260617_summary.zh-CN.md](w7900_p11_spmv_alg_switch_smoke_20260617_summary.zh-CN.md)
- 英文汇总：[w7900_p11_spmv_alg_switch_smoke_20260617_summary.md](w7900_p11_spmv_alg_switch_smoke_20260617_summary.md)
- CSV：[w7900_p11_spmv_alg_switch_smoke_20260617.csv](w7900_p11_spmv_alg_switch_smoke_20260617.csv)

关键结论：`set-cover-model` 在三种模式下均成功完成：默认 `csr_alg2`、
opt-in `default` 和 opt-in `csr_alg1`。初始 smoke 中该 patch 保持了
solver status 和迭代数一致。
