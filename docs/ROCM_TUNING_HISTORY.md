# ROCm tuning history and ablation results

This note documents the ROCm/HIP tuning sequence for the `cuPDLP-C-ROCm` branch and records the benchmark evidence used to evaluate the tuning impact.

The purpose of this document is not to claim final peak performance. It records a reproducible quick ablation workflow that compares selected tuning milestones on the AMD Radeon 890M / gfx1150 ROCm/HIP backend.

## Scope

The current project keeps three backend modes:

| Mode | Role |
|---|---|
| CPU | correctness and portability baseline |
| CUDA | upstream-compatible NVIDIA baseline |
| ROCm/HIP | AMD Radeon 890M / gfx1150 target backend |

This document focuses only on the ROCm/HIP backend tuning sequence.

## Tuning milestones

The ablation uses the following milestone commits:

| Milestone | Commit | Meaning |
|---|---|---|
| `pre_tuning` | `ae3b683` | pre-tuning baseline |
| `remove_sync` | `f9d7f0d` | remove redundant HIP device synchronize in movement interaction |
| `cache_attrs` | `8fed073` | cache HIP device attributes in linalg helpers |
| `fused_average` | `fa7e860` | fuse ROCm average iterate axpy updates |
| `reduce_scalar_copies` | `b44c7ab` | reduce movement interaction scalar copies |
| `current` | `c65a20083d8e03ca167164f4142a5c58f863ffbb` | current HEAD at the time of the ablation |

## Benchmark method

The repeated ablation uses:

- AMD Radeon 890M / gfx1150 ROCm/HIP backend.
- 6 representative cases.
- 5 repeated runs per milestone/case pair.
- `nIterLim=200000000`.
- `CASE_TIMEOUT_SEC=900`.
- Median solve time as the primary metric.
- Mean, standard deviation, min, max, and coefficient of variation retained in CSV for variability analysis.

The quick set intentionally excludes `greenbea`. That case is convergence-sensitive and long-running, so it is tracked separately in the numerical-behavior notes instead of the tuning quick benchmark.

## Cases

| Case | Tier | Purpose |
|---|---|---|
| `afiro` | S | tiny smoke/overhead case |
| `sc50b` | S | small Netlib case |
| `lotfi` | M | medium many-iteration case |
| `80bau3b` | M | medium case with visible GPU timing |
| `maros-r7` | L | large case but short iteration count |
| `pilot87` | L | larger representative case |

## Correctness summary

All repeated runs in the ablation reached `OPTIMAL` with exit code `0`.

The repeated benchmark therefore supports the conclusion that the tuning sequence did not change termination status, iteration counts, or feasibility/gap values for this quick set.

## Median solve time

Primary metric: median solve time across 5 repeated runs.

| Milestone | afiro | sc50b | lotfi | 80bau3b | maros-r7 | pilot87 |
|---|---:|---:|---:|---:|---:|---:|
| `pre_tuning` | 0.052744 | 0.072827 | 4.537407 | 0.970653 | 0.124608 | 8.690948 |
| `remove_sync` | 0.059098 | 0.071003 | 3.997434 | 0.915490 | 0.120013 | 8.179166 |
| `cache_attrs` | 0.060280 | 0.069627 | 3.986371 | 0.912363 | 0.117736 | 8.218034 |
| `fused_average` | 0.053140 | 0.069351 | 3.825229 | 0.901840 | 0.117184 | 8.000284 |
| `reduce_scalar_copies` | 0.052801 | 0.066655 | 3.615290 | 0.869338 | 0.116324 | 7.820215 |
| `current` | 0.052900 | 0.066839 | 3.646848 | 0.874944 | 0.121077 | 7.820457 |

## Current vs pre-tuning

| Case | pre_tuning median | current median | Speedup | Time reduction |
|---|---:|---:|---:|---:|
| `afiro` | 0.052744 | 0.052900 | 0.997x | -0.30% |
| `sc50b` | 0.072827 | 0.066839 | 1.090x | 8.22% |
| `lotfi` | 4.537407 | 3.646848 | 1.244x | 19.63% |
| `80bau3b` | 0.970653 | 0.874944 | 1.109x | 9.86% |
| `maros-r7` | 0.124608 | 0.121077 | 1.029x | 2.83% |
| `pilot87` | 8.690948 | 7.820457 | 1.111x | 10.02% |

