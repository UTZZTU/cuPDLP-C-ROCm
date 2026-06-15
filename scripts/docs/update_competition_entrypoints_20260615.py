from pathlib import Path

def replace_once(path, old, new):
    p = Path(path)
    s = p.read_text()
    if new in s:
        print(f"{path}: already updated")
        return
    if old not in s:
        raise SystemExit(f"{path}: anchor not found")
    p.write_text(s.replace(old, new, 1))
    print(f"{path}: updated")

def write_if_changed(path, content):
    p = Path(path)
    if p.exists() and p.read_text() == content:
        print(f"{path}: already up to date")
        return
    p.write_text(content)
    print(f"{path}: written")

# 1) README.md: make general project entry and contest entry coexist.
replace_once(
    "README.md",
    "> AMD ROCm/Radeon contest reviewers: start from [docs/COMPETITION_README.md](docs/COMPETITION_README.md) / [docs/COMPETITION_README.zh-CN.md](docs/COMPETITION_README.zh-CN.md).",
    "> General users: start from this README and the [documentation map](docs/README.md).\n"
    "> AMD ROCm/Radeon contest reviewers: see [docs/COMPETITION_README.md](docs/COMPETITION_README.md) / [docs/COMPETITION_README.zh-CN.md](docs/COMPETITION_README.zh-CN.md)."
)

# 2) README.zh-CN.md: same policy in Chinese.
replace_once(
    "README.zh-CN.md",
    "> AMD ROCm/Radeon contest reviewers: start from [docs/COMPETITION_README.md](docs/COMPETITION_README.md) / [docs/COMPETITION_README.zh-CN.md](docs/COMPETITION_README.zh-CN.md).",
    "> 普通 GitHub 读者：请从本 README 和 [文档地图](docs/README.md) 开始。\n"
    "> AMD ROCm/Radeon 赛题评委：请查看 [docs/COMPETITION_README.md](docs/COMPETITION_README.md) / [docs/COMPETITION_README.zh-CN.md](docs/COMPETITION_README.zh-CN.md)。"
)

# 3) COMPETITION_README.md: clarify that it is only a reviewer path.
replace_once(
    "docs/COMPETITION_README.md",
    "This is the reviewer-facing entry point for the AMD ROCm / Radeon contest track.",
    "This is a reviewer-oriented path through a general-purpose open-source ROCm/HIP migration and validation repository. It does not replace the general README; it only maps the project evidence to the AMD ROCm / Radeon contest track."
)

# 4) COMPETITION_README.zh-CN.md: Chinese counterpart.
replace_once(
    "docs/COMPETITION_README.zh-CN.md",
    "本文是 AMD ROCm / Radeon 赛题方向的评委入口文档。",
    "本文是通用 ROCm/HIP 迁移与验证开源仓库中的评审阅读路径，不替代通用 README；它只负责把项目证据映射到 AMD ROCm / Radeon 赛题要求。"
)

# 5) Add reader paths to docs/README.md without moving existing files.
docs_readme = Path("docs/README.md")
s = docs_readme.read_text()

reader_block = """## Reader paths / 读者路径

| Reader / 读者 | Start from / 建议入口 | Purpose / 用途 |
|---|---|---|
| General GitHub users / 普通 GitHub 读者 | [Repository README](../README.md) / [中文主页](../README.zh-CN.md) | Understand the project scope, backend modes, validation status, and quick-start workflow |
| ROCm migration developers / ROCm 迁移开发者 | [ROCm porting guide](ROCM_PORTING_GUIDE.md), [CUDA-to-ROCm case study](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md), [ROCM_WORKFLOW.md](ROCM_WORKFLOW.md) | Reuse the migration process, build workflow, and backend design notes |
| Validation and benchmark readers / 验证与 benchmark 读者 | [validation index](../validation/README.md), [benchmark index](benchmarks/README.md), [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | Check committed summaries, case lists, CSV files, and expected outputs |
| W7900 / gfx1100 readers | [W7900 current status](W7900_CURRENT_STATUS.md), [W7900 profiling plan](W7900_ROCM_PROFILING_PLAN.md), [W7900 optimization baselines](W7900_OPTIMIZATION_BASELINES.md) | Follow the W7900 validation, profiling, and before/current/after plan |
| AMD ROCm/Radeon contest reviewers / 赛题评委 | [COMPETITION_README.md](COMPETITION_README.md), [COMPETITION_SCORECARD.md](COMPETITION_SCORECARD.md) | Read the same project evidence through the contest scoring requirements |

"""

