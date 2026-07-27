# Documentation map / 文档地图

This is the central navigation page for maintained project documentation.
本页是项目维护文档的唯一总导航，区分当前结论、使用说明、证据索引和历史里程碑。

## Recommended reading paths / 推荐阅读路径

| Reader / 读者 | Start here / 建议入口 | Goal / 目标 |
|---|---|---|
| General GitHub reader / 普通读者 | [English homepage](../README.en.md) / [中文主页](../README.md) | Understand scope, contributions, results, and limitations |
| User reproducing the project / 复现项目 | [Reproducibility](REPRODUCIBILITY.md) / [可复现性](REPRODUCIBILITY.zh-CN.md) | Inspect committed evidence or rerun W7900 workflows |
| ROCm migration developer / ROCm 迁移开发者 | [ROCm porting guide](ROCM_PORTING_GUIDE.md), [migration case study](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) | Understand backend boundaries and porting decisions |
| Validation reader / 验证读者 | [validation index](../validation/README.md) / [验证索引](../validation/README.zh-CN.md) | Locate case lists, curated CSV, summaries, and expected interpretation |
| Performance researcher / 性能研究者 | [W7900 current status](W7900_CURRENT_STATUS.md), [profiling notes](ROCM_PROFILING_NOTES.md), [tuning history](ROCM_TUNING_HISTORY.md) | Follow profiling, accepted tuning, negative results, and convergence effects |
| Contest reviewer / 竞赛评委 | [Competition entry](COMPETITION_README.md) / [竞赛入口](COMPETITION_README.zh-CN.md) | Read the general repository evidence through contest requirements |

## Core project documents / 核心项目文档

| Topic / 主题 | English | 中文 | Role / 作用 |
|---|---|---|---|
| Repository overview / 项目总览 | [README](../README.en.md) | [README](../README.md) | Authoritative current homepage |
| Build and run / 构建运行 | [ROCm workflow](ROCM_WORKFLOW.md) | [ROCm 工作流](ROCM_WORKFLOW.zh-CN.md) | Daily build and execution workflow |
| Reproducibility / 可复现性 | [Guide](REPRODUCIBILITY.md) | [指南](REPRODUCIBILITY.zh-CN.md) | Evidence inspection and rerun instructions |
| Validation semantics / 验证语义 | [Validation](VALIDATION.md) | [验证说明](VALIDATION.zh-CN.md) | PASS/FAIL/INCOMPLETE comparison rules |
| Backend architecture / 后端架构 | [Backend modes](BACKEND_MODES_AND_NAMING.md) | [后端模式](BACKEND_MODES_AND_NAMING.zh-CN.md) | CPU/CUDA/ROCm boundaries and naming |
| Porting / 移植 | [ROCm porting guide](ROCM_PORTING_GUIDE.md) | [ROCm 移植指南](ROCM_PORTING_GUIDE.zh-CN.md) | Practical HIP migration guidance |
| Migration case study / 迁移案例 | [Case study](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) | [案例](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) | End-to-end engineering narrative |

## Current results and analysis / 当前结果与分析

| Topic / 主题 | English | 中文 | Source evidence / 证据 |
|---|---|---|---|
| W7900 current status / 当前状态 | [Status](W7900_CURRENT_STATUS.md) | [状态](W7900_CURRENT_STATUS.zh-CN.md) | non-hard23, P10–P12, P14-A1, limitations |
| Performance behavior / 性能行为 | [Analysis](W7900_PERFORMANCE_BEHAVIOR.md) | [分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md) | Per-case and convergence interpretation |
| Profiling / 性能剖析 | [Notes](ROCM_PROFILING_NOTES.md) | [记录](ROCM_PROFILING_NOTES.zh-CN.md) | Profiling workflow and hotspot findings |
| Tuning history / 调优历史 | [History](ROCM_TUNING_HISTORY.md) | [历史](ROCM_TUNING_HISTORY.zh-CN.md) | Accepted changes and validation gates |
| Tuning guidance / 调优指南 | [Guide](TUNING_GUIDE_ROCM.md) | [指南](TUNING_GUIDE_ROCM.zh-CN.md) | Safe optimization methodology |
| Cross-device results / 跨设备结果 | [Benchmarks](CROSS_DEVICE_BENCHMARKS.md) | [Benchmark](CROSS_DEVICE_BENCHMARKS.zh-CN.md) | CPU/CUDA/ROCm references |
| Numerical behavior / 数值行为 | [greenbea note](NUMERICAL_BEHAVIOR_GREENBEA.md) | [greenbea 说明](NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md) | Case-specific convergence behavior |

