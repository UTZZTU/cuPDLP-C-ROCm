# 竞赛评分项与仓库证据对照

> English: [COMPETITION_SCORECARD.md](COMPETITION_SCORECARD.md)

本文把竞赛评审关注点映射到仓库当前证据，不是普通读者的主页。普通读者应从[中文主页](../README.md)或[文档地图](README.md)开始。

## 当前范围

**项目：** 将 cuPDLP-C 迁移到 AMD ROCm/HIP，并建立验证、profiling 与保守调优证据链。

| 平台 | 作用 |
|---|---|
| Radeon PRO W7900 / `gfx1100` | 当前主要 ROCm 验证与调优平台 |
| Radeon 890M / `gfx1150` | 早期迁移与调优里程碑 |
| RTX 3090 / RTX 4090D / H100 | CUDA 参考 |
| CPU | 正确性与可移植性参考 |

项目不声称提出新的线性规划算法。核心贡献是后端迁移及其证据驱动的工程方法。

## 评分项证据表

| 评审方向 | 仓库证据 | 当前状态与边界 |
|---|---|---|
| 项目背景与挑战 | [竞赛入口](COMPETITION_README.zh-CN.md)、[迁移案例](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) | 仓库叙事已完整；论文/PPT 属于独立展示材料 |
| 方案与架构 | HIP backend、兼容层、[后端模式](BACKEND_MODES_AND_NAMING.zh-CN.md)、[porting 指南](ROCM_PORTING_GUIDE.zh-CN.md) | CPU、CUDA、ROCm 路径已说明；可选 Python/apps 不属于主要验证合同 |
| ROCm 组件使用 | HIP runtime、hipBLAS、hipSPARSE、`rocprofv3`、`gfx1100` 构建脚本 | 已在 W7900 上实现并形成证据 |
| 功能验证 | [验证语义](VALIDATION.zh-CN.md)、[validation 索引](../validation/README.zh-CN.md) | smoke、Netlib、large-MPS non-hard23、困难 case 诊断和重复验证均已归档 |
| 性能分析 | [W7900 性能行为](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)、P10 summaries、跨设备 CSV | P10 表明 rocSPARSE CSR SpMV 是主要 GPU 热点；同时保留 aggregate 与 per-case 解释 |
| 平台调优 | [调优历史](ROCM_TUNING_HISTORY.zh-CN.md)、[P11 summary](../validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md) | P11 接受 `HIPSPARSE_SPMV_CSR_ALG1`；`csr_alg2` 保留为回退 |
| 保守工程流程 | [P12 negative result](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md) | 因收敛路径变化而拒绝，证明不能只凭运行时间接受执行层修改 |
| 重复 before/current 证据 | [P14-A1 summary](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md) | current 6/6 胜出；geomean 1.18889；median 1.19502；迭代数一致 |
| Large-case 结果 | [W7900 当前状态](W7900_CURRENT_STATUS.zh-CN.md) | non-hard23 为 23/23 `OPTIMAL`；hard3 明确单独报告 |
| 多 GPU 证据 | [8-card fast8 summary](../validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md) | 仅表示独立任务吞吐，不是单个 LP 的分布式算法 |
| 可复现性 | [复现指南](REPRODUCIBILITY.zh-CN.md)、脚本、case lists、checksums、curated CSV | 任意主机可检查静态证据；重新验证 W7900 性能需要匹配的 ROCm 主机 |
| 交付准备 | [提交清单](SUBMISSION_CHECKLIST.zh-CN.md) | 仓库证据已准备；论文、PPT、视频是独立交付物 |

## 关键数字

| 结论 | 数值 |
|---|---:|
| W7900 non-hard23 | 23/23 `OPTIMAL` |
| Total wall time | 2960.171 s |
| Total solve time | 2742.940 s |
| P14-A1 current wins | 6/6 |
| P14-A1 geomean speedup | 1.18889 |
| P14-A1 median speedup | 1.19502 |
| 8 个独立任务 | 8 卡并发 146 s vs 单卡顺序 558 s |

## 解释规则

评审时必须保持以下边界：

1. 当前 W7900 结果是 post-890M-tuning engineering baseline，不是真正 first-runnable baseline。
2. W7900 before anchor 是 `ae3b683 / pre_tuning`。
3. 8 卡结果表示独立任务吞吐。
4. hard3 不隐藏在 non-hard23 中。
5. W7900 aggregate time 仍落后于高端 CUDA 参考，但 per-case 竞争力不同。
6. P12 是被拒绝的实验，不能包装为成功优化。
7. 可选 P14-B ALG1-vs-ALG2 repeated evidence 是增强项，不是未完成的核心范围。

## 推荐评审路径

1. [竞赛入口](COMPETITION_README.zh-CN.md)
2. [W7900 当前状态](W7900_CURRENT_STATUS.zh-CN.md)
3. [P10 targeted profiling](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md)
4. [P11 SpMV tuning](../validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md)
5. [P12 negative result](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md)
6. [P14-A1 repeated validation](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md)
7. [可复现性指南](REPRODUCIBILITY.zh-CN.md)
