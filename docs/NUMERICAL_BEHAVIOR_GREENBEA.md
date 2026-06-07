# Numerical behavior note: `greenbea`

This note documents why the Netlib `greenbea` case is tracked separately in this ROCm/HIP port of cuPDLP-C.

The short version: `greenbea` is not treated as a simple pass/fail smoke case. It is a convergence-sensitive long-running LP instance that exposes numerical-trajectory differences between CPU, CUDA, and ROCm/HIP backends.

## Background

cuPDLP-C is based on PDLP / PDHG-style first-order methods for linear programming. Public PDLP references describe PDLP as a practical first-order LP method derived from applying primal-dual hybrid gradient (PDHG) to a saddle-point formulation of LP. They also emphasize that the method is designed to scale because its core operation is matrix-vector multiplication.

This matters for `greenbea` because the GPU backends execute the same high-level method through different sparse matrix-vector kernels, vector-update kernels, reduction paths, synchronization points, and floating-point operation order. For most cases in this repository's validation set, these differences do not affect termination status. For `greenbea`, the backend trajectory is more sensitive.

References:

- Google Research / NeurIPS 2021, *Practical Large-Scale Linear Programming using Primal-Dual Hybrid Gradient*: https://proceedings.neurips.cc/paper/2021/hash/a8fbbd3b11424ce032ba813493d95ad7-Abstract.html
- OR-Tools PDLP mathematical background: https://developers.google.com/optimization/lp/pdlp_math
- COPT-Public/cuPDLP-C upstream repository: https://github.com/COPT-Public/cuPDLP-C
- cuPDLP.jl GPU PDHG paper: https://arxiv.org/abs/2311.12180

## Why `greenbea` is tracked separately

Most validation cases are used to answer:

> Does the backend build and solve representative LP instances correctly?

`greenbea` is used to answer a different question:

> How do CPU, CUDA, and ROCm/HIP numerical trajectories differ on a convergence-sensitive case under the same high-level solver settings?

For this reason, `greenbea` should not be hidden or removed just because one GPU backend hits the wall-clock limit. It is useful evidence for understanding backend numerical behavior.

## Current benchmark policy for `greenbea`

The project policy is:

- Keep `nIterLim=200000000`.
- Treat 3600 seconds as the effective long-case wall-clock limit for cross-device reporting.
- Preserve timeout / limit results as valid numerical-behavior data.
- Record termination code, iteration count, feasibility, duality gap, and solve time.
- Do not repeatedly extend the time limit just to force convergence.

This avoids turning a convergence-sensitive diagnostic case into an unbounded manual benchmark.

## Observed results

The following observations come from the project's cross-device benchmark runs.

### RTX 3090 CUDA

A dedicated `greenbea` 200M run on RTX 3090 reached the internal 3600 second limit on the CUDA GPU path.

| Backend | Status | Iterations | Solve time | Relative primal feasibility | Relative dual feasibility | Relative duality gap |
|---|---|---:|---:|---:|---:|---:|
| CPU | `OPTIMAL` | 8,538,920 | 1286.92 s | — | — | — |
| CUDA GPU | `TIMELIMIT_OR_ITERLIMIT` | 41,615,624 | 3600.000060 s | 0.21299620838891 | 0.00000067393008 | 0.00256258916268 |

The CUDA GPU run remained feasible according to the solver's primal/dual code fields, but did not reach the solver's optimal termination condition within the 3600 second limit.

### RTX 4090D CUDA

The RTX 4090D full 200M benchmark recorded `greenbea` as a shell-level timeout for the CUDA run.

| Backend | Status | Iterations | Solve time |
|---|---|---:|---:|
| CPU | `OPTIMAL` | 8,538,920 | 1178.48 s |
| CUDA GPU | shell timeout | — | 3600 s wall-clock limit |

The earlier failed 4090D CUDA attempt was caused by CUDA context initialization failure due to GPU compute-mode / occupancy interference. That issue was resolved by rerunning on an available GPU. The final 4090D result still treated `greenbea` as a long convergence-sensitive case rather than a regular quick case.

### Radeon 890M ROCm/HIP

The Radeon 890M full 200M benchmark recorded `greenbea` as a shell-level timeout on the ROCm/HIP run.

| Backend | Status | Iterations | Solve time |
|---|---|---:|---:|
| CPU | `OPTIMAL` | 8,538,920 | 592.58 s |
| ROCm/HIP GPU | shell timeout | — | 3600 s wall-clock limit |

