# cuPDLP-C-ROCm

> 中文版: [`README.zh-CN.md`](README.zh-CN.md)

`cuPDLP-C-ROCm` is a ROCm/HIP port and validation fork of upstream cuPDLP-C for AMD GPUs/APUs. The project keeps the CPU path and upstream-compatible CUDA path, and adds a ROCm/HIP backend for AMD Radeon-class hardware.

| Item | Current value |
|---|---|
| Primary ROCm target | AMD Radeon 890M |
| ROCm architecture | `gfx1150` |
| ROCm version used in local validation | 7.2.1 |
| Planned larger AMD target | AMD Radeon PRO W7900 / `gfx1100` |
| CUDA baseline devices | RTX 3090, RTX 4090D, H100 |

> Status: experimental but buildable. The ROCm/HIP backend has passed smoke validation and a cross-device Netlib benchmark matrix on AMD Radeon 890M / `gfx1150`. It is not yet a production-ready, broadly certified, or fully tuned ROCm solver release.

## Documentation

| English | Chinese | Purpose |
|---|---|---|
| [`docs/ROCM_WORKFLOW.md`](docs/ROCM_WORKFLOW.md) | [`docs/ROCM_WORKFLOW.zh-CN.md`](docs/ROCM_WORKFLOW.zh-CN.md) | Daily build, validation, profiling, and benchmark commands |
| [`docs/VALIDATION.md`](docs/VALIDATION.md) | [`docs/VALIDATION.zh-CN.md`](docs/VALIDATION.zh-CN.md) | CPU-vs-ROCm validation semantics |
| [`docs/CROSS_DEVICE_BENCHMARKS.md`](docs/CROSS_DEVICE_BENCHMARKS.md) | [`docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md`](docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md) | RTX 3090 / RTX 4090D / Radeon 890M benchmark matrix |
| [`docs/LARGE_MPS_BENCHMARK_PLAN.md`](docs/LARGE_MPS_BENCHMARK_PLAN.md) | [`docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md`](docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md) | H100-sourced large MPS workflow and cross-device plan |
| [`docs/ROCM_PORTING_GUIDE.md`](docs/ROCM_PORTING_GUIDE.md) | [`docs/ROCM_PORTING_GUIDE.zh-CN.md`](docs/ROCM_PORTING_GUIDE.zh-CN.md) | CUDA-to-ROCm/HIP migration record |
| [`docs/TUNING_GUIDE_ROCM.md`](docs/TUNING_GUIDE_ROCM.md) | [`docs/TUNING_GUIDE_ROCM.zh-CN.md`](docs/TUNING_GUIDE_ROCM.zh-CN.md) | ROCm profiling, completed tuning steps, and future targets |
| [`README_UPSTREAM.md`](README_UPSTREAM.md) | - | Original upstream README backup |

## What this repository provides

- CPU-only cuPDLP-C build path.
- Upstream-compatible CUDA build path for NVIDIA baselines.
- ROCm/HIP backend built from migrated CUDA backend code.
- `plc` executable linked against the ROCm/HIP backend.
- CPU-vs-ROCm smoke validation scripts.
- Extended Netlib validation cases.
- Cross-device benchmark workflow and summaries for RTX 3090, RTX 4090D, and Radeon 890M.
- Large MPS benchmark workflow based on H100-hosted cases, inventory files, and SHA256 manifests.
- `rocprofv3` profiling workflow and summary helpers.

## Backend modes

| Mode | CMake options | Role |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | Correctness and portability baseline |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | Upstream-compatible NVIDIA backend and benchmark baseline |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD Radeon ROCm/HIP target backend |

`BUILD_CUDA` and `BUILD_ROCM` must not be enabled at the same time. Use separate build directories such as `build-cpu`, `build-cuda`, and `build-rocm-plc`.

`BUILD_HIP` may still appear as a legacy compatibility alias in older notes, but the public ROCm option is `BUILD_ROCM=ON`.

## Current validation and benchmark status

Smoke validation currently passes:

| Case | Source | ROCm result |
|---|---|---|
| `afiro` | `example/afiro.mps` | PASS |
| `sc50b` | `validation/netlib/sc50b.mps` | PASS |

