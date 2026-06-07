#ifndef CUPDLP_BACKEND_COMPAT_H
#define CUPDLP_BACKEND_COMPAT_H

/*
 * Backend compatibility aliases for shared C sources.
 *
 * Public build modes:
 *   CPU:       BUILD_CUDA=OFF, BUILD_ROCM=OFF
 *   CUDA:      BUILD_CUDA=ON,  BUILD_ROCM=OFF
 *   ROCm/HIP:  BUILD_CUDA=OFF, BUILD_ROCM=ON
 *
 * Shared C files should use CUPDLP_* backend aliases instead of directly
 * calling cublas/cusparse/cuda or hipblas/hipsparse/hip APIs.
 */

#if defined(CUPDLP_USE_ROCM)

#include "hip/cupdlp_hip_kernels.h"

#define CUPDLP_BLAS_CREATE          hipblasCreate
#define CUPDLP_BLAS_DESTROY         hipblasDestroy
#define CUPDLP_BLAS_DAXPY           hipblasDaxpy
#define CUPDLP_BLAS_SAXPY           hipblasSaxpy
#define CUPDLP_BLAS_DDOT            hipblasDdot
#define CUPDLP_BLAS_SDOT            hipblasSdot
#define CUPDLP_BLAS_DNRM2           hipblasDnrm2
#define CUPDLP_BLAS_SNRM2           hipblasSnrm2
#define CUPDLP_BLAS_DSCAL           hipblasDscal
#define CUPDLP_BLAS_SSCAL           hipblasSscal

#define CUPDLP_SPARSE_CREATE        hipsparseCreate
#define CUPDLP_SPARSE_DESTROY       hipsparseDestroy
#define CUPDLP_SPARSE_CREATE_CSR    hipsparseCreateCsr
#define CUPDLP_SPARSE_CREATE_CSC    hipsparseCreateCsc
#define CUPDLP_SPARSE_CREATE_DNVEC  hipsparseCreateDnVec
#define CUPDLP_SPARSE_DESTROY_DNVEC hipsparseDestroyDnVec
#define CUPDLP_SPARSE_DESTROY_SPMAT hipsparseDestroySpMat

#define CUPDLP_DEVICE_FREE          hipFree
#define CUPDLP_DEVICE_RESET         hipDeviceReset

#define CUPDLP_SPARSE_INDEX_32I       HIPSPARSE_INDEX_32I
#define CUPDLP_SPARSE_INDEX_BASE_ZERO HIPSPARSE_INDEX_BASE_ZERO
#define CUPDLP_COMPUTE_TYPE           HipComputeType

#elif defined(CUPDLP_USE_CUDA)

#include "cuda/cupdlp_cuda_kernels.cuh"

#define CUPDLP_BLAS_CREATE          cublasCreate
#define CUPDLP_BLAS_DESTROY         cublasDestroy
#define CUPDLP_BLAS_DAXPY           cublasDaxpy
#define CUPDLP_BLAS_SAXPY           cublasSaxpy
#define CUPDLP_BLAS_DDOT            cublasDdot
#define CUPDLP_BLAS_SDOT            cublasSdot
#define CUPDLP_BLAS_DNRM2           cublasDnrm2
#define CUPDLP_BLAS_SNRM2           cublasSnrm2
#define CUPDLP_BLAS_DSCAL           cublasDscal
#define CUPDLP_BLAS_SSCAL           cublasSscal

#define CUPDLP_SPARSE_CREATE        cusparseCreate
#define CUPDLP_SPARSE_DESTROY       cusparseDestroy
#define CUPDLP_SPARSE_CREATE_CSR    cusparseCreateCsr
#define CUPDLP_SPARSE_CREATE_CSC    cusparseCreateCsc
#define CUPDLP_SPARSE_CREATE_DNVEC  cusparseCreateDnVec
#define CUPDLP_SPARSE_DESTROY_DNVEC cusparseDestroyDnVec
#define CUPDLP_SPARSE_DESTROY_SPMAT cusparseDestroySpMat

#define CUPDLP_DEVICE_FREE          cudaFree
#define CUPDLP_DEVICE_RESET         cudaDeviceReset

#define CUPDLP_SPARSE_INDEX_32I       CUSPARSE_INDEX_32I
#define CUPDLP_SPARSE_INDEX_BASE_ZERO CUSPARSE_INDEX_BASE_ZERO
#define CUPDLP_COMPUTE_TYPE           CudaComputeType

#endif

#endif
