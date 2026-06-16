# W7900 P11 SpMV algorithm sweep summary

Run dir: `/app/cupdlp_w7900/results/w7900_p11_spmv_alg_sweep_20260616_222054`

This P11 sweep evaluates the opt-in HIP SpMV algorithm switch introduced by:

- `d1c2465 tuning: add opt-in HIP SpMV algorithm switch`

Modes:

- `csr_alg2`: default behavior, no `CUPDLP_HIP_SPMV_ALG` environment variable
- `env_default`: `CUPDLP_HIP_SPMV_ALG=default`
- `csr_alg1`: `CUPDLP_HIP_SPMV_ALG=csr_alg1`

Cases:

- `L2CTA3D`
- `set-cover-model`
- `square41`
- `thk_48`
- `tpl-tub-ws1617`

Raw logs remain under `/app/cupdlp_w7900/results` and are intentionally not committed.

## Correctness and stability

- All 15 runs exit with code 0: `True`
- Solver status is stable across modes for each case: `True`
- Iteration count is stable across modes for each case: `True`

## Solve-time comparison

| case | status stable | nIter stable | csr_alg2 solve s | env_default solve s | csr_alg1 solve s | best solve mode | csr_alg1 / csr_alg2 | env_default / csr_alg2 |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| L2CTA3D | True | True | 4.917409e-01 | 5.051799e-01 | 4.932051e-01 | csr_alg2 | 1.002978 | 1.027329 |
| set-cover-model | True | True | 11.493450 | 11.362370 | 11.333480 | csr_alg1 | 9.860816e-01 | 9.885952e-01 |
| square41 | True | True | 106.490500 | 106.729000 | 106.138100 | csr_alg1 | 9.966908e-01 | 1.002240 |
| thk_48 | True | True | 68.087580 | 68.261270 | 68.027230 | csr_alg1 | 9.991136e-01 | 1.002551 |
| tpl-tub-ws1617 | True | True | 97.543020 | 97.946200 | 97.444810 | csr_alg1 | 9.989932e-01 | 1.004133 |
| geomean | — | — | — | — | — | — | 9.967549e-01 | 1.004892 |

## Interpretation

The three SpMV algorithm modes all preserve solver status and iteration count on the five targeted P10 cases. `csr_alg1` is the fastest mode on four of the five cases by single-run solve time, while the default `csr_alg2` is slightly faster on the short `L2CTA3D` case. The geometric-mean solve-time ratio of `csr_alg1 / csr_alg2` is below 1.0, but the margin is small. This should be treated as a promising experiment result, not yet as a final performance conclusion.

Next validation should either repeat the sweep to estimate run-to-run noise, or profile the most interesting pair, `csr_alg1` vs `csr_alg2`, with rocprofv3 on `set-cover-model`, `square41`, `thk_48`, and `tpl-tub-ws1617`.

## Files

- `w7900_p11_spmv_alg_sweep_20260617.csv`
