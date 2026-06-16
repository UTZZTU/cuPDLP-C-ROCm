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

runtime_out = VAL / f"w7900_rocprof_starter3_runtime_{DATE}.csv"
solver_out = VAL / f"w7900_rocprof_starter3_solver_{DATE}.csv"
hip_out = VAL / f"w7900_rocprof_starter3_hip_api_top_{DATE}.csv"
kernel_out = VAL / f"w7900_rocprof_starter3_kernel_top_{DATE}.csv"
md_out = VAL / f"w7900_rocprof_starter3_summary_{DATE}.md"
zh_out = VAL / f"w7900_rocprof_starter3_summary_{DATE}.zh-CN.md"

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

def fnum(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def shorten_name(name: str, limit: int = 150) -> str:
    name = " ".join(name.replace("\n", " ").split())
    return name if len(name) <= limit else name[: limit - 3] + "..."

def collect_stats(kind: str, dst: Path, topn: int = 8):
    rows_out = []
    profiler_root = OUT / "profiler"
    for case_dir in sorted(profiler_root.iterdir()):
        if not case_dir.is_dir():
            continue
        case = case_dir.name
        files = sorted(case_dir.glob(f"**/*_{kind}_stats.csv"))
        if not files:
            rows_out.append({
                "case": case,
                "rank": "",
                "name": "MISSING",
                "calls": "",
                "total_ms": "",
                "avg_us": "",
                "percentage": "",
                "min_us": "",
                "max_us": "",
                "stddev_us": "",
                "source_file": "",
            })
            continue

        src = files[0]
        rows = read_csv(src)
        rows.sort(key=lambda r: fnum(r.get("Percentage", 0)), reverse=True)

        for rank, r in enumerate(rows[:topn], start=1):
            rows_out.append({
                "case": case,
                "rank": rank,
                "name": shorten_name(r.get("Name", "")),
                "calls": r.get("Calls", ""),
                "total_ms": f"{fnum(r.get('TotalDurationNs')) / 1e6:.6f}",
                "avg_us": f"{fnum(r.get('AverageNs')) / 1e3:.6f}",
                "percentage": r.get("Percentage", ""),
                "min_us": f"{fnum(r.get('MinNs')) / 1e3:.6f}",
                "max_us": f"{fnum(r.get('MaxNs')) / 1e3:.6f}",
                "stddev_us": f"{fnum(r.get('StdDev')) / 1e3:.6f}",
                "source_file": str(src),
            })

    fields = ["case", "rank", "name", "calls", "total_ms", "avg_us", "percentage", "min_us", "max_us", "stddev_us", "source_file"]
    with dst.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows_out)
    print(f"wrote {dst}")
    return rows_out

hip_rows = collect_stats("hip_api", hip_out)
kernel_rows = collect_stats("kernel", kernel_out)

solver_rows = read_csv(solver_out)
runtime_rows = read_csv(runtime_out)

def md_table(rows, cols):
    out = []
    out.append("| " + " | ".join(cols) + " |")
    out.append("|" + "|".join(["---"] * len(cols)) + "|")
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out)

def top_for(rows, case, n=5):
    return [r for r in rows if r.get("case") == case][:n]

cases = ["set-cover-model", "square41", "s100"]

en = []
en.append("# W7900 rocprof starter3 summary")
en.append("")
en.append(f"Result directory: `{OUT}`")
en.append("")
en.append("This is a compact summary of the W7900 `rocprof` starter3 run. Raw profiler trace files are intentionally not committed because they are large.")
en.append("")
en.append("## Solver summary")
en.append("")
en.append(md_table(solver_rows, ["case", "runtime_status", "exit_code", "wall_seconds", "terminationCode", "nIter", "dSolvingTime", "DeviceMatVecProdTime", "dRelDualityGap"]))
en.append("")
en.append("## Runtime summary")
en.append("")
en.append(md_table(runtime_rows, ["case", "status", "exit_code", "wall_seconds"]))
en.append("")
en.append("## Key interpretation")
en.append("")
en.append("- `set-cover-model` and `square41` reached `OPTIMAL` under the profiling run.")
en.append("- `s100` reached the solver time limit at about 900 seconds with relative duality gap around `4.94e-04`; its profiler stats files are available, but the external profiler wrapper ended with timeout code `124` during trace finalization.")
en.append("- Raw HIP API and kernel trace files are large and should stay outside Git. Commit only the compact CSV and Markdown summaries.")
en.append("")
for case in cases:
    en.append(f"## Top HIP API stats: `{case}`")
    en.append("")
    en.append(md_table(top_for(hip_rows, case), ["rank", "name", "calls", "total_ms", "percentage", "avg_us"]))
    en.append("")
    en.append(f"## Top kernel stats: `{case}`")
    en.append("")
    en.append(md_table(top_for(kernel_rows, case), ["rank", "name", "calls", "total_ms", "percentage", "avg_us"]))
    en.append("")

md_out.write_text("\n".join(en))
print(f"wrote {md_out}")

zh = []
zh.append("# W7900 rocprof starter3 摘要")
zh.append("")
zh.append(f"结果目录：`{OUT}`")
zh.append("")
zh.append("本文是 W7900 `rocprof` starter3 运行结果的 compact summary。原始 profiler trace 文件体积很大，不进入 Git。")
zh.append("")
zh.append("## 求解器摘要")
zh.append("")
zh.append(md_table(solver_rows, ["case", "runtime_status", "exit_code", "wall_seconds", "terminationCode", "nIter", "dSolvingTime", "DeviceMatVecProdTime", "dRelDualityGap"]))
zh.append("")
zh.append("## 外层运行摘要")
zh.append("")
zh.append(md_table(runtime_rows, ["case", "status", "exit_code", "wall_seconds"]))
zh.append("")
zh.append("## 关键解释")
zh.append("")
zh.append("- `set-cover-model` 和 `square41` 在 profiling 运行中达到 `OPTIMAL`。")
zh.append("- `s100` 的 solver 在约 900 秒达到时间上限，relative duality gap 约为 `4.94e-04`；其 profiler stats 文件已经生成，但外层 profiler wrapper 在 trace finalization 阶段以 timeout code `124` 结束。")
zh.append("- 原始 HIP API trace 和 kernel trace 文件体积很大，应保存在 Git 外部；Git 中只提交 compact CSV 和 Markdown summary。")
zh.append("")
for case in cases:
    zh.append(f"## Top HIP API stats：`{case}`")
    zh.append("")
    zh.append(md_table(top_for(hip_rows, case), ["rank", "name", "calls", "total_ms", "percentage", "avg_us"]))
    zh.append("")
    zh.append(f"## Top kernel stats：`{case}`")
    zh.append("")
    zh.append(md_table(top_for(kernel_rows, case), ["rank", "name", "calls", "total_ms", "percentage", "avg_us"]))
    zh.append("")

zh_out.write_text("\n".join(zh))
print(f"wrote {zh_out}")

print("\nCompact outputs:")
for p in [runtime_out, solver_out, hip_out, kernel_out, md_out, zh_out]:
    print(p)
