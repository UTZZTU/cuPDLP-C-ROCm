from pathlib import Path

Path("scripts/docs").mkdir(parents=True, exist_ok=True)

en = """# Submission checklist

> 中文: [SUBMISSION_CHECKLIST.zh-CN.md](SUBMISSION_CHECKLIST.zh-CN.md)

This checklist tracks contest-facing deliverables without turning the repository into a contest-only project. The repository remains a general ROCm/HIP migration, validation, and benchmarking project.

## Repository delivery

| Item | Status | Evidence / next step |
|---|---|---|
| General project README | Done | [../README.md](../README.md), [../README.zh-CN.md](../README.zh-CN.md) |
| Documentation map | Done | [README.md](README.md) |
| Competition reviewer path | Done | [COMPETITION_README.md](COMPETITION_README.md), [COMPETITION_SCORECARD.md](COMPETITION_SCORECARD.md) |
| Reproducibility guide | Done | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| W7900 current status | Done | [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md) |
| W7900 performance interpretation | Done | [W7900_PERFORMANCE_BEHAVIOR.md](W7900_PERFORMANCE_BEHAVIOR.md) |
| W7900 optimization-baseline policy | Done | [W7900_OPTIMIZATION_BASELINES.md](W7900_OPTIMIZATION_BASELINES.md) |
| Docker/container skeleton | Done as skeleton | [../docker/Dockerfile.w7900](../docker/Dockerfile.w7900), [../docker/README_DOCKER_W7900.md](../docker/README_DOCKER_W7900.md). This is an environment declaration skeleton, not the source of current W7900 performance numbers. |
| Curated validation summaries | Done for current milestone | See [../validation/README.md](../validation/README.md) |
| Raw MPS data policy | Done | Raw `.mps` files stay outside Git. |

## W7900 experiment items

| Item | Status | Notes |
|---|---|---|
| W7900 smoke validation | Done | Current repository documents completed smoke validation. |
| W7900 Netlib 27-case validation | Done | Current repository documents completed Netlib validation. |
| W7900 non-hard large-MPS baseline | Done | `non-hard23`: 23/23 `OPTIMAL`; hard3 tracked separately. |
| W7900 `rocprof` starter3 | Pending W7900 machine | Cases: `set-cover-model.mps`, `square41.mps`, `s100.mps`. |
| hard3 probe2 | Pending W7900 machine | Cases: `dlr1.mps`, `fhnw-binschedule1.mps`. |
| true before/current core6 | Pending W7900 machine | `ae3b683 / pre_tuning` versus current `rocm-w7900-gfx1100`. |
| W7900-specific tuning | Pending profiling evidence | Do not tune blindly; choose the first target after profiler results. |
| W7900 profiling result summary | Pending W7900 machine | Commit compact CSV/Markdown only, not raw profiler traces. |

## Contest submission materials

| Material | Status | Repository support |
|---|---|---|
| Technical paper | Not started | Use `COMPETITION_README`, `COMPETITION_SCORECARD`, `REPRODUCIBILITY`, W7900 status/performance docs, and future profiling results. |
| Presentation slides | Not started | Build after paper outline and W7900 profiling results. |
| Demo video | Not started | Should show repository structure, reproducibility workflow, W7900 run/profiling evidence if available, and result summaries. |
| Engineering code repository | In progress, mostly ready | Current branch: `rocm-w7900-gfx1100`. |
| Docker image / container package | Skeleton present | Strict final image remains future packaging work. |
| Example inputs and expected outputs | Mostly ready | Validation case lists and committed CSV/Markdown summaries are present. |

## Final cautions

- Do not describe current W7900 non-hard23 as an unoptimized baseline.
- Do not mix hard3 cases into the primary non-hard23 baseline.
- Do not commit raw `.mps` data or raw profiler trace directories.
- Do not claim W7900-specific bottlenecks have been optimized before `rocprof` results exist.
- Keep English and Chinese documents synchronized.
"""

zh = """# 提交清单

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
"""

Path("docs/SUBMISSION_CHECKLIST.md").write_text(en)
Path("docs/SUBMISSION_CHECKLIST.zh-CN.md").write_text(zh)

print("wrote docs/SUBMISSION_CHECKLIST.md")
print("wrote docs/SUBMISSION_CHECKLIST.zh-CN.md")
