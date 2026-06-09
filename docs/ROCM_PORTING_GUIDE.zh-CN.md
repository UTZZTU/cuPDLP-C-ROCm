# 将 cuPDLP-C 从 CUDA 移植到 ROCm/HIP

> English version: [`ROCM_PORTING_GUIDE.md`](ROCM_PORTING_GUIDE.md)

本文记录本仓库如何从原始 CUDA-based cuPDLP-C 项目迁移到面向 AMD Radeon 890M / `gfx1150` 的 ROCm/HIP 构建。

它有两个目的：

1. 记录本仓库使用的迁移路径。
2. 为类似 GPU solver 项目提供可复用 CUDA-to-HIP checklist。

## 1. 项目背景

原始 cuPDLP-C 项目包含用于 GPU 加速线性规划的 CUDA backend。本 port 保留 CPU 路径和上游兼容 CUDA 路径，同时为 AMD 硬件新增 ROCm/HIP backend。

当前已验证 ROCm 目标：

| 项目 | 值 |
|---|---|
| GPU/APU | AMD Radeon 890M |
| 架构 | `gfx1150` |
| OS | Ubuntu 24.04.x |
| ROCm | 7.2.1 |
| HIP compiler | ROCm Clang 22.0.0 |
| HiGHS | 1.6.0 |

## 2. 迁移策略

迁移采用分阶段方式，而不是全局搜索替换。

主要 workflow：

1. 保留上游 CUDA 代码作为参考。
2. 验证 ROCm 能识别并运行目标设备。
3. 先构建并运行 CPU baseline。
4. 只用 `hipify-clang` 转换 CUDA backend 源文件。
5. 创建独立 `cupdlp/hip/` backend 目录。
6. 手动适配 header、CMake 和 host-side C/C++ 代码。
7. 在 ROCm 路径中替换 CUDA runtime、cuBLAS 和 cuSPARSE 调用。
8. 先将 HIP backend 构建成独立 library。
9. 将 HIP backend 链接进完整 `plc` 可执行文件。
10. 与 CPU 输出做验证。
11. 添加 hygiene checks 和 CTest smoke validation。
12. 在性能调优前添加 profiling。
13. 增加与 CUDA baseline 的跨设备 benchmark 对比。

这种分阶段方法让每一种失败模式更容易隔离。

## 3. ROCm 环境验证

移植代码前先验证目标 GPU：

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm-smi
/opt/rocm/bin/hipcc --version
```

在改 solver 前应先编译并运行最小 HIP smoke test：

```bash
hipcc --offload-arch=gfx1150 hip_smoke.cpp -o hip_smoke
./hip_smoke
```

## 4. 先建立 CPU baseline

修改 GPU 代码前先构建 CPU baseline：

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

示例运行：

```bash
./build-cpu/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_cpu_sum.json \
  -nIterLim 200
```

CPU 输出是后续 ROCm validation 的数值参考。

## 5. HIPIFY 范围

只对原始 CUDA backend 文件执行 HIPIFY：

```text
cupdlp/cuda/cupdlp_cuda_kernels.cu
cupdlp/cuda/cupdlp_cudalinalg.cu
cupdlp/cuda/cupdlp_cuda_kernels.cuh
cupdlp/cuda/cupdlp_cudalinalg.cuh
```

它们迁移到：

```text
cupdlp/hip/cupdlp_hip_kernels.cpp
cupdlp/hip/cupdlp_hip_linalg.cpp
cupdlp/hip/cupdlp_hip_kernels.h
cupdlp/hip/cupdlp_hip_linalg.h
```

不要盲目 HIPIFY 全仓库。Host-side C/C++ 集成需要人工审查。

## 6. HIPIFY 后的手动修复

常见手动修复包括：

- 调整 ROCm/HIP include path；
- 在需要时为 HIP shuffle 调用使用 64-bit mask；
- 将 CUDA runtime 调用替换为 HIP runtime 调用；
- 将 cuBLAS 调用替换为 hipBLAS；
- 将 cuSPARSE 调用替换为 hipSPARSE；
- 适配不支持的 helper API；
- 添加 `CHECK_HIP` 和 `CHECK_HIP_STRICT` 类宏；
- 在 C/HIP 边界安全重构前保留内部兼容符号。

示例：

```text
cudaMalloc      -> hipMalloc
cudaFree        -> hipFree
cudaMemcpy      -> hipMemcpy
cudaDeviceReset -> hipDeviceReset
cublas*         -> hipblas*
cusparse*       -> hipsparse*
CUDA_R_32F      -> HIP_R_32F
CUDA_R_64F      -> HIP_R_64F
```

## 7. CMake 集成

公开 ROCm 构建选项是：

```bash
-DBUILD_ROCM=ON
```

顶层 CMake 必须拒绝 CUDA 和 ROCm 同时启用。

ROCm/HIP 构建中，CMake 启用 HIP 并查找 ROCm 包，例如：

```cmake
enable_language(HIP)
find_package(hip REQUIRED CONFIG)
find_package(hipblas REQUIRED CONFIG)
find_package(hipsparse REQUIRED CONFIG)
```

HIP 架构通过以下参数设置：

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

## 8. Host-side 代码适配

多个 C host 文件需要人工适配，因为它们分配 GPU memory、创建 handle 或调用 BLAS/SPARSE routine。

重要区域：

```text
cupdlp/cupdlp_defs.h
cupdlp/cupdlp_linalg.c
cupdlp/cupdlp_utils.c
interface/mps_highs.c
interface/CMakeLists.txt
```

小型 backend compatibility layer 会将 CUDA 和 HIP descriptor/handle type 映射到项目级 alias，尽量避免主 solver 代码直接依赖 CUDA 或 HIP type。

## 9. 构建 ROCm/HIP port

`gfx1150`：

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

生成的可执行文件是：

```text
build-rocm-plc/bin/plc
```

## 10. 用 smoke 示例验证

```bash
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_sum.json \
  -nIterLim 200
```

成功运行应报告 `terminationCode = OPTIMAL`、`primalCode = FEASIBLE` 和 `dualCode = FEASIBLE`。

## 11. 适配其他 AMD GPU

识别架构：

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
```

然后把：

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

替换成目标架构，例如 Radeon PRO W7900 在支持条件满足时使用：

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1100
```

## 12. 迁移辅助脚本

机械迁移 helper 存放在：

```text
tools/migration/
```

它们记录机械编辑过程，不是普通用户构建项目所必需的。

## 13. 命名策略

用户可见文档和输出应优先使用 ROCm/HIP 术语。历史迁移笔记和上游备份可以保留 CUDA 术语。内部兼容符号可以保留到 C/HIP 边界安全重构完成后。

不要在没有专门兼容性 pass 和 validation run 的情况下删除 `cuda_csr_Ax`、`cuda_csc_ATy` 或 `cuda_alloc_MVbuffer`。

## 14. 当前限制

- ROCm/HIP backend 仍是实验性。
- `gfx1150` 是当前已验证 AMD 目标。
- `gfx1100` / W7900 需要单独 validation pass。
- 部分内部 CUDA-style 名称因兼容性仍保留。
- Broad large MPS validation 正在进行中。
- 尚无 ROCm CI。

## 15. 推荐下一步

1. 保持用户可见 CUDA wording 清理，同时保留必要兼容符号。
2. 完成 large MPS benchmark matrix。
3. 记录 Radeon 890M pre-tuning 和 tuned ROCm 结果。
4. 添加 W7900 / `gfx1100` 构建和验证说明。
5. 将 profiling 从 smoke case 扩展到更大 LP 实例。