## Evidence indexes / 证据索引

| Evidence area / 证据区域 | Entry / 入口 |
|---|---|
| Validation case lists, CSV, and summaries | [validation/README.md](../validation/README.md) / [validation/README.zh-CN.md](../validation/README.zh-CN.md) |
| Benchmark reports and curated CSV | [benchmarks/README.md](benchmarks/README.md) |
| W7900 figures | [`assets/w7900/`](assets/w7900/) |
| Competition architecture and evidence maps | [`assets/competition/`](assets/competition/) |
| Upstream project snapshot | [README_UPSTREAM.md](../README_UPSTREAM.md) |

## Competition-facing documents / 竞赛材料

| Document / 文档 | English | 中文 | Maintenance status / 维护状态 |
|---|---|---|---|
| Reviewer entry / 评审入口 | [COMPETITION_README](COMPETITION_README.md) | [竞赛入口](COMPETITION_README.zh-CN.md) | Current |
| Score mapping / 评分项映射 | [Scorecard](COMPETITION_SCORECARD.md) | [评分对照](COMPETITION_SCORECARD.zh-CN.md) | Update when rules change |
| Submission checklist / 提交清单 | [Checklist](SUBMISSION_CHECKLIST.md) | [清单](SUBMISSION_CHECKLIST.zh-CN.md) | Repository readiness; external artifacts are owner-managed |
| Video guide / 视频指南 | — | [视频演示指南](VIDEO_DEMO_GUIDE.zh-CN.md) | Optional submission support |

## Historical and milestone documents / 历史与里程碑文档

These files remain in place because they preserve decisions and experimental context, but they are not current-status entry points.
这些文件用于保留决策和实验上下文，不应作为当前状态入口。

| Document / 文档 | Status / 状态 | Current replacement / 当前入口 |
|---|---|---|
| `README_ROCM_gfx1150*` | Earlier Radeon 890M / `gfx1150` milestone | [Current homepage](../README.en.md) / [中文主页](../README.md) |
| `W7900_FIRST_PORT*` | First-port snapshot | [W7900 current status](W7900_CURRENT_STATUS.md) |
| `platforms/W7900_PLATFORM_NOTES.md` | Historical machine-specific environment record | [Current reproducibility](REPRODUCIBILITY.md) |
| `W7900_ROCM_PROFILING_PLAN*` | Completed profiling plan | [Profiling notes](ROCM_PROFILING_NOTES.md), P10/P11/P12 in validation index |
| `LARGE_MPS_BENCHMARK_PLAN*` | Original benchmark plan | [Benchmark index](benchmarks/README.md), [validation index](../validation/README.md) |
| Dated files under `validation/` | Immutable experiment evidence | [Validation index](../validation/README.md) |

## Documentation maintenance rules / 文档维护规则

1. Current claims belong in the two root homepages, `W7900_CURRENT_STATUS*`, and index pages.
   当前结论只在根目录中英文主页、`W7900_CURRENT_STATUS*` 和索引页维护。
2. Dated experiment reports are evidence records; do not append new “final status” sections to them.
   日期化实验报告是证据记录，不再追加新的“最终状态”。
3. New experiments should add a compact CSV/Markdown pair, then update the relevant index and current-status page.
   新实验提交 compact CSV/Markdown 后，只更新相应索引和当前状态页。
4. English and Chinese current documents must be updated together.
   当前态中英文文档必须同步修改。
5. Raw MPS files, raw profiler traces, local builds, and credentials stay outside Git.
   原始 MPS、原始 profiler trace、本地构建和凭据不进入 Git。
6. Competition documents map general project evidence; they must not redefine the project as contest-only software.
   竞赛文档只映射通用项目证据，不把项目改写成一次性竞赛软件。
