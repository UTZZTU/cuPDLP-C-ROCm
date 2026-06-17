# 竞赛入口文档：基于 Radeon GPU 的 ROCm 大规模线性规划求解器迁移与性能分析

> English: [COMPETITION_README.md](COMPETITION_README.md)

本文是通用 ROCm/HIP 迁移与验证开源仓库中的评审阅读路径，不替代通用 README；它只负责把项目证据映射到 AMD ROCm / Radeon 赛题要求。

## 项目题目

**基于 AMD ROCm 与 Radeon GPU 的大规模线性规划求解器迁移、验证与性能分析**

## 项目背景与挑战

大规模线性规划是典型科研计算和运筹优化工作负载。cuPDLP/PDLP 类求解器反复使用稀疏矩阵向量乘、向量更新、归约和数值收敛判断。上游项目主要面向 CUDA，因此本项目的挑战是将求解器迁移到 AMD ROCm/HIP，同时保持正确性、可复现性和跨设备可比较性。

## 目标平台

| 平台 | 作用 |
|---|---|
| Radeon 890M / `gfx1150` | ROCm/HIP 首轮迁移、调优历史和 baseline 验证 |
| Radeon PRO W7900 / `gfx1100` | large-MPS 工作站 GPU 验证、P10 profiling、P11 SpMV tuning 与 P12 rejected experiment 记录 |
| RTX 3090 / RTX 4090D / H100 | CUDA 跨设备参考 |

## 方案与实现

| 方向 | 仓库证据 |
|---|---|
| ROCm/HIP 迁移 | HIP backend、ROCm build workflow、CUDA/ROCm compatibility fixes |
| 验证 | smoke、Netlib、large-MPS case lists、parsed CSV summaries |
| Benchmark | 890M、W7900、3090、4090D、H100 reference data |
| W7900 当前状态 | [W7900 当前状态](W7900_CURRENT_STATUS.zh-CN.md) |
| 性能分析 | [W7900 性能行为分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md) |
| 优化基线 | [W7900 优化基线说明](W7900_OPTIMIZATION_BASELINES.zh-CN.md) |
| Profiling 计划 | [W7900 ROCm profiling 计划](W7900_ROCM_PROFILING_PLAN.zh-CN.md) |
| 评分项对照 | [竞赛评分项对照](COMPETITION_SCORECARD.zh-CN.md) |
| 提交清单 | [提交清单](SUBMISSION_CHECKLIST.zh-CN.md) |
| 架构与证据图 | [项目架构图](assets/competition/project_architecture.svg), [证据地图](assets/competition/evidence_map.svg) |
| Validation 索引 | [validation README](../validation/README.zh-CN.md) |

## 当前 W7900 成果

W7900 分支已经不再只是 first-port smoke 实验。目前已有：

- W7900 smoke validation；
- W7900 Netlib 27-case validation；
- W7900 large-MPS `initial17_safe`；
- W7900 large-MPS `watchlist6` 和 `near_optimal2`；
- W7900 large-MPS `non-hard23`：23/23 `OPTIMAL`；
- hard3 拆分：`dlr1.mps`、`Dual2_5000.mps`、`fhnw-binschedule1.mps`。

| 指标 | 数值 |
|---|---|
| W7900 non-hard23 cases | 23 |
| Termination | 23/23 `OPTIMAL` |
| Total wall time | 2960.171 s |
| Total solve time | 2742.940 s |
| 当前状态 | post-890M-tuning engineering baseline |

## 重要基线修正

当前 W7900 non-hard23 结果**不是**未优化 first-port baseline，而是 current post-890M-tuning engineering baseline。

| 角色 | 版本 | 目的 |
|---|---|---|
| Before | `ae3b683` / `pre_tuning` | 真正 first-runnable ROCm anchor |
| Current | current `rocm-w7900-gfx1100` | post-890M-tuning W7900 engineering baseline |
| After / accepted endpoint | P11 current W7900 tuning policy | 当前默认 `HIPSPARSE_SPMV_CSR_ALG1`，旧默认可用 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 回退 |

## 性能解释

