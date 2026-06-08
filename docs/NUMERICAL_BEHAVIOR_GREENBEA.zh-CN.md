# 数值行为说明：`greenbea`

本文说明为什么 Netlib `greenbea` case 在 `cuPDLP-C-ROCm` 项目中被单独记录和分析。

简要结论是：`greenbea` 不应被当作普通 smoke test 的 pass/fail case。它是一个长时间运行、收敛敏感的线性规划实例，能够暴露 CPU、CUDA、ROCm/HIP 后端之间的数值轨迹差异。

## 背景

cuPDLP-C 基于 PDLP / PDHG 类一阶方法求解线性规划。公开 PDLP 文献指出，PDLP 是一种实用的一阶线性规划方法，它由 primal-dual hybrid gradient（PDHG）应用到 LP 的 saddle-point formulation 得到；其核心计算是矩阵-向量乘法，因此具备扩展到大规模问题的潜力。

这对 `greenbea` 很重要。GPU 后端虽然执行同一套高层 solver 逻辑，但底层会经过不同的：

- 稀疏矩阵-向量乘法实现；
- 向量更新 kernel；
- reduction 顺序；
- 同步点；
- host-device scalar copy；
- BLAS / sparse library 行为；
- 浮点运算顺序。

对大多数 validation case，这些差异不会影响 termination status。但对 `greenbea` 这类收敛敏感 case，这些差异可能改变迭代轨迹，导致 CPU、CUDA、ROCm/HIP 的最终状态和收敛速度表现不同。

参考资料：

- Google Research / NeurIPS 2021, *Practical Large-Scale Linear Programming using Primal-Dual Hybrid Gradient*: https://proceedings.neurips.cc/paper/2021/hash/a8fbbd3b11424ce032ba813493d95ad7-Abstract.html
- OR-Tools PDLP mathematical background: https://developers.google.com/optimization/lp/pdlp_math
- COPT-Public/cuPDLP-C upstream repository: https://github.com/COPT-Public/cuPDLP-C
- cuPDLP.jl GPU PDHG paper: https://arxiv.org/abs/2311.12180

## 为什么 `greenbea` 要单独记录？

大多数 validation case 用来回答：

> 这个后端是否能构建并正确求解代表性 LP 实例？

`greenbea` 用来回答的是另一个问题：

> 在相同高层 solver 设置下，CPU、CUDA、ROCm/HIP 后端的长迭代数值轨迹有什么差异？

因此，`greenbea` 不应该因为 GPU 后端达到 wall-clock limit 就被隐藏或删除。它是一个有价值的数值行为证据，用于后续分析不同后端的收敛路径。

## 当前 `greenbea` benchmark 策略

项目当前策略是：

- 保持 `nIterLim=200000000`；
- 跨设备报告中将 3600 秒作为长 case 的有效 wall-clock limit；
- timeout / limit 结果保留为数值行为数据；
- 记录 termination code、iteration count、feasibility、duality gap 和 solve time；
- 不通过无限增加 time limit 强行追求 GPU 收敛；
- 将 runtime failure 与 solver convergence limit 区分记录。

这样可以避免把一个收敛敏感诊断 case 变成无边界的手工 benchmark。

## 已观察结果

以下结果来自项目已经完成的跨设备 benchmark。

### RTX 3090 CUDA

RTX 3090 上单独运行的 `greenbea` 200M 实验中，CUDA GPU 路径达到内部 3600 秒限制。

| 后端 | 状态 | 迭代数 | 求解时间 | 相对 primal feasibility | 相对 dual feasibility | 相对 duality gap |
|---|---|---:|---:|---:|---:|---:|
| CPU | `OPTIMAL` | 8,538,920 | 1286.92 s | — | — | — |
| CUDA GPU | `TIMELIMIT_OR_ITERLIMIT` | 41,615,624 | 3600.000060 s | 0.21299620838891 | 0.00000067393008 | 0.00256258916268 |

该 CUDA GPU 结果中 primal/dual code 仍显示 feasible，但没有在 3600 秒限制内达到 solver 的 optimal termination 条件。

### RTX 4090D CUDA

RTX 4090D full 200M benchmark 中，`greenbea` 的 CUDA run 记录为 shell-level timeout。

| 后端 | 状态 | 迭代数 | 求解时间 |
|---|---|---:|---:|
| CPU | `OPTIMAL` | 8,538,920 | 1178.48 s |
| CUDA GPU | shell timeout | — | 3600 s wall-clock limit |

需要注意：早期 4090D CUDA 失败曾由 CUDA context initialization failure 引起，原因与 GPU compute mode / 其他进程占用有关。这个运行环境问题后来通过切换可用 GPU 重新运行解决。最终 4090D 结果仍然说明 `greenbea` 是长时间收敛敏感 case，而不是普通 quick validation case。

### Radeon 890M ROCm/HIP

Radeon 890M full 200M benchmark 中，`greenbea` 的 ROCm/HIP run 记录为 shell-level timeout。

| 后端 | 状态 | 迭代数 | 求解时间 |
|---|---|---:|---:|
| CPU | `OPTIMAL` | 8,538,920 | 592.58 s |
| ROCm/HIP GPU | shell timeout | — | 3600 s wall-clock limit |

同一轮 890M full run 中，大多数其他 case 在 ROCm/HIP 后端达到 `OPTIMAL`。因此，`greenbea` 不应被解释为 ROCm/HIP 后端整体失败，而应被解释为一个特定的 convergence-sensitive case。

## 结果解释

目前证据说明：

