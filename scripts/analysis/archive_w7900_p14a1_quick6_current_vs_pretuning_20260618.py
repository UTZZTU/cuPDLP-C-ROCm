#!/usr/bin/env python3
from pathlib import Path
import csv
import math
import re
import statistics as stats

ROOT = Path(__file__).resolve().parents[2]
PTR = ROOT / "validation/results/latest_w7900_p14a1_quick6_current_vs_pretuning.txt"

OUT_RAW = ROOT / "validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_raw.csv"
OUT_AGG = ROOT / "validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_aggregated.csv"
OUT_CMP = ROOT / "validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv"
OUT_MD = ROOT / "validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md"
OUT_ZH = ROOT / "validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md"

RE_STATUS = re.compile(r"Solving information:\s*(.*)")
RE_PRIMAL_OBJ = re.compile(r"Primal objective:\s*([+-]?[0-9.]+e[+-][0-9]+)")
RE_DUAL_OBJ = re.compile(r"Dual objective:\s*([+-]?[0-9.]+e[+-][0-9]+)")
RE_INFEAS_P = re.compile(r"Primal infeas \(abs/rel\):\s*([0-9.eE+-]+)\s*/\s*([0-9.eE+-]+)")
RE_INFEAS_D = re.compile(r"Dual infeas \(abs/rel\):\s*([0-9.eE+-]+)\s*/\s*([0-9.eE+-]+)")
RE_GAP = re.compile(r"Duality gap \(abs/rel\):\s*([0-9.eE+-]+)\s*/\s*([0-9.eE+-]+)")
RE_NITER = re.compile(r"Number of iterations:\s*(\d+)")
RE_TOTAL = re.compile(r"Total solver time\s*([0-9.eE+-]+)\s+in\s+(\d+)\s+iterations")
RE_SOLVE = re.compile(r"Solve time\s*([0-9.eE+-]+)\s+in\s+(\d+)\s+iterations")
RE_ITERS = re.compile(r"Iters per sec\s*([0-9.eE+-]+)")
RE_MATVEC = re.compile(r"DeviceMatVecProd\s*([0-9.eE+-]+)")
RE_UPDATE = re.compile(r"UpdateIterates\s*([0-9.eE+-]+)\s+in\s+(\d+)\s+calls")

def fnum(x):
    try:
        return float(x)
    except Exception:
        return math.nan

def parse_log(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    row = {}

    m = RE_STATUS.search(text)
    row["status"] = m.group(1).strip() if m else ""

    for key, rx in [
        ("primal_objective", RE_PRIMAL_OBJ),
        ("dual_objective", RE_DUAL_OBJ),
        ("niter", RE_NITER),
        ("iters_per_sec", RE_ITERS),
    ]:
        m = rx.search(text)
        row[key] = m.group(1) if m else ""

    m = RE_INFEAS_P.search(text)
    row["primal_infeas_abs"] = m.group(1) if m else ""
    row["primal_infeas_rel"] = m.group(2) if m else ""

    m = RE_INFEAS_D.search(text)
    row["dual_infeas_abs"] = m.group(1) if m else ""
    row["dual_infeas_rel"] = m.group(2) if m else ""

    m = RE_GAP.search(text)
    row["duality_gap_abs"] = m.group(1) if m else ""
    row["duality_gap_rel"] = m.group(2) if m else ""

    m = RE_TOTAL.search(text)
    row["total_solver_time_sec"] = m.group(1) if m else ""

    m = RE_SOLVE.search(text)
    row["solve_time_sec"] = m.group(1) if m else ""

    m = RE_MATVEC.search(text)
    row["device_matvec_time_sec"] = m.group(1) if m else ""

    m = RE_UPDATE.search(text)
    row["update_iterates_sec"] = m.group(1) if m else ""
    row["update_iterates_calls"] = m.group(2) if m else ""

    niter = fnum(row.get("niter", ""))
    solve = fnum(row.get("solve_time_sec", ""))
    row["ms_per_iter"] = "" if not math.isfinite(niter) or niter <= 0 or not math.isfinite(solve) else f"{solve * 1000.0 / niter:.9g}"

    return row

def read_exit(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"exit=(\d+)", txt)
    return m.group(1) if m else txt.strip()

def collect(result_root: Path):
    rows = []

    for meta in sorted((result_root / "runs").glob("*/*/rep_*/meta.txt")):
        info = {}
        for line in meta.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                info[k] = v

        label = info["label"]
        case = info["case"]
        rep = info["rep"]

        outdir = meta.parent
        logs = list(outdir.glob(f"{case}_{label}_rep{rep}.log"))
        exits = list(outdir.glob(f"{case}_{label}_rep{rep}.exit"))

        row = {
            "label": label,
            "case": case,
            "rep": rep,
            "exitcode": read_exit(exits[0]) if exits else "",
            "log_file": str(logs[0].relative_to(result_root)) if logs else "",
            "run_dir": str(outdir),
            "mps": info.get("mps", ""),
            "nIterLim": info.get("nIterLim", ""),
            "dTimeLim": info.get("dTimeLim", ""),
        }

        if logs:
            row.update(parse_log(logs[0]))
        rows.append(row)

    return rows

def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"[OK] wrote {path.relative_to(ROOT)}")

