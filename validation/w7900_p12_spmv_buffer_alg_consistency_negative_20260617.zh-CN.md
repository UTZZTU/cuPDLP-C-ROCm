# W7900 P12 negative finding：SpMV buffer algorithm consistency

本文记录 P11 之后一次被拒绝的低风险执行层调优实验。

## 背景

P11 已将当前 W7900 默认 HIP SpMV algorithm 切换为
`HIPSPARSE_SPMV_CSR_ALG1`，并保留
`CUPDLP_HIP_SPMV_ALG=csr_alg2` 作为旧默认回退路径。

随后的源码审计发现一个一致性候选点：
`cuda_alloc_MVbuffer()` 中的 `hipsparseSpMV_bufferSize()` 仍使用本地
algorithm 变量 `HIPSPARSE_SPMV_CSR_ALG2`，而实际 runtime
`hipsparseSpMV()` 调用已经使用 `cupdlp_hip_spmv_alg()`。

## 实验内容

被拒绝的 patch 尝试做两件事：

1. 在 `cupdlp_hip_spmv_alg()` 中缓存 `CUPDLP_HIP_SPMV_ALG` 解析结果；
2. 让 `cuda_alloc_MVbuffer()` 中的 `hipsparseSpMV_bufferSize()` 使用
   `cupdlp_hip_spmv_alg()`。

## 观察结果

测试 case：`set-cover-model`

patch 后观察结果：

- exit code：`0`
- solver status：`Optimal current solution`
- 迭代数：`7600`
- solve time：`1.148008e+01`
- total solver time：`1.278179e+01`
- primal objective：`+7.58183814e+09`
- dual objective：`+7.58170468e+09`
- relative primal infeasibility：`9.84e-05`
- relative dual infeasibility：`0.00e+00`
- relative duality gap：`8.80e-06`

此前 P11 smoke 和 sweep 中，`set-cover-model` 在已接受的 SpMV
algorithm-switch 策略下稳定为 `7480` iterations。

## 决策

该 patch 被拒绝并撤回。

虽然这个实现一致性思路是合理的，但它改变了 solver 轨迹。它违反了本项目
对低风险调优的判断标准：执行层改动应保持 solver status、迭代数、
primal infeasibility、dual infeasibility 和 duality gap 不变，除非明确把它
作为更深层数值实验处理。

## 解释

这个结果本身很有价值。它说明即使是看起来局部的 SpMV buffer/algorithm
一致性改动，也可能影响 W7900 上观察到的 PDLP 迭代轨迹。因此该方向如果后续
继续推进，应作为未来更深层验证工作，而不是当前阶段的快速调优 patch。

## 最终状态

未提交：

- `cupdlp/hip/cupdlp_hip_linalg.cpp` patch 已撤回。
- 临时 patch 脚本已删除。

已接受终点仍为：

- 当前 W7900 默认 SpMV algorithm：`HIPSPARSE_SPMV_CSR_ALG1`
- 回退旧默认：`CUPDLP_HIP_SPMV_ALG=csr_alg2`
