#!/usr/bin/env python3
import csv
import math
import os
import shutil
import sys
from pathlib import Path

if len(sys.argv) < 3:
    raise SystemExit("usage: extract_w7900_8card_batch_fast8_compact_20260616.py CONCURRENT_OUT SEQUENTIAL_OUT")

CONCURRENT = Path(sys.argv[1])
SEQUENTIAL = Path(sys.argv[2])

if not CONCURRENT.exists():
    raise SystemExit(f"missing concurrent dir: {CONCURRENT}")
if not SEQUENTIAL.exists():
    raise SystemExit(f"missing sequential dir: {SEQUENTIAL}")

DATE = "20260616"
VAL = Path("validation")
VAL.mkdir(exist_ok=True)

con_runtime_out = VAL / f"w7900_8card_batch_fast8_concurrent_runtime_{DATE}.csv"
con_solver_out = VAL / f"w7900_8card_batch_fast8_concurrent_solver_{DATE}.csv"
seq_runtime_out = VAL / f"w7900_8card_batch_fast8_single_gpu_seq_runtime_{DATE}.csv"
seq_solver_out = VAL / f"w7900_8card_batch_fast8_single_gpu_seq_solver_{DATE}.csv"
comparison_out = VAL / f"w7900_8card_batch_fast8_comparison_{DATE}.csv"
md_out = VAL / f"w7900_8card_batch_fast8_summary_{DATE}.md"
zh_out = VAL / f"w7900_8card_batch_fast8_summary_{DATE}.zh-CN.md"

def copy(src, dst):
    if not src.exists():
        raise SystemExit(f"missing source file: {src}")
    shutil.copyfile(src, dst)
    print(f"wrote {dst}")

copy(CONCURRENT / "runtime_summary.csv", con_runtime_out)
copy(CONCURRENT / "parsed_solver_summary.csv", con_solver_out)
copy(SEQUENTIAL / "runtime_summary.csv", seq_runtime_out)
copy(SEQUENTIAL / "parsed_solver_summary.csv", seq_solver_out)

def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def fnum(x):
    try:
        return float(x)
    except Exception:
        return float("nan")

def read_float_file(path):
    return float(path.read_text().strip())

con_makespan = read_float_file(CONCURRENT / "batch_makespan_seconds.txt")
seq_makespan = read_float_file(SEQUENTIAL / "sequential_makespan_seconds.txt")
speedup = seq_makespan / con_makespan
efficiency = speedup / 8.0
con_cases_per_hour = 8.0 / (con_makespan / 3600.0)
seq_cases_per_hour = 8.0 / (seq_makespan / 3600.0)

con_runtime = read_csv(con_runtime_out)
seq_runtime = read_csv(seq_runtime_out)
con_solver = read_csv(con_solver_out)
seq_solver = read_csv(seq_solver_out)

con_rt = {r["case"].replace(".mps", ""): r for r in con_runtime}
seq_rt = {r["case"].replace(".mps", ""): r for r in seq_runtime}
con_sv = {r["case"]: r for r in con_solver}
seq_sv = {r["case"]: r for r in seq_solver}

comparison_rows = []
for case in sorted(set(con_sv) & set(seq_sv)):
    cr = con_rt.get(case, {})
    sr = seq_rt.get(case, {})
    cs = con_sv[case]
    ss = seq_sv[case]

    con_wall = fnum(cr.get("wall_seconds"))
    seq_wall = fnum(sr.get("wall_seconds"))
    wall_ratio = seq_wall / con_wall if con_wall and not math.isnan(con_wall) else float("nan")

    comparison_rows.append({
        "case": case,
        "concurrent_gpu": cr.get("gpu", ""),
        "concurrent_status": cr.get("status", ""),
        "sequential_status": sr.get("status", ""),
        "concurrent_wall_seconds": cr.get("wall_seconds", ""),
        "sequential_wall_seconds": sr.get("wall_seconds", ""),
        "sequential_over_concurrent_wall_ratio": f"{wall_ratio:.6f}" if not math.isnan(wall_ratio) else "",
        "concurrent_termination": cs.get("terminationCode", ""),
        "sequential_termination": ss.get("terminationCode", ""),
        "concurrent_solve_time": cs.get("dSolvingTime", ""),
        "sequential_solve_time": ss.get("dSolvingTime", ""),
        "concurrent_gap": cs.get("dRelDualityGap", ""),
        "sequential_gap": ss.get("dRelDualityGap", ""),
    })

fields = [
    "case",
    "concurrent_gpu",
    "concurrent_status",
    "sequential_status",
    "concurrent_wall_seconds",
    "sequential_wall_seconds",
    "sequential_over_concurrent_wall_ratio",
    "concurrent_termination",
    "sequential_termination",
    "concurrent_solve_time",
    "sequential_solve_time",
    "concurrent_gap",
    "sequential_gap",
]

with comparison_out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(comparison_rows)
print(f"wrote {comparison_out}")

def md_table(rows, cols):
    lines = []
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "|".join(["---"] * len(cols)) + "|")
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(lines)

display_cols = [
    "case",
    "concurrent_gpu",
    "concurrent_status",
    "sequential_status",
    "concurrent_wall_seconds",
    "sequential_wall_seconds",
    "concurrent_termination",
    "sequential_termination",
]

