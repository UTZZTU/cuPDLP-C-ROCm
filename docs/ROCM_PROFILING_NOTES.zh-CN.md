# ROCm Profiling 说明

本文记录 `cuPDLP-C-ROCm` 项目中 ROCm/HIP 后端的 `rocprofv3` profiling 结果，并解释各个 tuning milestone 到底优化了哪些开销。

这份文档的目标不是只说明“运行时间变短了”，而是解释：

> ROCm tuning 为什么有效？每个优化 commit 改善的是 HIP runtime、kernel dispatch、memory copy，还是 kernel 本身？

## 文档范围

本文关注 Radeon 890M / `gfx1150` 开发平台上的 ROCm/HIP profiling。

profiling 使用：

```text
rocprofv3 --runtime-trace --output-format csv
```

该模式会记录 HIP runtime API trace、kernel dispatch trace、memory copy trace、scratch memory trace 以及相关 runtime 信息。

本次 profile 的 tuning milestones 包括：

| Milestone | Commit | 含义 |
|---|---|---|
| `pre_tuning` | `ae3b683` | 调优前 baseline |
| `remove_sync` | `f9d7f0d` | 移除多余 HIP device synchronization |
| `cache_attrs` | `8fed073` | 缓存 HIP device attributes |
| `fused_average` | `fa7e860` | 融合 ROCm average-iterate AXPY 更新 |
| `reduce_scalar_copies` | `b44c7ab` | 减少 movement interaction 中的 scalar copies |
| `current` | 当前 HEAD | 当前 CPU/CUDA/ROCm 三模态工程版本 |

本次 profile 的 case 包括：

| Case | 原因 |
|---|---|
| `lotfi` | 中等规模 case，调优收益明显 |
| `scfxm1` | current-vs-reduce 中有小幅 timing 差异，适合查疑点 |
| `pilot87` | 较大代表性 case，适合作为正向对照 |

## 为什么需要 profiling？

之前 repeated benchmark 已经说明：

1. ROCm tuning sequence 相对 pre-tuning baseline 有可测收益；
2. current 三模态工程版本相对 `reduce_scalar_copies` 没有系统性性能回退。

但 solve time 只能回答“快不快”，不能回答“为什么快”。

profiling 要回答的问题是：

1. `remove_sync` 是否真的减少了 runtime / synchronization overhead？
2. `cache_attrs` 是否减少了重复 HIP runtime calls？
3. `fused_average` 是否减少了 kernel dispatch？
4. `reduce_scalar_copies` 是否减少了 runtime/copy/dispatch overhead？
5. current 后续工程改动是否保留了优化后的 trace 结构？

## 核心结论

本次 profiling 最重要的结论是：

> ROCm tuning 的收益主要来自减少 HIP runtime API 开销和 kernel dispatch 数量；当前三模态工程版本保留了 tuning 后形成的优化 trace 结构。

从 `pre_tuning` 到 `current`，三个 profiled case 的变化大致如下：

| Case | solve time 下降 | HIP API calls 下降 | HIP API time 下降 | kernel dispatch 下降 | kernel time 下降 |
|---|---:|---:|---:|---:|---:|
| `lotfi` | 24.02% | 36.50% | 21.23% | 14.13% | 16.97% |
| `pilot87` | 17.55% | 31.81% | 14.64% | 11.52% | 7.86% |
| `scfxm1` | 23.87% | 36.18% | 20.55% | 13.99% | 16.73% |

这说明优化收益不是单次 benchmark 噪声，也不是单纯某一个 SpMV kernel 变快，而是迭代求解过程中 runtime call、kernel dispatch 和部分 GPU kernel 总时间整体下降。

## 各 milestone 解释

### `remove_sync`

从 `pre_tuning` 到 `remove_sync`：

| Case | solve time 变化 | HIP API time 变化 | kernel time 变化 |
|---|---:|---:|---:|
| `lotfi` | -12.47% | -13.10% | -3.85% |
| `pilot87` | -9.00% | -8.60% | -1.26% |
| `scfxm1` | -10.88% | -11.13% | -1.91% |

解释：

`remove_sync` 的主要收益来自降低 HIP runtime / synchronization 相关开销。kernel time 也有小幅变化，但并不是主要来源。

