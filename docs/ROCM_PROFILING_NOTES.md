# ROCm Profiling Notes

This document explains the ROCm/HIP profiling evidence collected for the `cuPDLP-C-ROCm` tuning sequence.

The goal is not only to show that the solver became faster, but also to explain *why* the ROCm tuning sequence improved performance.

## Scope

This document focuses on ROCm/HIP profiling on the Radeon 890M / `gfx1150` development platform.

The profiling data was collected with `rocprofv3 --runtime-trace --output-format csv`, which records HIP runtime API traces, kernel dispatch traces, memory copy traces, scratch memory traces, and related runtime information.

The profiled tuning milestones were:

| Milestone | Commit | Meaning |
|---|---|---|
| `pre_tuning` | `ae3b683` | Pre-tuning baseline |
| `remove_sync` | `f9d7f0d` | Remove redundant HIP device synchronization |
| `cache_attrs` | `8fed073` | Cache HIP device attributes |
| `fused_average` | `fa7e860` | Fuse ROCm average-iterate AXPY updates |
| `reduce_scalar_copies` | `b44c7ab` | Reduce scalar copies in movement interaction |
| `current` | current HEAD | Current three-backend engineering version |

The profiled cases were:

| Case | Reason |
|---|---|
| `lotfi` | Medium-size case with clear tuning improvement |
| `scfxm1` | Case where current-vs-reduce had a small timing difference |
| `pilot87` | Larger representative case and positive control |

## Why profiling was needed

Earlier benchmark data already showed that the ROCm tuning sequence improved solve time on the 6-case quick set and that the current engineering version did not systematically regress relative to `reduce_scalar_copies`.

However, solve time alone does not explain the source of the improvement.

The profiling run was designed to answer:

1. Did `remove_sync` reduce runtime or synchronization overhead?
2. Did `cache_attrs` reduce repeated HIP runtime calls?
3. Did `fused_average` reduce kernel dispatches?
4. Did `reduce_scalar_copies` reduce runtime/copy/dispatch overhead?
5. Did the current three-backend engineering version preserve the optimized trace structure?

## Summary of main findings

The main finding is:

> The ROCm tuning sequence improves performance primarily by reducing HIP runtime API overhead and kernel dispatch count, while the current three-backend engineering version preserves the optimized trace structure.

From `pre_tuning` to `current`, the profiled cases showed the following approximate reductions:

| Case | Solve time reduction | HIP API calls reduction | HIP API time reduction | Kernel dispatch reduction | Kernel time reduction |
|---|---:|---:|---:|---:|---:|
| `lotfi` | 24.02% | 36.50% | 21.23% | 14.13% | 16.97% |
| `pilot87` | 17.55% | 31.81% | 14.64% | 11.52% | 7.86% |
| `scfxm1` | 23.87% | 36.18% | 20.55% | 13.99% | 16.73% |

This indicates that the improvements are not just measurement noise and are not solely caused by a single sparse matrix-vector kernel becoming faster. The changes reduce repeated runtime calls, kernel dispatches, and runtime overhead around the iterative solver loop.

## Milestone-by-milestone interpretation

### `remove_sync`

From `pre_tuning` to `remove_sync`, solve time decreased clearly across all three profiled cases.

| Case | Solve time change | HIP API time change | Kernel time change |
|---|---:|---:|---:|
| `lotfi` | -12.47% | -13.10% | -3.85% |
| `pilot87` | -9.00% | -8.60% | -1.26% |
| `scfxm1` | -10.88% | -11.13% | -1.91% |

Interpretation:

`remove_sync` mainly reduced HIP runtime / synchronization-related overhead. Kernel time changed only modestly, so the main benefit was not a faster SpMV kernel, but less runtime overhead around the GPU work.

This matches the intended change: removing redundant HIP device synchronization should reduce unnecessary host-side waiting and runtime overhead.

### `cache_attrs`

From `remove_sync` to `cache_attrs`, HIP API call counts dropped substantially:

| Case | HIP API calls change | Solve time change |
|---|---:|---:|
| `lotfi` | -15.62% | -1.87% |
| `pilot87` | -13.53% | -0.10% |
| `scfxm1` | -15.53% | -1.20% |

