# 跨设备 benchmark 记录

本文记录 `cuPDLP-C-ROCm` 项目当前阶段的跨设备 benchmark 设计、已完成结果和后续扩展计划。

本项目的跨设备 benchmark 不是单纯比较“哪张显卡更快”，而是为了回答以下问题：

1. ROCm/HIP 后端是否能在 AMD Radeon 平台上稳定求解代表性 LP/MPS case？
2. CPU、CUDA、ROCm/HIP 三种后端的 termination status、iteration count 和 solve time 有何差异？
3. 小规模、中规模、大规模 case 对 GPU 后端的表现有何影响？
4. current 工程版本相对历史 tuning milestone 是否出现性能回退？
5. 后续迁移到 Radeon PRO W7900 时应如何选择 benchmark 子集？

## 项目背景

`cuPDLP-C-ROCm` 是基于上游 `cuPDLP-C` 的 ROCm/HIP 移植和工程化验证分支。

当前项目保留三种后端：

| 后端 | 作用 |
|---|---|
| CPU | 正确性与可移植性 baseline |
| CUDA | 上游兼容的 NVIDIA GPU baseline |
| ROCm/HIP | AMD Radeon / ROCm 目标后端 |

跨设备 benchmark 的目标是把这三种后端放在可比较的实验框架里，而不是只在单个 `afiro.mps` 上证明能运行。

## 当前已测试平台

当前阶段已记录以下平台：

| 平台 | 后端 | 作用 |
|---|---|---|
| RTX 3090 | CUDA | NVIDIA CUDA baseline |
| RTX 4090D | CUDA | 更强 NVIDIA CUDA baseline |
| Radeon 890M | ROCm/HIP | AMD Radeon / gfx1150 本地开发验证平台 |
| 各机器 CPU | CPU | 每台机器本地 CPU baseline |

后续计划加入：

| 平台 | 后端 | 作用 |
|---|---|---|
| H100 | CUDA | 大规模 MPS / 高端 CUDA 对照 |
| Radeon PRO W7900 | ROCm/HIP | 比赛主平台，gfx1100 目标后端 |

Radeon PRO W7900 是 AMD Radeon PRO W 系列 RDNA3 设备，ROCm 支持矩阵中列为 `gfx1100`。后续迁移时需要将 ROCm build 的 `CMAKE_HIP_ARCHITECTURES` 从当前 890M 的 `gfx1150` 切换到 W7900 的 `gfx1100`。

## Benchmark 设计原则

### 统一 case list

当前 full benchmark 使用统一的 MPS case list。典型 case 包括：

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

其中 `greenbea` 被单独视为 convergence-sensitive case，不作为普通 quick validation case 解读。

### 统一 solver 参数

主要 benchmark 使用：

```text
nIterLim = 200000000
```

对于长 case，使用 3600 秒作为实际 long-case wall-clock policy。达到 timeout 或 `TIMELIMIT_OR_ITERLIMIT` 的结果不删除，而是保留为数值行为证据。

### 统一记录字段

每个 case 尽量记录：

- backend；
- case name；
- termination status；
- shell exit code；
- iteration count；
- solve time；
- DeviceMatVecProdTime；
- primal feasibility；
- dual feasibility；
- duality gap；
- JSON 输出；
- stdout/stderr log；
- GPU/CPU 型号；
- CUDA 或 ROCm 版本；
- commit SHA。

## 为什么不能只看 solve time？

LP 一阶方法的跨设备表现需要同时看：

1. termination status；
2. iteration count；
3. solve time；
4. feasibility / gap；
5. 是否达到 wall-clock limit；
6. GPU kernel 时间；
7. host-device copy 和 runtime overhead。

如果只看 solve time，容易误解两类情况：

- 小 case 上 GPU 慢，可能只是 launch overhead 主导；
- 长 case timeout，可能是数值轨迹差异，而不是 runtime failure。

因此，本项目同时保留 JSON 字段和日志，而不是只保留 summary table。

## Radeon 890M ROCm/HIP full run

Radeon 890M 上的 ROCm/HIP full run 显示：除 `greenbea` 外，大多数 case 能在 ROCm/HIP 后端达到 `OPTIMAL`。

代表性结果：

| Case | CPU status | ROCm/HIP status | CPU iter | ROCm iter | CPU time | ROCm time | 说明 |
|---|---|---|---:|---:|---:|---:|---|
| `afiro` | OPTIMAL | OPTIMAL | 200 | 200 | 0.000223 | 0.055775 | 极小 case，GPU 固定开销主导 |
| `80bau3b` | OPTIMAL | OPTIMAL | 10120 | 10280 | 0.908968 | 0.887086 | ROCm/HIP 接近或略快 |
| `fit2d` | OPTIMAL | OPTIMAL | 5000 | 5040 | 1.00425 | 1.18779 | ROCm/HIP 略慢 |
| `greenbeb` | OPTIMAL | OPTIMAL | 752560 | 1814520 | 54.0035 | 152.025 | GPU 迭代轨迹不同 |
| `pilot4` | OPTIMAL | OPTIMAL | 2694640 | 2222240 | 32.7476 | 97.1357 | 长迭代 case |
| `pilot87` | OPTIMAL | OPTIMAL | 71280 | 81960 | 7.69941 | 7.91001 | 接近持平 |
| `greenbea` | OPTIMAL | shell timeout | 8538920 | — | 592.58 | — | convergence-sensitive case |

