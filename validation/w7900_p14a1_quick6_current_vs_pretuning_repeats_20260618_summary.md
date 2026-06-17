# W7900 P14-A1 quick6 current vs pre_tuning repeated validation

Result root: `/app/cupdlp_w7900/results/w7900_p14a1_quick6_current_vs_pretuning_20260617_170205`

This experiment repeats the 890M-style quick6 methodology on W7900 / `gfx1100`.
It compares:

- `pre_tuning`: `ae3b683`
- `current`: current `rocm-w7900-gfx1100` HEAD at run time

Each case/version pair is run three times. The main timing metric is median
solve time.

## Aggregate result

- wins where `current` is faster: `6/6`
- geometric mean speedup, `pre_tuning / current`: `1.18889`
- median speedup, `pre_tuning / current`: `1.19502`

A value greater than 1 means `current` is faster.

## Comparison table

| case | pre median solve s | current median solve s | speedup pre/current | pre nIter | current nIter |
|---|---:|---:|---:|---:|---:|
| `80bau3b` | 1.265655 | 1.008045 | 1.25555407 | 7800 | 7800 |
| `afiro` | 0.1074691 | 0.1012969 | 1.06093178 | 200 | 200 |
| `lotfi` | 11.31668 | 8.445734 | 1.33992854 | 85840 | 85840 |
| `maros-r7` | 0.1602161 | 0.144289 | 1.11038333 | 560 | 560 |
| `pilot87` | 12.76718 | 10.20149 | 1.2515015 | 82240 | 82240 |
| `sc50b` | 0.1539228 | 0.1351941 | 1.13853193 | 560 | 560 |

## Interpretation note

This is quick-set tuning-transfer evidence, not a replacement for the large-MPS
baseline. It should be reported separately from non-hard23 large-MPS results.
