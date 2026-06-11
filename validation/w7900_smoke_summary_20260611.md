# W7900 smoke validation summary 20260611

> 中文: [w7900_smoke_summary_20260611.zh-CN.md](w7900_smoke_summary_20260611.zh-CN.md)

CSV source: [w7900_smoke_summary_20260611.csv](w7900_smoke_summary_20260611.csv)

Generated result directory: `validation/results/w7900_smoke_20260611_162123`

This smoke validation runs the repository smoke case list on W7900 / `gfx1100`: `afiro` and `sc50b`.

| case | result | CPU status | ROCm/W7900 status | CPU iter | ROCm iter | CPU rel primal | ROCm rel primal | CPU rel dual | ROCm rel dual | CPU rel gap | ROCm rel gap |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| afiro | PASS | OPTIMAL/FEASIBLE/FEASIBLE | OPTIMAL/FEASIBLE/FEASIBLE | 199 | 199 | 3.926084712e-05 | 3.927125321e-05 | 5.66716996e-06 | 5.655315e-06 | 7.607918754e-05 | 7.604444646e-05 |
| sc50b | PASS | OPTIMAL/FEASIBLE/FEASIBLE | OPTIMAL/FEASIBLE/FEASIBLE | 560 | 560 | 5.263803303e-05 | 1.038226622e-05 | 7.615967577e-05 | 2.016543289e-05 | 4.26642561e-05 | 3.368112311e-05 |

## Counts

```text
PASS: 2
INCOMPLETE: 0
FAIL: 0
```

## Interpretation

This W7900 run follows the repository validation policy: CPU is used as the baseline, ROCm/W7900 is compared against CPU by solver status, and OPTIMAL cases are checked against relative primal feasibility, relative dual feasibility, and relative gap thresholds.
