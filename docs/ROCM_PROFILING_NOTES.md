# ROCm profiling notes

> 中文版：[ROCM_PROFILING_NOTES.zh-CN.md](ROCM_PROFILING_NOTES.zh-CN.md)

This page consolidates the current profiling interpretation. Dated CSV and Markdown files under `validation/` remain the source evidence.

## Scope

The repository contains two profiling stages:

| Stage | Platform | Purpose |
|---|---|---|
| Early structural profiling | Radeon 890M / `gfx1150` | Identify launch, copy, synchronization, and runtime-query overhead |
| P10 targeted profiling | Radeon PRO W7900 / `gfx1100` | Identify the current large-case W7900 hotspots before platform-specific tuning |

The 890M stage is historical evidence. P10 is the current W7900 profiling reference.

## Profiling tools and output policy

The maintained workflow prefers `rocprofv3`, with legacy `rocprof` as a fallback where supported.

Generated raw trace directories are not committed. The repository keeps:

- runtime summaries;
- HIP API top tables;
- kernel top tables;
- memory-copy summaries;
- compact Markdown interpretation.

Primary W7900 entry:

```bash
bash scripts/run_w7900_p10_current_targeted_rocprof.sh
```

Generic smoke profiling remains available:

```bash
RESULT_ROOT=profiling/results/current \
  bash scripts/profile_rocm_smoke.sh

python3 scripts/summarize_rocm_profile.py \
  --input profiling/results/current \
  --output profiling/results/current/profile_summary.md
```

## P10 case set

P10 uses five targeted cases selected to cover different runtime shapes:

```text
thk_48
square41
L2CTA3D
set-cover-model
tpl-tub-ws1617
```

Do not confuse this set with the earlier `cases_w7900_rocprof_starter3.txt` workflow. The starter3 artifacts remain useful historical profiling evidence, but they are not the P10 targeted case list.

## Metrics to interpret together

Solver-level:

| Metric | Purpose |
|---|---|
| Wall time and solve time | End-to-end and solver-loop cost |
| `nIter` | Convergence-path cost |
| Feasibility and gap | Correctness |
| `DeviceMatVecProdTime` | Sparse-matvec contribution |

Runtime-level:

| Metric | Purpose |
|---|---|
| `hipLaunchKernel` | Launch granularity and frequency |
| `hipMemcpy` / `hipMemcpyAsync` | Host/device and scalar-transfer pressure |
| Synchronization APIs | Ordering overhead |
| Allocation APIs | Repeated setup cost |

Kernel-level:

| Group | Purpose |
|---|---|
| rocSPARSE CSR SpMV | Core sparse work |
| rocBLAS reductions and vector operations | Level-1 and reduction cost |
| Custom PDLP update kernels | Solver-specific update cost |
| ROCclr copy/fill kernels | Hidden memory-operation overhead |

## Historical 890M findings

Early smoke profiling showed many small GPU operations rather than one isolated custom-kernel bottleneck. That evidence motivated low-risk structural changes:

1. remove redundant device synchronization;
2. cache stable HIP device attributes;
3. fuse average-iterate AXPY updates;
4. reduce movement-interaction scalar copies.

These changes reduced synchronization, launches, AXPY dispatches, and small copy operations while preserving the validation result. Full historical numbers remain in:

- [profiling tuning milestones](../validation/rocm_prof_tuning_milestones_summary.md)
- [tuning ablation repeats](../validation/rocm_tuning_ablation_6cases_repeats_summary.md)
- [current vs reduce comparison](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.md)

## W7900 P10 findings

The P10 evidence shows that rocSPARSE CSR SpMV is the dominant GPU kernel group on the targeted W7900 cases. Runtime overhead from `hipMemcpy`, `hipMemcpyAsync`, and kernel launches also remains visible.

Source artifacts:

- [P10 summary](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.md)
- [HIP API top table](../validation/w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv)
- [kernel top table](../validation/w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv)
- [memory-copy top table](../validation/w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv)
- [milestone deltas](../validation/w7900_p10_current_targeted_rocprof_20260617_milestone_deltas.csv)

The correct conclusion is not “replace hipSPARSE with a custom SpMV.” The evidence justified a controlled comparison of supported hipSPARSE SpMV algorithms.

## From profiling to tuning

P10 led to P11:

- add a runtime SpMV algorithm switch;
- compare `CSR_ALG1`, `CSR_ALG2`, and the library default;
- keep correctness and iteration behavior visible;
- accept `HIPSPARSE_SPMV_CSR_ALG1` as the current default;
- retain `CUPDLP_HIP_SPMV_ALG=csr_alg2` as rollback.

P12 then tested a related buffer-algorithm consistency change. It was rejected because `set-cover-model` changed from 7480 to 7600 iterations. This is evidence that profiling and tuning decisions must include numerical trajectory, not only kernel timing.

P14-A1 repeated the current-vs-pre-tuning comparison on quick6 and confirmed 6/6 current wins with unchanged iteration counts.

## Current profiling conclusion

For the current project endpoint:

```text
primary W7900 kernel hotspot: rocSPARSE CSR SpMV
secondary runtime concerns: copies and launch overhead
accepted tuning endpoint: CSR_ALG1 default
required safeguard: correctness and convergence validation
```

No additional long profiling run is required to support the current repository conclusion. Future profiling is optional and should answer a specific question, such as reduction-path cost, scalar readback, or a new GPU architecture.

## Related documents

- [W7900 current status](W7900_CURRENT_STATUS.md)
- [ROCm tuning history](ROCM_TUNING_HISTORY.md)
- [ROCm tuning guide](TUNING_GUIDE_ROCM.md)
- [Validation index](../validation/README.md)
