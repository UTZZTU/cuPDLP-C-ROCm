# W7900 ROCm profiling 计划

> English: [W7900_ROCM_PROFILING_PLAN.md](W7900_ROCM_PROFILING_PLAN.md)

本文定义 W7900 / `gfx1100` 调优前的 profiling 计划。它应在 baseline 文档稳定之后、kernel 级修改之前使用。

<!-- W7900_OPTIMIZATION_BASELINES_20260614_BEGIN -->
## 后续 profiling 的 baseline 口径修正

当前 W7900 分支继承了此前 890M/gfx1150 ROCm tuning，并已经完成自身 P10/P11/P12/P14-A1 证据链。`ae3b683` 仍作为真正 pre-tuning anchor，当前 W7900 HEAD 是 P11 和 P14-A1 后已接受的项目终点。

详见 [W7900 优化基线说明](W7900_OPTIMIZATION_BASELINES.zh-CN.md)。
<!-- W7900_OPTIMIZATION_BASELINES_20260614_END -->

## 当前 baseline 状态

profiling 阶段基于以下已记录 baseline：

- smoke validation：已完成
- Netlib 27-case validation：已完成
- large-MPS `initial17_safe`：已完成
- large-MPS `watchlist6` + `near_optimal2`：已完成
- 合并后的 large-MPS `non-hard23`：23/23 `OPTIMAL`
- `hard3`：单独用于收敛轨迹分析

profiling 的目标不是重新证明正确性，而是定位 W7900 路径的耗时来源，并判断哪些瓶颈值得调优。

## Profiling case matrix

| 分组 | Cases | 目的 |
|---|---|---|
| fast representative | `set-cover-model`, `supportcase10`, `L2CTA3D` | 检查固定开销、HIP API overhead、setup cost 和短运行 kernel profile |
| competitive representative | `square41`, `thk_48`, `tpl-tub-ws1617` | 分析 W7900 在 wall time 上接近或超过高端参考设备的 case |
| slow-but-solvable | `s100`, `Primal2_1000` | 分析高迭代次数和 gap trajectory |
| hard3 diagnostic | `dlr1`, `Dual2_5000`, `fhnw-binschedule1` | 只做短诊断；在单独分析前不混入主 baseline |

## 工具层次

使用分层 profiling 流程：

1. solver runtime JSON baseline。
2. `rocm-smi` 或 AMD SMI 记录 GPU telemetry。
3. 有 `rocprofv3` 时使用 HIP/kernel trace 和 statistics。
4. 第一轮 trace 找到目标 kernel 后，再考虑 counter collection。

## 需要记录的指标

| 指标 | 意义 |
|---|---|
| `wall_seconds` | 端到端用户可见性能 |
| `dSolvingTime` | solver 内部计算时间 |
| `DeviceMatVecProdTime` | SpMV 相关设备端时间 |
| `nIter` | 区分单次迭代速度和收敛行为 |
| relative primal/dual/gap | 判断数值进展和 near-tolerance stall |
| HIP API time | 判断 launch/copy/runtime overhead |
| kernel statistics | 找主要 kernel 和高频 dispatch |
| GPU power/temperature/utilization | 排除环境或功耗温度问题 |

## Profiling 阶段

### Stage 0：环境与工具检测

记录：

```bash
command -v rocprofv3 rocprof rocm-smi amd-smi hipcc || true
rocminfo | grep -E "Name:|Marketing Name|gfx" || true
rocm-smi || true
```

### Stage 1：无 profiler baseline rerun

先不挂 profiler 跑选定 case，保存：

- JSON output
- terminal log
- `runtime_summary.csv`
- 跑前/跑后的 `rocm-smi` snapshot

这是 profiler overhead 之前的参考。

### Stage 2：HIP 和 kernel trace

有 `rocprofv3` 时优先使用：

```bash
rocprofv3 --stats --hip-trace --kernel-trace --output-format csv --output-directory "$OUT/rocprofv3" -- "$PLC" -fname "$MPS" -out "$JSON" -nIterLim "$ITER_LIMIT" -dTimeLim "$TIME_LIMIT"
```

如果机器上只有 legacy `rocprof`，应先检查本机版本后再补 fallback。

### Stage 3：分析 top kernels 和 overhead

每个 case 输出：

- total time 排名前列的 kernel
- call count 排名前列的 kernel
- HIP API overhead summary
- `DeviceMatVecProdTime / dSolvingTime`
- `nIter` 与 solve time 的关系

### Stage 4：确定调优目标

不要盲目调所有路径。根据 profiling 数据决定优先级：

- SpMV/kernel 优化
- reduction 优化
- 减少不必要 host-device copy
- 降低 HIP setup 或 launch overhead
- 只有在收敛行为改变时才调 solver control path

## 预期解释

W7900 快的场景：

- case 规模足够大，可以摊薄 setup/launch overhead；
- SpMV 和 vector operation 占主导；
- 收敛稳定；
- 显存带宽和 VRAM 容量能发挥作用。

W7900 慢的场景：

- 迭代次数主导；
- gap 在阈值附近停滞；
- restart/step-size 路径与 CUDA 参考不同；
- 小 case 被固定开销主导；
- 当前 ROCm/gfx1100 kernel 还没调优。

## 输出策略

raw large MPS 和 raw profiler trace directory 不进 git。

只提交：

- scripts
- curated CSV summaries
- Markdown summaries
- 小型 SVG charts
- 精简 profiler summaries

建议输出根目录：

```text
/app/cupdlp_w7900/results/w7900_rocprof/
```

建议提交的 summary：

```text
validation/w7900_rocprof_case_matrix_*.csv
validation/w7900_rocprof_kernel_top_*.csv
validation/w7900_rocprof_hip_api_top_*.csv
docs/W7900_ROCM_PROFILING_PLAN.md
```

## 第一轮 profiling 建议

先从三个 case 开始：

1. `set-cover-model`：fast/representative，用于分析 overhead 和 kernel dispatch。
2. `square41`：competitive case，用于展示 W7900 强项。
3. `s100`：slow-but-solvable，用于区分迭代次数和单次迭代成本。

原始计划中不从 hard3 开始；当前 hard3 probe2 已归档，后续不再作为 pending profiling 前置项。

## 完成状态更新 / 2026-06-17

本文档是原始 W7900 profiling plan。该计划现在已经执行完毕，并由已提交的
P10/P11/P12 artifacts 取代。

当前状态：

- P10 targeted rocprof profiling 已完成。
- P11 SpMV algorithm switch、smoke 和五 case sweep 已完成。
- 当前 W7900 默认 SpMV algorithm：
  `HIPSPARSE_SPMV_CSR_ALG1`。
- 回退路径：
  `CUPDLP_HIP_SPMV_ALG=csr_alg2`。
- P12 SpMV buffer algorithm consistency 实验已测试并拒绝，因为它改变了迭代数。

取代本文档的最终材料：

- `validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md`
- `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`
- `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md`
