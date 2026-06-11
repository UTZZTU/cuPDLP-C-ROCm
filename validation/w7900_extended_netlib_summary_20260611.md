# W7900 extended Netlib validation summary 20260611

> 中文: [w7900_extended_netlib_summary_20260611.zh-CN.md](w7900_extended_netlib_summary_20260611.zh-CN.md)

CSV source: [w7900_extended_netlib_summary_20260611.csv](w7900_extended_netlib_summary_20260611.csv)

Generated result directory: `validation/results/w7900_extended_netlib_20260611_162213`

This extended Netlib validation runs `afiro`, `adlittle`, `blend`, `sc50a`, `sc50b`, and `share2b` on W7900 / `gfx1100`.

| case | result | CPU status | ROCm/W7900 status | CPU iter | ROCm iter | CPU rel primal | ROCm rel primal | CPU rel dual | ROCm rel dual | CPU rel gap | ROCm rel gap |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| afiro | PASS | OPTIMAL/FEASIBLE/FEASIBLE | OPTIMAL/FEASIBLE/FEASIBLE | 199 | 199 | 3.926084712e-05 | 3.927125321e-05 | 5.66716996e-06 | 5.655315e-06 | 7.607918754e-05 | 7.604444646e-05 |
| adlittle | PASS | OPTIMAL/FEASIBLE/FEASIBLE | OPTIMAL/FEASIBLE/FEASIBLE | 2400 | 2520 | 1.124043364e-05 | 8.765366263e-05 | 4.255831971e-05 | 3.03931769e-06 | 5.575227294e-05 | 9.749494793e-05 |
| blend | PASS | OPTIMAL/FEASIBLE/FEASIBLE | OPTIMAL/FEASIBLE/FEASIBLE | 1480 | 1360 | 1.116213844e-05 | 9.457719337e-05 | 4.91024373e-06 | 9.14138399e-06 | 1.00249966e-05 | 5.862129422e-05 |
| sc50a | PASS | OPTIMAL/FEASIBLE/FEASIBLE | OPTIMAL/FEASIBLE/FEASIBLE | 600 | 560 | 2.695564409e-05 | 2.567629437e-05 | 1.96724388e-06 | 1.28000175e-06 | 6.919486993e-05 | 1.874509385e-05 |
| sc50b | PASS | OPTIMAL/FEASIBLE/FEASIBLE | OPTIMAL/FEASIBLE/FEASIBLE | 560 | 560 | 5.263803303e-05 | 1.038226622e-05 | 7.615967577e-05 | 2.016543289e-05 | 4.26642561e-05 | 3.368112311e-05 |
| share2b | INCOMPLETE | TIMELIMIT_OR_ITERLIMIT/FEASIBLE/FEASIBLE | TIMELIMIT_OR_ITERLIMIT/FEASIBLE/FEASIBLE | 4999 | 4999 | 0.07349329349144 | 0.10665245903405 | 0.04325215418385 | 0.04044222933488 | 0.01715132394069 | 0.0209386550027 |

## Counts

```text
PASS: 5
INCOMPLETE: 1
FAIL: 0
```

## Interpretation

This W7900 run follows the repository validation policy: CPU is used as the baseline, ROCm/W7900 is compared against CPU by solver status, and OPTIMAL cases are checked against relative primal feasibility, relative dual feasibility, and relative gap thresholds.
