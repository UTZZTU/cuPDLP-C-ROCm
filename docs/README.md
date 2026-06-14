# Documentation map / 文档地图

This page is the central index for project-maintained documentation.  
本页是项目维护文档的总索引，目的是避免文档存在但没有入口的问题。

<!-- COMPETITION_README_20260614_BEGIN -->
<!-- REPRODUCIBILITY_20260614_BEGIN -->
| Reproducibility / 可复现性 | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md) | How to reproduce committed summaries, recover W7900 machines, check data, and run starter profiling |
<!-- REPRODUCIBILITY_20260614_END -->

| Competition README / 竞赛入口 | [COMPETITION_README.md](COMPETITION_README.md) | [COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md) | Reviewer-facing entry point aligned with the AMD ROCm/Radeon contest track |
<!-- COMPETITION_README_20260614_END -->

## Main entry points / 主入口

| Topic / 主题 | English | 中文 | Notes / 说明 |
|---|---|---|---|
| Repository homepage / 仓库主页 | [../README.md](../README.md) | [../README.zh-CN.md](../README.zh-CN.md) | Main project overview |
| ROCm 890M quick README | [../README_ROCM_gfx1150.md](../README_ROCM_gfx1150.md) | [../README_ROCM_gfx1150.zh-CN.md](../README_ROCM_gfx1150.zh-CN.md) | Focused quick-start page for the gfx1150 milestone |
| Validation index / Validation 索引 | [../validation/README.md](../validation/README.md) | [../validation/README.zh-CN.md](../validation/README.zh-CN.md) | Validation Markdown summaries and CSV links |
| Benchmark index / Benchmark 索引 | [benchmarks/README.md](benchmarks/README.md) | [benchmarks/README.md](benchmarks/README.md) | Benchmark documents and CSV links |
| Upstream reference / 上游参考 | [../README_UPSTREAM.md](../README_UPSTREAM.md) | — | Intentionally preserved as upstream snapshot; not translated |

## Workflow, validation, and build semantics / 工作流、验证与构建语义

| Topic / 主题 | English | 中文 |
|---|---|---|
| Daily ROCm workflow / 日常 ROCm 工作流 | [ROCM_WORKFLOW.md](ROCM_WORKFLOW.md) | [ROCM_WORKFLOW.zh-CN.md](ROCM_WORKFLOW.zh-CN.md) |
| Validation semantics / 验证语义 | [VALIDATION.md](VALIDATION.md) | [VALIDATION.zh-CN.md](VALIDATION.zh-CN.md) |
| Backend modes and naming / 后端模式与命名 | [BACKEND_MODES_AND_NAMING.md](BACKEND_MODES_AND_NAMING.md) | [BACKEND_MODES_AND_NAMING.zh-CN.md](BACKEND_MODES_AND_NAMING.zh-CN.md) |
| ROCm porting guide / ROCm porting 指南 | [ROCM_PORTING_GUIDE.md](ROCM_PORTING_GUIDE.md) | [ROCM_PORTING_GUIDE.zh-CN.md](ROCM_PORTING_GUIDE.zh-CN.md) |
| CUDA to ROCm case study / CUDA 到 ROCm 迁移案例 | [CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) | [CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) |

## Validation data directory / Validation 数据目录

