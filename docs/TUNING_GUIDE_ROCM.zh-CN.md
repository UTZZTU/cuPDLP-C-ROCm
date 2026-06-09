# ROCm 调优指南

> English version: [`TUNING_GUIDE_ROCM.md`](TUNING_GUIDE_ROCM.md)

本文记录 cuPDLP-C ROCm/HIP port 的 profiling 和 tuning notes。

## 目标和范围

| 项目 | 值 |
|---|---|
| 当前已验证目标 | AMD Radeon 890M |
| 架构 | `gfx1150` |
| ROCm | 7.2.1 |
| Profiler | `rocprofv3` |
| 构建目标 | `build-rocm-plc/bin/plc` |

本文不是宣称 ROCm/HIP backend 已完全调优，而是记录当前 profiling baseline、已完成的低风险 tuning 步骤，以及后续优化方向。

## 为什么需要调优

PDLP 类一阶 LP solver 高度依赖重复 sparse matrix-vector product 和 vector operation。重要操作包括：

- `Ax`；
- `Aty`；
- hipSPARSE / rocSPARSE SpMV；
- hipBLAS / rocBLAS vector operation；
- vector update；
- reduction；
- projection kernel；
- residual computation；
- host/device synchronization；
- memory allocation；
- host/device memory transfer。

`afiro.mps` 和 `sc50b.mps` 这类小 case 适合 correctness 和 workflow validation，但太小，不代表更大 sparse LP 问题上的最终 GPU 性能。

## Profiling 入口

运行 smoke profiling：

```bash
RESULT_ROOT=profiling/results/current \
  ./scripts/profile_rocm_smoke.sh
```

汇总 `rocprofv3` CSV trace：

```bash
python3 scripts/summarize_rocm_profile.py \
  --input profiling/results/current \
  --output profiling/results/current/profile_summary.md
```

Copy/copyBuffer 分析：

```bash
python3 scripts/analyze_rocm_copy_trace.py \
  --input profiling/results/current/sc50b_rocprofv3 \
  | tee profiling/results/current/sc50b_copy_analysis.md
```

Profiling 输出是生成 artifact，不应提交。

## 初始 profiling 观察

`afiro` 和 `sc50b` 的初始 `rocprofv3` runtime trace 显示，小 case runtime 由大量小 GPU 操作主导，而不是由单个 custom kernel 主导。

观察到的热点包括：

- `hipLaunchKernel`；
- `hipMemcpyAsync`；
- `hipMemcpy`；
- `hipDeviceSynchronize`；
- `hipStreamSynchronize`；
- `hipMalloc` / `hipFree`；
- `__amd_rocclr_copyBuffer`；
- `__amd_rocclr_fillBufferAligned`；
- rocSPARSE SpMV kernels；
- rocBLAS AXPY、dot、norm 和 scaling kernels；
- custom PDLP update 和 movement kernels。

第一阶段结论：

```text
对小 smoke case，先优化结构性开销：launch、copy、synchronization 和 repeated runtime query。
不要一开始就做低层 instruction tuning 或 custom SpMV 重写。
```

## 需要跟踪的指标

Solver-level metrics：

| 指标 | 作用 |
|---|---|
| Wall-clock time | 用户可见端到端 runtime |
| Solve time | 主 solver loop runtime |
| Iteration count | 算法推进程度 |
| Iterations per second | 粗粒度吞吐 |
| Matvec time | Sparse linear algebra 贡献 |
| Feasibility and gap | 正确性和收敛质量 |

Runtime-level metrics：

| 指标 | 作用 |
|---|---|
| `hipLaunchKernel` count/time | Kernel launch 粒度 |
| `hipMemcpyAsync` count/time | 异步内存传输频率 |
| `hipMemcpy` count/time | 同步内存传输频率 |
| `hipDeviceSynchronize` count/time | 全局同步开销 |
| `hipStreamSynchronize` count/time | Stream 同步开销 |
| `hipMalloc` / `hipFree` count | 重复分配开销 |
| `hipGetDevice` / attribute query count | 重复 runtime query 开销 |

Kernel-level metrics：

| Kernel group | 作用 |
|---|---|
| rocSPARSE SpMV kernels | PDLP 核心 sparse matvec 工作 |
| rocBLAS AXPY kernels | Vector update 开销 |
| rocBLAS dot/norm kernels | Reduction 开销 |
| Custom gradient kernels | PDLP update 成本 |
| Movement kernels | Restart 和 movement interaction 成本 |
| ROCclr copy/fill kernels | 隐式 copy/fill 开销 |

