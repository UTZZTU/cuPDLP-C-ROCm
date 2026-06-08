# 验证指南

本文说明如何在 `cuPDLP-C-ROCm` 项目中进行 CPU / CUDA / ROCm-HIP 三种后端的构建、smoke validation、full benchmark、结果汇总和故障排查。

本文对应英文文档：

- [`docs/VALIDATION.md`](VALIDATION.md)

## 验证目标

本项目的验证不是只确认某个样例能运行，而是要回答以下问题：

1. CPU、CUDA、ROCm/HIP 三种构建模式是否边界清晰？
2. ROCm/HIP 后端是否能在 Radeon 平台上构建并运行？
3. CUDA 后端是否仍保持上游兼容？
4. 同一批 MPS case 在不同后端上的 termination status、iteration count 和 solve time 是否可记录、可比较？
5. timeout、runtime failure、数值收敛差异是否能被区分？
6. 性能调优是否有 repeated benchmark 和 profiling 证据支持？

上游 `cuPDLP-C` 是用 GPU 上的一阶 PDLP 算法求解 LP 的 C 实现。本 fork 的验证体系在此基础上增加了 ROCm/HIP 后端和跨设备对照。

## 后端模式

当前公开构建模式为：

| 模式 | CMake 选项 | 用途 |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | 正确性与可移植性 baseline |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | NVIDIA / 上游兼容 GPU 后端 |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD Radeon / ROCm 目标后端 |

约定：

- `BUILD_CUDA` 与 `BUILD_ROCM` 不能同时为 ON；
- `BUILD_HIP` 不再作为公开选项；
- ROCm/HIP 构建统一使用 `BUILD_ROCM=ON`；
- 不同后端应使用不同 build directory；
- 不要在同一 build directory 中反复切换 CPU/CUDA/ROCm 模式。

## 依赖

### 通用依赖

- CMake
- C/C++ 编译器
- HiGHS
- MPS / Netlib 测试数据
- Python 3

HiGHS 是一个开源高性能线性优化软件，项目通过 HiGHS 相关接口读取和处理 MPS/LP 数据。

### ROCm/HIP 后端依赖

常用检查命令：

```bash
rocminfo | grep -E "Name:|gfx" | head -n 80
rocm-smi
hipcc --version
```

Radeon 890M 当前开发目标为：

```text
gfx1150
```

Radeon PRO W7900 后续目标为：

```text
gfx1100
```

### CUDA 后端依赖

CUDA 构建需要：

- CUDA toolkit；
- cuBLAS；
- cuSPARSE；
- 可用 NVIDIA GPU；
- 正确的 `CUDA_HOME` 和 `LD_LIBRARY_PATH`；
- 对应机器上的 HiGHS 路径。

在多 GPU 服务器上，CUDA run 还需要注意 `CUDA_VISIBLE_DEVICES`、GPU compute mode、其他进程占用和 CUDA context 初始化问题。

## 构建验证

### CPU build

```bash
cmake -S . -B build-cpu \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=OFF

cmake --build build-cpu --target plc -j"$(nproc)"
```

### ROCm/HIP build：Radeon 890M / gfx1150

```bash
cmake -S . -B build-rocm-plc \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1150

cmake --build build-rocm-plc --target plc -j"$(nproc)"
```

### ROCm/HIP build：Radeon PRO W7900 / gfx1100

```bash
cmake -S . -B build-rocm-w7900 \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1100

cmake --build build-rocm-w7900 --target plc -j"$(nproc)"
```

### CUDA build

```bash
cmake -S . -B build-cuda \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=ON \
  -DBUILD_ROCM=OFF

cmake --build build-cuda --target plc -j"$(nproc)"
```

如果 CUDA build 失败，应优先检查：

