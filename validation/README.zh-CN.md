# Validation 结果索引

> English: [README.md](README.md)

本目录保存可提交、可审阅的 case lists、curated CSV 和 Markdown summaries。日期化文件是实验记录；当前结论请从 [W7900 当前状态](../docs/W7900_CURRENT_STATUS.zh-CN.md) 开始。

## 当前 W7900 主证据

| 主题 | Summary | CSV / 数据 | 结论 |
|---|---|---|---|
| Smoke | [中文](w7900_smoke_summary_20260611.zh-CN.md) | [CSV](w7900_smoke_summary_20260611.csv) | CPU 与 ROCm 状态检查 |
| Netlib extended | [中文](w7900_extended_netlib_summary_20260611.zh-CN.md) | [CSV](w7900_extended_netlib_summary_20260611.csv) | 扩展 Netlib 验证 |
| 27-case baseline | [中文](w7900_27cases_baseline_20260611.zh-CN.md) | [aggregated](w7900_27cases_baseline_20260611_aggregated.csv), [raw](w7900_27cases_baseline_20260611_raw.csv) | W7900 早期完整基线 |
| Large-MPS non-hard23 | [中文](w7900_large_mps_nonhard23_20260613.zh-CN.md) | [solver](w7900_large_mps_nonhard23_20260613.csv), [runtime](w7900_large_mps_nonhard23_20260613_runtime.csv) | 23/23 `OPTIMAL` |
| P10 targeted profiling | [中文](w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md) | [runtime](w7900_p10_current_targeted_rocprof_20260617_runtime.csv), [kernel](w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv), [HIP API](w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv) | CSR SpMV 为主要热点 |
| P11 SpMV tuning | [中文](w7900_p11_spmv_tuning_summary_20260617.zh-CN.md) | [sweep](w7900_p11_spmv_alg_sweep_20260617.csv), [default smoke](w7900_p11_default_spmv_alg1_smoke_20260617.csv) | 接受 `CSR_ALG1` 默认策略 |
| P12 negative result | [中文](w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md) | — | 修改迭代轨迹，patch 被拒绝 |
| P14-A1 quick6 repeats | [中文](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md) | [comparison](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv), [aggregated](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_aggregated.csv), [raw](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_raw.csv) | current 6/6 胜出 |
| hard3 probe2 | [中文](w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md) | [solver](w7900_large_mps_hard3_probe2_600s_solver_20260616.csv), [runtime](w7900_large_mps_hard3_probe2_600s_runtime_20260616.csv) | 困难 case 单独诊断 |
| 8-card fast8 batch | [中文](w7900_8card_batch_fast8_summary_20260616.zh-CN.md) | [comparison](w7900_8card_batch_fast8_comparison_20260616.csv) | 独立任务吞吐，不是单 LP 多 GPU |

## P11 分析链

P11 的结论不是直接从一次 sweep 得出，而是按以下顺序建立：

1. [runtime 调用点清单](w7900_p11_runtime_callsite_inventory_20260617.zh-CN.md)
   [CSV](w7900_p11_runtime_callsite_inventory_20260617.csv)
2. [第一轮优化候选](w7900_p11_first_patch_candidates_20260617.zh-CN.md)
   [CSV](w7900_p11_first_patch_candidates_20260617.csv)
3. [SpMV algorithm switch smoke](w7900_p11_spmv_alg_switch_smoke_20260617_summary.zh-CN.md)
   [CSV](w7900_p11_spmv_alg_switch_smoke_20260617.csv)
4. [五 case algorithm sweep](w7900_p11_spmv_alg_sweep_20260617_summary.zh-CN.md)
   [CSV](w7900_p11_spmv_alg_sweep_20260617.csv)
5. [default ALG1 smoke](w7900_p11_default_spmv_alg1_smoke_20260617_summary.zh-CN.md)
   [CSV](w7900_p11_default_spmv_alg1_smoke_20260617.csv)
6. [P11 最终总结](w7900_p11_spmv_tuning_summary_20260617.zh-CN.md)

## Before/current 与 earlier ROCm 证据

