# ROCm Profiling Evidence and Final Conclusions

> 中文：[ROCM_PROFILING_NOTES.zh-CN.md](ROCM_PROFILING_NOTES.zh-CN.md)
> Final results: [W7900_FINAL_RESULTS_20260729.md](W7900_FINAL_RESULTS_20260729.md)

This document separates detailed hotspot evidence from final formal trace
integrity. Dated compact CSV/Markdown files are the source of specific hotspot
claims; raw traces remain outside Git.

## Profiling stages

| Stage | Platform | Role |
|---|---|---|
| Early structural profiling | Radeon 890M / `gfx1150` | Synchronization, launch, copy, and runtime-query overhead |
| P10 targeted profiling | W7900 / `gfx1100` | Kernel/API hotspots for five large-MPS cases |
| Final session2 profile gate | W7900 / `gfx1100` | Formal identity and trace-collection integrity |

P10 supports detailed hotspot interpretation. Final session2 supports formal
collection and archival completeness.

## P10 cases and evidence

Cases: `thk_48`, `square41`, `L2CTA3D`, `set-cover-model`,
`tpl-tub-ws1617`.

Evidence:

- P10 summary
- runtime table
- kernel top table
- HIP API top table
- memory-copy table
- milestone deltas

The compact evidence supports:

- rocSPARSE CSR SpMV as a major GPU kernel group, especially for
  `set-cover-model`, `square41`, and `thk_48`;
- prominent `hipMemcpy` cost in longer runs;
- visible `hipMemcpyAsync` and `hipLaunchKernel` overhead;
- controlled work on SpMV policy, launch volume, and narrow copy reduction;
- no unvalidated changes to residual, restart, termination, scaling, or
  floating-point update order.

## Profiling-to-tuning chain

P11 accepted `HIPSPARSE_SPMV_CSR_ALG1` as the default and retained
`CUPDLP_HIP_SPMV_ALG=csr_alg2` as fallback.

P12 was rejected after the `set-cover-model` iteration count changed from 7480
to 7600.

P14-A1 then confirmed repeated current gains on quick6 with identical iteration
counts.

Profiling proposes a measurement question; an accepted optimization still
requires termination, feasibility, gap, iteration, and repeated-performance
checks.

## Final session2 profile gate

All five final profiles have:

```text
runtime_status = DONE
exit_code = 0
profile_validation_status = PASS
trace_csv_count = 5
kernel_trace_count = 1
```

See
[profile_summary.csv](../validation/final_w7900_20260729/profile_summary.csv).

This proves formal trace collection and archival integrity. It does not create
new kernel rankings or percentages. The repository does not infer hotspots from
file counts and does not commit raw traces.

## Final endpoint

```text
Detailed W7900 hotspot source: P10 compact evidence
Formal profiling integrity: session2 5/5 PASS
Accepted tuning endpoint: CSR_ALG1 default
Required guardrail: correctness, convergence trajectory, repeatability
```

The current release requires no additional long profiling. Future traces should
serve a new, explicit question such as a new GPU architecture, reduction path,
or scalar-readback investigation.
