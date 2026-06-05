# ROCm tuning guide

This document records profiling and tuning notes for the ROCm/HIP port of cuPDLP-C.

The current verified target is:

| Item | Value |
|---|---|
| GPU/APU | AMD Radeon 890M |
| Architecture | `gfx1150` |
| ROCm | 7.2.1 |
| Profiler | `rocprofv3` 1.1.0 |
| Build target | `build-rocm-plc/bin/plc` |

This document is not a claim that the ROCm/HIP backend is fully tuned. It is a record of the current profiling baseline and the next tuning directions.

## Current status

The ROCm/HIP backend currently:

- builds successfully,
- passes smoke validation,
- passes the current extended Netlib validation matrix except for one `INCOMPLETE` case,
- runs through CTest,
- has a reproducible smoke profiling script,
- has initial `rocprofv3` runtime trace results for `afiro` and `sc50b`.

No low-level performance optimization has been completed yet.

The current tuning priority is:

1. correctness,
2. validation coverage,
3. reproducible profiling,
4. bottleneck analysis,
5. safe tuning changes,
6. validation after each tuning change.

## Why tuning is needed

PDLP-style first-order LP solvers rely heavily on repeated sparse matrix-vector products and vector operations.

Important operations include:

- `Ax`,
- `Aty`,
- hipSPARSE SpMV,
- hipBLAS vector operations,
- vector updates,
- reductions,
- projection kernels,
- residual computation,
- host/device synchronization,
- memory allocation,
- host/device memory transfer.

Small cases such as `afiro.mps` and `sc50b.mps` are useful for correctness and workflow validation, but they are too small to represent final GPU performance on larger sparse LP problems.

For small cases, fixed overhead can dominate:

- HIP runtime calls,
- kernel launch overhead,
- stream synchronization,
- device memory allocation,
- device copy and fill operations,
- profiler overhead.

## Profiling entry point

The current smoke profiling script is:

```bash
./scripts/profile_rocm_smoke.sh
```

It performs the following steps:

1. Configures the ROCm/HIP build.
2. Builds the `plc` target.
3. Runs baseline ROCm smoke cases without profiler.
4. Runs `rocprofv3` runtime tracing when `rocprofv3` is available.
5. Writes profiling outputs under `profiling/results/`.

Default result directory:

```text
profiling/results/latest/
```

This directory is generated output and ignored by Git.

## Running the profiling smoke workflow

Run:

```bash
./scripts/profile_rocm_smoke.sh
```

To use a different architecture:

```bash
ROCM_ARCH=gfx1150 ./scripts/profile_rocm_smoke.sh
```

To write results to a different directory:

```bash
RESULT_ROOT=profiling/results/run_001 ./scripts/profile_rocm_smoke.sh
```

## Manual baseline commands

The profiling script runs baseline solver commands similar to the following.

For `afiro`:

```bash
./build-rocm-plc/bin/plc   -fname ./example/afiro.mps   -out profiling/results/latest/afiro_rocm_baseline.json   -nIterLim 200
```

For `sc50b`:

```bash
./build-rocm-plc/bin/plc   -fname ./validation/netlib/sc50b.mps   -out profiling/results/latest/sc50b_rocm_baseline.json   -nIterLim 5000
```

## Manual rocprofv3 command

The script uses conservative `rocprofv3` runtime tracing options.

Example:

```bash
rocprofv3   --runtime-trace   --summary   --summary-per-domain   --output-directory profiling/results/latest/afiro_rocprofv3   --output-file afiro   --output-format csv   -- ./build-rocm-plc/bin/plc       -fname ./example/afiro.mps       -out profiling/results/latest/afiro_rocm_profiled.json       -nIterLim 200
```

The command intentionally avoids hardware counters at this stage. Runtime trace is enough for the first pass because it shows HIP API calls, kernel dispatches, memory allocation, and memory copy activity.

Counters should be added later only after the major hot kernels and call patterns are known.

## Expected profiling outputs

A successful profiling run should create files such as:

```text
profiling/results/latest/afiro_rocm_baseline.json
profiling/results/latest/afiro_rocm_baseline.log
profiling/results/latest/afiro_rocm_profiled.json
profiling/results/latest/afiro_rocprofv3.log
profiling/results/latest/afiro_rocprofv3/afiro_agent_info.csv
profiling/results/latest/afiro_rocprofv3/afiro_hip_api_trace.csv
profiling/results/latest/afiro_rocprofv3/afiro_kernel_trace.csv
profiling/results/latest/afiro_rocprofv3/afiro_memory_allocation_trace.csv
profiling/results/latest/sc50b_rocm_baseline.json
profiling/results/latest/sc50b_rocm_baseline.log
profiling/results/latest/sc50b_rocm_profiled.json
profiling/results/latest/sc50b_rocprofv3.log
profiling/results/latest/sc50b_rocprofv3/sc50b_agent_info.csv
profiling/results/latest/sc50b_rocprofv3/sc50b_hip_api_trace.csv
profiling/results/latest/sc50b_rocprofv3/sc50b_kernel_trace.csv
profiling/results/latest/sc50b_rocprofv3/sc50b_memory_allocation_trace.csv
```

## Initial profiling observations

Initial `rocprofv3` runtime trace was collected on:

- `afiro`,
- `sc50b`.

The observed hot areas are consistent across both smoke cases.

Top HIP API activity includes:

- `hipGetDevice`,
- `hipLaunchKernel`,
- `hipMemcpyAsync`,
- `hipMemcpy`,
- `hipDeviceSynchronize`,
- `hipStreamSynchronize`,
- `hipMalloc`,
- `hipFree`,
- `hipMemset`.

Top kernel dispatch activity includes:

- `__amd_rocclr_copyBuffer`,
- `__amd_rocclr_fillBufferAligned`,
- rocSPARSE `csrmvn_general_kernel`,
- rocBLAS `axpy`,
- rocBLAS dot and norm reduction kernels,
- custom PDLP kernels such as `primal_grad_step_kernel`,
- custom PDLP kernels such as `dual_grad_step_kernel`,
- custom movement kernels,
- custom feasibility and projection kernels.

The first-pass conclusion is:

```text
For the current small smoke cases, runtime is dominated by many small GPU operations,
kernel launches, copy/fill dispatches, rocSPARSE SpMV, rocBLAS vector kernels,
and custom PDLP update kernels. It is not yet dominated by a single custom kernel.
```

This matters because the first tuning target should not be low-level instruction tuning. The first tuning target should be reducing unnecessary launches, copies, synchronization, and repeated device-side setup.

## Interpreting small-case profiles

Small LP cases are useful for detecting obvious runtime problems, but they can exaggerate overhead.

For `afiro` and `sc50b`, the solver time is very small, so the following can dominate the profiling view:

- profiler overhead,
- runtime setup,
- repeated `hipGetDevice` calls,
- launch overhead,
- copy buffer dispatches,
- synchronization,
- small memory copies,
- small BLAS and sparse operations.

Do not overfit tuning decisions to these cases.

Use smoke profiling to identify structural problems, then validate tuning decisions on larger cases.

## Solver-level metrics to track

From solver logs and JSON summaries, track:

| Metric | Why it matters |
|---|---|
| Total solver time | End-to-end runtime |
| Solve time | Main loop runtime |
| Iteration count | Algorithmic progress |
| Iterations per second | Coarse throughput measure |
| `Ax` time | Sparse matrix-vector product direction |
| `Aty` time | Transposed sparse matrix-vector product direction |
| Device matrix-vector product time | GPU SpMV contribution |
| Allocation/copy time | Setup and data movement overhead |
| Copy-to-host time | Host readback overhead |

These should be compared before and after tuning changes.

## Runtime-level metrics to track

From `rocprofv3` HIP API summaries, track:

