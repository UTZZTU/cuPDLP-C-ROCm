#ifndef CUPDLP_HIP_KERNELS_H
#define CUPDLP_HIP_KERNELS_H

#include <stdio.h>
#include <stdlib.h>  /* EXIT_FAILURE */
#include <hipblas/hipblas.h>
#include <hipsparse/hipsparse.h>
#include <hip/hip_runtime.h>

//#define CUPDLP_BLOCK_SIZE 512

#ifndef SFLOAT

#ifdef DLONG
typedef long long cupdlp_int;
#else
typedef int cupdlp_int;
#endif
typedef double cupdlp_float;
#define HipComputeType HIP_R_64F
#define cupdlp_fma_rn __fma_rn

#else

typedef float cupdlp_float;
#define HipComputeType HIP_R_32F
#define cupdlp_fma_rn __fmaf_rn

#endif

static inline hipError_t check_cuda_call(hipError_t status,
                                          const char *filename, int line)
{
  if (status != hipSuccess) {
    printf("HIP API failed at line %d of %s with error: %s (%d)\n",
      line, filename, hipGetErrorString(status), status);
  }
  return status;
}

static inline hipsparseStatus_t check_cusparse_call(hipsparseStatus_t status,
                                                   const char *filename, int line)
{
  if (status != HIPSPARSE_STATUS_SUCCESS) {
    printf("hipSPARSE API failed at line %d of %s with error: %s (%d)\n",
      line, filename, hipsparseGetErrorString(status), status);
  }
  return status;
}

static inline hipblasStatus_t check_cublas_call(hipblasStatus_t status,
                                               const char *filename, int line)
{
  if (status != HIPBLAS_STATUS_SUCCESS) {
    printf("hipBLAS API failed at line %d of %s with error: %s (%d)\n",
      line, filename, "hipBLAS error", status);
  }
  return status;
}

static inline hipError_t check_cuda_last(const char *filename, int line)
{
  hipError_t status = hipGetLastError();
  if (status != hipSuccess) {
    printf("HIP API failed at line %d of %s with error: %s (%d)\n",
      line, filename, hipGetErrorString(status), status);
  }
  return status;
}

#define CHECK_CUDA(res) \
  { if (check_cuda_call(res, __FILE__, __LINE__) != hipSuccess) \
      return EXIT_FAILURE; }
#define CHECK_CUDA_STRICT(res) \
  { if (check_cuda_call(res, __FILE__, __LINE__) != hipSuccess) \
      exit(EXIT_FAILURE); }
#define CHECK_CUDA_IGNORE(res) \
  { check_cuda_call(res, __FILE__, __LINE__); }

#define CHECK_CUSPARSE(res) \
  { if (check_cusparse_call(res, __FILE__, __LINE__) != HIPSPARSE_STATUS_SUCCESS) \
      return EXIT_FAILURE; }
#define CHECK_CUSPARSE_STRICT(res) \
  { if (check_cusparse_call(res, __FILE__, __LINE__) != HIPSPARSE_STATUS_SUCCESS) \
      exit(EXIT_FAILURE); }
#define CHECK_CUSPARSE_IGNORE(res) \
  { check_cusparse_call(res, __FILE__, __LINE__); }

#define CHECK_CUBLAS(res) \
  { if (check_cublas_call(res, __FILE__, __LINE__) != HIPBLAS_STATUS_SUCCESS) \
      return EXIT_FAILURE; }
#define CHECK_CUBLAS_STRICT(res) \
  { if (check_cublas_call(res, __FILE__, __LINE__) != HIPBLAS_STATUS_SUCCESS) \
      exit(EXIT_FAILURE); }
#define CHECK_CUBLAS_IGNORE(res) \
  { check_cublas_call(res, __FILE__, __LINE__); }

#define CHECK_CUDA_LAST() check_cuda_last(__FILE__, __LINE__)


#define CUPDLP_FREE_VEC(x) \
  { check_cuda_call(hipFree(x), __FILE__, __LINE__); x = cupdlp_NULL; }

#define CUPDLP_COPY_VEC(dst, src, type, size) \
  check_cuda_call( \
    hipMemcpy(dst, src, sizeof(type) * (size), hipMemcpyDefault), \
    __FILE__, __LINE__)

#define CUPDLP_ZERO_VEC(var, type, size) \
  check_cuda_call( \
    hipMemset(var, 0, sizeof(type) * (size)), __FILE__, __LINE__)

#define CUPDLP_INIT_VEC(var, size)                                             \
  {                                                                            \
    hipError_t status = hipMalloc((void **)&var, (size) * sizeof(__typeof__(*var))); \
    check_cuda_call(status, __FILE__, __LINE__);                               \
    if (status != hipSuccess) goto exit_cleanup;                              \
  }

#define CUPDLP_INIT_ZERO_VEC(var, size)                                         \
  {                                                                            \
    hipError_t status = hipMalloc((void **)&var, (size) * sizeof(__typeof__(*var))); \
    check_cuda_call(status, __FILE__, __LINE__);                               \
    if (status != hipSuccess) goto exit_cleanup;                              \
    status = hipMemset(var, 0, (size) * sizeof(__typeof__(*var)));            \
    if (status != hipSuccess) goto exit_cleanup;                              \
  }