- `CUDA_HOME` 是否正确；
- `nvcc` 是否可用；
- `LD_LIBRARY_PATH` 是否包含 CUDA 和 HiGHS；
- CMake 是否找到了正确 CUDA toolkit；
- 是否误用了 ROCm/HIP-only API；
- 是否有 unresolved symbol；
- `BUILD_CUDA` 与 `BUILD_ROCM` 是否同时打开。

## 最小 smoke test

最小 smoke case：

```text
example/afiro.mps
```

ROCm/HIP：

```bash
./build-rocm-plc/bin/plc \
  -fname example/afiro.mps \
  -out /tmp/afiro_rocm.json \
  -nIterLim 200000000

cat /tmp/afiro_rocm.json
```

CPU：

```bash
./build-cpu/bin/plc \
  -fname example/afiro.mps \
  -out /tmp/afiro_cpu.json \
  -nIterLim 200000000

cat /tmp/afiro_cpu.json
```

CUDA：

```bash
CUDA_VISIBLE_DEVICES=0 ./build-cuda/bin/plc \
  -fname example/afiro.mps \
  -out /tmp/afiro_cuda.json \
  -nIterLim 200000000

cat /tmp/afiro_cuda.json
```

成功时应看到 JSON 中包含：

```json
"terminationCode":"OPTIMAL"
```

以及 `nIter`、`dSolvingTime`、`dRelPrimalFeas`、`dRelDualFeas`、`dRelDualityGap` 等字段。

## 常用验证 case list

### smoke case

```text
afiro
sc50b
```

用途：

- 快速判断 build 和 runtime 是否正常；
- 快速发现 backend 初始化问题；
- 不适合用于严肃性能比较。

### tuning quick set

当前 tuning quick set 包括：

```text
afiro
sc50b
lotfi
80bau3b
maros-r7
pilot87
```

用途：

- 比较 ROCm tuning milestone；
- 快速发现优化是否影响 correctness；
- 进行 repeated benchmark；
- 观察中小规模 case 的性能变化。

### full benchmark set

当前 full benchmark set 包含 28 个 case，其中 `greenbea` 单独作为 convergence-sensitive case 解释。

常用全量 case 包括：

```text
25fv47
80bau3b
afiro
degen2
degen3
fit1d
fit2d
greenbea
greenbeb
israel
lotfi
maros-r7
pilot4
pilot87
recipe
sc105
sc205
sc50b
scagr25
scagr7
scfxm1
scfxm2
scfxm3
sctap1
sctap2
ship04s
ship08s
stair
```

不含 `greenbea` 的 27-case set 适合用于 current-vs-tuning milestone repeated comparison。

## 结果字段说明

典型 solver JSON 包含：

| 字段 | 含义 |
|---|---|
| `solver` | solver 名称 |
| `nIter` | 迭代次数 |
| `dSolvingTime` | solver 求解时间 |
| `dPresolveTime` | presolve 时间 |
| `dScalingTime` | scaling 时间 |
| `DeviceMatVecProdTime` | GPU 矩阵-向量相关时间 |
| `dPrimalObj` | primal objective |
| `dDualObj` | dual objective |
| `dPrimalFeas` | primal feasibility |
| `dDualFeas` | dual feasibility |
| `dDualityGap` | duality gap |
| `dRelPrimalFeas` | relative primal feasibility |
| `dRelDualFeas` | relative dual feasibility |
| `dRelDualityGap` | relative duality gap |
| `terminationCode` | termination status |
| `primalCode` | primal feasibility code |
| `dualCode` | dual feasibility code |

常见 `terminationCode`：

| 值 | 解释 |
|---|---|
| `OPTIMAL` | 达到 solver optimal termination |
| `TIMELIMIT_OR_ITERLIMIT` | 达到时间或迭代限制 |
| 空缺 | 可能是 shell timeout、runtime failure 或 JSON 未生成 |

## 如何区分不同失败类型

### 1. solver 正常结束但未 OPTIMAL

表现：

```json
"terminationCode":"TIMELIMIT_OR_ITERLIMIT"
```

