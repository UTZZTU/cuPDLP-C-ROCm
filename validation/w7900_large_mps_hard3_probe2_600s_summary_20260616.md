# W7900 large-MPS hard3 probe2 600s summary

Result directory: `/app/cupdlp_w7900/results/w7900_large_mps_hard3_probe2_600s_20260616_180208`

This is a compact summary of the W7900 hard3 probe2 diagnostic run. The run uses a 600-second solver time limit and tracks hard cases separately from the non-hard23 large-MPS baseline.

## Runtime summary

| case | status | exit_code | wall_seconds |
|---|---|---|---|
| dlr1.mps | DONE | 0 | 645.180829 |
| fhnw-binschedule1.mps | DONE | 0 | 614.012251 |

## Solver summary

| case | runtime_status | exit_code | wall_seconds | terminationCode | nIter | dSolvingTime | DeviceMatVecProdTime | dRelPrimalFeas | dRelDualFeas | dRelDualityGap |
|---|---|---|---|---|---|---|---|---|---|---|
| dlr1 | DONE | 0 | 645.180829 | TIMELIMIT_OR_ITERLIMIT | 76724 | 600.005066 | 0.500722 | 2.89095896012908 | 3.79388430029909 | 0.28406864922219 |
| fhnw-binschedule1 | DONE | 0 | 614.012251 | TIMELIMIT_OR_ITERLIMIT | 25985 | 600.013012 | 0.249548 | 6.590635427e-05 | 0.0 | 0.39159839307069 |

## Interpretation

- Both `dlr1` and `fhnw-binschedule1` reached the 600-second solver time limit.
- `dlr1` has relative duality gap around `0.284`, with relative primal and dual infeasibility still large; it is not near convergence under the 600-second probe.
- `fhnw-binschedule1` has small primal infeasibility and zero dual infeasibility, but relative duality gap remains around `0.392`; it is also not near an OPTIMAL termination under the 600-second probe.
- These cases remain tracked as hard cases and should not be mixed into the non-hard23 primary baseline.
- No immediate 1800-second extension is recommended from this probe; W7900-specific tuning and later targeted probes should come first.

## Repository policy

Commit only compact CSV and Markdown summaries. Raw large-MPS files and large intermediate result directories stay outside Git.
