# W7900 当前状态

> English: [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md)

本文是 Radeon PRO W7900 / `gfx1100` 的权威当前状态页。日期化实验过程保留在 `validation/`，本页只维护已验证结论、解释边界和主要证据入口。

## 当前结论

- W7900 ROCm/HIP build、smoke、Netlib 和 large-MPS 验证已经完成当前阶段闭环。
- large-MPS 主结果使用 `non-hard23`：23/23 `OPTIMAL`；hard3 单独报告。
- P10 targeted profiling 确认 rocSPARSE CSR SpMV 是主要 GPU kernel 热点。
- P11 接受可运行时选择的 SpMV 策略，并将 `HIPSPARSE_SPMV_CSR_ALG1` 设为当前默认。
- 旧策略可以通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 恢复。
- P12 的 buffer-algorithm consistency patch 因改变迭代轨迹而被拒绝。
- P14-A1 repeated validation 在 quick6 上得到 6/6 current wins，并保持 pre/current 迭代数一致。

当前分支不是“未优化 first port”。正确口径是：

| 角色 | 版本 | 含义 |
|---|---|---|
| Pre-tuning anchor | `ae3b683` / `pre_tuning` | 首个可运行 ROCm 锚点 |
| Current engineering baseline | 当前 `rocm-w7900-gfx1100` | 继承 890M 调优后的 W7900 工程版本 |
| Accepted W7900 endpoint | P11 policy | 默认 `CSR_ALG1`，保留 `csr_alg2` 回退 |
| Rejected experiment | P12 | 未进入当前分支行为的负向实验 |

## Large-MPS non-hard23

| Metric | Value |
|---|---:|
| Cases | 23 |
| Termination | 23/23 `OPTIMAL` |
| W7900 total wall time | 2960.171 s |
| W7900 total solve time | 2742.940 s |
| Source groups | `initial17_safe` 17；`near_optimal2_1800s` 2；`watchlist6_900s` 4 |

主要证据：

- [non-hard23 中文汇总](../validation/w7900_large_mps_nonhard23_20260613.zh-CN.md)
- [solver CSV](../validation/w7900_large_mps_nonhard23_20260613.csv)
- [runtime CSV](../validation/w7900_large_mps_nonhard23_20260613_runtime.csv)

![W7900 non-hard23 wall comparison](assets/w7900/w7900_nonhard23_wall_compare.svg)

![W7900 non-hard23 solve comparison](assets/w7900/w7900_nonhard23_solve_compare.svg)

## 同 23 个 case 的跨设备参考

| Device | Backend | Wall time sum | Solve time sum |
|---|---|---:|---:|
| H100 | CUDA | 1701.350 s | 1433.577 s |
| RTX 3090 | CUDA | 1898.370 s | 1513.214 s |
| RTX 4090D | CUDA | 2730.760 s | 1329.789 s |
| W7900 | ROCm/HIP | 2960.171 s | 2742.940 s |
| Radeon 890M | ROCm/HIP | 5015.740 s | 4842.987 s |

正确解释是：

- W7900 相比 890M 有明显提升；
- W7900 在部分 case 上具有 per-case 竞争力；
- aggregate solve time 仍落后于本项目中的高端 CUDA 参考；
- 结论不能只根据硬件峰值或单个 case 推广。

完整 case 分类见 [W7900 性能行为分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)。

## P10–P12 profiling 与 tuning 证据链

### P10：targeted profiling

5 个代表 case 的 compact profiling 表明：

- rocSPARSE CSR SpMV 是多个 case 的主要 GPU kernel 热点；
- `hipMemcpy`、`hipMemcpyAsync` 和 `hipLaunchKernel` 在较长 case 中也占有明显成本；
- 后续优化应优先考虑 SpMV 策略、launch 数量和窄范围 copy reduction；
- 不应在没有验证的情况下改变 residual、restart、termination、scaling 或浮点更新顺序。

证据：[P10 中文汇总](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md)。

### P11：接受的 SpMV tuning

P11 先建立 runtime 调用点清单和候选优先级，再实现 opt-in SpMV algorithm switch、smoke 和五 case sweep。最终接受：

```text
default: HIPSPARSE_SPMV_CSR_ALG1
fallback: CUPDLP_HIP_SPMV_ALG=csr_alg2
```

证据：

- [P11 tuning 总结](../validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md)
- [algorithm sweep](../validation/w7900_p11_spmv_alg_sweep_20260617_summary.zh-CN.md)
- [default ALG1 smoke](../validation/w7900_p11_default_spmv_alg1_smoke_20260617_summary.zh-CN.md)

### P12：被拒绝的执行层修改

P12 尝试让 `hipsparseSpMV_bufferSize()` 与执行阶段使用同一选择算法。该修改使 `set-cover-model` 的迭代数由 7480 变为 7600，因此没有进入接受终点。

这说明“只改执行层”并不等于“数值行为一定不变”。证据：[P12 negative finding](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md)。

## P14-A1 repeated validation

quick6 repeated validation 对比 `ae3b683 / pre_tuning` 与当前分支：

| Metric | Result |
|---|---:|
| Cases | 6 |
| Current wins | 6/6 |
| Geometric-mean speedup | 1.18889 |
| Median speedup | 1.19502 |
| Iteration-count consistency | pre/current 一致 |

证据：

- [P14-A1 中文汇总](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md)
- [comparison CSV](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv)
- [aggregated CSV](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_aggregated.csv)

## hard3 与 8 卡实验边界

hard3：

```text
dlr1.mps
Dual2_5000.mps
fhnw-binschedule1.mps
```

它们单独用于困难 case 诊断，不混入 non-hard23 主结果。见 [hard3 说明](W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md) 和 [probe2 汇总](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md)。

8 卡 fast8 的 146 s 对比单卡顺序 558 s，表示 8 个独立 MPS 作业的并发吞吐。它不是把一个 LP 分解到 8 张 GPU。见 [8-card fast8 汇总](../validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md)。

## 已知限制

- 当前实现和 tuning 结论主要针对 `gfx1100`，并继承部分 `gfx1150` 经验。
- 自定义 kernel 的参数和 reduction 假设尚未构成广泛 AMD 架构认证。
- aggregate 性能仍受迭代次数、收敛路径和 host/device overhead 共同影响。
- 当前没有单问题分布式多 GPU 求解能力。
- Docker 只是环境骨架，W7900 已提交数字来自实际主机运行。
- 任何新的优化都必须同时检查 termination、feasibility、gap、迭代数和重复运行性能。

## 继续阅读

- [可复现性指南](REPRODUCIBILITY.zh-CN.md)
- [Validation 索引](../validation/README.zh-CN.md)
- [ROCm profiling 记录](ROCM_PROFILING_NOTES.zh-CN.md)
- [ROCm tuning 历史](ROCM_TUNING_HISTORY.zh-CN.md)
- [W7900 性能行为分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)
- [优化基线说明](W7900_OPTIMIZATION_BASELINES.zh-CN.md)
