# W7900 P14-A1 quick6 current vs pre_tuning repeated validation

结果目录：`/app/cupdlp_w7900/results/w7900_p14a1_quick6_current_vs_pretuning_20260617_170205`

本实验在 W7900 / `gfx1100` 上复用 890M-style quick6 方法论，对比：

- `pre_tuning`：`ae3b683`
- `current`：运行时当前 `rocm-w7900-gfx1100` HEAD

每个 case/version 组合重复运行 3 次。主计时指标为 median solve time。

## 汇总结果

- `current` 更快的 case 数：`6/6`
- 几何平均 speedup，`pre_tuning / current`：`1.18889`
- 中位数 speedup，`pre_tuning / current`：`1.19502`

大于 1 表示 `current` 更快。

## 对比表

| case | pre median solve s | current median solve s | speedup pre/current | pre nIter | current nIter |
|---|---:|---:|---:|---:|---:|
| `80bau3b` | 1.265655 | 1.008045 | 1.25555407 | 7800 | 7800 |
| `afiro` | 0.1074691 | 0.1012969 | 1.06093178 | 200 | 200 |
| `lotfi` | 11.31668 | 8.445734 | 1.33992854 | 85840 | 85840 |
| `maros-r7` | 0.1602161 | 0.144289 | 1.11038333 | 560 | 560 |
| `pilot87` | 12.76718 | 10.20149 | 1.2515015 | 82240 | 82240 |
| `sc50b` | 0.1539228 | 0.1351941 | 1.13853193 | 560 | 560 |

## 解释说明

这是 quick-set tuning-transfer evidence，不替代 large-MPS baseline。它应与
non-hard23 large-MPS 结果分开表述。
