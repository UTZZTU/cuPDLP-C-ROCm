# ROCm tuning guide

> 中文版：[TUNING_GUIDE_ROCM.zh-CN.md](TUNING_GUIDE_ROCM.zh-CN.md)

This guide describes how to tune the ROCm/HIP backend without weakening numerical reliability. It reflects the completed 890M and W7900 evidence rather than presenting old plans as current work.

## Current platform policy

| Item | Current value |
|---|---|
| Primary ROCm branch | `rocm-w7900-gfx1100` |
| Primary ROCm platform | Radeon PRO W7900 / `gfx1100` |
| Earlier tuning milestone | Radeon 890M / `gfx1150` |
| Current SpMV default | `HIPSPARSE_SPMV_CSR_ALG1` |
| Rollback | `CUPDLP_HIP_SPMV_ALG=csr_alg2` |
| Main executable | `plc` |

The backend remains a research and engineering validation path, not a production-certified solver release.

## Core rule

A performance patch is acceptable only when all three questions have defensible answers:

1. Is the output still valid?
2. Is the convergence trajectory acceptably stable?
3. Is the measured speedup repeatable on representative cases?

Kernel timing alone is not sufficient.

## Why solver tuning is different

End-to-end solve time is approximately:

```text
solve time ≈ per-iteration cost × iteration count
```

A lower per-iteration cost can be offset by more iterations. Floating-point order, reductions, sparse-library policy, and synchronization can influence the path taken by PDHG.

Always track:

- termination status;
- primal and dual feasibility;
- relative gap;
- `nIter`;
- wall and solve time;
- representative profiler metrics.

## Establish the baseline

Before changing code:

```bash
git rev-parse HEAD
git status
```

Choose and record:

- a fixed before commit;
- the same case list;
- iteration and timeout limits;
- environment variables;
- compiler and ROCm versions;
- GPU architecture;
- warm-up and repeat counts.

For W7900 before/current comparisons, use `ae3b683 / pre_tuning` as the true before anchor. Do not use the current post-890M-tuning branch as an “unoptimized” baseline.

## Validation ladder

| Change type | Required evidence |
|---|---|
| Documentation or naming | Markdown/link checks |
| Runtime-query or setup cleanup | Smoke plus representative validation |
| Copy, synchronization, or launch change | Smoke, Netlib subset, repeated timing |
| Sparse/BLAS algorithm policy | Smoke, targeted cases, iteration/residual checks, rollback |
| Reduction or algorithm-adjacent code | Broad validation and trajectory diagnostics |
| New architecture | Fresh build, smoke, representative large cases, profiling |

Escalate validation when a change can affect operation ordering or floating-point reductions.

## Profiling workflow

W7900 targeted entry:

```bash
bash scripts/run_w7900_p10_current_targeted_rocprof.sh
```

P10 cases:

```text
thk_48
square41
L2CTA3D
set-cover-model
tpl-tub-ws1617
```

Generic smoke profiling:

```bash
RESULT_ROOT=profiling/results/current \
  bash scripts/profile_rocm_smoke.sh
```

Raw traces stay outside Git. Commit compact tables and interpretation.

## Select patches from evidence

A good first patch should be:

- localized;
- reversible;
- easy to validate;
- motivated by a measured hotspot;
- unlikely to alter mathematical semantics.

The 890M sequence followed this rule by reducing synchronization, stable runtime queries, repeated AXPY launches, and scalar copies before attempting deeper kernel changes.

On W7900, P10 identified SpMV as the major hotspot. P11 therefore compared supported hipSPARSE algorithms instead of replacing hipSPARSE wholesale.

## Current SpMV switch

| Mode | Configuration |
|---|---|
| Current default | no environment variable; `HIPSPARSE_SPMV_CSR_ALG1` |
| Roll back to old policy | `CUPDLP_HIP_SPMV_ALG=csr_alg2` |
| Try library default | `CUPDLP_HIP_SPMV_ALG=default` |

Example:

```bash
CUPDLP_HIP_SPMV_ALG=csr_alg2 \
  ./build-rocm-w7900/bin/plc \
  -fname /path/to/case.mps \
  -out /tmp/case.json \
  -nIterLim 200000000
```

Keep the environment setting in logs and result metadata.

## Repeat timing correctly

For a timing claim:

1. run the same binary/case configuration;
2. use at least one warm-up where appropriate;
3. collect multiple measured repeats;
4. report median or geometric-mean speedup;
5. show per-case results, not only an aggregate;
6. verify iteration counts and numerical fields.

P14-A1 is the current model: quick6, repeated current-vs-pre-tuning runs, 6/6 wins, geometric-mean speedup 1.18889, median 1.19502, and unchanged iterations.

## Rejection criteria

Reject or hold a patch when:

- status changes;
- feasibility/gap exceeds the validation contract;
- iteration count changes without a convincing explanation and benefit;
- speedup is inconsistent across repeats;
- a small-case gain regresses representative large cases;
- rollback is unavailable for a platform-sensitive policy;
- the profiler result does not support the patch rationale.

P12 is the canonical negative example: a buffer-algorithm consistency change altered `set-cover-model` from 7480 to 7600 iterations and was rejected.

## Reporting

For each accepted or rejected experiment, record:

```text
before reference
after reference
platform and software environment
case list and limits
status and numerical comparison
iteration counts
timing repeats
profiler evidence
decision
rollback method
```

Keep raw run directories outside Git and commit curated CSV/Markdown summaries.

## Current endpoint and optional work

The current W7900 tuning evidence chain is complete through:

- P10 targeted profiling;
- P11 accepted SpMV policy;
- P12 rejected execution-layer experiment;
- P14-A1 repeated before/current confirmation.

Optional future work should answer a specific new question. Examples include repeated ALG1-vs-ALG2 evidence, reduction-path profiling, scalar-readback analysis, or validation on another AMD architecture. These are enhancements, not unfinished core scope.

## Related documents

- [ROCm profiling notes](ROCM_PROFILING_NOTES.md)
- [ROCm tuning history](ROCM_TUNING_HISTORY.md)
- [Validation semantics](VALIDATION.md)
- [W7900 current status](W7900_CURRENT_STATUS.md)
