# cuPDLP-C-ROCm

> English: [README.en.md](README.en.md)
> 文档地图：[docs/README.md](docs/README.md)
> 竞赛评审入口：[docs/COMPETITION_README.zh-CN.md](docs/COMPETITION_README.zh-CN.md)

`cuPDLP-C-ROCm` 是上游 [cuPDLP-C](README_UPSTREAM.md) 的 ROCm/HIP 移植、验证与性能分析分支。项目保留 CPU 和上游兼容 CUDA 路径，并新增 AMD GPU 后端，重点记录科学计算求解器从 CUDA 迁移到 ROCm 时的工程边界、数值验证和性能证据。

## 项目定位

本项目的贡献不是提出新的线性规划算法，而是：

- 将 cuPDLP-C 的 GPU 执行路径迁移到 ROCm/HIP；
- 维护 CPU、CUDA、ROCm 三种后端模式；
- 为 smoke、Netlib、large-MPS、profiling 和 tuning 建立可追溯证据链；
- 记录性能优化与数值收敛相互影响的正向和负向实验；
- 提供可复用的 CUDA-to-ROCm 科学计算迁移经验。

| 项目 | 当前状态 |
|---|---|
| 当前主分支 | `rocm-w7900-gfx1100` |
| 当前主要 ROCm 平台 | Radeon PRO W7900 / `gfx1100` |
| 早期 ROCm 里程碑 | Radeon 890M / `gfx1150` |
| 参考后端 | CPU、CUDA（RTX 3090、RTX 4090D、H100） |
| 当前 W7900 SpMV 默认策略 | `HIPSPARSE_SPMV_CSR_ALG1` |
| 回退策略 | `CUPDLP_HIP_SPMV_ALG=csr_alg2` |
| 发布属性 | 研究与工程验证项目；不是生产级、广泛认证的求解器发行版 |

## 关键结果

| 证据 | 结果 | 说明 |
|---|---|---|
| W7900 large-MPS non-hard23 | 23/23 `OPTIMAL` | wall time 2960.171 s；solve time 2742.940 s |
| P10 targeted profiling | rocSPARSE CSR SpMV 为主要 GPU 热点 | `hipMemcpy`、`hipMemcpyAsync` 和 kernel launch 也值得关注 |
| P11 SpMV tuning | 接受 `CSR_ALG1` 作为当前默认 | 保留 `csr_alg2` 环境变量回退路径 |
| P12 negative experiment | patch 被拒绝 | `set-cover-model` 迭代数由 7480 变为 7600，说明执行层修改也可能改变数值轨迹 |
| P14-A1 quick6 repeats | current 6/6 胜出 | geomean speedup 1.18889；median 1.19502；迭代数保持一致 |
| 8-card fast8 batch | 146 s vs 单卡顺序 558 s | 这是 8 个独立 MPS 任务的吞吐实验，不是单个 LP 的分布式多 GPU 求解 |

完整结果、边界条件和证据链接见 [W7900 当前状态](docs/W7900_CURRENT_STATUS.zh-CN.md) 与 [Validation 索引](validation/README.zh-CN.md)。

## 求解与执行流程

```text
MPS input
  -> HiGHS parsing / optional presolve
  -> cuPDLP model and scaling
  -> CSR + CSC sparse matrices
  -> CPU / CUDA / ROCm backend
  -> PDHG iterations
  -> feasibility, gap and termination checks
  -> JSON / solution output
```

当前提交的主要验证路径使用 HiGHS 解析，并保持 presolve 关闭。代码中存在 optional presolve 路径，但 nontrivial postsolve 与恢复到原始变量空间尚未纳入当前验证合同，因此不能把它描述为已经完整验证的主流程。

核心工作负载包括 `Ax`、`Aᵀy` 稀疏矩阵向量乘、向量更新、投影、归约、步长调整和 restart。端到端性能通常可以理解为：

```text
total time ≈ per-iteration cost × number of iterations
```

因此，GPU kernel 更快不一定自动带来总求解时间更短；浮点顺序和执行层变化也可能改变收敛路径。

## 后端模式

| 模式 | CMake 选项 | 用途 |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | 正确性与可移植性基线 |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | NVIDIA 参考后端 |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD GPU 后端 |

`BUILD_CUDA` 与 `BUILD_ROCM` 不应同时开启。不同后端应使用独立构建目录。

## 快速开始

### 1. 克隆仓库

```bash
git clone --recurse-submodules \
  --branch rocm-w7900-gfx1100 \
  https://github.com/UTZZTU/cuPDLP-C-ROCm.git
cd cuPDLP-C-ROCm
```

### 2. 在任意主机检查已提交证据