if "## Reader paths / 读者路径" not in s:
    anchor = "本页是项目维护文档的总索引，目的是避免文档存在但没有入口的问题。\n\n"
    if anchor in s:
        s = s.replace(anchor, anchor + reader_block, 1)
    else:
        # fallback: insert after the first heading
        lines = s.splitlines()
        if not lines or not lines[0].startswith("#"):
            raise SystemExit("docs/README.md: cannot find insertion point")
        s = lines[0] + "\n\n" + reader_block + "\n".join(lines[1:]) + "\n"
    docs_readme.write_text(s)
    print("docs/README.md: reader paths inserted")
else:
    print("docs/README.md: reader paths already exist")

scorecard_en = """# Competition scorecard alignment

> 中文: [COMPETITION_SCORECARD.zh-CN.md](COMPETITION_SCORECARD.zh-CN.md)

This page maps the AMD ROCm/Radeon contest requirements to repository evidence. It is a reviewer-oriented checklist, not the main project entry point. General users should start from [../README.md](../README.md) and [README.md](README.md).

## Scope

Project: ROCm/HIP migration, validation, benchmarking, and profiling of a large-scale linear programming solver on AMD Radeon-class GPUs.

Current status:

- Radeon 890M / `gfx1150`: first ROCm migration target, validation, and tuning history.
- Radeon PRO W7900 / `gfx1100`: workstation-class validation target with current non-hard large-MPS baseline.
- NVIDIA RTX 3090 / RTX 4090D / H100: CUDA reference devices for comparison.

## Scorecard

| Contest requirement | Repository evidence | Current status | Remaining work |
|---|---|---|---|
| Project background and challenge | [COMPETITION_README.md](COMPETITION_README.md), [CUDA-to-ROCm case study](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) | CUDA-oriented solver migrated toward ROCm/HIP; LP/HPC workload challenge documented | Technical paper should turn this into a concise narrative |
| Solution and implementation | HIP backend, [ROCM_WORKFLOW.md](ROCM_WORKFLOW.md), [ROCM_PORTING_GUIDE.md](ROCM_PORTING_GUIDE.md), README backend-mode section | CPU, CUDA, and ROCm backend modes are documented | Paper/PPT should include a module diagram and ROCm component map |
| ROCm component usage | HIP runtime, hipBLAS/hipSPARSE build path, `rocprofv3`/`rocprof` workflow, ROCm device architecture selection | ROCm/HIP build and profiling workflow are present | Add W7900 profiling result tables after the next W7900 run |
| Performance and resource analysis | [W7900 performance behavior](W7900_PERFORMANCE_BEHAVIOR.md), [ROCM tuning history](ROCM_TUNING_HISTORY.md), validation/benchmark CSVs | Current W7900 non-hard23 summary and cross-device references are committed | Need W7900 `rocprof` starter3 results, VRAM/telemetry, and before/current core6 comparison |
| Reproducibility and delivery | [REPRODUCIBILITY.md](REPRODUCIBILITY.md), validation case lists, scripts, curated CSV/Markdown summaries | Fresh W7900 recovery, data policy, expected outputs, and profiling workflow are documented | Dedicated Docker/Containerfile remains a final-submission work item |
| Functional completeness and code quality | Source tree, scripts, validation summaries, backend mode policy | Main solver path is buildable and validation-driven | Add more code-level comments only where needed; avoid cosmetic churn |
| Stage results and plan | [W7900 current status](W7900_CURRENT_STATUS.md), [W7900 optimization baselines](W7900_OPTIMIZATION_BASELINES.md), [W7900 profiling plan](W7900_ROCM_PROFILING_PLAN.md) | Current/before/after policy is explicit | Run W7900 profiling, hard3 probes, then W7900-specific tuning |
| Innovation add-on: unsupported functionality | ROCm/HIP backend adaptation of a CUDA-oriented scientific solver | Project demonstrates a non-trivial ROCm backend migration | External ROCm upstream PR is not yet claimed |
| Innovation add-on: bottleneck optimization | 890M tuning history and planned W7900 profiling | Prior ROCm optimization history is documented | W7900-specific bottleneck claims must wait for `rocprof` results |

## Current caution

The current W7900 non-hard23 result is a post-890M-tuning engineering baseline, not the true unoptimized first-runnable ROCm baseline. The true before/current comparison should use `ae3b683 / pre_tuning` versus current `rocm-w7900-gfx1100`.
"""

