# Competition reviewer entry: ROCm-enabled large-scale LP solver on Radeon GPUs

> 中文: [COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md)

This page maps the code, validation, and performance evidence in the general open-source repository to competition review needs. It does not replace the [project homepage](../README.en.md) or redefine the project as contest-only software.

## Problem

cuPDLP-C is a PDLP/PDHG implementation for large-scale linear programming. Its main loop repeatedly executes sparse matrix-vector products, vector updates, projections, reductions, and convergence checks. The project addresses:

> How can a CUDA-oriented scientific solver be migrated to AMD ROCm/HIP, and how can reproducible evidence show that it builds, solves real instances, preserves acceptable numerical behavior, and can be tuned without undermining convergence reliability?

## Contributions

| Area | Contribution | Primary evidence |
|---|---|---|
| ROCm/HIP port | AMD backend added while preserving CPU and CUDA paths | [Migration case study](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md), [backend modes](BACKEND_MODES_AND_NAMING.md) |
| Correctness validation | smoke, Netlib, large-MPS, and CPU-vs-ROCm comparisons | [Validation index](../validation/README.md) |
| Cross-device analysis | 890M, W7900, RTX 3090, RTX 4090D, and H100 | [Cross-device benchmarks](CROSS_DEVICE_BENCHMARKS.md) |
| Profiling | P10 targeted rocprof identifies CSR SpMV and runtime overhead | [P10 summary](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.md) |
| Safe tuning | P11 accepts the `CSR_ALG1` default with a fallback | [P11 summary](../validation/w7900_p11_spmv_tuning_summary_20260617.md) |
| Negative result | P12 rejects a patch after iteration-count change | [P12 negative result](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md) |
| Repeated validation | P14-A1 reports 6/6 current wins on quick6 | [P14-A1 summary](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md) |
| Reproducibility | Environment recovery, data checks, expected outputs, and rerun policy | [Reproducibility](REPRODUCIBILITY.md) |

## Current W7900 results

| Metric | Result |
|---|---:|
| large-MPS non-hard23 | 23 cases |
| Termination | 23/23 `OPTIMAL` |
| Total wall time | 2960.171 s |
| Total solve time | 2742.940 s |
| P14-A1 current wins | 6/6 |
| P14-A1 geometric-mean speedup | 1.18889 |
| Current SpMV default | `HIPSPARSE_SPMV_CSR_ALG1` |

The current W7900 result is an engineering baseline after inherited 890M tuning, not an unoptimized first port:

| Role | Version |
|---|---|
| Before | `ae3b683` / `pre_tuning` |
| Current | current `rocm-w7900-gfx1100` |
| Accepted endpoint | P11 `CSR_ALG1` policy |
| Rejected change | P12 buffer-algorithm consistency patch |

See [W7900 current status](W7900_CURRENT_STATUS.md) for the complete interpretation.

## Performance interpretation

Performance cannot be explained by peak GPU specifications or aggregate time alone:

```text
total time ≈ per-iteration cost × number of iterations
```

W7900 is more likely to benefit when instances are large enough, SpMV/vector operations dominate, and convergence is stable. For cases such as `s100` and `Primal2_1000`, total time is more strongly controlled by iteration count and the gap trajectory.

The evidence is deliberately conservative:

- it reports the improvement over 890M;
- it does not hide that aggregate performance remains behind high-end CUDA references;
- hard3 is reported separately;
- the rejected P12 experiment remains visible;
- the eight-card result is identified as independent-job throughput, not one-problem multi-GPU solving.

## Reviewer reading order

1. [Project architecture](assets/competition/project_architecture.svg)
2. [Evidence map](assets/competition/evidence_map.svg)
3. [W7900 current status](W7900_CURRENT_STATUS.md)
4. [CUDA-to-ROCm migration case study](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md)
5. [P10 profiling](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.md)
6. [P11 tuning](../validation/w7900_p11_spmv_tuning_summary_20260617.md)
7. [P12 negative result](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md)
8. [P14-A1 repeats](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md)
9. [Reproducibility](REPRODUCIBILITY.md)
10. [Competition scorecard](COMPETITION_SCORECARD.md)

## Contribution boundaries

The project can claim:

- a real CUDA-to-ROCm/HIP solver migration;
- a three-backend engineering boundary;
- W7900 build, validation, profiling, tuning, and repeated validation;
- a safe-tuning methodology supported by accepted and rejected experiments;
- cross-device and per-case performance analysis.

The project must not claim:

- a new PDLP algorithm;
- that W7900 beats CUDA on every case;
- distributed solution of one LP in the eight-card experiment;
- that the Docker skeleton reproduces every performance number;
- broad certification across all AMD GPU architectures.

## Submission materials

Repository-side engineering material and evidence indexes are available. External paper, slides, and video status is maintained by the project owner at submission time; see the [submission checklist](SUBMISSION_CHECKLIST.md).

Raw `.mps` files and raw profiler traces are not committed. Reviewable scripts, case lists, curated CSV, Markdown summaries, and SVG figures are committed instead.
