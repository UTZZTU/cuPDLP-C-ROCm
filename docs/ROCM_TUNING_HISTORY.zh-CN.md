# ROCm 调优历史

> English: [ROCM_TUNING_HISTORY.md](ROCM_TUNING_HISTORY.md)

本文按统一时间线记录调优过程，不再把旧计划与当前状态混在一起。带日期的报告和 CSV 仍是权威实验材料。

## Baseline 角色

| 角色 | 参考 | 含义 |
|---|---|---|
| Pre-tuning anchor | `ae3b683 / pre_tuning` | 用于 before/current 分析的 first-runnable ROCm anchor |
| 890M engineering sequence | `ae3b683` 之后的 milestones | `gfx1150` 上的结构性开销调优 |
| W7900 current branch | `rocm-w7900-gfx1100` | post-890M-tuning engineering baseline |
| W7900 accepted endpoint | P11 policy | `HIPSPARSE_SPMV_CSR_ALG1` 默认，`csr_alg2` 回退 |

当前 W7900 baseline 不能描述为未优化 first port。

## 890M 结构性调优序列

早期 profiling-driven sequence 聚焦低风险结构性开销：

| Milestone | 修改 |
|---|---|
| `ae3b683` | pre-tuning anchor |
| `f9d7f0d` | 删除冗余同步 |
| `8fed073` | 缓存 HIP device attributes |
| `fa7e860` | 融合 average-iterate updates |
| `b44c7ab` | 减少 movement-interaction scalar copies |

具体代码级内容以 Git 历史为准。

### 为什么选择这些修改

Smoke profiling 显示以下调用较多：

- kernel launches；
- small copies；
- synchronization；
- 稳定 device-attribute queries；
- 重复向量更新。

因此先减少结构性开销，而不是直接重写 sparse 或 reduction 内核。

### 验证证据

890M 阶段包括：

- 6-case repeated ablation；
- 27-case current-vs-reduce comparison；
- profiling milestone summaries；
- CPU/ROCm validation checks。

6-case 历史显示组合修改带来有效收益。最后两个接近 milestone 的 27-case 比较中，base-over-current geomean 接近持平（`0.9995092331107024`），说明不能过度解释很小的 aggregate 差异。

证据：

- [profiling milestones](../validation/rocm_prof_tuning_milestones_summary.zh-CN.md)
- [6-case repeated ablation](../validation/rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md)
- [27-case comparison](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md)

## W7900 调优前验证

W7900 / `gfx1100` 先建立了：

1. CPU 与 ROCm build 路径；
2. `afiro` smoke validation；
3. Netlib validation；
4. large-MPS subsets；
5. non-hard23 23/23 `OPTIMAL`；
6. hard3 独立分组。

因此平台特化调优开始前已经有正确性和 large-case 证据基础。

## P10：targeted profiling

P10 使用：

```text
thk_48
square41
L2CTA3D
set-cover-model
tpl-tub-ws1617
```

主要结论是 rocSPARSE CSR SpMV 在 targeted W7900 GPU kernel profile 中占主导，copy 和 launch overhead 是次级关注点。

见 [P10 summary](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md)。

## P11：接受的 SpMV algorithm policy

P11 没有重写 sparse library，而是增加 runtime 选择：

| 选择 | Runtime 值 |
|---|---|
| 当前默认 | `HIPSPARSE_SPMV_CSR_ALG1` |
| 旧默认回退 | `CUPDLP_HIP_SPMV_ALG=csr_alg2` |
| Library experimental default | `CUPDLP_HIP_SPMV_ALG=default` |

该阶段包括：

- runtime call-site inventory；
- algorithm switch smoke validation；
- 5-case algorithm sweep；
- default-policy smoke validation；
- final tuning summary。

见 [P11 summary](../validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md)。

## P12：被拒绝的执行层实验

P12 尝试让 `hipsparseSpMV_bufferSize()` 查询与选定执行算法一致。由于 `set-cover-model` 迭代数从 7480 变为 7600，patch 被拒绝。

该结果说明：

> 一个修改即使局部合理、具有性能动机，如果引入无法充分解释的数值轨迹变化，也不应被接受。

见 [P12 negative result](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md)。

## P14-A1：重复 before/current 确认

P14-A1 重复比较 current 与 `pre_tuning` quick6：

| 指标 | 结果 |
|---|---:|
| Current wins | 6/6 |
| Geomean speedup | 1.18889 |
| Median speedup | 1.19502 |
| 迭代数变化 | 0/6 |

见 [P14-A1 summary](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md)。

## 8 卡吞吐

fast8 实验测量 8 个独立 MPS 任务：

```text
8 卡并发：146 s
单卡顺序：558 s
```

这是 batch throughput，不是单个 LP 的分布式多 GPU 求解。

见 [8-card summary](../validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md)。

## 当前终点

当前接受策略是：

```text
W7900 默认 SpMV：HIPSPARSE_SPMV_CSR_ALG1
回退：CUPDLP_HIP_SPMV_ALG=csr_alg2
验证保护：CPU/ROCm status 与数值检查
before anchor：ae3b683 / pre_tuning
```

P10、P11、P12 和 P14-A1 已闭合当前 W7900 tuning 证据链。P14-B ALG1-vs-ALG2 repeated study 可作为可选增强，但不是未完成的核心范围。

## 未来调优规则

1. 固定 before reference 与 case list。
2. 记录 status、residual、gap、`nIter`、wall time 和 solve time。
3. 性能结论使用重复运行。
4. 先 profiling，再选择 patch。
5. 拒绝引入无法解释收敛变化的修改。
6. 困难 case 必须可见并单独报告。
7. 不只针对 smoke case 调优。
8. 平台敏感 policy 保留 runtime rollback。

## 相关文档

- [ROCm profiling 记录](ROCM_PROFILING_NOTES.zh-CN.md)
- [ROCm 调优指南](TUNING_GUIDE_ROCM.zh-CN.md)
- [W7900 当前状态](W7900_CURRENT_STATUS.zh-CN.md)
- [Validation 索引](../validation/README.zh-CN.md)
