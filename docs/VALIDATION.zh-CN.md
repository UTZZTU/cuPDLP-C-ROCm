# ROCm 验证

> English version: [VALIDATION.md](VALIDATION.md)  
> 文档地图: [README.md](README.md)  
> Validation 结果索引: [../validation/README.zh-CN.md](../validation/README.zh-CN.md)

本文定义 `cuPDLP-C-ROCm` 如何用 CPU baseline 验证 ROCm/HIP backend。

## 验证结果文件

整理后的 validation Markdown 汇总和 CSV 文件统一索引在：

- [../validation/README.zh-CN.md](../validation/README.zh-CN.md)
- [../validation/README.md](../validation/README.md)

常用 validation CSV：

| 结果组 | Markdown 汇总 | CSV 文件 |
|---|---|---|
| 跨设备 Netlib 汇总 | [CROSS_DEVICE_BENCHMARKS.zh-CN.md](CROSS_DEVICE_BENCHMARKS.zh-CN.md) | [cross_device_full_summary.csv](../validation/cross_device_full_summary.csv) |
| current vs reduce 重复测试对比 | [../validation/rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md) | [comparison](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.csv), [aggregated](../validation/rocm_current_vs_reduce_27cases_repeats_aggregated.csv), [raw](../validation/rocm_current_vs_reduce_27cases_repeats_raw.csv) |
| rocprof tuning milestones | [../validation/rocm_prof_tuning_milestones_summary.zh-CN.md](../validation/rocm_prof_tuning_milestones_summary.zh-CN.md) | [summary](../validation/rocm_prof_tuning_milestones_summary.csv), [deltas](../validation/rocm_prof_tuning_milestones_deltas.csv), [HIP API](../validation/rocm_prof_tuning_milestones_hip_api_top.csv), [kernel](../validation/rocm_prof_tuning_milestones_kernel_top.csv), [memory-copy](../validation/rocm_prof_tuning_milestones_memory_copy_top.csv) |
| tuning ablation 6-case 重复测试 | [../validation/rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md](../validation/rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md) | [summary](../validation/rocm_tuning_ablation_6cases_repeats_summary.csv), [raw](../validation/rocm_tuning_ablation_6cases_repeats_raw.csv) |

## 已验证 ROCm 目标

| 项目 | 890M / `gfx1150` | W7900 / `gfx1100` |
|---|---|---|
| GPU/APU | AMD Radeon 890M | AMD Radeon PRO W7900 |
| ROCm | 7.2.1 | W7900 ROCm SDK environment |
| HIP compiler | ROCm Clang 22.0.0 | `/opt/python/bin/hipcc` / ROCm SDK |
| Solver 可执行文件 | `build-rocm-plc/bin/plc` | `build-rocm-w7900/bin/plc` |
| 状态 | smoke、Netlib、benchmark、890M tuning history 已归档 | smoke、Netlib、large-MPS baseline、P10 profiling、P11 tuning、P12 rejected finding 已归档 |
| CPU baseline 可执行文件 | `build-cpu/bin/plc` | `build-cpu/bin/plc` |

## 验证目标

验证 workflow 检查 ROCm/HIP backend 相比 CPU backend 是否产生数值上合理的结果。CPU backend 被用作正确性 baseline，因为它不依赖 GPU runtime 行为，也更容易 debug。

验证目标不是 bitwise equality。CPU 和 ROCm/HIP run 可能因为以下原因走出不同浮点轨迹：

- BLAS 和 sparse library 不同；
- sparse matrix-vector multiplication 顺序不同；
- reduction 顺序不同；
- restart 轨迹不同；
- kernel launch 和 synchronization 行为不同。

因此验证目标是：

```text
same solver status + comparable relative feasibility and gap metrics
```

## 验证层级

本项目当前使用以下验证层级：

1. Smoke validation。
2. Extended Netlib validation。
3. Cross-device Netlib benchmark validation。
4. Large MPS dataset validation and performance benchmarking。

Smoke validation 是修改 ROCm/HIP backend 代码前后的最低必跑检查。Extended 和 benchmark validation 用于较大改动后的覆盖扩展。

## Smoke validation

默认 smoke validation：

```bash
./scripts/run_validation.sh
```

当前 smoke case 列在：

```text
validation/cases.txt
```

当前 smoke case：

