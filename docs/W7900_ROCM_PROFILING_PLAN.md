# W7900 ROCm profiling plan

> 中文: [W7900_ROCM_PROFILING_PLAN.zh-CN.md](W7900_ROCM_PROFILING_PLAN.zh-CN.md)

This document defines the profiling plan before W7900 / `gfx1100` tuning. It should be used after the baseline documentation is stable and before making kernel-level changes.

<!-- W7900_OPTIMIZATION_BASELINES_20260614_BEGIN -->
## Baseline correction for future profiling

The current W7900 branch has already inherited earlier 890M/gfx1150 ROCm tuning. Future profiling should therefore distinguish `ae3b683` as the true pre-tuning anchor, current W7900 as the post-890M-tuning engineering baseline, and a future W7900-specific tuning branch as the final after-tuning result.

See [W7900 optimization baselines](W7900_OPTIMIZATION_BASELINES.md).
<!-- W7900_OPTIMIZATION_BASELINES_20260614_END -->

## Current baseline state

The profiling stage starts from a documented baseline:

- smoke validation: completed
- Netlib 27-case validation: completed
- large-MPS `initial17_safe`: completed
- large-MPS `watchlist6` + `near_optimal2`: completed
- combined large-MPS `non-hard23`: 23/23 `OPTIMAL`
- `hard3`: separated for convergence-trajectory analysis

The goal of profiling is not to re-prove correctness. The goal is to identify where the W7900 path spends time and which bottlenecks are worth tuning.

## Profiling case matrix

| Group | Cases | Purpose |
|---|---|---|
| fast representative | `set-cover-model`, `supportcase10`, `L2CTA3D` | Check fixed overhead, HIP API overhead, setup cost, and short-run kernel profile |
| competitive representative | `square41`, `thk_48`, `tpl-tub-ws1617` | Study cases where W7900 can approach or exceed high-end references in wall time |
| slow-but-solvable | `s100`, `Primal2_1000` | Study high-iteration behavior and gap trajectory after confirmed `OPTIMAL` follow-up |
| hard3 diagnostic | `dlr1`, `Dual2_5000`, `fhnw-binschedule1` | Short diagnostic only; do not mix into primary baseline before separate analysis |

## Tooling

Use a layered profiling workflow:

1. Baseline runtime JSON from the solver.
2. GPU telemetry using `rocm-smi` or AMD SMI.
3. HIP/kernel trace and statistics using `rocprofv3` when available.
4. Optional counter collection after the first trace identifies target kernels.

## Metrics to record

| Metric | Why it matters |
|---|---|
| `wall_seconds` | End-to-end user-visible performance |
| `dSolvingTime` | Solver-side compute time |
| `DeviceMatVecProdTime` | SpMV-related device time |
| `nIter` | Separates per-iteration speed from convergence behavior |
| relative primal/dual/gap | Indicates numerical progress and near-tolerance stalls |
| HIP API time | Shows launch/copy/runtime overhead |
| kernel statistics | Shows dominant kernels and repeated dispatch patterns |
| GPU power/temperature/utilization | Helps distinguish compute bottlenecks from environment issues |

## Profiling stages

### Stage 0: environment and tool detection

Record:

```bash
command -v rocprofv3 rocprof rocm-smi amd-smi hipcc || true
rocminfo | grep -E "Name:|Marketing Name|gfx" || true
rocm-smi || true
```

### Stage 1: no-profiler baseline rerun

Run the selected case without profiler first and save:

- JSON output
- terminal log
- `runtime_summary.csv`
- `rocm-smi` snapshot before and after

This gives the reference before profiler overhead.

### Stage 2: HIP and kernel trace

Preferred command form when `rocprofv3` is available:

```bash
rocprofv3 --stats --hip-trace --kernel-trace --output-format csv --output-directory "$OUT/rocprofv3" -- "$PLC" -fname "$MPS" -out "$JSON" -nIterLim "$ITER_LIMIT" -dTimeLim "$TIME_LIMIT"
```

Fallback command form if only legacy `rocprof` is available should be added after checking the installed version on the machine.

### Stage 3: analyze top kernels and overhead

For each case, produce:

- top kernels by total time
- top kernels by call count
- HIP API overhead summary
- ratio of `DeviceMatVecProdTime / dSolvingTime`
- relationship between `nIter` and total solve time

### Stage 4: choose tuning targets

Do not tune all code paths blindly. Use the profiling data to decide between:

- SpMV/kernel optimization
- reduction optimization
- avoiding unnecessary host-device copies
- lowering HIP setup or launch overhead
- tuning solver control path only if convergence behavior changes

## Expected interpretation

W7900 can be fast when:

- the case has enough work to amortize setup/launch overhead;
- SpMV and vector operations dominate;
- convergence is stable;
- memory bandwidth and VRAM capacity matter.

W7900 can be slow when:

- iteration count dominates;
- gap stalls close to tolerance;
- restart/step-size path differs from CUDA references;
- small cases are dominated by fixed overhead;
- current ROCm/gfx1100 kernels are not yet tuned.

## Output policy

Raw large MPS files and raw profiler trace directories should not be committed.

Commit only:

- scripts
- curated CSV summaries
- Markdown summaries
- small SVG charts
- selected compact profiler summaries

Recommended output root:

```text
/app/cupdlp_w7900/results/w7900_rocprof/
```

Recommended committed summaries:

```text
validation/w7900_rocprof_case_matrix_*.csv
validation/w7900_rocprof_kernel_top_*.csv
validation/w7900_rocprof_hip_api_top_*.csv
docs/W7900_ROCM_PROFILING_PLAN.md
```

## First profiling run recommendation

Start with three cases:

1. `set-cover-model` — fast/representative, useful for overhead and kernel dispatch analysis.
2. `square41` — competitive case, useful for showing W7900 strength.
3. `s100` — slow-but-solvable, useful for separating iteration count from per-iteration cost.

Do not start with hard3. Hard3 should be used only after the profiling workflow is stable.

## Completion update / 2026-06-17

This document is the original W7900 profiling plan. The plan has now been
executed and superseded by committed P10/P11/P12 artifacts.

Current status:

- P10 targeted rocprof profiling completed.
- P11 SpMV algorithm switch, smoke, and five-case sweep completed.
- Current W7900 default SpMV algorithm:
  `HIPSPARSE_SPMV_CSR_ALG1`.
- Rollback path:
  `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
- P12 SpMV buffer algorithm consistency experiment tested and rejected
  because it changed iteration count.

Superseding documents:

- `validation/w7900_p10_current_targeted_rocprof_20260617_summary.md`
- `validation/w7900_p11_spmv_tuning_summary_20260617.md`
- `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md`
