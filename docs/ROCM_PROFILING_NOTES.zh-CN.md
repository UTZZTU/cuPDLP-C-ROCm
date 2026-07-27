# ROCm profiling 记录与当前结论

> English: [ROCM_PROFILING_NOTES.md](ROCM_PROFILING_NOTES.md)

本文整合当前 profiling 解释。`validation/` 下带日期的 CSV 与 Markdown 仍是源证据。

## 范围

仓库包含两个 profiling 阶段：

| 阶段 | 平台 | 目的 |
|---|---|---|
| 早期结构性 profiling | Radeon 890M / `gfx1150` | 识别 launch、copy、同步和 runtime query 开销 |
| P10 targeted profiling | Radeon PRO W7900 / `gfx1100` | 在平台特化调优前识别当前 large-case W7900 热点 |

890M 阶段属于历史证据；P10 是当前 W7900 profiling 参考。

## 工具与输出策略

维护脚本优先使用 `rocprofv3`，在支持环境中可回退到 legacy `rocprof`。

Raw trace directories 不提交。仓库保留：

- runtime summaries；
- HIP API top tables；
- kernel top tables；
- memory-copy summaries；
- compact Markdown 解释。

W7900 主要入口：

```bash
bash scripts/run_w7900_p10_current_targeted_rocprof.sh
```

通用 smoke profiling 仍可使用：

```bash
RESULT_ROOT=profiling/results/current \
  bash scripts/profile_rocm_smoke.sh

python3 scripts/summarize_rocm_profile.py \
  --input profiling/results/current \
  --output profiling/results/current/profile_summary.md
```

## P10 case set

P10 使用 5 个 targeted cases，覆盖不同运行形态：

```text
thk_48
square41
L2CTA3D
set-cover-model
tpl-tub-ws1617
```

不要把它与更早的 `cases_w7900_rocprof_starter3.txt` workflow 混淆。starter3 仍是有效历史证据，但不是 P10 targeted case list。

## 需要联合解释的指标

Solver 层：

| 指标 | 用途 |
|---|---|
| Wall time 与 solve time | 端到端和主循环成本 |
| `nIter` | 收敛路径成本 |
| Feasibility 与 gap | 正确性 |
| `DeviceMatVecProdTime` | 稀疏 matvec 占比 |

Runtime 层：

| 指标 | 用途 |
|---|---|
| `hipLaunchKernel` | launch 粒度与频率 |
| `hipMemcpy` / `hipMemcpyAsync` | 主机/设备与 scalar transfer 压力 |
| Synchronization APIs | 排序与同步开销 |
| Allocation APIs | 重复 setup 成本 |

Kernel 层：

| 组 | 用途 |
|---|---|
| rocSPARSE CSR SpMV | 核心稀疏计算 |
| rocBLAS reduction 与向量操作 | Level-1 与归约成本 |
| 自定义 PDLP update kernels | 求解器特定更新成本 |
| ROCclr copy/fill kernels | 隐式 memory-operation 开销 |

## 890M 历史发现

早期 smoke profiling 表明，小 case 的主要特征是大量小 GPU 操作，而不是某一个孤立的自定义 kernel。该证据推动了四类低风险结构优化：

1. 删除冗余 device synchronization；
2. 缓存稳定的 HIP device attributes；
3. 融合 average-iterate AXPY updates；
4. 减少 movement-interaction scalar copies。

这些修改在保持验证结果的前提下减少了同步、launch、AXPY dispatch 和小 copy。完整历史数字见：

- [profiling tuning milestones](../validation/rocm_prof_tuning_milestones_summary.zh-CN.md)
- [tuning ablation repeats](../validation/rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md)
- [current vs reduce comparison](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md)

## W7900 P10 发现

P10 证据表明，在 targeted W7900 cases 上，rocSPARSE CSR SpMV 是主要 GPU kernel group。`hipMemcpy`、`hipMemcpyAsync` 和 kernel launch 开销也仍然可见。

源证据：

- [P10 summary](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md)
- [HIP API top table](../validation/w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv)
- [kernel top table](../validation/w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv)
- [memory-copy top table](../validation/w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv)
- [milestone deltas](../validation/w7900_p10_current_targeted_rocprof_20260617_milestone_deltas.csv)

正确结论不是“立刻用自定义 SpMV 替代 hipSPARSE”，而是对库提供的 SpMV algorithm 做受控比较。

## 从 profiling 到 tuning

P10 推动了 P11：

- 增加 runtime SpMV algorithm switch；
- 比较 `CSR_ALG1`、`CSR_ALG2` 与 library default；
- 同时观察正确性和迭代行为；
- 接受 `HIPSPARSE_SPMV_CSR_ALG1` 作为当前默认；
- 保留 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 回退。

P12 随后测试相关的 buffer-algorithm consistency 修改。由于 `set-cover-model` 迭代数由 7480 变为 7600，该修改被拒绝。这说明 profiling 与 tuning 决策必须包含数值轨迹，而不能只看 kernel 时间。

P14-A1 对 quick6 重复 current-vs-pre-tuning 比较，确认 current 6/6 胜出且迭代数不变。

## 当前 profiling 结论

当前项目终点可以概括为：

```text
主要 W7900 kernel 热点：rocSPARSE CSR SpMV
次级 runtime 关注点：copy 与 launch overhead
已接受调优终点：CSR_ALG1 默认
必要保护：正确性与收敛验证
```

支撑当前仓库结论不再需要额外 long profiling。未来 profiling 应服务于明确问题，例如 reduction path、scalar readback 或新 GPU 架构。

## 相关文档

- [W7900 当前状态](W7900_CURRENT_STATUS.zh-CN.md)
- [ROCm 调优历史](ROCM_TUNING_HISTORY.zh-CN.md)
- [ROCm 调优指南](TUNING_GUIDE_ROCM.zh-CN.md)
- [Validation 索引](../validation/README.zh-CN.md)
