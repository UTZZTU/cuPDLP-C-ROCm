# Final W7900 Formal Compact Evidence (2026-07-29)

> 中文：[README.zh-CN.md](README.zh-CN.md)
> Interpretation: [Final W7900 results](../../docs/W7900_FINAL_RESULTS_20260729.md)

This directory contains compact, reviewable data from the final formal W7900
experiment. Raw MPS inputs, raw profiler traces, full resource time series, and
large archives remain outside Git.

## Identity

```text
branch=rocm-w7900-gfx1100
solver=735764807d8698ff30811d1a6fcc45d4a3fd4817
harness=b5b9a6ffc1a041a48a0e051568d0134a3822556c
Window1=d2ce13091072a7c40c2c89bdd988e94c2fca36772da38e0af87de6332e7cd94a
Window2=7f8fbcd45591f4dbe0899d18df76329b1f9a17ff433b6dcd3c06d743aaead0db
```

## Coverage

| Stage | Count | Status |
|---|---:|---|
| baseline23 | 46 | 46/46 `VALIDATED_OPTIMAL` |
| precision | 30 | 30/30 `VALIDATED_OPTIMAL` |
| profiles | 5 | 5/5 `PASS` |
| static features | 23 | 23/23 `PASS` |
| formal solver total | 76 | 76/76 |

## Contents

Identity/QC:

- `formal_experiment_identity.json`
- `formal_experiments_complete.json`
- `final_analysis_released.json`
- `window1_qc_summary.json`
- `window2_qc_summary.json`
- `static_feature_validation_report.json`
- `files.sha256`

Baseline:

- `baseline_aggregated.csv`
- `baseline_repeats.csv`
- `throughput_summary.csv`
- `baseline_resource_summary.csv`

Tolerance study:

- `precision_matrix.csv`
- `precision_aggregated.csv`
- `precision_sensitivity.csv`
- `precision_resource_summary.csv`

Profiling:

- `profile_summary.csv`
- Detailed hotspots remain grounded in the historical P10 compact tables.

Static/analysis:

- `nonhard23_mps_structural_features.csv`
- `nonhard23_feature_dictionary.csv`
- `static_performance_spearman.csv`
- `static_association_leave_one_out.csv`
- `final_claims_review.csv`
- `final_summary.csv`

## Verify

```bash
python3 ../../scripts/analysis/generate_final_w7900_release.py --check-only
```

Expected:

```text
FINAL_W7900_RELEASE_DATA_PASS
```

## Boundaries

- compact evidence, not raw archives;
- throughput means sequential independent MPS cases;
- tolerance conclusions cover five cases;
- static correlations are exploratory;
- final profile summary validates collection integrity, not new hotspot ratios;
- hard3 is outside the formal nonhard23 matrix.
