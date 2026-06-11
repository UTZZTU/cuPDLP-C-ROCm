# W7900 smoke validation 汇总 20260611

> English: [w7900_smoke_summary_20260611.md](w7900_smoke_summary_20260611.md)

CSV 来源: [w7900_smoke_summary_20260611.csv](w7900_smoke_summary_20260611.csv)

生成结果目录: `validation/results/w7900_smoke_20260611_162123`

本 smoke validation 在 W7900 / `gfx1100` 上运行仓库 smoke case list：`afiro` 和 `sc50b`。

| case | 结果 | CPU 状态 | ROCm/W7900 状态 | CPU 迭代 | ROCm 迭代 | CPU rel primal | ROCm rel primal | CPU rel dual | ROCm rel dual | CPU rel gap | ROCm rel gap |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| afiro | PASS | OPTIMAL/FEASIBLE/FEASIBLE | OPTIMAL/FEASIBLE/FEASIBLE | 199 | 199 | 3.926084712e-05 | 3.927125321e-05 | 5.66716996e-06 | 5.655315e-06 | 7.607918754e-05 | 7.604444646e-05 |
| sc50b | PASS | OPTIMAL/FEASIBLE/FEASIBLE | OPTIMAL/FEASIBLE/FEASIBLE | 560 | 560 | 5.263803303e-05 | 1.038226622e-05 | 7.615967577e-05 | 2.016543289e-05 | 4.26642561e-05 | 3.368112311e-05 |

## 计数

```text
PASS: 2
INCOMPLETE: 0
FAIL: 0
```

## 解释

本次 W7900 运行遵循仓库 validation 语义：CPU 作为 baseline，ROCm/W7900 与 CPU 比较 solver status；对于 OPTIMAL case，再检查 relative primal feasibility、relative dual feasibility 和 relative gap 是否满足容差。
