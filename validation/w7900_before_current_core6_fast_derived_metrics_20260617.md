# W7900 before/current fast-core6 derived metrics

Source files:

- `validation/w7900_before_current_core6_fast_current_solver_20260616.csv`
- `validation/w7900_before_current_core6_fast_pre_tuning_solver_20260616.csv`

This derived table separates total solve time into iteration count and per-iteration execution time.

## Summary

- Correctness status remains unchanged: all six cases are `OPTIMAL` in both runs.
- `current` has lower ms/iter on 6/6 cases.
- `current` has lower total solve time on 3/6 cases.
- `current` has higher iteration count on 4/6 cases.
- Geomean current/pre solve-time ratio: `1.20587`.
- Geomean current/pre iteration ratio: `1.34686`.
- Geomean current/pre ms-per-iteration ratio: `0.89532`.

## Derived table

| case | iter ratio | solve ratio | ms/iter ratio | current ms/iter | pre ms/iter | interpretation |
|---|---|---|---|---|---|---|
| L2CTA3D | 2 | 1.3076 | 0.653802 | 6.30116 | 9.63772 | current lower ms/iter, but higher iteration count makes total solve time worse |
| rmine15 | 1 | 0.981893 | 0.981893 | 1.82566 | 1.85933 | current improves both ms/iter and total solve time |
| set-cover-model | 1.58475 | 1.56411 | 0.986979 | 1.55778 | 1.57833 | current lower ms/iter, but higher iteration count makes total solve time worse |
| square41 | 1 | 0.965202 | 0.965202 | 0.83119 | 0.861157 | current improves both ms/iter and total solve time |
| thk_48 | 1.01606 | 0.89731 | 0.883131 | 3.86258 | 4.37374 | current improves both ms/iter and total solve time |
| tpl-tub-ws1617 | 1.85368 | 1.76784 | 0.95369 | 1.18914 | 1.24688 | current lower ms/iter, but higher iteration count makes total solve time worse |

## Interpretation

The current W7900/gfx1100 branch keeps fast-core6 correctness stable, but performance remains mixed. The derived metrics show that per-iteration execution time improved on all six cases, while iteration count increased on four cases. Therefore, the next tuning stage should not be framed as pure kernel optimization only. It should preserve the execution-layer gains while investigating why convergence iteration count increased on cases such as `L2CTA3D`, `set-cover-model`, and `tpl-tub-ws1617`.

## Figures

- `../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg`
- `../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg`