| Topic / 主题 | English | 中文 | Raw CSV / 原始汇总 |
|---|---|---|---|
| Validation directory index / validation 目录索引 | [../validation/README.md](../validation/README.md) | [../validation/README.zh-CN.md](../validation/README.zh-CN.md) | See validation index |
| W7900 smoke validation / W7900 smoke 验证 | [../validation/w7900_smoke_summary_20260611.md](../validation/w7900_smoke_summary_20260611.md) | [../validation/w7900_smoke_summary_20260611.zh-CN.md](../validation/w7900_smoke_summary_20260611.zh-CN.md) | [CSV](../validation/w7900_smoke_summary_20260611.csv) |
| W7900 extended Netlib validation / W7900 扩展 Netlib 验证 | [../validation/w7900_extended_netlib_summary_20260611.md](../validation/w7900_extended_netlib_summary_20260611.md) | [../validation/w7900_extended_netlib_summary_20260611.zh-CN.md](../validation/w7900_extended_netlib_summary_20260611.zh-CN.md) | [CSV](../validation/w7900_extended_netlib_summary_20260611.csv) |
| W7900 27-case ROCm baseline / W7900 27-case ROCm baseline | [../validation/w7900_27cases_baseline_20260611.md](../validation/w7900_27cases_baseline_20260611.md) | [../validation/w7900_27cases_baseline_20260611.zh-CN.md](../validation/w7900_27cases_baseline_20260611.zh-CN.md) | [aggregated CSV](../validation/w7900_27cases_baseline_20260611_aggregated.csv), [raw CSV](../validation/w7900_27cases_baseline_20260611_raw.csv) |
| W7900 vs cross-device reference / W7900 跨设备参考对比 | [../validation/w7900_vs_cross_device_27cases_20260611.md](../validation/w7900_vs_cross_device_27cases_20260611.md) | [../validation/w7900_vs_cross_device_27cases_20260611.zh-CN.md](../validation/w7900_vs_cross_device_27cases_20260611.zh-CN.md) | [CSV](../validation/w7900_vs_cross_device_27cases_20260611.csv) |
| Cross-device Netlib summary / 跨设备 Netlib 汇总 | [CROSS_DEVICE_BENCHMARKS.md](CROSS_DEVICE_BENCHMARKS.md) | [CROSS_DEVICE_BENCHMARKS.zh-CN.md](CROSS_DEVICE_BENCHMARKS.zh-CN.md) | [cross_device_full_summary.csv](../validation/cross_device_full_summary.csv) |
| current vs reduce repeated comparison | [../validation/rocm_current_vs_reduce_27cases_repeats_comparison.md](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.md) | [../validation/rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md) | [comparison](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.csv), [aggregated](../validation/rocm_current_vs_reduce_27cases_repeats_aggregated.csv), [raw](../validation/rocm_current_vs_reduce_27cases_repeats_raw.csv) |
| rocprof tuning milestones / rocprof tuning 里程碑 | [../validation/rocm_prof_tuning_milestones_summary.md](../validation/rocm_prof_tuning_milestones_summary.md) | [../validation/rocm_prof_tuning_milestones_summary.zh-CN.md](../validation/rocm_prof_tuning_milestones_summary.zh-CN.md) | [summary](../validation/rocm_prof_tuning_milestones_summary.csv), [deltas](../validation/rocm_prof_tuning_milestones_deltas.csv), [HIP API](../validation/rocm_prof_tuning_milestones_hip_api_top.csv), [kernel](../validation/rocm_prof_tuning_milestones_kernel_top.csv), [memory-copy](../validation/rocm_prof_tuning_milestones_memory_copy_top.csv) |
| tuning ablation 6-case repeats / 6-case tuning ablation 重复测试 | [../validation/rocm_tuning_ablation_6cases_repeats_summary.md](../validation/rocm_tuning_ablation_6cases_repeats_summary.md) | [../validation/rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md](../validation/rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md) | [summary](../validation/rocm_tuning_ablation_6cases_repeats_summary.csv), [raw](../validation/rocm_tuning_ablation_6cases_repeats_raw.csv) |

## Benchmarks and numerical behavior / Benchmark 与数值行为

| Topic / 主题 | English | 中文 | Raw data / 原始汇总数据 |
|---|---|---|---|
| Netlib cross-device benchmarks / Netlib 跨设备 benchmark | [CROSS_DEVICE_BENCHMARKS.md](CROSS_DEVICE_BENCHMARKS.md) | [CROSS_DEVICE_BENCHMARKS.zh-CN.md](CROSS_DEVICE_BENCHMARKS.zh-CN.md) | [cross_device_full_summary.csv](../validation/cross_device_full_summary.csv) |
| Large MPS benchmark plan / large MPS benchmark 计划 | [LARGE_MPS_BENCHMARK_PLAN.md](LARGE_MPS_BENCHMARK_PLAN.md) | [LARGE_MPS_BENCHMARK_PLAN.zh-CN.md](LARGE_MPS_BENCHMARK_PLAN.zh-CN.md) | See benchmark docs below |
<!-- W7900_LARGE_MPS_INITIAL17_20260613_BEGIN -->
<!-- W7900_LARGE_MPS_NONHARD23_20260613_BEGIN -->
<!-- W7900_CURRENT_STATUS_20260614_BEGIN -->
<!-- W7900_DOC_SWEEP_20260614_BEGIN -->
| W7900 hard3 notes / W7900 hard3 说明 | [W7900_LARGE_MPS_HARD3_NOTES.md](W7900_LARGE_MPS_HARD3_NOTES.md) | [W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md](W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md) | hard3 split for `dlr1`, `Dual2_5000`, and `fhnw-binschedule1` |
<!-- W7900_DOC_SWEEP_20260614_END -->

<!-- W7900_PERFORMANCE_BEHAVIOR_20260614_BEGIN -->
<!-- W7900_ROCM_PROFILING_PLAN_20260614_BEGIN -->
<!-- W7900_OPTIMIZATION_BASELINES_20260614_BEGIN -->
| W7900 optimization baselines / W7900 优化基线 | [W7900_OPTIMIZATION_BASELINES.md](W7900_OPTIMIZATION_BASELINES.md) | [W7900_OPTIMIZATION_BASELINES.zh-CN.md](W7900_OPTIMIZATION_BASELINES.zh-CN.md) | Clarifies `ae3b683` pre-tuning, `b44c7ab` reduce-scalar-copies, current engineering baseline, and future before/after policy |
<!-- W7900_OPTIMIZATION_BASELINES_20260614_END -->

