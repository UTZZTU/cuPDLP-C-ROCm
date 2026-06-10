# cuPDLP-C-ROCm

> 中文主页: [README.zh-CN.md](README.zh-CN.md)  
> ROCm/gfx1150 quick start: [README_ROCM_gfx1150.md](README_ROCM_gfx1150.md)  
> Documentation map: [docs/README.md](docs/README.md)  
> Validation index: [validation/README.md](validation/README.md)  
> Benchmark index: [docs/benchmarks/README.md](docs/benchmarks/README.md)

`cuPDLP-C-ROCm` is a ROCm/HIP port and validation fork of upstream cuPDLP-C for AMD GPUs/APUs. The project keeps the CPU path and upstream-compatible CUDA path, and adds a ROCm/HIP backend for AMD Radeon-class hardware.

| Item | Current value |
|---|---|
| Primary ROCm target | AMD Radeon 890M |
| ROCm architecture | `gfx1150` |
| ROCm version used in local validation | 7.2.1 |
| Planned larger AMD target | AMD Radeon PRO W7900 / `gfx1100` |
| CUDA baseline devices | RTX 3090, RTX 4090D, H100 |

> Status: experimental but buildable. The ROCm/HIP backend has passed smoke validation, Netlib validation, cross-device benchmark checks, and large-MPS baseline testing on AMD Radeon 890M / `gfx1150`. It is not yet a production-ready or fully tuned ROCm solver release.

## Start here

| Need | English | 中文 |
|---|---|---|
| ROCm/gfx1150 quick start | [README_ROCM_gfx1150.md](README_ROCM_gfx1150.md) | [README_ROCM_gfx1150.zh-CN.md](README_ROCM_gfx1150.zh-CN.md) |
| Full documentation map | [docs/README.md](docs/README.md) | [docs/README.md](docs/README.md) |
| Validation data index | [validation/README.md](validation/README.md) | [validation/README.zh-CN.md](validation/README.zh-CN.md) |
| Benchmark index | [docs/benchmarks/README.md](docs/benchmarks/README.md) | [docs/benchmarks/README.md](docs/benchmarks/README.md) |

## Documentation

| Topic | English | 中文 |
|---|---|---|
| Build / run / validation workflow | [docs/ROCM_WORKFLOW.md](docs/ROCM_WORKFLOW.md) | [docs/ROCM_WORKFLOW.zh-CN.md](docs/ROCM_WORKFLOW.zh-CN.md) |
| CPU vs ROCm validation semantics | [docs/VALIDATION.md](docs/VALIDATION.md) | [docs/VALIDATION.zh-CN.md](docs/VALIDATION.zh-CN.md) |
| Backend modes and naming policy | [docs/BACKEND_MODES_AND_NAMING.md](docs/BACKEND_MODES_AND_NAMING.md) | [docs/BACKEND_MODES_AND_NAMING.zh-CN.md](docs/BACKEND_MODES_AND_NAMING.zh-CN.md) |
| CUDA to ROCm migration case study | [docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md](docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) | [docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md](docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) |
| ROCm porting guide | [docs/ROCM_PORTING_GUIDE.md](docs/ROCM_PORTING_GUIDE.md) | [docs/ROCM_PORTING_GUIDE.zh-CN.md](docs/ROCM_PORTING_GUIDE.zh-CN.md) |
| ROCm profiling notes | [docs/ROCM_PROFILING_NOTES.md](docs/ROCM_PROFILING_NOTES.md) | [docs/ROCM_PROFILING_NOTES.zh-CN.md](docs/ROCM_PROFILING_NOTES.zh-CN.md) |
| ROCm tuning history | [docs/ROCM_TUNING_HISTORY.md](docs/ROCM_TUNING_HISTORY.md) | [docs/ROCM_TUNING_HISTORY.zh-CN.md](docs/ROCM_TUNING_HISTORY.zh-CN.md) |
| ROCm tuning guide | [docs/TUNING_GUIDE_ROCM.md](docs/TUNING_GUIDE_ROCM.md) | [docs/TUNING_GUIDE_ROCM.zh-CN.md](docs/TUNING_GUIDE_ROCM.zh-CN.md) |
| Cross-device Netlib benchmarks | [docs/CROSS_DEVICE_BENCHMARKS.md](docs/CROSS_DEVICE_BENCHMARKS.md) | [docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md](docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md) |
| Large MPS benchmark plan | [docs/LARGE_MPS_BENCHMARK_PLAN.md](docs/LARGE_MPS_BENCHMARK_PLAN.md) | [docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md](docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md) |
| greenbea numerical behavior | [docs/NUMERICAL_BEHAVIOR_GREENBEA.md](docs/NUMERICAL_BEHAVIOR_GREENBEA.md) | [docs/NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md](docs/NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md) |
| Upstream reference snapshot | [README_UPSTREAM.md](README_UPSTREAM.md) | — |