Geometric mean speedup for current vs pre-tuning across the 6-case quick set is approximately **1.094x**.

The main gains are visible on the medium and larger cases:

- `lotfi`: about 19.6% lower median solve time.
- `pilot87`: about 10.0% lower median solve time.
- `80bau3b`: about 9.9% lower median solve time.
- `sc50b`: about 8.2% lower median solve time.

`afiro` is dominated by fixed overhead and does not show meaningful improvement.

## Fastest observed milestone by case

| Case | Fastest milestone | Fastest median solve time |
|---|---|---:|
| `afiro` | `pre_tuning` | 0.052744 |
| `sc50b` | `reduce_scalar_copies` | 0.066655 |
| `lotfi` | `reduce_scalar_copies` | 3.615290 |
| `80bau3b` | `reduce_scalar_copies` | 0.869338 |
| `maros-r7` | `reduce_scalar_copies` | 0.116324 |
| `pilot87` | `reduce_scalar_copies` | 7.820215 |

The `reduce_scalar_copies` milestone is the fastest observed point for 5 of 6 quick cases.

The current branch remains faster than the pre-tuning baseline on 5 of 6 cases, but it is not the fastest observed point for every case. This is expected because later commits include backend compatibility, CUDA restoration, CMake cleanup, and documentation work rather than pure ROCm performance tuning only.

## Median DeviceMatVecProdTime

| Milestone | afiro | sc50b | lotfi | 80bau3b | maros-r7 | pilot87 |
|---|---:|---:|---:|---:|---:|---:|
| `pre_tuning` | 0.019731 | 0.021287 | 0.283484 | 0.050591 | 0.019830 | 0.262654 |
| `remove_sync` | 0.020783 | 0.022891 | 0.235519 | 0.042941 | 0.019717 | 0.226007 |
| `cache_attrs` | 0.022485 | 0.020762 | 0.224449 | 0.043925 | 0.020229 | 0.242991 |
| `fused_average` | 0.019422 | 0.022065 | 0.220678 | 0.047636 | 0.020546 | 0.233992 |
| `reduce_scalar_copies` | 0.020542 | 0.020963 | 0.218564 | 0.046652 | 0.020861 | 0.231445 |
| `current` | 0.020111 | 0.021583 | 0.233689 | 0.047721 | 0.020473 | 0.222489 |

The matvec timing does not explain all solve-time changes. Several tuning commits reduce overhead outside sparse matrix-vector product time, especially movement-interaction synchronization and scalar-copy overhead.

## Interpretation

The ROCm tuning sequence produced measurable improvement on the 6-case quick set.

The most important observations are:

1. The repeated ablation confirms correctness stability: all runs reached `OPTIMAL`.
2. Median solve time improved for 5 of 6 cases from `pre_tuning` to `current`.
3. The largest current-vs-baseline improvement is on `lotfi`.
4. The `reduce_scalar_copies` milestone is the fastest observed point for most cases.
5. Some later non-performance work may have small overhead or run-to-run noise, so future tuning should compare against both `pre_tuning` and `reduce_scalar_copies`.

## Limitations

This is a quick ablation, not a final statistically exhaustive performance study.

Known limitations:

- The case set is intentionally small.
- Each version/case pair is repeated 5 times, which is enough for quick signal but not exhaustive.
- The test uses wall-clock solve time reported by the solver, not external profiler timing.
- The benchmark is run on an integrated AMD Radeon 890M environment where system load, power state, and thermal state may affect timing.
- `greenbea` is excluded because it is a long-running convergence-sensitive case, not a tuning quick benchmark.

## Recommended next steps

1. Preserve the repeated raw and aggregated CSV files under `validation/`.
2. Use `reduce_scalar_copies` as a useful performance reference point for future ROCm tuning.
3. Use the current branch as the engineering baseline because it restores CPU/CUDA/ROCm three-mode compatibility.
4. Add a separate numerical-behavior note for `greenbea`.
5. If future tuning changes are made, compare against both `current` and `reduce_scalar_copies` on the same 6-case repeated benchmark.
