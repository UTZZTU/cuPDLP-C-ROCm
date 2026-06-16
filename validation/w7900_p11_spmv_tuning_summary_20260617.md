# W7900 P11 SpMV tuning summary

This note closes the P11 W7900-specific SpMV tuning loop.

## Motivation

P10 targeted profiling showed that rocSPARSE CSR SpMV is the dominant
GPU kernel hotspot on the selected W7900 cases, while HIP API traces also
showed significant host-device copy pressure. Because copy reduction can
affect residual, restart, or termination logic, P11 first chose a safer
execution-layer experiment: SpMV algorithm selection.

## What changed

P11 introduced an opt-in HIP SpMV algorithm switch around the existing
generic `hipsparseSpMV` calls:

- default mode before P11-8-lite: `HIPSPARSE_SPMV_CSR_ALG2`
- opt-in experiment: `CUPDLP_HIP_SPMV_ALG=default`
- opt-in experiment: `CUPDLP_HIP_SPMV_ALG=csr_alg1`
- rollback after default update: `CUPDLP_HIP_SPMV_ALG=csr_alg2`

The final W7900 current default is now `HIPSPARSE_SPMV_CSR_ALG1`.

## Evidence chain

1. `f1fe620` added P10 targeted rocprof summaries.
2. `28f3796` added the P11 runtime callsite inventory.
3. `f48b5fd` ranked first-patch candidates.
4. `d1c2465` added the opt-in HIP SpMV algorithm switch.
5. `48b1ad9` validated the switch on `set-cover-model`.
6. `6ccf722` ran the five-case, three-mode SpMV sweep.
7. `2643849` changed the W7900 default to CSR ALG1.
8. `0649024` validated the new default and the CSR ALG2 rollback path.

## Final interpretation

P11 should be described as a conservative W7900 tuning policy update:

- The solver numerical path is not intentionally changed.
- Solver status and iteration count remained stable in the five-case sweep.
- `csr_alg1` showed a small favorable tendency on most long targeted cases.
- The effect size is small, so this is not a final performance conclusion.
- The old default is explicitly recoverable with `CUPDLP_HIP_SPMV_ALG=csr_alg2`.

## Next recommended work

With limited time, P11 can be considered complete. The next useful work is
documentation/report integration, not another long profiling run. If more
tuning time becomes available later, the next technical direction is a
careful scalar-copy analysis with explicit validation of residual,
restart, termination, primal infeasibility, dual infeasibility, and
duality gap.
