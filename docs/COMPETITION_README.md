# Competition README: ROCm-enabled large-scale LP solver on Radeon GPUs

> 中文: [COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md)

This is the reviewer-facing entry point for the AMD ROCm / Radeon contest track.

## Project title

**ROCm-enabled Large-scale Linear Programming Solver Migration, Validation, and Profiling on AMD Radeon GPUs**

## Problem background and challenge

Large-scale linear programming is a scientific-computing and operations-research workload. cuPDLP/PDLP-style solvers repeatedly use sparse matrix-vector products, vector updates, reductions, and numerical convergence checks. The upstream project is CUDA-oriented, so the challenge is to migrate the solver to AMD ROCm/HIP while preserving correctness, reproducibility, and cross-device comparability.

## Target platforms

| Platform | Role |
|---|---|
| Radeon 890M / `gfx1150` | First ROCm/HIP migration, tuning history, and baseline validation |
| Radeon PRO W7900 / `gfx1100` | Large-MPS workstation GPU validation and future W7900-specific profiling/tuning |
| RTX 3090 / RTX 4090D / H100 | CUDA reference devices for cross-device comparison |

## Implementation summary

| Area | Repository evidence |
|---|---|
| ROCm/HIP migration | HIP backend, ROCm build workflow, CUDA/ROCm compatibility fixes |
| Validation | smoke, Netlib, large-MPS case lists, parsed CSV summaries |
| Benchmarking | 890M, W7900, 3090, 4090D, and H100 reference data |
| W7900 status | [W7900 current status](W7900_CURRENT_STATUS.md) |
| Performance analysis | [W7900 performance behavior](W7900_PERFORMANCE_BEHAVIOR.md) |
| Optimization baseline | [W7900 optimization baselines](W7900_OPTIMIZATION_BASELINES.md) |
| Profiling plan | [W7900 ROCm profiling plan](W7900_ROCM_PROFILING_PLAN.md) |
| Validation index | [validation README](../validation/README.md) |

## Current W7900 results

The W7900 branch is no longer only a first-port smoke experiment. It has:

- W7900 smoke validation;
- W7900 Netlib 27-case validation;
- W7900 large-MPS `initial17_safe`;
- W7900 large-MPS `watchlist6` and `near_optimal2`;
- W7900 large-MPS `non-hard23`: 23/23 `OPTIMAL`;
- hard3 split: `dlr1.mps`, `Dual2_5000.mps`, `fhnw-binschedule1.mps`.

| Metric | Value |
|---|---|
| W7900 non-hard23 cases | 23 |
| Termination | 23/23 `OPTIMAL` |
| Total wall time | 2960.171 s |
| Total solve time | 2742.940 s |
| Current status | post-890M-tuning engineering baseline |

## Important baseline correction

The current W7900 non-hard23 result is **not** an unoptimized first-port baseline. It is the current post-890M-tuning engineering baseline.

| Role | Version | Purpose |
|---|---|---|
| Before | `ae3b683` / `pre_tuning` | true first-runnable ROCm anchor |
| Current | current `rocm-w7900-gfx1100` | post-890M-tuning W7900 engineering baseline |
| After | future W7900-specific tuning branch | final W7900-specific optimized result |

## Performance interpretation

The project uses both aggregate and per-case analysis. Aggregate time is useful, but W7900 competitiveness is clearer at the per-case level. The core interpretation is:

```text
total time ≈ per-iteration cost × number of iterations
```

W7900 can be strong on large, bandwidth-sensitive, SpMV/vector-operation-heavy cases with stable convergence. Slow cases such as `s100` and `Primal2_1000` should be explained through iteration count and gap trajectory as well as kernel performance.

## Next planned work

1. Run W7900 `rocprofv3` starter3 profiling on `set-cover-model`, `square41`, and `s100`.
2. Record wall time, solver time, `DeviceMatVecProdTime`, `nIter`, HIP/kernel trace, and GPU telemetry.
3. Run hard3 short probes for `dlr1` and `fhnw-binschedule1`.
4. Run true before/current comparison on the core6 list using `ae3b683` vs current.
5. Perform W7900-specific tuning only after profiling results identify bottlenecks.

## Submission-material mapping

| Competition material | Repository status |
|---|---|
| Technical paper | to be built from this README, performance behavior, tuning history, and profiling results |
| Demo PPT | to be created after first profiling results |
| Demo video | should show build, validation, charts, and profiling workflow |
| Engineering repository | current repository with scripts, validation CSVs, Markdown summaries, SVG charts |
| Reproducibility | bootstrap scripts exist; dedicated reproducibility document is next |
