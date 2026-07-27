# W7900 性能行为分析

> English: [W7900_PERFORMANCE_BEHAVIOR.md](W7900_PERFORMANCE_BEHAVIOR.md)

本文解释当前 W7900 / `gfx1100` 的性能行为，不只是重复 benchmark 表格。它用于支撑后续比赛报告和 ROCm profiling/tuning。

## 本文补充什么

当前 W7900 证据已经不只是“代码能跑”。分支已经有可复现的 23-case non-hard large-MPS baseline，并且把困难收敛行为拆成 hard3 单独处理。

本文补充三点：

1. 理论价值：为什么 PDLP 类 LP 求解器适合 GPU 加速；
2. 应用价值：为什么 W7900 对 large LP/MPS 工作负载有意义；
3. 性能解释：为什么有些 case 快，有些 case 慢或 hard。

## 硬件与求解器解释

W7900 对 large LP/MPS 有吸引力，是因为它同时具备较高 FP32 吞吐、48GB GDDR6 显存、384-bit 显存接口、864GB/s 峰值显存带宽和 ECC 支持。这些特性适合反复访问大规模稀疏矩阵和稠密向量的求解器。

但是，PDLP 总时间不能只理解成 GPU 算力：

```text
total time ≈ per-iteration cost × number of iterations
```

单次迭代成本与稀疏矩阵向量乘、向量操作、归约和数据移动相关。迭代次数则由数值路径决定：residual、duality gap、step-size 演化、scaling、restart 和问题条件数都会影响收敛。

## Non-hard23 结果汇总

| 指标 | 数值 |
|---|---|
| Case 数量 | 23 |
| Termination | 23/23 OPTIMAL |
| Total wall time | 2960.171 s |
| Total solve time | 2742.940 s |
| Total DeviceMatVecProdTime | 10.176 s |

<!-- W7900_COMPETITIVE_CHARTS_20260614_BEGIN -->
## W7900 与 H100 / CUDA 参考的竞争力

之前的 aggregate solve-time 图适合分析瓶颈，但容易掩盖 W7900 在许多单个 large-MPS case 上已经具备竞争力这一点。因此下面改用 per-case wall time 展示 W7900 在哪些 case 上接近或超过高端参考设备。

### W7900 vs H100 per-case wall-time ratio

数值大于 1.0 表示 W7900 在该 case 上比 H100 更快。

| Case | W7900 wall | H100 wall | H100/W7900 |
|---|---|---|---|
| supportcase10 | 5.47 | 13.26 | 2.42x |
| square41 | 115.16 | 245.92 | 2.14x |
| datt256_lp | 2.49 | 4.02 | 1.61x |
| a2864 | 14.31 | 20.20 | 1.41x |
| set-cover-model | 26.93 | 34.74 | 1.29x |
| scpm1 | 5.67 | 7.07 | 1.25x |
| L2CTA3D | 44.85 | 55.57 | 1.24x |
| ex10 | 1.34 | 1.63 | 1.22x |
| savsched1 | 2.51 | 2.96 | 1.18x |
| woodlands09 | 2.97 | 3.24 | 1.09x |
| neos-5251015 | 2.67 | 2.81 | 1.05x |
| graph40-40 | 2.27 | 2.35 | 1.04x |

![W7900 wall ratio vs H100](assets/w7900/w7900_nonhard23_wall_ratio_vs_h100.svg)

### 竞争力分段

| 参考设备 | W7900 更快 | 1.5x 内接近 | 超过 1.5x 较慢 |
|---|---|---|---|
| H100 | 12 | 6 | 5 |
| RTX 4090D | 19 | 2 | 2 |
| RTX 3090 | 13 | 5 | 5 |
| Radeon 890M | 17 | 4 | 2 |

![W7900 competitiveness bands](assets/w7900/w7900_nonhard23_competitiveness_bands.svg)

### 代表 case 对比

这张图刻意同时包含 W7900 表现强的 case 和 slow-but-solvable case。相比只看 aggregate totals，这种叙事更适合比赛展示，因为它把硬件竞争力和收敛敏感 case 区分开。

![Representative wall comparison](assets/w7900/w7900_nonhard23_representative_wall_compare.svg)

![Representative solve comparison](assets/w7900/w7900_nonhard23_representative_solve_compare.svg)
<!-- W7900_COMPETITIVE_CHARTS_20260614_END -->

## W7900 相对 890M 的加速

下表和图使用 solve time，更接近 solver 计算本身，而不是端到端 wall time。

| Case | 890M solve | W7900 solve | Speedup | Source group |
|---|---|---|---|---|
| set-cover-model | 148.037 | 11.464 | 12.91x | initial17_safe |
| thk_48 | 695.568 | 68.336 | 10.18x | watchlist6_900s |
| a2864 | 11.609 | 1.577 | 7.363x | initial17_safe |
| scpm1 | 4.944 | 0.707 | 6.994x | initial17_safe |
| neos-5052403-cygnet | 15.138 | 2.776 | 5.454x | initial17_safe |
| square41 | 562.727 | 106.404 | 5.289x | watchlist6_900s |
| woodlands09 | 1.590 | 0.306 | 5.190x | initial17_safe |
| tpl-tub-ws1617 | 467.122 | 98.123 | 4.761x | watchlist6_900s |
| L2CTA3D | 2.339 | 0.497 | 4.703x | initial17_safe |
| savsched1 | 0.972 | 0.238 | 4.079x | initial17_safe |
| neos-5251015 | 1.408 | 0.363 | 3.879x | initial17_safe |
| irish-electricity | 26.884 | 8.229 | 3.267x | initial17_safe |