| Case | MPS 路径 | 迭代限制 | 结果 |
|---|---|---:|---|
| `afiro` | `example/afiro.mps` | 200 | PASS |
| `sc50b` | `validation/netlib/sc50b.mps` | 5000 | PASS |

期望摘要：

```text
PASS: 2
INCOMPLETE: 0
FAIL: 0
```

生成的 smoke report 位于：

```text
validation/results/latest/
```

该目录是生成输出，不应提交。

## 完整 ROCm port 检查

推荐本地检查：

```bash
./scripts/check_rocm_port.sh
ctest --test-dir build-rocm-plc --output-on-failure
```

完整检查包括：

1. `scripts/check_rocm_port_hygiene.sh`
2. `scripts/run_validation.sh`
3. 已配置 ROCm build tree 时的 CTest ROCm 检查。

在推送 ROCm/HIP backend、validation script 或 workflow 变化前使用此命令。

## ROCm hygiene 检查

Hygiene 检查脚本是：

```bash
./scripts/check_rocm_port_hygiene.sh
```

它检查以下 guardrail：

- HIP backend 文件不应重新引入直接 `CHECK_CUDA`、`CHECK_CUSPARSE` 或 `CHECK_CUBLAS` 调用。
- CMake 文件不应重新引入容易误导的历史 HIP/CUDA 公共选项。
- 必需的 HIP 检查宏，例如 `CHECK_HIP_STRICT`，必须保留。
- `cuda_csr_Ax`、`cuda_csc_ATy`、`cuda_alloc_MVbuffer` 等 legacy exported compatibility symbol 在 C/HIP 边界安全重构前必须保留。

## Extended Netlib validation

准备 Netlib case：

```bash
./scripts/prepare_netlib_cases.sh
```

运行 extended validation：

```bash
RESULT_ROOT=validation/results/extended_netlib \
  ./scripts/run_validation.sh validation/cases_extended_netlib.txt
```

当前 extended case 列在：

```text
validation/cases_extended_netlib.txt
```

当前 extended validation 状态：

| Case | MPS 路径 | 迭代限制 | 结果 | 说明 |
|---|---|---:|---|---|
| `afiro` | `example/afiro.mps` | 200 | PASS | 基线示例 |
| `adlittle` | `validation/netlib/adlittle.mps` | 5000 | PASS | 相对验证指标通过 |
| `blend` | `validation/netlib/blend.mps` | 5000 | PASS | 相对验证指标通过 |
| `sc50a` | `validation/netlib/sc50a.mps` | 5000 | PASS | 相对验证指标通过 |
| `sc50b` | `validation/netlib/sc50b.mps` | 5000 | PASS | Smoke + extended case |
| `share2b` | `validation/netlib/share2b.mps` | 5000 | INCOMPLETE | 当前设置下达到迭代或时间限制 |

期望 extended summary：

```text
PASS: 5
INCOMPLETE: 1
FAIL: 0
```

当 CPU 和 ROCm 在当前迭代或时间限制下表现一致时，`INCOMPLETE` 不被视为 ROCm port failure。

## Medium 和 large validation set

项目正在从小 Netlib case 扩展到更大 case。更大验证工作应按以下顺序推进：

1. 在 Git 之外准备或下载 MPS 文件。
2. 生成包含文件名和大小的 inventory 文件。
3. 生成 SHA256 manifest。
4. 将同一数据集下载或复制到每台设备。
5. benchmark 前运行 `sha256sum -c`。
6. 只提交 manifest、整理后的 summary 和文档。

当前 large MPS workflow 见 [LARGE_MPS_BENCHMARK_PLAN.zh-CN.md](LARGE_MPS_BENCHMARK_PLAN.zh-CN.md)。

## 比较脚本

比较脚本是：

```bash
scripts/compare_cpu_rocm.py
```

它读取 CPU 和 ROCm JSON 输出文件，并生成 Markdown 比较报告，包含：

- status comparison；
- hard relative metric comparison；
- informational diagnostics。

## 状态比较

以下状态字段是 hard check：

| 字段 | 含义 |
|---|---|
| `terminationCode` | Solver termination status |
| `primalCode` | Primal feasibility status |
| `dualCode` | Dual feasibility status |

PASS 结果要求 CPU 和 ROCm 状态码一致。

## Hard numeric checks

当 CPU 和 ROCm 都报告：

```text
terminationCode = OPTIMAL
```

hard numeric checks 为：

