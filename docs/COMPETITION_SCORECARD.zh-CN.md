# 竞赛评分项与仓库最终证据对照

> English: [COMPETITION_SCORECARD.md](COMPETITION_SCORECARD.md)

| 评审方向 | 仓库证据 | 最终状态与边界 |
|---|---|---|
| 项目背景与挑战 | [竞赛入口](COMPETITION_README.zh-CN.md)、[迁移案例](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) | 真实科学计算迁移，不是新算法 |
| 方案与架构 | HIP backend、[后端模式](BACKEND_MODES_AND_NAMING.zh-CN.md) | CPU/CUDA/ROCm 边界清楚 |
| ROCm 组件 | HIP、hipBLAS、hipSPARSE、rocprofv3 | W7900 实机证据 |
| 正确性与数值验证 | [验证说明](VALIDATION.zh-CN.md)、[最终结果](W7900_FINAL_RESULTS_20260729.zh-CN.md) | 76/76 正式运行验证通过 |
| 基线与吞吐 | [最终 compact evidence](../validation/final_w7900_20260729/README.zh-CN.md) | 单卡顺序吞吐均值 28.061611 cases/hour |
| 精度敏感性 | precision CSV 与图 | 30/30；五例三档双重复 |
| 资源指标 | resource CSV 与精度—资源图 | VRAM、利用率、功耗等有采样 |
| Profiling | P10 compact + final profile summary | 具体热点以 P10 为准；最终 5/5 trace PASS |
| 安全调优 | P11、P12、P14-A1 | 接受、拒绝、重复验证均保留 |
| 工作负载画像 | [性能行为](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md) | 区分迭代主导与初始化主导 |
| 静态结构分析 | 23/23 static features | 相关为探索性，不写成因果 |
| 多 GPU | fast8 历史证据 | 仅独立任务吞吐 |
| 可复现性 | [最终复现指南](FINAL_REPRODUCTION_GUIDE.zh-CN.md) | 普通主机可检查与重画；硬件重跑需 W7900 |
| 工程交付 | README、文档地图、checksums、验证脚本 | 最终发布包完整 |

## 最终关键数字

| 结论 | 数值 |
|---|---:|
| 正式 solver 记录 | 76/76 |
| nonhard23 | 23 × 2 = 46 |
| precision | 5 × 3 × 2 = 30 |
| profile | 5/5 |
| 单卡顺序吞吐均值 | 28.061611 cases/hour |
| 总时间 CV 中位数 | 0.377% |
| Top-3 总时间占比 | 82.22% |
| 最大实际误差/目标精度 | 0.998079 |

## 必须保持的解释规则

1. 正式 harness 与冻结 solver 角色不同，不能混写。
2. 吞吐表示独立 MPS，不是单个 LP 多 GPU。
3. hard3 单独报告。
4. P12 负向证据不能删除。
5. precision 结论只覆盖五例。
6. 静态相关不能写成因果或条件数结论。
7. Docker 不是正式性能数字来源。
