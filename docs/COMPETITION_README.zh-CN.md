# 竞赛入口文档：基于 Radeon GPU 的 ROCm 大规模线性规划求解器迁移与性能分析

> English: [COMPETITION_README.md](COMPETITION_README.md)

本文是 AMD ROCm / Radeon 赛题方向的评委入口文档。

## 项目题目

**基于 AMD ROCm 与 Radeon GPU 的大规模线性规划求解器迁移、验证与性能分析**

## 项目背景与挑战

大规模线性规划是典型科研计算和运筹优化工作负载。cuPDLP/PDLP 类求解器反复使用稀疏矩阵向量乘、向量更新、归约和数值收敛判断。上游项目主要面向 CUDA，因此本项目的挑战是将求解器迁移到 AMD ROCm/HIP，同时保持正确性、可复现性和跨设备可比较性。

## 目标平台

| 平台 | 作用 |
|---|---|
| Radeon 890M / `gfx1150` | ROCm/HIP 首轮迁移、调优历史和 baseline 验证 |
| Radeon PRO W7900 / `gfx1100` | large-MPS 工作站 GPU 验证和后续 W7900-specific profiling/tuning |
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
| After | future W7900-specific tuning branch | 最终 W7900-specific optimized result |

## 性能解释

项目同时使用 aggregate 和 per-case 分析。aggregate time 有价值，但 W7900 的竞争力在 per-case 层面更清楚。核心解释是：

```text
total time ≈ per-iteration cost × number of iterations
```

W7900 更适合规模足够大、带宽敏感、SpMV/向量操作占比较高且收敛稳定的 case。`s100`、`Primal2_1000` 等慢 case 应结合迭代次数、gap trajectory 和 kernel performance 一起解释。

## 下一步计划

1. 在 `set-cover-model`、`square41`、`s100` 上运行 W7900 `rocprofv3` starter3 profiling。
2. 记录 wall time、solver time、`DeviceMatVecProdTime`、`nIter`、HIP/kernel trace 和 GPU telemetry。
3. 对 `dlr1`、`fhnw-binschedule1` 运行 hard3 short probes。
4. 使用 `ae3b683` vs current 跑 core6 true before/current comparison。
5. profiling 结果定位瓶颈后再做 W7900-specific tuning。

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
| 演示说明 PPT | 第一轮 profiling 结果完成后制作 |
| 演示视频 | 展示 build、validation、charts 和 profiling workflow |
| 工程代码仓库 | 当前仓库已有 scripts、validation CSV、Markdown summaries、SVG charts |
| 可复现性 | 已在 [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md) 中说明；覆盖环境恢复、数据校验、期望输出和 starter profiling |