没有 W7900 时仍可检查仓库中已提交的 CSV、Markdown 和 SVG：

```bash
python3 - <<'PY'
import csv
from pathlib import Path

rows = list(csv.DictReader(
    Path("validation/w7900_large_mps_nonhard23_20260613.csv").open()
))
print("cases:", len(rows))
print("termination:", sorted({r["terminationCode"] for r in rows}))
print("wall:", sum(float(r["wall_seconds"]) for r in rows))
print("solve:", sum(float(r["dSolvingTime"]) for r in rows))
PY
```

预期为 23 个 case，且 termination 全部为 `OPTIMAL`。

### 3. 在 W7900 上恢复、构建并运行 smoke

仓库的 bootstrap 脚本默认管理 `/app/cupdlp_w7900` 工作区，并会在其中克隆或更新固定分支、准备 HiGHS、构建 CPU/ROCm 版本。一次完成恢复、构建和 smoke：

```bash
RUN_BUILD=1 RUN_SMOKE=1 \
  bash scripts/bootstrap_w7900_workspace.sh
```

完成后，脚本管理的仓库位于：

```text
/app/cupdlp_w7900/src/cuPDLP-C-ROCm
```

在已经激活依赖与 ROCm 环境的现有 checkout 中，也可以只运行：

```bash
bash scripts/build_w7900_cpu.sh
bash scripts/build_w7900_rocm.sh
bash scripts/run_w7900_smoke.sh
```

维护脚本使用：

```text
build-cpu/bin/plc
build-rocm-w7900/bin/plc
```

`plc` 的最小调用形式为：

```bash
./build-rocm-w7900/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm.json \
  -nIterLim 200
```

环境、数据集、profiling 和 repeated-validation 细节见[可复现性指南](docs/REPRODUCIBILITY.zh-CN.md)。

## 文档入口

| 需求 | 中文 | English |
|---|---|---|
| 完整文档导航 | [文档地图](docs/README.md) | [Documentation map](docs/README.md) |
| 构建和运行 | [ROCm 工作流](docs/ROCM_WORKFLOW.zh-CN.md) | [ROCm workflow](docs/ROCM_WORKFLOW.md) |
| 复现实验 | [可复现性指南](docs/REPRODUCIBILITY.zh-CN.md) | [Reproducibility](docs/REPRODUCIBILITY.md) |
| 验证语义 | [验证说明](docs/VALIDATION.zh-CN.md) | [Validation semantics](docs/VALIDATION.md) |
| 当前 W7900 结论 | [W7900 当前状态](docs/W7900_CURRENT_STATUS.zh-CN.md) | [W7900 current status](docs/W7900_CURRENT_STATUS.md) |
| 性能与调优 | [性能行为](docs/W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)、[调优历史](docs/ROCM_TUNING_HISTORY.zh-CN.md) | [Performance behavior](docs/W7900_PERFORMANCE_BEHAVIOR.md), [tuning history](docs/ROCM_TUNING_HISTORY.md) |
| 原始汇总索引 | [Validation 索引](validation/README.zh-CN.md) | [Validation index](validation/README.md) |
| CUDA-to-ROCm 迁移 | [迁移案例](docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) | [Migration case study](docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) |
| 竞赛评审 | [竞赛入口](docs/COMPETITION_README.zh-CN.md) | [Competition entry](docs/COMPETITION_README.md) |

## 结果与数据策略

原始 large-MPS 文件、原始 profiler trace、机器本地构建目录和临时运行目录不进入 Git。仓库提交：

- case lists 和 manifests；
- curated CSV；
- Markdown summaries；
- 小型 SVG 图表；
- 可复现脚本；
- 接受和拒绝的调优结论。

历史日期化报告保留为证据，但当前结论只在主页、`docs/W7900_CURRENT_STATUS*` 和索引文档中维护。

## 已知限制

- 当前 ROCm 实现和参数主要在 `gfx1150`、`gfx1100` 上验证，不能等同于所有 AMD 架构均已认证。
- W7900 aggregate performance 仍落后于本项目中的高端 CUDA 参考；竞争力需要结合具体 case 和收敛路径解释。
- hard3 与 non-hard23 分开报告，不能把 hard3 隐藏或混入主结果。
- 8 卡结果是独立任务并发吞吐，不是单问题多 GPU 算法。
- Docker 文件是环境骨架，不是当前 W7900 性能数字的来源。
- Python/apps 等可选路径不是当前 ROCm 主验证路径。

## 上游与许可证

上游 README 快照保存在 [README_UPSTREAM.md](README_UPSTREAM.md)，用于说明原始项目背景。除非相应文件另有说明，本仓库遵循 [MIT License](LICENSE)。
