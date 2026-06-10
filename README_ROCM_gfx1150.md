# ROCm/HIP quick start for Radeon 890M / gfx1150

> 中文: [README_ROCM_gfx1150.zh-CN.md](README_ROCM_gfx1150.zh-CN.md)  
> Main README: [README.md](README.md)  
> Documentation map: [docs/README.md](docs/README.md)

This page is a focused quick-start for the currently validated ROCm/HIP target: AMD Radeon 890M / `gfx1150`.

## Environment

| Component | Expected value |
|---|---|
| ROCm target | AMD Radeon 890M |
| GPU arch | `gfx1150` |
| Build option | `BUILD_ROCM=ON` |
| CUDA build option | `BUILD_CUDA=OFF` |
| HIP arch option | `-DCMAKE_HIP_ARCHITECTURES=gfx1150` |

Check device visibility:

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
hipcc --version
```

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
