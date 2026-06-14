#!/usr/bin/env python3
from pathlib import Path
import html

BLOCK_BEGIN = "<!-- W7900_OPTIMIZATION_BASELINES_20260614_BEGIN -->"
BLOCK_END = "<!-- W7900_OPTIMIZATION_BASELINES_20260614_END -->"

DOC_EN = Path("docs/W7900_OPTIMIZATION_BASELINES.md")
DOC_ZH = Path("docs/W7900_OPTIMIZATION_BASELINES.zh-CN.md")
TIMELINE = Path("docs/assets/w7900/rocm_tuning_milestone_timeline.svg")
CASE_LIST = Path("validation/cases_w7900_large_mps_before_after_core6.txt")

MILESTONES = [
    ("pre_tuning", "ae3b683", "Add ROCm profiling summary script", "true first-runnable / pre-tuning anchor"),
    ("remove_sync", "f9d7f0d", "remove redundant HIP synchronize", "first synchronization cleanup"),
    ("cache_attrs", "8fed073", "cache HIP device attributes", "helper-level overhead cleanup"),
    ("fused_average", "fa7e860", "Fuse ROCm average iterate axpy updates", "average iterate update fusion"),
    ("reduce_scalar_copies", "b44c7ab", "Reduce movement interaction scalar copies", "fast historical tuning milestone"),
    ("current_engineering", "35a7a7b", "add W7900 ROCm profiling plan", "current post-890M-tuning engineering branch"),
]

CORE6 = [
    "set-cover-model.mps",
    "square41.mps",
    "s100.mps",
    "Primal2_1000.mps",
    "thk_48.mps",
    "tpl-tub-ws1617.mps",
]

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")
    print("[ok] wrote", path)

def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |"]
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for r in rows:
        out.append("| " + " | ".join(map(str, r)) + " |")
    return "\n".join(out)

def make_timeline():
    width, height = 1160, 340
    left, right, y = 80, 80, 150
    step = (width - left - right) / (len(MILESTONES) - 1)
    colors = {
        "pre_tuning": "#991b1b",
        "reduce_scalar_copies": "#1f4b99",
        "current_engineering": "#166534",
    }
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="34" text-anchor="middle" font-size="22" font-family="Arial, sans-serif" font-weight="700">ROCm/HIP tuning milestones and W7900 baseline wording</text>',
        f'<text x="{width/2}" y="60" text-anchor="middle" font-size="13" font-family="Arial, sans-serif" fill="#555">Current W7900 results are post-890M-tuning engineering baseline, not the original first-runnable ROCm baseline.</text>',
        f'<line x1="{left}" y1="{y}" x2="{width-right}" y2="{y}" stroke="#9ca3af" stroke-width="3"/>',
    ]
    for i, (name, commit, title, desc) in enumerate(MILESTONES):
        x = left + i * step
        c = colors.get(name, "#4b5563")
        p.append(f'<circle cx="{x:.1f}" cy="{y}" r="10" fill="{c}"/>')
        p.append(f'<text x="{x:.1f}" y="{y-26}" text-anchor="middle" font-size="13" font-family="Arial, sans-serif" font-weight="700">{html.escape(name)}</text>')
        p.append(f'<text x="{x:.1f}" y="{y+34}" text-anchor="middle" font-size="12" font-family="Arial, sans-serif">{html.escape(commit)}</text>')
        short = title if len(title) <= 44 else title[:41] + "..."
        p.append(f'<text x="{x:.1f}" y="{y+54}" text-anchor="middle" font-size="11" font-family="Arial, sans-serif" fill="#555">{html.escape(short)}</text>')
    p.append('<text x="80" y="300" font-size="12" font-family="Arial, sans-serif" fill="#555">Red = true before anchor; blue = fast historical tuning milestone; green = current W7900 engineering branch.</text>')
    p.append("</svg>")
    write(TIMELINE, "\n".join(p))

