# ROCm tuning guide

> 中文版: [`TUNING_GUIDE_ROCM.zh-CN.md`](TUNING_GUIDE_ROCM.zh-CN.md)

This document records profiling and tuning notes for the ROCm/HIP port of cuPDLP-C.

## Target and scope

| Item | Value |
|---|---|
| Current verified target | AMD Radeon 890M |
| Architecture | `gfx1150` |
| ROCm | 7.2.1 |
| Profiler | `rocprofv3` |
| Build target | `build-rocm-plc/bin/plc` |

This document is not a claim that the ROCm/HIP backend is fully tuned. It records the current profiling baseline, completed low-risk tuning steps, and future optimization directions.

## Why tuning is needed

PDLP-style first-order LP solvers rely heavily on repeated sparse matrix-vector products and vector operations. Important operations include:

- `Ax`,
- `Aty`,
- hipSPARSE / rocSPARSE SpMV,
- hipBLAS / rocBLAS vector operations,
- vector updates,
- reductions,
- projection kernels,
- residual computation,
- host/device synchronization,
- memory allocation,
- host/device memory transfer.

Small cases such as `afiro.mps` and `sc50b.mps` are useful for correctness and workflow validation, but they are too small to represent final GPU performance on larger sparse LP problems.

## Profiling entry point

Run smoke profiling:

```bash
RESULT_ROOT=profiling/results/current \
  ./scripts/profile_rocm_smoke.sh
```

Summarize `rocprofv3` CSV traces:

```bash
python3 scripts/summarize_rocm_profile.py \
  --input profiling/results/current \
  --output profiling/results/current/profile_summary.md
```

For copy/copyBuffer analysis:

```bash
python3 scripts/analyze_rocm_copy_trace.py \
  --input profiling/results/current/sc50b_rocprofv3 \
  | tee profiling/results/current/sc50b_copy_analysis.md
```

Profiling outputs are generated artifacts and should not be committed.

## Initial profiling observations

Initial `rocprofv3` runtime traces on `afiro` and `sc50b` showed that small-case runtime is dominated by many small GPU operations rather than one single custom kernel.

Observed hot areas include:

- `hipLaunchKernel`,
- `hipMemcpyAsync`,
- `hipMemcpy`,
- `hipDeviceSynchronize`,
- `hipStreamSynchronize`,
- `hipMalloc` / `hipFree`,
- `__amd_rocclr_copyBuffer`,
- `__amd_rocclr_fillBufferAligned`,
- rocSPARSE SpMV kernels,
- rocBLAS AXPY, dot, norm, and scaling kernels,
- custom PDLP update and movement kernels.

First-pass conclusion:

```text
For small smoke cases, optimize structural overhead first: launches, copies, synchronization, and repeated runtime queries.
Do not start with low-level instruction tuning or custom SpMV rewrites.
```

## Metrics to track

Solver-level metrics:

| Metric | Why it matters |
|---|---|
| Wall-clock time | End-to-end user-visible runtime |
| Solve time | Main solver loop runtime |
| Iteration count | Algorithmic progress |
| Iterations per second | Coarse throughput |
| Matvec time | Sparse linear algebra contribution |
| Feasibility and gap | Correctness and convergence quality |

Runtime-level metrics:

| Metric | Why it matters |
|---|---|
| `hipLaunchKernel` count/time | Kernel launch granularity |
| `hipMemcpyAsync` count/time | Async memory transfer frequency |
| `hipMemcpy` count/time | Synchronous transfer frequency |
| `hipDeviceSynchronize` count/time | Global synchronization overhead |
| `hipStreamSynchronize` count/time | Stream synchronization overhead |
| `hipMalloc` / `hipFree` count | Repeated allocation overhead |
| `hipGetDevice` / attribute query count | Repeated runtime query overhead |

Kernel-level metrics:

| Kernel group | Why it matters |
|---|---|
| rocSPARSE SpMV kernels | PDLP core sparse matvec work |
| rocBLAS AXPY kernels | Vector update overhead |
| rocBLAS dot/norm kernels | Reduction overhead |
| Custom gradient kernels | PDLP update cost |
| Movement kernels | Restart and movement interaction cost |
| ROCclr copy/fill kernels | Hidden copy/fill overhead |

## Completed profiling-driven optimizations

The current tuning pass completed four low-risk optimizations on Radeon 890M / `gfx1150`.

### 1. Remove redundant device synchronization

A redundant `hipDeviceSynchronize()` was removed from the ROCm/HIP movement interaction path. The final blocking device-to-host copy already provides the required ordering for reading scalar results on the host.

Observed smoke-profile effect:

| Case | Before | After |
|---|---:|---:|
| `afiro` `hipDeviceSynchronize` calls | 203 | 3 |
| `sc50b` `hipDeviceSynchronize` calls | 564 | 3 |

### 2. Cache HIP device attributes

