# cuPDLP-C-ROCm

> English homepage: [README.md](README.md)  
> ROCm/gfx1150 快速入口: [README_ROCM_gfx1150.zh-CN.md](README_ROCM_gfx1150.zh-CN.md)  
> 文档地图: [docs/README.md](docs/README.md)  
> 验证数据索引: [validation/README.zh-CN.md](validation/README.zh-CN.md)  
> Benchmark 索引: [docs/benchmarks/README.md](docs/benchmarks/README.md)

`cuPDLP-C-ROCm` 是基于上游 cuPDLP-C 的 ROCm/HIP 移植与验证分支。项目保留 CPU 路径和上游兼容 CUDA 路径，并新增面向 AMD Radeon 平台的 ROCm/HIP 后端。

| 项目 | 当前值 |
|---|---|
| 主要 ROCm 目标 | AMD Radeon 890M |
| ROCm 架构 | `gfx1150` |
| 本地验证 ROCm 版本 | 7.2.1 |
| 正在验证的额外 ROCm 目标 | AMD Radeon PRO W7900 / `gfx1100` |
| CUDA baseline 设备 | RTX 3090, RTX 4090D, H100 |

> 状态：实验性但可构建。当前 ROCm/HIP 后端已经通过 smoke validation、Netlib 验证、跨设备 benchmark，以及 Radeon 890M / `gfx1150` 上的大规模 MPS baseline 测试。W7900 / `gfx1100` 分支已通过 first-port CPU-vs-ROCm `afiro` smoke validation，正在进入 extended validation 和 tuning 阶段。它还不是生产级、完全调优、广泛认证的 ROCm solver release。

## 从哪里开始

| 需求 | English | 中文 |
|---|---|---|
| ROCm/gfx1150 快速入口 | [README_ROCM_gfx1150.md](README_ROCM_gfx1150.md) | [README_ROCM_gfx1150.zh-CN.md](README_ROCM_gfx1150.zh-CN.md) |
| 完整文档地图 | [docs/README.md](docs/README.md) | [docs/README.md](docs/README.md) |
| 验证数据索引 | [validation/README.md](validation/README.md) | [validation/README.zh-CN.md](validation/README.zh-CN.md) |
| Benchmark 索引 | [docs/benchmarks/README.md](docs/benchmarks/README.md) | [docs/benchmarks/README.md](docs/benchmarks/README.md) |

## 文档

| 需求 | English | 中文 |
|---|---|---|
| 构建、运行、验证日常流程 | [docs/ROCM_WORKFLOW.md](docs/ROCM_WORKFLOW.md) | [docs/ROCM_WORKFLOW.zh-CN.md](docs/ROCM_WORKFLOW.zh-CN.md) |
| CPU vs ROCm 验证语义 | [docs/VALIDATION.md](docs/VALIDATION.md) | [docs/VALIDATION.zh-CN.md](docs/VALIDATION.zh-CN.md) |
| 后端模式与命名策略 | [docs/BACKEND_MODES_AND_NAMING.md](docs/BACKEND_MODES_AND_NAMING.md) | [docs/BACKEND_MODES_AND_NAMING.zh-CN.md](docs/BACKEND_MODES_AND_NAMING.zh-CN.md) |
| CUDA 到 ROCm 迁移案例 | [docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md](docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) | [docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md](docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) |
| ROCm porting 指南 | [docs/ROCM_PORTING_GUIDE.md](docs/ROCM_PORTING_GUIDE.md) | [docs/ROCM_PORTING_GUIDE.zh-CN.md](docs/ROCM_PORTING_GUIDE.zh-CN.md) |
| ROCm profiling 记录 | [docs/ROCM_PROFILING_NOTES.md](docs/ROCM_PROFILING_NOTES.md) | [docs/ROCM_PROFILING_NOTES.zh-CN.md](docs/ROCM_PROFILING_NOTES.zh-CN.md) |
| ROCm tuning 历史 | [docs/ROCM_TUNING_HISTORY.md](docs/ROCM_TUNING_HISTORY.md) | [docs/ROCM_TUNING_HISTORY.zh-CN.md](docs/ROCM_TUNING_HISTORY.zh-CN.md) |
| ROCm tuning 指南 | [docs/TUNING_GUIDE_ROCM.md](docs/TUNING_GUIDE_ROCM.md) | [docs/TUNING_GUIDE_ROCM.zh-CN.md](docs/TUNING_GUIDE_ROCM.zh-CN.md) |
| Netlib 跨设备 benchmark | [docs/CROSS_DEVICE_BENCHMARKS.md](docs/CROSS_DEVICE_BENCHMARKS.md) | [docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md](docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md) |
| large MPS benchmark 计划 | [docs/LARGE_MPS_BENCHMARK_PLAN.md](docs/LARGE_MPS_BENCHMARK_PLAN.md) | [docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md](docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md) |
| greenbea 数值行为 | [docs/NUMERICAL_BEHAVIOR_GREENBEA.md](docs/NUMERICAL_BEHAVIOR_GREENBEA.md) | [docs/NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md](docs/NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md) |
| W7900 / `gfx1100` first-port 记录 | [docs/W7900_FIRST_PORT.md](docs/W7900_FIRST_PORT.md) | [docs/W7900_FIRST_PORT.zh-CN.md](docs/W7900_FIRST_PORT.zh-CN.md) |
| 上游参考快照 | [README_UPSTREAM.md](README_UPSTREAM.md) | — |