这属于 solver-level limit。应保留 JSON，并记录 feasibility/gap。

### 2. shell-level timeout

表现：

```text
.exitcode = 124
JSON 可能不存在或不完整
```

这是外部 `timeout` 命令终止进程。应记录为 wall-clock timeout，而不是简单删除。

### 3. runtime failure

表现可能包括：

```text
CUDA context cannot be initialized
CUSPARSE API failed
hipSPARSE API failed
hipBLAS API failed
Segmentation fault
undefined symbol
```

这类错误是 runtime/build/backend 问题，应与 solver convergence limit 区分。

### 4. build failure

表现：

```text
cmake configure failed
cmake build failed
undefined reference
header not found
library not found
```

应先修构建和链接，不要把它当成 solver 数值问题。

## greenbea 特殊说明

`greenbea` 是本项目保留的 convergence-sensitive case。

它不应被视为普通 smoke failure，也不应因为 GPU timeout 而删除。

项目策略：

- 保留 `greenbea`；
- 单独记录 timeout / limit；
- 保留 feasibility 和 gap 字段；
- 区分 CPU、CUDA、ROCm/HIP 数值轨迹；
- 不通过无限延长 time limit 强行追求收敛；
- 后续增加 checkpoint-level logging 和 profiling。

详细说明见：

- [`docs/NUMERICAL_BEHAVIOR_GREENBEA.md`](NUMERICAL_BEHAVIOR_GREENBEA.md)
- [`docs/NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md`](NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md)

## Benchmark 脚本

### ROCm tuning ablation

```bash
REPEAT_N=5 CASE_TIMEOUT_SEC=900 \
  scripts/run_rocm_tuning_ablation_6cases_repeats.sh
```

输出示例：

```text
validation/results/tuning_ablation_6cases_repeats_<timestamp>/
```

固化结果：

```text
validation/rocm_tuning_ablation_6cases_repeats_raw.csv
validation/rocm_tuning_ablation_6cases_repeats_summary.csv
validation/rocm_tuning_ablation_6cases_repeats_summary.md
```

### current vs reduce_scalar_copies

```bash
REPEAT_N=3 CASE_TIMEOUT_SEC=900 \
  scripts/run_rocm_current_vs_reduce_27cases_repeats.sh
```

输出示例：

```text
validation/results/current_vs_reduce_27cases_repeats_<timestamp>/
```

固化结果：

```text
validation/rocm_current_vs_reduce_27cases_repeats_raw.csv
validation/rocm_current_vs_reduce_27cases_repeats_aggregated.csv
validation/rocm_current_vs_reduce_27cases_repeats_comparison.csv
validation/rocm_current_vs_reduce_27cases_repeats_comparison.md
```

### benchmark 汇总

```bash
scripts/summarize_benchmark.py
```

该脚本会读取每个 case 的 JSON 和 exit code，生成 summary CSV/MD。

## Repeated benchmark 规则

性能比较不建议依赖单次运行。

推荐规则：

| 场景 | 推荐 repeat |
|---|---:|
| smoke | 1 |
| quick tuning | 3-5 |
| 正式 tuning ablation | 5 |
| focused regression check | 10 |
| 大规模长 case | 1-3，视运行时间决定 |

主指标：

```text
median solve time
```

同时保留：

- mean；
- std；
- min；
- max；
- CV；
- termination status；
- iteration count。

## 如何解读小 case

小 case 如 `afiro`、`recipe`、`sc50b` 可能受以下因素主导：

- 程序启动；
- 文件读取；
- backend 初始化；
- GPU memory allocation；
- kernel launch；
- host-device scalar transfer；
- synchronization；
- 系统负载和功耗状态。

因此，小 case 可以用于 smoke 和 overhead 观察，但不适合单独作为 GPU 性能结论。

## 如何解读中大型 case

中大型 case 更适合看 GPU 后端：

