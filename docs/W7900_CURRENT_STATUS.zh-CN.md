# W7900 当前状态

> English: [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md)
> 最终结果：[W7900_FINAL_RESULTS_20260729.zh-CN.md](W7900_FINAL_RESULTS_20260729.zh-CN.md)

本文是 Radeon PRO W7900 / `gfx1100` 的权威当前状态页。日期化历史报告继续
保存在 `validation/`；本页只维护当前结论和边界。

## 最终结论

W7900 正式实验、证据 QC 和离线分析发布已经闭环：

- nonhard23：23 例 × 2 次，46/46 `VALIDATED_OPTIMAL`；
- 目标精度实验：5 例 × 3 档 × 2 次，30/30 `VALIDATED_OPTIMAL`；
- targeted profiling：5/5 `PASS`；
- 静态结构分析：23/23 `PASS`；
- 正式 solver 记录合计：**76/76**；
- 最终标志：
  `FORMAL_W7900_EXPERIMENTS_COMPLETE`、
  `FINAL_ANALYSIS_RELEASED`。

不再需要为当前发布重跑 W7900。只有出现新的、预先定义的研究问题时，才应
重新申请 W7900。

## 正式身份

| 角色 | 值 |
|---|---|
| 正式分支 | `rocm-w7900-gfx1100` |
| 冻结 solver | `735764807d8698ff30811d1a6fcc45d4a3fd4817` |
| 正式 harness | `b5b9a6ffc1a041a48a0e051568d0134a3822556c` |
| Window 1 SHA256 | `d2ce13091072a7c40c2c89bdd988e94c2fca36772da38e0af87de6332e7cd94a` |
| Window 2 SHA256 | `7f8fbcd45591f4dbe0899d18df76329b1f9a17ff433b6dcd3c06d743aaead0db` |

求解器边界 `CMakeLists.txt`、`cmake/`、`cupdlp/`、`interface/` 在正式
harness 中与冻结基线一致。

## 核心数字

| 指标 | 正式结果 |
|---|---:|
| 两轮完整 23 例总时间 | 2950.625997 s / 2950.674611 s |
| 两轮单卡顺序吞吐 | 28.061842 / 28.061379 cases/hour |
| 吞吐均值 | **28.061611 cases/hour** |
| 总时间 CV 中位数 | **0.377%** |
| CV < 2% | **22/23** |
| 两轮迭代数一致 | **23/23** |
| Top-3 总时间占比 | **82.22%** |
| precision 总时间倍率 | **1.01×–4.01×** |
| precision 迭代倍率 | **2.02×–11.58×** |
| 最大实际误差/目标精度 | **0.998079** |

## 工作负载解释

最终数据支持两类主要工作负载：

1. **迭代/计算主导：** `s100`、`Primal2_1000`、`thk_63`、
   `square41` 等；
2. **读取/初始化主导：** `L2CTA3D` 是最清楚的代表，其矩阵规模很大但
   迭代数很少，求解阶段只占总时间小部分。

因此，W7900 上的总时间不能只用 GPU 峰值解释：

```text
总时间 ≈ 读取/初始化/收尾 + 单迭代成本 × 迭代次数
```

完整分析见
[W7900 性能行为](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)。

## Profiling 与调优终点

历史 P10 compact evidence 表明：

- rocSPARSE CSR SpMV 是多个 targeted case 的主要 GPU kernel group；
- `hipMemcpy`、`hipMemcpyAsync` 和 launch 开销也需要关注。

P11 接受：

```text
default: HIPSPARSE_SPMV_CSR_ALG1
fallback: CUPDLP_HIP_SPMV_ALG=csr_alg2
```

P12 的 buffer-algorithm consistency 修改改变了 `set-cover-model` 的
迭代轨迹，因此被拒绝。P14-A1 随后确认 quick6 上 current 6/6 胜出且迭代
数一致。

最终 session2 再次完成五例 profile 采集与 trace 验证，但 raw trace 不进入
Git，也不从 trace 文件数量推导新的热点比例。

## 历史结果的角色

以下证据继续保留，但不取代最终正式发布：

- 2026-06-13 单轮 non-hard23；
- P10 profiling；
- P11 accepted tuning；
- P12 negative experiment；
- P14-A1 repeated before/current；
- 8-card fast8 independent-task throughput；
- hard3 diagnostics。

## 当前边界

- 当前项目没有单问题分布式多 GPU 求解能力。
- 8 卡结果只表示独立任务吞吐。
- precision 结果只覆盖五例。
- 静态相关为探索性，不证明因果。
- hard3 不混入 nonhard23。
- Docker 是环境骨架，不是正式性能数字来源。
- 当前主要验证保持 presolve 关闭；nontrivial postsolve 与原变量恢复未纳入
  正式合同。
- 本项目不声称提出新的 PDLP 算法或认证所有 AMD GPU。

## 继续阅读

- [最终结果](W7900_FINAL_RESULTS_20260729.zh-CN.md)
- [最终复现指南](FINAL_REPRODUCTION_GUIDE.zh-CN.md)
- [Profiling 记录](ROCM_PROFILING_NOTES.zh-CN.md)
- [Validation 索引](../validation/README.zh-CN.md)
- [最终 compact evidence](../validation/final_w7900_20260729/README.zh-CN.md)
