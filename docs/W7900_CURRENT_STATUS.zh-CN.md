# W7900 当前状态与文档修订锚点

> English: [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md)

本文是 W7900 / `gfx1100` 的当前状态锚点，用来替换仓库中较旧的 first-port-only 描述。

## 当前状态

W7900 分支已经不再只是 `afiro` smoke 实验。目前已经具备：

- W7900 first-port build 与 smoke validation。
- W7900 Netlib 27-case baseline。
- W7900 large-MPS `initial17_safe` baseline。
- W7900 large-MPS `non-hard23` baseline。
- 剩余 large-MPS hard cases 单独拆出分析：`dlr1.mps`、`Dual2_5000.mps`、`fhnw-binschedule1.mps`。

## Large-MPS non-hard23 汇总

| Metric | Value |
|---|---|
| Cases | 23 |
| Termination | 23/23 OPTIMAL |
| Source groups | initial17_safe: 17, near_optimal2_1800s: 2, watchlist6_900s: 4 |
| W7900 total wall time | 2960.171 s |
| W7900 total solve time | 2742.940 s |

<!-- W7900_COMPETITIVE_CHARTS_20260614_BEGIN -->
## Per-case 竞争力亮点

non-hard23 aggregate totals 有分析价值，但 W7900 最有说服力的故事是 per-case：W7900 在部分 large-MPS case 上可以接近甚至超过 H100 的 wall time，而慢 case 更适合从收敛行为解释。

![W7900 wall ratio vs H100](assets/w7900/w7900_nonhard23_wall_ratio_vs_h100.svg)

完整竞争力和 case 分类讨论见 [W7900 性能行为分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)。
<!-- W7900_COMPETITIVE_CHARTS_20260614_END -->

## 同 23 个 case 的跨设备参考

| Device | Wall time sum | Solve time sum | Wall vs W7900 | Solve vs W7900 |
|---|---|---|---|---|
| H100 / CUDA | 1701.350 | 1433.577 | 0.57x | 0.52x |
| RTX 3090 / CUDA | 1898.370 | 1513.214 | 0.64x | 0.55x |
| RTX 4090D / CUDA | 2730.760 | 1329.789 | 0.92x | 0.48x |
| W7900 / ROCm | 2960.171 | 2742.940 | 1.00x | 1.00x |
| Radeon 890M / ROCm | 5015.740 | 4842.987 | 1.69x | 1.77x |

![Non-hard23 wall comparison](assets/w7900/w7900_nonhard23_wall_compare.svg)

![Non-hard23 solve comparison](assets/w7900/w7900_nonhard23_solve_compare.svg)

## W7900 最慢 non-hard cases

| Case | Source group | nIter | Wall time | Solve time | Rel gap |
|---|---|---|---|---|---|
| s100 | near_optimal2_1800s | 675400 | 1100.650 | 1098.047 | 9.986063828e-05 |
| Primal2_1000 | near_optimal2_1800s | 1203440 | 1046.038 | 1037.885 | 9.830367122e-05 |
| thk_63 | watchlist6_900s | 73960 | 288.564 | 252.165 | 4.756861046e-05 |
| square41 | watchlist6_900s | 128360 | 115.159 | 106.404 | 9.463231177e-05 |
| tpl-tub-ws1617 | watchlist6_900s | 82600 | 112.519 | 98.123 | 4.13613801e-05 |
| thk_48 | watchlist6_900s | 17720 | 110.058 | 68.336 | 5.213466659e-05 |
| rmine15 | initial17_safe | 15000 | 28.928 | 27.271 | 4.180620533e-05 |
| neos-3025225 | initial17_safe | 6080 | 23.590 | 17.538 | 7.825931282e-05 |
| set-cover-model | initial17_safe | 7480 | 26.926 | 11.464 | 9.3551367e-06 |
| irish-electricity | initial17_safe | 53680 | 9.285 | 8.229 | 1.62842043e-06 |

![W7900 slowest cases](assets/w7900/w7900_nonhard23_slowest_cases.svg)

## 理论价值与应用价值

cuPDLP/PDLP 类求解器面向大规模线性规划问题，其核心操作是稀疏矩阵向量乘法，因此适合 GPU 加速。但总耗时同时取决于单次迭代开销和收敛路径。

对于项目报告，这一阶段的 W7900 工作能够体现：

- 科学计算求解器从 CUDA 到 ROCm 的可复现迁移路径。
- 大显存 AMD 工作站 GPU 面向 large LP/MPS 工作负载的验证流程。
- 基于数据的 safe、slow-but-solvable、hard-case 分层方法。
- 后续 ROCm profiling 与 tuning 的调优前 baseline。

## 为什么 W7900 有些 case 快、有些 case 慢

W7900 具备较高 FP32 峰值、较大显存和较高显存带宽，因此当 case 有足够的稀疏矩阵向量乘工作量并且收敛稳定时，能够发挥硬件优势。但 PDLP 总耗时不只是硬件吞吐问题：

```text
total time ≈ per-iteration cost × number of iterations
```

对于 hard LP instance，稀疏归约、浮点顺序、adaptive restart 时机、step-size 演化、residual/gap 轨迹上的微小差异，都可能改变迭代路径。这可以解释为什么 W7900 在部分 large case 上表现较好，但在 `s100`、`Primal2_1000` 或 hard3 上表现不一定理想。

<!-- W7900_PERFORMANCE_BEHAVIOR_20260614_BEGIN -->
## 相关性能行为分析

关于为什么 W7900 在部分 large-MPS case 上快、在另一些 case 上慢，详见：

- [W7900 performance behavior analysis](W7900_PERFORMANCE_BEHAVIOR.md)
- [W7900 性能行为分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)
<!-- W7900_PERFORMANCE_BEHAVIOR_20260614_END -->

<!-- W7900_ROCM_PROFILING_PLAN_20260614_BEGIN -->
<!-- W7900_OPTIMIZATION_BASELINES_20260614_BEGIN -->
## 优化基线口径说明

当前 W7900 non-hard23 结果不是未优化 first-port baseline，而是继承 890M/gfx1150 调优成果后的 current ROCm/HIP 工程分支在 W7900 / `gfx1100` 上的验证。

详见 [W7900 优化基线说明](W7900_OPTIMIZATION_BASELINES.zh-CN.md)。
<!-- W7900_OPTIMIZATION_BASELINES_20260614_END -->

## ROCm profiling 与调优计划

下一阶段不是盲目改 kernel，而是先固定 profiling case matrix，并记录 wall time、solver time、`DeviceMatVecProdTime`、`nIter`、HIP/kernel trace 和 GPU telemetry。

详见 [W7900 ROCm profiling 计划](W7900_ROCM_PROFILING_PLAN.zh-CN.md)。
<!-- W7900_ROCM_PROFILING_PLAN_20260614_END -->

## 下一步文档任务

1. 更新 `README.md` 和 `README.zh-CN.md`，把 W7900 描述为已经具备 baseline 的验证目标，而不是 planned/first-port-only 状态。
2. 更新 `docs/README.md` 和 validation index，让当前状态页、non-hard23、initial17、watchlist6、near2、hard3 都有清晰入口。
3. 更新 `docs/W7900_FIRST_PORT.md` 和平台记录，补充 bootstrap 与临时机器易丢失的恢复流程。
4. 在正式调优前先补 hard3 note，不把 hard3 混入第一轮主 baseline。
5. 等 W7900 文档状态统一后，再开始 ROCm profiling/tuning。
