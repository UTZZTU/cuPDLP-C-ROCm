#!/usr/bin/env python3
from pathlib import Path

root = Path(".")
linalg_cpp = root / "cupdlp/hip/cupdlp_hip_linalg.cpp"
linalg_h = root / "cupdlp/hip/cupdlp_hip_linalg.h"
kernels_cpp = root / "cupdlp/hip/cupdlp_hip_kernels.cpp"
kernels_h = root / "cupdlp/hip/cupdlp_hip_kernels.h"
step_c = root / "cupdlp/cupdlp_step.c"

for path in (linalg_cpp, linalg_h, kernels_cpp, kernels_h, step_c):
    if not path.exists():
        raise SystemExit(f"missing file: {path}")

h = kernels_h.read_text(encoding="utf-8")
decl_anchor = "__global__ void sum_kernel(cupdlp_float * __restrict__ res, const cupdlp_float * __restrict__ x, int n);\n"
decl_new = (
    decl_anchor
    + "\n__global__ void update_average_kernel(cupdlp_float * __restrict__ x_sum,\n"
    + "                                      const cupdlp_float * __restrict__ x_update,\n"
    + "                                      cupdlp_float * __restrict__ y_sum,\n"
    + "                                      const cupdlp_float * __restrict__ y_update,\n"
    + "                                      cupdlp_float alpha,\n"
    + "                                      int n_cols,\n"
    + "                                      int n_rows);\n"
)
if "update_average_kernel" not in h:
    if decl_anchor not in h:
        raise SystemExit("could not find sum_kernel declaration anchor in cupdlp_hip_kernels.h")
    h = h.replace(decl_anchor, decl_new, 1)
    kernels_h.write_text(h, encoding="utf-8")
    print(f"updated {kernels_h}")
else:
    print(f"skip {kernels_h}: update_average_kernel already present")

cpp = kernels_cpp.read_text(encoding="utf-8")
definition = """
__global__ void update_average_kernel(cupdlp_float * __restrict__ x_sum,
                                      const cupdlp_float * __restrict__ x_update,
                                      cupdlp_float * __restrict__ y_sum,
                                      const cupdlp_float * __restrict__ y_update,
                                      cupdlp_float alpha,
                                      int n_cols,
                                      int n_rows) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n_cols) {
    x_sum[i] += alpha * x_update[i];
  }
  if (i < n_rows) {
    y_sum[i] += alpha * y_update[i];
  }
}
"""
if "update_average_kernel" not in cpp:
    sum_def_start = cpp.find("__global__ void sum_kernel(")
    if sum_def_start == -1:
        raise SystemExit("could not find sum_kernel definition anchor in cupdlp_hip_kernels.cpp")
    next_global = cpp.find("\n__global__ void", sum_def_start + 1)
    if next_global == -1:
        cpp = cpp.rstrip() + "\n" + definition + "\n"
    else:
        cpp = cpp[:next_global] + "\n" + definition + cpp[next_global:]
    kernels_cpp.write_text(cpp, encoding="utf-8")
    print(f"updated {kernels_cpp}")
else:
    print(f"skip {kernels_cpp}: update_average_kernel already present")

lh = linalg_h.read_text(encoding="utf-8")
proto_anchor = """void cupdlp_dgrad_cuda(cupdlp_float *yUpdate,
                       const cupdlp_float *y, const cupdlp_float *b,
                       const cupdlp_float *Ax, const cupdlp_float *AxUpdate,
                       cupdlp_float dDualStep, int nRows, int nEqs);
"""
proto_new = proto_anchor + """
void cupdlp_update_average_cuda(cupdlp_float *xSum,
                                const cupdlp_float *xUpdate,
                                cupdlp_float *ySum,
                                const cupdlp_float *yUpdate,
                                cupdlp_float dMeanStepSize,
                                int nCols,
                                int nRows);
"""
if "cupdlp_update_average_cuda" not in lh:
    if proto_anchor not in lh:
        raise SystemExit("could not find cupdlp_dgrad_cuda prototype anchor in cupdlp_hip_linalg.h")
    lh = lh.replace(proto_anchor, proto_new, 1)
    linalg_h.write_text(lh, encoding="utf-8")
    print(f"updated {linalg_h}")
else:
    print(f"skip {linalg_h}: cupdlp_update_average_cuda already present")

lc = linalg_cpp.read_text(encoding="utf-8")
wrapper = """
void cupdlp_update_average_cuda(cupdlp_float *xSum,
                                const cupdlp_float *xUpdate,
                                cupdlp_float *ySum,
                                const cupdlp_float *yUpdate,
                                cupdlp_float dMeanStepSize,
                                int nCols,
                                int nRows) {
  int n = std::max(nCols, nRows);
  update_average_kernel<<<nBlocks256(n), 256>>>(xSum, xUpdate, ySum, yUpdate,
                                                dMeanStepSize, nCols, nRows);
}
"""
if "void cupdlp_update_average_cuda(" not in lc:
    impl_anchor = """void cupdlp_dgrad_cuda(cupdlp_float *yUpdate,
                       const cupdlp_float *y, const cupdlp_float *b,
                       const cupdlp_float *Ax, const cupdlp_float *AxUpdate,
                       cupdlp_float dDualStep, int nRows, int nEqs) {
  dual_grad_step_kernel<<<nBlocks256(nRows), 256>>>(yUpdate, y, b, Ax, AxUpdate, dDualStep, nRows, nEqs);
}
"""
    if impl_anchor not in lc:
        raise SystemExit("could not find cupdlp_dgrad_cuda implementation anchor in cupdlp_hip_linalg.cpp")
    lc = lc.replace(impl_anchor, impl_anchor + wrapper, 1)
    linalg_cpp.write_text(lc, encoding="utf-8")
    print(f"updated {linalg_cpp}")
else:
    print(f"skip {linalg_cpp}: cupdlp_update_average_cuda already present")

sc = step_c.read_text(encoding="utf-8")
old = """  cupdlp_axpy(work, lp->nCols, &dMeanStepSize, xUpdate->data, iterates->xSum);
  cupdlp_axpy(work, lp->nRows, &dMeanStepSize, yUpdate->data, iterates->ySum);

  stepsize->dSumPrimalStep += dMeanStepSize;
  stepsize->dSumDualStep += dMeanStepSize;
"""
new = """#if !(CUPDLP_CPU) && USE_KERNELS
  cupdlp_update_average_cuda(iterates->xSum, xUpdate->data,
                             iterates->ySum, yUpdate->data,
                             dMeanStepSize, (int)lp->nCols, (int)lp->nRows);
#else
  cupdlp_axpy(work, lp->nCols, &dMeanStepSize, xUpdate->data, iterates->xSum);
  cupdlp_axpy(work, lp->nRows, &dMeanStepSize, yUpdate->data, iterates->ySum);
#endif

  stepsize->dSumPrimalStep += dMeanStepSize;
  stepsize->dSumDualStep += dMeanStepSize;
"""
if old in sc:
    sc = sc.replace(old, new, 1)
elif "cupdlp_update_average_cuda(iterates->xSum" in sc:
    print(f"skip {step_c}: PDHG_Update_Average already updated")
else:
    raise SystemExit("could not find PDHG_Update_Average axpy block in cupdlp_step.c")

step_c.write_text(sc, encoding="utf-8")
print(f"updated {step_c}")
print("done")
