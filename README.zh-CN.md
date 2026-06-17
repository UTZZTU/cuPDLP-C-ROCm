<!-- COMPETITION_README_20260614_BEGIN -->
> 普通 GitHub 读者：请从本 README 和 [文档地图](docs/README.md) 开始。
> AMD ROCm/Radeon 赛题评委：请查看 [docs/COMPETITION_README.md](docs/COMPETITION_README.md) / [docs/COMPETITION_README.zh-CN.md](docs/COMPETITION_README.zh-CN.md)。
<!-- COMPETITION_README_20260614_END -->

# cuPDLP-C-ROCm

| 入口 | 链接 |
|---|---|
| English homepage | [README.en.md](README.en.md) |
| ROCm/gfx1150 快速入口 | [README_ROCM_gfx1150.zh-CN.md](README_ROCM_gfx1150.zh-CN.md) |
| 文档地图 | [docs/README.md](docs/README.md) |
| 验证数据索引 | [validation/README.zh-CN.md](validation/README.zh-CN.md) |
| Benchmark 索引 | [docs/benchmarks/README.md](docs/benchmarks/README.md) |

`cuPDLP-C-ROCm` 是基于上游 cuPDLP-C 的 ROCm/HIP 移植与验证分支。项目保留 CPU 路径和上游兼容 CUDA 路径，并新增面向 AMD Radeon 平台的 ROCm/HIP 后端。

| 项目 | 当前值 |
|---|---|
| 主要 ROCm 目标 | AMD Radeon 890M |
| ROCm 架构 | `gfx1150` |
| 本地验证 ROCm 版本 | 7.2.1 |
| 已完成验证与调优的额外 ROCm 目标 | AMD Radeon PRO W7900 / `gfx1100` |
| CUDA baseline 设备 | RTX 3090, RTX 4090D, H100 |

> 状态：实验性但可构建。当前 ROCm/HIP 后端已经通过 smoke validation、Netlib 验证、跨设备 benchmark、large-MPS baseline，以及 Radeon 890M / `gfx1150` 与 Radeon PRO W7900 / `gfx1100` 上的验证与调优记录。W7900 阶段已经完成 P10 targeted profiling 和 P11 SpMV tuning；当前默认 SpMV algorithm 为 `HIPSPARSE_SPMV_CSR_ALG1`，旧默认可用 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 回退。它仍不是生产级、广泛认证的 ROCm solver release，但当前项目阶段已经完成。

## 从哪里开始

| 需求 | English | 中文 |
|---|---|---|
| ROCm/gfx1150 快速入口 | [README_ROCM_gfx1150.md](README_ROCM_gfx1150.md) | [README_ROCM_gfx1150.zh-CN.md](README_ROCM_gfx1150.zh-CN.md) |
| 完整文档地图 | [docs/README.md](docs/README.md) | [docs/README.md](docs/README.md) |
| 验证数据索引 | [validation/README.md](validation/README.md) | [validation/README.zh-CN.md](validation/README.zh-CN.md) |
| Benchmark 索引 | [docs/benchmarks/README.md](docs/benchmarks/README.md) | [docs/benchmarks/README.md](docs/benchmarks/README.md) |

## 文档

| 需求 | English | 中文 |
|---|---|---|
| 构建、运行、验证日常流程 | [docs/ROCM_WORKFLOW.md](docs/ROCM_WORKFLOW.md) | [docs/ROCM_WORKFLOW.zh-CN.md](docs/ROCM_WORKFLOW.zh-CN.md) |
| CPU vs ROCm 验证语义 | [docs/VALIDATION.md](docs/VALIDATION.md) | [docs/VALIDATION.zh-CN.md](docs/VALIDATION.zh-CN.md) |
| 后端模式与命名策略 | [docs/BACKEND_MODES_AND_NAMING.md](docs/BACKEND_MODES_AND_NAMING.md) | [docs/BACKEND_MODES_AND_NAMING.zh-CN.md](docs/BACKEND_MODES_AND_NAMING.zh-CN.md) |
| CUDA 到 ROCm 迁移案例 | [docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md](docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) | [docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md](docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) |
| ROCm porting 指南 | [docs/ROCM_PORTING_GUIDE.md](docs/ROCM_PORTING_GUIDE.md) | [docs/ROCM_PORTING_GUIDE.zh-CN.md](docs/ROCM_PORTING_GUIDE.zh-CN.md) |
| ROCm profiling 记录 | [docs/ROCM_PROFILING_NOTES.md](docs/ROCM_PROFILING_NOTES.md) | [docs/ROCM_PROFILING_NOTES.zh-CN.md](docs/ROCM_PROFILING_NOTES.zh-CN.md) |
| ROCm tuning 历史 | [docs/ROCM_TUNING_HISTORY.md](docs/ROCM_TUNING_HISTORY.md) | [docs/ROCM_TUNING_HISTORY.zh-CN.md](docs/ROCM_TUNING_HISTORY.zh-CN.md) |
| ROCm tuning 指南 | [docs/TUNING_GUIDE_ROCM.md](docs/TUNING_GUIDE_ROCM.md) | [docs/TUNING_GUIDE_ROCM.zh-CN.md](docs/TUNING_GUIDE_ROCM.zh-CN.md) |
| Netlib 跨设备 benchmark | [docs/CROSS_DEVICE_BENCHMARKS.md](docs/CROSS_DEVICE_BENCHMARKS.md) | [docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md](docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md) |
| large MPS benchmark 计划 | [docs/LARGE_MPS_BENCHMARK_PLAN.md](docs/LARGE_MPS_BENCHMARK_PLAN.md) | [docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md](docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md) |
| greenbea 数值行为 | [docs/NUMERICAL_BEHAVIOR_GREENBEA.md](docs/NUMERICAL_BEHAVIOR_GREENBEA.md) | [docs/NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md](docs/NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md) |
| W7900 / `gfx1100` current status | [docs/W7900_CURRENT_STATUS.md](docs/W7900_CURRENT_STATUS.md) | [docs/W7900_CURRENT_STATUS.zh-CN.md](docs/W7900_CURRENT_STATUS.zh-CN.md) |
| W7900 / `gfx1100` first-port 记录 | [docs/W7900_FIRST_PORT.md](docs/W7900_FIRST_PORT.md) | [docs/W7900_FIRST_PORT.zh-CN.md](docs/W7900_FIRST_PORT.zh-CN.md) |
| 上游参考快照 | [README_UPSTREAM.md](README_UPSTREAM.md) | — |

