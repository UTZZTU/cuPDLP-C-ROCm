# Validation results index

> 中文: [README.zh-CN.md](README.zh-CN.md)

This directory stores reviewable case lists, curated CSV files, and Markdown summaries. Dated files are experiment records; start from [W7900 current status](../docs/W7900_CURRENT_STATUS.md) for the current interpretation.

## Primary current W7900 evidence

| Topic | Summary | CSV / data | Conclusion |
|---|---|---|---|
| Smoke | [English](w7900_smoke_summary_20260611.md) | [CSV](w7900_smoke_summary_20260611.csv) | CPU and ROCm status check |
| Extended Netlib | [English](w7900_extended_netlib_summary_20260611.md) | [CSV](w7900_extended_netlib_summary_20260611.csv) | Extended Netlib validation |
| 27-case baseline | [English](w7900_27cases_baseline_20260611.md) | [aggregated](w7900_27cases_baseline_20260611_aggregated.csv), [raw](w7900_27cases_baseline_20260611_raw.csv) | Early full W7900 baseline |
| Large-MPS non-hard23 | [English](w7900_large_mps_nonhard23_20260613.md) | [solver](w7900_large_mps_nonhard23_20260613.csv), [runtime](w7900_large_mps_nonhard23_20260613_runtime.csv) | 23/23 `OPTIMAL` |
| P10 targeted profiling | [English](w7900_p10_current_targeted_rocprof_20260617_summary.md) | [runtime](w7900_p10_current_targeted_rocprof_20260617_runtime.csv), [kernel](w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv), [HIP API](w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv) | CSR SpMV is the main hotspot |
| P11 SpMV tuning | [English](w7900_p11_spmv_tuning_summary_20260617.md) | [sweep](w7900_p11_spmv_alg_sweep_20260617.csv), [default smoke](w7900_p11_default_spmv_alg1_smoke_20260617.csv) | `CSR_ALG1` accepted as default |
| P12 negative result | [English](w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md) | — | Iteration trajectory changed; patch rejected |
| P14-A1 quick6 repeats | [English](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md) | [comparison](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv), [aggregated](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_aggregated.csv), [raw](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_raw.csv) | current wins 6/6 |
| hard3 probe2 | [English](w7900_large_mps_hard3_probe2_600s_summary_20260616.md) | [solver](w7900_large_mps_hard3_probe2_600s_solver_20260616.csv), [runtime](w7900_large_mps_hard3_probe2_600s_runtime_20260616.csv) | Difficult cases reported separately |
| 8-card fast8 batch | [English](w7900_8card_batch_fast8_summary_20260616.md) | [comparison](w7900_8card_batch_fast8_comparison_20260616.csv) | Independent-job throughput, not one-LP multi-GPU |

## P11 analysis chain

P11 was not based on one isolated sweep. The evidence was built in this order:

1. [Runtime callsite inventory](w7900_p11_runtime_callsite_inventory_20260617.md)
   [CSV](w7900_p11_runtime_callsite_inventory_20260617.csv)
2. [First patch candidates](w7900_p11_first_patch_candidates_20260617.md)
   [CSV](w7900_p11_first_patch_candidates_20260617.csv)
3. [SpMV algorithm-switch smoke](w7900_p11_spmv_alg_switch_smoke_20260617_summary.md)
   [CSV](w7900_p11_spmv_alg_switch_smoke_20260617.csv)
4. [Five-case algorithm sweep](w7900_p11_spmv_alg_sweep_20260617_summary.md)
   [CSV](w7900_p11_spmv_alg_sweep_20260617.csv)
5. [Default ALG1 smoke](w7900_p11_default_spmv_alg1_smoke_20260617_summary.md)
   [CSV](w7900_p11_default_spmv_alg1_smoke_20260617.csv)
6. [Final P11 summary](w7900_p11_spmv_tuning_summary_20260617.md)

## Before/current and earlier ROCm evidence