![W7900 speedup vs 890M](assets/w7900/w7900_nonhard23_speedup_vs_890m.svg)

## W7900 相对最佳 CUDA 参考

数值大于 1 表示 W7900 在该 case 上快于最佳 CUDA 参考；小于 1 表示最佳 CUDA 参考更快。

![W7900 relative to best CUDA](assets/w7900/w7900_nonhard23_relative_to_best_cuda.svg)

## Case 分类

![W7900 case classes](assets/w7900/w7900_nonhard23_case_classes.svg)

| Case | 类别 | nIter | W7900 solve time | Rel gap |
|---|---|---|---|---|
| s100 | slow-but-solvable (>120s) | 675400 | 1098.047 | 9.986063828e-05 |
| Primal2_1000 | slow-but-solvable (>120s) | 1203440 | 1037.885 | 9.830367122e-05 |
| thk_63 | slow-but-solvable (>120s) | 73960 | 252.165 | 4.756861046e-05 |
| square41 | medium (10-120s) | 128360 | 106.404 | 9.463231177e-05 |
| tpl-tub-ws1617 | medium (10-120s) | 82600 | 98.123 | 4.13613801e-05 |
| thk_48 | medium (10-120s) | 17720 | 68.336 | 5.213466659e-05 |
| rmine15 | medium (10-120s) | 15000 | 27.271 | 4.180620533e-05 |
| neos-3025225 | medium (10-120s) | 6080 | 17.538 | 7.825931282e-05 |
| set-cover-model | medium (10-120s) | 7480 | 11.464 | 9.3551367e-06 |
| irish-electricity | fast (<10s) | 53680 | 8.229 | 1.62842043e-06 |
| s250r10 | fast (<10s) | 5240 | 5.121 | 5.357990561e-05 |
| supportcase10 | fast (<10s) | 23800 | 4.481 | 9.776586066e-05 |
| neos-5052403-cygnet | fast (<10s) | 8640 | 2.776 | 9.375217334e-05 |
| a2864 | fast (<10s) | 1400 | 1.577 | 2.844014065e-05 |
| datt256_lp | fast (<10s) | 520 | 0.730 | 5.77976796e-05 |
| scpm1 | fast (<10s) | 1320 | 0.707 | 9.490131535e-05 |
| L2CTA3D | fast (<10s) | 80 | 0.497 | 1.005417564e-05 |
| qap15 | fast (<10s) | 2840 | 0.449 | 4.56259611e-06 |
| neos-5251015 | fast (<10s) | 800 | 0.363 | 5.393595963e-05 |
| woodlands09 | fast (<10s) | 800 | 0.306 | 7.699777596e-05 |
| savsched1 | fast (<10s) | 520 | 0.238 | 7.879146734e-05 |
| ex10 | fast (<10s) | 280 | 0.127 | 4.524774349e-05 |
| graph40-40 | fast (<10s) | 80 | 0.105 | 3.326118142e-05 |

## W7900 更适合什么类型的数据

当前数据表明，W7900 更适合：

- 规模足够大，能够摊薄 HIP setup、文件解析、矩阵搬运和 launch 固定开销的 case；
- 收敛轨迹稳定，迭代次数不会极端膨胀的 case；
- SpMV 和向量操作占比较高，能够利用显存带宽和并行度的 case；
- 显存占用较大、需要 48GB VRAM 和 ECC 支持的工作负载。

## 为什么有些 case 慢

W7900 上某个 case 慢，不一定说明 GPU 算得慢，可能是：

- LP instance 需要大量 PDLP 迭代；
- gap trajectory 在阈值附近停滞；
- adaptive restart 或 step-size 在不同硬件/后端上的路径不同；
- reduction 或 sparse operation 暴露出 ROCm/gfx1100 kernel 效率问题；
- tiny case 中固定开销占主导。

<!-- W7900_OPTIMIZATION_BASELINES_20260614_BEGIN -->
## Baseline 口径修正

W7900 non-hard23 结果应理解为 post-890M-tuning engineering baseline，不应作为未来 before/after 分析里的“调优前 baseline”。真正的 pre-tuning anchor 是 `ae3b683`。

详见 [W7900 优化基线说明](W7900_OPTIMIZATION_BASELINES.zh-CN.md)。
<!-- W7900_OPTIMIZATION_BASELINES_20260614_END -->

## 调优启示与当前终点

已完成证据表明，W7900 tuning 必须联合考虑 kernel 成本和数值轨迹：

- 记录 per-case `nIter`；
- 保留 residual 与 gap 检查；
- 观察 `DeviceMatVecProdTime`；
- 使用 HIP API 与 kernel profiles；
- 比较相同 case list 与 limits；
- hard3 保持单独分组。

P10 识别出 rocSPARSE CSR SpMV 是主要 targeted hotspot。P11 接受 `HIPSPARSE_SPMV_CSR_ALG1` 作为当前默认，并保留 `csr_alg2` 回退。P12 因迭代数变化拒绝相关 execution-layer 修改。P14-A1 随后确认 repeated current-vs-pre-tuning 收益且迭代数不变。

因此当前项目终点是有证据支撑的 SpMV policy，而不是声称已经消除所有 ROCm 瓶颈。未来 tuning 只有在提出新的测量问题并预先定义验证方案后才应开始。