Extended Netlib validation currently reports:

| Case | Result | Notes |
|---|---|---|
| `afiro` | PASS | Baseline example |
| `adlittle` | PASS | Relative validation metrics pass |
| `blend` | PASS | Relative validation metrics pass |
| `sc50a` | PASS | Relative validation metrics pass |
| `sc50b` | PASS | Smoke + extended case |
| `share2b` | INCOMPLETE | Hits current iteration/time limit; not treated as a ROCm port failure |

Cross-device Netlib benchmark summary:

| Device | CPU result | GPU/ROCm result | Exception |
|---|---:|---:|---|
| RTX 3090 / CUDA | 28/28 OPTIMAL after `greenbea` 200M supplement | 27/28 OPTIMAL | `greenbea` CUDA reached solver internal 3600s limit |
| RTX 4090D / CUDA | 28/28 OPTIMAL | 27/28 OPTIMAL | `greenbea` CUDA hit external 3600s timeout |
| Radeon 890M / ROCm | 28/28 OPTIMAL | 27/28 OPTIMAL | `greenbea` ROCm hit external 3600s timeout |

Large MPS benchmarking is the current next stage. Raw `.mps` files stay outside Git. Only inventory files, SHA256 manifests, curated CSV/Markdown summaries, and documentation should be committed.

## Tested environment

| Component | Version / value |
|---|---|
| OS | Ubuntu 24.04.x |
| ROCm | 7.2.1 |
| HIP compiler | ROCm Clang 22.0.0 |
| GPU/APU | AMD Radeon 890M |
| GPU architecture | `gfx1150` |
| HiGHS | 1.6.0 |
| Build system | CMake + Ninja |

CUDA baselines are run locally on NVIDIA systems such as RTX 3090, RTX 4090D, and H100 using upstream-compatible cuPDLP-C CUDA builds.

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

## CPU baseline build

```bash
cmake -S . -B build-cpu -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=OFF \
  -DBUILD_HIP=OFF \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF

cmake --build build-cpu --target plc -j"$(nproc)"
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

## Benchmarking

Netlib cross-device benchmark uses:

```text
validation/cases_benchmark_200m.txt
nIterLim = 200000000
per-run timeout = 3600s
```

Radeon 890M run:

```bash
CASE_TIMEOUT_SEC=3600 ./scripts/run_benchmark_890m_full.sh
./scripts/summarize_benchmark.py
```

Large MPS workflow is documented in [`docs/LARGE_MPS_BENCHMARK_PLAN.md`](docs/LARGE_MPS_BENCHMARK_PLAN.md).

## Profiling and tuning

```bash
RESULT_ROOT=profiling/results/current ./scripts/profile_rocm_smoke.sh
python3 scripts/summarize_rocm_profile.py \
  --input profiling/results/current \
  --output profiling/results/current/profile_summary.md
```

Initial gfx1150 profiling shows that small-case runtime is dominated by many small operations: HIP launch overhead, memory copies, ROCclr copyBuffer dispatches, rocSPARSE SpMV, rocBLAS vector kernels, and custom PDLP update kernels.

## Adapting to another ROCm GPU

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
```

Then set the proper architecture, for example:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1100
```

for AMD Radeon PRO W7900, depending on ROCm support.

## Naming policy

User-visible ROCm output and documentation should use ROCm/HIP terminology. Historical migration notes and `README_UPSTREAM.md` may keep CUDA terminology. Internal compatibility symbols may remain until the C/HIP boundary is refactored safely.

Do not remove compatibility symbols such as `cuda_csr_Ax`, `cuda_csc_ATy`, or `cuda_alloc_MVbuffer` without updating the C/HIP call boundary and validation scripts.

## Benchmarks

- [Large MPS CUDA/ROCm baseline summary 中文版](docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.zh-CN.md)
- [Large MPS CUDA/ROCm baseline summary English](docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.md)
- [cuPDLPx vs cuPDLP-C short13 comparison 中文版](docs/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.zh-CN.md)
- [cuPDLPx vs cuPDLP-C short13 comparison English](docs/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.md)