| 主题 | Summary | 数据 |
|---|---|---|
| before/current fast-core6 | [中文](w7900_before_current_core6_fast_summary_20260616.zh-CN.md) | [comparison](w7900_before_current_core6_fast_comparison_20260616.csv) |
| 派生单迭代指标 | [中文](w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md) | [CSV](w7900_before_current_core6_fast_derived_metrics_20260617.csv) |
| W7900 vs cross-device 27 cases | [中文](w7900_vs_cross_device_27cases_20260611.zh-CN.md) | [CSV](w7900_vs_cross_device_27cases_20260611.csv) |
| Cross-device full summary | [项目文档](../docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md) | [CSV](cross_device_full_summary.csv) |
| ROCm current vs reduce repeated | [中文](rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md) | [comparison](rocm_current_vs_reduce_27cases_repeats_comparison.csv), [aggregated](rocm_current_vs_reduce_27cases_repeats_aggregated.csv), [raw](rocm_current_vs_reduce_27cases_repeats_raw.csv) |
| ROCm profiling milestones | [中文](rocm_prof_tuning_milestones_summary.zh-CN.md) | [summary](rocm_prof_tuning_milestones_summary.csv), [deltas](rocm_prof_tuning_milestones_deltas.csv) |
| ROCm tuning ablation | [中文](rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md) | [summary](rocm_tuning_ablation_6cases_repeats_summary.csv), [raw](rocm_tuning_ablation_6cases_repeats_raw.csv) |

## Large-MPS 分层证据

| 分组 | Summary | 数据 |
|---|---|---|
| initial17 safe | [中文](w7900_large_mps_initial17_safe_20260613.zh-CN.md) | [solver](w7900_large_mps_initial17_safe_20260613.csv), [runtime](w7900_large_mps_initial17_safe_20260613_runtime.csv) |
| near-optimal2 | — | [solver](w7900_large_mps_near_optimal2_1800s_20260613.csv), [runtime](w7900_large_mps_near_optimal2_1800s_20260613_runtime.csv) |
| watchlist6 diagnostics | — | [solver](w7900_large_mps_watchlist6_diag_900s_20260613.csv), [runtime](w7900_large_mps_watchlist6_diag_900s_20260613_runtime.csv) |
| non-hard23 merged result | [中文](w7900_large_mps_nonhard23_20260613.zh-CN.md) | [solver](w7900_large_mps_nonhard23_20260613.csv), [runtime](w7900_large_mps_nonhard23_20260613_runtime.csv) |
| hard3 | [项目说明](../docs/W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md) | [probe2 summary](w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md) |

## Case lists

| Purpose | File |
|---|---|
| Basic smoke | [cases.txt](cases.txt) |
| Extended Netlib | [cases_extended_netlib.txt](cases_extended_netlib.txt) |
| W7900 27-case | [cases_benchmark_200m_w7900_27.txt](cases_benchmark_200m_w7900_27.txt) |
| Tuning quick6 | [cases_tuning_quick.txt](cases_tuning_quick.txt) |
| P10 starter3 | [cases_w7900_rocprof_starter3.txt](cases_w7900_rocprof_starter3.txt) |
| before/current core6 | [cases_w7900_large_mps_before_after_core6_fast.txt](cases_w7900_large_mps_before_after_core6_fast.txt) |
| non-hard23 | [cases_w7900_large_mps_before_after_nonhard23.txt](cases_w7900_large_mps_before_after_nonhard23.txt) |
| hard3 | [cases_w7900_large_mps_hard3.txt](cases_w7900_large_mps_hard3.txt) |
| 8-card fast8 | [cases_w7900_8card_batch_fast8.txt](cases_w7900_8card_batch_fast8.txt) |

## 解释规则

- 日期化 summary 是不可变实验记录；新的当前结论更新索引和状态页，不改写旧结果。
- `non-hard23` 与 hard3 分开解释。
- 8-card fast8 是 independent-MPS throughput。
- 性能比较必须同时查看 wall time、solve time、`nIter`、termination、feasibility 和 gap。
- P12 属于负向证据，不能从索引中删除。
- raw `.mps`、raw profiler trace 和机器本地运行目录不提交。

## 相关入口

- [W7900 当前状态](../docs/W7900_CURRENT_STATUS.zh-CN.md)
- [可复现性指南](../docs/REPRODUCIBILITY.zh-CN.md)
- [验证语义](../docs/VALIDATION.zh-CN.md)
- [Benchmark 索引](../docs/benchmarks/README.md)
