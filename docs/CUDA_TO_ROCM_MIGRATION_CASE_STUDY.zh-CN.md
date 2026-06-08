# CUDA 到 ROCm/HIP 迁移案例研究

本文总结本仓库将上游 `cuPDLP-C` 改造为 CPU / CUDA / ROCm-HIP 三模态项目的实际迁移路径。

这篇文档的目的不是只说明“改了哪些 API”，而是帮助后续贡献者理解：为什么要这样迁移、为什么不能简单删除 CUDA、为什么需要验证矩阵、为什么需要性能消融和数值行为文档。

## 项目背景

上游 `cuPDLP-C` 是 CUDA-oriented 的 GPU 一阶线性规划求解器实现。本 fork 的目标是在保留上游 CPU/CUDA 能力的同时，增加 AMD Radeon / ROCm-HIP 后端。

最终项目不是一个“删掉 CUDA 的 ROCm fork”，而是一个三后端工程分支：

- CPU：正确性与可移植性基线；
- CUDA：上游兼容的 NVIDIA GPU 后端；
- ROCm/HIP：AMD Radeon / ROCm 目标后端。

## 为什么不删除 CUDA？

迁移初期很容易产生一个想法：既然目标是 ROCm/HIP，那么是不是可以删除 CUDA，只保留 CPU + ROCm？

这个项目后来的结论是：**不应该删除 CUDA**。

CUDA 仍然有价值，因为：

1. 它是上游原始 GPU 后端；
2. 它能提供 NVIDIA 设备上的性能与数值行为基线；
3. 它能帮助区分“ROCm 移植问题”和“一般 GPU 后端数值行为差异”；
4. 它让本 fork 更容易和上游 `cuPDLP-C` 对照；
5. 它能帮助后续读者理解哪些逻辑来自原 CUDA 路径，哪些逻辑是 ROCm/HIP 新增路径。

当前策略是：

| 后端 | 是否保留 | 原因 |
|---|---|---|
| CPU | 保留 | 正确性、可移植性和无 GPU baseline |
| CUDA | 保留 | 上游兼容路径和 NVIDIA 对照基线 |
| ROCm/HIP | 保留 | AMD Radeon / ROCm 目标后端 |

## 总体迁移策略

本项目采用分阶段迁移，而不是一次性重写：

1. 先确保 CPU baseline 可用；
2. 增加最小 ROCm/HIP 后端；
3. 先跑通最小样例 `afiro.mps`；
4. 建立 build / validation / benchmark 脚本；
5. 扩展 Netlib/MPS 验证覆盖；
6. 恢复 CUDA backend 兼容性；
7. 明确 CPU / CUDA / ROCm 三模态命名规则；
8. 建立跨设备 benchmark；
9. 补充 ROCm tuning ablation 证据；
10. 对 `greenbea` 等收敛敏感 case 单独写数值行为文档。

这个过程比“直接 hipify 然后调性能”更稳。

## 外部迁移经验与本项目对应关系

AMD HIP 官方文档说明，HIPIFY 可以自动把部分 CUDA 代码转换为 HIP 代码，例如将 CUDA API 转换为 HIP API；但复杂项目通常仍然需要手动处理构建系统、平台差异、库映射、unsupported functions 和后端特化逻辑。

ROCm 文档也说明，ROCm 组件通常提供 CMake config packages，Linux 下常见做法是通过 `-D CMAKE_PREFIX_PATH=/opt/rocm` 让 CMake 找到 ROCm 包。

CUDA 侧，现代 CMake 已经支持把 CUDA 作为 first-class language，因此保留 CUDA 后端不仅是保留 `.cu` 文件，还需要确保 CMake 能够正确启用 CUDA 编译、链接 CUDA 库并构建 CUDA target。

本项目的经验与这些公开建议一致：自动转换只能解决一部分问题，真正的工程迁移还需要 build-mode 设计、兼容层、验证体系和性能分析。

参考资料：

- AMD ROCm HIP porting guide: https://rocm.docs.amd.com/projects/HIP/en/latest/how-to/hip_porting_guide.html
- ROCm CMake packages: https://rocm.docs.amd.com/en/latest/conceptual/cmake-packages.html
- HIPIFY: https://github.com/ROCm/HIPIFY
- CMake CUDA language support: https://cmake.org/cmake/help/latest/prop_tgt/CUDA_ARCHITECTURES.html
- Ginkgo CUDA-to-HIP porting case study: https://arxiv.org/abs/2006.14290
- GPU numerics portability paper: https://arxiv.org/abs/2410.09172