`README_UPSTREAM.md` 是上游 README 备份，故意作为原始参考快照保留，不翻译、不重写。

## Benchmarks

原始 `.mps` 大文件不提交到 Git。仓库只提交整理后的 CSV 结果和解释文档。

| 主题 | English | 中文 | 原始结果 CSV |
|---|---|---|---|
| Large MPS CUDA/ROCm baseline | [summary](docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.md) | [中文版](docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.zh-CN.md) | [platform summary](results/benchmarks/large_mps_platform_summary_20260610.csv), [per-case timing](results/benchmarks/large_mps_per_case_timing_summary_20260610.csv) |
| cuPDLPx vs cuPDLP-C short13 | [comparison](docs/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.md) | [中文版](docs/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.zh-CN.md) | [comparison CSV](results/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.csv) |

## 本仓库提供什么

- CPU-only cuPDLP-C 构建路径。
- 上游兼容 CUDA 构建路径，用于 NVIDIA baseline。
- 由 CUDA backend 迁移而来的 ROCm/HIP backend。
- 链接 ROCm/HIP backend 的 `plc` 可执行文件。
- CPU-vs-ROCm smoke validation 脚本。
- W7900 / `gfx1100` build、smoke validation、Netlib validation、large-MPS baseline、P10 profiling、P11 SpMV tuning 和 P12 rejected experiment 记录。
- 扩展 Netlib 验证 case。
- RTX 3090、RTX 4090D、H100、Radeon 890M 的跨设备 benchmark 工作流与结果文档。
- large MPS benchmark 文档和整理后的 CSV 汇总。
- `rocprofv3` profiling 工作流与 ROCm tuning 笔记。
- 面向 CUDA 到 ROCm/HIP 科学计算项目迁移的案例文档。

## 后端模式

| 模式 | CMake 选项 | 作用 |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | 正确性与可移植性 baseline |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | 上游兼容 NVIDIA 后端与 benchmark baseline |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD Radeon ROCm/HIP 目标后端 |

`BUILD_CUDA` 和 `BUILD_ROCM` 不能同时开启。不同后端建议使用不同 build 目录，例如 `build-cpu`、`build-cuda`、`build-rocm-plc`。

## 当前验证与 benchmark 状态

Large MPS baseline 状态：

| 平台 | 后端 | 结果 |
|---|---|---|
| RTX 3090 | CUDA upstream | 25/26 OPTIMAL, 1/26 TIMELIMIT |
| Radeon 890M | ROCm/HIP baseline | 24/26 OPTIMAL, 2/26 TIMELIMIT |
| RTX 4090D | CUDA upstream | 26/26 OPTIMAL |
| H100 | CUDA upstream | 26/26 OPTIMAL |
| Radeon PRO W7900 | ROCm/HIP W7900 当前调优终点 | non-hard large-MPS 23/23 OPTIMAL；P10 profiling、P11 SpMV tuning、P12 rejected experiment 已归档 |

cuPDLPx short13 对比状态：

| Solver | 平台 | 结果 |
|---|---|---|
| cuPDLP-C upstream | RTX 4090D CUDA | 选定 13 个短/中等 case 上 13/13 OPTIMAL |
| cuPDLPx v0.2.9 | RTX 4090D CUDA | 同一批 case 上 13/13 OPTIMAL |