| W7900 ROCm profiling plan / W7900 ROCm profiling 计划 | [W7900_ROCM_PROFILING_PLAN.md](W7900_ROCM_PROFILING_PLAN.md) | [W7900_ROCM_PROFILING_PLAN.zh-CN.md](W7900_ROCM_PROFILING_PLAN.zh-CN.md) | Profiling case matrix, metrics, tools, and output policy before ROCm/gfx1100 tuning |
<!-- W7900_ROCM_PROFILING_PLAN_20260614_END -->

| W7900 performance behavior / W7900 性能行为分析 | [W7900_PERFORMANCE_BEHAVIOR.md](W7900_PERFORMANCE_BEHAVIOR.md) | [W7900_PERFORMANCE_BEHAVIOR.zh-CN.md](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md) | Theory/application value, speedup charts, case classes, and tuning implications |
<!-- W7900_PERFORMANCE_BEHAVIOR_20260614_END -->

| W7900 current status / W7900 当前状态 | [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md) | [W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md) | Current W7900 baseline, charts, non-hard23 status, and hard3 split |
<!-- W7900_CURRENT_STATUS_20260614_END -->

| W7900 large-MPS non-hard23 baseline / W7900 large-MPS non-hard23 baseline | [../validation/w7900_large_mps_nonhard23_20260613.md](../validation/w7900_large_mps_nonhard23_20260613.md) | [../validation/w7900_large_mps_nonhard23_20260613.zh-CN.md](../validation/w7900_large_mps_nonhard23_20260613.zh-CN.md) | [solver CSV](../validation/w7900_large_mps_nonhard23_20260613.csv), [runtime CSV](../validation/w7900_large_mps_nonhard23_20260613_runtime.csv) |
<!-- W7900_LARGE_MPS_NONHARD23_20260613_END -->

| W7900 large-MPS initial17 safe baseline / W7900 large-MPS initial17 safe baseline | [../validation/w7900_large_mps_initial17_safe_20260613.md](../validation/w7900_large_mps_initial17_safe_20260613.md) | [../validation/w7900_large_mps_initial17_safe_20260613.zh-CN.md](../validation/w7900_large_mps_initial17_safe_20260613.zh-CN.md) | [solver CSV](../validation/w7900_large_mps_initial17_safe_20260613.csv), [runtime CSV](../validation/w7900_large_mps_initial17_safe_20260613_runtime.csv) |
<!-- W7900_LARGE_MPS_INITIAL17_20260613_END -->

| Large MPS CUDA/ROCm baseline / large MPS CUDA/ROCm baseline | [benchmarks/large_mps_cuda_rocm_baseline_20260610.md](benchmarks/large_mps_cuda_rocm_baseline_20260610.md) | [benchmarks/large_mps_cuda_rocm_baseline_20260610.zh-CN.md](benchmarks/large_mps_cuda_rocm_baseline_20260610.zh-CN.md) | [platform summary](../results/benchmarks/large_mps_platform_summary_20260610.csv), [per-case timing](../results/benchmarks/large_mps_per_case_timing_summary_20260610.csv) |
| cuPDLPx vs cuPDLP-C short13 / cuPDLPx 对比 | [benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.md](benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.md) | [benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.zh-CN.md](benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.zh-CN.md) | [comparison CSV](../results/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.csv) |
| greenbea numerical behavior / greenbea 数值行为 | [NUMERICAL_BEHAVIOR_GREENBEA.md](NUMERICAL_BEHAVIOR_GREENBEA.md) | [NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md](NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md) | Case-specific notes |

## Profiling and tuning / Profiling 与调优

| Topic / 主题 | English | 中文 |
|---|---|---|
| ROCm profiling notes / ROCm profiling 记录 | [ROCM_PROFILING_NOTES.md](ROCM_PROFILING_NOTES.md) | [ROCM_PROFILING_NOTES.zh-CN.md](ROCM_PROFILING_NOTES.zh-CN.md) |
| ROCm tuning history / ROCm tuning 历史 | [ROCM_TUNING_HISTORY.md](ROCM_TUNING_HISTORY.md) | [ROCM_TUNING_HISTORY.zh-CN.md](ROCM_TUNING_HISTORY.zh-CN.md) |
| ROCm tuning guide / ROCm tuning 指南 | [TUNING_GUIDE_ROCM.md](TUNING_GUIDE_ROCM.md) | [TUNING_GUIDE_ROCM.zh-CN.md](TUNING_GUIDE_ROCM.zh-CN.md) |

## Maintenance rules / 维护规则

- Keep `README.md`, `README.zh-CN.md`, and this file as the main navigation hubs.
- Keep `validation/README.md` and `validation/README.zh-CN.md` as the validation data entry points.
- Benchmark and validation Markdown summaries should link to their CSV source files.
- If an English project document is updated, update the matching Chinese document.
- If a Chinese project document is updated first, update the matching English document.
- Keep `README_UPSTREAM.md` as an upstream reference snapshot.