1. CPU 在已记录运行中能够将 `greenbea` 求解到 `OPTIMAL`；
2. CUDA 和 ROCm/HIP GPU 路径可能表现出明显不同的数值轨迹；
3. 3090 CUDA 200M run 达到 41.6M iteration 和 3600 秒仍未 `OPTIMAL`；
4. 4090D CUDA 和 890M ROCm/HIP 在 full benchmark workflow 中达到 wall-clock limit；
5. 大多数其他 validation case 在 GPU 后端可达到 `OPTIMAL`，所以 `greenbea` 应单独归类为收敛敏感实例。

这并不能证明 ROCm/HIP port 数值错误。它说明：在这个 LP 实例上，GPU 后端轨迹与 CPU 后端差异足够明显，需要单独分析。

## 为什么 CPU 与 GPU 迭代轨迹会不同？

即便使用相同高层算法和相同 MPS 输入，不同后端仍可能因为以下因素产生轨迹差异：

- 稀疏矩阵-向量乘法实现不同；
- reduction 顺序不同；
- 浮点加法结合顺序不同；
- vector update 是否被 fusion；
- 同步点和 kernel launch 顺序不同；
- host-device scalar copy 时机不同；
- BLAS / sparse library 的底层实现不同；
- adaptive step size 或 restart 决策受到微小数值差异影响。

对于许多 LP 实例，这些差异不会影响最终 termination。对于退化、病态或收敛敏感实例，微小差异可能在百万级甚至千万级迭代中放大，最终表现为 iteration count、feasibility、gap 或 timeout 行为差异。

这对 PDHG/PDLP 类算法尤其重要，因为它们是迭代型一阶方法，长时间运行中会反复执行大量矩阵-向量乘法和向量更新。

## 对 validation 的意义

`greenbea` 应该保留在 validation / benchmark 体系中，而不是删除。

推荐记录规则：

| 场景 | 记录方式 |
|---|---|
| CPU 达到 `OPTIMAL` | 作为 baseline success 记录 |
| GPU 达到 `OPTIMAL` | 记录 status、iteration、solve time、feasibility、gap |
| GPU 达到 wall-clock timeout | 记录为 convergence-sensitive timeout，不记为缺失数据 |
| GPU 发生 context/runtime failure | 单独记录为环境或运行时错误 |
| feasibility/gap 明显不同 | 保留 JSON 和 log 用于轨迹分析 |

## 不应该做的表述

不要说：

- “`greenbea` 证明 ROCm 是错的。”
- “`greenbea` 证明 CUDA 是错的。”
- “`greenbea` timeout，所以应该从 benchmark 删除。”
- “CPU 和 GPU iteration count 必须一致。”

更合适的表述是：

- “`greenbea` 是 CPU、CUDA、ROCm/HIP 轨迹不同的收敛敏感 case。”
- “该 case 对后续数值分析有价值。”
- “timeout 结果应保留，因为它体现了后端行为差异。”

## 后续分析建议

后续不要只通过增加 time limit 来处理 `greenbea`。更有价值的是收集 trajectory-level diagnostics。

建议后续工作：

1. 增加定期 logging，记录 primal feasibility、dual feasibility 和 relative duality gap；
2. 在固定 iteration checkpoint 比较 CPU、CUDA、ROCm/HIP 轨迹；
3. 如果可行，记录 restart / step-size 变化；
4. 比较 average iterate 与 last iterate 的 termination 行为；
5. 分别记录 sparse matrix-vector time 与 vector update time；
6. 测试 ROCm fused update kernel 是否影响 `greenbea` 轨迹；
7. 设计 checkpoint benchmark，而不是只依赖 end-of-run JSON；
8. 跨设备比较仍保留 3600 秒 wall-clock policy。

## 建议保留的数据

每次长 `greenbea` run 建议保留：

- solver JSON 输出；
- stdout/stderr log；
- shell exit code；
- 运行环境摘要；
- CPU/GPU 型号；
- ROCm 或 CUDA 版本；
- commit SHA；
- case timeout；
- `nIterLim`；
- feasibility 和 duality gap 字段。

## 与 ROCm profiling 的关系

`greenbea` 的主要价值是数值行为分析，不一定适合作为快速 tuning benchmark。

但是，在后续 W7900 或大规模 MPS 实验中，仍可以对 `greenbea` 或类似 long-running case 做 profiling，关注：

- SpMV kernel 占比；
- vector update kernel 占比；
- memory copy 次数和耗时；
- synchronization 次数；
- HIP runtime API 时间；
- kernel launch overhead；
- long-run 中各类操作占比是否随 iteration 增加保持稳定。

需要注意，profiling 本身会引入额外开销，因此 profiling run 与普通 benchmark run 应分开记录。

## 与大规模 MPS 实验的关系

`greenbea` 提醒我们：大规模 LP benchmark 不应该只看最终 solve time，还应保留数值状态字段。

后续引入 H100 上的大规模 MPS 数据集、以及迁移到 Radeon PRO W7900 后，应对大规模 case 分层：

| 层级 | 用途 |
|---|---|
| medium-large | 可在较短时间内完成，用于跨设备比较 |
| large | 用于展示 GPU 计算优势 |
| stress | 用于数值行为和长时间运行分析 |
| convergence-sensitive | 单独记录轨迹，不简单归入 pass/fail |

## 总结

`greenbea` 被保留为数值行为诊断 case。

它的价值在于提醒我们：ROCm/HIP 移植项目不能只用“能否构建”和“quick case 是否 OPTIMAL”评价，还必须关注长时间运行、收敛敏感实例上的轨迹差异。

当前项目立场是：

> ROCm/HIP 后端已经能在 Radeon 890M 上求解 broad validation set 中的大多数 case；`greenbea` 仍是一个收敛敏感长 case，其 timeout 行为应被记录为后续数值分析证据，而不是隐藏为普通失败样例。