scorecard_zh = """# 竞赛评分项对照

> English: [COMPETITION_SCORECARD.md](COMPETITION_SCORECARD.md)

本文把 AMD ROCm/Radeon 赛题要求映射到仓库证据。它是评审视角的检查表，不是项目唯一入口。普通读者应先阅读 [../README.zh-CN.md](../README.zh-CN.md) 和 [README.md](README.md)。

## 范围

项目：在 AMD Radeon 类 GPU 上对大规模线性规划求解器进行 ROCm/HIP 迁移、验证、benchmark 与 profiling。

当前状态：

- Radeon 890M / `gfx1150`：首个 ROCm 迁移、验证与 tuning 历史平台。
- Radeon PRO W7900 / `gfx1100`：工作站级验证平台，已有 current non-hard large-MPS baseline。
- NVIDIA RTX 3090 / RTX 4090D / H100：CUDA 参考设备，用于跨设备对比。

## 评分项对照

| 赛题要求 | 仓库证据 | 当前状态 | 待补工作 |
|---|---|---|---|
| 项目背景与挑战 | [COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md)、[CUDA 到 ROCm 迁移案例](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) | 已说明 CUDA-oriented solver 向 ROCm/HIP 迁移的挑战，以及 LP/HPC 工作负载背景 | 技术论文中需压缩成更清晰的叙事 |
| 方案与实现 | HIP backend、[ROCM_WORKFLOW.zh-CN.md](ROCM_WORKFLOW.zh-CN.md)、[ROCM_PORTING_GUIDE.zh-CN.md](ROCM_PORTING_GUIDE.zh-CN.md)、README 后端模式说明 | 已记录 CPU、CUDA、ROCm 三种后端模式和构建流程 | 论文/PPT 中需要补模块图与 ROCm 组件映射图 |
| ROCm 组件使用 | HIP runtime、hipBLAS/hipSPARSE 构建路径、`rocprofv3`/`rocprof` workflow、ROCm device architecture 选择 | 已具备 ROCm/HIP 构建与 profiling workflow | 下次 W7900 实验后补 profiling 结果表 |
| 性能与资源分析 | [W7900 性能行为分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)、[ROCm tuning 历史](ROCM_TUNING_HISTORY.zh-CN.md)、validation/benchmark CSV | 已提交 W7900 non-hard23 summary 和跨设备参考数据 | 仍需 W7900 `rocprof` starter3、VRAM/telemetry、before/current core6 对比 |
| 复现与交付 | [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md)、validation case lists、scripts、curated CSV/Markdown summaries | 已写 fresh W7900 recovery、数据策略、期望输出和 profiling workflow | Dedicated Docker/Containerfile 仍是 final-submission work item |
| 功能完整性与代码质量 | 源码目录、scripts、validation summaries、backend mode policy | 主要求解路径已按 build/validation 驱动维护 | 只在必要位置补代码注释，避免无意义大改 |
| 阶段性成果与规划 | [W7900 当前状态](W7900_CURRENT_STATUS.zh-CN.md)、[W7900 优化基线](W7900_OPTIMIZATION_BASELINES.zh-CN.md)、[W7900 profiling 计划](W7900_ROCM_PROFILING_PLAN.zh-CN.md) | current/before/after 口径已明确 | 继续跑 W7900 profiling、hard3 probes，再做 W7900-specific tuning |
| 附加分：未支持功能开发 | CUDA-oriented 科学计算求解器的 ROCm/HIP 后端适配 | 已体现非平凡 ROCm 后端迁移 | 暂不声称已有 ROCm 上游 PR |
| 附加分：性能瓶颈定位与优化 | 890M tuning 历史与 W7900 profiling 计划 | 已记录此前 ROCm 优化历史 | W7900-specific bottleneck 结论必须等待 `rocprof` 实测结果 |

## 当前注意事项

当前 W7900 non-hard23 结果是继承 890M tuning 的工程基线，不是真正未优化 first-runnable ROCm baseline。正式 before/current 对比应使用 `ae3b683 / pre_tuning` 与当前 `rocm-w7900-gfx1100`。
"""

write_if_changed("docs/COMPETITION_SCORECARD.md", scorecard_en)
write_if_changed("docs/COMPETITION_SCORECARD.zh-CN.md", scorecard_zh)

# 6) Link scorecard from Competition README files.
replace_once(
    "docs/COMPETITION_README.md",
    "| Profiling plan | [W7900 ROCm profiling plan](W7900_ROCM_PROFILING_PLAN.md) |",
    "| Profiling plan | [W7900 ROCm profiling plan](W7900_ROCM_PROFILING_PLAN.md) |\n"
    "| Contest scorecard | [Competition scorecard alignment](COMPETITION_SCORECARD.md) |"
)

replace_once(
    "docs/COMPETITION_README.zh-CN.md",
    "| Profiling 计划 | [W7900 ROCm profiling 计划](W7900_ROCM_PROFILING_PLAN.zh-CN.md) |",
    "| Profiling 计划 | [W7900 ROCm profiling 计划](W7900_ROCM_PROFILING_PLAN.zh-CN.md) |\n"
    "| 评分项对照 | [竞赛评分项对照](COMPETITION_SCORECARD.zh-CN.md) |"
)

print("done")