`README_UPSTREAM.md` 是上游 README 备份，故意作为原始参考快照保留，不翻译、不重写。

## Benchmarks

原始 `.mps` 大文件不提交到 Git。仓库只提交整理后的 CSV 结果和解释文档。

| 主题 | English | 中文 | 原始结果 CSV |
|---|---|---|---|
| Large MPS CUDA/ROCm baseline | [summary](docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.md) | [中文版](docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.zh-CN.md) | [platform summary](results/benchmarks/large_mps_platform_summary_20260610.csv), [per-case timing](results/benchmarks/large_mps_per_case_timing_summary_20260610.csv) |
| cuPDLPx vs cuPDLP-C short13 | [comparison](docs/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.md) | [中文版](docs/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.zh-CN.md) | [comparison CSV](results/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.csv) |

## 本仓库提供什么

- CPU-only cuPDLP-C 构建路径。
- 上游兼容 CUDA 构建路径，用于 NVIDIA baseline。
- 由 CUDA backend 迁移而来的 ROCm/HIP backend。
- 链接 ROCm/HIP backend 的 `plc` 可执行文件。
- CPU-vs-ROCm smoke validation 脚本。
- W7900 / `gfx1100` first-port 构建脚本和 smoke validation 记录。
- 扩展 Netlib 验证 case。
- RTX 3090、RTX 4090D、H100、Radeon 890M 的跨设备 benchmark 工作流与结果文档。
- large MPS benchmark 文档和整理后的 CSV 汇总。
- `rocprofv3` profiling 工作流与 ROCm tuning 笔记。
- 面向 CUDA 到 ROCm/HIP 科学计算项目迁移的案例文档。

## 后端模式

| 模式 | CMake 选项 | 作用 |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | 正确性与可移植性 baseline |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | 上游兼容 NVIDIA 后端与 benchmark baseline |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD Radeon ROCm/HIP 目标后端 |

`BUILD_CUDA` 和 `BUILD_ROCM` 不能同时开启。不同后端建议使用不同 build 目录，例如 `build-cpu`、`build-cuda`、`build-rocm-plc`。

## 当前验证与 benchmark 状态

Large MPS baseline 状态：

| 平台 | 后端 | 结果 |
|---|---|---|
| RTX 3090 | CUDA upstream | 25/26 OPTIMAL, 1/26 TIMELIMIT |
| Radeon 890M | ROCm/HIP baseline | 24/26 OPTIMAL, 2/26 TIMELIMIT |
| RTX 4090D | CUDA upstream | 26/26 OPTIMAL |
| H100 | CUDA upstream | 26/26 OPTIMAL |

cuPDLPx short13 对比状态：

| Solver | 平台 | 结果 |
|---|---|---|
| cuPDLP-C upstream | RTX 4090D CUDA | 选定 13 个短/中等 case 上 13/13 OPTIMAL |
| cuPDLPx v0.2.9 | RTX 4090D CUDA | 同一批 case 上 13/13 OPTIMAL |

## 快速开始：构建 ROCm/HIP 版本

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

运行 smoke example：

```bash
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_sum.json \
  -nIterLim 200
```

## 验证

```bash
./scripts/check_rocm_port.sh
ctest --test-dir build-rocm-plc --output-on-failure
```

扩展验证：

```bash
RESULT_ROOT=validation/results/extended_netlib \
  ./scripts/run_validation.sh validation/cases_extended_netlib.txt
```

整理后的验证结果和 CSV 见 [validation/README.zh-CN.md](validation/README.zh-CN.md)。

## Profiling 与 tuning

```bash
RESULT_ROOT=profiling/results/current ./scripts/profile_rocm_smoke.sh

python3 scripts/summarize_rocm_profile.py \
  --input profiling/results/current \
  --output profiling/results/current/profile_summary.md
```

详见 [docs/ROCM_PROFILING_NOTES.zh-CN.md](docs/ROCM_PROFILING_NOTES.zh-CN.md)、[docs/ROCM_TUNING_HISTORY.zh-CN.md](docs/ROCM_TUNING_HISTORY.zh-CN.md)、[docs/TUNING_GUIDE_ROCM.zh-CN.md](docs/TUNING_GUIDE_ROCM.zh-CN.md)。

## 适配其他 ROCm GPU

先识别 GPU 架构：

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
```

然后设置对应架构，例如 W7900/gfx1100：

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1100
```

实际支持取决于 ROCm 版本、Linux 发行版、内核和 AMD GPU/APU 支持状态。