| 指标 | 容忍度 |
|---|---:|
| `dRelPrimalFeas` | `1e-4` |
| `dRelDualFeas` | `1e-4` |
| `dRelDualityGap` | `1e-4` |

这些相对指标比 raw absolute objective difference 更适合跨 CPU 和 GPU 执行路径比较。

## Informational diagnostics

以下字段会被记录，但它们本身不是 hard failure criteria：

| 字段 | 原因 |
|---|---|
| `nIter` | CPU 和 GPU 可能有不同 restart 或浮点轨迹 |
| `dPrimalObj` | 绝对目标值差异可能依赖问题尺度 |
| `dDualObj` | 绝对目标值差异可能依赖问题尺度 |
| `dPrimalFeas` | 绝对可行性可能依赖问题尺度 |
| `dDualFeas` | 绝对可行性可能依赖问题尺度 |
| `dDualityGap` | 绝对 gap 可能依赖问题尺度 |

CPU 和 ROCm run 可以在迭代数或中间绝对值上不同，同时仍达到等价的相对 feasibility 和 gap 标准。

## PASS、INCOMPLETE 和 FAIL

### PASS

满足以下条件时 case 为 PASS：

- 状态字段匹配；
- CPU 和 ROCm 都报告 `OPTIMAL`；
- hard relative metric 在容忍度内。

### INCOMPLETE

满足以下条件时 case 为 INCOMPLETE：

- CPU 和 ROCm 都达到当前迭代或时间限制；或
- case 需要更高迭代限制或单独调查；并且
- 结果不表明 ROCm-specific correctness failure。

`share2b` 和 `greenbea` 这类 convergence-sensitive case 应记录，而不是隐藏。

### FAIL

满足以下条件时 case 为 FAIL：

- CPU 和 ROCm 状态码不同；
- 或者两者都报告 `OPTIMAL` 但 hard relative metric 超过容忍度；
- 或者出现未处理状态组合。

FAIL 表示在把 ROCm/HIP backend 视为该 case 已验证之前，需要进一步调查。

## CTest 集成

启用 testing 配置：

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
```

列出测试：

```bash
ctest --test-dir build-rocm-plc -N
```

运行测试：

```bash
ctest --test-dir build-rocm-plc --output-on-failure
```

## 手动验证命令

构建 CPU：

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

构建 ROCm/HIP：

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

运行 CPU：

```bash
./build-cpu/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_cpu_sum.json \
  -nIterLim 200
```

运行 ROCm/HIP：

```bash
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_sum.json \
  -nIterLim 200
```

比较输出：

```bash
scripts/compare_cpu_rocm.py \
  --case afiro \
  --cpu /tmp/afiro_cpu_sum.json \
  --rocm /tmp/afiro_rocm_sum.json \
  --out /tmp/afiro_compare.md
```

## 生成文件

Validation script 会生成：

```text
validation/results/
```

Netlib 准备过程会生成：

```text
validation/netlib/
validation/netlib_compressed/
tools/emps
tools/emps.c
```

这些路径应被 Git 忽略。只提交源脚本、case list、manifest、整理后的 summary 和文档。

## 当前限制与已完成验证范围

- ROCm/HIP backend 仍是实验性，不是生产级认证 solver release。
- 原始 `gfx1150` / 890M validation target 已完成当前范围。
- W7900 / `gfx1100` validation 也已完成当前范围：smoke、Netlib、
  large-MPS baseline、P10 profiling、P11 SpMV tuning、P12 rejected
  experiment note 均已归档。
- `share2b` 在当前 Netlib 迭代或时间限制下仍为 INCOMPLETE。
- `greenbea` 是 convergence-sensitive case，应继续单独记录。
- 当前还没有 ROCm CI runner。
- 部分 legacy CUDA-style 名称因 C/HIP 兼容边界仍保留。

## 后续验证工作

已完成或已被取代的项目：

- larger sparse LP validation：已在 curated large-MPS benchmark 范围完成；
- validate `gfx1100`：已在 W7900 当前项目范围完成；
- profiling/tuning validation：已由 P10/P11/P12 完成。

可选未来工作：

- 增加更多 Netlib LP cases；
- 增加 infeasible 和 unbounded LP cases；
- 增加 badly scaled cases；
- 定期记录 validation snapshots；
- 有合适 runner 时添加 ROCm CI；
- W7900 可用后补 P14-A current-vs-before repeated validation；
- W7900 可用后补 P14-B CSR ALG1-vs-ALG2 repeated validation。