这符合预期：移除多余 HIP device synchronization 后，host-side waiting 和 runtime overhead 会减少。

### `cache_attrs`

从 `remove_sync` 到 `cache_attrs`：

| Case | HIP API calls 变化 | solve time 变化 |
|---|---:|---:|
| `lotfi` | -15.62% | -1.87% |
| `pilot87` | -13.53% | -0.10% |
| `scfxm1` | -15.53% | -1.20% |

解释：

`cache_attrs` 明确减少了重复 HIP runtime 查询类调用。由于这些 API 调用本身比同步轻，solve time 下降不如 `remove_sync` 明显，但 trace 已经证明调用结构改善了。

### `fused_average`

从 `cache_attrs` 到 `fused_average`：

| Case | kernel dispatch 变化 | HIP API calls 变化 | solve time 变化 |
|---|---:|---:|---:|
| `lotfi` | -7.04% | -15.98% | -8.10% |
| `pilot87` | -5.75% | -13.52% | -4.92% |
| `scfxm1` | -6.99% | -15.81% | -1.94% |

解释：

`fused_average` 减少了 average-iterate update 路径中的独立 GPU 操作数量。trace 中 kernel dispatch 数量下降，这正是 vector update fusion 应该产生的效果。

对于中小规模 LP case，kernel launch / dispatch overhead 可能比较明显，因此减少 dispatch count 能改善总体 solve time。

### `reduce_scalar_copies`

从 `fused_average` 到 `reduce_scalar_copies`：

| Case | HIP API calls 变化 | kernel dispatch 变化 | solve time 变化 |
|---|---:|---:|---:|
| `lotfi` | -6.38% | -7.63% | -4.52% |
| `pilot87` | -5.24% | -6.13% | -1.56% |
| `scfxm1` | -6.26% | -7.53% | -1.88% |

解释：

`reduce_scalar_copies` 进一步减少了 movement interaction 路径中的 scalar movement 和相关 runtime 工作。trace 显示 HIP API calls 和 kernel dispatches 都进一步下降，尤其对多迭代的 `lotfi` 更明显。

### `current`

从 `reduce_scalar_copies` 到 `current`：

| Case | HIP API calls | kernel dispatches | solve time |
|---|---:|---:|---:|
| `lotfi` | 0% | 0% | +0.81% |
| `pilot87` | 0% | 0% | -3.10% |
| `scfxm1` | 0% | 0% | -10.14% |

解释：

current 后续包含了很多工程化改动，例如恢复 CUDA 兼容、清理 backend 模式、移除公开 `BUILD_HIP` 选项、补充文档和固化 benchmark 结果。

profiling 结果说明：这些工程性改动没有增加额外 HIP API calls，也没有增加 kernel dispatches。

因此可以得出一个重要工程结论：

> 当前三模态工程版本保留了 `reduce_scalar_copies` 阶段形成的 ROCm 优化 trace 结构。

## Hotspot 观察

top kernel 和 top HIP API trace 显示，当前 ROCm/HIP 路径的热点主要集中在：

- rocSPARSE sparse matrix-vector kernels；
- rocBLAS AXPY / dot / norm / reduction kernels；
- movement interaction kernels；
- primal / dual gradient update kernels；
- runtime buffer copy；
- HIP memory-copy-related API calls。

典型热点名称包括：

```text
__amd_rocclr_copyBuffer
rocsparse::csrmvn_general_kernel
rocblas_axpy_kernel
movement_1_kernel
movement_2_kernel
primal_grad_step_kernel
dual_grad_step_kernel
rocBLAS dot / reduction kernels
```

这说明后续优化应重点关注：

1. 减少不必要 runtime calls；
2. 在安全前提下减少 kernel dispatch；
3. 减少 host-device scalar transfer；
4. 继续评估 vector update fusion；
5. 在更大 MPS case 上观察 rocSPARSE SpMV 行为；
6. 在 W7900 / `gfx1100` 上重新做 profiling，找平台特化瓶颈。

## memory-copy trace 注意事项

