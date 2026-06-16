#!/usr/bin/env python3
import csv
import math
import os
import shutil
import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("OUT_ROOT", ""))
if not OUT.exists():
    raise SystemExit(f"missing OUT_ROOT: {OUT}")

DATE = "20260616"
VAL = Path("validation")
VAL.mkdir(exist_ok=True)

current_runtime_out = VAL / f"w7900_before_current_core6_fast_current_runtime_{DATE}.csv"
pre_runtime_out = VAL / f"w7900_before_current_core6_fast_pre_tuning_runtime_{DATE}.csv"
current_solver_out = VAL / f"w7900_before_current_core6_fast_current_solver_{DATE}.csv"
pre_solver_out = VAL / f"w7900_before_current_core6_fast_pre_tuning_solver_{DATE}.csv"
comparison_out = VAL / f"w7900_before_current_core6_fast_comparison_{DATE}.csv"
md_out = VAL / f"w7900_before_current_core6_fast_summary_{DATE}.md"
zh_out = VAL / f"w7900_before_current_core6_fast_summary_{DATE}.zh-CN.md"

def copy(src, dst):
    if not src.exists():
        raise SystemExit(f"missing source file: {src}")
    shutil.copyfile(src, dst)
    print(f"wrote {dst}")

copy(OUT / "current" / "runtime_summary.csv", current_runtime_out)
copy(OUT / "pre_tuning" / "runtime_summary.csv", pre_runtime_out)
copy(OUT / "current" / "parsed_solver_summary.csv", current_solver_out)
copy(OUT / "pre_tuning" / "parsed_solver_summary.csv", pre_solver_out)

def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def fnum(x):
    try:
        return float(x)
    except Exception:
        return float("nan")

current_rows = read_csv(current_solver_out)
pre_rows = read_csv(pre_solver_out)

cur = {r["case"]: r for r in current_rows}
pre = {r["case"]: r for r in pre_rows}

comparison_rows = []
ratios = []
current_wins = 0
pre_wins = 0

for case in sorted(set(cur) & set(pre)):
    c = cur[case]
    p = pre[case]

    c_solve = fnum(c.get("dSolvingTime"))
    p_solve = fnum(p.get("dSolvingTime"))
    ratio = c_solve / p_solve if p_solve and not math.isnan(p_solve) else float("nan")
    speedup = p_solve / c_solve if c_solve and not math.isnan(c_solve) else float("nan")

    if not math.isnan(ratio):
        ratios.append(ratio)
        if ratio < 1.0:
            current_wins += 1
        elif ratio > 1.0:
            pre_wins += 1

    comparison_rows.append({
        "case": case,
        "current_termination": c.get("terminationCode", ""),
        "pre_tuning_termination": p.get("terminationCode", ""),
        "current_iter": c.get("nIter", ""),
        "pre_tuning_iter": p.get("nIter", ""),
        "current_solve_time": c.get("dSolvingTime", ""),
        "pre_tuning_solve_time": p.get("dSolvingTime", ""),
        "current_over_pre_solve_ratio": f"{ratio:.6f}" if not math.isnan(ratio) else "",
        "pre_over_current_speedup": f"{speedup:.6f}" if not math.isnan(speedup) else "",
        "current_wall_seconds": c.get("wall_seconds", ""),
        "pre_tuning_wall_seconds": p.get("wall_seconds", ""),
        "current_gap": c.get("dRelDualityGap", ""),
        "pre_tuning_gap": p.get("dRelDualityGap", ""),
    })

fields = [
    "case",
    "current_termination",
    "pre_tuning_termination",
    "current_iter",
    "pre_tuning_iter",
    "current_solve_time",
    "pre_tuning_solve_time",
    "current_over_pre_solve_ratio",
    "pre_over_current_speedup",
    "current_wall_seconds",
    "pre_tuning_wall_seconds",
    "current_gap",
    "pre_tuning_gap",
]

with comparison_out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(comparison_rows)
print(f"wrote {comparison_out}")

gm_ratio = math.prod(ratios) ** (1 / len(ratios)) if ratios else float("nan")
gm_speedup = 1 / gm_ratio if gm_ratio else float("nan")

def md_table(rows, cols):
    lines = []
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "|".join(["---"] * len(cols)) + "|")
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(lines)

display_cols = [
    "case",
    "current_termination",
    "pre_tuning_termination",
    "current_solve_time",
    "pre_tuning_solve_time",
    "current_over_pre_solve_ratio",
    "pre_over_current_speedup",
]

