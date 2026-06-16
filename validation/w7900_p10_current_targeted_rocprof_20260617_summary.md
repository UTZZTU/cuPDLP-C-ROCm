# W7900 P10 current targeted rocprof summary

Run dir: `/app/cupdlp_w7900/results/w7900_p10_current_targeted_rocprof_20260616_213242`

Trace mode: `rocprofv3 --runtime-trace --output-format csv`.

This P10 run profiles the current W7900/gfx1100 branch on five targeted cases selected from the P9 derived-metric analysis:

- positive execution-efficiency sample: `thk_48`
- stable iteration-count sample: `square41`
- convergence-regression samples: `L2CTA3D`, `set-cover-model`, `tpl-tub-ws1617`

Raw rocprofv3 trace files remain under `/app/cupdlp_w7900/results` and are intentionally not committed. This validation entry commits only compact CSV/Markdown summaries.

## Runtime summary

- Cases: `5`
- Successful OPTIMAL cases: `5/5`
- Cases: `L2CTA3D, set-cover-model, square41, thk_48, tpl-tub-ws1617`

| case | status | nIter | solve s | HIP API calls | HIP API ms | kernel dispatches | kernel ms | memcpy count | memcpy ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L2CTA3D | OPTIMAL | 80 | 0.533784 | 4533 | 1270.0 | 2991 | 435.076 | 55 | 51.885 |
| set-cover-model | OPTIMAL | 7480 | 12.011 | 164440 | 12220.9 | 138676 | 10470.4 | 30 | 21.051 |
| square41 | OPTIMAL | 128360 | 115.577 | 2470120 | 112513.0 | 2049235 | 96132.6 | 26 | 12.409 |
| thk_48 | OPTIMAL | 17720 | 69.485 | 396979 | 69824.5 | 337117 | 65716.9 | 57 | 54.630 |
| tpl-tub-ws1617 | OPTIMAL | 82600 | 103.876 | 1667279 | 102111.0 | 1395714 | 90161.0 | 20 | 7.682 |

## Top rank-1 hotspots by case

| case | top kernel | kernel calls | kernel total ms | top HIP API | HIP calls | HIP API total ms |
|---|---|---:|---:|---|---:|---:|
| L2CTA3D | `rocsparse::csrmvn_general_kernel` | 97 | 85.228 | `hipMemcpy` | 146 | 697.713 |
| set-cover-model | `rocsparse::csrmvn_general_kernel` | 7943 | 4979.3 | `hipMemcpy` | 8289 | 10344.7 |
| square41 | `rocsparse::csrmvn_general_kernel` | 266214 | 90546.2 | `hipMemcpy` | 136533 | 95098.6 |
| thk_48 | `rocsparse::csrmvn_general_kernel` | 18249 | 18199.8 | `hipMemcpy` | 18843 | 60743.7 |
| tpl-tub-ws1617 | `rocsparse::csrmvn_general_kernel` | 169996 | 73250.4 | `hipMemcpy` | 87290 | 88177.8 |

## Interpretation

The five targeted cases all complete successfully under current. The traces confirm that rocSPARSE CSR SpMV kernels are the dominant GPU kernel hotspot on several cases, especially `set-cover-model`, `square41`, and `thk_48`. HIP API time is dominated by `hipMemcpy` on the longer cases, while `hipLaunchKernel` and `hipMemcpyAsync` are also prominent. This supports the next tuning direction: keep profiling focused on SpMV behavior, kernel launch volume, and host-device copy reduction, while avoiding unvalidated changes to residual, restart, termination, or scaling logic.

## Files

- `w7900_p10_current_targeted_rocprof_20260617_runtime.csv`
- `w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv`
- `w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv`
- `w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv`
- `w7900_p10_current_targeted_rocprof_20260617_milestone_deltas.csv`
