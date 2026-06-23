<!-- COMPETITION_README_20260614_BEGIN -->
> General users: start from this English README or the [Chinese homepage](README.md).
> AMD ROCm/Radeon contest reviewers: see [docs/COMPETITION_README.md](docs/COMPETITION_README.md) / [docs/COMPETITION_README.zh-CN.md](docs/COMPETITION_README.zh-CN.md).
<!-- COMPETITION_README_20260614_END -->

# cuPDLP-C-ROCm

| Entry | Link |
|---|---|
| Chinese homepage | [README.md](README.md) |
| ROCm/gfx1150 quick start | [README_ROCM_gfx1150.md](README_ROCM_gfx1150.md) |
| Documentation map | [docs/README.md](docs/README.md) |
| Validation index | [validation/README.md](validation/README.md) |
| Benchmark index | [docs/benchmarks/README.md](docs/benchmarks/README.md) |

`cuPDLP-C-ROCm` is a ROCm/HIP port and validation fork of upstream cuPDLP-C for AMD GPUs/APUs. The project keeps the CPU path and upstream-compatible CUDA path, and adds a ROCm/HIP backend for AMD Radeon-class hardware.

| Item | Current value |
|---|---|
| Primary ROCm target | AMD Radeon 890M |
| ROCm architecture | `gfx1150` |
| ROCm version used in local validation | 7.2.1 |
| Additional validated ROCm target | AMD Radeon PRO W7900 / `gfx1100` |
| CUDA baseline devices | RTX 3090, RTX 4090D, H100 |

> Status: experimental but buildable. The ROCm/HIP backend has passed smoke validation, Netlib validation, cross-device benchmark checks, and large-MPS baseline testing on AMD Radeon 890M / `gfx1150`. The W7900 / `gfx1100` branch has completed smoke validation, Netlib validation, non-hard large-MPS baseline, P10 targeted profiling, P11 SpMV tuning, P12 rejected-experiment documentation, and P14-A1 quick6 repeated validation. It is still an experimental ROCm solver branch rather than a production-certified solver release, but the current project-stage W7900 evidence chain is closed.

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
| W7900 / `gfx1100` current status | [docs/W7900_CURRENT_STATUS.md](docs/W7900_CURRENT_STATUS.md) | [docs/W7900_CURRENT_STATUS.zh-CN.md](docs/W7900_CURRENT_STATUS.zh-CN.md) |
| W7900 / `gfx1100` first-port record | [docs/W7900_FIRST_PORT.md](docs/W7900_FIRST_PORT.md) | [docs/W7900_FIRST_PORT.zh-CN.md](docs/W7900_FIRST_PORT.zh-CN.md) |
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
- W7900 / `gfx1100` build, smoke validation, Netlib 27-case validation, and large-MPS non-hard23 baseline notes.
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
| Radeon PRO W7900 | ROCm/HIP current post-890M-tuning engineering baseline | 23/23 non-hard large-MPS OPTIMAL; hard3 tracked separately |

cuPDLPx short13 comparison status:

| Solver | Platform | Result |
|---|---|---|
| cuPDLP-C upstream | RTX 4090D CUDA | 13/13 OPTIMAL on selected short/medium cases |
| cuPDLPx v0.2.9 | RTX 4090D CUDA | 13/13 OPTIMAL on the same selected cases |

## Quick start

This section gives the W7900 / `gfx1100` path from cloning the repository to running a minimal smoke example. For the complete environment recovery, data preparation, batch validation, profiling, and result-reproduction workflow, see [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md).

### 1. Clone the project

```bash
git clone -b rocm-w7900-gfx1100 https://github.com/UTZZTU/cuPDLP-C-ROCm.git
cd cuPDLP-C-ROCm
```

If submodules are needed, initialize them with:

```bash
git submodule update --init --recursive
```

### 2. Recover the W7900 ROCm/HIP environment

The W7900 test environment should be treated as a volatile machine. Prefer the repository bootstrap script to recreate the workspace, dependencies, HiGHS installation, build directories, and runtime environment. See the reproducibility guide for prerequisites and optional controls.

