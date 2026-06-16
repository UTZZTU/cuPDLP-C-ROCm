# W7900 P11 runtime 调用点清单

本清单基于 P10 targeted rocprof 结果，对源码中的 HIP/runtime 与 sparse-BLAS 相关调用点进行定位。

P10 显示，5 个 targeted case 的 rank-1 HIP API 成本均为 `hipMemcpy`，rank-1 GPU kernel 均为 `rocsparse::csrmvn_general_kernel`。本清单是正式改代码前的 triage 步骤：先定位候选调用点，再决定是否修改。

## 汇总

匹配到的调用点总数：`95`

按优先级：

- `P0`: 22
- `P1`: 63
- `P2`: 10

按类别：

- `cublas_compat_api`: 7
- `cuda_kernel_syntax`: 56
- `cusparse_compat_api`: 11
- `hip_device_query`: 3
- `hip_malloc_free`: 5
- `hip_memcpy_async`: 1
- `hip_memcpy_sync`: 2
- `hip_memset`: 2
- `hipsparse_api`: 8

按源码角色：

- `hip-port`: 50
- `interface`: 4
- `linalg`: 34
- `other`: 7

## P0 调用点

P0 包括同步/异步 host-device copy 和 sparse SpMV 相关 API 调用。这些位置需要优先检查，但不代表一定要优先修改。

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
| P0 | `hip_memcpy_async` | `cupdlp/hip/cupdlp_hip_linalg.cpp:364` | hip-port | `CHECK_HIP_STRICT(hipMemcpyAsync(buf_5 + 2, buf_1, sizeof(cupdlp_float), hipMemcpyDeviceToDevice))` |
| P0 | `hip_memcpy_sync` | `cupdlp/hip/cupdlp_hip_kernels.h:106` | hip-port | `hipMemcpy(dst, src, sizeof(type) * (size), hipMemcpyDefault), \` |
| P0 | `hip_memcpy_sync` | `cupdlp/hip/cupdlp_hip_linalg.cpp:365` | hip-port | `CHECK_HIP_STRICT(hipMemcpy(res, buf_5, 3 * sizeof(cupdlp_float), hipMemcpyDeviceToHost))` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_kernels.h:46` | hip-port | `line, filename, hipsparseGetErrorString(status), status);` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:49` | hip-port | `CHECK_HIPSPARSE(hipsparseSpMV_bufferSize(` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:57` | hip-port | `CHECK_HIPSPARSE(hipsparseSpMV_bufferSize(` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:77` | hip-port | `CHECK_HIPSPARSE(hipsparseSpMV(handle, op, &alpha, hip_csc, vecX, &beta, vecAx,` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:94` | hip-port | `CHECK_HIPSPARSE(hipsparseSpMV(handle, op, &alpha, hip_csr, vecX, &beta, vecAx,` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:109` | hip-port | `CHECK_HIPSPARSE(hipsparseSpMV(handle, op, &alpha, hip_csc, vecY, &beta, vecATy,` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:125` | hip-port | `CHECK_HIPSPARSE(hipsparseSpMV(handle, op, &alpha, hip_csr, vecY, &beta, vecATy,` |
| P0 | `hipsparse_api` | `cupdlp/hip/cupdlp_hip_linalg.cpp:382` | hip-port | `CHECK_HIPSPARSE(hipsparseGetVersion(handle, &v_hipsparse))` |

## P1 调用点

P1 包括 kernel launch 语法、同步调用和 BLAS 调用，可用于解释 kernel launch 数量或 reduction 开销。

| priority | category | file:line | role | snippet |
|---|---|---|---|---|
| P1 | `cublas_compat_api` | `apps/onlinelp.cpp:99` | other | `CHECK_CUBLAS(cublasCreate(&w->cublashandle));` |
| P1 | `cublas_compat_api` | `cupdlp/cuda/test_cublas.c:37` | other | `CHECK_CUBLAS(cublasDnrm2(cublashandle, len, d_vec1, 1, &result));` |
| P1 | `cublas_compat_api` | `cupdlp/cuda/test_cublas.c:119` | other | `CHECK_CUBLAS(cublasCreate(&cublashandle));` |
| P1 | `cublas_compat_api` | `cupdlp/cuda/test_cublas.c:147` | other | `CHECK_CUBLAS(cublasDestroy(cublashandle));` |
| P1 | `cublas_compat_api` | `interface/mps_abip.c:190` | interface | `CHECK_CUBLAS(cublasCreate(&w->cublashandle));` |
| P1 | `cublas_compat_api` | `interface/mps_clp.c:157` | interface | `CHECK_CUBLAS(cublasCreate(&w->cublashandle));` |
| P1 | `cublas_compat_api` | `pycupdlp/cupdlp_bindings.cpp:390` | other | `CHECK_CUBLAS(cublasCreate(&w->cublashandle));` |
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
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:223` | hip-port | `element_wise_dot_kernel<<<nBlocks256(n), 256>>>(x, y, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:228` | hip-port | `element_wise_initHaslb_kernel<<<nBlocks256(n), 256>>>(haslb, lb, bound, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:233` | hip-port | `element_wise_initHasub_kernel<<<nBlocks256(n), 256>>>(hasub, ub, bound, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:238` | hip-port | `element_wise_filterlb_kernel<<<nBlocks256(n), 256>>>(x, lb, bound, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:243` | hip-port | `element_wise_filterub_kernel<<<nBlocks256(n), 256>>>(x, ub, bound, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:247` | hip-port | `init_cuda_vec_kernel<<<nBlocks256(n), 256>>>(x, val, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:254` | hip-port | `primal_grad_step_kernel<<<nBlocks256(nCols), 256>>>(xUpdate, x, cost, ATy, lb, ub, dPrimalStep, nCols);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:261` | hip-port | `dual_grad_step_kernel<<<nBlocks256(nRows), 256>>>(yUpdate, y, b, Ax, AxUpdate, dDualStep, nRows, nEqs);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:272` | hip-port | `update_average_kernel<<<nBlocks256(n), 256>>>(xSum, xUpdate, ySum, yUpdate,` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:280` | hip-port | `naive_sub_kernel<<<nBlocks256(n), 256>>>(z, x, y, n);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:334` | hip-port | `movement_1_kernel<<<nBlocks, RED_BLOCK_SIZE>>>(buf_1, buf_2, xUpdate, x, atyUpdate, aty, nCols);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:338` | hip-port | `sum_kernel<<<nBlocks2, SUM_BLOCK_SIZE>>>(buf_3, buf_1, nBlocks);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:339` | hip-port | `sum_kernel<<<nBlocks2, SUM_BLOCK_SIZE>>>(buf_4, buf_2, nBlocks);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:349` | hip-port | `save_movement_xy_kernel<<<1, 1>>>(buf_5, buf_1, buf_2);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:352` | hip-port | `movement_2_kernel<<<nBlocks, RED_BLOCK_SIZE>>>(buf_1, yUpdate, y, nRows);` |
| P1 | `cuda_kernel_syntax` | `cupdlp/hip/cupdlp_hip_linalg.cpp:356` | hip-port | `sum_kernel<<<nBlocks2, SUM_BLOCK_SIZE>>>(buf_2, buf_1, nBlocks);` |

## 调优解释

不要盲目删除 copy 或同步。对于 PDLP，residual 检查、restart 逻辑、termination 判断、scaling 和 objective/gap 输出都可能依赖 host 可见值的时序。因此第一个安全的 P11 优化候选应满足：

1. 只属于执行层优化。
2. 不改变 residual、restart、termination、scaling 或浮点更新顺序。
3. 能在 P10 五个 targeted case 和 fast-core6 集合上验证。
4. 至少改善 HIP API calls、`hipMemcpy` time/count、kernel dispatch count 或 ms/iter 中的一项。
5. 保持 status、gap、primal infeasibility 和 dual infeasibility 正常。

## 文件

- `w7900_p11_runtime_callsite_inventory_20260617.csv`
