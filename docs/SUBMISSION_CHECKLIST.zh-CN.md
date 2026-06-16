# 提交清单

> English: [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)

本文用于跟踪竞赛提交材料，但不把仓库改造成只为竞赛服务的项目。仓库主体仍然是通用 ROCm/HIP 迁移、验证与 benchmark 工程。

## 仓库交付

| 条目 | 状态 | 证据 / 下一步 |
|---|---|---|
| 通用项目 README | 已完成 | [../README.md](../README.md), [../README.zh-CN.md](../README.zh-CN.md) |
| 文档地图 | 已完成 | [README.md](README.md) |
| 竞赛评审阅读路径 | 已完成 | [COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md), [COMPETITION_SCORECARD.zh-CN.md](COMPETITION_SCORECARD.zh-CN.md) |
| 复现文档 | 已完成 | [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md) |
| W7900 当前状态 | 已完成 | [W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md) |
| W7900 性能解释 | 已完成 | [W7900_PERFORMANCE_BEHAVIOR.zh-CN.md](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md) |
| W7900 优化基线口径 | 已完成 | [W7900_OPTIMIZATION_BASELINES.zh-CN.md](W7900_OPTIMIZATION_BASELINES.zh-CN.md) |
| Docker/container 骨架 | 已提供骨架 | [../docker/Dockerfile.w7900](../docker/Dockerfile.w7900), [../docker/README_DOCKER_W7900.zh-CN.md](../docker/README_DOCKER_W7900.zh-CN.md)。这是环境声明骨架，不是当前 W7900 性能数字来源。 |
| 项目架构图与证据地图 | 已完成 | [项目架构图](assets/competition/project_architecture.svg), [证据地图](assets/competition/evidence_map.svg) |
| 整理后的 validation summary | 当前里程碑已完成 | 见 [../validation/README.zh-CN.md](../validation/README.zh-CN.md) |
| raw MPS 数据策略 | 已完成 | 原始 `.mps` 文件保存在 Git 外部。 |

## W7900 实验条目

| 条目 | 状态 | 说明 |
|---|---|---|
| W7900 smoke validation | 已完成 | 仓库已记录 completed smoke validation。 |
| W7900 Netlib 27-case validation | 已完成 | 仓库已记录 completed Netlib validation。 |
| W7900 non-hard large-MPS baseline | 已完成 | `non-hard23`: 23/23 `OPTIMAL`；hard3 单独跟踪。 |
| W7900 `rocprof` starter3 | 等 W7900 机器 | case: `set-cover-model.mps`, `square41.mps`, `s100.mps`。 |
| hard3 probe2 | 等 W7900 机器 | case: `dlr1.mps`, `fhnw-binschedule1.mps`。 |
| true before/current core6 | 等 W7900 机器 | `ae3b683 / pre_tuning` 对比当前 `rocm-w7900-gfx1100`。 |
| W7900-specific tuning | 等 profiling 证据 | 不盲目调代码；等 profiler 结果后决定第一刀优化目标。 |
| W7900 profiling 结果摘要 | 等 W7900 机器 | 只提交 compact CSV/Markdown，不提交 raw profiler traces。 |

## 竞赛提交材料

| 材料 | 状态 | 仓库支撑 |
|---|---|---|
| 技术论文 | 未开始 | 使用 `COMPETITION_README`、`COMPETITION_SCORECARD`、`REPRODUCIBILITY`、W7900 状态/性能文档，以及后续 profiling 结果。 |
| 演示 PPT | 未开始 | 等论文大纲和 W7900 profiling 结果后制作。 |
| 演示视频 | 未开始 | 应展示仓库结构、复现流程、W7900 运行/profiling 证据和结果摘要。 |
| 工程代码仓库 | 进行中，主体基本完成 | 当前分支：`rocm-w7900-gfx1100`。 |
| Docker image / container package | 已有骨架 | 严格 final image 仍属于后续打包工作。 |
| 示例输入与期望输出 | 基本具备 | 已有 validation case list 和提交后的 CSV/Markdown summary。 |

## 最终注意事项

- 不要把当前 W7900 non-hard23 称为未优化 baseline。
- 不要把 hard3 混入 primary non-hard23 baseline。
- 不要提交 raw `.mps` 数据或 raw profiler trace directory。
- 在 `rocprof` 结果出来前，不要声称已经优化了 W7900-specific bottleneck。
- 英文和中文文档保持同步。

<!-- W7900_LATEST_EXPERIMENTS_20260616_BEGIN -->
## W7900 实验完成情况 / 2026-06-16

| 项目 | 状态 | 证据 |
|---|---|---|
| rocprof starter3 | 已完成 | [W7900 rocprof starter3 摘要](../validation/w7900_rocprof_starter3_summary_20260616.zh-CN.md) |
| hard3 probe2 | 已完成 | [W7900 hard3 probe2 600s 摘要](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md) |
| true before/current fast-core6 | 已完成 | [W7900 before/current fast-core6 摘要](../validation/w7900_before_current_core6_fast_summary_20260616.zh-CN.md) |
| 8-card independent-MPS batch throughput | 已完成 | [W7900 8-card fast8 batch 摘要](../validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md) |
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
