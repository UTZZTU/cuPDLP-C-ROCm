# W7900 P11 SpMV algorithm switch smoke 汇总

本次 smoke validation 检查第一个真正的 P11 tuning patch：

- commit：`d1c2465 tuning: add opt-in HIP SpMV algorithm switch`
- case：`set-cover-model`
- 默认行为：`HIPSPARSE_SPMV_CSR_ALG2`
- opt-in 模式：
  - `CUPDLP_HIP_SPMV_ALG=default`
  - `CUPDLP_HIP_SPMV_ALG=csr_alg1`

原始日志继续保留在 `/app/cupdlp_w7900/results`，不提交到 Git。

## 结果

- 所有运行 exit code 均为 0：`True`
- 所有运行均报告 `Optimal current solution`：`True`
- 所有运行迭代数一致：`True`
- 观察到的迭代数：`7480`

## 聚合时间

| mode | runs | exitcodes | status | nIter | mean solve s | min solve s | max solve s | mean total s | mean UpdateIterates s |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| default | 2 | 0 | Optimal current solution. | 7480 | 11.326795 | 11.319240 | 11.334350 | 12.609330 | 10.539820 |
| env_default | 2 | 0 | Optimal current solution. | 7480 | 11.391860 | 11.305140 | 11.478580 | 12.690090 | 10.552390 |
| csr_alg1 | 2 | 0 | Optimal current solution. | 7480 | 11.357640 | 11.348970 | 11.366310 | 12.644165 | 10.551835 |

## 解释

opt-in SpMV algorithm switch 在 `set-cover-model` 上通过初始 smoke validation。三种模式均保持 solver status、迭代数、目标值、primal infeasibility、dual infeasibility 和 duality gap 一致。本次小规模 smoke 中的时间差异范围较窄，暂时不能作为性能结论。

因此该 patch 适合进入更完整的 P11 sweep。下一步应在 P10 的五个 targeted cases 上比较 `default`、`csr_alg1` 和默认 `csr_alg2` 模式，即 `L2CTA3D`、`set-cover-model`、`square41`、`thk_48`、`tpl-tub-ws1617`。

## 文件

- `w7900_p11_spmv_alg_switch_smoke_20260617.csv`
