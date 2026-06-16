# W7900 before/current fast-core6 摘要

结果目录：`/app/cupdlp_w7900/results/w7900_before_current_core6_900s_core6_fast_900s_20260616_185300`

本文是 W7900 fast-core6 before/current 对比的 compact summary。

对比版本：

- `pre_tuning`：`ae3b683 / pre_tuning`，在 W7900 上通过补充 ROCm Python SDK include path 完成构建。
- `current`：当前 `rocm-w7900-gfx1100` 工程分支。

Fast-core6 case list：

- `set-cover-model.mps`
- `square41.mps`
- `thk_48.mps`
- `tpl-tub-ws1617.mps`
- `L2CTA3D.mps`
- `rmine15.mps`

## 对比结果

| case | current_termination | pre_tuning_termination | current_solve_time | pre_tuning_solve_time | current_over_pre_solve_ratio | pre_over_current_speedup |
|---|---|---|---|---|---|---|
| L2CTA3D | OPTIMAL | OPTIMAL | 0.504093 | 0.385509 | 1.307604 | 0.764758 |
| rmine15 | OPTIMAL | OPTIMAL | 27.384925 | 27.889919 | 0.981893 | 1.018441 |
| set-cover-model | OPTIMAL | OPTIMAL | 11.652169 | 7.449711 | 1.564110 | 0.639341 |
| square41 | OPTIMAL | OPTIMAL | 106.691588 | 110.538147 | 0.965202 | 1.036053 |
| thk_48 | OPTIMAL | OPTIMAL | 68.444947 | 76.277967 | 0.897310 | 1.114443 |
| tpl-tub-ws1617 | OPTIMAL | OPTIMAL | 98.223063 | 55.561147 | 1.767837 | 0.565663 |

## 汇总

- current 按 solve time 取胜：`3/6` 个 case。
- pre_tuning 按 solve time 取胜：`3/6` 个 case。
- 几何平均 current/pre solve-time ratio：`1.205873`。
- 几何平均 pre/current speedup：`0.829274`。

## 结果解释

- 两个版本在 fast-core6 的 6 个 case 上都达到 `OPTIMAL`。
- 当前工程分支在这个 fast subset 上并非全面快于 `ae3b683 / pre_tuning`。
- 这轮结果应作为真实 before/current 工程对比，而不能写成笼统的 W7900 加速结论。
- 该混合结果进一步说明后续 W7900-specific profiling 和 tuning 是必要的。
- `s100` 和 `Primal2_1000` 因已知 W7900 运行时间较长，被有意排除在本次 fast-core6 之外，以适配当前实验时间窗口。

## 仓库策略

只提交 compact CSV 和 Markdown summary。raw large-MPS 文件和大型运行目录保存在 Git 外部。

## 派生每迭代分析 / 2026-06-17

后续派生分析已经补充：

- [派生指标中文汇总](w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md)
- [派生指标 CSV](w7900_before_current_core6_fast_derived_metrics_20260617.csv)
- [单迭代耗时比图](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)
- [迭代次数比图](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

派生指标显示，current 在 6 个 case 上均降低了 ms/iter，但由于部分
case 需要更多迭代，总 solve time 仍呈 mixed pattern。这说明下一阶段
调优应保留执行效率收益，同时检查收敛行为变化。