## 构建模式设计

当前公开构建模式如下：

| 模式 | CMake 选项 | 用途 |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | CPU baseline |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | NVIDIA / 上游兼容后端 |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD Radeon / ROCm 后端 |

约定：

- `BUILD_CUDA` 与 `BUILD_ROCM` 互斥；
- 默认二者都 OFF 时构建 CPU 模式；
- `BUILD_HIP` 不再作为公开选项；
- ROCm/HIP 统一通过 `BUILD_ROCM=ON` 表达；
- 不要在同一个 build directory 中切换 CPU/CUDA/ROCm 模式。

推荐构建目录：

```text
build-cpu/
build-cuda/
build-rocm-plc/
build-rocm-w7900/
```

原因是 CMake 会缓存 compiler、backend option、library path 和 package discovery 结果。不同后端复用同一个 build 目录容易产生混乱。

## 后端兼容层

这次迁移中最重要的教训之一是：**不能让 HIP API 直接泄漏到共享 C 代码路径里**。

例如，如果共享文件里直接出现：

```c
hipblasCreate(...)
hipsparseCreate(...)
hipDeviceReset()
hipFree(...)
```

那么 CUDA build 很可能编译或链接失败。

因此项目引入后端兼容映射层，让共享代码调用项目级 API，而不是直接调用 CUDA 或 HIP API。

示例风格：

```c
CUPDLP_BLAS_CREATE(...)
CUPDLP_SPARSE_CREATE(...)
CUPDLP_DEVICE_RESET()
CUPDLP_DEVICE_FREE(...)
```

然后在兼容头中按后端映射：

| 项目级 API | CUDA 后端 | ROCm/HIP 后端 |
|---|---|---|
| `CUPDLP_BLAS_CREATE` | `cublasCreate` | `hipblasCreate` |
| `CUPDLP_SPARSE_CREATE` | `cusparseCreate` | `hipsparseCreate` |
| `CUPDLP_DEVICE_RESET` | `cudaDeviceReset` | `hipDeviceReset` |
| `CUPDLP_DEVICE_FREE` | `cudaFree` | `hipFree` |

这样可以在尽量复用公共 solver 逻辑的同时，保留 CUDA 和 ROCm/HIP 两条 GPU 路径。

## 哪些命名该改，哪些可以暂时不改？

迁移项目中很容易陷入“把所有 cuda 字样都改掉”的陷阱。

本项目采用分级策略：

| 区域 | 策略 |
|---|---|
| README / docs | 面向用户的说明应明确 CPU / CUDA / ROCm-HIP |
| scripts | ROCm 工作流使用 ROCm/HIP 命名 |
| 用户可见日志 | 尽量避免误导性的 CUDA 字样 |
| 内部兼容字段 | 可以暂时保留 CUDA 风格命名 |
| 上游历史文档 | 保留 CUDA 背景 |
| 迁移辅助脚本 | 保留历史和迁移痕迹 |

因此，内部仍可能看到：

```text
cuda_csr
cuda_vec
cupdlp_update_average_cuda
```

这类名称不一定表示 ROCm/HIP 运行时在调用 CUDA 库。它们可能只是历史兼容字段或共享结构体名称。

更安全的策略是：

1. 先修用户可见文档和日志；
2. 再修构建选项和脚本；
3. 最后再逐步重构内部命名；
4. 每次内部命名重构都必须同时验证 CPU/CUDA/ROCm 三种模式。

## 验证流程演进

### 阶段 1：最小 smoke

最小样例：

```text
example/afiro.mps
```

它用来确认：

- 程序能否构建；
- MPS 文件能否读取；
- 后端能否初始化；
- JSON 输出是否正常；
- solver 能否结束。

### 阶段 2：小型 Netlib case

随后加入：

```text
sc50b
sc105
sc205
scagr7
recipe
lotfi
```

这些 case 用于暴露 parser、稀疏矩阵、内存分配、向量更新和迭代路径问题。

