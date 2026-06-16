# W7900 P11 default SpMV ALG1 smoke 汇总

本次 validation 检查 P11 默认策略更新：

- commit：`2643849 tuning: default HIP SpMV algorithm to CSR ALG1`
- 新默认：`HIPSPARSE_SPMV_CSR_ALG1`
- 回退模式：`CUPDLP_HIP_SPMV_ALG=csr_alg2`
- case：`set-cover-model`

原始日志继续保留在 `/app/cupdlp_w7900/results`，不提交到 Git。

## 结果

- 两次运行 exit code 均为 0：`True`
- 两次运行均报告 `Optimal current solution`：`True`
- 两次运行迭代数一致：`True`
- 两次运行保持 primal 和 dual objective 一致：`True`

## Smoke 表

| mode | exit | status | nIter | solve s | total s | primal rel infeas | dual rel infeas | rel gap |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| default_csr_alg1 | 0 | Optimal current solution. | 7480 | 1.145234e+01 | 1.277736e+01 | 9.81e-05 | 0.00e+00 | 9.36e-06 |
| rollback_csr_alg2 | 0 | Optimal current solution. | 7480 | 1.134371e+01 | 1.262357e+01 | 9.81e-05 | 0.00e+00 | 9.36e-06 |

## 解释

新的 SpMV 默认策略通过了短 smoke validation。当前默认无环境变量路径使用 `csr_alg1`，旧默认仍可通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 恢复。

本 smoke 是正确性和回退能力检查，不是性能结论。选择 `csr_alg1` 作为当前 W7900 默认策略的主要依据仍然是前面的 P11 五 case sweep。

## 文件

- `w7900_p11_default_spmv_alg1_smoke_20260617.csv`
