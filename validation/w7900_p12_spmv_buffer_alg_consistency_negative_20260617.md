# W7900 P12 negative finding: SpMV buffer algorithm consistency

This note records a rejected post-P11 low-risk execution-layer tuning
experiment.

## Context

P11 changed the current W7900 default HIP SpMV algorithm to
`HIPSPARSE_SPMV_CSR_ALG1`, while preserving rollback with
`CUPDLP_HIP_SPMV_ALG=csr_alg2`.

After that, source audit showed one remaining consistency candidate:
`cuda_alloc_MVbuffer()` still queried `hipsparseSpMV_bufferSize()` with a
local algorithm variable set to `HIPSPARSE_SPMV_CSR_ALG2`, while actual
runtime `hipsparseSpMV()` calls used `cupdlp_hip_spmv_alg()`.

## Experiment

The rejected patch attempted two changes:

1. cache `CUPDLP_HIP_SPMV_ALG` parsing in `cupdlp_hip_spmv_alg()`;
2. make `cuda_alloc_MVbuffer()` use `cupdlp_hip_spmv_alg()` for
   `hipsparseSpMV_bufferSize()`.

## Observed result

Test case: `set-cover-model`

Observed after the patch:

- exit code: `0`
- solver status: `Optimal current solution`
- iteration count: `7600`
- solve time: `1.148008e+01`
- total solver time: `1.278179e+01`
- primal objective: `+7.58183814e+09`
- dual objective: `+7.58170468e+09`
- relative primal infeasibility: `9.84e-05`
- relative dual infeasibility: `0.00e+00`
- relative duality gap: `8.80e-06`

Previous P11 smoke and sweep runs had `set-cover-model` stable at
`7480` iterations under the accepted SpMV algorithm-switch policy.

## Decision

The patch was rejected and reverted.

Although the implementation idea was reasonable, it changed the solver
trajectory. This violates the low-risk tuning rule used in this project:
execution-layer changes should preserve solver status, iteration count,
primal infeasibility, dual infeasibility, and duality gap unless the
change is explicitly treated as a deeper numerical experiment.

## Interpretation

This is useful evidence. It shows that even apparently local
SpMV-buffer/algorithm consistency changes can affect the observed PDLP
iteration trajectory on W7900. Therefore, further work in this direction
should be treated as future deeper validation work rather than as a final
quick tuning patch.

## Final status

Not committed:

- `cupdlp/hip/cupdlp_hip_linalg.cpp` patch was reverted.
- temporary patch script was removed.

Accepted endpoint remains:

- current W7900 default SpMV algorithm: `HIPSPARSE_SPMV_CSR_ALG1`
- rollback: `CUPDLP_HIP_SPMV_ALG=csr_alg2`
