#!/usr/bin/env python3
from pathlib import Path

BLOCK_BEGIN = "<!-- COMPETITION_README_20260614_BEGIN -->"
BLOCK_END = "<!-- COMPETITION_README_20260614_END -->"

COMP_EN = Path("docs/COMPETITION_README.md")
COMP_ZH = Path("docs/COMPETITION_README.zh-CN.md")

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")
    print("[ok] wrote", path)

def insert_or_replace(path, block, anchors):
    p = Path(path)
    if not p.exists():
        print("[skip] missing", path)
        return
    s = p.read_text()
    if BLOCK_BEGIN in s and BLOCK_END in s:
        before = s.split(BLOCK_BEGIN)[0].rstrip()
        after = s.split(BLOCK_END, 1)[1].lstrip()
        p.write_text(before + "\n\n" + block.rstrip() + "\n\n" + after)
        print("[ok] replaced block in", path)
        return
    for anchor in anchors:
        if anchor in s:
            p.write_text(s.replace(anchor, block.rstrip() + "\n\n" + anchor, 1))
            print("[ok] inserted block in", path)
            return
    p.write_text(s.rstrip() + "\n\n" + block.rstrip() + "\n")
    print("[ok] appended block in", path)

def doc_en():
    return """# Competition README: ROCm-enabled large-scale LP solver on Radeon GPUs

> 中文: [COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md)

This is the reviewer-facing entry point for the AMD ROCm / Radeon contest track.

## Project title

**ROCm-enabled Large-scale Linear Programming Solver Migration, Validation, and Profiling on AMD Radeon GPUs**

## Problem background and challenge

Large-scale linear programming is a scientific-computing and operations-research workload. cuPDLP/PDLP-style solvers repeatedly use sparse matrix-vector products, vector updates, reductions, and numerical convergence checks. The upstream project is CUDA-oriented, so the challenge is to migrate the solver to AMD ROCm/HIP while preserving correctness, reproducibility, and cross-device comparability.

## Target platforms

| Platform | Role |
|---|---|
| Radeon 890M / `gfx1150` | First ROCm/HIP migration, tuning history, and baseline validation |
| Radeon PRO W7900 / `gfx1100` | Large-MPS workstation GPU validation and future W7900-specific profiling/tuning |
| RTX 3090 / RTX 4090D / H100 | CUDA reference devices for cross-device comparison |

## Implementation summary

| Area | Repository evidence |
|---|---|
| ROCm/HIP migration | HIP backend, ROCm build workflow, CUDA/ROCm compatibility fixes |
| Validation | smoke, Netlib, large-MPS case lists, parsed CSV summaries |
| Benchmarking | 890M, W7900, 3090, 4090D, and H100 reference data |
| W7900 status | [W7900 current status](W7900_CURRENT_STATUS.md) |
| Performance analysis | [W7900 performance behavior](W7900_PERFORMANCE_BEHAVIOR.md) |
| Optimization baseline | [W7900 optimization baselines](W7900_OPTIMIZATION_BASELINES.md) |
| Profiling plan | [W7900 ROCm profiling plan](W7900_ROCM_PROFILING_PLAN.md) |
| Validation index | [validation README](../validation/README.md) |

## Current W7900 results

The W7900 branch is no longer only a first-port smoke experiment. It has:

- W7900 smoke validation;
- W7900 Netlib 27-case validation;
- W7900 large-MPS `initial17_safe`;
- W7900 large-MPS `watchlist6` and `near_optimal2`;
- W7900 large-MPS `non-hard23`: 23/23 `OPTIMAL`;
- hard3 split: `dlr1.mps`, `Dual2_5000.mps`, `fhnw-binschedule1.mps`.

| Metric | Value |
|---|---|
| W7900 non-hard23 cases | 23 |
| Termination | 23/23 `OPTIMAL` |
| Total wall time | 2960.171 s |
| Total solve time | 2742.940 s |
| Current status | post-890M-tuning engineering baseline |

## Important baseline correction

The current W7900 non-hard23 result is **not** an unoptimized first-port baseline. It is the current post-890M-tuning engineering baseline.

| Role | Version | Purpose |
|---|---|---|
| Before | `ae3b683` / `pre_tuning` | true first-runnable ROCm anchor |
| Current | current `rocm-w7900-gfx1100` | post-890M-tuning W7900 engineering baseline |
| After | future W7900-specific tuning branch | final W7900-specific optimized result |

## Performance interpretation

The project uses both aggregate and per-case analysis. Aggregate time is useful, but W7900 competitiveness is clearer at the per-case level. The core interpretation is:

```text
total time ≈ per-iteration cost × number of iterations
```

W7900 can be strong on large, bandwidth-sensitive, SpMV/vector-operation-heavy cases with stable convergence. Slow cases such as `s100` and `Primal2_1000` should be explained through iteration count and gap trajectory as well as kernel performance.

## Next planned work

1. Run W7900 `rocprofv3` starter3 profiling on `set-cover-model`, `square41`, and `s100`.
2. Record wall time, solver time, `DeviceMatVecProdTime`, `nIter`, HIP/kernel trace, and GPU telemetry.
3. Run hard3 short probes for `dlr1` and `fhnw-binschedule1`.
4. Run true before/current comparison on the core6 list using `ae3b683` vs current.
5. Perform W7900-specific tuning only after profiling results identify bottlenecks.

## Submission-material mapping

| Competition material | Repository status |
|---|---|
| Technical paper | to be built from this README, performance behavior, tuning history, and profiling results |
| Demo PPT | to be created after first profiling results |
| Demo video | should show build, validation, charts, and profiling workflow |
| Engineering repository | current repository with scripts, validation CSVs, Markdown summaries, SVG charts |
| Reproducibility | bootstrap scripts exist; dedicated reproducibility document is next |
"""

