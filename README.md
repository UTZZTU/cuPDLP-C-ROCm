# cuPDLP-C-ROCm

> English: [README.en.md](README.en.md)
> 文档地图：[docs/README.md](docs/README.md)
> 最终 W7900 结果：[docs/W7900_FINAL_RESULTS_20260729.zh-CN.md](docs/W7900_FINAL_RESULTS_20260729.zh-CN.md)
> 最终复现指南：[docs/FINAL_REPRODUCTION_GUIDE.zh-CN.md](docs/FINAL_REPRODUCTION_GUIDE.zh-CN.md)

`cuPDLP-C-ROCm` 是上游 [cuPDLP-C](README_UPSTREAM.md) 的 ROCm/HIP
移植、验证与性能分析分支。项目保留 CPU 与上游兼容 CUDA 路径，并新增
AMD GPU 后端。项目贡献是科学计算求解器迁移、数值验证、性能剖析和
证据链工程，不是提出新的线性规划算法。

## 最终发布状态

| 项目 | 最终状态 |
|---|---|
| 默认分支 | `rocm-w7900-gfx1100` |
| 冻结求解器源码 | `735764807d8698ff30811d1a6fcc45d4a3fd4817` |
| 正式实验 harness | `b5b9a6ffc1a041a48a0e051568d0134a3822556c` |
| 主要 ROCm 平台 | Radeon PRO W7900 / `gfx1100` |
| 正式 W7900 实验 | **76/76 `VALIDATED_OPTIMAL`** |
| 最终证据状态 | `FORMAL_W7900_EXPERIMENTS_COMPLETE`、`FINAL_ANALYSIS_RELEASED` |
| 发布属性 | 研究与工程验证项目；不是生产级通用求解器发行版 |

求解器源码边界固定在 `CMakeLists.txt`、`cmake/`、`cupdlp/` 和
`interface/`。最终 harness 提交只增加实验、验证和归档能力，不改变冻结
求解器源码。

## 正式 W7900 结果

| 证据 | 正式结果 | 口径 |
|---|---:|---|
| nonhard23 基线 | 23 例 × 2 次，46/46 验证通过 | 单卡、顺序独立 MPS |
| 两轮完整总时间 | 2950.626 s / 2950.675 s | 每轮完整 23 例 |
| 单卡吞吐 | 28.061842 / 28.061379 cases/hour | 均值 **28.061611** |
| 精度敏感性 | 5 例 × 3 档 × 2 次，30/30 验证通过 | `1e-3`、`1e-4`、`1e-5` |
| Profiling | 5/5 `PASS` | 每例有 trace CSV 与 kernel trace |
| 静态结构分析 | 23/23 通过 | rows、columns、nnz、密度和不规则性 |
| 数值质量 | 30/30 实际误差不高于目标精度 | 最大 `error/tolerance=0.998079` |

主要发现：

- `s100`、`Primal2_1000`、`thk_63` 占完整基线总时间的
  **82.22%**，性能呈明显长尾；
- 23 例总时间 CV 中位数为 **0.377%**，
  **22/23** 低于 2%，23/23 两轮迭代数一致；
- 从 `1e-3` 收紧到 `1e-5`，五例总时间成本为
  **1.01×–
  4.01×**，
  迭代成本为
  **2.02×–
  11.58×**；
- `matrix_nnz` 与采样峰值显存的探索性 Spearman 相关系数为
  **0.882**；静态相关不代表因果。

完整数据、图和边界见
[最终结果页](docs/W7900_FINAL_RESULTS_20260729.zh-CN.md)。

## 快速检查最终证据

无需 W7900，也可以在普通 Linux 主机检查提交的 compact evidence：

```bash
python3 scripts/analysis/generate_final_w7900_release.py --check-only
bash scripts/verify_final_repository_release.sh
```

预期标志：

```text
FINAL_W7900_RELEASE_DATA_PASS
FINAL_REPOSITORY_RELEASE_PASS
```

重新生成正式图表：

```bash
python3 scripts/analysis/generate_final_w7900_release.py
```

## 构建与最小运行

### CPU

```bash
cmake -S . -B build-cpu -G Ninja   -DCMAKE_BUILD_TYPE=Release   -DBUILD_CUDA=OFF   -DBUILD_ROCM=OFF
cmake --build build-cpu -j"$(nproc)"
```

### W7900 / ROCm

在匹配的 W7900 环境中：

```bash
bash scripts/build_w7900_cpu.sh
bash scripts/build_w7900_rocm.sh
bash scripts/run_w7900_smoke.sh
```

完整 fresh-machine、数据集、mini gate、`baseline23`、`session2`、归档和
常见故障处理见
[最终复现指南](docs/FINAL_REPRODUCTION_GUIDE.zh-CN.md)。

## 结果与数据策略

Git 仓库提交：

- case lists、manifests 和 checksums；
- compact curated CSV/JSON；
- Markdown summaries；
- 小型 PNG/SVG；
- 验证、分析与复现脚本。

以下内容不进入 Git：

- 原始 MPS；
- raw profiler trace；
- 本地 build 和临时运行目录；
- Cookie、SSH key 或其他凭据。

## 重要边界

- 单卡吞吐表示顺序处理独立 MPS，不是单个 LP 的多 GPU 求解。
- 历史 8 卡 fast8 表示 8 个独立任务并发，不是分布式 LP 算法。
- precision 结论只覆盖五个代表实例。
- 静态相关是探索性关联，不证明因果。
- hard3 与 nonhard23 分开报告。
- Docker 文件是环境骨架，正式数字来自真实 W7900 主机。
- `presolve` 关闭是当前主要验证合同；nontrivial postsolve 和原变量恢复未
  纳入本轮正式验证。

## 文档入口

| 需求 | 文档 |
|---|---|
| 最终结果与结论 | [W7900 最终结果](docs/W7900_FINAL_RESULTS_20260729.zh-CN.md) |
| 当前权威状态 | [W7900 当前状态](docs/W7900_CURRENT_STATUS.zh-CN.md) |
| 最终复现 | [最终复现指南](docs/FINAL_REPRODUCTION_GUIDE.zh-CN.md) |
| 验证语义 | [验证说明](docs/VALIDATION.zh-CN.md) |
| 性能解释 | [性能行为](docs/W7900_PERFORMANCE_BEHAVIOR.zh-CN.md) |
| Profiling | [Profiling 记录](docs/ROCM_PROFILING_NOTES.zh-CN.md) |
| compact evidence | [最终 validation 包](validation/final_w7900_20260729/README.zh-CN.md) |
| 竞赛评审 | [竞赛入口](docs/COMPETITION_README.zh-CN.md) |
| 完整导航 | [文档地图](docs/README.md) |

## 上游与许可证

上游 README 快照见 [README_UPSTREAM.md](README_UPSTREAM.md)。除非相应
文件另有说明，本仓库遵循 [MIT License](LICENSE)。
