#!/usr/bin/env python3
import csv
import os
import shutil
import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("OUT", ""))
if not OUT.exists():
    raise SystemExit(f"missing result dir: {OUT}")

DATE = "20260616"
VAL = Path("validation")
VAL.mkdir(exist_ok=True)

runtime_out = VAL / f"w7900_large_mps_hard3_probe2_600s_runtime_{DATE}.csv"
solver_out = VAL / f"w7900_large_mps_hard3_probe2_600s_solver_{DATE}.csv"
md_out = VAL / f"w7900_large_mps_hard3_probe2_600s_summary_{DATE}.md"
zh_out = VAL / f"w7900_large_mps_hard3_probe2_600s_summary_{DATE}.zh-CN.md"

def copy_if_exists(src: Path, dst: Path):
    if not src.exists():
        raise SystemExit(f"missing source file: {src}")
    shutil.copyfile(src, dst)
    print(f"wrote {dst}")

copy_if_exists(OUT / "runtime_summary.csv", runtime_out)
copy_if_exists(OUT / "parsed_solver_summary.csv", solver_out)

def read_csv(path: Path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

solver_rows = read_csv(solver_out)
runtime_rows = read_csv(runtime_out)

def md_table(rows, cols):
    lines = []
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "|".join(["---"] * len(cols)) + "|")
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(lines)

solver_cols = [
    "case",
    "runtime_status",
    "exit_code",
    "wall_seconds",
    "terminationCode",
    "nIter",
    "dSolvingTime",
    "DeviceMatVecProdTime",
    "dRelPrimalFeas",
    "dRelDualFeas",
    "dRelDualityGap",
]

runtime_cols = ["case", "status", "exit_code", "wall_seconds"]

en = []
en.append("# W7900 large-MPS hard3 probe2 600s summary")
en.append("")
en.append(f"Result directory: `{OUT}`")
en.append("")
en.append("This is a compact summary of the W7900 hard3 probe2 diagnostic run. The run uses a 600-second solver time limit and tracks hard cases separately from the non-hard23 large-MPS baseline.")
en.append("")
en.append("## Runtime summary")
en.append("")
en.append(md_table(runtime_rows, runtime_cols))
en.append("")
en.append("## Solver summary")
en.append("")
en.append(md_table(solver_rows, solver_cols))
en.append("")
en.append("## Interpretation")
en.append("")
en.append("- Both `dlr1` and `fhnw-binschedule1` reached the 600-second solver time limit.")
en.append("- `dlr1` has relative duality gap around `0.284`, with relative primal and dual infeasibility still large; it is not near convergence under the 600-second probe.")
en.append("- `fhnw-binschedule1` has small primal infeasibility and zero dual infeasibility, but relative duality gap remains around `0.392`; it is also not near an OPTIMAL termination under the 600-second probe.")
en.append("- These cases remain tracked as hard cases and should not be mixed into the non-hard23 primary baseline.")
en.append("- No immediate 1800-second extension is recommended from this probe; W7900-specific tuning and later targeted probes should come first.")
en.append("")
en.append("## Repository policy")
en.append("")
en.append("Commit only compact CSV and Markdown summaries. Raw large-MPS files and large intermediate result directories stay outside Git.")
en.append("")
md_out.write_text("\n".join(en))
print(f"wrote {md_out}")

zh = []
zh.append("# W7900 large-MPS hard3 probe2 600s 摘要")
zh.append("")
zh.append(f"结果目录：`{OUT}`")
zh.append("")
zh.append("本文是 W7900 hard3 probe2 诊断运行的 compact summary。该运行使用 600 秒 solver time limit，并将 hard case 与 non-hard23 large-MPS 主 baseline 分开跟踪。")
zh.append("")
zh.append("## 外层运行摘要")
zh.append("")
zh.append(md_table(runtime_rows, runtime_cols))
zh.append("")
zh.append("## 求解器摘要")
zh.append("")
zh.append(md_table(solver_rows, solver_cols))
zh.append("")
zh.append("## 结果解释")
zh.append("")
zh.append("- `dlr1` 和 `fhnw-binschedule1` 都达到 600 秒 solver time limit。")
zh.append("- `dlr1` 的 relative duality gap 约为 `0.284`，relative primal / dual infeasibility 仍然较大；在 600 秒 probe 下并未接近收敛。")
zh.append("- `fhnw-binschedule1` 的 primal infeasibility 较小、dual infeasibility 为 0，但 relative duality gap 仍约为 `0.392`；在 600 秒 probe 下同样没有接近 OPTIMAL termination。")
zh.append("- 这两个 case 继续作为 hard case 单独跟踪，不混入 non-hard23 主 baseline。")
zh.append("- 根据本次 probe，不建议立即加时到 1800 秒；应先完成 W7900-specific tuning 或后续更有针对性的诊断。")
zh.append("")
zh.append("## 仓库策略")
zh.append("")
zh.append("只提交 compact CSV 和 Markdown summary。raw large-MPS 文件和大型中间结果目录保存在 Git 外部。")
zh.append("")
zh_out.write_text("\n".join(zh))
print(f"wrote {zh_out}")

print("\nCompact outputs:")
for p in [runtime_out, solver_out, md_out, zh_out]:
    print(p)
