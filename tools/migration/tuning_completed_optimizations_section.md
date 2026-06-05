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
