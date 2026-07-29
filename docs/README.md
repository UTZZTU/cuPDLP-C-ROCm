# Documentation map / 文档地图

This is the central navigation page for maintained project documentation.
本页是项目维护文档的唯一总导航。

## Start here / 推荐入口

| Reader / 读者 | Entry / 入口 | Goal / 目标 |
|---|---|---|
| General reader / 普通读者 | [English homepage](../README.en.md) / [中文主页](../README.md) | Scope, contribution, final results, limitations |
| Final-result reviewer / 最终结果审阅 | [Final results](W7900_FINAL_RESULTS_20260729.md) / [最终结果](W7900_FINAL_RESULTS_20260729.zh-CN.md) | Formal 46+30 runs, resources, profiles, figures |
| Reproducer / 复现者 | [Final reproduction](FINAL_REPRODUCTION_GUIDE.md) / [最终复现指南](FINAL_REPRODUCTION_GUIDE.zh-CN.md) | Inspect evidence, rebuild, rerun, regenerate figures |
| Validation reader / 验证读者 | [Validation](VALIDATION.md) / [验证说明](VALIDATION.zh-CN.md) | PASS semantics, formal evidence boundaries |
| Performance reader / 性能读者 | [Performance behavior](W7900_PERFORMANCE_BEHAVIOR.md) / [性能行为](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md) | Workload profile and tolerance behavior |
| Contest reviewer / 竞赛评委 | [Competition entry](COMPETITION_README.md) / [竞赛入口](COMPETITION_README.zh-CN.md) | Evidence mapped to review requirements |

## Authoritative current documents / 当前权威文档

| Topic / 主题 | English | 中文 |
|---|---|---|
| Repository overview / 项目总览 | [README](../README.en.md) | [README](../README.md) |
| Final formal results / 最终正式结果 | [Final results](W7900_FINAL_RESULTS_20260729.md) | [最终结果](W7900_FINAL_RESULTS_20260729.zh-CN.md) |
| Current W7900 status / 当前状态 | [Status](W7900_CURRENT_STATUS.md) | [状态](W7900_CURRENT_STATUS.zh-CN.md) |
| Final reproduction / 最终复现 | [Guide](FINAL_REPRODUCTION_GUIDE.md) | [指南](FINAL_REPRODUCTION_GUIDE.zh-CN.md) |
| Validation semantics / 验证语义 | [Validation](VALIDATION.md) | [验证](VALIDATION.zh-CN.md) |
| Performance interpretation / 性能解释 | [Analysis](W7900_PERFORMANCE_BEHAVIOR.md) | [分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md) |
| Profiling / 性能剖析 | [Notes](ROCM_PROFILING_NOTES.md) | [记录](ROCM_PROFILING_NOTES.zh-CN.md) |
| Tuning history / 调优历史 | [History](ROCM_TUNING_HISTORY.md) | [历史](ROCM_TUNING_HISTORY.zh-CN.md) |
| Backend boundaries / 后端边界 | [Modes](BACKEND_MODES_AND_NAMING.md) | [模式](BACKEND_MODES_AND_NAMING.zh-CN.md) |
| CUDA-to-ROCm migration / 迁移案例 | [Case study](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) | [案例](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) |

## Final compact evidence / 最终 compact 证据

- [English index](../validation/final_w7900_20260729/README.md)
- [中文索引](../validation/final_w7900_20260729/README.zh-CN.md)
- [Validation index](../validation/README.md)
- [验证索引](../validation/README.zh-CN.md)
- [Final exact figures](assets/w7900/final20260729/)

## Competition-facing documents / 竞赛材料

| Document / 文档 | English | 中文 |
|---|---|---|
| Reviewer entry / 评审入口 | [Entry](COMPETITION_README.md) | [入口](COMPETITION_README.zh-CN.md) |
| Score mapping / 评分映射 | [Scorecard](COMPETITION_SCORECARD.md) | [评分对照](COMPETITION_SCORECARD.zh-CN.md) |
| Submission checklist / 提交清单 | [Checklist](SUBMISSION_CHECKLIST.md) | [清单](SUBMISSION_CHECKLIST.zh-CN.md) |
| Video guide / 视频指南 | — | [指南](VIDEO_DEMO_GUIDE.zh-CN.md) |

## Historical documents / 历史文档

Historical and dated files remain immutable evidence, not current-status entry
points. 历史计划和日期化报告保留决策与实验上下文，不再承担当前结论。

| Historical area / 历史区域 | Current replacement / 当前入口 |
|---|---|
| `README_ROCM_gfx1150*` | Root README |
| `W7900_FIRST_PORT*` | `W7900_CURRENT_STATUS*` |
| `W7900_ROCM_PROFILING_PLAN*` | `ROCM_PROFILING_NOTES*` |
| `W7900_FINAL_SPRINT_RUNBOOK.zh-CN.md` | Completed runbook; use final results and reproduction guide |
| Dated `validation/` files | Validation indexes and final compact package |

## Maintenance rules / 维护规则

1. Current claims belong in the root READMEs, final-results pages, current-status
   pages, and indexes.
2. Dated reports are immutable evidence.
3. English and Chinese current documents must be updated together.
4. Raw MPS, raw profiler traces, local builds, and credentials stay outside Git.
5. Competition documents map general project evidence; they do not redefine the
   repository as contest-only software.
6. New performance claims require a compact data file, identity/checksum record,
   and explicit scope.