```bash
bash scripts/bootstrap_w7900_workspace.sh
```

If the local ROCm SDK or HiGHS installation paths differ from the defaults, follow [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) and adjust `ROCM_PATH`, `HIP_HIPCC_EXECUTABLE`, and `HIGHS_HOME`.

### 3. Build the ROCm/HIP version

W7900 uses the AMD `gfx1100` target. A typical build command is:

```bash
cmake -S . -B build-w7900-rocm -G Ninja \
  -DBUILD_ROCM=ON \
  -DROCM_PATH=/opt/python \
  -DHIP_HIPCC_EXECUTABLE=/opt/python/bin/hipcc \
  -DCMAKE_HIP_ARCHITECTURES=gfx1100 \
  -DHIGHS_HOME=/root/cupdlp_w7900/deps/install/highs-1.6.0

cmake --build build-w7900-rocm -j"$(nproc)"
```

### 4. Run a minimal smoke example

After the build finishes, run `afiro.mps` first to confirm that the ROCm/HIP backend can read an MPS file and complete a small solve.

```bash
find . -iname "afiro.mps" -o -iname "afiro.mps.gz"
find build-w7900-rocm -maxdepth 4 -type f -executable | sort | grep -Ei "cupdlp|pdlp|mps|solver"
```

Run the executable and MPS path found above, for example:

```bash
./build-w7900-rocm/bin/cupdlp ./example/afiro.mps
```

If the repository provides a wrapper script for single-case smoke validation, it can be used instead. For large-MPS data preparation, non-hard23 validation, 8-card independent-MPS throughput, and profiling/tuning reproduction, continue with [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md).

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

## Final W7900 project status / 2026-06-17

The W7900 / `gfx1100` project stage is now complete for the current
repository scope. The branch has progressed beyond first-port and baseline
documentation:

- W7900 ROCm build, smoke validation, Netlib validation, large-MPS baseline,
  targeted profiling, and P11 SpMV tuning have been completed.
- P10 targeted profiling identified rocSPARSE/hipSPARSE CSR SpMV as the main
  GPU kernel hotspot on the selected W7900 cases.
- P11 added an opt-in HIP SpMV algorithm switch and validated three modes:
  `csr_alg2`, `default`, and `csr_alg1`.
- The current W7900 default SpMV algorithm is
  `HIPSPARSE_SPMV_CSR_ALG1`.
- The previous default remains recoverable with
  `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
- This is a W7900-specific current-default tuning choice, not a final
  cross-platform peak-performance claim.

For the authoritative W7900 endpoint, see:

- `docs/W7900_CURRENT_STATUS.md`
- `validation/w7900_p11_spmv_tuning_summary_20260617.md`

## Final W7900 endpoint / 2026-06-17

The W7900 / `gfx1100` project stage is complete for the current repository
scope. It should no longer be described as only a future, baseline-only, or
pre-tuning target.

Current accepted endpoint:

- W7900 build, smoke validation, Netlib validation, and large-MPS baseline
  documentation are complete.
- P10 targeted rocprof profiling is complete.
- P11 SpMV tuning is complete.
- Current W7900 default SpMV algorithm:
  `HIPSPARSE_SPMV_CSR_ALG1`.
- Rollback to the previous default:
  `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
- P12 records a rejected SpMV buffer-algorithm consistency experiment where
  iteration count changed, so that patch was not accepted.

Authoritative endpoints:

- `docs/W7900_CURRENT_STATUS.md`
- `validation/w7900_p11_spmv_tuning_summary_20260617.md`
- `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md`

## Final supplemental validation after P14-A1 / 2026-06-18

W7900 now includes P14-A1 quick6 current-vs-pre_tuning repeated validation.
`current` is faster than `pre_tuning` on `6/6` quick6 cases, with geometric-mean
speedup `1.18889` and median speedup `1.19502`, while preserving iteration counts.

This is quick-set tuning-transfer evidence and should be reported separately from
the non-hard23 large-MPS baseline. No additional W7900 experiment is required for
the current project closure; P14-B remains future optional only.