Other cases in the same 890M full run reached `OPTIMAL` on ROCm/HIP, so this result should not be interpreted as the ROCm backend generally failing validation. It is specific to `greenbea`.

## Interpretation

The evidence suggests that `greenbea` is convergence-sensitive across GPU backends.

The most important points are:

1. CPU solves `greenbea` to `OPTIMAL` in the recorded runs.
2. CUDA and ROCm/HIP GPU paths can require substantially different trajectories.
3. The 3090 CUDA 200M run reached 41.6M iterations and 3600 seconds without `OPTIMAL`.
4. 4090D CUDA and 890M ROCm/HIP both hit the wall-clock limit in the full benchmark workflow.
5. Most other validation cases reach `OPTIMAL` on the GPU backends, so `greenbea` should be documented as a special convergence-sensitive instance.

This does not prove that the ROCm/HIP port is numerically wrong. It shows that the GPU backend trajectory differs enough on this LP instance that the case needs separate numerical analysis.

## Why CPU and GPU iteration trajectories can differ

Even with the same high-level algorithm and the same input MPS file, the following backend-level differences may change the trajectory of a first-order method:

- sparse matrix-vector product implementation,
- reduction order,
- vector update fusion,
- synchronization placement,
- host-device scalar transfer timing,
- BLAS / sparse library implementation details,
- floating-point operation ordering,
- restart and adaptive step-size decisions triggered by small numerical differences.

For many LP instances, these differences are harmless. For a near-degenerate or convergence-sensitive case, they can lead to different iteration counts or limit behavior.

This is especially relevant for PDHG/PDLP-style methods, where the algorithm is iterative and large runs may involve millions of matrix-vector operations and vector updates.

## What this means for validation

`greenbea` should be reported in validation, not removed.

Recommended reporting rules:

| Scenario | How to report |
|---|---|
| CPU reaches `OPTIMAL` | Report as baseline success |
| GPU reaches `OPTIMAL` | Report status, iteration count, solve time, feasibility, gap |
| GPU hits wall-clock timeout | Report as convergence-sensitive timeout, not as missing data |
| GPU has context/runtime failure | Report separately as environment/runtime failure |
| Feasibility/gap differs materially | Preserve JSON fields and logs for trajectory analysis |

## What not to claim

Do not claim:

- "`greenbea` proves ROCm is incorrect."
- "`greenbea` proves CUDA is incorrect."
- "`greenbea` should be excluded because it times out."
- "CPU and GPU must have identical iteration counts."

Instead, say:

- "`greenbea` is a convergence-sensitive case where CPU, CUDA, and ROCm/HIP trajectories differ."
- "The case is useful for future numerical analysis."
- "Timeout results are retained because they provide evidence about backend behavior."

## Recommended future investigation

Future work should focus on collecting trajectory-level diagnostics rather than simply increasing time limits.

Recommended next steps:

1. Add periodic logging for primal feasibility, dual feasibility, and relative duality gap.
2. Compare CPU, CUDA, and ROCm/HIP trajectories at fixed iteration checkpoints.
3. Record restart / step-size behavior if available.
4. Compare average iterate and last iterate termination behavior.
5. Compare sparse matrix-vector timing and update timing separately.
6. Test whether fused ROCm update kernels alter the trajectory on `greenbea`.
7. Run a reduced checkpoint benchmark rather than only end-of-run JSON.
8. Keep the 3600 second wall-clock policy for cross-device comparability.

## Suggested data files to preserve

For each long `greenbea` run, preserve:

- solver JSON output when available,
- stdout/stderr log,
- shell exit code,
- environment summary,
- CPU/GPU model,
- ROCm or CUDA version,
- commit SHA,
- case timeout,
- `nIterLim`,
- feasibility and duality gap fields.

## Summary

`greenbea` is retained as a numerical-behavior diagnostic case.

It is valuable because it shows that the ROCm/HIP port should be evaluated not only by build success and quick-case `OPTIMAL` status, but also by long-run trajectory behavior on difficult LP instances.

The current project position is:

> The ROCm/HIP backend solves the broad validation set on Radeon 890M, but `greenbea` remains a convergence-sensitive long case. Its timeout behavior is documented and preserved as evidence for future numerical analysis rather than hidden as a failed ordinary smoke test.
