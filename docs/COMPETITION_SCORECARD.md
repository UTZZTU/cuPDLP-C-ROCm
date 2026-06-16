# Competition scorecard alignment

> 中文: [COMPETITION_SCORECARD.zh-CN.md](COMPETITION_SCORECARD.zh-CN.md)

This page maps the AMD ROCm/Radeon contest requirements to repository evidence. It is a reviewer-oriented checklist, not the main project entry point. General users should start from the [Chinese homepage](../README.md), [English README](../README.en.md), and [documentation map](README.md).

## Scope

Project: ROCm/HIP migration, validation, benchmarking, and profiling of a large-scale linear programming solver on AMD Radeon-class GPUs.

Current status:

- Radeon 890M / `gfx1150`: first ROCm migration target, validation, and tuning history.
- Radeon PRO W7900 / `gfx1100`: workstation-class validation target with current non-hard large-MPS baseline.
- NVIDIA RTX 3090 / RTX 4090D / H100: CUDA reference devices for comparison.

## Scorecard

| Contest requirement | Repository evidence | Current status | Remaining work |
|---|---|---|---|
| Project background and challenge | [COMPETITION_README.md](COMPETITION_README.md), [CUDA-to-ROCm case study](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) | CUDA-oriented solver migrated toward ROCm/HIP; LP/HPC workload challenge documented | Technical paper should turn this into a concise narrative |
| Solution and implementation | HIP backend, [ROCM_WORKFLOW.md](ROCM_WORKFLOW.md), [ROCM_PORTING_GUIDE.md](ROCM_PORTING_GUIDE.md), README backend-mode section | CPU, CUDA, and ROCm backend modes are documented | Paper/PPT should include a module diagram and ROCm component map |
| ROCm component usage | HIP runtime, hipBLAS/hipSPARSE build path, `rocprofv3`/`rocprof` workflow, ROCm device architecture selection | ROCm/HIP build and profiling workflow are present | Add W7900 profiling result tables after the next W7900 run |
| Performance and resource analysis | [W7900 performance behavior](W7900_PERFORMANCE_BEHAVIOR.md), [ROCM tuning history](ROCM_TUNING_HISTORY.md), validation/benchmark CSVs | Current W7900 non-hard23 summary and cross-device references are committed | Need W7900 `rocprof` starter3 results, VRAM/telemetry, and before/current core6 comparison |
| Reproducibility and delivery | [REPRODUCIBILITY.md](REPRODUCIBILITY.md), validation case lists, scripts, curated CSV/Markdown summaries | Fresh W7900 recovery, data policy, expected outputs, and profiling workflow are documented | Lightweight Docker/container skeleton is present; strict final image remains future packaging work |
| Functional completeness and code quality | Source tree, scripts, validation summaries, backend mode policy | Main solver path is buildable and validation-driven | Add more code-level comments only where needed; avoid cosmetic churn |
| Stage results and plan | [W7900 current status](W7900_CURRENT_STATUS.md), [W7900 optimization baselines](W7900_OPTIMIZATION_BASELINES.md), [W7900 profiling plan](W7900_ROCM_PROFILING_PLAN.md) | Current/before/after policy is explicit | Run W7900 profiling, hard3 probes, then W7900-specific tuning |
| Innovation add-on: unsupported functionality | ROCm/HIP backend adaptation of a CUDA-oriented scientific solver | Project demonstrates a non-trivial ROCm backend migration | External ROCm upstream PR is not yet claimed |
| Innovation add-on: bottleneck optimization | 890M tuning history and planned W7900 profiling | Prior ROCm optimization history is documented | W7900-specific bottleneck claims must wait for `rocprof` results |

## Current caution

The current W7900 non-hard23 result is a post-890M-tuning engineering baseline, not the true unoptimized first-runnable ROCm baseline. The true before/current comparison should use `ae3b683 / pre_tuning` versus current `rocm-w7900-gfx1100`.

<!-- W7900_LATEST_EXPERIMENTS_20260616_BEGIN -->
## 2026-06-16 W7900 evidence update

The W7900 evidence set now includes:

| Requirement area | Latest evidence |
|---|---|
| Profiling and bottleneck evidence | [W7900 rocprof starter3 summary](../validation/w7900_rocprof_starter3_summary_20260616.md) |
| Hard-case handling | [W7900 hard3 probe2 600s summary](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.md) |
| Before/current comparison | [W7900 before/current fast-core6 summary](../validation/w7900_before_current_core6_fast_summary_20260616.md) |
| Multi-GPU throughput | [W7900 8-card fast8 batch summary](../validation/w7900_8card_batch_fast8_summary_20260616.md) |
<!-- W7900_LATEST_EXPERIMENTS_20260616_END -->

## Final W7900 competition status / 2026-06-17

The W7900 competition-facing workflow is now complete for the current
repository scope. Earlier “next planned work” items such as W7900 profiling,
before/current analysis, and W7900-specific tuning have been closed by the
P10/P11/P12 evidence chain.

Final competition-facing conclusion:

- W7900 / `gfx1100` ROCm build and validation are complete.
- P10 targeted rocprof profiling has been archived.
- P11 SpMV tuning is the accepted W7900-specific tuning endpoint.
- The current W7900 default SpMV algorithm is
  `HIPSPARSE_SPMV_CSR_ALG1`.
- The old default can be restored with
  `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
- P12 records a rejected buffer-algorithm consistency patch to show that
  additional execution-layer changes were tested conservatively.

Recommended final evidence links:

- `docs/W7900_CURRENT_STATUS.md`
- `validation/w7900_p11_spmv_tuning_summary_20260617.md`
- `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md`
