# Validation Results Index

> 中文：[README.zh-CN.md](README.zh-CN.md)

This directory contains reviewable case lists, curated CSV files, and Markdown
summaries. Current formal claims start from the
[final W7900 results](../docs/W7900_FINAL_RESULTS_20260729.md). Dated files remain
immutable historical evidence.

## Final formal W7900 evidence

| Topic | Entry | Conclusion |
|---|---|---|
| Final compact package | [Index](final_w7900_20260729/README.md) | 76/76 formal solver records validated |
| Identity and QC | [Identity](final_w7900_20260729/formal_experiment_identity.json) | Branch, solver, harness, archive SHA fixed |
| baseline23 | [Aggregated](final_w7900_20260729/baseline_aggregated.csv), [repeats](final_w7900_20260729/baseline_repeats.csv) | 23 × 2 = 46/46 |
| throughput | [Summary](final_w7900_20260729/throughput_summary.csv) | Two complete sequential single-card repeats |
| precision | [Matrix](final_w7900_20260729/precision_matrix.csv), [aggregated](final_w7900_20260729/precision_aggregated.csv) | 5 × 3 × 2 = 30/30 |
| sensitivity | [Ratios](final_w7900_20260729/precision_sensitivity.csv) | Case-dependent tolerance cost |
| resources | [Baseline](final_w7900_20260729/baseline_resource_summary.csv), [precision](final_w7900_20260729/precision_resource_summary.csv) | Formal resource coverage |
| profiles | [Summary](final_w7900_20260729/profile_summary.csv) | 5/5 trace validation PASS |
| static structure | [Features](final_w7900_20260729/nonhard23_mps_structural_features.csv) | 23/23 |
| associations | [Spearman](final_w7900_20260729/static_performance_spearman.csv) | Exploratory, non-causal |
| final claims | [Review table](final_w7900_20260729/final_claims_review.csv) | Values, sources, boundaries |

## Historical W7900 evidence chain

The following remains available for migration, tuning, and negative-evidence
history:

- smoke and extended Netlib;
- early 27-case and 2026-06-13 single-run non-hard23;
- P10 targeted profiling;
- P11 accepted SpMV policy;
- P12 rejected iteration-changing patch;
- P14-A1 repeated current-vs-pre-tuning;
- hard3 diagnostics;
- independent-task fast8.

## P10 compact profiling

- runtime table
- kernel top table
- HIP API top table
- memory-copy table
- milestone deltas

Specific hotspot claims remain grounded in these compact tables. Final session2
validates formal collection and trace integrity.

## Interpretation rules

1. Final formal repeat data is the current primary result.
2. Dated reports remain immutable.
3. nonhard23 and hard3 remain separate.
4. Single-card throughput is sequential independent MPS.
5. fast8 is eight independent jobs.
6. Compare total time, solver time, iterations, and numerical status together.
7. P12 negative evidence remains visible.
8. Tolerance conclusions cover five cases.
9. Static association is non-causal.
10. Raw MPS, raw traces, local runs, and credentials stay outside Git.

## Entry points

- [Final W7900 results](../docs/W7900_FINAL_RESULTS_20260729.md)
- [Current status](../docs/W7900_CURRENT_STATUS.md)
- [Final reproduction](../docs/FINAL_REPRODUCTION_GUIDE.md)
- [Validation semantics](../docs/VALIDATION.md)
- [Profiling notes](../docs/ROCM_PROFILING_NOTES.md)
