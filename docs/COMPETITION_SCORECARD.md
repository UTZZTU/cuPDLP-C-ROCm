# Competition scorecard alignment

> 中文：[COMPETITION_SCORECARD.zh-CN.md](COMPETITION_SCORECARD.zh-CN.md)

This page maps contest-oriented evaluation items to the current repository evidence. It is not the general project homepage. General readers should start from the [English README](../README.en.md) or [documentation map](README.md).

## Current scope

**Project:** migration, validation, profiling, and controlled tuning of cuPDLP-C on AMD ROCm/HIP.

| Platform | Role |
|---|---|
| Radeon PRO W7900 / `gfx1100` | Current primary ROCm validation and tuning platform |
| Radeon 890M / `gfx1150` | Earlier migration and tuning milestone |
| RTX 3090 / RTX 4090D / H100 | CUDA references |
| CPU | Correctness and portability reference |

The project does not claim a new LP algorithm. Its contribution is the backend migration and the evidence-driven engineering methodology.

## Evidence scorecard

| Evaluation area | Repository evidence | Current status and boundary |
|---|---|---|
| Background and challenge | [Competition entry](COMPETITION_README.md), [migration case study](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) | Complete repository narrative; paper/PPT remain presentation artifacts |
| Solution architecture | HIP backend, compatibility layer, [backend modes](BACKEND_MODES_AND_NAMING.md), [porting guide](ROCM_PORTING_GUIDE.md) | CPU, CUDA, and ROCm paths documented; optional Python/apps paths are outside the primary validation contract |
| ROCm component usage | HIP runtime, hipBLAS, hipSPARSE, `rocprofv3`, `gfx1100` build scripts | Implemented and evidenced on W7900 |
| Functional validation | [Validation semantics](VALIDATION.md), [validation index](../validation/README.md) | Smoke, Netlib, large-MPS non-hard23, hard-case diagnostics, and repeated validation are archived |
| Performance analysis | [W7900 performance behavior](W7900_PERFORMANCE_BEHAVIOR.md), P10 summaries, cross-device CSV | P10 identifies rocSPARSE CSR SpMV as the dominant GPU hotspot; aggregate and per-case interpretations are both retained |
| Platform-specific tuning | [Tuning history](ROCM_TUNING_HISTORY.md), [P11 summary](../validation/w7900_p11_spmv_tuning_summary_20260617.md) | P11 accepts `HIPSPARSE_SPMV_CSR_ALG1`; `csr_alg2` remains a rollback |
| Conservative engineering | [P12 negative result](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md) | Rejected after a convergence-path change; demonstrates that execution-layer changes are not accepted on timing alone |
| Repeated before/current evidence | [P14-A1 summary](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md) | Current wins 6/6; geometric-mean speedup 1.18889; median 1.19502; iteration counts unchanged |
| Large-case outcome | [W7900 current status](W7900_CURRENT_STATUS.md) | non-hard23 is 23/23 `OPTIMAL`; hard3 remains explicitly separate |
| Multi-GPU evidence | [8-card fast8 summary](../validation/w7900_8card_batch_fast8_summary_20260616.md) | Independent-job throughput only; not a distributed algorithm for one LP |
| Reproducibility | [Reproducibility guide](REPRODUCIBILITY.md), scripts, case lists, checksums, curated CSV | Static evidence can be inspected on any host; fresh W7900 performance requires a matching ROCm machine |
| Delivery readiness | [Submission checklist](SUBMISSION_CHECKLIST.md) | Repository evidence is ready; paper, slides, and video are separate deliverables |

## Key numerical claims

| Claim | Value |
|---|---:|
| W7900 non-hard23 | 23/23 `OPTIMAL` |
| Total wall time | 2960.171 s |
| Total solve time | 2742.940 s |
| P14-A1 current wins | 6/6 |
| P14-A1 geometric-mean speedup | 1.18889 |
| P14-A1 median speedup | 1.19502 |
| Eight independent jobs | 146 s concurrent vs 558 s one-GPU sequential |

## Interpretation rules

Reviewers should keep these boundaries explicit:

1. The current W7900 result is a post-890M-tuning engineering baseline, not the true first-runnable baseline.
2. The before anchor for W7900 analysis is `ae3b683 / pre_tuning`.
3. The eight-card result measures throughput for independent jobs.
4. hard3 is not hidden inside non-hard23.
5. W7900 aggregate time trails the high-end CUDA references, while per-case competitiveness varies.
6. P12 is a negative result and must not be presented as an accepted optimization.
7. Optional P14-B repeated ALG1-vs-ALG2 evidence is an enhancement, not unfinished core scope.

## Recommended reviewer path

1. [Competition entry](COMPETITION_README.md)
2. [W7900 current status](W7900_CURRENT_STATUS.md)
3. [P10 targeted profiling](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.md)
4. [P11 SpMV tuning](../validation/w7900_p11_spmv_tuning_summary_20260617.md)
5. [P12 negative result](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md)
6. [P14-A1 repeated validation](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md)
7. [Reproducibility guide](REPRODUCIBILITY.md)
