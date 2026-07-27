# cuPDLP-C-ROCm

> 中文主页: [README.md](README.md)
> Documentation map: [docs/README.md](docs/README.md)
> Competition reviewer entry: [docs/COMPETITION_README.md](docs/COMPETITION_README.md)

`cuPDLP-C-ROCm` is a ROCm/HIP port, validation, and performance-analysis branch of upstream [cuPDLP-C](README_UPSTREAM.md). It preserves the CPU path and the upstream-compatible CUDA path, adds an AMD GPU backend, and records the engineering, numerical-validation, and performance evidence required for a scientific-computing migration from CUDA to ROCm.

## Project scope

This project does not introduce a new linear-programming algorithm. Its contributions are:

- porting the cuPDLP-C GPU execution path to ROCm/HIP;
- maintaining CPU, CUDA, and ROCm backend modes;
- building a traceable evidence chain for smoke, Netlib, large-MPS, profiling, and tuning;
- recording both accepted optimizations and rejected experiments that affect convergence behavior;
- documenting reusable CUDA-to-ROCm migration lessons for scientific software.

| Item | Current status |
|---|---|
| Main branch | `rocm-w7900-gfx1100` |
| Current primary ROCm platform | Radeon PRO W7900 / `gfx1100` |
| Earlier ROCm milestone | Radeon 890M / `gfx1150` |
| Reference backends | CPU and CUDA on RTX 3090, RTX 4090D, and H100 |
| Current W7900 SpMV default | `HIPSPARSE_SPMV_CSR_ALG1` |
| Fallback | `CUPDLP_HIP_SPMV_ALG=csr_alg2` |
| Release status | Research and engineering validation project; not a broadly certified production solver release |

## Key results

| Evidence | Result | Interpretation |
|---|---|---|
| W7900 large-MPS non-hard23 | 23/23 `OPTIMAL` | 2960.171 s wall time; 2742.940 s solve time |
| P10 targeted profiling | rocSPARSE CSR SpMV is the dominant GPU hotspot | `hipMemcpy`, `hipMemcpyAsync`, and kernel launch overhead also matter |
| P11 SpMV tuning | `CSR_ALG1` accepted as the current default | `csr_alg2` remains available as a runtime fallback |
| P12 negative experiment | patch rejected | `set-cover-model` changed from 7480 to 7600 iterations, showing that execution-layer changes can alter the numerical trajectory |
| P14-A1 quick6 repeats | current wins 6/6 | geometric-mean speedup 1.18889; median 1.19502; iteration counts unchanged |
| 8-card fast8 batch | 146 s versus 558 s sequential on one GPU | throughput for eight independent MPS jobs, not distributed solution of one LP |

See [W7900 current status](docs/W7900_CURRENT_STATUS.md) and the [validation index](validation/README.md) for boundaries and source artifacts.

## Solver and execution flow

```text
MPS input
  -> HiGHS parsing / optional presolve
  -> cuPDLP model and scaling
  -> CSR + CSC sparse matrices
  -> CPU / CUDA / ROCm backend
  -> PDHG iterations
  -> feasibility, gap, and termination checks
  -> JSON / solution output
```

The main workload consists of `Ax` and `Aᵀy` sparse matrix-vector products, vector updates, projections, reductions, step-size adaptation, and restart logic. End-to-end behavior is usefully summarized as:

```text
total time ≈ per-iteration cost × number of iterations
```

A faster GPU kernel therefore does not guarantee a shorter solve. Floating-point order and execution-layer changes can also alter the convergence path.

## Backend modes

| Mode | CMake options | Purpose |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | Correctness and portability baseline |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | NVIDIA reference backend |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD GPU backend |

`BUILD_CUDA` and `BUILD_ROCM` should not be enabled together. Use separate build directories for each backend.

## Quick start

### 1. Clone

```bash
git clone --recurse-submodules \
  --branch rocm-w7900-gfx1100 \
  https://github.com/UTZZTU/cuPDLP-C-ROCm.git
cd cuPDLP-C-ROCm
```

