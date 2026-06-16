# W7900 P11 default SpMV ALG1 smoke summary

This validation checks the P11 default-policy update:

- commit: `2643849 tuning: default HIP SpMV algorithm to CSR ALG1`
- new default: `HIPSPARSE_SPMV_CSR_ALG1`
- rollback mode: `CUPDLP_HIP_SPMV_ALG=csr_alg2`
- case: `set-cover-model`

Raw logs remain under `/app/cupdlp_w7900/results` and are not committed.

## Result

- Both runs exit with code 0: `True`
- Both runs report `Optimal current solution`: `True`
- Both runs use the same iteration count: `True`
- Both runs preserve primal and dual objective values: `True`

## Smoke table

| mode | exit | status | nIter | solve s | total s | primal rel infeas | dual rel infeas | rel gap |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| default_csr_alg1 | 0 | Optimal current solution. | 7480 | 1.145234e+01 | 1.277736e+01 | 9.81e-05 | 0.00e+00 | 9.36e-06 |
| rollback_csr_alg2 | 0 | Optimal current solution. | 7480 | 1.134371e+01 | 1.262357e+01 | 9.81e-05 | 0.00e+00 | 9.36e-06 |

## Interpretation

The new default SpMV algorithm policy passes the short smoke validation. The default no-env path now uses `csr_alg1`, and the old default can still be restored with `CUPDLP_HIP_SPMV_ALG=csr_alg2`.

This smoke is a correctness and rollback check, not a performance conclusion. The broader P11 five-case sweep remains the main evidence for choosing `csr_alg1` as the current W7900 default.

## Files

- `w7900_p11_default_spmv_alg1_smoke_20260617.csv`