- SpMV 时间占比更高；
- 向量更新更多；
- GPU 并行度更容易体现；
- 固定启动开销占比更低。

后续 H100 和 W7900 上的大规模 MPS 数据会更适合展示 ROCm/Radeon 平台能力。

## ROCm profiling

Benchmark 回答“快不快”，profiling 回答“为什么快或慢”。

后续建议使用 `rocprofv3` 记录：

- HIP runtime API trace；
- HSA trace；
- kernel dispatch trace；
- memory copy trace；
- memory allocation trace；
- marker trace；
- kernel timeline。

典型命令形式：

```bash
rocprofv3 --sys-trace -- ./build-rocm-plc/bin/plc \
  -fname validation/netlib/lotfi.mps \
  -out /tmp/lotfi_rocm.json \
  -nIterLim 200000000
```

优先 profiling case：

| Case | 原因 |
|---|---|
| `lotfi` | tuning 收益明显 |
| `scfxm1` | current-vs-reduce 中略慢，适合查疑点 |
| `pilot87` | 较大 case，适合作为正向对照 |

后续 W7900 上应加入一个大规模 MPS 代表 case。

## 仓库结果管理

推荐约定：

| 文件类型 | 位置 |
|---|---|
| 常规脚本 | `scripts/` |
| 迁移辅助脚本 | `tools/migration/` |
| case list | `validation/` |
| curated CSV/MD | `validation/` |
| 本地原始结果 | `validation/results/` |
| 文档 | `docs/` |

`validation/results/` 通常包含大量本地原始 logs，不应全部作为主要提交对象。建议只把整理后的 summary CSV/MD 固化到 `validation/`。

## 提交前检查

提交前建议执行：

```bash
git status --short
git diff --check
```

检查 CRLF：

```bash
git ls-files -z | while IFS= read -r -d '' f; do
  [ -f "$f" ] || continue
  case "$f" in
    *.mps) continue ;;
  esac
  grep -Iq . "$f" || continue
  grep -Il $'\r' "$f" || true
done | sort
```

如果有 Python CSV 生成脚本，应确保：

```python
csv.DictWriter(..., lineterminator="\n")
```

## 当前已完成验证结论

当前阶段项目已经完成：

1. CPU / CUDA / ROCm 三模态构建边界整理；
2. ROCm/HIP 后端在 Radeon 890M 上可构建、可运行；
3. CUDA 后端已恢复 smoke 兼容；
4. full benchmark 覆盖多组 Netlib/MPS case；
5. 3090 / 4090D / 890M 跨设备结果已记录；
6. ROCm tuning ablation 已做 repeated benchmark；
7. current 与 `reduce_scalar_copies` milestone 的 27-case 对比已完成；
8. `greenbea` 数值行为已单独文档化；
9. 中英文文档体系正在补齐。

## 后续验证计划

建议后续按以下顺序推进：

1. 完成中英文文档；
2. 增加 ROCm profiling 脚本；
3. 对 `lotfi`、`scfxm1`、`pilot87` 做 current-vs-reduce profiling；
4. 在 H100 上整理大规模 MPS inventory；
5. 选择 medium-large / large MPS 子集；
6. 在 3090 / 4090D / H100 上跑 CUDA baseline；
7. 在 W7900 上跑 ROCm/HIP 主平台结果；
8. 对比 cuPDLP-C 与 cuPDLPx；
9. 根据 profiling 结果继续 ROCm/HIP 调优。

## 总结

本项目的验证体系已经从“单个样例能否跑通”扩展为：

- 三后端构建验证；
- smoke validation；
- Netlib/MPS full benchmark；
- repeated tuning ablation；
- current-vs-history performance check；
- convergence-sensitive case 文档；
- 后续 profiling 和 W7900 平台验证计划。

这套验证体系的目标是确保 ROCm/HIP 移植不仅能运行，而且能被复现、比较、解释和继续优化。