Repeated HIP device attribute queries were cached in the HIP linear algebra helper path.

This reduces runtime API noise and avoids repeated queries of stable device attributes such as multiprocessor count and warp size.

### 3. Fuse average-iterate AXPY updates

Two per-iteration average-iterate AXPY updates were fused into one custom ROCm/HIP kernel:

```text
update_average_kernel
```

Observed effect:

| Metric | `afiro` before | `afiro` after | `sc50b` before | `sc50b` after |
|---|---:|---:|---:|---:|
| `hipLaunchKernel` calls | 2667 | 2468 | 6071 | 5511 |
| `rocblas_axpy_kernel` dispatches | 506 | 108 | 1270 | 150 |
| `update_average_kernel` dispatches | 0 | 199 | 0 | 560 |

### 4. Reduce movement interaction scalar D2D copies

Two small device-to-device scalar copies in `cupdlp_movement_interaction_cuda()` were replaced by a small custom kernel:

```text
save_movement_xy_kernel
```

Observed smoke-profile effect:

| Metric | `afiro` before | `afiro` after | `sc50b` before | `sc50b` after |
|---|---:|---:|---:|---:|
| `hipMemcpyAsync` calls | 1136 | 736 | 2485 | 1363 |
| `__amd_rocclr_copyBuffer` dispatches | 1444 | 1044 | 3182 | 2060 |
| `save_movement_xy_kernel` dispatches | 0 | 200 | 0 | 561 |

This reduced many tiny copyBuffer dispatches while preserving validation results.

## Current post-optimization profile shape

Remaining hot areas include:

- `hipLaunchKernel`,
- remaining `hipMemcpy` / `hipMemcpyAsync`,
- remaining `__amd_rocclr_copyBuffer`,
- rocBLAS dot and norm reductions,
- rocSPARSE SpMV kernels.

The AXPY path is no longer the dominant rocBLAS issue. Remaining rocBLAS hotspots are mostly reduction-style operations, which are higher risk to replace.

## What not to change casually

Avoid these changes without larger validation and profiling:

- removing legacy C/HIP compatibility symbols,
- rewriting sparse matrix storage,
- replacing all rocBLAS calls with custom kernels,
- replacing all rocSPARSE calls with custom SpMV kernels,
- replacing dot/norm reductions without careful numerical validation,
- full HIP Graph capture of the solver loop,
- tuning only for `afiro` or `sc50b`.

## Large-case profiling policy

The next profiling stage should use larger MPS cases. Suggested first large-case profiling targets should include:

- one case where ROCm is competitive,
- one case where ROCm is slower,
- one large sparse case where SpMV dominates,
- one convergence-sensitive case if logs are stable enough.

Use large-case profiling to decide whether the next bottleneck is launch count, SpMV, BLAS reductions, memory movement, or convergence trajectory.

## Future tuning work

- Add profiling templates for large MPS cases.
- Add ROCTx ranges around solver phases.
- Separate setup time from main iteration time more clearly.
- Investigate remaining scalar readback and synchronization.
- Investigate reduction kernels only after validation coverage is larger.
- Investigate SpMV descriptor and buffer reuse.
- `gfx1150` vs `gfx1100` comparison is now represented by W7900 P10/P11/P12/P14-A1 artifacts.

## Summary

The current ROCm/HIP port is validated enough to begin profiling and controlled tuning, but not enough to claim final performance. Early tuning should focus on:

```text
launch count + synchronization + memory copies + SpMV + BLAS level-1 reductions
```

Every tuning change must be paired with validation and before/after profiling or benchmark evidence.

## W7900 tuning endpoint / 2026-06-17

This guide was originally written around the Radeon 890M / `gfx1150`
tuning sequence. The W7900 / `gfx1100` follow-up is now complete for the
current project scope.

Current W7900 policy:

- default HIP SpMV algorithm: `HIPSPARSE_SPMV_CSR_ALG1`
- rollback to old default: `CUPDLP_HIP_SPMV_ALG=csr_alg2`
- experimental hipSPARSE default: `CUPDLP_HIP_SPMV_ALG=default`

No additional long profiling run is required for the current project
endpoint. Further tuning should be treated as future work and should
focus on carefully validated scalar-copy or reduction-path changes.

## Final W7900 tuning-guide status after P14-A1 / 2026-06-18

This guide was originally centered on 890M / `gfx1150` tuning. The W7900 /
`gfx1100` follow-up now has its own closure evidence:

- P10 targeted profiling;
- P11 SpMV algorithm policy, current default `HIPSPARSE_SPMV_CSR_ALG1`;
- P12 rejected buffer-algorithm consistency experiment;
- P14-A1 quick6 repeated current-vs-pre_tuning validation.

P14-A1 shows `current` faster on `6/6` quick6 cases, with geomean speedup
`1.18889` and median speedup `1.19502`.

No further W7900 experiment is required for the current project closure.