本次结果中，`memory_copy_trace.csv` 的记录可能较少，但 `trace_hip_api_top.csv` 中的 `hipMemcpy` / `hipMemcpyAsync` 仍可能占比较高。

这不表示结果无效，而是说明：

> low-level memory-copy trace 和 HIP API trace 的统计层级不同。

因此，解释 memory-copy 相关开销时，应优先结合：

- `trace_hip_api_top.csv`；
- `hipMemcpy` / `hipMemcpyAsync` 总时间；
- `hip_api_total_ms`；
- solver JSON 中已有的 copy timing 字段。

更准确的表述是：

> HIP memory-copy-related API time 是一个重要 runtime 组成部分，但在当前 profiling mode 下，low-level memory-copy trace events 可能比较稀疏。

## 与 benchmark 结果的关系

profiling 结果与 repeated benchmark 互相补充：

- repeated tuning ablation 证明 current 相对 pre-tuning baseline 更快；
- 27-case current-vs-reduce 证明 current 相对 `reduce_scalar_copies` 没有系统性性能回退；
- rocprofv3 milestone trace 解释了优化来源：减少 HIP API overhead、减少 kernel dispatch、降低 runtime/kernel total time。

因此，本项目现在不仅能说“ROCm/HIP 后端能跑”，还能说：

> ROCm/HIP 后端的调优收益有 trace 证据支撑，并且当前三模态工程分支保留了这些优化后的 runtime 结构。

## 后续 profiling 计划

### 短期

保留当前 profiling set：

```text
lotfi
scfxm1
pilot87
```

这三个 case 已经足够解释当前 tuning sequence。

### W7900 平台

Radeon PRO W7900 到手后，应使用：

```text
-DCMAKE_HIP_ARCHITECTURES=gfx1100
```

重新运行相同 profiling workflow。

建议首批 W7900 profiling case：

```text
lotfi
scfxm1
pilot87
一个 medium-large MPS case
一个 large MPS case
```

### 大规模 MPS

对于更大规模 MPS case，应重点观察：

- SpMV kernel time；
- rocSPARSE kernel 行为；
- memory bandwidth 相关表现；
- 每 iteration 的 kernel dispatch 数量；
- host-device copy overhead；
- GPU compute time 是否压过固定 overhead。

### cuPDLP-C vs cuPDLPx

如果后续评估 cuPDLPx，也可以复用同类 profiling 维度：

- algorithmic iteration count；
- total solve time；
- kernel dispatch count；
- SpMV time；
- vector update / reduction time；
- runtime overhead。

## 相关文件

profiling 数据文件：

```text
validation/rocm_prof_tuning_milestones_summary.csv
validation/rocm_prof_tuning_milestones_deltas.csv
validation/rocm_prof_tuning_milestones_kernel_top.csv
validation/rocm_prof_tuning_milestones_hip_api_top.csv
validation/rocm_prof_tuning_milestones_memory_copy_top.csv
validation/rocm_prof_tuning_milestones_summary.md
```

profiling 脚本：

```text
scripts/profile_rocm_tuning_milestones_rocprofv3.sh
scripts/summarize_rocprofv3_milestones.py
```

## 总结

本次 `rocprofv3` milestone trace 证明：

> ROCm tuning sequence 的主要收益来自减少 HIP runtime API overhead 和 kernel dispatch count；当前 CPU/CUDA/ROCm 三模态工程分支保留了这些优化后的 trace 结构。

这使得项目的性能叙事从“运行时间变短”升级为“有 profiler 证据说明为什么变快”，对后续 W7900 迁移、大规模 MPS 实验和比赛技术方案都有直接价值。

## W7900 profiling 完成状态更新 / 2026-06-17

本文前面提到的 W7900 migration，在当前项目阶段已经完成。W7900 不再是未来
profiling 目标，而是已经拥有 P10 targeted rocprof summaries 和 P11 SpMV
tuning endpoint。

当前 W7900 profiling/tuning 入口：

- `validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md`
- `validation/w7900_p11_spmv_alg_sweep_20260617_summary.zh-CN.md`
- `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`

当前结论是：SpMV 是第一条已经完成的 W7900-specific tuning path。copy
reduction 和 reduction-kernel 仍可作为未来方向，但不属于当前项目终点。
