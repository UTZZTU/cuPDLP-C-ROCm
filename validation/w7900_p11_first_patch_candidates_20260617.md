# W7900 P11 first patch candidates

This report combines P10 targeted rocprof data with the P11 runtime callsite inventory to choose the first safe optimization direction.

## Input evidence

- P10 runtime CSV: `w7900_p10_current_targeted_rocprof_20260617_runtime.csv`
- P10 HIP API top CSV: `w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv`
- P10 kernel top CSV: `w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv`
- P11 inventory CSV: `w7900_p11_runtime_callsite_inventory_20260617.csv`

All targeted cases OPTIMAL: `True`

Targeted cases: `L2CTA3D, set-cover-model, square41, thk_48, tpl-tub-ws1617`

## Runtime pressure points

| case | status | nIter | solve s | HIP API calls | HIP ms | kernel dispatches | kernel ms | kernel dispatches / iter | HIP ms / iter |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L2CTA3D | OPTIMAL | 80 | 0.533784 | 4533 | 1270.0 | 2991 | 435.076 | 37.388 | 15.875 |
| set-cover-model | OPTIMAL | 7480 | 12.011 | 164440 | 12220.9 | 138676 | 10470.4 | 18.540 | 1.634 |
| square41 | OPTIMAL | 128360 | 115.577 | 2470120 | 112513.0 | 2049235 | 96132.6 | 15.965 | 0.876542 |
| thk_48 | OPTIMAL | 17720 | 69.485 | 396979 | 69824.5 | 337117 | 65716.9 | 19.025 | 3.940 |
| tpl-tub-ws1617 | OPTIMAL | 82600 | 103.876 | 1667279 | 102111.0 | 1395714 | 90161.0 | 16.897 | 1.236 |

## Rank-1 hotspots by case

| case | rank-1 HIP API | rank-1 kernel |
|---|---|---|
| L2CTA3D | `hipMemcpy` | `rocsparse::csrmvn_general_kernel` |
| set-cover-model | `hipMemcpy` | `rocsparse::csrmvn_general_kernel` |
| square41 | `hipMemcpy` | `rocsparse::csrmvn_general_kernel` |
| thk_48 | `hipMemcpy` | `rocsparse::csrmvn_general_kernel` |
| tpl-tub-ws1617 | `hipMemcpy` | `rocsparse::csrmvn_general_kernel` |

## Candidate ranking

| rank | candidate | expected effect | risk | recommendation |
|---:|---|---|---|---|
| 1 | copy-reduction triage around scalar host reads | reduce hipMemcpy time/count if repeated scalar D2H copies are confirmed | high if tied to residual/restart/termination decisions | inspect callsites first; do not remove numerical host reads blindly |
| 2 | SpMV profiling and algorithm sweep | reduce dominant rocsparse CSR SpMV kernel time | medium because SpMV algorithm can alter determinism or summation order | make an opt-in experiment flag before changing default behavior |
| 3 | kernel launch volume cleanup for vector/reduction helper kernels | reduce launch count and small-kernel overhead | medium if fusion changes floating-point order | only fuse execution-equivalent helper kernels with identical update order |
| 4 | device-query and allocation cleanup | reduce startup overhead on short cases | low | lower priority because long cases are dominated by copy/SpMV/launch |

## Relevant callsites

### Copy callsites