## 快速开始：构建 ROCm/HIP 版本

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

运行 smoke example：

```bash
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_sum.json \
  -nIterLim 200
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

整理后的验证结果和 CSV 见 [validation/README.zh-CN.md](validation/README.zh-CN.md)。

## Profiling 与 tuning

```bash
RESULT_ROOT=profiling/results/current ./scripts/profile_rocm_smoke.sh

python3 scripts/summarize_rocm_profile.py \
  --input profiling/results/current \
  --output profiling/results/current/profile_summary.md
```

详见 [docs/ROCM_PROFILING_NOTES.zh-CN.md](docs/ROCM_PROFILING_NOTES.zh-CN.md)、[docs/ROCM_TUNING_HISTORY.zh-CN.md](docs/ROCM_TUNING_HISTORY.zh-CN.md)、[docs/TUNING_GUIDE_ROCM.zh-CN.md](docs/TUNING_GUIDE_ROCM.zh-CN.md)。

## 适配其他 ROCm GPU

先识别 GPU 架构：

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
```

然后设置对应架构，例如 W7900/gfx1100：

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1100
```

实际支持取决于 ROCm 版本、Linux 发行版、内核和 AMD GPU/APU 支持状态。

## W7900 项目最终状态 / 2026-06-17

当前仓库范围内，W7900 / `gfx1100` 阶段已经完成。该分支已经不再停留在
first-port 或 baseline 文档阶段：

- W7900 ROCm build、smoke validation、Netlib validation、large-MPS baseline、
  targeted profiling 和 P11 SpMV tuning 均已完成。
- P10 targeted profiling 确认 rocSPARSE/hipSPARSE CSR SpMV 是所选 W7900
  case 上的主要 GPU kernel 热点。
- P11 增加 opt-in HIP SpMV algorithm switch，并验证了 `csr_alg2`、
  `default`、`csr_alg1` 三种模式。
- 当前 W7900 默认 SpMV algorithm 已设为
  `HIPSPARSE_SPMV_CSR_ALG1`。
- 旧默认仍可通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 显式恢复。
- 这是 W7900-specific 当前默认调优策略，不是最终跨平台峰值性能结论。

W7900 当前权威入口见：

- `docs/W7900_CURRENT_STATUS.zh-CN.md`
- `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`

## W7900 最终终点 / 2026-06-17

当前仓库范围内，W7900 / `gfx1100` 阶段已经完成。它不应再被描述为未来目标、
baseline-only 目标或 pre-tuning 目标。

当前已接受终点：

- W7900 build、smoke validation、Netlib validation 和 large-MPS baseline
  文档已完成。
- P10 targeted rocprof profiling 已完成。
- P11 SpMV tuning 已完成。
- 当前 W7900 默认 SpMV algorithm：
  `HIPSPARSE_SPMV_CSR_ALG1`。
- 回退旧默认：
  `CUPDLP_HIP_SPMV_ALG=csr_alg2`。
- P12 记录了一次被拒绝的 SpMV buffer-algorithm consistency 实验；该实验导致
  迭代数变化，因此未接受该 patch。

权威入口：

- `docs/W7900_CURRENT_STATUS.zh-CN.md`
- `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`
- `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md`

## P14-A1 后的 W7900 最终验证终点 / 2026-06-18

当前项目终点不再需要继续补实验。

W7900 最终证据链：

- W7900 build、smoke validation、Netlib validation 和 large-MPS baseline 已归档。
- P10 targeted rocprof profiling 已归档。
- P11 SpMV tuning 已归档；当前默认 SpMV algorithm 为 `HIPSPARSE_SPMV_CSR_ALG1`。
- P12 记录了被拒绝的 SpMV buffer-algorithm consistency 实验。
- P14-A1 补充了 quick6 current-vs-pre_tuning repeated validation。

P14-A1 结果：

- `current` 在 quick6 的 `6/6` 个 case 上快于 `pre_tuning`。
- 几何平均 speedup：`1.18889`。
- 中位数 speedup：`1.19502`。
- pre/current 迭代数保持一致。

P14-B CSR ALG1-vs-ALG2 repeated validation 不再是当前收尾 blocker。它可以保留为未来可选稳健性检查，但当前项目闭环不再需要继续补实验。

见 [P14-A1 quick6 中文汇总](validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md)。

## P14-A1 后的最终补充验证 / 2026-06-18

W7900 已补充 P14-A1 quick6 current-vs-pre_tuning repeated validation。结果显示
`current` 在 quick6 的 `6/6` 个 case 上快于 `pre_tuning`，几何平均 speedup 为
`1.18889`，中位数 speedup 为 `1.19502`，且 pre/current 迭代数保持一致。

这作为 quick-set tuning-transfer evidence，与 non-hard23 large-MPS baseline 分开表述。当前项目收尾不再需要额外 W7900 实验；P14-B 仅保留为未来可选稳健性检查。
