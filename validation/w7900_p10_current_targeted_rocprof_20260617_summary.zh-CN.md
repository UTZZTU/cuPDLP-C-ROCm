# W7900 P10 current targeted rocprof 汇总

运行目录：`/app/cupdlp_w7900/results/w7900_p10_current_targeted_rocprof_20260616_213242`

Trace 模式：`rocprofv3 --runtime-trace --output-format csv`。

本次 P10 对 current W7900/gfx1100 分支上的 5 个代表 case 做 targeted profiling，这些 case 来自 P9 派生指标分析：

- 正向执行效率样本：`thk_48`
- 迭代数稳定样本：`square41`
- 收敛迭代数回退样本：`L2CTA3D`、`set-cover-model`、`tpl-tub-ws1617`

原始 rocprofv3 trace 文件继续保留在 `/app/cupdlp_w7900/results`，不提交到 Git。本条 validation 只提交 compact CSV/Markdown 汇总。

## 运行汇总

- case 数：`5`
- 成功 OPTIMAL：`5/5`
- case：`L2CTA3D, set-cover-model, square41, thk_48, tpl-tub-ws1617`

| case | status | nIter | solve s | HIP API calls | HIP API ms | kernel dispatches | kernel ms | memcpy count | memcpy ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L2CTA3D | OPTIMAL | 80 | 0.533784 | 4533 | 1270.0 | 2991 | 435.076 | 55 | 51.885 |
| set-cover-model | OPTIMAL | 7480 | 12.011 | 164440 | 12220.9 | 138676 | 10470.4 | 30 | 21.051 |
| square41 | OPTIMAL | 128360 | 115.577 | 2470120 | 112513.0 | 2049235 | 96132.6 | 26 | 12.409 |
| thk_48 | OPTIMAL | 17720 | 69.485 | 396979 | 69824.5 | 337117 | 65716.9 | 57 | 54.630 |
| tpl-tub-ws1617 | OPTIMAL | 82600 | 103.876 | 1667279 | 102111.0 | 1395714 | 90161.0 | 20 | 7.682 |

## 每个 case 的 rank-1 热点

| case | top kernel | kernel calls | kernel total ms | top HIP API | HIP calls | HIP API total ms |
|---|---|---:|---:|---|---:|---:|
| L2CTA3D | `rocsparse::csrmvn_general_kernel` | 97 | 85.228 | `hipMemcpy` | 146 | 697.713 |
| set-cover-model | `rocsparse::csrmvn_general_kernel` | 7943 | 4979.3 | `hipMemcpy` | 8289 | 10344.7 |
| square41 | `rocsparse::csrmvn_general_kernel` | 266214 | 90546.2 | `hipMemcpy` | 136533 | 95098.6 |
| thk_48 | `rocsparse::csrmvn_general_kernel` | 18249 | 18199.8 | `hipMemcpy` | 18843 | 60743.7 |
| tpl-tub-ws1617 | `rocsparse::csrmvn_general_kernel` | 169996 | 73250.4 | `hipMemcpy` | 87290 | 88177.8 |

## 解释

5 个 targeted case 在 current 下均成功完成。trace 结果确认，rocSPARSE CSR SpMV kernel 是多个 case 的主要 GPU kernel 热点，尤其是 `set-cover-model`、`square41` 和 `thk_48`。在较长 case 上，HIP API 时间主要由 `hipMemcpy` 主导，同时 `hipLaunchKernel` 和 `hipMemcpyAsync` 也很突出。这支持下一步调优方向：继续聚焦 SpMV 行为、kernel launch 数量和 host-device copy reduction，同时避免在没有明确数值验证的情况下改动 residual、restart、termination 或 scaling 逻辑。

## 文件

- `w7900_p10_current_targeted_rocprof_20260617_runtime.csv`
- `w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv`
- `w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv`
- `w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv`
- `w7900_p10_current_targeted_rocprof_20260617_milestone_deltas.csv`
