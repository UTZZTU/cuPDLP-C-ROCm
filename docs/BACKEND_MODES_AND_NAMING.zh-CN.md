# 后端模式与命名策略

> English: [BACKEND_MODES_AND_NAMING.md](BACKEND_MODES_AND_NAMING.md)  
> 文档地图: [README.md](README.md)

本仓库保留三种互斥的构建模式：

| 模式 | CMake 选项 | 作用 |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | 正确性与可移植性 baseline |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | 上游兼容 NVIDIA 后端与 benchmark baseline |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD Radeon 890M / `gfx1150` 目标后端 |

`BUILD_CUDA` 与 `BUILD_ROCM` 不能同时开启。

`BUILD_HIP` 不再作为公开构建选项使用。ROCm/HIP 后端统一使用：

```bash
-DBUILD_ROCM=ON
```

## 为什么仍然保留 CUDA

本项目是上游 cuPDLP-C 的 ROCm/HIP 移植分支，但 CUDA backend 被有意保留。

保留 CUDA 的原因包括：

- 让仓库与上游实现保持接近；
- 为跨设备 benchmark 提供 NVIDIA baseline；
- 帮助区分 ROCm 特有问题和一般 GPU backend 行为；
- 为 CUDA-to-ROCm 迁移文档提供上下文。

例如，`greenbea` case 在 CUDA 和 ROCm 路径上都表现出 GPU-backend 收敛敏感性。保留 CUDA backend 能让这种解释更清楚。

## 后端源码布局

重要后端相关路径：

```text
cupdlp/cuda/      从上游 cuPDLP-C 继承的 CUDA backend 源码
cupdlp/hip/       ROCm/HIP backend 源码
cupdlp/           CPU/GPU 共享 solver 代码
interface/        solver 可执行入口
```

共享 C 源码不应该直接调用 CUDA-only 或 HIP-only runtime/library API。共享代码应使用：

```text
cupdlp/cupdlp_backend_compat.h
```

该文件会根据当前构建模式，将共享后端操作映射到 CUDA 或 ROCm/HIP 实现。

示例：

| 共享别名 | CUDA 模式 | ROCm/HIP 模式 |
|---|---|---|
| `CUPDLP_BLAS_DAXPY` | `cublasDaxpy` | `hipblasDaxpy` |
| `CUPDLP_SPARSE_CREATE_CSR` | `cusparseCreateCsr` | `hipsparseCreateCsr` |
| `CUPDLP_DEVICE_FREE` | `cudaFree` | `hipFree` |
| `CUPDLP_DEVICE_RESET` | `cudaDeviceReset` | `hipDeviceReset` |

## 命名策略

本仓库使用如下命名策略：

- 用户可见的 ROCm 输出、README、benchmark 文档应使用 ROCm/HIP 术语；
- 历史迁移记录和 `README_UPSTREAM.md` 可以保留 CUDA 术语；
- 内部兼容符号可以暂时保留 CUDA 风格名称，直到 C/HIP 边界安全重构完成；
- 不要只为了“名字干净”删除兼容符号，例如 `cuda_csr_Ax`、`cuda_csc_ATy`、`cuda_alloc_MVbuffer`。删除前必须同步更新 C/HIP 调用边界和验证脚本。

## 相关文档

- [ROCm workflow guide](ROCM_WORKFLOW.md) / [中文](ROCM_WORKFLOW.zh-CN.md)
- [ROCm porting guide](ROCM_PORTING_GUIDE.md) / [中文](ROCM_PORTING_GUIDE.zh-CN.md)
- [CUDA to ROCm migration case study](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) / [中文](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md)
