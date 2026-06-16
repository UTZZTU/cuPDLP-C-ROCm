# W7900 最新实验图表

![8-card fast8 makespan](../docs/assets/w7900/latest_experiments/w7900_8card_fast8_makespan.svg)

![before/current fast-core6 solve time](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_solve_time.svg)

![hard3 probe2 relative gap](../docs/assets/w7900/latest_experiments/w7900_hard3_probe2_relative_gap.svg)

![s100 top kernel share](../docs/assets/w7900/latest_experiments/w7900_rocprof_s100_top_kernel_percent.svg)

关键数字：

- 8-card fast8 并发 makespan：`146s`。
- 单 GPU 顺序 fast8 makespan：`558s`。
- 实测 batch makespan speedup：`3.82x`。

## before/current 派生比值图 / 2026-06-17

这两张图扩展 fast-core6 before/current 分析，把迭代次数变化和单迭代
执行耗时变化分开展示。

![W7900 fast-core6 单迭代耗时比](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)

![W7900 fast-core6 迭代次数比](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

相关汇总：
[w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md](w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md)
