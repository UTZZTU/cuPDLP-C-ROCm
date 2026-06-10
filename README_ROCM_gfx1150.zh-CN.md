# Radeon 890M / gfx1150 的 ROCm/HIP 快速入口

> English: [README_ROCM_gfx1150.md](README_ROCM_gfx1150.md)  
> 主 README: [README.zh-CN.md](README.zh-CN.md)  
> 文档地图: [docs/README.md](docs/README.md)  
> 验证数据索引: [validation/README.zh-CN.md](validation/README.zh-CN.md)  
> Benchmark 索引: [docs/benchmarks/README.md](docs/benchmarks/README.md)

本页是当前已经验证的 ROCm/HIP 目标平台 AMD Radeon 890M / `gfx1150` 的快速入口。

## 环境

| 项目 | 期望值 |
|---|---|
| ROCm 目标 | AMD Radeon 890M |
| GPU 架构 | `gfx1150` |
| ROCm 构建选项 | `BUILD_ROCM=ON` |
| CUDA 构建选项 | `BUILD_CUDA=OFF` |
| HIP 架构选项 | `-DCMAKE_HIP_ARCHITECTURES=gfx1150` |

检查设备可见性：

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
hipcc --version
```

## 构建

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

推荐完整本地检查：

```bash
./scripts/check_rocm_port.sh
ctest --test-dir build-rocm-plc --output-on-failure
```

## 验证数据

validation 目录下的 markdown 汇总和对应 CSV 统一从这里进入：

- [validation/README.zh-CN.md](validation/README.zh-CN.md)
- [validation/rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md](validation/rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md)
- [validation/rocm_prof_tuning_milestones_summary.zh-CN.md](validation/rocm_prof_tuning_milestones_summary.zh-CN.md)
- [validation/rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md](validation/rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md)

## Benchmarks

- Netlib 跨设备 benchmark: [docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md](docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md)
- large MPS baseline: [docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.zh-CN.md](docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.zh-CN.md)
- large MPS 原始汇总 CSV:
  - [results/benchmarks/large_mps_platform_summary_20260610.csv](results/benchmarks/large_mps_platform_summary_20260610.csv)
  - [results/benchmarks/large_mps_per_case_timing_summary_20260610.csv](results/benchmarks/large_mps_per_case_timing_summary_20260610.csv)

## 相关文档

- [docs/ROCM_WORKFLOW.zh-CN.md](docs/ROCM_WORKFLOW.zh-CN.md)
- [docs/VALIDATION.zh-CN.md](docs/VALIDATION.zh-CN.md)
- [docs/BACKEND_MODES_AND_NAMING.zh-CN.md](docs/BACKEND_MODES_AND_NAMING.zh-CN.md)
- [docs/ROCM_PORTING_GUIDE.zh-CN.md](docs/ROCM_PORTING_GUIDE.zh-CN.md)
- [docs/TUNING_GUIDE_ROCM.zh-CN.md](docs/TUNING_GUIDE_ROCM.zh-CN.md)