| Topic | Summary | Data |
|---|---|---|
| before/current fast-core6 | [English](w7900_before_current_core6_fast_summary_20260616.md) | [comparison](w7900_before_current_core6_fast_comparison_20260616.csv) |
| Derived per-iteration metrics | [English](w7900_before_current_core6_fast_derived_metrics_20260617.md) | [CSV](w7900_before_current_core6_fast_derived_metrics_20260617.csv) |
| W7900 vs cross-device 27 cases | [English](w7900_vs_cross_device_27cases_20260611.md) | [CSV](w7900_vs_cross_device_27cases_20260611.csv) |
| Cross-device full summary | [Project document](../docs/CROSS_DEVICE_BENCHMARKS.md) | [CSV](cross_device_full_summary.csv) |
| ROCm current vs reduce repeats | [English](rocm_current_vs_reduce_27cases_repeats_comparison.md) | [comparison](rocm_current_vs_reduce_27cases_repeats_comparison.csv), [aggregated](rocm_current_vs_reduce_27cases_repeats_aggregated.csv), [raw](rocm_current_vs_reduce_27cases_repeats_raw.csv) |
| ROCm profiling milestones | [English](rocm_prof_tuning_milestones_summary.md) | [summary](rocm_prof_tuning_milestones_summary.csv), [deltas](rocm_prof_tuning_milestones_deltas.csv) |
| ROCm tuning ablation | [English](rocm_tuning_ablation_6cases_repeats_summary.md) | [summary](rocm_tuning_ablation_6cases_repeats_summary.csv), [raw](rocm_tuning_ablation_6cases_repeats_raw.csv) |

## Large-MPS evidence layers

| Group | Summary | Data |
|---|---|---|
| initial17 safe | [English](w7900_large_mps_initial17_safe_20260613.md) | [solver](w7900_large_mps_initial17_safe_20260613.csv), [runtime](w7900_large_mps_initial17_safe_20260613_runtime.csv) |
| near-optimal2 | — | [solver](w7900_large_mps_near_optimal2_1800s_20260613.csv), [runtime](w7900_large_mps_near_optimal2_1800s_20260613_runtime.csv) |
| watchlist6 diagnostics | — | [solver](w7900_large_mps_watchlist6_diag_900s_20260613.csv), [runtime](w7900_large_mps_watchlist6_diag_900s_20260613_runtime.csv) |
| merged non-hard23 | [English](w7900_large_mps_nonhard23_20260613.md) | [solver](w7900_large_mps_nonhard23_20260613.csv), [runtime](w7900_large_mps_nonhard23_20260613_runtime.csv) |
| hard3 | [Project notes](../docs/W7900_LARGE_MPS_HARD3_NOTES.md) | [probe2 summary](w7900_large_mps_hard3_probe2_600s_summary_20260616.md) |

## Case lists

| Purpose | File |
|---|---|
| Basic smoke | [cases.txt](cases.txt) |
| Extended Netlib | [cases_extended_netlib.txt](cases_extended_netlib.txt) |
| W7900 27-case | [cases_benchmark_200m_w7900_27.txt](cases_benchmark_200m_w7900_27.txt) |
| Tuning quick6 | [cases_tuning_quick.txt](cases_tuning_quick.txt) |
| P10 starter3 | [cases_w7900_rocprof_starter3.txt](cases_w7900_rocprof_starter3.txt) |
| before/current core6 | [cases_w7900_large_mps_before_after_core6_fast.txt](cases_w7900_large_mps_before_after_core6_fast.txt) |
| non-hard23 | [cases_w7900_large_mps_before_after_nonhard23.txt](cases_w7900_large_mps_before_after_nonhard23.txt) |
| hard3 | [cases_w7900_large_mps_hard3.txt](cases_w7900_large_mps_hard3.txt) |
| 8-card fast8 | [cases_w7900_8card_batch_fast8.txt](cases_w7900_8card_batch_fast8.txt) |

## Interpretation rules

- Dated summaries are immutable experiment records; new current conclusions update the indexes and current-status page.
- `non-hard23` and hard3 are interpreted separately.
- Eight-card fast8 is independent-MPS throughput.
- Performance comparisons must include wall time, solve time, `nIter`, termination, feasibility, and gap.
- P12 is negative evidence and must remain discoverable.
- Raw `.mps`, raw profiler traces, and machine-local result directories are not committed.

## Related entries

- [W7900 current status](../docs/W7900_CURRENT_STATUS.md)
- [Reproducibility](../docs/REPRODUCIBILITY.md)
- [Validation semantics](../docs/VALIDATION.md)
- [Benchmark index](../docs/benchmarks/README.md)