### 2. Inspect committed evidence on any host

A W7900 is not required to inspect committed CSV, Markdown, and SVG artifacts:

```bash
python3 - <<'PY'
import csv
from pathlib import Path

rows = list(csv.DictReader(
    Path("validation/w7900_large_mps_nonhard23_20260613.csv").open()
))
print("cases:", len(rows))
print("termination:", sorted({r["terminationCode"] for r in rows}))
print("wall:", sum(float(r["wall_seconds"]) for r in rows))
print("solve:", sum(float(r["dSolvingTime"]) for r in rows))
PY
```

The expected result is 23 cases with `OPTIMAL` termination.

### 3. Recover, build, and run smoke on W7900

```bash
bash scripts/bootstrap_w7900_workspace.sh
bash scripts/build_w7900_cpu.sh
bash scripts/build_w7900_rocm.sh
bash scripts/run_w7900_smoke.sh
```

The maintained W7900 scripts use:

```text
build-cpu/bin/plc
build-rocm-w7900/bin/plc
```

A minimal `plc` invocation is:

```bash
./build-rocm-w7900/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm.json \
  -nIterLim 200
```

See the [reproducibility guide](docs/REPRODUCIBILITY.md) for environment, dataset, profiling, and repeated-validation details.

## Documentation

| Need | English | 中文 |
|---|---|---|
| Full navigation | [Documentation map](docs/README.md) | [文档地图](docs/README.md) |
| Build and run | [ROCm workflow](docs/ROCM_WORKFLOW.md) | [ROCm 工作流](docs/ROCM_WORKFLOW.zh-CN.md) |
| Reproduce experiments | [Reproducibility](docs/REPRODUCIBILITY.md) | [可复现性指南](docs/REPRODUCIBILITY.zh-CN.md) |
| Validation semantics | [Validation](docs/VALIDATION.md) | [验证说明](docs/VALIDATION.zh-CN.md) |
| Current W7900 conclusions | [W7900 current status](docs/W7900_CURRENT_STATUS.md) | [W7900 当前状态](docs/W7900_CURRENT_STATUS.zh-CN.md) |
| Performance and tuning | [Performance behavior](docs/W7900_PERFORMANCE_BEHAVIOR.md), [tuning history](docs/ROCM_TUNING_HISTORY.md) | [性能行为](docs/W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)、[调优历史](docs/ROCM_TUNING_HISTORY.zh-CN.md) |
| Raw-summary index | [Validation index](validation/README.md) | [Validation 索引](validation/README.zh-CN.md) |
| CUDA-to-ROCm migration | [Migration case study](docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) | [迁移案例](docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) |
| Competition review | [Competition entry](docs/COMPETITION_README.md) | [竞赛入口](docs/COMPETITION_README.zh-CN.md) |

## Evidence and data policy

Raw large-MPS files, raw profiler traces, machine-local build directories, and temporary run directories are not committed. The repository keeps:

- case lists and manifests;
- curated CSV summaries;
- Markdown summaries;
- compact SVG figures;
- reproducibility scripts;
- accepted and rejected tuning conclusions.

Dated experiment reports remain as evidence. Current conclusions are maintained only in the homepages, `docs/W7900_CURRENT_STATUS*`, and index documents.

## Known limitations

- The ROCm implementation and tuning policy have primarily been validated on `gfx1150` and `gfx1100`; this is not certification for every AMD architecture.
- W7900 aggregate performance remains behind the high-end CUDA references in this repository; competitiveness must be interpreted per case and together with convergence behavior.
- hard3 is reported separately from non-hard23 and must not be hidden or merged into the primary result.
- The eight-GPU result is independent-job throughput, not a multi-GPU algorithm for one LP.
- The Docker files are an environment skeleton, not the source of the committed W7900 performance numbers.
- Optional Python/apps paths are not part of the primary ROCm validation path.

## Upstream and license

The upstream README snapshot is preserved in [README_UPSTREAM.md](README_UPSTREAM.md). Unless a file states otherwise, this repository is distributed under the [MIT License](LICENSE).
