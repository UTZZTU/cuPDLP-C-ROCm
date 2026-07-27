# 提交清单

> English: [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)

本清单区分“仓库内可验证材料”和“仓库外提交物”。外部论文、PPT、视频的实际完成状态由项目维护者在提交时更新，避免仓库长期保存过时的“未开始/进行中”描述。

## 仓库内工程材料

| 条目 | 状态 | 入口 |
|---|---|---|
| 中英文项目主页 | 已具备 | [中文](../README.md), [English](../README.en.md) |
| 文档地图 | 已具备 | [docs/README.md](README.md) |
| W7900 当前状态 | 已具备 | [W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md) |
| 可复现性指南 | 已具备 | [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md) |
| Validation 证据索引 | 已具备 | [validation/README.zh-CN.md](../validation/README.zh-CN.md) |
| 竞赛评审路径 | 已具备 | [COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md) |
| 评分项对照 | 已具备，规则变化时更新 | [COMPETITION_SCORECARD.zh-CN.md](COMPETITION_SCORECARD.zh-CN.md) |
| 架构图与证据地图 | 已具备 | [架构图](assets/competition/project_architecture.svg), [证据地图](assets/competition/evidence_map.svg) |
| Docker/container | 环境骨架 | [Docker 说明](../docker/README_DOCKER_W7900.zh-CN.md) |
| raw 数据策略 | 已明确 | `.mps` 和 raw traces 不进入 Git |

## W7900 证据闭环

| 条目 | 状态 | 证据 |
|---|---|---|
| build 与 smoke | 已完成当前阶段 | [smoke summary](../validation/w7900_smoke_summary_20260611.zh-CN.md) |
| Netlib / 27-case | 已完成 | [27-case baseline](../validation/w7900_27cases_baseline_20260611.zh-CN.md) |
| non-hard23 | 23/23 `OPTIMAL` | [summary](../validation/w7900_large_mps_nonhard23_20260613.zh-CN.md) |
| hard3 | 单独报告 | [notes](W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md) |
| P10 profiling | 已完成 | [summary](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md) |
| P11 tuning | 已接受 `CSR_ALG1` 默认策略 | [summary](../validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md) |
| P12 negative result | 已记录并拒绝 patch | [negative finding](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md) |
| P14-A1 repeats | current 6/6 胜出 | [summary](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md) |
| 8-card fast8 | independent-MPS throughput | [summary](../validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md) |

## 仓库外提交物

在最终提交前由维护者填写，不在本仓库中长期固化状态：

| 材料 | 最终检查 |
|---|---|
| 技术论文 | 题目、贡献边界、实验数字、图表和仓库引用一致 |
| 演示 PPT | 不夸大算法创新，不把 8 卡吞吐写成单问题多 GPU |
| 演示视频 | 展示真实构建/运行或明确使用已提交 evidence inspection |
| 提交表单 | 分支、commit、环境、数据来源和许可证准确 |
| 可选容器 | 明确是环境骨架还是经过验证的完整复现镜像 |

## 最终一致性检查

- [ ] 当前主分支和提交号已记录。
- [ ] 中英文主页与 W7900 状态页结论一致。
- [ ] non-hard23 写为 23/23 `OPTIMAL`，hard3 单独说明。
- [ ] 当前默认写为 `HIPSPARSE_SPMV_CSR_ALG1`，回退为 `CUPDLP_HIP_SPMV_ALG=csr_alg2`。
- [ ] P12 被拒绝实验仍可发现。
- [ ] P14-A1 写为 6/6 current wins，geomean 1.18889，median 1.19502。
- [ ] 8-card 结果明确为 8 个独立 MPS 任务。
- [ ] 不声称提出新的 PDLP 算法。
- [ ] 不声称 W7900 在所有 case 上超过 CUDA。
- [ ] raw MPS、raw traces、build 目录、凭据没有进入提交。
- [ ] `git diff --check` 和 Markdown/link 检查通过。
- [ ] 提交材料引用的仓库链接和文件路径可访问。
