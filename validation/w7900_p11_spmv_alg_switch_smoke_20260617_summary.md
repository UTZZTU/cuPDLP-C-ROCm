# W7900 P11 SpMV algorithm switch smoke summary

This smoke validation checks the first real P11 tuning patch:

- commit: `d1c2465 tuning: add opt-in HIP SpMV algorithm switch`
- case: `set-cover-model`
- default behavior: `HIPSPARSE_SPMV_CSR_ALG2`
- opt-in modes:
  - `CUPDLP_HIP_SPMV_ALG=default`
  - `CUPDLP_HIP_SPMV_ALG=csr_alg1`

Raw logs remain under `/app/cupdlp_w7900/results` and are not committed.

## Result

- All runs exit with code 0: `True`
- All runs report `Optimal current solution`: `True`
- All runs use the same iteration count: `True`
- Observed iteration count: `7480`

## Aggregated timing

| mode | runs | exitcodes | status | nIter | mean solve s | min solve s | max solve s | mean total s | mean UpdateIterates s |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| default | 2 | 0 | Optimal current solution. | 7480 | 11.326795 | 11.319240 | 11.334350 | 12.609330 | 10.539820 |
| env_default | 2 | 0 | Optimal current solution. | 7480 | 11.391860 | 11.305140 | 11.478580 | 12.690090 | 10.552390 |
| csr_alg1 | 2 | 0 | Optimal current solution. | 7480 | 11.357640 | 11.348970 | 11.366310 | 12.644165 | 10.551835 |

## Interpretation

The opt-in SpMV algorithm switch passes the initial smoke validation on `set-cover-model`. All three modes preserve solver status, iteration count, objective values, primal infeasibility, dual infeasibility, and duality gap. The timing differences in this small smoke are within a narrow range and should not yet be treated as a performance conclusion.

The patch is therefore suitable for a broader P11 sweep on the five targeted P10 cases. The next validation should compare `default`, `csr_alg1`, and the default `csr_alg2` mode across `L2CTA3D`, `set-cover-model`, `square41`, `thk_48`, and `tpl-tub-ws1617`.

## Files

- `w7900_p11_spmv_alg_switch_smoke_20260617.csv`
