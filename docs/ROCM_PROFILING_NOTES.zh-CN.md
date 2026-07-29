# ROCm profiling 记录与最终结论

> English: [ROCM_PROFILING_NOTES.md](ROCM_PROFILING_NOTES.md)
> 最终结果：[W7900_FINAL_RESULTS_20260729.zh-CN.md](W7900_FINAL_RESULTS_20260729.zh-CN.md)

本文整合项目 profiling 证据。日期化 compact CSV/Markdown 是具体热点的源证据；
raw trace 始终保存在 Git 外。

## Profiling 阶段

| 阶段 | 平台 | 作用 |
|---|---|---|
| 早期结构性 profiling | Radeon 890M / `gfx1150` | 识别同步、launch、copy 和 runtime query 开销 |
| P10 targeted profiling | W7900 / `gfx1100` | 对五个代表 large-MPS case 定位 kernel/API 热点 |
| 最终 session2 profile gate | W7900 / `gfx1100` | 验证五例正式 trace 采集与归档完整性 |

P10 负责具体热点解释；最终 session2 负责正式身份、采集和 trace 完整性验证。
两者不能混成同一种证据。

## P10 targeted cases

```text
thk_48
square41
L2CTA3D
set-cover-model
tpl-tub-ws1617
```

源文件：

- [P10 summary](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md)
- [runtime](../validation/w7900_p10_current_targeted_rocprof_20260617_runtime.csv)
- [kernel top](../validation/w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv)
- [HIP API top](../validation/w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv)
- [memory copy](../validation/w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv)
- [milestone deltas](../validation/w7900_p10_current_targeted_rocprof_20260617_milestone_deltas.csv)

## 具体热点结论

P10 compact evidence 支持：

- rocSPARSE CSR SpMV 是多个代表 case 的主要 GPU kernel group，特别是
  `set-cover-model`、`square41` 和 `thk_48`；
- 长运行实例的 HIP API 时间中，`hipMemcpy` 较突出；
- `hipMemcpyAsync` 和 `hipLaunchKernel` 也是应关注的 runtime 开销；
- 具体优化方向应围绕 SpMV 策略、launch 数量和窄范围 copy reduction；
- 不应在没有数值验证的情况下改 residual、restart、termination、scaling 或
  浮点更新顺序。

## 从 profiling 到安全调优

### P11：接受

P11 对 hipSPARSE 提供的 CSR SpMV algorithm 做受控 sweep，最终接受：

```text
default: HIPSPARSE_SPMV_CSR_ALG1
fallback: CUPDLP_HIP_SPMV_ALG=csr_alg2
```

### P12：拒绝

buffer-algorithm consistency 修改使 `set-cover-model` 的迭代数从 7480
变为 7600，因此未进入当前分支。

### P14-A1：重复确认

quick6 repeated current-vs-pre-tuning 中 current 6/6 胜出，且前后迭代数一致。

这条链说明：profiling 只负责提出测量问题；接受优化必须同时检查 termination、
feasibility、gap、迭代数和重复运行。

## 最终 session2 profile gate

最终正式 Window 2 中，五个代表 case 全部满足：

```text
runtime_status = DONE
exit_code = 0
profile_validation_status = PASS
trace_csv_count = 5
kernel_trace_count = 1
```

对应 compact 表：
[profile_summary.csv](../validation/final_w7900_20260729/profile_summary.csv)。

该 gate 证明：

- 正式分支和冻结 solver 身份下 profile 可运行；
- 每例存在非空 trace CSV 和 kernel trace；
- 五例采集与归档流程完整。

它不单独证明新的 kernel 排名或百分比。最终仓库不会从 trace 文件数量虚构热点，
也不提交 raw trace。

## 指标联合解释

Solver 层：

| 指标 | 用途 |
|---|---|
| 总时间、求解时间 | 端到端与主循环成本 |
| `nIter` | 收敛路径成本 |
| feasibility、gap | 数值正确性 |
| 每迭代时间 | 执行成本 |
| 求解阶段占比 | 区分求解主导和初始化主导 |

Runtime/kernel 层：

| 指标 | 用途 |
|---|---|
| kernel calls / total duration | 主要 GPU 工作 |
| `hipLaunchKernel` | launch 频率 |
| `hipMemcpy*` | 主机/设备和标量搬运压力 |
| synchronization | 排序和等待 |
| allocation/setup | 固定初始化成本 |

## 最终结论

```text
具体 W7900 热点来源：P10 compact evidence
正式 profiling 完整性：session2 5/5 PASS
已接受调优终点：CSR_ALG1 默认
必要保护：正确性、收敛轨迹、重复性
```

当前发布不需要额外 long profiling。未来只有在提出新的明确问题，例如新 GPU
架构、reduction path 或 scalar readback 时，才应采集新 trace。