__global__ void element_primal_feas_kernel(cupdlp_float *z,
                                           const cupdlp_float *ax,
                                           const cupdlp_float *rhs,
                                           const cupdlp_float *rowScale,
                                           int ifScaled,
                                           int nEqs, int nRows);

__global__ void element_dual_feas_kernel_1(cupdlp_float *z,
                                           const cupdlp_float *aty,
                                           const cupdlp_float *cost,
                                           int nCols);

__global__ void element_dual_feas_kernel_2(cupdlp_float *z,
                                           const cupdlp_float *dualResidual,
                                           const cupdlp_float *hasLower,
                                           int nCols);

__global__ void element_dual_feas_kernel_3(cupdlp_float *z,
                                           const cupdlp_float *dualResidual,
                                           const cupdlp_float *hasUpper,
                                           int nCols);

__global__ void element_primal_infeas_kernel(cupdlp_float *z, const cupdlp_float *aty,
                                             const cupdlp_float *dSlackPos,
                                             const cupdlp_float *dSlackNeg,
                                             const cupdlp_float *colScale,
                                             cupdlp_float alpha, int ifScaled, int nCols);

__global__ void element_dual_infeas_kernel_lb(cupdlp_float *z,
                                              const cupdlp_float *x,
                                              const cupdlp_float *hasLower,
                                              const cupdlp_float *colScale,
                                              cupdlp_float alpha, int ifScaled, int nCols);

__global__ void element_dual_infeas_kernel_ub(cupdlp_float *z,
                                              const cupdlp_float *x,
                                              const cupdlp_float *hasUpper,
                                              const cupdlp_float *colScale,
                                              cupdlp_float alpha, int ifScaled, int nCols);

__global__ void element_dual_infeas_kernel_constr(cupdlp_float *z,
                                                  const cupdlp_float *ax,
                                                  const cupdlp_float *rowScale,
                                                  cupdlp_float alpha, int ifScaled,
                                                  int nEqs, int nRows);

__global__ void element_wise_dot_kernel(cupdlp_float *x, const cupdlp_float *y, int n);

__global__ void element_wise_div_kernel(cupdlp_float *x, const cupdlp_float *y, int n);

__global__ void element_wise_projlb_kernel(cupdlp_float *x,
                                           const cupdlp_float *lb, int n);

__global__ void element_wise_projub_kernel(cupdlp_float *x,
                                           const cupdlp_float *ub, int n);

__global__ void element_wise_projSamelb_kernel(cupdlp_float *x,
                                               cupdlp_float lb, int n);

__global__ void element_wise_projSameub_kernel(cupdlp_float *x,
                                               cupdlp_float ub, int n);

__global__ void element_wise_initHaslb_kernel(cupdlp_float *haslb,
                                              const cupdlp_float *lb,
                                              cupdlp_float bound, int n);

__global__ void element_wise_initHasub_kernel(cupdlp_float *hasub,
                                              const cupdlp_float *ub,
                                              cupdlp_float bound, int n);

__global__ void element_wise_filterlb_kernel(cupdlp_float *x,
                                             const cupdlp_float *lb,
                                             cupdlp_float bound, int n);

__global__ void element_wise_filterub_kernel(cupdlp_float *x,
                                             const cupdlp_float *ub,
                                             cupdlp_float bound, int n);

__global__ void init_cuda_vec_kernel(cupdlp_float *x, cupdlp_float val, int n);

__global__ void primal_grad_step_kernel(cupdlp_float * __restrict__ xUpdate,
                                        const cupdlp_float * __restrict__ x,
                                        const cupdlp_float * __restrict__ cost,
                                        const cupdlp_float * __restrict__ ATy,
                                        const cupdlp_float * __restrict__ lb,
                                        const cupdlp_float * __restrict__ ub,
                                        cupdlp_float dPrimalStep, int nCols);

__global__ void dual_grad_step_kernel(cupdlp_float * __restrict__ yUpdate,
                                      const cupdlp_float * __restrict__ y,
                                      const cupdlp_float * __restrict__ b,
                                      const cupdlp_float * __restrict__ Ax,
                                      const cupdlp_float * __restrict__ AxUpdate,
                                      cupdlp_float dDualStep, int nRows, int nEqs);

/*
__global__ void naive_sub_kernel(cupdlp_float *z, const cupdlp_float *x,
                                 const cupdlp_float *y, int n);
*/


__global__ void movement_1_kernel(cupdlp_float * __restrict__ res_x, cupdlp_float * __restrict__ res_y,
                                  const cupdlp_float * __restrict__ xUpdate, const cupdlp_float * __restrict__ x,
                                  const cupdlp_float * __restrict__ atyUpdate, const cupdlp_float * __restrict__ aty,
                                  int nCols);

__global__ void movement_2_kernel(cupdlp_float * __restrict__ res,
                                  const cupdlp_float * __restrict__ yUpdate, const cupdlp_float * __restrict__ y,
                                  int nRows);

__global__ void sum_kernel(cupdlp_float * __restrict__ res, const cupdlp_float * __restrict__ x, int n);

#endif
