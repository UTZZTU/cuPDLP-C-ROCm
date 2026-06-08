# cuPDLP-C-ROCm

> 中文说明文档。英文主页见 [`README.md`](README.md)。

`cuPDLP-C-ROCm` 是基于上游 [`COPT-Public/cuPDLP-C`](https://github.com/COPT-Public/cuPDLP-C) 的 ROCm/HIP 移植与工程化验证项目。项目目标是在保留 CPU 与 CUDA 路径的基础上，为 AMD Radeon / ROCm 平台提供可构建、可验证、可 benchmark 的 PDLP 一阶线性规划求解器实验分支。

当前分支重点面向：

- AMD Radeon 890M / `gfx1150` 本地开发与验证；
- 后续迁移到 AMD Radeon PRO W7900 / `gfx1100` 平台；
- 与 NVIDIA CUDA 设备上的上游 GPU 路径进行对照；
- 为大规模线性规划、科学计算和 ROCm 生态迁移提供可复现实验材料。

## 项目背景

线性规划（Linear Programming, LP）是运筹优化、工程调度、能源系统、网络流、机器学习和科学计算中的基础问题。PDLP / PDHG 类一阶方法近年来在大规模 LP 上受到关注，因为其核心计算以稀疏矩阵-向量乘法和向量更新为主，天然适合 GPU 并行。

上游 `cuPDLP-C` 是 cuPDLP 的 C 语言实现，面向 CUDA GPU。这个项目在其基础上探索：

1. 如何将 CUDA 依赖的科学计算项目迁移到 AMD ROCm/HIP；
2. 如何保留 CPU / CUDA / ROCm 三种后端模式；
3. 如何在 AMD Radeon 平台上验证正确性、性能和数值行为；
4. 如何用 benchmark 与 profiling 数据解释优化效果。

## 当前状态

项目当前已经形成三种后端模式：

| 模式 | CMake 选项 | 作用 |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | 正确性与可移植性基线 |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | 保留上游 NVIDIA GPU 后端 |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD Radeon / ROCm 目标后端 |

注意：

- `BUILD_CUDA` 和 `BUILD_ROCM` 互斥；
- 旧的 `BUILD_HIP` 公共选项已移除；
- ROCm/HIP 构建统一使用 `BUILD_ROCM=ON`；
- 内部仍可能保留部分 `cuda_*` 兼容命名，它们不代表 ROCm 运行时在调用 CUDA 库。

## 已完成工作概览

本项目已经完成以下阶段性工作：

- 建立 ROCm/HIP 后端目录与 CMake 构建路径；
- 适配 hipBLAS / hipSPARSE / HIP runtime；
- 修复 CPU、CUDA、ROCm 三模态构建边界；
- 恢复 CUDA backend 兼容性；
- 移除旧的 `BUILD_HIP` 公共构建选项；
- 建立 Netlib/MPS 验证脚本与 benchmark 脚本；
- 完成 Radeon 890M 上的 ROCm/HIP 验证；
- 完成 RTX 3090 / RTX 4090D / Radeon 890M 的跨设备 benchmark 记录；
- 对 ROCm tuning 做了 repeated ablation；
- 记录 `greenbea` 数值行为差异；
- 编写 CUDA 到 ROCm/HIP 迁移案例文档；
- 建立 `.gitattributes` 行尾规范，减少 CRLF/LF 问题。

## 仓库结构

```text
README.md
README.zh-CN.md
CMakeLists.txt

cupdlp/
  cuda/                         # 上游 CUDA 后端
  hip/                          # ROCm/HIP 后端
  cupdlp_backend_compat.h       # 后端兼容映射层

interface/                      # MPS/HiGHS 接口与命令行入口

scripts/
  run_validation.sh
  summarize_benchmark.py
  run_rocm_tuning_*.sh
  run_rocm_current_vs_reduce_*.sh

tools/
  migration/                    # 迁移辅助脚本

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
- [`docs/ROCM_PROFILING_NOTES.md`](docs/ROCM_PROFILING_NOTES.md)
  NUMERICAL_BEHAVIOR_GREENBEA.md
  CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md
```

## 依赖环境

### 通用依赖

- CMake
- C/C++ 编译器
- HiGHS 1.6.0
- Netlib / MPS 测试数据

### ROCm/HIP 后端

建议使用 ROCm 7.x 或与目标 Radeon GPU 兼容的 ROCm 版本。Radeon 890M 当前开发目标为 `gfx1150`，Radeon PRO W7900 后续目标为 `gfx1100`。

常用检查命令：

```bash
rocminfo | grep -E "Name:|gfx" | head -n 80
rocm-smi
hipcc --version
```

### CUDA 后端

CUDA 后端保留为上游兼容路径，适用于 RTX 3090、RTX 4090D、H100 等 NVIDIA 环境。具体 CUDA 版本、HiGHS 路径和 GPU compute mode 需要按机器配置设置。

## 构建方式

### CPU 构建

```bash
cmake -S . -B build-cpu \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=OFF

cmake --build build-cpu --target plc -j"$(nproc)"
```

### ROCm/HIP 构建：Radeon 890M / gfx1150

```bash
cmake -S . -B build-rocm-plc \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1150

cmake --build build-rocm-plc --target plc -j"$(nproc)"
```

### ROCm/HIP 构建：Radeon PRO W7900 / gfx1100

```bash
cmake -S . -B build-rocm-w7900 \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1100

cmake --build build-rocm-w7900 --target plc -j"$(nproc)"
```

### CUDA 构建

```bash
cmake -S . -B build-cuda \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=ON \
  -DBUILD_ROCM=OFF

cmake --build build-cuda --target plc -j"$(nproc)"
```

不同机器上的 CUDA、HiGHS、CMake 路径可能不同，请按实际环境设置 `CUDA_HOME`、`HIGHS_HOME`、`PATH` 和 `LD_LIBRARY_PATH`。

## 快速运行

以 `afiro.mps` 为例：

```bash
./build-rocm-plc/bin/plc \
  -fname example/afiro.mps \
  -out /tmp/afiro_rocm.json \
  -nIterLim 200000000

cat /tmp/afiro_rocm.json
```

CPU 版本：

```bash
./build-cpu/bin/plc \
  -fname example/afiro.mps \
  -out /tmp/afiro_cpu.json \
  -nIterLim 200000000
```

## 验证与 benchmark

常用验证入口：

```bash
scripts/run_validation.sh
```

benchmark 结果汇总：

```bash
scripts/summarize_benchmark.py
```

ROCm tuning quick set：

```bash
REPEAT_N=5 CASE_TIMEOUT_SEC=900 \
  scripts/run_rocm_tuning_ablation_6cases_repeats.sh
```

当前工程版本与 `reduce_scalar_copies` milestone 的 27-case 对比：

```bash
REPEAT_N=3 CASE_TIMEOUT_SEC=900 \
  scripts/run_rocm_current_vs_reduce_27cases_repeats.sh
```

## 当前 benchmark 结论摘要

项目目前已经记录：

- Radeon 890M ROCm/HIP full benchmark；
- RTX 3090 CUDA benchmark；
- RTX 4090D CUDA benchmark；
- ROCm tuning ablation repeated results；
- current HEAD 与 `reduce_scalar_copies` milestone 的 27-case repeated comparison；
- `greenbea` 长时间收敛敏感 case 的数值行为。

重要结论：

1. 当前 ROCm/HIP 后端可以在 Radeon 890M 上完成 broad validation set 的多数 case；
2. ROCm tuning 相对 pre-tuning baseline 在 quick set 上有可测收益；
3. 当前三模态工程版本与此前最快 ROCm tuning milestone 整体性能基本持平；
4. `greenbea` 是 convergence-sensitive case，应单独记录数值轨迹，不应简单隐藏；
5. 小规模 case 可能被 launch overhead 和固定开销主导，大规模 MPS 数据更适合展示 GPU 价值。

详细数据见：

- [`docs/VALIDATION.md`](docs/VALIDATION.md)
- [`docs/CROSS_DEVICE_BENCHMARKS.md`](docs/CROSS_DEVICE_BENCHMARKS.md)
- [`docs/ROCM_TUNING_HISTORY.md`](docs/ROCM_TUNING_HISTORY.md)
- [`docs/NUMERICAL_BEHAVIOR_GREENBEA.md`](docs/NUMERICAL_BEHAVIOR_GREENBEA.md)

## 数值行为说明：greenbea

`greenbea` 被保留为数值行为诊断 case。它不是普通 smoke test，而是用于观察 CPU、CUDA、ROCm/HIP 在长迭代、收敛敏感 LP 上的轨迹差异。

当前项目策略：

- 保留 `greenbea`；
- 记录 timeout / limit 结果；
- 记录 iteration、feasibility、duality gap；
- 不通过无限延长时间强行追求收敛；
- 后续通过 checkpoint logging 与 profiling 分析轨迹差异。

详细说明见：

- [`docs/NUMERICAL_BEHAVIOR_GREENBEA.md`](docs/NUMERICAL_BEHAVIOR_GREENBEA.md)

## ROCm tuning 与 profiling 计划

当前项目已经完成初步 tuning ablation，但后续还会继续补充 ROCm profiling 证据。
   参考 [`docs/ROCM_PROFILING_NOTES.zh-CN.md`](docs/ROCM_PROFILING_NOTES.zh-CN.md) 与 [`docs/ROCM_PROFILING_NOTES.md`](docs/ROCM_PROFILING_NOTES.md)。

计划使用 `rocprofv3` 记录：

- HIP runtime API 时间；
- kernel dispatch 次数；
- kernel 执行时间；
- memory copy 时间；
- memory allocation 时间；
- 同步调用开销；
- SpMV 与 vector update 的时间占比。

目标不是只报告“变快了”，而是解释“为什么变快”。

## 后续计划

后续路线按由简到难推进：

1. **中英文文档体系**  
   为主要英文文档补充对应中文文档，方便中文读者学习和复现。

2. **ROCm profiling 证据**  
   用 `rocprofv3` 对典型 case 做调优前后对比。

3. **大规模 MPS 数据集**  
   在 H100 / RTX 4090D / RTX 3090 / Radeon 890M / Radeon PRO W7900 上建立更大规模 benchmark matrix。

4. **cuPDLP-C 与 cuPDLPx 对比**  
   先在 CUDA 环境下比较两者在相同 MPS case 上的运行表现，再评估是否需要迁移 cuPDLPx 到 ROCm/HIP。

5. **Radeon PRO W7900 迁移与优化**  
   将当前 ROCm/HIP 工程经验迁移到比赛平台 W7900，并针对 `gfx1100` 做 profiling 与优化。

## 文档索引

英文文档：

- [`docs/BACKEND_MODES_AND_NAMING.md`](docs/BACKEND_MODES_AND_NAMING.md)
- [`docs/VALIDATION.md`](docs/VALIDATION.md)
- [`docs/CROSS_DEVICE_BENCHMARKS.md`](docs/CROSS_DEVICE_BENCHMARKS.md)
- [`docs/ROCM_TUNING_HISTORY.md`](docs/ROCM_TUNING_HISTORY.md)
- [`docs/NUMERICAL_BEHAVIOR_GREENBEA.md`](docs/NUMERICAL_BEHAVIOR_GREENBEA.md)
- [`docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md`](docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md)

中文文档将逐步补齐：

- `README.zh-CN.md`
- `docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md`
- `docs/ROCM_TUNING_HISTORY.zh-CN.md`
- `docs/ROCM_PROFILING_NOTES.zh-CN.md`
- `docs/NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md`
- `docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md`
- `docs/VALIDATION.zh-CN.md`

## 贡献与维护约定

- 修改英文文档时，应同步更新对应中文文档；
- 普通脚本放在 `scripts/`；
- 迁移辅助脚本放在 `tools/migration/`；
- curated benchmark CSV/MD 放在 `validation/`；
- 大量本地实验输出放在 `validation/results/`，不作为主要提交对象；
- 不要把 ROCm timeout case 简单删掉，应保留为数值行为证据；
- 性能优化需要配套 before/after benchmark 或 profiling 记录。

## 致谢

本项目基于上游 `cuPDLP-C`，其算法与工程基础来自 cuPDLP / PDLP / PDHG 相关研究与开源实现。该 fork 的重点是探索 CUDA 科学计算项目迁移到 AMD ROCm/HIP 与 Radeon 平台时的工程路径、验证方法和性能调优流程。
