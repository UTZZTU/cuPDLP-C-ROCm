# W7900 P11 SpMV tuning 总结

本文档用于收尾 P11 的 W7900-specific SpMV 调优闭环。

## 动机

P10 targeted profiling 显示，在所选 W7900 case 上，rocSPARSE CSR SpMV
是主要 GPU kernel 热点；同时 HIP API trace 也显示 host-device copy 压力
明显。由于 copy reduction 可能影响 residual、restart 或 termination 逻辑，
P11 首先选择了更安全的执行层实验：SpMV algorithm selection。

## 改了什么

P11 围绕已有 generic `hipsparseSpMV` 调用增加了 opt-in HIP SpMV
algorithm switch：

- P11-8-lite 之前的默认模式：`HIPSPARSE_SPMV_CSR_ALG2`
- opt-in 实验：`CUPDLP_HIP_SPMV_ALG=default`
- opt-in 实验：`CUPDLP_HIP_SPMV_ALG=csr_alg1`
- 默认策略更新后的回退：`CUPDLP_HIP_SPMV_ALG=csr_alg2`

最终当前 W7900 默认策略已切换为 `HIPSPARSE_SPMV_CSR_ALG1`。

## 证据链

1. `f1fe620` 添加 P10 targeted rocprof summaries。
2. `28f3796` 添加 P11 runtime callsite inventory。
3. `f48b5fd` 排序 first-patch candidates。
4. `d1c2465` 增加 opt-in HIP SpMV algorithm switch。
5. `48b1ad9` 在 `set-cover-model` 上验证 switch。
6. `6ccf722` 完成五 case、三 mode SpMV sweep。
7. `2643849` 将 W7900 默认策略改为 CSR ALG1。
8. `0649024` 验证新默认和 CSR ALG2 回退路径。

## 最终解释

P11 应表述为一个保守的 W7900 tuning policy update：

- 没有主动改变 solver 数值路径。
- 五 case sweep 中 solver status 和迭代数保持稳定。
- `csr_alg1` 在多数长 targeted case 上表现出小幅有利倾向。
- 幅度较小，因此不能写成最终性能结论。
- 旧默认可以通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 显式恢复。

## 下一步建议

在时间有限的情况下，P11 可以视为完成。下一步更适合做文档/报告整合，
而不是继续跑长 profiling。如果后续还有调优时间，再进入更谨慎的 scalar-copy
分析，并明确验证 residual、restart、termination、primal infeasibility、
dual infeasibility 和 duality gap。