def doc_en():
    rows = [[a,b,c,d] for a,b,c,d in MILESTONES]
    core_rows = [
        ["set-cover-model.mps", "fast representative; overhead/kernel-dispatch analysis"],
        ["square41.mps", "competitive W7900 case"],
        ["s100.mps", "slow-but-solvable; iteration-count sensitive"],
        ["Primal2_1000.mps", "near-optimal at 900s and OPTIMAL under 1800s"],
        ["thk_48.mps", "medium/large representative"],
        ["tpl-tub-ws1617.mps", "large representative for cross-device comparison"],
    ]
    return f'''# W7900 optimization baselines

> 中文: [W7900_OPTIMIZATION_BASELINES.zh-CN.md](W7900_OPTIMIZATION_BASELINES.zh-CN.md)

This document corrects the baseline wording for W7900 / `gfx1100`.

The current W7900 large-MPS `non-hard23` result is **not** an unoptimized first-port baseline. It is a W7900 validation of the current ROCm/HIP engineering branch, and that branch already inherits the earlier Radeon 890M / `gfx1150` tuning work.

## Required wording

Use this wording in reports:

```text
The W7900 non-hard23 baseline is the current post-890M-tuning engineering baseline.
It is not the original first-runnable ROCm baseline.
```

## Milestone timeline

![ROCm tuning milestone timeline](assets/w7900/rocm_tuning_milestone_timeline.svg)

{md_table(["Milestone", "Commit", "Role", "Interpretation"], rows)}

## Evidence from the existing tuning history

The repository tuning history already states that `pre_tuning` is `ae3b683`, `reduce_scalar_copies` is `b44c7ab`, and the current branch is an engineering baseline because it keeps CPU/CUDA/ROCm three-mode compatibility. It also records that current improves over `pre_tuning` on the 6-case quick set, while `reduce_scalar_copies` is the fastest observed point for most quick-set cases.

Therefore, current W7900 data should be presented as **post-tuning engineering validation on W7900**, not as **before-tuning W7900 data**.

## Future before/after policy

| Role | Version | Purpose |
|---|---|---|
| Before | `pre_tuning` / `ae3b683` | true first-runnable/pre-tuning ROCm anchor |
| Current | `rocm-w7900-gfx1100` current HEAD | current post-890M-tuning W7900 engineering baseline |
| After | future W7900-specific tuning branch | final W7900-specific optimized result |

## Recommended first before/after subset

{md_table(["Case", "Reason"], core_rows)}

Run this core6 subset before attempting a full non-hard23 rerun. The full large-MPS non-hard23 rerun should be reserved for the true pre-tuning anchor if time permits, the final W7900-specific optimized branch, or major solver/kernel changes.

## Documentation policy

- Do not call current W7900 non-hard23 "unoptimized".
- Use `ae3b683` as the real before anchor.
- Use `current` as the engineering baseline.
- Use `reduce_scalar_copies` as a historical fast reference.
- Keep hard3 separate until convergence trajectory evidence is documented.
'''

