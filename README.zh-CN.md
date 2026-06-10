# cuPDLP-C-ROCm

> English version: [`README.md`](README.md)

`cuPDLP-C-ROCm` 是基于上游 cuPDLP-C 的 ROCm/HIP 移植、验证和 benchmark 分支，目标是让 cuPDLP-C 在 AMD GPU/APU 上具备可构建、可验证、可分析的 ROCm/HIP 后端。项目保留 CPU 路径和上游兼容 CUDA 路径，同时新增 ROCm/HIP backend。

| 项目 | 当前值 |
|---|---|
| 主要 ROCm 目标 | AMD Radeon 890M |
| ROCm 架构 | `gfx1150` |
| 本地验证使用的 ROCm 版本 | 7.2.1 |
| 正在验证的额外 ROCm 目标 | AMD Radeon PRO W7900 / `gfx1100` |
| CUDA baseline 设备 | RTX 3090、RTX 4090D、H100 |

> 状态：实验性但可构建。ROCm/HIP backend 已经在 AMD Radeon 890M / `gfx1150` 上通过 smoke validation 和跨设备 Netlib benchmark matrix。W7900 / `gfx1100` 分支已通过 first-port CPU-vs-ROCm `afiro` smoke validation，正在进入 extended validation 和 tuning 阶段。它还不是生产级、广泛认证或完全调优的 ROCm 求解器版本。

## 文档

| 英文 | 中文 | 用途 |
|---|---|---|
| [`docs/ROCM_WORKFLOW.md`](docs/ROCM_WORKFLOW.md) | [`docs/ROCM_WORKFLOW.zh-CN.md`](docs/ROCM_WORKFLOW.zh-CN.md) | 日常构建、验证、profiling 和 benchmark 命令 |
| [`docs/VALIDATION.md`](docs/VALIDATION.md) | [`docs/VALIDATION.zh-CN.md`](docs/VALIDATION.zh-CN.md) | CPU-vs-ROCm 验证语义 |
| [`docs/CROSS_DEVICE_BENCHMARKS.md`](docs/CROSS_DEVICE_BENCHMARKS.md) | [`docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md`](docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md) | RTX 3090 / RTX 4090D / Radeon 890M benchmark matrix |
| [`docs/LARGE_MPS_BENCHMARK_PLAN.md`](docs/LARGE_MPS_BENCHMARK_PLAN.md) | [`docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md`](docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md) | H100 来源 large MPS workflow 和跨设备计划 |
| [`docs/ROCM_PORTING_GUIDE.md`](docs/ROCM_PORTING_GUIDE.md) | [`docs/ROCM_PORTING_GUIDE.zh-CN.md`](docs/ROCM_PORTING_GUIDE.zh-CN.md) | CUDA 到 ROCm/HIP 迁移记录 |
| [`docs/TUNING_GUIDE_ROCM.md`](docs/TUNING_GUIDE_ROCM.md) | [`docs/TUNING_GUIDE_ROCM.zh-CN.md`](docs/TUNING_GUIDE_ROCM.zh-CN.md) | ROCm profiling、已完成调优和后续目标 |
| [`docs/W7900_FIRST_PORT.md`](docs/W7900_FIRST_PORT.md) | [`docs/W7900_FIRST_PORT.zh-CN.md`](docs/W7900_FIRST_PORT.zh-CN.md) | W7900 / `gfx1100` first-port 构建和 smoke validation 记录 |
| [`README_UPSTREAM.md`](README_UPSTREAM.md) | - | 上游原始 README 备份 |

## 本仓库提供什么

- CPU-only cuPDLP-C 构建路径。
- 上游兼容 CUDA 构建路径，用于 NVIDIA baseline。
- 从 CUDA backend 迁移而来的 ROCm/HIP backend。
- 链接 ROCm/HIP backend 的 `plc` 可执行文件。
- CPU-vs-ROCm smoke validation 脚本。
- 扩展 Netlib validation case。
- RTX 3090、RTX 4090D、Radeon 890M 的跨设备 benchmark workflow 和结果摘要。
- W7900 / `gfx1100` first-port 构建脚本和 smoke validation 记录。
- 基于 H100 来源 case、inventory 和 SHA256 manifest 的 large MPS benchmark workflow。
- `rocprofv3` profiling workflow 和摘要脚本。

## 后端模式

| 模式 | CMake 选项 | 作用 |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | 正确性和可移植性 baseline |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | 上游兼容 NVIDIA backend 和 benchmark baseline |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD Radeon ROCm/HIP 目标 backend |