### 阶段 3：跨设备 benchmark

后续扩展到：

- RTX 3090 CUDA；
- RTX 4090D CUDA；
- Radeon 890M ROCm/HIP；
- 每台机器的 CPU baseline。

统一设置包括：

- `nIterLim=200000000`；
- 长 case 采用 3600 秒 wall-clock policy；
- 记录 status、iterations、solve time、feasibility、duality gap；
- 保留 timeout 和 limit case 作为数值行为证据。

## 跨设备 benchmark 经验

跨设备测试说明：

1. 小 case 很容易被启动开销和固定开销主导；
2. 中大型 case 更适合比较 GPU 后端；
3. 有些 case CPU 更快，并不代表 GPU 后端无价值；
4. 长迭代和稀疏矩阵占主导的 case 更能体现 GPU 优势；
5. CPU、CUDA、ROCm/HIP 的 iteration count 不一定完全一致；
6. `greenbea` 这类 case 应该作为数值行为诊断，而不是普通 pass/fail smoke。

因此本项目将 workflow 分层：

| Workflow | 目的 |
|---|---|
| smoke validation | 快速构建与正确性检查 |
| tuning quick set | ROCm 调优开发 |
| full validation matrix | 跨设备对比 |
| long numerical cases | 收敛轨迹分析 |
| profiling set | 定位 kernel / copy / sync 开销 |

## ROCm 调优证据

项目已经做过若干 ROCm tuning：

| Commit | 改动 |
|---|---|
| `f9d7f0d` | 移除 movement interaction 中多余 HIP device synchronize |
| `8fed073` | 缓存 HIP device attributes |
| `fa7e860` | 融合 ROCm average iterate axpy updates |
| `b44c7ab` | 减少 movement interaction scalar copies |

最初这些调优缺少完整 before/after 证据。后来补充了 repeated ablation：

- 6 个 milestone；
- 6 个 case；
- 每个 version/case 重复 5 次；
- median solve time 作为主指标；
- 保留 mean/std/min/max/CV。

结果显示，current 相对 pre-tuning baseline 在 quick set 上有可测提升。

此外，又做了 current HEAD 与 `reduce_scalar_copies` 的 27-case repeated comparison。结果表明：当前三模态工程版本与此前最快 ROCm tuning milestone 整体性能基本持平，没有出现系统性性能回退。

## 数值行为经验

`greenbea` 是本项目重点保留的数值行为 case。

它不应被简单删除，原因是：

- CPU 可达到 `OPTIMAL`；
- CUDA/ROCm GPU 路径可能出现 timeout 或 convergence-sensitive 行为；
- 它能帮助观察不同后端的数值轨迹差异；
- 它能提醒我们不要只看 quick smoke。

项目策略：

- 保留 `greenbea`；
- 记录 timeout / limit；
- 记录 feasibility / gap；
- 区分 runtime failure 和 solver convergence limit；
- 不通过无限延长时间强行追求收敛；
- 后续增加 checkpoint logging 和 profiling。

## 本次迁移中遇到的典型问题

### 1. 构建选项混乱

问题：

```text
BUILD_CUDA
BUILD_ROCM
BUILD_HIP
```

多个选项语义重叠，容易导致用户误用。

解决：

```text
BUILD_CUDA=ON  -> CUDA
BUILD_ROCM=ON  -> ROCm/HIP
二者都 OFF     -> CPU
BUILD_HIP      -> 移除公开选项
```

### 2. HIP API 泄漏进 CUDA build

问题：

共享路径中直接调用 HIP API，导致 CUDA 构建失败。

解决：

使用 `cupdlp_backend_compat.h` 中的项目级兼容宏。

### 3. ROCm 优化误伤 CUDA

问题：

ROCm fused kernel 曾经通过泛 GPU 条件进入 CUDA build，导致 CUDA 下找不到符号。

解决：

ROCm-only fast path 使用：

```c
#if defined(CUPDLP_USE_ROCM) && USE_KERNELS
```

CUDA 后端继续走原 BLAS/AXPY 路径，除非以后单独实现并验证 CUDA fused kernel。

### 4. 脚本散落在根目录

问题：

临时 benchmark 脚本放在仓库根目录会让项目结构混乱。

解决：