解读：

- Radeon 890M 是集成 GPU / 本地开发平台，不应期望在所有 case 上超过高端 CPU 或独立 GPU；
- 它的价值在于验证 ROCm/HIP 移植路径、构建流程、正确性和初步性能；
- 小 case 被固定开销主导；
- 更大规模 MPS case 更适合展示 GPU 后端价值；
- `greenbea` 不应作为普通失败样例删除，而应保留为数值行为 case。

## RTX 4090D CUDA full run

RTX 4090D CUDA full run 在排除早期 CUDA context 初始化问题后，完成了大部分 case 的 CUDA 数据记录。

代表性结果：

| Case | CPU status | CUDA status | CPU iter | CUDA iter | CPU time | CUDA time | 说明 |
|---|---|---|---:|---:|---:|---:|---|
| `afiro` | OPTIMAL | OPTIMAL | 200 | 200 | 0.000228 | 0.033316 | 极小 case，GPU 固定开销主导 |
| `80bau3b` | OPTIMAL | OPTIMAL | 10120 | 11720 | 1.67521 | 0.873151 | CUDA 明显快于 CPU |
| `fit2d` | OPTIMAL | OPTIMAL | 5000 | 4640 | 1.98156 | 0.376708 | CUDA 优势明显 |
| `greenbeb` | OPTIMAL | OPTIMAL | 752560 | 965560 | 103.155 | 72.3501 | CUDA 快于 CPU |
| `pilot87` | OPTIMAL | OPTIMAL | 71280 | 91880 | 14.9857 | 8.00709 | CUDA 快于 CPU |
| `greenbea` | OPTIMAL | shell timeout | 8538920 | — | 1178.48 | — | convergence-sensitive case |

解读：

- RTX 4090D 在中大型 case 上能明显体现 CUDA GPU 优势；
- `greenbea` 仍然表现为特殊长时间收敛敏感 case；
- 早期 CUDA context 初始化失败是运行环境问题，与 solver correctness 需要分开记录。

## RTX 3090 CUDA results

RTX 3090 上记录了 full 5M run 和专门的 `greenbea` 200M run。

`greenbea` 200M dedicated run：

| Backend | Status | Iterations | Solve time | Relative primal feasibility | Relative dual feasibility | Relative duality gap |
|---|---|---:|---:|---:|---:|---:|
| CPU | OPTIMAL | 8,538,920 | 1286.92 s | — | — | — |
| CUDA GPU | TIMELIMIT_OR_ITERLIMIT | 41,615,624 | 3600.000060 s | 0.21299620838891 | 0.00000067393008 | 0.00256258916268 |

解读：

- RTX 3090 CUDA 也没有在 3600 秒内让 `greenbea` GPU path 达到 `OPTIMAL`；
- 这进一步说明 `greenbea` 是跨 GPU 后端的 convergence-sensitive case；
- 不能把 `greenbea` timeout 简单归因到 ROCm/HIP。

## current vs reduce_scalar_copies 27-case repeated comparison

为了确认 current 三模态工程版本是否相对历史最快 ROCm tuning milestone 出现性能回退，项目比较了：

```text
base:    reduce_scalar_copies (`b44c7ab`)
current: 当前 HEAD
case:    full benchmark list 去掉 greenbea
repeat:  3 次
```

结果：

```text
Geometric mean speedup of base over current: 0.9995092331107024
```

解读：

- base 与 current 整体几何平均几乎持平；
- current 没有出现系统性性能回退；
- 少数小 case 上 current 略慢，多数差距在噪声范围；
- 一些中大型 case 上 current 反而更快；
- 当前三模态工程结构可以作为后续 W7900 迁移 baseline。

慢超过 2% 的 case：

```text
afiro
sc50b
recipe
scfxm1
```

其中 `afiro`、`sc50b`、`recipe` 都偏小，容易受固定开销和噪声影响。`scfxm1` 后续可以作为 focused profiling 候选。

current 更快的代表 case：

```text
israel
maros-r7
ship08s
degen2
greenbeb
pilot87
```

这说明 current 与 `reduce_scalar_copies` 的关系不能简单说成“变慢”或“变快”，更合理的表述是整体持平。

## 为什么大规模 MPS 很重要？

当前 Netlib case 对项目早期验证很有价值，但规模不一定足够展示高端 GPU 优势。

小 case 中，以下开销可能占主导：

- 程序启动；
- MPS 读取；
- backend 初始化；
- device memory allocation；
- kernel launch；
- host-device scalar copy；
- synchronization。

随着问题规模增大，SpMV 和向量更新的计算量增加，GPU 并行能力更容易体现。因此，后续应引入 H100 机器上的大规模 MPS 数据集，筛选 medium-large / large / stress 三层 case。

建议分层：