def doc_zh():
    rows = [[a,b,c,d] for a,b,c,d in MILESTONES]
    core_rows = [
        ["set-cover-model.mps", "fast representative；分析 overhead / kernel dispatch"],
        ["square41.mps", "W7900 competitive case"],
        ["s100.mps", "slow-but-solvable；迭代次数敏感"],
        ["Primal2_1000.mps", "900s near-optimal，1800s 内 OPTIMAL"],
        ["thk_48.mps", "中大型代表 case"],
        ["tpl-tub-ws1617.mps", "适合跨设备比较的 large representative"],
    ]
    return f'''# W7900 优化基线说明

> English: [W7900_OPTIMIZATION_BASELINES.md](W7900_OPTIMIZATION_BASELINES.md)

本文修正 W7900 / `gfx1100` 当前结果的 baseline 口径。

当前 W7900 large-MPS `non-hard23` 结果**不是**未优化 first-port baseline。它是 current ROCm/HIP 工程分支在 W7900 上的验证结果，而该分支已经继承了此前 Radeon 890M / `gfx1150` 的调优成果。

## 必须采用的表述

后续报告中建议这样写：

```text
The W7900 non-hard23 baseline is the current post-890M-tuning engineering baseline.
It is not the original first-runnable ROCm baseline.
```

中文表述：

```text
当前 W7900 non-hard23 结果是继承 890M/gfx1150 调优成果后的 current engineering baseline，
不是最初只跑通、未调优的 ROCm baseline。
```

## Milestone 时间线

![ROCm tuning milestone timeline](assets/w7900/rocm_tuning_milestone_timeline.svg)

{md_table(["Milestone", "Commit", "作用", "解释"], rows)}

## 现有 tuning history 证据

已有 tuning history 已经说明：`pre_tuning` 是 `ae3b683`，`reduce_scalar_copies` 是 `b44c7ab`，current branch 是保留 CPU/CUDA/ROCm 三模态兼容的工程 baseline。它还记录了 current 相对 `pre_tuning` 在 6-case quick set 上有提升，而 `reduce_scalar_copies` 是多数 quick-set case 上观察到的最快 milestone。

因此，当前 W7900 数据应表述为 **post-tuning engineering validation on W7900**，而不是 **before-tuning W7900 data**。

## 后续 before/after 策略

| 角色 | 版本 | 目的 |
|---|---|---|
| Before | `pre_tuning` / `ae3b683` | 真正 first-runnable / pre-tuning ROCm anchor |
| Current | `rocm-w7900-gfx1100` current HEAD | 当前 post-890M-tuning W7900 engineering baseline |
| After | future W7900-specific tuning branch | 最终 W7900-specific optimized result |

## 建议第一组 before/after 子集

{md_table(["Case", "原因"], core_rows)}

先跑这个 core6 子集，不要一开始就重跑完整 non-hard23。完整 large-MPS non-hard23 rerun 应保留给真正 pre-tuning anchor、最终 W7900-specific optimized branch，或重大 solver/kernel 改动后。

## 文档口径策略

- 不要把 current W7900 non-hard23 称为“未优化”。
- 使用 `ae3b683` 作为真正 before anchor。
- 使用 current 作为 engineering baseline。
- 使用 `reduce_scalar_copies` 作为历史最快参考点。
- hard3 在收敛轨迹证据完成前继续单独分组。
'''

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
    for a in anchors:
        if a in s:
            p.write_text(s.replace(a, block.rstrip() + "\n\n" + a, 1))
            print("[ok] inserted block in", path)
            return
    p.write_text(s.rstrip() + "\n\n" + block.rstrip() + "\n")
    print("[ok] appended block in", path)

