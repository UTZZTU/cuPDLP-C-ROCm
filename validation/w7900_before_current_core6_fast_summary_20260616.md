# W7900 before/current fast-core6 summary

Result directory: `/app/cupdlp_w7900/results/w7900_before_current_core6_900s_core6_fast_900s_20260616_185300`

This is a compact summary of the W7900 fast-core6 before/current comparison.

Compared versions:

- `pre_tuning`: `ae3b683 / pre_tuning`, built on W7900 with ROCm Python SDK include-path adaptation.
- `current`: current `rocm-w7900-gfx1100` engineering branch.

Fast-core6 case list:

- `set-cover-model.mps`
- `square41.mps`
- `thk_48.mps`
- `tpl-tub-ws1617.mps`
- `L2CTA3D.mps`
- `rmine15.mps`

## Comparison

| case | current_termination | pre_tuning_termination | current_solve_time | pre_tuning_solve_time | current_over_pre_solve_ratio | pre_over_current_speedup |
|---|---|---|---|---|---|---|
| L2CTA3D | OPTIMAL | OPTIMAL | 0.504093 | 0.385509 | 1.307604 | 0.764758 |
| rmine15 | OPTIMAL | OPTIMAL | 27.384925 | 27.889919 | 0.981893 | 1.018441 |
| set-cover-model | OPTIMAL | OPTIMAL | 11.652169 | 7.449711 | 1.564110 | 0.639341 |
| square41 | OPTIMAL | OPTIMAL | 106.691588 | 110.538147 | 0.965202 | 1.036053 |
| thk_48 | OPTIMAL | OPTIMAL | 68.444947 | 76.277967 | 0.897310 | 1.114443 |
| tpl-tub-ws1617 | OPTIMAL | OPTIMAL | 98.223063 | 55.561147 | 1.767837 | 0.565663 |

## Aggregate

- Current wins by solve time: `3/6` cases.
- Pre-tuning wins by solve time: `3/6` cases.
- Geometric mean current/pre solve-time ratio: `1.205873`.
- Geometric mean pre/current speedup: `0.829274`.

## Interpretation

- Both versions reached `OPTIMAL` on all six fast-core6 cases.
- The current engineering branch is not uniformly faster than `ae3b683 / pre_tuning` on this fast subset.
- This result should be used as a truthful before/current engineering comparison, not as a blanket W7900 speedup claim.
- The mixed result reinforces the need for W7900-specific profiling and tuning.
- `s100` and `Primal2_1000` were intentionally excluded from this fast-core6 run because their known W7900 runtimes are too long for the available experiment window.

## Repository policy

Commit only compact CSV and Markdown summaries. Raw large-MPS files and raw run directories stay outside Git.
