# W7900 current status

> 中文: [W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md)

This is the authoritative current-status page for Radeon PRO W7900 / `gfx1100`. Dated experiment details remain under `validation/`; this page maintains only validated conclusions, interpretation boundaries, and primary evidence links.

## Current conclusion

- W7900 ROCm/HIP build, smoke, Netlib, and large-MPS validation are closed for the current project stage.
- The primary large-MPS result is `non-hard23`: 23/23 `OPTIMAL`; hard3 is reported separately.
- P10 targeted profiling identifies rocSPARSE CSR SpMV as the main GPU-kernel hotspot.
- P11 accepts a runtime-selectable SpMV policy and makes `HIPSPARSE_SPMV_CSR_ALG1` the current default.
- The previous policy remains available through `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
- The P12 buffer-algorithm consistency patch was rejected because it changed the iteration trajectory.
- P14-A1 repeated validation reports 6/6 current wins on quick6 with unchanged pre/current iteration counts.

The current branch is not an “unoptimized first port.” The correct baseline terminology is:

| Role | Version | Meaning |
|---|---|---|
| Pre-tuning anchor | `ae3b683` / `pre_tuning` | First runnable ROCm anchor |
| Current engineering baseline | current `rocm-w7900-gfx1100` | W7900 build after inherited 890M tuning |
| Accepted W7900 endpoint | P11 policy | `CSR_ALG1` default with `csr_alg2` fallback |
| Rejected experiment | P12 | Negative result that did not enter the accepted behavior |

## Large-MPS non-hard23

| Metric | Value |
|---|---:|
| Cases | 23 |
| Termination | 23/23 `OPTIMAL` |
| W7900 total wall time | 2960.171 s |
| W7900 total solve time | 2742.940 s |
| Source groups | `initial17_safe` 17; `near_optimal2_1800s` 2; `watchlist6_900s` 4 |

Primary evidence:

- [non-hard23 summary](../validation/w7900_large_mps_nonhard23_20260613.md)
- [solver CSV](../validation/w7900_large_mps_nonhard23_20260613.csv)
- [runtime CSV](../validation/w7900_large_mps_nonhard23_20260613_runtime.csv)

![W7900 non-hard23 wall comparison](assets/w7900/w7900_nonhard23_wall_compare.svg)

![W7900 non-hard23 solve comparison](assets/w7900/w7900_nonhard23_solve_compare.svg)

## Cross-device reference on the matching 23 cases

| Device | Backend | Wall time sum | Solve time sum |
|---|---|---:|---:|
| H100 | CUDA | 1701.350 s | 1433.577 s |
| RTX 3090 | CUDA | 1898.370 s | 1513.214 s |
| RTX 4090D | CUDA | 2730.760 s | 1329.789 s |
| W7900 | ROCm/HIP | 2960.171 s | 2742.940 s |
| Radeon 890M | ROCm/HIP | 5015.740 s | 4842.987 s |

The correct interpretation is:

- W7900 substantially improves over 890M;
- W7900 is competitive on selected cases;
- aggregate solve time remains behind the high-end CUDA references in this repository;
- conclusions must not be generalized from peak hardware specifications or one case.

See [W7900 performance behavior](W7900_PERFORMANCE_BEHAVIOR.md) for case classes.

## P10–P12 profiling and tuning evidence

### P10: targeted profiling

Compact profiling for five representative cases shows that:

- rocSPARSE CSR SpMV is the dominant GPU kernel on multiple cases;
- `hipMemcpy`, `hipMemcpyAsync`, and `hipLaunchKernel` are also material on longer cases;
- follow-up tuning should prioritize SpMV policy, launch count, and narrow copy-reduction experiments;
- residual, restart, termination, scaling, and floating-point update order must not be changed without explicit numerical validation.

Evidence: [P10 summary](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.md).

### P11: accepted SpMV tuning

P11 first created a runtime callsite inventory and ranked safe candidates, then implemented an opt-in SpMV algorithm switch, smoke validation, and a five-case sweep. The accepted policy is:

```text
default: HIPSPARSE_SPMV_CSR_ALG1
fallback: CUPDLP_HIP_SPMV_ALG=csr_alg2
```

Evidence:

- [P11 tuning summary](../validation/w7900_p11_spmv_tuning_summary_20260617.md)
- [algorithm sweep](../validation/w7900_p11_spmv_alg_sweep_20260617_summary.md)
- [default ALG1 smoke](../validation/w7900_p11_default_spmv_alg1_smoke_20260617_summary.md)

### P12: rejected execution-layer change

P12 made `hipsparseSpMV_bufferSize()` use the same selected algorithm as execution. `set-cover-model` changed from 7480 to 7600 iterations, so the patch was not accepted.

This demonstrates that an execution-layer-only change is not automatically numerically neutral. Evidence: [P12 negative finding](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md).

## P14-A1 repeated validation

quick6 repeated validation compares `ae3b683 / pre_tuning` against the current branch:

| Metric | Result |
|---|---:|
| Cases | 6 |
| Current wins | 6/6 |
| Geometric-mean speedup | 1.18889 |
| Median speedup | 1.19502 |
| Iteration-count consistency | unchanged between pre/current |

Evidence:

- [P14-A1 summary](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md)
- [comparison CSV](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv)
- [aggregated CSV](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_aggregated.csv)

## hard3 and eight-GPU boundaries

hard3 consists of:

```text
dlr1.mps
Dual2_5000.mps
fhnw-binschedule1.mps
```

These cases are used for difficult-case diagnosis and are not merged into the primary non-hard23 result. See [hard3 notes](W7900_LARGE_MPS_HARD3_NOTES.md) and the [probe2 summary](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.md).

The eight-card fast8 result, 146 s versus 558 s sequential on one GPU, measures concurrent throughput for eight independent MPS jobs. It is not an algorithm that distributes one LP across eight GPUs. See the [8-card fast8 summary](../validation/w7900_8card_batch_fast8_summary_20260616.md).

## Known limitations

- The implementation and tuning conclusions primarily target `gfx1100` and inherit selected `gfx1150` experience.
- Custom-kernel parameters and reduction assumptions do not constitute broad AMD-architecture certification.
- Aggregate performance remains jointly controlled by iteration count, convergence path, and host/device overhead.
- There is no distributed multi-GPU solver for one problem.
- The Docker files are an environment skeleton; committed W7900 numbers come from actual host runs.
- Every new optimization must check termination, feasibility, gap, iteration count, and repeated-run performance.

## Continue reading

- [Reproducibility](REPRODUCIBILITY.md)
- [Validation index](../validation/README.md)
- [ROCm profiling notes](ROCM_PROFILING_NOTES.md)
- [ROCm tuning history](ROCM_TUNING_HISTORY.md)
- [W7900 performance behavior](W7900_PERFORMANCE_BEHAVIOR.md)
- [Optimization-baseline policy](W7900_OPTIMIZATION_BASELINES.md)