def update_docs():
    docs_block = f'''{BLOCK_BEGIN}
| W7900 optimization baselines / W7900 优化基线 | [W7900_OPTIMIZATION_BASELINES.md](W7900_OPTIMIZATION_BASELINES.md) | [W7900_OPTIMIZATION_BASELINES.zh-CN.md](W7900_OPTIMIZATION_BASELINES.zh-CN.md) | Clarifies `ae3b683` pre-tuning, `b44c7ab` reduce-scalar-copies, current engineering baseline, and future before/after policy |
{BLOCK_END}'''
    insert_or_replace("docs/README.md", docs_block, ["| W7900 ROCm profiling plan / W7900 ROCm profiling 计划", "| W7900 performance behavior / W7900 性能行为分析"])

    status_en = f'''{BLOCK_BEGIN}
## Optimization baseline interpretation

The current W7900 non-hard23 result is not an unoptimized first-port baseline. It is a validation of the current post-890M-tuning ROCm/HIP engineering branch on W7900 / `gfx1100`.

See [W7900 optimization baselines](W7900_OPTIMIZATION_BASELINES.md).
{BLOCK_END}'''
    insert_or_replace("docs/W7900_CURRENT_STATUS.md", status_en, ["## ROCm profiling and tuning plan", "## Current status"])

    status_zh = f'''{BLOCK_BEGIN}
## 优化基线口径说明

当前 W7900 non-hard23 结果不是未优化 first-port baseline，而是继承 890M/gfx1150 调优成果后的 current ROCm/HIP 工程分支在 W7900 / `gfx1100` 上的验证。

详见 [W7900 优化基线说明](W7900_OPTIMIZATION_BASELINES.zh-CN.md)。
{BLOCK_END}'''
    insert_or_replace("docs/W7900_CURRENT_STATUS.zh-CN.md", status_zh, ["## ROCm profiling 与调优计划", "## 当前状态"])

    perf_en = f'''{BLOCK_BEGIN}
## Baseline wording correction

The W7900 non-hard23 result should be read as a post-890M-tuning engineering baseline. It should not be used as the "before tuning" baseline in future before/after analysis. The true pre-tuning anchor is `ae3b683`.

See [W7900 optimization baselines](W7900_OPTIMIZATION_BASELINES.md).
{BLOCK_END}'''
    insert_or_replace("docs/W7900_PERFORMANCE_BEHAVIOR.md", perf_en, ["## Tuning implication", "## Hardware and solver interpretation"])

    perf_zh = f'''{BLOCK_BEGIN}
## Baseline 口径修正

W7900 non-hard23 结果应理解为 post-890M-tuning engineering baseline，不应作为未来 before/after 分析里的“调优前 baseline”。真正的 pre-tuning anchor 是 `ae3b683`。

详见 [W7900 优化基线说明](W7900_OPTIMIZATION_BASELINES.zh-CN.md)。
{BLOCK_END}'''
    insert_or_replace("docs/W7900_PERFORMANCE_BEHAVIOR.zh-CN.md", perf_zh, ["## 对调优的启示", "## 硬件与求解器解释"])

    plan_en = f'''{BLOCK_BEGIN}
## Baseline correction for future profiling

The current W7900 branch has already inherited earlier 890M/gfx1150 ROCm tuning. Future profiling should therefore distinguish `ae3b683` as the true pre-tuning anchor, current W7900 as the post-890M-tuning engineering baseline, and a future W7900-specific tuning branch as the final after-tuning result.

See [W7900 optimization baselines](W7900_OPTIMIZATION_BASELINES.md).
{BLOCK_END}'''
    insert_or_replace("docs/W7900_ROCM_PROFILING_PLAN.md", plan_en, ["## Current baseline state", "## Profiling case matrix"])

    plan_zh = f'''{BLOCK_BEGIN}
## 后续 profiling 的 baseline 口径修正

当前 W7900 分支已经继承此前 890M/gfx1150 ROCm tuning。后续 profiling 应区分：`ae3b683` 作为真正 pre-tuning anchor，current W7900 作为 post-890M-tuning engineering baseline，future W7900-specific tuning branch 作为最终 after-tuning 结果。

详见 [W7900 优化基线说明](W7900_OPTIMIZATION_BASELINES.zh-CN.md)。
{BLOCK_END}'''
    insert_or_replace("docs/W7900_ROCM_PROFILING_PLAN.zh-CN.md", plan_zh, ["## 当前 baseline 状态", "## Profiling case matrix"])

def main():
    make_timeline()
    write(DOC_EN, doc_en())
    write(DOC_ZH, doc_zh())
    CASE_LIST.parent.mkdir(parents=True, exist_ok=True)
    CASE_LIST.write_text("\n".join(CORE6) + "\n")
    print("[ok] wrote", CASE_LIST)
    update_docs()
    print("[done] generated W7900 optimization baseline documentation")

if __name__ == "__main__":
    main()