项目同时使用 aggregate 和 per-case 分析。aggregate time 有价值，但 W7900 的竞争力在 per-case 层面更清楚。核心解释是：

```text
total time ≈ per-iteration cost × number of iterations
```

W7900 更适合规模足够大、带宽敏感、SpMV/向量操作占比较高且收敛稳定的 case。`s100`、`Primal2_1000` 等慢 case 应结合迭代次数、gap trajectory 和 kernel performance 一起解释。

## 下一步计划状态

原计划中的 W7900 starter profiling、hard3 short probes、before/current core6 comparison 和 W7900-specific tuning 已由 P10/P11/P12 证据链闭环：

1. P10 targeted rocprof profiling 已完成并归档。
2. hard3 probe2 已完成，hard3 不混入 primary non-hard23 baseline。
3. before/current fast-core6 已完成；若要增强性能统计说服力，后续只补 representative repeated validation。
4. P11 已完成 SpMV algorithm switch、smoke、five-case sweep，并将当前默认设为 `HIPSPARSE_SPMV_CSR_ALG1`。
5. P12 已记录一个被拒绝的 SpMV buffer algorithm consistency patch，说明额外 execution-layer 改动经过保守验证。

<!-- REPRODUCIBILITY_20260614_BEGIN -->
## 可复现性

评委导向的复现步骤见 [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md)。

它覆盖：

- 没有 W7900 机器时检查已提交 W7900 non-hard23 summaries；
- fresh W7900 机器恢复；
- large-MPS 数据放置与 SHA256 校验；
- smoke validation；
- starter `rocprofv3` profiling workflow；
- 文件提交策略。
<!-- REPRODUCIBILITY_20260614_END -->

## 提交材料映射

| 竞赛材料 | 仓库当前状态 |
|---|---|
| 技术论文 | 可基于本文、performance behavior、tuning history、profiling results 撰写 |
| 演示说明 PPT | 可基于 W7900 current status、P10 targeted profiling、P11 SpMV tuning、P12 rejected finding 和 cuPDLPx positioning 制作 |
| 演示视频 | 展示 build、validation、charts 和 profiling workflow |
| 工程代码仓库 | 当前仓库已有 scripts、validation CSV、Markdown summaries、SVG charts |
| 可复现性 | 已在 [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md) 中说明；覆盖环境恢复、数据校验、期望输出和 starter profiling |

<!-- W7900_LATEST_EXPERIMENTS_20260616_BEGIN -->
## 最新 W7900 证据 / 2026-06-16

最新提交的 W7900 证据可从 validation 索引进入：

- [rocprof starter3](../validation/w7900_rocprof_starter3_summary_20260616.zh-CN.md)：三个 starter case 的 compact profiling 摘要。
- [hard3 probe2 600s](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md)：hard case 诊断结果。
- [before/current fast-core6](../validation/w7900_before_current_core6_fast_summary_20260616.zh-CN.md)：`ae3b683 / pre_tuning` 与当前分支对比。
- [8-card fast8 batch throughput](../validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md)：8 个独立 MPS 任务，8 卡并发 146s，对比单 GPU 顺序 558s。
<!-- W7900_LATEST_EXPERIMENTS_20260616_END -->

## W7900 竞赛口径最终状态 / 2026-06-17

当前仓库范围内，面向竞赛展示的 W7900 工作流已经完成。此前写作“next planned
work”的 W7900 profiling、before/current analysis 和 W7900-specific tuning
已由 P10/P11/P12 证据链闭环。

最终竞赛口径结论：

- W7900 / `gfx1100` ROCm build 和 validation 已完成。
- P10 targeted rocprof profiling 已归档。
- P11 SpMV tuning 是已接受的 W7900-specific tuning endpoint。
- 当前 W7900 默认 SpMV algorithm 为
  `HIPSPARSE_SPMV_CSR_ALG1`。
- 旧默认可通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 恢复。
- P12 记录了一次被拒绝的 buffer-algorithm consistency patch，说明额外
  execution-layer 改动也经过了保守验证。

推荐最终证据入口：

- `docs/W7900_CURRENT_STATUS.zh-CN.md`
- `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`
- `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md`