Interpretation:

`cache_attrs` did what it was intended to do: reduce repeated HIP runtime queries for device attributes. The solve-time effect is smaller than `remove_sync`, because these API calls are lighter than explicit synchronization, but the trace confirms that the runtime call structure improved.

### `fused_average`

From `cache_attrs` to `fused_average`, kernel dispatch count and HIP API call count decreased:

| Case | Kernel dispatch change | HIP API calls change | Solve time change |
|---|---:|---:|---:|
| `lotfi` | -7.04% | -15.98% | -8.10% |
| `pilot87` | -5.75% | -13.52% | -4.92% |
| `scfxm1` | -6.99% | -15.81% | -1.94% |

Interpretation:

`fused_average` reduced the number of separate GPU operations in the average-iterate update path. The trace confirms a lower dispatch count, which is the expected effect of fusing vector update operations.

This is important because small and medium LP cases can be sensitive to kernel launch overhead. Reducing dispatch count can improve solve time even if individual kernel implementations are not dramatically faster.

### `reduce_scalar_copies`

From `fused_average` to `reduce_scalar_copies`, the trace showed further reductions in HIP API calls and kernel dispatches:

| Case | HIP API calls change | Kernel dispatch change | Solve time change |
|---|---:|---:|---:|
| `lotfi` | -6.38% | -7.63% | -4.52% |
| `pilot87` | -5.24% | -6.13% | -1.56% |
| `scfxm1` | -6.26% | -7.53% | -1.88% |

Interpretation:

`reduce_scalar_copies` improved the movement-interaction path by reducing scalar movement and associated runtime work. The profiling data shows that this optimization reduced the runtime and dispatch structure further, especially on the more iteration-heavy `lotfi` case.

### `current`

From `reduce_scalar_copies` to `current`, the trace structure was preserved:

| Case | HIP API calls | Kernel dispatches | Solve time |
|---|---:|---:|---:|
| `lotfi` | 0% | 0% | +0.81% |
| `pilot87` | 0% | 0% | -3.10% |
| `scfxm1` | 0% | 0% | -10.14% |

Interpretation:

The current engineering version did not add extra HIP API calls or kernel dispatches relative to `reduce_scalar_copies`.

This is an important engineering result. The commits after `reduce_scalar_copies` restored CUDA compatibility, cleaned backend modes, removed the public `BUILD_HIP` option, added documentation, and solidified benchmark artifacts. Profiling shows that these structural changes did not disrupt the optimized ROCm runtime trace pattern.

A concise conclusion is:

> Current HEAD preserves the optimized ROCm runtime trace structure established by `reduce_scalar_copies`.

## Hotspot observations

The top kernel and HIP API traces show that the ROCm/HIP solver path spends time in the following categories:

- rocSPARSE sparse matrix-vector kernels;
- rocBLAS AXPY, dot, norm, and reduction kernels;
- movement interaction kernels;
- primal and dual gradient update kernels;
- runtime buffer copy operations;
- HIP memory-copy-related API calls.

Typical hotspot names include:

```text
__amd_rocclr_copyBuffer
rocsparse::csrmvn_general_kernel
rocblas_axpy_kernel
movement_1_kernel
movement_2_kernel
primal_grad_step_kernel
dual_grad_step_kernel
rocBLAS dot / reduction kernels
```

This suggests that future optimization should focus on:

1. reducing unnecessary runtime calls;
2. reducing kernel dispatch count where safe;
3. reducing host-device scalar transfer;
4. improving vector update fusion;
5. investigating rocSPARSE SpMV behavior on larger MPS cases;
6. using W7900 / `gfx1100` profiling to identify platform-specific bottlenecks.

## Memory-copy trace caveat

The `memory_copy_trace.csv` output can be sparse even when `hipMemcpy` or `hipMemcpyAsync` appears prominently in HIP API traces.

Therefore, this project should interpret memory-copy-related cost primarily through:

- `trace_hip_api_top.csv`;
- `hipMemcpy` and `hipMemcpyAsync` total time;
- `hip_api_total_ms`;
- solver-level copy timing fields where available.

