# W7900 P11 SpMV algorithm sweep 汇总

运行目录：`/app/cupdlp_w7900/results/w7900_p11_spmv_alg_sweep_20260616_222054`

本次 P11 sweep 评估如下提交引入的 opt-in HIP SpMV algorithm switch：

- `d1c2465 tuning: add opt-in HIP SpMV algorithm switch`

模式：

- `csr_alg2`：默认行为，不设置 `CUPDLP_HIP_SPMV_ALG`
- `env_default`：`CUPDLP_HIP_SPMV_ALG=default`
- `csr_alg1`：`CUPDLP_HIP_SPMV_ALG=csr_alg1`

Case：

- `L2CTA3D`
- `set-cover-model`
- `square41`
- `thk_48`
- `tpl-tub-ws1617`

原始日志继续保留在 `/app/cupdlp_w7900/results`，不提交到 Git。

## 正确性与稳定性

- 15 个 run 全部 exit code 为 0：`True`
- 每个 case 在三种 mode 下 solver status 稳定：`True`
- 每个 case 在三种 mode 下迭代数稳定：`True`

## 求解时间对比

| case | status stable | nIter stable | csr_alg2 solve s | env_default solve s | csr_alg1 solve s | best solve mode | csr_alg1 / csr_alg2 | env_default / csr_alg2 |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| L2CTA3D | True | True | 4.917409e-01 | 5.051799e-01 | 4.932051e-01 | csr_alg2 | 1.002978 | 1.027329 |
| set-cover-model | True | True | 11.493450 | 11.362370 | 11.333480 | csr_alg1 | 9.860816e-01 | 9.885952e-01 |
| square41 | True | True | 106.490500 | 106.729000 | 106.138100 | csr_alg1 | 9.966908e-01 | 1.002240 |
| thk_48 | True | True | 68.087580 | 68.261270 | 68.027230 | csr_alg1 | 9.991136e-01 | 1.002551 |
| tpl-tub-ws1617 | True | True | 97.543020 | 97.946200 | 97.444810 | csr_alg1 | 9.989932e-01 | 1.004133 |
| geomean | — | — | — | — | — | — | 9.967549e-01 | 1.004892 |

## 解释

三种 SpMV algorithm mode 在 P10 的五个 targeted case 上都保持了 solver status 和迭代数一致。按单次 solve time 看，`csr_alg1` 在 5 个 case 中有 4 个最快，而默认 `csr_alg2` 在短 case `L2CTA3D` 上略快。`csr_alg1 / csr_alg2` 的 solve-time 几何平均低于 1.0，但幅度很小。因此这应被写成“有希望的实验结果”，不能直接写成最终性能结论。

下一步可以选择重复 sweep 估计运行噪声，或者对更有代表性的 `csr_alg1` vs `csr_alg2` 做 rocprofv3 对比，优先 case 为 `set-cover-model`、`square41`、`thk_48`、`tpl-tub-ws1617`。

## 文件

- `w7900_p11_spmv_alg_sweep_20260617.csv`