def summarize(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r["case"], r["label"]), []).append(r)

    agg = []
    for (case, label), rs in sorted(groups.items()):
        solves = [fnum(r.get("solve_time_sec", "")) for r in rs]
        solves = [x for x in solves if math.isfinite(x)]
        niters = sorted({r.get("niter", "") for r in rs})
        statuses = sorted({r.get("status", "") for r in rs})
        exits = sorted({r.get("exitcode", "") for r in rs})

        if solves:
            mean = stats.mean(solves)
            median = stats.median(solves)
            stdev = stats.stdev(solves) if len(solves) > 1 else 0.0
            cv = stdev / mean if mean else math.nan
            min_v = min(solves)
            max_v = max(solves)
        else:
            mean = median = stdev = cv = min_v = max_v = math.nan

        niter_num = fnum(niters[0]) if len(niters) == 1 else math.nan
        ms_per_iter = median * 1000.0 / niter_num if math.isfinite(median) and math.isfinite(niter_num) and niter_num > 0 else math.nan

        agg.append({
            "case": case,
            "label": label,
            "runs": str(len(rs)),
            "exitcodes": ";".join(exits),
            "statuses": ";".join(statuses),
            "niters": ";".join(niters),
            "solve_mean_sec": f"{mean:.9g}" if math.isfinite(mean) else "",
            "solve_median_sec": f"{median:.9g}" if math.isfinite(median) else "",
            "solve_std_sec": f"{stdev:.9g}" if math.isfinite(stdev) else "",
            "solve_cv": f"{cv:.9g}" if math.isfinite(cv) else "",
            "solve_min_sec": f"{min_v:.9g}" if math.isfinite(min_v) else "",
            "solve_max_sec": f"{max_v:.9g}" if math.isfinite(max_v) else "",
            "median_ms_per_iter": f"{ms_per_iter:.9g}" if math.isfinite(ms_per_iter) else "",
        })

    return agg

def compare(agg):
    by_case = {}
    for r in agg:
        by_case.setdefault(r["case"], {})[r["label"]] = r

    out = []
    speedups = []
    for case, d in sorted(by_case.items()):
        pre = d.get("pre_tuning")
        cur = d.get("current")
        if not pre or not cur:
            continue

        pre_med = fnum(pre["solve_median_sec"])
        cur_med = fnum(cur["solve_median_sec"])
        speedup = pre_med / cur_med if math.isfinite(pre_med) and math.isfinite(cur_med) and cur_med > 0 else math.nan
        if math.isfinite(speedup):
            speedups.append(speedup)

        out.append({
            "case": case,
            "pre_median_solve_sec": pre["solve_median_sec"],
            "current_median_solve_sec": cur["solve_median_sec"],
            "median_speedup_pre_over_current": f"{speedup:.9g}" if math.isfinite(speedup) else "",
            "pre_niters": pre["niters"],
            "current_niters": cur["niters"],
            "pre_statuses": pre["statuses"],
            "current_statuses": cur["statuses"],
            "pre_cv": pre["solve_cv"],
            "current_cv": cur["solve_cv"],
        })

    if speedups:
        geo = math.exp(sum(math.log(x) for x in speedups) / len(speedups))
        med = stats.median(speedups)
    else:
        geo = med = math.nan

    return out, geo, med