## 已完成 profiling-driven optimizations

当前 tuning pass 在 Radeon 890M / `gfx1150` 上完成了四个低风险优化。

### 1. 移除冗余 device synchronization

从 ROCm/HIP movement interaction 路径中移除了一个冗余 `hipDeviceSynchronize()`。最终 blocking device-to-host copy 已经能提供 host 读取 scalar result 所需的顺序保证。

Smoke-profile 效果：

| Case | Before | After |
|---|---:|---:|
| `afiro` `hipDeviceSynchronize` calls | 203 | 3 |
| `sc50b` `hipDeviceSynchronize` calls | 564 | 3 |

### 2. 缓存 HIP device attributes

在 HIP linear algebra helper 路径中缓存重复查询的 device attributes。

这会减少 runtime API noise，避免反复查询 multiprocessor count 和 warp size 等稳定属性。

### 3. 融合 average-iterate AXPY updates

两个每迭代 average-iterate AXPY update 被融合到一个 custom ROCm/HIP kernel：

```text
update_average_kernel
```

观察效果：

| 指标 | `afiro` before | `afiro` after | `sc50b` before | `sc50b` after |
|---|---:|---:|---:|---:|
| `hipLaunchKernel` calls | 2667 | 2468 | 6071 | 5511 |
| `rocblas_axpy_kernel` dispatches | 506 | 108 | 1270 | 150 |
| `update_average_kernel` dispatches | 0 | 199 | 0 | 560 |

### 4. 减少 movement interaction scalar D2D copies

`cupdlp_movement_interaction_cuda()` 中两个小的 device-to-device scalar copy 被替换为一个小 custom kernel：

```text
save_movement_xy_kernel
```

Smoke-profile 效果：

| 指标 | `afiro` before | `afiro` after | `sc50b` before | `sc50b` after |
|---|---:|---:|---:|---:|
| `hipMemcpyAsync` calls | 1136 | 736 | 2485 | 1363 |
| `__amd_rocclr_copyBuffer` dispatches | 1444 | 1044 | 3182 | 2060 |
| `save_movement_xy_kernel` dispatches | 0 | 200 | 0 | 561 |

这减少了许多 tiny copyBuffer dispatch，同时保持 validation 结果。

## 当前优化后 profile 形态

剩余热点包括：

- `hipLaunchKernel`；
- remaining `hipMemcpy` / `hipMemcpyAsync`；
- remaining `__amd_rocclr_copyBuffer`；
- rocBLAS dot 和 norm reductions；
- rocSPARSE SpMV kernels。

AXPY 路径不再是主要 rocBLAS 问题。剩余 rocBLAS 热点主要是 reduction 类操作，替换风险更高。

## 不应随意修改什么

没有更大 validation 和 profiling 前，避免以下变化：

- 删除 legacy C/HIP compatibility symbols；
- 重写 sparse matrix storage；
- 用 custom kernel 替换所有 rocBLAS 调用；
- 用 custom SpMV 替换所有 rocSPARSE 调用；
- 没有严谨数值验证就替换 dot/norm reductions；
- 对 solver loop 做完整 HIP Graph capture；
- 只为 `afiro` 或 `sc50b` 调优。

## Large-case profiling 策略

下一阶段 profiling 应使用更大的 MPS case。建议首批 large-case profiling targets 包括：

- 一个 ROCm 有竞争力的 case；
- 一个 ROCm 更慢的 case；
- 一个 SpMV 主导的大 sparse case；
- 如果日志稳定，选择一个 convergence-sensitive case。

用 large-case profiling 判断下一个瓶颈是 launch count、SpMV、BLAS reductions、memory movement 还是 convergence trajectory。

## 后续 tuning 工作

- 添加 large MPS case profiling 模板。
- 添加 solver phase 的 ROCTx range。
- 更清晰地区分 setup time 和 main iteration time。
- 调查剩余 scalar readback 和 synchronization。
- 在 validation 覆盖更大后再调查 reduction kernel。
- 调查 SpMV descriptor 和 buffer reuse。
- W7900 迁移后比较 `gfx1150` 和 `gfx1100`。

## 总结

当前 ROCm/HIP port 已经足以开始 profiling 和受控 tuning，但还不足以宣称最终性能。早期 tuning 应聚焦：

```text
launch count + synchronization + memory copies + SpMV + BLAS level-1 reductions
```

每个 tuning change 都必须配套 validation 和 before/after profiling 或 benchmark 证据。
