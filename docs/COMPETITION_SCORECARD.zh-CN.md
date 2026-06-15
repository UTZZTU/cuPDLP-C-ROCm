# 竞赛评分项对照

> English: [COMPETITION_SCORECARD.md](COMPETITION_SCORECARD.md)

本文把 AMD ROCm/Radeon 赛题要求映射到仓库证据。它是评审视角的检查表，不是项目唯一入口。普通读者应先阅读 [../README.zh-CN.md](../README.zh-CN.md) 和 [README.md](README.md)。

## 范围

项目：在 AMD Radeon 类 GPU 上对大规模线性规划求解器进行 ROCm/HIP 迁移、验证、benchmark 与 profiling。

当前状态：

- Radeon 890M / `gfx1150`：首个 ROCm 迁移、验证与 tuning 历史平台。
- Radeon PRO W7900 / `gfx1100`：工作站级验证平台，已有 current non-hard large-MPS baseline。
- NVIDIA RTX 3090 / RTX 4090D / H100：CUDA 参考设备，用于跨设备对比。

## 评分项对照

| 赛题要求 | 仓库证据 | 当前状态 | 待补工作 |
|---|---|---|---|
| 项目背景与挑战 | [COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md)、[CUDA 到 ROCm 迁移案例](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) | 已说明 CUDA-oriented solver 向 ROCm/HIP 迁移的挑战，以及 LP/HPC 工作负载背景 | 技术论文中需压缩成更清晰的叙事 |
| 方案与实现 | HIP backend、[ROCM_WORKFLOW.zh-CN.md](ROCM_WORKFLOW.zh-CN.md)、[ROCM_PORTING_GUIDE.zh-CN.md](ROCM_PORTING_GUIDE.zh-CN.md)、README 后端模式说明 | 已记录 CPU、CUDA、ROCm 三种后端模式和构建流程 | 论文/PPT 中需要补模块图与 ROCm 组件映射图 |
| ROCm 组件使用 | HIP runtime、hipBLAS/hipSPARSE 构建路径、`rocprofv3`/`rocprof` workflow、ROCm device architecture 选择 | 已具备 ROCm/HIP 构建与 profiling workflow | 下次 W7900 实验后补 profiling 结果表 |
| 性能与资源分析 | [W7900 性能行为分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)、[ROCm tuning 历史](ROCM_TUNING_HISTORY.zh-CN.md)、validation/benchmark CSV | 已提交 W7900 non-hard23 summary 和跨设备参考数据 | 仍需 W7900 `rocprof` starter3、VRAM/telemetry、before/current core6 对比 |
| 复现与交付 | [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md)、validation case lists、scripts、curated CSV/Markdown summaries | 已写 fresh W7900 recovery、数据策略、期望输出和 profiling workflow | Dedicated Docker/Containerfile 仍是 final-submission work item |
| 功能完整性与代码质量 | 源码目录、scripts、validation summaries、backend mode policy | 主要求解路径已按 build/validation 驱动维护 | 只在必要位置补代码注释，避免无意义大改 |
| 阶段性成果与规划 | [W7900 当前状态](W7900_CURRENT_STATUS.zh-CN.md)、[W7900 优化基线](W7900_OPTIMIZATION_BASELINES.zh-CN.md)、[W7900 profiling 计划](W7900_ROCM_PROFILING_PLAN.zh-CN.md) | current/before/after 口径已明确 | 继续跑 W7900 profiling、hard3 probes，再做 W7900-specific tuning |
| 附加分：未支持功能开发 | CUDA-oriented 科学计算求解器的 ROCm/HIP 后端适配 | 已体现非平凡 ROCm 后端迁移 | 暂不声称已有 ROCm 上游 PR |
| 附加分：性能瓶颈定位与优化 | 890M tuning 历史与 W7900 profiling 计划 | 已记录此前 ROCm 优化历史 | W7900-specific bottleneck 结论必须等待 `rocprof` 实测结果 |

## 当前注意事项

当前 W7900 non-hard23 结果是继承 890M tuning 的工程基线，不是真正未优化 first-runnable ROCm baseline。正式 before/current 对比应使用 `ae3b683 / pre_tuning` 与当前 `rocm-w7900-gfx1100`。