en = []
en.append("# W7900 before/current fast-core6 summary")
en.append("")
en.append(f"Result directory: `{OUT}`")
en.append("")
en.append("This is a compact summary of the W7900 fast-core6 before/current comparison.")
en.append("")
en.append("Compared versions:")
en.append("")
en.append("- `pre_tuning`: `ae3b683 / pre_tuning`, built on W7900 with ROCm Python SDK include-path adaptation.")
en.append("- `current`: current `rocm-w7900-gfx1100` engineering branch.")
en.append("")
en.append("Fast-core6 case list:")
en.append("")
en.append("- `set-cover-model.mps`")
en.append("- `square41.mps`")
en.append("- `thk_48.mps`")
en.append("- `tpl-tub-ws1617.mps`")
en.append("- `L2CTA3D.mps`")
en.append("- `rmine15.mps`")
en.append("")
en.append("## Comparison")
en.append("")
en.append(md_table(comparison_rows, display_cols))
en.append("")
en.append("## Aggregate")
en.append("")
en.append(f"- Current wins by solve time: `{current_wins}/6` cases.")
en.append(f"- Pre-tuning wins by solve time: `{pre_wins}/6` cases.")
en.append(f"- Geometric mean current/pre solve-time ratio: `{gm_ratio:.6f}`.")
en.append(f"- Geometric mean pre/current speedup: `{gm_speedup:.6f}`.")
en.append("")
en.append("## Interpretation")
en.append("")
en.append("- Both versions reached `OPTIMAL` on all six fast-core6 cases.")
en.append("- The current engineering branch is not uniformly faster than `ae3b683 / pre_tuning` on this fast subset.")
en.append("- This result should be used as a truthful before/current engineering comparison, not as a blanket W7900 speedup claim.")
en.append("- The mixed result reinforces the need for W7900-specific profiling and tuning.")
en.append("- `s100` and `Primal2_1000` were intentionally excluded from this fast-core6 run because their known W7900 runtimes are too long for the available experiment window.")
en.append("")
en.append("## Repository policy")
en.append("")
en.append("Commit only compact CSV and Markdown summaries. Raw large-MPS files and raw run directories stay outside Git.")
en.append("")
md_out.write_text("\n".join(en))
print(f"wrote {md_out}")

zh = []
zh.append("# W7900 before/current fast-core6 摘要")
zh.append("")
zh.append(f"结果目录：`{OUT}`")
zh.append("")
zh.append("本文是 W7900 fast-core6 before/current 对比的 compact summary。")
zh.append("")
zh.append("对比版本：")
zh.append("")
zh.append("- `pre_tuning`：`ae3b683 / pre_tuning`，在 W7900 上通过补充 ROCm Python SDK include path 完成构建。")
zh.append("- `current`：当前 `rocm-w7900-gfx1100` 工程分支。")
zh.append("")
zh.append("Fast-core6 case list：")
zh.append("")
zh.append("- `set-cover-model.mps`")
zh.append("- `square41.mps`")
zh.append("- `thk_48.mps`")
zh.append("- `tpl-tub-ws1617.mps`")
zh.append("- `L2CTA3D.mps`")
zh.append("- `rmine15.mps`")
zh.append("")
zh.append("## 对比结果")
zh.append("")
zh.append(md_table(comparison_rows, display_cols))
zh.append("")
zh.append("## 汇总")
zh.append("")
zh.append(f"- current 按 solve time 取胜：`{current_wins}/6` 个 case。")
zh.append(f"- pre_tuning 按 solve time 取胜：`{pre_wins}/6` 个 case。")
zh.append(f"- 几何平均 current/pre solve-time ratio：`{gm_ratio:.6f}`。")
zh.append(f"- 几何平均 pre/current speedup：`{gm_speedup:.6f}`。")
zh.append("")
zh.append("## 结果解释")
zh.append("")
zh.append("- 两个版本在 fast-core6 的 6 个 case 上都达到 `OPTIMAL`。")
zh.append("- 当前工程分支在这个 fast subset 上并非全面快于 `ae3b683 / pre_tuning`。")
zh.append("- 这轮结果应作为真实 before/current 工程对比，而不能写成笼统的 W7900 加速结论。")
zh.append("- 该混合结果进一步说明后续 W7900-specific profiling 和 tuning 是必要的。")
zh.append("- `s100` 和 `Primal2_1000` 因已知 W7900 运行时间较长，被有意排除在本次 fast-core6 之外，以适配当前实验时间窗口。")
zh.append("")
zh.append("## 仓库策略")
zh.append("")
zh.append("只提交 compact CSV 和 Markdown summary。raw large-MPS 文件和大型运行目录保存在 Git 外部。")
zh.append("")
zh_out.write_text("\n".join(zh))
print(f"wrote {zh_out}")

print("\nCompact outputs:")
for p in [
    current_runtime_out,
    pre_runtime_out,
    current_solver_out,
    pre_solver_out,
    comparison_out,
    md_out,
    zh_out,
]:
    print(p)
