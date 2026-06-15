# Competition scorecard alignment

> 中文: [COMPETITION_SCORECARD.zh-CN.md](COMPETITION_SCORECARD.zh-CN.md)

This page maps the AMD ROCm/Radeon contest requirements to repository evidence. It is a reviewer-oriented checklist, not the main project entry point. General users should start from [../README.md](../README.md) and [README.md](README.md).

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