`BUILD_CUDA` 和 `BUILD_ROCM` 不能同时启用。不同后端模式应使用独立构建目录，例如 `build-cpu`、`build-cuda` 和 `build-rocm-plc`。

`BUILD_HIP` 可能仍在旧笔记中作为兼容别名出现，但 ROCm 后端的公开选项是 `BUILD_ROCM=ON`。

## 当前验证和 benchmark 状态

当前 smoke validation 通过：

| Case | 来源 | ROCm 结果 |
|---|---|---|
| `afiro` | `example/afiro.mps` | PASS |
| `sc50b` | `validation/netlib/sc50b.mps` | PASS |

当前扩展 Netlib validation 结果：

| Case | 结果 | 说明 |
|---|---|---|
| `afiro` | PASS | 基线示例 |
| `adlittle` | PASS | 相对验证指标通过 |
| `blend` | PASS | 相对验证指标通过 |
| `sc50a` | PASS | 相对验证指标通过 |
| `sc50b` | PASS | Smoke + extended case |
| `share2b` | INCOMPLETE | 达到当前迭代或时间限制，不视为 ROCm port failure |

跨设备 Netlib benchmark 摘要：

| 设备 | CPU 结果 | GPU/ROCm 结果 | 例外 |
|---|---:|---:|---|
| RTX 3090 / CUDA | `greenbea` 200M 补跑后 28/28 OPTIMAL | 27/28 OPTIMAL | `greenbea` CUDA 达到 solver 内部 3600s 限制 |
| RTX 4090D / CUDA | 28/28 OPTIMAL | 27/28 OPTIMAL | `greenbea` CUDA 命中外部 3600s timeout |
| Radeon 890M / ROCm | 28/28 OPTIMAL | 27/28 OPTIMAL | `greenbea` ROCm 命中外部 3600s timeout |

Large MPS benchmark 是当前下一阶段。原始 `.mps` 文件不进入 Git，只提交 inventory、SHA256 manifest、整理后的 CSV/Markdown 摘要和文档。

## 已测试环境

| 组件 | 版本 / 值 |
|---|---|
| OS | Ubuntu 24.04.x |
| ROCm | 7.2.1 |
| HIP compiler | ROCm Clang 22.0.0 |
| GPU/APU | AMD Radeon 890M |
| GPU 架构 | `gfx1150` |
| HiGHS | 1.6.0 |
| 构建系统 | CMake + Ninja |

CUDA baseline 在 RTX 3090、RTX 4090D、H100 等 NVIDIA 系统上使用上游兼容 cuPDLP-C CUDA 构建本地运行。

## 快速开始：ROCm/HIP 构建

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

运行 smoke 示例：

```bash
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_sum.json \
  -nIterLim 200
```

## CPU baseline 构建

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

## Benchmark

Netlib 跨设备 benchmark 使用：

```text
validation/cases_benchmark_200m.txt
nIterLim = 200000000
per-run timeout = 3600s
```

Radeon 890M 运行：

```bash
CASE_TIMEOUT_SEC=3600 ./scripts/run_benchmark_890m_full.sh
./scripts/summarize_benchmark.py
```

Large MPS workflow 见 [`docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md`](docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md)。

## Profiling 和 tuning

```bash
RESULT_ROOT=profiling/results/current ./scripts/profile_rocm_smoke.sh
python3 scripts/summarize_rocm_profile.py \
  --input profiling/results/current \
  --output profiling/results/current/profile_summary.md
```

初始 gfx1150 profiling 显示，小 case runtime 由大量小操作主导：HIP launch overhead、memory copy、ROCclr copyBuffer dispatch、rocSPARSE SpMV、rocBLAS vector kernel 和 custom PDLP update kernel。

## 适配其他 ROCm GPU

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
```

然后设置对应架构，例如 AMD Radeon PRO W7900 可使用：

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1100
```

实际可用性取决于 ROCm 支持状态。

## 命名策略

用户可见 ROCm 输出和文档应使用 ROCm/HIP 术语。历史迁移笔记和 `README_UPSTREAM.md` 可以保留 CUDA 术语。内部兼容符号可保留到 C/HIP 边界安全重构完成之后。

不要在没有同步修改 C/HIP 调用边界和验证脚本的情况下删除 `cuda_csr_Ax`、`cuda_csc_ATy`、`cuda_alloc_MVbuffer` 等兼容符号。
