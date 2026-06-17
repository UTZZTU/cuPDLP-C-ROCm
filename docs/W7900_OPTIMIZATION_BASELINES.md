# W7900 optimization baselines

> 中文: [W7900_OPTIMIZATION_BASELINES.zh-CN.md](W7900_OPTIMIZATION_BASELINES.zh-CN.md)

This document corrects the baseline wording for W7900 / `gfx1100`.

The current W7900 large-MPS `non-hard23` result is **not** an unoptimized first-port baseline. It is a W7900 validation of the current ROCm/HIP engineering branch, and that branch already inherits the earlier Radeon 890M / `gfx1150` tuning work.

## Required wording

Use this wording in reports:

```text
The W7900 non-hard23 baseline is the current post-890M-tuning engineering baseline.
It is not the original first-runnable ROCm baseline.
```

## Milestone timeline

![ROCm tuning milestone timeline](assets/w7900/rocm_tuning_milestone_timeline.svg)

| Milestone | Commit | Role | Interpretation |
|---|---|---|---|
| pre_tuning | ae3b683 | Add ROCm profiling summary script | true first-runnable / pre-tuning anchor |
| remove_sync | f9d7f0d | remove redundant HIP synchronize | first synchronization cleanup |
| cache_attrs | 8fed073 | cache HIP device attributes | helper-level overhead cleanup |
| fused_average | fa7e860 | Fuse ROCm average iterate axpy updates | average iterate update fusion |
| reduce_scalar_copies | b44c7ab | Reduce movement interaction scalar copies | fast historical tuning milestone |
| current_engineering | 35a7a7b | add W7900 ROCm profiling plan | current post-890M-tuning engineering branch |

## Evidence from the existing tuning history

The repository tuning history already states that `pre_tuning` is `ae3b683`, `reduce_scalar_copies` is `b44c7ab`, and the current branch is an engineering baseline because it keeps CPU/CUDA/ROCm three-mode compatibility. It also records that current improves over `pre_tuning` on the 6-case quick set, while `reduce_scalar_copies` is the fastest observed point for most quick-set cases.

Therefore, current W7900 data should be presented as **post-tuning engineering validation on W7900**, not as **before-tuning W7900 data**.

## Before/after policy status

| Role | Version | Purpose |
|---|---|---|
| Before | `pre_tuning` / `ae3b683` | true first-runnable/pre-tuning ROCm anchor |
| Current | `rocm-w7900-gfx1100` current HEAD | current post-890M-tuning W7900 engineering baseline |
| Current endpoint | current `rocm-w7900-gfx1100` HEAD | accepted W7900 endpoint after P11/P14-A1 |

## Recommended first before/after subset

| Case | Reason |
|---|---|
| set-cover-model.mps | fast representative; overhead/kernel-dispatch analysis |
| square41.mps | competitive W7900 case |
| s100.mps | slow-but-solvable; iteration-count sensitive |
| Primal2_1000.mps | near-optimal at 900s and OPTIMAL under 1800s |
| thk_48.mps | medium/large representative |
| tpl-tub-ws1617.mps | large representative for cross-device comparison |

Run this core6 subset before attempting a full non-hard23 rerun. The full large-MPS non-hard23 rerun should be reserved for the true pre-tuning anchor if time permits, the final W7900-specific optimized branch, or major solver/kernel changes.

## Documentation policy

- Do not call current W7900 non-hard23 "unoptimized".
- Use `ae3b683` as the real before anchor.
- Use `current` as the engineering baseline.
- Use `reduce_scalar_copies` as a historical fast reference.
- Keep hard3 separate until convergence trajectory evidence is documented.

## Completion update / 2026-06-17

This document originally defined the before/after policy for W7900
optimization. The accepted W7900-specific tuning endpoint is now available.

Accepted endpoint:

- P11 changed the current W7900 default SpMV algorithm to
  `HIPSPARSE_SPMV_CSR_ALG1`.
- The old default remains available with
  `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
- P11 five-case sweep preserved solver status and iteration count across
  the evaluated SpMV modes.
- P12 tested one additional SpMV buffer algorithm consistency patch and
  rejected it because the iteration count changed.

Final references:

- `validation/w7900_p11_spmv_tuning_summary_20260617.md`
- `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md`

## Final before/after interpretation after P14-A1 / 2026-06-18

The earlier “future before/after policy” has now been partially closed by
P14-A1. The project does not need a new full W7900-specific after branch for
the current endpoint.

Current interpretation:

| Role | Version | Current interpretation |
|---|---|---|
| Before | `pre_tuning` / `ae3b683` | true first-runnable/pre-tuning ROCm anchor |
| Current endpoint | current `rocm-w7900-gfx1100` HEAD | accepted W7900 engineering endpoint with P11 default `HIPSPARSE_SPMV_CSR_ALG1` |
| Repeated evidence | P14-A1 quick6 | current is faster on `6/6` quick6 cases; geomean `1.18889`; median `1.19502` |

Do not describe P14-B as required. It remains a future optional robustness check only.