- 常规构建/验证/benchmark 脚本放 `scripts/`；
- 迁移辅助脚本放 `tools/migration/`；
- curated 结果放 `validation/`；
- 本地原始大结果放 `validation/results/`，不作为主要提交对象。

### 5. 单次 benchmark 容易误判

问题：

单次 timing 有噪声，尤其是小 case。

解决：

- tuning ablation 采用 repeat；
- 主指标使用 median；
- 保留 mean/std/CV；
- 需要时做 focused repeat 和 profiling。

### 6. Python CSV 生成 CRLF

问题：

Python `csv` 默认可能生成 CRLF，导致 `git diff --check` 报 trailing whitespace。

解决：

```python
csv.DictWriter(..., lineterminator="\n")
```

并通过 `.gitattributes` 统一仓库文本行尾。

## 类似项目的推荐迁移流程

对于其他 CUDA 依赖的科学计算项目，推荐按以下顺序迁移：

1. 保留上游 baseline；
2. 先验证 CPU 或非 GPU 路径；
3. 在原 CUDA 环境中确认上游 GPU 路径可用；
4. 添加最小 ROCm/HIP 后端；
5. 尽早建立 backend compatibility layer；
6. 简化公开构建选项；
7. 先跑通一个最小 case；
8. 扩展小/中/大 case；
9. 建立脚本化 validation；
10. 建立跨设备 benchmark；
11. 保留并解释 long convergence-sensitive case；
12. 每次性能优化都配套 repeated benchmark；
13. 再做 profiler 驱动的定向优化；
14. 最后再做内部命名重构。

## 推荐仓库结构

```text
README.md
README.zh-CN.md
CMakeLists.txt

cupdlp/
  cuda/
  hip/
  cupdlp_backend_compat.h

interface/

scripts/
  run_validation.sh
  run_benchmark_*.sh
  summarize_benchmark.py
  run_rocm_tuning_*.sh

tools/
  migration/

validation/
  cases.txt
  cases_tuning_quick.txt
  rocm_tuning_ablation_*.csv
  rocm_current_vs_reduce_*.csv
  netlib/

docs/
  BACKEND_MODES_AND_NAMING.md
  VALIDATION.md
  CROSS_DEVICE_BENCHMARKS.md
  ROCM_TUNING_HISTORY.md
  NUMERICAL_BEHAVIOR_GREENBEA.md
  CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md
```

## 常用构建命令

### CPU

```bash
cmake -S . -B build-cpu \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=OFF

cmake --build build-cpu --target plc -j"$(nproc)"
```

### ROCm/HIP

```bash
cmake -S . -B build-rocm-plc \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1150

cmake --build build-rocm-plc --target plc -j"$(nproc)"
```

Radeon PRO W7900 后续应使用：

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1100
```

### CUDA

```bash
cmake -S . -B build-cuda \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=ON \
  -DBUILD_ROCM=OFF

cmake --build build-cuda --target plc -j"$(nproc)"
```

## 后续工作

项目已经完成基础迁移和初步调优，但仍有后续任务：

1. 补齐中英文双文档；
2. 用 `rocprofv3` 建立调优前后的时间占比证据；
3. 引入更大规模 MPS 数据集；
4. 在 CUDA 环境中对比 cuPDLP-C 与 cuPDLPx；
5. 迁移到 Radeon PRO W7900 / `gfx1100`；
6. 针对 W7900 做平台特化 profiling 和优化；
7. 对 `greenbea` 增加 checkpoint-level trajectory logging；
8. 将更多验证流程脚本化，形成 CI-lite。

## 总结

这个项目最重要的经验是：

> CUDA 到 ROCm/HIP 的迁移不是简单 API 替换，而是一个包含后端边界、构建系统、验证矩阵、性能证据和数值行为解释的完整工程过程。

对本项目而言，成功路线是：

1. 保留 CPU 和 CUDA baseline；
2. 增加 ROCm/HIP 作为第三后端；
3. 建立 backend compatibility layer；
4. 用 MPS/Netlib case 逐步验证；
5. 做跨设备 benchmark；
6. 用 repeated benchmark 证明调优效果；
7. 用数值行为文档解释 convergence-sensitive case；
8. 后续再迁移到 W7900 并做平台化优化。