`README_UPSTREAM.md` is intentionally kept as an upstream reference snapshot and is not translated or rewritten as project documentation.

## Benchmarks

The raw `.mps` benchmark files are not committed. Curated result CSVs and explanation documents are committed instead.

| Topic | English | 中文 | Raw CSV |
|---|---|---|---|
| Large MPS CUDA/ROCm baseline | [summary](docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.md) | [中文版](docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.zh-CN.md) | [platform summary](results/benchmarks/large_mps_platform_summary_20260610.csv), [per-case timing](results/benchmarks/large_mps_per_case_timing_summary_20260610.csv) |
| cuPDLPx vs cuPDLP-C short13 | [comparison](docs/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.md) | [中文版](docs/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.zh-CN.md) | [comparison CSV](results/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.csv) |

## What this repository provides

- CPU-only cuPDLP-C build path.
- Upstream-compatible CUDA build path for NVIDIA baselines.
- ROCm/HIP backend built from migrated CUDA backend code.
- `plc` executable linked against the ROCm/HIP backend.
- CPU-vs-ROCm smoke validation scripts.
- Extended Netlib validation cases.
- Cross-device benchmark workflows and summaries for RTX 3090, RTX 4090D, H100, and Radeon 890M.
- Large MPS benchmark documents and curated CSV summaries.
- `rocprofv3` profiling workflow and ROCm tuning notes.
- Migration documentation for CUDA-to-ROCm/HIP scientific-computing projects.

## Backend modes

| Mode | CMake options | Role |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | Correctness and portability baseline |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | Upstream-compatible NVIDIA backend and benchmark baseline |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD Radeon ROCm/HIP target backend |

`BUILD_CUDA` and `BUILD_ROCM` must not be enabled at the same time. Use separate build directories such as `build-cpu`, `build-cuda`, and `build-rocm-plc`.

## Current validation and benchmark status

Large MPS baseline status:

| Platform | Backend | Result |
|---|---|---|
| RTX 3090 | CUDA upstream | 25/26 OPTIMAL, 1/26 TIMELIMIT |
| Radeon 890M | ROCm/HIP baseline | 24/26 OPTIMAL, 2/26 TIMELIMIT |
| RTX 4090D | CUDA upstream | 26/26 OPTIMAL |
| H100 | CUDA upstream | 26/26 OPTIMAL |

cuPDLPx short13 comparison status:

| Solver | Platform | Result |
|---|---|---|
| cuPDLP-C upstream | RTX 4090D CUDA | 13/13 OPTIMAL on selected short/medium cases |
| cuPDLPx v0.2.9 | RTX 4090D CUDA | 13/13 OPTIMAL on the same selected cases |

## Quick start: ROCm/HIP build

```bash
cmake -S . -B build-rocm-plc -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DBUILD_TESTING=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1150

cmake --build build-rocm-plc --target plc -j"$(nproc)"
```

Run a smoke example:

```bash
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_sum.json \
  -nIterLim 200
```

## Validation

```bash
./scripts/check_rocm_port.sh
ctest --test-dir build-rocm-plc --output-on-failure
```

Extended validation:

```bash
RESULT_ROOT=validation/results/extended_netlib \
  ./scripts/run_validation.sh validation/cases_extended_netlib.txt
```

See [validation/README.md](validation/README.md) for curated validation summaries and CSV files.

## Profiling and tuning

```bash
RESULT_ROOT=profiling/results/current ./scripts/profile_rocm_smoke.sh

python3 scripts/summarize_rocm_profile.py \
  --input profiling/results/current \
  --output profiling/results/current/profile_summary.md
```

See [docs/ROCM_PROFILING_NOTES.md](docs/ROCM_PROFILING_NOTES.md), [docs/ROCM_TUNING_HISTORY.md](docs/ROCM_TUNING_HISTORY.md), and [docs/TUNING_GUIDE_ROCM.md](docs/TUNING_GUIDE_ROCM.md).

## Adapting to another ROCm GPU

Identify the GPU architecture:

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
```

Then set the matching architecture, for example:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1100
```

for AMD Radeon PRO W7900, depending on ROCm support.
