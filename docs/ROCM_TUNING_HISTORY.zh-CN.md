# ROCm 调优历史与消融实验结果

本文记录 `cuPDLP-C-ROCm` 分支中 ROCm/HIP 后端的调优过程、benchmark 方法和阶段性结论。

这篇文档不是最终性能报告，而是一个可复现实验记录：它说明我们如何比较不同 ROCm tuning milestone，如何判断调优是否有效，以及如何看待 current 工程版本与历史最快 tuning 版本之间的关系。

## 文档范围

本项目当前保留三种后端模式：

| 模式 | 作用 |
|---|---|
| CPU | 正确性与可移植性基线 |
| CUDA | 上游兼容的 NVIDIA GPU 后端 |
| ROCm/HIP | AMD Radeon / ROCm 目标后端 |

本文只关注 ROCm/HIP 后端的调优历史。

CUDA 后端的作用是提供上游兼容和 NVIDIA 对照基线；CPU 后端用于 correctness baseline。ROCm/HIP 后端是本项目的主要移植与优化对象。

## 为什么要记录调优历史？

最初的 ROCm/HIP 移植目标是“先跑通”。随着项目推进，后续又做了一些性能相关优化，例如减少同步、减少 host-device scalar copy、融合部分向量更新等。

但是，仅仅说“做了优化”是不够的。科学计算项目需要回答：

1. 优化是否真的带来性能收益？
2. 收益是普遍存在，还是只在少数 case 上出现？
3. 优化是否影响 solver 的 termination status？
4. 优化是否改变迭代次数或数值结果？
5. 后续工程化改动是否导致性能回退？

因此，本项目补充了 repeated benchmark 和 tuning ablation，把调优过程变成可复查的数据证据。

## Benchmark 方法

调优 benchmark 使用以下原则：

- 使用固定 case list；
- 固定 `nIterLim=200000000`；
- 对每个 version/case 重复运行；
- 使用 median solve time 作为主指标；
- 同时保留 mean、std、min、max、CV；
- 保留 termination status、exit code、iteration count、feasibility 和 gap；
- 不用单次运行结果直接下结论。

采用 median 的原因是：小规模 GPU benchmark 很容易受到系统负载、功耗状态、温度、driver/runtime 状态和固定启动开销影响。重复运行并报告 median、mean、standard deviation 和 coefficient of variation 能更稳健地判断性能趋势。

## Tuning milestones

消融实验使用以下 milestone：

| Milestone | Commit | 含义 |
|---|---|---|
| `pre_tuning` | `ae3b683` | 调优前 baseline |
| `remove_sync` | `f9d7f0d` | 移除 movement interaction 中多余 HIP device synchronize |
| `cache_attrs` | `8fed073` | 缓存 HIP device attributes |
| `fused_average` | `fa7e860` | 融合 ROCm average iterate axpy updates |
| `reduce_scalar_copies` | `b44c7ab` | 减少 movement interaction scalar copies |
| `current` | current HEAD at run time | 当前三模态工程版本 |

其中 `reduce_scalar_copies` 是历史上观察到的最快 ROCm tuning milestone 之一；`current` 则包含后续工程化改动，例如恢复 CUDA 兼容、清理构建选项、补充文档和验证数据。

## 6-case repeated tuning ablation

为了比较调优阶段的收益，项目首先使用 6 个代表性 case：

| Case | Tier | 用途 |
|---|---|---|
| `afiro` | S | 极小 smoke/overhead case |
| `sc50b` | S | 小型 Netlib case |
| `lotfi` | M | 中等、多迭代 case |
| `80bau3b` | M | 中等规模 case |
| `maros-r7` | L | 大型但迭代数较少的 case |
| `pilot87` | L | 较大代表性 case |

实验设置：

```text
6 个 milestone × 6 个 case × 5 次 repeat = 180 次 solver run
```

主指标为 5 次运行的 median solve time。

## 6-case correctness 结论

在 6-case repeated ablation 中，所有 version/case/repeat 均达到：

```text
terminationCode = OPTIMAL
exit code = 0
```

同时，同一 case 在不同 milestone 下 iteration count 保持一致。这说明这些 ROCm tuning 没有破坏 quick set 上的基本正确性和收敛状态。

## 6-case median solve time

主指标：5 次重复运行的 median solve time。

| Milestone | afiro | sc50b | lotfi | 80bau3b | maros-r7 | pilot87 |
|---|---:|---:|---:|---:|---:|---:|
| `pre_tuning` | 0.052744 | 0.072827 | 4.537407 | 0.970653 | 0.124608 | 8.690948 |
| `remove_sync` | 0.059098 | 0.071003 | 3.997434 | 0.915490 | 0.120013 | 8.179166 |
| `cache_attrs` | 0.060280 | 0.069627 | 3.986371 | 0.912363 | 0.117736 | 8.218034 |
| `fused_average` | 0.053140 | 0.069351 | 3.825229 | 0.901840 | 0.117184 | 8.000284 |
| `reduce_scalar_copies` | 0.052801 | 0.066655 | 3.615290 | 0.869338 | 0.116324 | 7.820215 |
| `current` | 0.052900 | 0.066839 | 3.646848 | 0.874944 | 0.121077 | 7.820457 |

