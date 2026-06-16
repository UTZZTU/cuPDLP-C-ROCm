# W7900 latest experiment figures

![8-card fast8 makespan](../docs/assets/w7900/latest_experiments/w7900_8card_fast8_makespan.svg)

![before/current fast-core6 solve time](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_solve_time.svg)

![hard3 probe2 relative gap](../docs/assets/w7900/latest_experiments/w7900_hard3_probe2_relative_gap.svg)

![s100 top kernel share](../docs/assets/w7900/latest_experiments/w7900_rocprof_s100_top_kernel_percent.svg)

Key numbers:

- 8-card fast8 concurrent makespan: `146s`.
- Single-GPU sequential fast8 makespan: `558s`.
- Measured batch makespan speedup: `3.82x`.

## Derived before/current ratio figures / 2026-06-17

These two figures extend the fast-core6 before/current analysis by
separating iteration-count changes from per-iteration execution cost.

![W7900 fast-core6 ms/iter ratio](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)

![W7900 fast-core6 iteration ratio](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

Related summary:
[w7900_before_current_core6_fast_derived_metrics_20260617.md](w7900_before_current_core6_fast_derived_metrics_20260617.md)