| 层级 | 用途 |
|---|---|
| smoke | 构建和基本 correctness |
| quick tuning | 快速调优对比 |
| full validation | 代表性跨设备验证 |
| medium-large | 展示 GPU 优势 |
| large | W7900 / H100 / 4090D 主对比 |
| stress | 长时间数值行为分析 |

## 后续 H100 / W7900 benchmark 计划

### H100

H100 主要用于：

- 跑大规模 MPS inventory；
- 建立 CUDA 高端 GPU 上限参考；
- 对 cuPDLP-C 与 cuPDLPx 做 CUDA baseline 对比；
- 筛选适合 W7900 的大规模 case 子集。

建议先做 inventory：

```bash
find /path/to/mps_root -type f \( -name "*.mps" -o -name "*.mps.gz" -o -name "*.MPS" -o -name "*.MPS.gz" \) \
  -printf "%p,%s\n" | sort -t, -k2,2n > h100_large_mps_inventory.csv
```

然后按文件大小、来源、预估运行时间分层，不要一开始全量跑。

### Radeon PRO W7900

W7900 是比赛主平台，后续应作为 ROCm/HIP 主要展示设备。

迁移时先检查环境：

```bash
rocminfo | grep -E "Name:|gfx" | head -n 80
rocm-smi
hipcc --version
```

构建目标：

```bash
cmake -S . -B build-rocm-w7900 \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1100

cmake --build build-rocm-w7900 --target plc -j"$(nproc)"
```

W7900 benchmark 顺序建议：

1. smoke：`afiro`、`sc50b`；
2. quick tuning set：6-case；
3. full no-greenbea：27-case；
4. greenbea：单独长 case；
5. medium-large MPS subset；
6. large MPS subset；
7. rocprofv3 profiling set。

## Profiling 与 benchmark 的关系

Benchmark 回答“快不快”，profiling 回答“为什么快或慢”。

后续 ROCm profiling 应关注：

- HIP runtime API；
- kernel dispatch；
- memory copy；
- memory allocation；
- HSA trace；
- SpMV kernel；
- vector update kernel；
- synchronization；
- kernel launch overhead。

建议先 profile：

```text
lotfi
scfxm1
pilot87
```

原因：

| Case | 用途 |
|---|---|
| `lotfi` | tuning 收益明显，适合解释优化收益 |
| `scfxm1` | current 相对 reduce 略慢，适合查疑点 |
| `pilot87` | 较大 case，current 表现较好，适合作正向对照 |

后续在 W7900 上还应加入一个大规模 MPS 代表 case。

## 当前结论

当前跨设备 benchmark 支持以下阶段性结论：

1. ROCm/HIP 后端已经能在 Radeon 890M 上完成 broad validation set 中的大多数 case；
2. RTX 4090D / RTX 3090 CUDA 数据提供了 NVIDIA GPU baseline；
3. 小 case 不适合直接判断 GPU 计算能力；
4. 中大型 case 更能体现 GPU 后端优势；
5. `greenbea` 是 convergence-sensitive case，应单独分析；
6. current 三模态工程版本没有相对历史最快 ROCm tuning milestone 出现系统性性能回退；
7. 后续需要引入更大规模 MPS 数据和 W7900 平台实测。

## 已固化结果文件

项目当前保留以下 benchmark 相关结果文件：

```text
validation/rocm_tuning_ablation_6cases_repeats_raw.csv
validation/rocm_tuning_ablation_6cases_repeats_summary.csv
validation/rocm_tuning_ablation_6cases_repeats_summary.md

validation/rocm_current_vs_reduce_27cases_repeats_raw.csv
validation/rocm_current_vs_reduce_27cases_repeats_aggregated.csv
validation/rocm_current_vs_reduce_27cases_repeats_comparison.csv
validation/rocm_current_vs_reduce_27cases_repeats_comparison.md
```

跨设备 full benchmark 的 summary 记录在对应 docs 和 validation 结果中。大型原始 logs 通常保留在本地 `validation/results/`，不作为主要 curated artifact 提交。

## 后续任务

建议后续按以下顺序推进：

1. 补齐中英文文档；
2. 增加 `rocprofv3` profiling 脚本；
3. 引入 H100 大规模 MPS inventory；
4. 选择 medium-large / large 子集；
5. 在 3090、4090D、H100 上跑 CUDA baseline；
6. 在 W7900 上跑 ROCm/HIP 主平台结果；
7. 对 cuPDLP-C 与 cuPDLPx 做 CUDA 环境对比；
8. 将 W7900 数据补入 cross-device benchmark；
9. 根据 profiling 结果继续 ROCm/HIP 平台化调优。

## 总结

跨设备 benchmark 当前已经证明：本项目不再只是“ROCm/HIP 能跑 afiro”，而是已经具备 CPU / CUDA / ROCm 三模态对照、Netlib full validation、tuning ablation 和 convergence-sensitive case 记录。

下一阶段的重点是：

> 引入更大规模 MPS 数据、补充 ROCm profiling 证据，并将主平台迁移到 Radeon PRO W7900，用更具代表性的科学计算负载展示 ROCm/Radeon 平台能力。
