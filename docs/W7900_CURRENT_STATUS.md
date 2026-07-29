# W7900 Current Status

> 中文：[W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md)
> Final results: [W7900_FINAL_RESULTS_20260729.md](W7900_FINAL_RESULTS_20260729.md)

This is the authoritative current-status page for Radeon PRO W7900 / `gfx1100`.
Dated historical reports remain under `validation/`.

## Final conclusion

The formal W7900 experiment, QC, and offline-analysis release are complete:

- nonhard23: 23 cases × 2 repeats, 46/46 `VALIDATED_OPTIMAL`;
- tolerance study: 5 cases × 3 levels × 2 repeats,
  30/30 `VALIDATED_OPTIMAL`;
- targeted profiling: 5/5 `PASS`;
- static structure analysis: 23/23 `PASS`;
- total formal solver records: **76/76**;
- final markers:
  `FORMAL_W7900_EXPERIMENTS_COMPLETE`,
  `FINAL_ANALYSIS_RELEASED`.

The current release does not require another W7900 run. New hardware work should
begin only from a new, pre-defined research question.

## Formal identity

| Role | Value |
|---|---|
| Formal branch | `rocm-w7900-gfx1100` |
| Frozen solver | `735764807d8698ff30811d1a6fcc45d4a3fd4817` |
| Formal harness | `b5b9a6ffc1a041a48a0e051568d0134a3822556c` |
| Window 1 SHA256 | `d2ce13091072a7c40c2c89bdd988e94c2fca36772da38e0af87de6332e7cd94a` |
| Window 2 SHA256 | `7f8fbcd45591f4dbe0899d18df76329b1f9a17ff433b6dcd3c06d743aaead0db` |

The formal QC verifies that `CMakeLists.txt`, `cmake/`, `cupdlp/`, and
`interface/` match the frozen solver baseline.

## Core numbers

| Metric | Formal result |
|---|---:|
| Complete 23-case total time | 2950.625997 s / 2950.674611 s |
| Single-card sequential throughput | 28.061842 / 28.061379 cases/hour |
| Mean throughput | **28.061611 cases/hour** |
| Median total-time CV | **0.377%** |
| CV below 2% | **22/23** |
| Identical repeat iteration counts | **23/23** |
| Top-three total-time share | **82.22%** |
| Tolerance-study total-time ratio | **1.01×–4.01×** |
| Tolerance-study iteration ratio | **2.02×–11.58×** |
| Maximum achieved-error/requested-tolerance | **0.998079** |

## Workload interpretation

The final data separates:

1. iteration/compute-dominated cases such as `s100`, `Primal2_1000`,
   `thk_63`, and `square41`;
2. load/initialization-dominated cases, with `L2CTA3D` as the clearest
   example.

A useful model is:

```text
total time ≈ load/initialization/finalization
             + per-iteration cost × iteration count
```

See [W7900 performance behavior](W7900_PERFORMANCE_BEHAVIOR.md).

## Profiling and tuning endpoint

Historical P10 compact evidence identifies rocSPARSE CSR SpMV as a major kernel
group, with copy and launch overhead also visible. P11 accepted
`HIPSPARSE_SPMV_CSR_ALG1` as the default with
`CUPDLP_HIP_SPMV_ALG=csr_alg2` as fallback. P12 was rejected because it changed
the iteration trajectory. P14-A1 confirmed repeated quick6 gains with identical
iteration counts.

Final session2 completed and validated five profile traces, but raw traces stay
outside Git and trace-file counts are not used to invent new hotspot ratios.

## Boundaries

- no one-LP distributed multi-GPU capability;
- historical fast8 is independent-task throughput only;
- tolerance results cover five cases;
- static correlations are exploratory and non-causal;
- hard3 is separate from nonhard23;
- Docker is an environment skeleton, not the formal measurement source;
- presolve-off is the primary validation contract;
- no claim of a new PDLP algorithm or certification of all AMD GPUs.

## Continue reading

- [Final results](W7900_FINAL_RESULTS_20260729.md)
- [Final reproduction guide](FINAL_REPRODUCTION_GUIDE.md)
- [Profiling notes](ROCM_PROFILING_NOTES.md)
- [Validation index](../validation/README.md)
- [Final compact evidence](../validation/final_w7900_20260729/README.md)
