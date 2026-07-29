# Validation 结果索引

> English: [README.md](README.md)

本目录保存可提交、可审阅的 case lists、curated CSV 和 Markdown summaries。
当前正式结论从
[W7900 最终结果](../docs/W7900_FINAL_RESULTS_20260729.zh-CN.md)
开始；日期化文件是不可变历史证据。

## 最终正式 W7900 证据

| 主题 | 入口 | 结论 |
|---|---|---|
| Final compact package | [中文索引](final_w7900_20260729/README.zh-CN.md) | 76/76 正式 solver 记录验证通过 |
| Identity and QC | [identity](final_w7900_20260729/formal_experiment_identity.json) | branch、solver、harness、archive SHA 固定 |
| baseline23 | [aggregated](final_w7900_20260729/baseline_aggregated.csv)、[repeats](final_w7900_20260729/baseline_repeats.csv) | 23 × 2 = 46/46 |
| throughput | [summary](final_w7900_20260729/throughput_summary.csv) | 单卡顺序吞吐两轮完整 |
| precision | [matrix](final_w7900_20260729/precision_matrix.csv)、[aggregated](final_w7900_20260729/precision_aggregated.csv) | 5 × 3 × 2 = 30/30 |
| precision sensitivity | [ratios](final_w7900_20260729/precision_sensitivity.csv) | 目标精度成本实例依赖 |
| resources | [baseline](final_w7900_20260729/baseline_resource_summary.csv)、[precision](final_w7900_20260729/precision_resource_summary.csv) | 正式运行资源覆盖 |
| profiles | [summary](final_w7900_20260729/profile_summary.csv) | 5/5 trace validation PASS |
| static structure | [features](final_w7900_20260729/nonhard23_mps_structural_features.csv) | 23/23 |
| static association | [Spearman](final_w7900_20260729/static_performance_spearman.csv) | 探索性、非因果 |
| final claims | [review table](final_w7900_20260729/final_claims_review.csv) | 数字、来源和边界 |

## 历史 W7900 证据链

以下文件继续保留，用于解释移植、调优和负向实验历史：

| 主题 | Summary | 数据 / 结论 |
|---|---|---|
| Smoke | [中文](w7900_smoke_summary_20260611.zh-CN.md) | CPU 与 ROCm 状态检查 |
| Netlib extended | [中文](w7900_extended_netlib_summary_20260611.zh-CN.md) | 扩展 Netlib |
| 27-case baseline | [中文](w7900_27cases_baseline_20260611.zh-CN.md) | 早期 W7900 基线 |
| 2026-06-13 non-hard23 | [中文](w7900_large_mps_nonhard23_20260613.zh-CN.md) | 早期单轮 23/23 |
| P10 targeted profiling | [中文](w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md) | CSR SpMV、copy、launch 热点 |
| P11 SpMV tuning | [中文](w7900_p11_spmv_tuning_summary_20260617.zh-CN.md) | 接受 `CSR_ALG1` 默认 |
| P12 negative result | [中文](w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md) | 迭代轨迹变化，patch 被拒绝 |
| P14-A1 repeats | [中文](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md) | current 6/6 胜出，迭代数一致 |
| hard3 probe2 | [中文](w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md) | 困难实例单独诊断 |
| 8-card fast8 | [中文](w7900_8card_batch_fast8_summary_20260616.zh-CN.md) | 独立任务吞吐 |

## P10 compact profiling 文件

- [runtime](w7900_p10_current_targeted_rocprof_20260617_runtime.csv)
- [kernel top](w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv)
- [HIP API top](w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv)
- [memory copy](w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv)
- [milestone deltas](w7900_p10_current_targeted_rocprof_20260617_milestone_deltas.csv)

具体 kernel/API 热点结论以这些 compact 表为准；最终 session2 profile 负责正式
采集与 trace 完整性验证。

## 解释规则

1. 最终正式双重复数据替代六月单轮数据作为当前主数字。
2. 日期化历史报告不重写。
3. nonhard23 与 hard3 分开。
4. 单卡 throughput 是顺序独立 MPS。
5. fast8 是八个独立作业。
6. 性能比较同时查看总时间、求解时间、迭代数和数值状态。
7. P12 负向实验不能删除。
8. precision 结论只覆盖五例。
9. 静态关联不证明因果。
10. raw MPS、raw trace、本地运行目录和凭据不提交。

## 相关入口

- [W7900 最终结果](../docs/W7900_FINAL_RESULTS_20260729.zh-CN.md)
- [W7900 当前状态](../docs/W7900_CURRENT_STATUS.zh-CN.md)
- [最终复现指南](../docs/FINAL_REPRODUCTION_GUIDE.zh-CN.md)
- [验证语义](../docs/VALIDATION.zh-CN.md)
- [Profiling 记录](../docs/ROCM_PROFILING_NOTES.zh-CN.md)