| Metric | Why it matters |
|---|---|
| `hipLaunchKernel` count and time | Kernel launch granularity |
| `hipMemcpyAsync` count and time | Async memory transfer frequency |
| `hipMemcpy` count and time | Synchronous transfer frequency |
| `hipDeviceSynchronize` count and time | Global synchronization overhead |
| `hipStreamSynchronize` count and time | Stream synchronization overhead |
| `hipMalloc` / `hipFree` count | Repeated allocation overhead |
| `hipMemset` count and time | Repeated device initialization overhead |
| `hipGetDevice` count and time | Repeated runtime query overhead |

A tuning change should ideally reduce one or more of these without damaging validation results.

## Kernel-level metrics to track

From `rocprofv3` kernel summaries, track:

| Kernel group | Why it matters |
|---|---|
| rocSPARSE SpMV kernels | Sparse matrix-vector product bottleneck |
| rocBLAS AXPY kernels | Vector update overhead |
| rocBLAS dot/norm reduction kernels | Reduction overhead |
| Custom gradient kernels | PDLP update cost |
| Movement kernels | Restart and movement interaction cost |
| Feasibility kernels | Termination and residual check cost |
| ROCclr copy/fill kernels | Hidden copy/fill overhead |

Hardware counters should be added later for selected kernels only.

Potential future counter topics:

- memory bandwidth,
- wavefront occupancy,
- cache behavior,
- LDS usage,
- register pressure,
- VALU utilization,
- scalar/vector instruction mix.

## First tuning priorities

Based on current profiling, the first tuning priorities are:

1. Reduce repeated synchronization.
2. Reduce repeated small memory copies.
3. Reduce repeated runtime queries inside loops.
4. Reuse device buffers where possible.
5. Avoid unnecessary device-to-device copy/fill operations.
6. Reduce kernel launch count by fusing tiny kernels where safe.
7. Investigate whether some BLAS level-1 operations can be fused into existing custom kernels.
8. Keep sparse matrix data resident on device across iterations.
9. Validate every change against CPU results.
10. Profile after every meaningful change.

## Tuning direction: synchronization

Synchronization can be expensive when it appears inside an iterative solver loop.

Investigate:

- whether `hipDeviceSynchronize()` is required at each call site,
- whether `hipStreamSynchronize()` can be replaced by dependency ordering,
- whether error checking can avoid forced synchronization in release builds,
- whether host readback can be delayed or batched,
- whether termination checks can reduce device-to-host traffic.

Any synchronization removal must be validated carefully.

## Tuning direction: memory copies

Memory copies and ROCclr copy buffer dispatches appear prominently in smoke profiles.

Investigate:

- repeated `hipMemcpy` and `hipMemcpyAsync` paths,
- device-to-device copies of scalars or small buffers,
- host readback during residual and termination checks,
- temporary buffer movement,
- whether scalar values can remain on device longer,
- whether some copy operations are caused by library scalar pointer mode.

## Tuning direction: kernel launch count

Smoke profiling shows many small kernel dispatches.

Investigate:

- custom elementwise kernels that run once per iteration,
- projection kernels,
- feasibility kernels,
- movement kernels,
- small vector update kernels,
- opportunities to fuse adjacent elementwise passes.

Fusion should be done only after correctness is stable because it can change floating-point order and make debugging harder.

## Tuning direction: rocSPARSE SpMV

PDLP relies heavily on sparse matrix-vector products.

Investigate:

- CSR vs CSC paths,
- transpose vs non-transpose SpMV performance,
- buffer allocation reuse,
- matrix descriptor reuse,
- whether preprocessing can reduce format conversion overhead,
- whether larger LP cases show stronger SpMV dominance than smoke cases.

Do not assume `afiro` or `sc50b` is representative of large sparse LP performance.

## Tuning direction: rocBLAS vector operations

rocBLAS level-1 operations appear in the trace.

Investigate:

- AXPY frequency,
- dot/norm reduction frequency,
- scaling operations,
- whether several vector operations can be fused,
- whether temporary vectors can be eliminated,
- whether reduction results force synchronization or host readback.

Any replacement of library calls with custom kernels must be benchmarked and validated.

## gfx1150 notes

The current target is an integrated AMD Radeon 890M / `gfx1150`.

For this class of GPU/APU:

- host and device memory behavior may differ from discrete GPUs,
- small copies and synchronizations can still be expensive,
- fixed launch overhead can dominate small cases,
- memory bandwidth and system memory sharing should be considered,
- small benchmark cases are especially prone to misleading performance conclusions.

Recommended interpretation:

```text
Use gfx1150 smoke profiling to find structural overhead.
Use larger cases before making final performance claims.
```

## Profiling checklist

Before tuning:

```bash
./scripts/check_rocm_port.sh
ctest --test-dir build-rocm-plc --output-on-failure
./scripts/profile_rocm_smoke.sh
```

After tuning:

```bash
./scripts/check_rocm_port.sh
ctest --test-dir build-rocm-plc --output-on-failure
./scripts/profile_rocm_smoke.sh
```

Then compare:

- validation summaries,
- solver JSON outputs,
- solver timing logs,
- `rocprofv3` HIP API summaries,
- `rocprofv3` kernel dispatch summaries.

Do not accept a tuning change that improves timing but breaks validation.

## What not to do yet

Avoid these changes until validation coverage is larger:

- removing legacy C/HIP compatibility symbols,
- rewriting sparse matrix storage,
- replacing all rocBLAS calls with custom kernels,
- replacing all hipSPARSE calls with custom SpMV kernels,
- tuning only for `afiro`,
- drawing performance conclusions from one smoke case,
- relying on hardware counters before runtime trace hotspots are understood.

## Completed profiling-driven optimizations

This section records the profiling-driven optimizations completed during the
current ROCm/HIP tuning pass on AMD Radeon 890M / `gfx1150`.

The goal of this tuning pass was not to claim full solver-level performance
maturity. The goal was to remove obvious small-case runtime overhead while
preserving correctness against the CPU baseline.

All optimizations in this section were validated with:

```bash
./scripts/check_rocm_port.sh
ctest --test-dir build-rocm-plc --output-on-failure
```

The average-iterate fusion was also checked with extended Netlib validation.

### Optimization 1: remove redundant device synchronization

The first optimization removed a redundant `hipDeviceSynchronize()` from the
ROCm/HIP movement interaction path.

Before the change, `cupdlp_movement_interaction_cuda()` explicitly synchronized
the whole device before copying three scalar results back to the host. The final
blocking `hipMemcpy(..., hipMemcpyDeviceToHost)` already provides the required
host-side ordering for reading those scalar results.

Observed effect on smoke profiles:

| Case | Before | After |
|---|---:|---:|
| `afiro` `hipDeviceSynchronize` calls | 203 | 3 |
| `sc50b` `hipDeviceSynchronize` calls | 564 | 3 |

This optimization removed loop-level global synchronization from the smoke
cases without changing numerical validation results.

### Optimization 2: cache HIP device attributes

The second optimization cached repeated device attribute queries in the HIP
linear algebra helper path.

The original helper logic queried HIP device attributes such as:

- `hipDeviceAttributeMultiprocessorCount`,
- `hipDeviceAttributeWarpSize`.

These values do not change during a single-process, single-device smoke run.
The updated code caches them through small helper functions and reuses the
cached values.

Observed effect:

| Case | After |
|---|---:|
| `afiro` `hipDeviceGetAttribute` calls | 2 |
| `sc50b` `hipDeviceGetAttribute` calls | 2 |

This optimization mainly reduces HIP runtime API noise. It is not expected to
produce a large solver-time speedup by itself.

### Optimization 3: fuse average iterate AXPY updates

The third optimization fused two per-iteration average-iterate AXPY updates.

Before the change, `PDHG_Update_Average()` performed two rocBLAS AXPY calls per
iteration:

```c
cupdlp_axpy(work, lp->nCols, &dMeanStepSize, xUpdate->data, iterates->xSum);
cupdlp_axpy(work, lp->nRows, &dMeanStepSize, yUpdate->data, iterates->ySum);
```

The ROCm/HIP path now uses one custom kernel for both updates:

```text
update_average_kernel
```

Observed smoke-profile effect:

| Metric | `afiro` before | `afiro` after | `sc50b` before | `sc50b` after |
|---|---:|---:|---:|---:|
| `hipLaunchKernel` calls | 2667 | 2468 | 6071 | 5511 |
| `rocblas_axpy_kernel` dispatches | 506 | 108 | 1270 | 150 |
| `update_average_kernel` dispatches | 0 | 199 | 0 | 560 |

This confirms that the two fixed per-iteration AXPY launches were reduced to
one custom launch per iteration.

### Optimization 4: reduce movement interaction scalar D2D copies

The fourth optimization reduced scalar device-to-device copies in
`cupdlp_movement_interaction_cuda()`.

Before the change, the movement interaction path used three scalar D2D
`hipMemcpyAsync` calls and one final scalar D2H `hipMemcpy` call. A previous
attempt to replace all three D2D copies was rejected because `buf_1` and
`buf_2` are reused later in the function, and preserving pointers was not the
same as preserving values.

The safe version only replaces the first two D2D scalar copies, before
`buf_1` and `buf_2` are reused:

```text
save_movement_xy_kernel
```

The third D2D copy and final D2H copy remain unchanged.

Observed smoke-profile effect:

| Metric | `afiro` before | `afiro` after | `sc50b` before | `sc50b` after |
|---|---:|---:|---:|---:|
| `hipMemcpyAsync` calls | 1136 | 736 | 2485 | 1363 |
| `__amd_rocclr_copyBuffer` dispatches | 1444 | 1044 | 3182 | 2060 |
| `save_movement_xy_kernel` dispatches | 0 | 200 | 0 | 561 |
| `hipLaunchKernel` calls | 2468 | 2668 | 5511 | 6072 |

This confirms that many tiny D2D copies were replaced by one small custom kernel
per movement-interaction call. Kernel launch count increased by roughly the
iteration count, but copyBuffer dispatch count decreased by roughly twice the
iteration count.

For `sc50b`, the copy analysis after this change showed:

```text
hipMemcpy + hipMemcpyAsync events: 2060
__amd_rocclr_copyBuffer dispatches: 2060
copyBuffer dispatches near HIP memcpy events: 2060
```

This confirms that the remaining `copyBuffer` activity is still directly tied
to HIP memcpy calls.

### Current post-optimization profile shape

After these optimizations, the remaining smoke-profile hotspots are:

- `hipLaunchKernel`,
- remaining `hipMemcpy` / `hipMemcpyAsync`,
- remaining `__amd_rocclr_copyBuffer`,
- rocBLAS dot and norm reduction kernels,
- rocSPARSE SpMV kernels.

The AXPY path is no longer the dominant rocBLAS issue. The remaining rocBLAS
hotspots are mostly reduction-style operations such as dot and norm, which are
higher risk to replace than AXPY.

### Optimization policy after this pass

The following areas should not be changed casually:

- the third movement-interaction scalar copy,
- dot and norm reduction kernels,
- rocSPARSE SpMV,
- full HIP Graph capture of the solver loop.

These areas require larger validation cases and more detailed profiling before
being changed.

The next recommended engineering step is to keep the current optimizations as a
validated baseline, then expand profiling and validation to larger LP instances.

## Future tuning work

Planned tuning work:

- Add a profiling summary parser for `rocprofv3` CSV output.
- Add larger LP cases for performance profiling.
- Add before/after profiling report templates.
- Add optional hardware counter collection for selected kernels.
- Add ROCTx ranges around solver phases.
- Separate setup time from main iteration time more clearly.
- Investigate scalar readback and synchronization in termination checks.
- Investigate kernel fusion opportunities.
- Investigate SpMV format and descriptor reuse.
- Compare gfx1150 with other ROCm-supported GPUs/APUs.

## Summary

The current ROCm/HIP port is validated enough to begin profiling, but not enough to claim final performance.

The first profiling result suggests that early tuning should focus on:

```text
launch count + synchronization + memory copies + SpMV + BLAS level-1 reductions
```

Only after those structural issues are understood should the project move toward low-level kernel tuning.
