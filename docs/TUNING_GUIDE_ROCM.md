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