## current vs pre_tuning

| Case | pre_tuning median | current median | Speedup | Time reduction |
|---|---:|---:|---:|---:|
| `afiro` | 0.052744 | 0.052900 | 0.997x | -0.30% |
| `sc50b` | 0.072827 | 0.066839 | 1.090x | 8.22% |
| `lotfi` | 4.537407 | 3.646848 | 1.244x | 19.63% |
| `80bau3b` | 0.970653 | 0.874944 | 1.109x | 9.86% |
| `maros-r7` | 0.124608 | 0.121077 | 1.029x | 2.83% |
| `pilot87` | 8.690948 | 7.820457 | 1.111x | 10.02% |

current 相对 pre-tuning 在 6-case quick set 上几何平均约为：

```text
1.094x speedup
```

这说明 ROCm tuning 对中等和较大 case 有可测收益。尤其是：

- `lotfi`：约 19.6% median solve-time reduction；
- `pilot87`：约 10.0%；
- `80bau3b`：约 9.9%；
- `sc50b`：约 8.2%。

`afiro` 是极小 case，主要受固定启动开销影响，因此不能作为判断 GPU 优化效果的主要依据。

## 最快 observed milestone

在 6-case repeated ablation 中，各 case 的最快 milestone 如下：

| Case | Fastest milestone | Fastest median solve time |
|---|---|---:|
| `afiro` | `pre_tuning` | 0.052744 |
| `sc50b` | `reduce_scalar_copies` | 0.066655 |
| `lotfi` | `reduce_scalar_copies` | 3.615290 |
| `80bau3b` | `reduce_scalar_copies` | 0.869338 |
| `maros-r7` | `reduce_scalar_copies` | 0.116324 |
| `pilot87` | `reduce_scalar_copies` | 7.820215 |

`reduce_scalar_copies` 是 5/6 case 中观察到的最快 milestone。

这并不表示 current 分支不可接受。原因是 current 后续包含了三模态工程化修复、CUDA 兼容恢复、CMake 选项清理和文档补充等非纯性能改动。为了确认这些工程改动是否带来系统性性能回退，项目又做了 27-case current-vs-reduce 对比。

## 27-case current vs reduce_scalar_copies comparison

后续实验比较：

```text
base:    reduce_scalar_copies (`b44c7ab`)
current: 当前 HEAD
case:    validation/cases_benchmark_200m.txt 去掉 greenbea
repeat:  3 次
```

该实验目标是判断：

> 当前三模态工程版本是否相对历史最快 ROCm tuning milestone 出现系统性性能回退？

实验结果显示：

```text
Geometric mean speedup of base over current: 0.9995092331107024
```

这说明 base 与 current 整体几何平均几乎持平。严格说，base 相对 current 只快约 0.05%，这个量级可以认为是噪声，不构成实质性能回退。

## 27-case 结果解读

current 慢超过 2% 的 case 包括：

```text
afiro
sc50b
recipe
scfxm1
```

其中：

- `afiro`、`sc50b`、`recipe` 都是小 case，绝对时间差很小，且容易被启动开销和测量噪声影响；
- `recipe` 的 CV 较高，更可能是噪声；
- `scfxm1` 是后续可做 focused profiling 的候选 case。

同时，current 在一些中大型 case 上反而更快，例如：

```text
israel
maros-r7
ship08s
degen2
greenbeb
pilot87
```

特别是 `greenbeb` 和 `pilot87` 更有代表性，因为它们不是极小 case。

因此，27-case 结论是：

> current 与 `reduce_scalar_copies` 基本性能持平；current 没有出现系统性性能回退；少数小 case 的波动应谨慎解释。

## Median DeviceMatVecProdTime

6-case ablation 中的 median DeviceMatVecProdTime 如下：

| Milestone | afiro | sc50b | lotfi | 80bau3b | maros-r7 | pilot87 |
|---|---:|---:|---:|---:|---:|---:|
| `pre_tuning` | 0.019731 | 0.021287 | 0.283484 | 0.050591 | 0.019830 | 0.262654 |
| `remove_sync` | 0.020783 | 0.022891 | 0.235519 | 0.042941 | 0.019717 | 0.226007 |
| `cache_attrs` | 0.022485 | 0.020762 | 0.224449 | 0.043925 | 0.020229 | 0.242991 |
| `fused_average` | 0.019422 | 0.022065 | 0.220678 | 0.047636 | 0.020546 | 0.233992 |
| `reduce_scalar_copies` | 0.020542 | 0.020963 | 0.218564 | 0.046652 | 0.020861 | 0.231445 |
| `current` | 0.020111 | 0.021583 | 0.233689 | 0.047721 | 0.020473 | 0.222489 |

