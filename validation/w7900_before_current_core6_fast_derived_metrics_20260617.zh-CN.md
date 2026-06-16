# W7900 before/current fast-core6 派生指标

来源文件：

- `validation/w7900_before_current_core6_fast_current_solver_20260616.csv`
- `validation/w7900_before_current_core6_fast_pre_tuning_solver_20260616.csv`

本表把总求解时间拆成“迭代次数”和“每迭代执行耗时”，用于避免只看 solve time 得出片面结论。

## 总结

- 正确性状态保持不变：6 个 case 在两组运行中均为 `OPTIMAL`。
- `current` 在 6/6 个 case 上降低了 ms/iter。
- `current` 在 3/6 个 case 上降低了总 solve time。
- `current` 在 4/6 个 case 上迭代数增加。
- current/pre solve-time 几何平均比值：`1.20587`。
- current/pre iteration 几何平均比值：`1.34686`。
- current/pre ms-per-iteration 几何平均比值：`0.89532`。

## 派生表

| case | 迭代数比 | 求解时间比 | 单迭代耗时比 | current ms/iter | pre ms/iter | 解释 |
|---|---|---|---|---|---|---|
| L2CTA3D | 2 | 1.3076 | 0.653802 | 6.30116 | 9.63772 | current 单迭代更快，但迭代数增加使总求解时间变差 |
| rmine15 | 1 | 0.981893 | 0.981893 | 1.82566 | 1.85933 | current 同时改善单迭代耗时和总求解时间 |
| set-cover-model | 1.58475 | 1.56411 | 0.986979 | 1.55778 | 1.57833 | current 单迭代更快，但迭代数增加使总求解时间变差 |
| square41 | 1 | 0.965202 | 0.965202 | 0.83119 | 0.861157 | current 同时改善单迭代耗时和总求解时间 |
| thk_48 | 1.01606 | 0.89731 | 0.883131 | 3.86258 | 4.37374 | current 同时改善单迭代耗时和总求解时间 |
| tpl-tub-ws1617 | 1.85368 | 1.76784 | 0.95369 | 1.18914 | 1.24688 | current 单迭代更快，但迭代数增加使总求解时间变差 |

## 解释

当前 W7900/gfx1100 分支在 fast-core6 上保持正确性稳定，但性能仍是 mixed pattern。派生指标显示，6 个 case 的单迭代执行耗时全部下降，但 4 个 case 的迭代次数增加。因此下一阶段不应只按“kernel 越快越好”的单线叙事推进，而应保留执行层收益，同时追查 `L2CTA3D`、`set-cover-model`、`tpl-tub-ws1617` 等 case 的收敛迭代数为什么增加。

## 图表

- `../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg`
- `../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg`