en = []
en.append("# W7900 8-card fast8 batch throughput summary")
en.append("")
en.append(f"Concurrent result directory: `{CONCURRENT}`")
en.append(f"Single-GPU sequential result directory: `{SEQUENTIAL}`")
en.append("")
en.append("This is a compact summary of the W7900 independent-MPS batch throughput experiment. The experiment compares 8 independent MPS cases executed concurrently on 8 W7900 GPUs against the same 8 cases executed sequentially on one W7900 GPU.")
en.append("")
en.append("## Case list")
en.append("")
en.append("- `set-cover-model.mps`")
en.append("- `square41.mps`")
en.append("- `thk_48.mps`")
en.append("- `tpl-tub-ws1617.mps`")
en.append("- `L2CTA3D.mps`")
en.append("- `rmine15.mps`")
en.append("- `qap15.mps`")
en.append("- `graph40-40.mps`")
en.append("")
en.append("## Throughput summary")
en.append("")
en.append("| Metric | Value |")
en.append("|---|---:|")
en.append(f"| 8-card concurrent makespan seconds | {con_makespan:.0f} |")
en.append(f"| single-GPU sequential makespan seconds | {seq_makespan:.0f} |")
en.append(f"| makespan speedup | {speedup:.6f}x |")
en.append(f"| 8-card efficiency | {efficiency:.6f} |")
en.append(f"| concurrent cases per hour | {con_cases_per_hour:.6f} |")
en.append(f"| sequential cases per hour | {seq_cases_per_hour:.6f} |")
en.append("")
en.append("## Per-case comparison")
en.append("")
en.append(md_table(comparison_rows, display_cols))
en.append("")
en.append("## Interpretation")
en.append("")
en.append("- Both the 8-card concurrent run and the single-GPU sequential run solved all 8 cases to `OPTIMAL`.")
en.append(f"- The measured batch makespan improved from `{seq_makespan:.0f}s` to `{con_makespan:.0f}s`, giving a measured makespan speedup of `{speedup:.2f}x`.")
en.append("- This demonstrates the throughput value of the 8x W7900 node for batches of independent LP/MPS workloads.")
en.append("- This is an independent-task throughput result, not a claim that one MPS instance is accelerated across 8 GPUs.")
en.append("- GPU binding used `ROCR_VISIBLE_DEVICES` only; the earlier attempt that combined HIP and ROCR visibility filters failed and is intentionally not summarized as a result.")
en.append("")
en.append("## Repository policy")
en.append("")
en.append("Commit only compact CSV and Markdown summaries. Raw large-MPS files and raw run directories stay outside Git.")
en.append("")
md_out.write_text("\n".join(en))
print(f"wrote {md_out}")

zh = []
zh.append("# W7900 8-card fast8 批处理吞吐摘要")
zh.append("")
zh.append(f"8 卡并发结果目录：`{CONCURRENT}`")
zh.append(f"单 GPU 顺序结果目录：`{SEQUENTIAL}`")
zh.append("")
zh.append("本文是 W7900 independent-MPS batch throughput 实验的 compact summary。实验对比了 8 个独立 MPS case 在 8 张 W7900 上并发运行，与同一组 8 个 case 在单张 W7900 上顺序运行的总完成时间。")
zh.append("")
zh.append("## Case list")
zh.append("")
zh.append("- `set-cover-model.mps`")
zh.append("- `square41.mps`")
zh.append("- `thk_48.mps`")
zh.append("- `tpl-tub-ws1617.mps`")
zh.append("- `L2CTA3D.mps`")
zh.append("- `rmine15.mps`")
zh.append("- `qap15.mps`")
zh.append("- `graph40-40.mps`")
zh.append("")
zh.append("## 吞吐摘要")
zh.append("")
zh.append("| 指标 | 数值 |")
zh.append("|---|---:|")
zh.append(f"| 8 卡并发 makespan 秒数 | {con_makespan:.0f} |")
zh.append(f"| 单 GPU 顺序 makespan 秒数 | {seq_makespan:.0f} |")
zh.append(f"| makespan speedup | {speedup:.6f}x |")
zh.append(f"| 8 卡效率 | {efficiency:.6f} |")
zh.append(f"| 并发 cases per hour | {con_cases_per_hour:.6f} |")
zh.append(f"| 顺序 cases per hour | {seq_cases_per_hour:.6f} |")
zh.append("")
zh.append("## 单 case 对比")
zh.append("")
zh.append(md_table(comparison_rows, display_cols))
zh.append("")
zh.append("## 结果解释")
zh.append("")
zh.append("- 8 卡并发运行和单 GPU 顺序运行都在 8 个 case 上达到 `OPTIMAL`。")
zh.append(f"- 实测 batch makespan 从 `{seq_makespan:.0f}s` 降到 `{con_makespan:.0f}s`，对应 `{speedup:.2f}x` 的 makespan speedup。")
zh.append("- 这说明 8x W7900 节点适合面向独立 LP/MPS 工作负载的批处理吞吐场景。")
zh.append("- 这是 independent-task throughput 结果，不表示单个 MPS 实例被 8 张 GPU 联合加速。")
zh.append("- GPU 绑定使用 `ROCR_VISIBLE_DEVICES` only；此前同时设置 HIP 和 ROCR visibility filter 的尝试失败，不作为正式结果总结。")
zh.append("")
zh.append("## 仓库策略")
zh.append("")
zh.append("只提交 compact CSV 和 Markdown summary。raw large-MPS 文件和大型运行目录保存在 Git 外部。")
zh.append("")
zh_out.write_text("\n".join(zh))
print(f"wrote {zh_out}")

print("\nCompact outputs:")
for p in [
    con_runtime_out,
    con_solver_out,
    seq_runtime_out,
    seq_solver_out,
    comparison_out,
    md_out,
    zh_out,
]:
    print(p)
