# ROCm tuning history

> 中文版：[ROCM_TUNING_HISTORY.zh-CN.md](ROCM_TUNING_HISTORY.zh-CN.md)

This page records the tuning sequence without mixing old plans with current status. Dated reports and CSV files remain the authoritative experiment artifacts.

## Baseline roles

| Role | Reference | Meaning |
|---|---|---|
| Pre-tuning anchor | `ae3b683 / pre_tuning` | First-runnable ROCm anchor used for before/current analysis |
| 890M engineering sequence | milestones after `ae3b683` | Structural-overhead tuning on `gfx1150` |
| W7900 current branch | `rocm-w7900-gfx1100` | Post-890M-tuning engineering baseline |
| Accepted W7900 endpoint | P11 policy | `HIPSPARSE_SPMV_CSR_ALG1` default with `csr_alg2` rollback |

The current W7900 baseline must not be described as an unoptimized first port.

## 890M structural tuning sequence

The early profiling-driven sequence focused on low-risk structural overhead:

| Milestone | Change |
|---|---|
| `ae3b683` | pre-tuning anchor |
| `f9d7f0d` | remove redundant synchronization |
| `8fed073` | cache HIP device attributes |
| `fa7e860` | fuse average-iterate updates |
| `b44c7ab` | reduce movement-interaction scalar copies |

The exact repository history remains the source of code-level details.

### Why these changes were selected

Smoke profiling showed high counts of:

- kernel launches;
- small copies;
- synchronization;
- stable device-attribute queries;
- repeated vector updates.

The sequence therefore reduced structural overhead before attempting lower-level sparse or reduction rewrites.

### Validation evidence

The 890M evidence includes:

- six-case repeated ablation;
- 27-case current-vs-reduce comparison;
- profiling milestone summaries;
- CPU/ROCm validation checks.

The six-case history showed useful gains from the combined sequence. The 27-case comparison between the last two close milestones had a base-over-current geometric mean near parity (`0.9995092331107024`), showing why small aggregate differences should not be overinterpreted.

Evidence:

- [profiling milestones](../validation/rocm_prof_tuning_milestones_summary.md)
- [six-case repeated ablation](../validation/rocm_tuning_ablation_6cases_repeats_summary.md)
- [27-case comparison](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.md)

## W7900 validation before tuning

W7900 / `gfx1100` first established:

1. CPU and ROCm build paths;
2. `afiro` smoke validation;
3. Netlib validation;
4. large-MPS subsets;
5. non-hard23 with 23/23 `OPTIMAL`;
6. hard3 separation.

The W7900 baseline therefore had a correctness and large-case evidence base before platform-specific tuning.

## P10: targeted profiling

P10 profiled:

```text
thk_48
square41
L2CTA3D
set-cover-model
tpl-tub-ws1617
```

The main result was that rocSPARSE CSR SpMV dominated the targeted GPU kernel profile, with copies and launch overhead as secondary runtime concerns.

See [P10 summary](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.md).

## P11: accepted SpMV algorithm policy

P11 introduced a runtime selection policy rather than replacing the sparse library:

| Selection | Runtime value |
|---|---|
| Current default | `HIPSPARSE_SPMV_CSR_ALG1` |
| Old-default rollback | `CUPDLP_HIP_SPMV_ALG=csr_alg2` |
| Library experimental default | `CUPDLP_HIP_SPMV_ALG=default` |

The work included:

- runtime call-site inventory;
- algorithm switch smoke validation;
- a five-case algorithm sweep;
- default-policy smoke validation;
- a final tuning summary.

See [P11 summary](../validation/w7900_p11_spmv_tuning_summary_20260617.md).

## P12: rejected execution-layer experiment

P12 aligned the `hipsparseSpMV_bufferSize()` query with the selected execution algorithm. The patch was rejected because `set-cover-model` changed from 7480 to 7600 iterations.

This result is important:

> A change can be locally reasonable and performance-motivated yet still be unsuitable when it changes the numerical trajectory without sufficient benefit.

See [P12 negative result](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md).

## P14-A1: repeated before/current confirmation

P14-A1 repeated the quick6 comparison between current and `pre_tuning`:

| Metric | Result |
|---|---:|
| Current wins | 6/6 |
| Geometric-mean speedup | 1.18889 |
| Median speedup | 1.19502 |
| Iteration-count changes | 0/6 |

See [P14-A1 summary](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md).

## Eight-card throughput

The fast8 experiment measured eight independent MPS jobs:

```text
8-card concurrent: 146 s
one-GPU sequential: 558 s
```

This is batch throughput, not a distributed multi-GPU solver for one LP.

See [8-card summary](../validation/w7900_8card_batch_fast8_summary_20260616.md).

## Current endpoint

The accepted current policy is:

```text
W7900 default SpMV: HIPSPARSE_SPMV_CSR_ALG1
fallback: CUPDLP_HIP_SPMV_ALG=csr_alg2
validation anchor: CPU/ROCm status and numerical checks
before anchor: ae3b683 / pre_tuning
```

P10, P11, P12, and P14-A1 close the current W7900 tuning evidence chain. A repeated ALG1-vs-ALG2 P14-B study may be added as optional evidence, but it is not unfinished core scope.

## Rules for future tuning

1. Freeze a before reference and case list.
2. Record status, residuals, gap, `nIter`, wall time, and solve time.
3. Use repeated runs for timing claims.
4. Profile before selecting a patch.
5. Reject changes that introduce unexplained convergence movement.
6. Keep hard cases visible and separate.
7. Do not tune only for smoke cases.
8. Preserve a runtime rollback for platform-sensitive policy changes.

## Related documents

- [ROCm profiling notes](ROCM_PROFILING_NOTES.md)
- [ROCm tuning guide](TUNING_GUIDE_ROCM.md)
- [W7900 current status](W7900_CURRENT_STATUS.md)
- [Validation index](../validation/README.md)