这个表说明，solve time 变化不完全由 `DeviceMatVecProdTime` 解释。一些优化主要减少的是 SpMV 之外的开销，例如：

- host-device scalar copy；
- device synchronize；
- kernel launch / runtime overhead；
- vector update 路径；
- movement interaction 中的额外交互。

因此，后续 profiling 应使用 `rocprofv3` 进一步拆分 HIP runtime、kernel、memory copy 和 synchronization 时间。

## 如何解释这些调优？

本阶段可以得出以下结论：

1. ROCm/HIP 后端 tuning 在 quick set 上有可测收益；
2. current 相对 pre-tuning baseline 有明显提升；
3. `reduce_scalar_copies` 是 6-case quick set 中观察到的最快 milestone；
4. current 与 `reduce_scalar_copies` 在 27-case repeated comparison 中整体持平；
5. 当前工程化改动没有造成系统性性能回退；
6. 后续若继续优化，应以 profiler 证据为依据，而不是仅凭单次 solve time。

## 当前可以接受的工程判断

虽然 current 不是每个 case 的 fastest observed point，但它是更完整的工程版本，因为它包含：

- CPU / CUDA / ROCm 三模态边界；
- CUDA backend 兼容恢复；
- `BUILD_HIP` 公共选项移除；
- backend compatibility layer；
- 文档和 benchmark 结果固化；
- 行尾和脚本结构规范。

因此，当前版本适合作为后续 W7900 迁移和比赛平台验证的主线 baseline。

如果后续需要追求极限性能，可以同时对照：

```text
current HEAD
reduce_scalar_copies (`b44c7ab`)
```

## 后续 profiling 计划

下一步应补充 ROCm profiling，不只看 solver JSON 中的总时间。

建议使用 `rocprofv3` 采集：

- HIP runtime API trace；
- kernel dispatch trace；
- memory copy trace；
- memory allocation trace；
- HSA trace；
- marker trace；
- kernel timeline。

优先选择以下 case：

| Case | 原因 |
|---|---|
| `lotfi` | tuning 收益明显，适合解释收益来源 |
| `scfxm1` | current 相对 reduce 略慢，是可疑 case |
| `pilot87` | 较大 case，current 表现较好，可作正向对照 |

后续目标是回答：

1. 哪些 kernel 或 runtime 调用占主要时间？
2. 调优前后 memory copy 是否减少？
3. 同步调用数量是否减少？
4. vector update 或 movement interaction 是否变轻？
5. SpMV 时间占比是否随 case scale 变化？

## 局限性

本调优历史仍有局限：

- 当前 case 仍以 Netlib 中小规模问题为主；
- 890M 是本地开发平台，不是最终比赛平台；
- 5-repeat / 3-repeat 适合工程判断，但不是最终论文级统计；
- `DeviceMatVecProdTime` 只能解释部分 GPU 时间；
- 还缺少完整 `rocprofv3` trace 对比；
- 大规模 MPS 数据集尚未系统纳入；
- W7900 / `gfx1100` 平台还需要后续实测。

## 后续计划

建议后续按以下顺序推进：

1. 补齐中英文文档；
2. 增加 `rocprofv3` profiling 脚本；
3. 对 `lotfi`、`scfxm1`、`pilot87` 做 current-vs-reduce profiling；
4. 引入 H100 上的大规模 MPS 数据集；
5. 在 3090、4090D、H100、890M、W7900 上建立分层 benchmark；
6. 对比 cuPDLP-C 与 cuPDLPx；
7. 在 W7900 上针对 `gfx1100` 做平台化调优。

## 相关数据文件

本项目保留以下结果文件作为 tuning 证据：

```text
validation/rocm_tuning_ablation_6cases_repeats_raw.csv
validation/rocm_tuning_ablation_6cases_repeats_summary.csv
validation/rocm_tuning_ablation_6cases_repeats_summary.md

validation/rocm_current_vs_reduce_27cases_repeats_raw.csv
validation/rocm_current_vs_reduce_27cases_repeats_aggregated.csv
validation/rocm_current_vs_reduce_27cases_repeats_comparison.csv
validation/rocm_current_vs_reduce_27cases_repeats_comparison.md
```

## 总结

本阶段最重要的结论是：

> ROCm/HIP 后端从 pre-tuning 到 current 有可测性能提升；current 三模态工程版本与历史最快 tuning milestone 在 27-case repeated comparison 中整体持平，没有出现系统性性能回退。

这意味着当前分支既保留了工程完整性，又基本维持了 ROCm tuning 后的性能水平。后续优化应以 `rocprofv3` profiling 和大规模 MPS 数据为依据继续推进。
