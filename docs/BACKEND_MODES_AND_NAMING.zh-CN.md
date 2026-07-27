# 后端模式与命名策略

> English: [BACKEND_MODES_AND_NAMING.md](BACKEND_MODES_AND_NAMING.md)

本仓库维护三种后端模式，并按项目策略要求它们**互斥启用**：

| 模式 | CMake 选项 | 作用 |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | 正确性与可移植性基线 |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | 上游兼容的 NVIDIA 参考后端 |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD GPU 后端；当前主要平台是 W7900 / `gfx1100` |

Radeon 890M / `gfx1150` 是早期 ROCm 迁移与调优里程碑；Radeon PRO W7900 / `gfx1100` 是当前分支重点。

## 构建模式合同

每次只启用一种模式，并为不同后端使用独立构建目录：

```text
build-cpu
build-cuda
build-rocm-w7900
```

不要跨后端复用 CMake cache。

当前顶层 CMake 尚未对 `BUILD_CUDA=ON` 与 `BUILD_ROCM=ON` 的无效组合提供专门的 fatal guard，因此文档和自动化必须显式传入两个开关。以后可通过代码修改增加 CMake 级保护，但这不属于本次纯文档重构。

`BUILD_HIP` 不是受支持的公开选项，应使用 `BUILD_ROCM=ON`。

## 为什么保留 CUDA

CUDA 路径被有意保留，因为它：

- 让代码保持接近上游 cuPDLP-C；
- 提供 NVIDIA 参考性能；
- 帮助区分 ROCm 特有问题与通用 GPU 后端问题；
- 支撑可控的 CUDA-to-ROCm 迁移案例；
- 为收敛敏感 case 保留比较路径。

保留 CUDA 不代表当前分支以 CUDA 为主。当前重点仍是 W7900 上的 ROCm/HIP 路径。

## 源码布局

```text
cupdlp/cuda/                    上游兼容 CUDA 后端
cupdlp/hip/                     ROCm/HIP 后端
cupdlp/                         共享求解器代码
cupdlp/cupdlp_backend_compat.h  后端兼容别名
interface/                      命令行求解器入口
```

共享 C 代码应尽量通过兼容别名调用后端能力，而不是直接调用某个后端的 runtime API。

示例：

| 共享别名 | CUDA | ROCm/HIP |
|---|---|---|
| `CUPDLP_BLAS_DAXPY` | `cublasDaxpy` | `hipblasDaxpy` |
| `CUPDLP_SPARSE_CREATE_CSR` | `cusparseCreateCsr` | `hipsparseCreateCsr` |
| `CUPDLP_DEVICE_FREE` | `cudaFree` | `hipFree` |
| `CUPDLP_DEVICE_RESET` | `cudaDeviceReset` | `hipDeviceReset` |

## 命名策略

### 保留真实后端名称

以下位置保留 CUDA 名称是正确的：

```text
cupdlp/cuda/
README_UPSTREAM.md
CUDA benchmark 记录
历史迁移文档
```

以下位置应使用 ROCm/HIP 名称：

```text
cupdlp/hip/
ROCm 构建与验证输出
W7900 profiling 与 tuning 文档
```

### 共享接口优先使用后端中立名称

共享的用户可见输出应优先使用：

```text
device
GPU
sparse backend
BLAS backend
device preparation
```

不要让 CUDA 专有名称看起来像是在描述 ROCm 后端。

### 兼容符号只能经过验证后重构

部分共享内部符号仍包含 `cuda_`，例如：

```text
cuda_csr_Ax
cuda_csc_ATy
cuda_alloc_MVbuffer
```

不要机械重命名。安全替换需要新符号或 wrapper，并完成 CPU、CUDA、ROCm 验证。

## 推荐构建命令

CPU：

```bash
cmake -S . -B build-cpu -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=OFF \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF

cmake --build build-cpu --target plc -j"$(nproc)"
```

CUDA：

```bash
cmake -S . -B build-cuda -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=ON \
  -DBUILD_ROCM=OFF \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DCMAKE_PREFIX_PATH="$HIGHS_HOME"

cmake --build build-cuda --target plc -j"$(nproc)"
```

W7900 ROCm/HIP：

```bash
cmake -S . -B build-rocm-w7900 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DBUILD_TESTING=ON \
  -DCMAKE_HIP_ARCHITECTURES=gfx1100 \
  -DCMAKE_PREFIX_PATH="$CMAKE_PREFIX_PATH"

cmake --build build-rocm-w7900 --target plc -j"$(nproc)"
```

在仓库记录的 W7900 环境中，ROCm SDK 与 HiGHS 路径依赖机器配置，因此优先使用维护脚本：

```bash
bash scripts/build_w7900_cpu.sh
bash scripts/build_w7900_rocm.sh
bash scripts/run_w7900_smoke.sh
```

## 后端相关修改的最低验证

| 修改范围 | 最低检查 |
|---|---|
| 共享 CPU 代码 | CPU build 与 `afiro` |
| CUDA 后端或兼容别名 | CUDA build 与 smoke cases |
| ROCm/HIP 后端 | W7900 build 与 smoke |
| 算法相关 GPU 代码 | Extended Netlib 与代表性 large-MPS |
| 性能敏感代码 | 正确性验证、重复计时与 profiling |
| 只改命名或文档 | Markdown/link 检查与 `git diff --check` |

当前主要验证的可执行文件是 `plc`。可选 Python/apps 路径不属于当前 ROCm 验证合同。

## 相关文档

- [ROCm 工作流](ROCM_WORKFLOW.zh-CN.md)
- [ROCm porting 指南](ROCM_PORTING_GUIDE.zh-CN.md)
- [验证语义](VALIDATION.zh-CN.md)
- [W7900 当前状态](W7900_CURRENT_STATUS.zh-CN.md)
