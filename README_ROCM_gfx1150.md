# ROCm/HIP quick start for Radeon 890M / gfx1150

<!-- DOCUMENT_STATUS_NOTICE_BEGIN -->
> **Earlier platform milestone**
>
> This page preserves the Radeon 890M / `gfx1150` build and validation path. It is not the current branch homepage. Start from [README.en.md](README.en.md) and [W7900 current status](docs/W7900_CURRENT_STATUS.md) for the current project state.
<!-- DOCUMENT_STATUS_NOTICE_END -->

> 中文: [README_ROCM_gfx1150.zh-CN.md](README_ROCM_gfx1150.zh-CN.md)
> Main README: [README.md](README.md)
> Documentation map: [docs/README.md](docs/README.md)
> Validation index: [validation/README.md](validation/README.md)
> Benchmark index: [docs/benchmarks/README.md](docs/benchmarks/README.md)

This page is a focused quick-start for the currently validated ROCm/HIP target: AMD Radeon 890M / `gfx1150`.

## Environment

| Component | Expected value |
|---|---|
| ROCm target | AMD Radeon 890M |
| GPU arch | `gfx1150` |
| Build option | `BUILD_ROCM=ON` |
| CUDA build option | `BUILD_CUDA=OFF` |
| HIP arch option | `-DCMAKE_HIP_ARCHITECTURES=gfx1150` |

## Build

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

## Smoke validation

```bash
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_sum.json \
  -nIterLim 200
```

Recommended full local check:

```bash
./scripts/check_rocm_port.sh
ctest --test-dir build-rocm-plc --output-on-failure
```

## Validation data

- [validation/README.md](validation/README.md)
- [validation/rocm_current_vs_reduce_27cases_repeats_comparison.md](validation/rocm_current_vs_reduce_27cases_repeats_comparison.md)
- [validation/rocm_prof_tuning_milestones_summary.md](validation/rocm_prof_tuning_milestones_summary.md)
- [validation/rocm_tuning_ablation_6cases_repeats_summary.md](validation/rocm_tuning_ablation_6cases_repeats_summary.md)

## Benchmarks

- Netlib cross-device benchmark: [docs/CROSS_DEVICE_BENCHMARKS.md](docs/CROSS_DEVICE_BENCHMARKS.md)
- Large MPS baseline: [docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.md](docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.md)
- Raw large-MPS CSVs:
  - [results/benchmarks/large_mps_platform_summary_20260610.csv](results/benchmarks/large_mps_platform_summary_20260610.csv)
  - [results/benchmarks/large_mps_per_case_timing_summary_20260610.csv](results/benchmarks/large_mps_per_case_timing_summary_20260610.csv)

## Related docs

- [docs/ROCM_WORKFLOW.md](docs/ROCM_WORKFLOW.md)
- [docs/VALIDATION.md](docs/VALIDATION.md)
- [docs/BACKEND_MODES_AND_NAMING.md](docs/BACKEND_MODES_AND_NAMING.md)
- [docs/ROCM_PORTING_GUIDE.md](docs/ROCM_PORTING_GUIDE.md)
- [docs/TUNING_GUIDE_ROCM.md](docs/TUNING_GUIDE_ROCM.md)
