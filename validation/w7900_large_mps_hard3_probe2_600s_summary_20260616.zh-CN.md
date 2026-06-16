# W7900 large-MPS hard3 probe2 600s 摘要

结果目录：`/app/cupdlp_w7900/results/w7900_large_mps_hard3_probe2_600s_20260616_180208`

本文是 W7900 hard3 probe2 诊断运行的 compact summary。该运行使用 600 秒 solver time limit，并将 hard case 与 non-hard23 large-MPS 主 baseline 分开跟踪。

## 外层运行摘要

| case | status | exit_code | wall_seconds |
|---|---|---|---|
| dlr1.mps | DONE | 0 | 645.180829 |
| fhnw-binschedule1.mps | DONE | 0 | 614.012251 |

## 求解器摘要

| case | runtime_status | exit_code | wall_seconds | terminationCode | nIter | dSolvingTime | DeviceMatVecProdTime | dRelPrimalFeas | dRelDualFeas | dRelDualityGap |
|---|---|---|---|---|---|---|---|---|---|---|
| dlr1 | DONE | 0 | 645.180829 | TIMELIMIT_OR_ITERLIMIT | 76724 | 600.005066 | 0.500722 | 2.89095896012908 | 3.79388430029909 | 0.28406864922219 |
| fhnw-binschedule1 | DONE | 0 | 614.012251 | TIMELIMIT_OR_ITERLIMIT | 25985 | 600.013012 | 0.249548 | 6.590635427e-05 | 0.0 | 0.39159839307069 |

## 结果解释

- `dlr1` 和 `fhnw-binschedule1` 都达到 600 秒 solver time limit。
- `dlr1` 的 relative duality gap 约为 `0.284`，relative primal / dual infeasibility 仍然较大；在 600 秒 probe 下并未接近收敛。
- `fhnw-binschedule1` 的 primal infeasibility 较小、dual infeasibility 为 0，但 relative duality gap 仍约为 `0.392`；在 600 秒 probe 下同样没有接近 OPTIMAL termination。
- 这两个 case 继续作为 hard case 单独跟踪，不混入 non-hard23 主 baseline。
- 根据本次 probe，不建议立即加时到 1800 秒；应先完成 W7900-specific tuning 或后续更有针对性的诊断。

## 仓库策略

只提交 compact CSV 和 Markdown summary。raw large-MPS 文件和大型中间结果目录保存在 Git 外部。