def md_table(cmp_rows):
    lines = [
        "| case | pre median solve s | current median solve s | speedup pre/current | pre nIter | current nIter |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in cmp_rows:
        lines.append(
            f"| `{r['case']}` | {r['pre_median_solve_sec']} | {r['current_median_solve_sec']} | {r['median_speedup_pre_over_current']} | {r['pre_niters']} | {r['current_niters']} |"
        )
    return "\n".join(lines)

def main():
    if not PTR.exists():
        raise FileNotFoundError(PTR)

    result_root = Path(PTR.read_text(encoding="utf-8").strip())
    rows = collect(result_root)
    agg = summarize(rows)
    cmp_rows, geo, med = compare(agg)

    raw_fields = [
        "label", "case", "rep", "exitcode", "status", "niter",
        "solve_time_sec", "total_solver_time_sec", "ms_per_iter",
        "iters_per_sec", "device_matvec_time_sec", "update_iterates_sec",
        "update_iterates_calls", "primal_objective", "dual_objective",
        "primal_infeas_abs", "primal_infeas_rel", "dual_infeas_abs",
        "dual_infeas_rel", "duality_gap_abs", "duality_gap_rel",
        "nIterLim", "dTimeLim", "mps", "run_dir", "log_file",
    ]

    agg_fields = [
        "case", "label", "runs", "exitcodes", "statuses", "niters",
        "solve_mean_sec", "solve_median_sec", "solve_std_sec", "solve_cv",
        "solve_min_sec", "solve_max_sec", "median_ms_per_iter",
    ]

    cmp_fields = [
        "case", "pre_median_solve_sec", "current_median_solve_sec",
        "median_speedup_pre_over_current", "pre_niters", "current_niters",
        "pre_statuses", "current_statuses", "pre_cv", "current_cv",
    ]

    write_csv(OUT_RAW, rows, raw_fields)
    write_csv(OUT_AGG, agg, agg_fields)
    write_csv(OUT_CMP, cmp_rows, cmp_fields)

    md = f"""# W7900 P14-A1 quick6 current vs pre_tuning repeated validation

Result root: `{result_root}`

This experiment repeats the 890M-style quick6 methodology on W7900 / `gfx1100`.
It compares:

- `pre_tuning`: `ae3b683`
- `current`: current `rocm-w7900-gfx1100` HEAD at run time

Each case/version pair is run three times. The main timing metric is median
solve time.

## Aggregate result

- geometric mean speedup, `pre_tuning / current`: `{geo:.6g}`
- median speedup, `pre_tuning / current`: `{med:.6g}`

A value greater than 1 means `current` is faster.

## Comparison table

{md_table(cmp_rows)}

## Interpretation note

This is quick-set tuning-transfer evidence, not a replacement for the large-MPS
baseline. It should be reported separately from non-hard23 large-MPS results.
"""

    OUT_MD.write_text(md, encoding="utf-8", newline="\n")
    print(f"[OK] wrote {OUT_MD.relative_to(ROOT)}")

    zh = f"""# W7900 P14-A1 quick6 current vs pre_tuning repeated validation

结果目录：`{result_root}`

本实验在 W7900 / `gfx1100` 上复用 890M-style quick6 方法论，对比：

- `pre_tuning`：`ae3b683`
- `current`：运行时当前 `rocm-w7900-gfx1100` HEAD

每个 case/version 组合重复运行 3 次。主计时指标为 median solve time。

## 汇总结果

- 几何平均 speedup，`pre_tuning / current`：`{geo:.6g}`
- 中位数 speedup，`pre_tuning / current`：`{med:.6g}`

大于 1 表示 `current` 更快。

## 对比表

{md_table(cmp_rows)}

## 解释说明

这是 quick-set tuning-transfer evidence，不替代 large-MPS baseline。它应与
non-hard23 large-MPS 结果分开表述。
"""

    OUT_ZH.write_text(zh, encoding="utf-8", newline="\n")
    print(f"[OK] wrote {OUT_ZH.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