The low-level memory-copy trace and HIP API trace operate at different levels of abstraction. It is safer to write:

> HIP memory-copy-related API time is a major runtime component, while low-level memory-copy trace events may be sparse in this profiling mode.

## Relationship to benchmark results

The profiling results complement the repeated benchmark results:

- The repeated tuning ablation showed that current is faster than the pre-tuning baseline on the quick set.
- The 27-case current-vs-reduce comparison showed that current has no systematic regression relative to `reduce_scalar_copies`.
- The rocprofv3 milestone traces explain where the improvement came from: lower HIP API overhead, fewer kernel dispatches, and lower runtime/kernel total time.

Together, these results support the following claim:

> The ROCm/HIP port is not only functional, but also has evidence-backed tuning improvements and preserves those improvements in the current three-backend engineering branch.

## Suggested next profiling steps

### Short term

Keep the current profiling set as the stable milestone trace set:

```text
lotfi
scfxm1
pilot87
```

These three cases are sufficient for explaining the existing tuning sequence.

### W7900 migration

When Radeon PRO W7900 is available, repeat the same profiling workflow with:

```text
-DCMAKE_HIP_ARCHITECTURES=gfx1100
```

Recommended first W7900 profiling cases:

```text
lotfi
scfxm1
pilot87
one medium-large MPS case
one large MPS case
```

### Large MPS experiments

For larger MPS cases, focus on:

- SpMV kernel time;
- rocSPARSE kernel behavior;
- memory bandwidth behavior;
- kernel dispatch count per iteration;
- host-device copy overhead;
- whether GPU compute time dominates fixed overhead.

### cuPDLP-C vs cuPDLPx

If cuPDLPx is evaluated later, this same profiling format can help compare:

- algorithmic iteration count;
- total solve time;
- kernel dispatch count;
- SpMV time;
- vector update and reduction time;
- runtime overhead.

## Files

Profiling data is stored in:

```text
validation/rocm_prof_tuning_milestones_summary.csv
validation/rocm_prof_tuning_milestones_deltas.csv
validation/rocm_prof_tuning_milestones_kernel_top.csv
validation/rocm_prof_tuning_milestones_hip_api_top.csv
validation/rocm_prof_tuning_milestones_memory_copy_top.csv
validation/rocm_prof_tuning_milestones_summary.md
```

Profiling scripts:

```text
scripts/profile_rocm_tuning_milestones_rocprofv3.sh
scripts/summarize_rocprofv3_milestones.py
```

## Summary

The rocprofv3 milestone trace confirms that the ROCm tuning sequence reduces solve time mainly by reducing HIP runtime API overhead and kernel dispatch count. It also confirms that the current CPU/CUDA/ROCm engineering branch preserves the optimized trace structure established by the tuning milestones.

This gives the project a stronger performance story than solve-time tables alone: the optimization effects are visible in runtime traces, not just in end-to-end benchmark summaries.

## W7900 profiling completion update / 2026-06-17

The W7900 migration mentioned earlier in this document has now been
completed for the current project stage. Instead of remaining a future
profiling target, W7900 now has committed P10 targeted rocprof summaries
and a P11 SpMV tuning endpoint.

Current W7900 profiling/tuning links:

- `validation/w7900_p10_current_targeted_rocprof_20260617_summary.md`
- `validation/w7900_p11_spmv_alg_sweep_20260617_summary.md`
- `validation/w7900_p11_spmv_tuning_summary_20260617.md`

The current conclusion is that SpMV is the first completed
W7900-specific tuning path. Copy-reduction and reduction-kernel work
remain possible future directions but are not part of the current
project endpoint.

## cuPDLPx final positioning after W7900 closure

The repository already contains a separate RTX 4090D short13 comparison
between cuPDLP-C and cuPDLPx. That comparison showed cuPDLPx v0.2.9 was
stable on the selected short/medium cases and faster on most of them.
It should be used as an algorithmic reference only.

It should not be merged into W7900 ROCm profiling conclusions because it
differs in solver algorithm, implementation stack, hardware backend, and
output conventions. A future cuPDLPx-ROCm study would need a separate
benchmark protocol.
