# 竞赛评审入口：基于 Radeon GPU 的 ROCm 大规模线性规划求解器迁移与性能分析

> English: [COMPETITION_README.md](COMPETITION_README.md)

本文把通用开源仓库中的代码、验证和性能证据映射到竞赛评审需求。它不替代 [项目中文主页](../README.md)，也不把项目定义为只服务一次竞赛的软件。

## 项目问题

cuPDLP-C 是面向大规模线性规划的 PDLP/PDHG 求解器实现。核心迭代反复执行稀疏矩阵向量乘、向量更新、投影、归约和收敛判断。项目解决的问题是：

> 如何把以 CUDA 为主要 GPU 路径的科学计算求解器迁移到 AMD ROCm/HIP，并用可复现证据证明它能构建、能求解、数值行为可接受，而且性能优化没有破坏收敛可靠性。

## 项目贡献

| 方向 | 具体贡献 | 主要证据 |
|---|---|---|
| ROCm/HIP 迁移 | 新增 AMD 后端，保留 CPU/CUDA 路径 | [迁移案例](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md)、[后端模式](BACKEND_MODES_AND_NAMING.zh-CN.md) |
| 正确性验证 | smoke、Netlib、large-MPS、CPU-vs-ROCm 比较 | [Validation 索引](../validation/README.zh-CN.md) |
| 跨设备分析 | 890M、W7900、RTX 3090、RTX 4090D、H100 | [跨设备 benchmark](CROSS_DEVICE_BENCHMARKS.zh-CN.md) |
| 性能剖析 | P10 targeted rocprof，定位 CSR SpMV 和 runtime overhead | [P10 summary](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md) |
| 安全调优 | P11 接受 `CSR_ALG1` 默认并保留回退 | [P11 summary](../validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md) |
| 负向实验 | P12 因迭代数变化拒绝 patch | [P12 negative result](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md) |
| 重复验证 | P14-A1 quick6 current 6/6 胜出 | [P14-A1 summary](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md) |
| 可复现性 | 环境恢复、数据校验、期望输出和运行策略 | [可复现性指南](REPRODUCIBILITY.zh-CN.md) |

## 当前 W7900 结果

| Metric | Result |
|---|---:|
| large-MPS non-hard23 | 23 cases |
| Termination | 23/23 `OPTIMAL` |
| Total wall time | 2960.171 s |
| Total solve time | 2742.940 s |
| P14-A1 current wins | 6/6 |
| P14-A1 geomean speedup | 1.18889 |
| Current SpMV default | `HIPSPARSE_SPMV_CSR_ALG1` |

当前 W7900 结果是继承 890M 调优后的工程基线，不是未优化 first-port baseline：

| 角色 | 版本 |
|---|---|
| Before | `ae3b683` / `pre_tuning` |
| Current | 当前 `rocm-w7900-gfx1100` |
| Accepted endpoint | P11 `CSR_ALG1` policy |
| Rejected change | P12 buffer-algorithm consistency patch |

完整口径见 [W7900 当前状态](W7900_CURRENT_STATUS.zh-CN.md)。

## 性能解释

性能不能只用 GPU 峰值或 aggregate time 解释：

```text
total time ≈ per-iteration cost × number of iterations
```

W7900 在规模足够大、SpMV/向量操作占主导且收敛稳定的 case 上更容易发挥显存带宽和容量优势；在 `s100`、`Primal2_1000` 等 case 上，总时间更多受到迭代数和 gap trajectory 影响。

本项目的严谨性体现在：

- 报告 W7900 相比 890M 的提升；
- 不隐藏 aggregate 仍落后于高端 CUDA 参考的事实；
- hard3 单独报告；
- 保留 P12 被拒绝实验；
- 明确 8 卡结果是独立作业吞吐，不是单问题多 GPU。

## 评审阅读顺序

1. [项目架构图](assets/competition/project_architecture.svg)
2. [证据地图](assets/competition/evidence_map.svg)
3. [W7900 当前状态](W7900_CURRENT_STATUS.zh-CN.md)
4. [CUDA-to-ROCm 迁移案例](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md)
5. [P10 profiling](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md)
6. [P11 tuning](../validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md)
7. [P12 negative result](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md)
8. [P14-A1 repeats](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md)
9. [可复现性指南](REPRODUCIBILITY.zh-CN.md)
10. [评分项对照](COMPETITION_SCORECARD.zh-CN.md)

## 贡献边界

本项目可以主张：

- 完成真实求解器的 CUDA-to-ROCm/HIP 迁移；
- 建立三后端工程边界；
- 完成 W7900 build、验证、profiling、tuning 和 repeated validation；
- 提供正向与负向实验形成的安全调优方法；
- 给出跨设备和 per-case 性能分析。

本项目不应主张：

- 提出了新的 PDLP 算法；
- W7900 在所有 case 上超过 CUDA；
- 8 卡实验实现了单个 LP 的分布式求解；
- 当前 Docker 骨架完全复现所有性能数字；
- 已对所有 AMD GPU 架构完成认证。

## 提交材料

仓库内工程材料和证据索引已经具备。论文、PPT、视频等外部提交物由项目维护者在提交时更新状态，见 [提交清单](SUBMISSION_CHECKLIST.zh-CN.md)。

原始 `.mps` 和 raw profiler traces 不进入 Git；提交的是可审阅的脚本、case lists、curated CSV、Markdown summaries 和 SVG。