| priority | category | file:line | role | snippet |
|---|---|---|---|---|
| P0 | `hip_memcpy_async` | `cupdlp/hip/cupdlp_hip_linalg.cpp:364` | hip-port | `CHECK_HIP_STRICT(hipMemcpyAsync(buf_5 + 2, buf_1, sizeof(cupdlp_float), hipMemcpyDeviceToDevice))` |
| P0 | `hip_memcpy_sync` | `cupdlp/hip/cupdlp_hip_kernels.h:106` | hip-port | `hipMemcpy(dst, src, sizeof(type) * (size), hipMemcpyDefault), \` |
| P0 | `hip_memcpy_sync` | `cupdlp/hip/cupdlp_hip_linalg.cpp:365` | hip-port | `CHECK_HIP_STRICT(hipMemcpy(res, buf_5, 3 * sizeof(cupdlp_float), hipMemcpyDeviceToHost))` |

### SpMV / sparse-BLAS callsites

| priority | category | file:line | role | snippet |
|---|---|---|---|---|
| P0 | `cusparse_compat_api` | `apps/onlinelp.cpp:98` | other | `CHECK_CUSPARSE(cusparseCreate(&w->cusparsehandle));` |
| P0 | `cusparse_compat_api` | `cupdlp/cuda/cupdlp_cudalinalg.cu:29` | linalg | `CHECK_CUSPARSE(cusparseSpMV_bufferSize(` |
| P0 | `cusparse_compat_api` | `cupdlp/cuda/cupdlp_cudalinalg.cu:37` | linalg | `CHECK_CUSPARSE(cusparseSpMV_bufferSize(` |
| P0 | `cusparse_compat_api` | `cupdlp/cuda/cupdlp_cudalinalg.cu:57` | linalg | `CHECK_CUSPARSE(cusparseSpMV(handle, op, &alpha, cuda_csc, vecX, &beta, vecAx,` |
| P0 | `cusparse_compat_api` | `cupdlp/cuda/cupdlp_cudalinalg.cu:74` | linalg | `CHECK_CUSPARSE(cusparseSpMV(handle, op, &alpha, cuda_csr, vecX, &beta, vecAx,` |
| P0 | `cusparse_compat_api` | `cupdlp/cuda/cupdlp_cudalinalg.cu:89` | linalg | `CHECK_CUSPARSE(cusparseSpMV(handle, op, &alpha, cuda_csc, vecY, &beta, vecATy,` |
| P0 | `cusparse_compat_api` | `cupdlp/cuda/cupdlp_cudalinalg.cu:105` | linalg | `CHECK_CUSPARSE(cusparseSpMV(handle, op, &alpha, cuda_csr, vecY, &beta, vecATy,` |
| P0 | `cusparse_compat_api` | `cupdlp/cuda/cupdlp_cudalinalg.cu:353` | linalg | `CHECK_CUSPARSE(cusparseGetVersion(handle, &v_cusparse))` |
| P0 | `cusparse_compat_api` | `interface/mps_abip.c:189` | interface | `CHECK_CUSPARSE(cusparseCreate(&w->cusparsehandle));` |
| P0 | `cusparse_compat_api` | `interface/mps_clp.c:156` | interface | `CHECK_CUSPARSE(cusparseCreate(&w->cusparsehandle));` |
| P0 | `cusparse_compat_api` | `pycupdlp/cupdlp_bindings.cpp:389` | other | `CHECK_CUSPARSE(cusparseCreate(&w->cusparsehandle));` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_kernels.h:46` | hip-port | `line, filename, hipsparseGetErrorString(status), status);` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:49` | hip-port | `CHECK_HIPSPARSE(hipsparseSpMV_bufferSize(` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:57` | hip-port | `CHECK_HIPSPARSE(hipsparseSpMV_bufferSize(` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:77` | hip-port | `CHECK_HIPSPARSE(hipsparseSpMV(handle, op, &alpha, hip_csc, vecX, &beta, vecAx,` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:94` | hip-port | `CHECK_HIPSPARSE(hipsparseSpMV(handle, op, &alpha, hip_csr, vecX, &beta, vecAx,` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:109` | hip-port | `CHECK_HIPSPARSE(hipsparseSpMV(handle, op, &alpha, hip_csc, vecY, &beta, vecATy,` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:125` | hip-port | `CHECK_HIPSPARSE(hipsparseSpMV(handle, op, &alpha, hip_csr, vecY, &beta, vecATy,` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:382` | hip-port | `CHECK_HIPSPARSE(hipsparseGetVersion(handle, &v_hipsparse))` |

### Kernel launch callsites

| priority | category | file:line | role | snippet |
|---|---|---|---|---|
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:119` | linalg | `element_primal_feas_kernel<<<nBlocks256(nRows), 256>>>(z, ax, rhs, rowScale,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:127` | linalg | `element_dual_feas_kernel_1<<<nBlocks256(nCols), 256>>>(z, aty, cost, nCols);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:134` | linalg | `element_dual_feas_kernel_2<<<nBlocks256(nCols), 256>>>(z, dualResidual,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:142` | linalg | `element_dual_feas_kernel_3<<<nBlocks256(nCols), 256>>>(z, dualResidual,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:151` | linalg | `element_primal_infeas_kernel<<<nBlocks256(nCols), 256>>>(z, aty, dSlackPos,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:160` | linalg | `element_dual_infeas_kernel_lb<<<nBlocks256(nCols), 256>>>(z, x, hasLower,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:169` | linalg | `element_dual_infeas_kernel_ub<<<nBlocks256(nCols), 256>>>(z, x, hasUpper,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:178` | linalg | `element_dual_infeas_kernel_constr<<<nBlocks256(nRows), 256>>>(z, ax, rowScale,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:183` | linalg | `element_wise_projSameub_kernel<<<nBlocks256(n), 256>>>(x, ub, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:187` | linalg | `element_wise_projSamelb_kernel<<<nBlocks256(n), 256>>>(x, lb, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:191` | linalg | `element_wise_projub_kernel<<<nBlocks256(n), 256>>>(x, ub, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:195` | linalg | `element_wise_projlb_kernel<<<nBlocks256(n), 256>>>(x, lb, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:199` | linalg | `element_wise_div_kernel<<<nBlocks256(n), 256>>>(x, y, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:203` | linalg | `element_wise_dot_kernel<<<nBlocks256(n), 256>>>(x, y, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:208` | linalg | `element_wise_initHaslb_kernel<<<nBlocks256(n), 256>>>(haslb, lb, bound, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:213` | linalg | `element_wise_initHasub_kernel<<<nBlocks256(n), 256>>>(hasub, ub, bound, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:218` | linalg | `element_wise_filterlb_kernel<<<nBlocks256(n), 256>>>(x, lb, bound, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:223` | linalg | `element_wise_filterub_kernel<<<nBlocks256(n), 256>>>(x, ub, bound, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:227` | linalg | `init_cuda_vec_kernel<<<nBlocks256(n), 256>>>(x, val, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:234` | linalg | `primal_grad_step_kernel<<<nBlocks256(nCols), 256>>>(xUpdate, x, cost, ATy, lb, ub, dPrimalStep, nCols);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:241` | linalg | `dual_grad_step_kernel<<<nBlocks256(nRows), 256>>>(yUpdate, y, b, Ax, AxUpdate, dDualStep, nRows, nEqs);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:248` | linalg | `naive_sub_kernel<<<nBlocks256(n), 256>>>(z, x, y, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:303` | linalg | `movement_1_kernel<<<nBlocks, RED_BLOCK_SIZE>>>(buf_1, buf_2, xUpdate, x, atyUpdate, aty, nCols);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:307` | linalg | `sum_kernel<<<nBlocks2, SUM_BLOCK_SIZE>>>(buf_3, buf_1, nBlocks);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:308` | linalg | `sum_kernel<<<nBlocks2, SUM_BLOCK_SIZE>>>(buf_4, buf_2, nBlocks);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:322` | linalg | `movement_2_kernel<<<nBlocks, RED_BLOCK_SIZE>>>(buf_1, yUpdate, y, nRows);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/cuda/cupdlp_cudalinalg.cu:326` | linalg | `sum_kernel<<<nBlocks2, SUM_BLOCK_SIZE>>>(buf_2, buf_1, nBlocks);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:139` | hip-port | `element_primal_feas_kernel<<<nBlocks256(nRows), 256>>>(z, ax, rhs, rowScale,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:147` | hip-port | `element_dual_feas_kernel_1<<<nBlocks256(nCols), 256>>>(z, aty, cost, nCols);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:154` | hip-port | `element_dual_feas_kernel_2<<<nBlocks256(nCols), 256>>>(z, dualResidual,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:162` | hip-port | `element_dual_feas_kernel_3<<<nBlocks256(nCols), 256>>>(z, dualResidual,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:171` | hip-port | `element_primal_infeas_kernel<<<nBlocks256(nCols), 256>>>(z, aty, dSlackPos,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:180` | hip-port | `element_dual_infeas_kernel_lb<<<nBlocks256(nCols), 256>>>(z, x, hasLower,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:189` | hip-port | `element_dual_infeas_kernel_ub<<<nBlocks256(nCols), 256>>>(z, x, hasUpper,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:198` | hip-port | `element_dual_infeas_kernel_constr<<<nBlocks256(nRows), 256>>>(z, ax, rowScale,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:203` | hip-port | `element_wise_projSameub_kernel<<<nBlocks256(n), 256>>>(x, ub, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:207` | hip-port | `element_wise_projSamelb_kernel<<<nBlocks256(n), 256>>>(x, lb, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:211` | hip-port | `element_wise_projub_kernel<<<nBlocks256(n), 256>>>(x, ub, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:215` | hip-port | `element_wise_projlb_kernel<<<nBlocks256(n), 256>>>(x, lb, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:219` | hip-port | `element_wise_div_kernel<<<nBlocks256(n), 256>>>(x, y, n);` |
| ... | ... | ... | ... | truncated; see CSV for all 56 rows |

### Synchronization callsites

| priority | category | file:line | role | snippet |
|---|---|---|---|---|

## Recommendation

The first real P11 patch should not blindly delete `hipMemcpy` callsites. The safest next step is to inspect whether the repeated `hipMemcpy` pressure comes from scalar host reads required by residual, restart, or termination logic. If yes, those copies are numerically meaningful and should only be reduced through a guarded experiment with explicit validation. In parallel, SpMV algorithm tuning should be implemented as an opt-in experiment flag rather than a default behavior change, because it may affect determinism or floating-point summation order.

Therefore, the next code patch should be one of:

1. an opt-in profiling/experiment switch for SpMV algorithm selection; or
2. a narrow scalar-copy experiment behind a compile-time/runtime flag, with P10 and fast-core6 validation.