def doc_zh():
    return """# 竞赛入口文档：基于 Radeon GPU 的 ROCm 大规模线性规划求解器迁移与性能分析

> English: [COMPETITION_README.md](COMPETITION_README.md)

本文是 AMD ROCm / Radeon 赛题方向的评委入口文档。

## 项目题目

**基于 AMD ROCm 与 Radeon GPU 的大规模线性规划求解器迁移、验证与性能分析**

## 项目背景与挑战

大规模线性规划是典型科研计算和运筹优化工作负载。cuPDLP/PDLP 类求解器反复使用稀疏矩阵向量乘、向量更新、归约和数值收敛判断。上游项目主要面向 CUDA，因此本项目的挑战是将求解器迁移到 AMD ROCm/HIP，同时保持正确性、可复现性和跨设备可比较性。

## 目标平台

| 平台 | 作用 |
|---|---|
| Radeon 890M / `gfx1150` | ROCm/HIP 首轮迁移、调优历史和 baseline 验证 |
| Radeon PRO W7900 / `gfx1100` | large-MPS 工作站 GPU 验证和后续 W7900-specific profiling/tuning |
| RTX 3090 / RTX 4090D / H100 | CUDA 跨设备参考 |

## 方案与实现

| 方向 | 仓库证据 |
|---|---|
| ROCm/HIP 迁移 | HIP backend、ROCm build workflow、CUDA/ROCm compatibility fixes |
| 验证 | smoke、Netlib、large-MPS case lists、parsed CSV summaries |
| Benchmark | 890M、W7900、3090、4090D、H100 reference data |
| W7900 当前状态 | [W7900 当前状态](W7900_CURRENT_STATUS.zh-CN.md) |
| 性能分析 | [W7900 性能行为分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md) |
| 优化基线 | [W7900 优化基线说明](W7900_OPTIMIZATION_BASELINES.zh-CN.md) |
| Profiling 计划 | [W7900 ROCm profiling 计划](W7900_ROCM_PROFILING_PLAN.zh-CN.md) |
| Validation 索引 | [validation README](../validation/README.zh-CN.md) |

## 当前 W7900 成果

W7900 分支已经不再只是 first-port smoke 实验。目前已有：

- W7900 smoke validation；
- W7900 Netlib 27-case validation；
- W7900 large-MPS `initial17_safe`；
- W7900 large-MPS `watchlist6` 和 `near_optimal2`；
- W7900 large-MPS `non-hard23`：23/23 `OPTIMAL`；
- hard3 拆分：`dlr1.mps`、`Dual2_5000.mps`、`fhnw-binschedule1.mps`。

| 指标 | 数值 |
|---|---|
| W7900 non-hard23 cases | 23 |
| Termination | 23/23 `OPTIMAL` |
| Total wall time | 2960.171 s |
| Total solve time | 2742.940 s |
| 当前状态 | post-890M-tuning engineering baseline |

## 重要基线修正

当前 W7900 non-hard23 结果**不是**未优化 first-port baseline，而是 current post-890M-tuning engineering baseline。

| 角色 | 版本 | 目的 |
|---|---|---|
| Before | `ae3b683` / `pre_tuning` | 真正 first-runnable ROCm anchor |
| Current | current `rocm-w7900-gfx1100` | post-890M-tuning W7900 engineering baseline |
| After | future W7900-specific tuning branch | 最终 W7900-specific optimized result |

## 性能解释

项目同时使用 aggregate 和 per-case 分析。aggregate time 有价值，但 W7900 的竞争力在 per-case 层面更清楚。核心解释是：

```text
total time ≈ per-iteration cost × number of iterations
```

W7900 更适合规模足够大、带宽敏感、SpMV/向量操作占比较高且收敛稳定的 case。`s100`、`Primal2_1000` 等慢 case 应结合迭代次数、gap trajectory 和 kernel performance 一起解释。

## 下一步计划

1. 在 `set-cover-model`、`square41`、`s100` 上运行 W7900 `rocprofv3` starter3 profiling。
2. 记录 wall time、solver time、`DeviceMatVecProdTime`、`nIter`、HIP/kernel trace 和 GPU telemetry。
3. 对 `dlr1`、`fhnw-binschedule1` 运行 hard3 short probes。
4. 使用 `ae3b683` vs current 跑 core6 true before/current comparison。
5. profiling 结果定位瓶颈后再做 W7900-specific tuning。

## 提交材料映射

| 竞赛材料 | 仓库当前状态 |
|---|---|
| 技术论文 | 可基于本文、performance behavior、tuning history、profiling results 撰写 |
| 演示说明 PPT | 第一轮 profiling 结果完成后制作 |
| 演示视频 | 展示 build、validation、charts 和 profiling workflow |
| 工程代码仓库 | 当前仓库已有 scripts、validation CSV、Markdown summaries、SVG charts |
| 可复现性 | 已有 bootstrap scripts；下一步补 dedicated reproducibility document |
"""

def update_indexes():
    top = f"""{BLOCK_BEGIN}
> AMD ROCm/Radeon contest reviewers: start from [docs/COMPETITION_README.md](docs/COMPETITION_README.md) / [docs/COMPETITION_README.zh-CN.md](docs/COMPETITION_README.zh-CN.md).
{BLOCK_END}"""
    insert_or_replace("README.md", top, ["# cuPDLP-C ROCm/HIP Port", "# cuPDLP-C"])
    insert_or_replace("README.zh-CN.md", top, ["# cuPDLP-C ROCm/HIP Port", "# cuPDLP-C"])

    docs_block = f"""{BLOCK_BEGIN}
| Competition README / 竞赛入口 | [COMPETITION_README.md](COMPETITION_README.md) | [COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md) | Reviewer-facing entry point aligned with the AMD ROCm/Radeon contest track |
{BLOCK_END}"""
    insert_or_replace("docs/README.md", docs_block, ["## Main entry points / 主入口", "| W7900 optimization baselines / W7900 优化基线"])

def main():
    write(COMP_EN, doc_en())
    write(COMP_ZH, doc_zh())
    update_indexes()
    print("[done] competition README generated")

if __name__ == "__main__":
    main()
