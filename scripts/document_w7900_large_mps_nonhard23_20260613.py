#!/usr/bin/env python3
import csv
from pathlib import Path

INITIAL_CSV = Path("validation/w7900_large_mps_initial17_safe_20260613.csv")
INITIAL_RUNTIME_CSV = Path("validation/w7900_large_mps_initial17_safe_20260613_runtime.csv")
WATCH_CSV = Path("validation/w7900_large_mps_watchlist6_diag_900s_20260613.csv")
WATCH_RUNTIME_CSV = Path("validation/w7900_large_mps_watchlist6_diag_900s_20260613_runtime.csv")
NEAR_CSV = Path("validation/w7900_large_mps_near_optimal2_1800s_20260613.csv")
NEAR_RUNTIME_CSV = Path("validation/w7900_large_mps_near_optimal2_1800s_20260613_runtime.csv")
HIST_CSV = Path("results/benchmarks/large_mps_per_case_timing_summary_20260610.csv")

OUT_CSV = Path("validation/w7900_large_mps_nonhard23_20260613.csv")
OUT_RUNTIME_CSV = Path("validation/w7900_large_mps_nonhard23_20260613_runtime.csv")
OUT_MD = Path("validation/w7900_large_mps_nonhard23_20260613.md")
OUT_MD_ZH = Path("validation/w7900_large_mps_nonhard23_20260613.zh-CN.md")

BLOCK_BEGIN = "<!-- W7900_LARGE_MPS_NONHARD23_20260613_BEGIN -->"
BLOCK_END = "<!-- W7900_LARGE_MPS_NONHARD23_20260613_END -->"

def read_csv(path):
    if not path.exists():
        raise SystemExit(f"[error] missing required file: {path}")
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def stem_case(name):
    name = str(name).strip()
    return name[:-4] if name.endswith(".mps") else name

def fnum(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default

def fmt(value, ndigits=6):
    return f"{value:.{ndigits}f}"

def fmt_short(value):
    if value >= 100:
        return f"{value:.2f}"
    if value >= 10:
        return f"{value:.3f}"
    return f"{value:.6f}"

def markdown_table(headers, rows):
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(out)

def status_counts(rows, field):
    counts = {}
    for row in rows:
        key = row.get(field, "") or "UNKNOWN"
        counts[key] = counts.get(key, 0) + 1
    return counts

def combine_solver_rows():
    initial = read_csv(INITIAL_CSV)
    watch = read_csv(WATCH_CSV)
    near = read_csv(NEAR_CSV)

    by_case = {}
    source = {}
    for row in initial:
        case = stem_case(row["case"])
        row = dict(row)
        row["case"] = case
        by_case[case] = row
        source[case] = "initial17_safe"

    near_cases = {stem_case(row["case"]) for row in near}

    for row in watch:
        case = stem_case(row["case"])
        if case in near_cases:
            continue
        row = dict(row)
        row["case"] = case
        by_case[case] = row
        source[case] = "watchlist6_900s"

    for row in near:
        case = stem_case(row["case"])
        row = dict(row)
        row["case"] = case
        by_case[case] = row
        source[case] = "near_optimal2_1800s"

    rows = []
    for case in sorted(by_case):
        row = dict(by_case[case])
        row["source_group"] = source[case]
        rows.append(row)
    return rows

def combine_runtime_rows():
    runtime_files = [
        (INITIAL_RUNTIME_CSV, "initial17_safe"),
        (WATCH_RUNTIME_CSV, "watchlist6_900s"),
        (NEAR_RUNTIME_CSV, "near_optimal2_1800s"),
    ]
    rows_by_case = {}
    near_cases = {stem_case(r["case"]) for r in read_csv(NEAR_RUNTIME_CSV)}

    for path, group in runtime_files:
        for row in read_csv(path):
            case = stem_case(row["case"])
            if group == "watchlist6_900s" and case in near_cases:
                continue
            row = dict(row)
            row["case"] = case + ".mps"
            row["source_group"] = group
            rows_by_case[case] = row
    return [rows_by_case[c] for c in sorted(rows_by_case)]

def historical_totals(cases):
    if not HIST_CSV.exists():
        return {}
    hist_rows = read_csv(HIST_CSV)
    by_case = {stem_case(r["case"]): r for r in hist_rows}
    selected = [by_case[c] for c in cases if c in by_case]
    devices = [
        ("RTX 3090", "rtx3090_wall", "rtx3090_solve"),
        ("Radeon 890M", "radeon890m_wall", "radeon890m_solve"),
        ("RTX 4090D", "rtx4090d_wall", "rtx4090d_solve"),
        ("H100", "h100_wall", "h100_solve"),
    ]
    out = {}
    for device, wall_key, solve_key in devices:
        out[device] = {
            "wall": sum(fnum(r.get(wall_key, "")) for r in selected),
            "solve": sum(fnum(r.get(solve_key, "")) for r in selected),
        }
    return out

def insert_or_replace(path, block, anchors):
    p = Path(path)
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

def build_docs(rows):
    total_wall = sum(fnum(r["wall_seconds"]) for r in rows)
    total_solve = sum(fnum(r["dSolvingTime"]) for r in rows)
    total_matvec = sum(fnum(r["DeviceMatVecProdTime"]) for r in rows)
    cases = [r["case"] for r in rows]
    term_counts = status_counts(rows, "terminationCode")
    runtime_counts = status_counts(rows, "runtime_status")
    source_counts = status_counts(rows, "source_group")
    hist = historical_totals(cases)

    compare_rows = [["W7900 / ROCm", fmt(total_wall), fmt(total_solve), "1.00x", "1.00x"]]
    for device in ["H100", "RTX 3090", "RTX 4090D", "Radeon 890M"]:
        if device not in hist:
            continue
        wall = hist[device]["wall"]
        solve = hist[device]["solve"]
        compare_rows.append([
            device,
            fmt(wall),
            fmt(solve),
            f"{wall / total_wall:.2f}x" if total_wall else "NA",
            f"{solve / total_solve:.2f}x" if total_solve else "NA",
        ])

    slowest = sorted(rows, key=lambda r: fnum(r["dSolvingTime"]), reverse=True)[:10]
    slowest_rows = [[
        r["case"], r["source_group"], r["terminationCode"], r["nIter"],
        fmt_short(fnum(r["wall_seconds"])), fmt_short(fnum(r["dSolvingTime"])),
        fmt_short(fnum(r["DeviceMatVecProdTime"])), r["dRelDualityGap"]
    ] for r in slowest]

    full_rows = [[
        r["case"], r["source_group"], r["runtime_status"], r["terminationCode"],
        r["primalCode"], r["dualCode"], r["nIter"],
        fmt_short(fnum(r["wall_seconds"])), fmt_short(fnum(r["dSolvingTime"])),
        r["dRelPrimalFeas"], r["dRelDualFeas"], r["dRelDualityGap"]
    ] for r in sorted(rows, key=lambda x: x["case"])]

    summary_table = markdown_table(["Metric", "Value"], [
        ["Cases", len(rows)],
        ["Runtime status", ", ".join(f"{k}: {v}" for k, v in sorted(runtime_counts.items()))],
        ["Termination status", ", ".join(f"{k}: {v}" for k, v in sorted(term_counts.items()))],
        ["Source groups", ", ".join(f"{k}: {v}" for k, v in sorted(source_counts.items()))],
        ["Total wall time", fmt(total_wall) + " s"],
        ["Total solve time", fmt(total_solve) + " s"],
        ["Total DeviceMatVecProdTime", fmt(total_matvec) + " s"],
    ])
    compare_table = markdown_table(["Device", "Wall time sum", "Solve time sum", "Wall vs W7900", "Solve vs W7900"], compare_rows)
    slowest_table = markdown_table(["Case", "Source group", "Termination", "nIter", "Wall time", "Solve time", "Matvec time", "Rel gap"], slowest_rows)
    full_table = markdown_table(
        ["Case", "Source group", "Runtime", "Termination", "Primal", "Dual", "nIter", "Wall time", "Solve time", "Rel primal", "Rel dual", "Rel gap"],
        full_rows,
    )

    en = f'''# W7900 large-MPS non-hard23 baseline 20260613

> 中文: [w7900_large_mps_nonhard23_20260613.zh-CN.md](w7900_large_mps_nonhard23_20260613.zh-CN.md)

> Validation index: [README.md](README.md)

CSV sources: [solver summary](w7900_large_mps_nonhard23_20260613.csv), [runtime summary](w7900_large_mps_nonhard23_20260613_runtime.csv)

## Scope

This document records the W7900 / `gfx1100` large-MPS baseline for the 23 non-hard cases.

It combines:

- `initial17_safe`: 17 safe cases, all `OPTIMAL`.
- `watchlist6_900s`: 4 watchlist cases that reached `OPTIMAL` within the 900-second diagnostic run.
- `near_optimal2_1800s`: `Primal2_1000` and `s100`, which were near-optimal at 900 seconds and reached `OPTIMAL` in the 1800-second follow-up.

The remaining 3 cases are intentionally excluded from this non-hard baseline and should be documented separately as hard-case behavior:

- `dlr1.mps`
- `Dual2_5000.mps`
- `fhnw-binschedule1.mps`

## Configuration

```text
Platform: AMD Radeon PRO W7900 / gfx1100
Backend: ROCm/HIP
Run date: 2026-06-13
Main limits: nIterLim=1000000000, dTimeLim=7200 seconds where applicable
Short diagnostic limits: 900 seconds for watchlist6, 1800 seconds for near_optimal2
Primary metrics: external wall time and solver JSON dSolvingTime
```

## Summary

{summary_table}

## Cross-device reference on the same 23 cases

The existing cross-device large-MPS baseline is used only as a reference. This table sums only the matching 23 non-hard cases.

{compare_table}

## Slowest W7900 non-hard cases by solve time

{slowest_table}

## Full W7900 per-case results

{full_table}

## Interpretation

All 23 non-hard large-MPS cases reached `OPTIMAL` on W7900.

The two 900-second near-optimal cases, `Primal2_1000` and `s100`, both reached `OPTIMAL` when rerun with the 1800-second follow-up limit. Therefore they should be treated as slow but solvable non-hard cases, not as hard-case failures.

The remaining hard3 cases should stay outside the primary large-MPS baseline until they are analyzed separately.
'''
    zh = f'''# W7900 large-MPS non-hard23 baseline 20260613

> English: [w7900_large_mps_nonhard23_20260613.md](w7900_large_mps_nonhard23_20260613.md)

> Validation 索引: [README.zh-CN.md](README.zh-CN.md)

CSV 来源: [solver summary](w7900_large_mps_nonhard23_20260613.csv), [runtime summary](w7900_large_mps_nonhard23_20260613_runtime.csv)

## 范围

本文记录 W7900 / `gfx1100` 上 23 个 non-hard large-MPS case 的 baseline。

它合并了：

- `initial17_safe`：17 个较安全 case，全部 `OPTIMAL`。
- `watchlist6_900s`：watchlist 中 4 个在 900 秒诊断内达到 `OPTIMAL` 的 case。
- `near_optimal2_1800s`：`Primal2_1000` 和 `s100`，它们在 900 秒时接近最优，并在 1800 秒加时中达到 `OPTIMAL`。

剩余 3 个 case 不纳入这个 non-hard baseline，应作为 hard-case behavior 单独记录：

- `dlr1.mps`
- `Dual2_5000.mps`
- `fhnw-binschedule1.mps`

## 配置

```text
平台: AMD Radeon PRO W7900 / gfx1100
后端: ROCm/HIP
运行日期: 2026-06-13
主运行限制: nIterLim=1000000000，dTimeLim=7200 seconds where applicable
短诊断限制: watchlist6 为 900 秒，near_optimal2 为 1800 秒
主要指标: external wall time 和 solver JSON dSolvingTime
```

## 汇总

{summary_table}

## 同 23 个 case 的跨设备参考

已有跨设备 large-MPS baseline 只作为参考。下表只汇总与本次 23 个 non-hard case 重合的部分。

{compare_table}

## W7900 non-hard case 中 solve time 最慢的 case

{slowest_table}

## W7900 全量 per-case 结果

{full_table}

## 解释

23 个 non-hard large-MPS case 在 W7900 上全部达到 `OPTIMAL`。

`Primal2_1000` 和 `s100` 在 900 秒短诊断时没有达到 `OPTIMAL`，但 gap 已经接近阈值；在 1800 秒加时中二者都达到 `OPTIMAL`。因此它们应该被视为 slow but solvable non-hard cases，而不是 hard-case failure。

剩余 hard3 case 在完成单独分析前，不应混入主要 large-MPS baseline。
'''
    OUT_MD.write_text(en.rstrip() + "\n")
    OUT_MD_ZH.write_text(zh.rstrip() + "\n")
    print("[ok] wrote", OUT_MD)
    print("[ok] wrote", OUT_MD_ZH)

def update_indexes():
    block_validation_en = f'''{BLOCK_BEGIN}
## W7900 / gfx1100 large-MPS non-hard23 baseline

| File | Description |
|---|---|
| [w7900_large_mps_nonhard23_20260613.md](w7900_large_mps_nonhard23_20260613.md) | W7900 / `gfx1100` 23-case non-hard large-MPS baseline |
| [w7900_large_mps_nonhard23_20260613.zh-CN.md](w7900_large_mps_nonhard23_20260613.zh-CN.md) | Chinese W7900 23-case non-hard large-MPS baseline |
| [w7900_large_mps_nonhard23_20260613.csv](w7900_large_mps_nonhard23_20260613.csv) | Combined parsed solver summary CSV |
| [w7900_large_mps_nonhard23_20260613_runtime.csv](w7900_large_mps_nonhard23_20260613_runtime.csv) | Combined runtime wall-time CSV |
| [w7900_large_mps_watchlist6_diag_900s_20260613.csv](w7900_large_mps_watchlist6_diag_900s_20260613.csv) | 900-second watchlist diagnostic CSV |
| [w7900_large_mps_near_optimal2_1800s_20260613.csv](w7900_large_mps_near_optimal2_1800s_20260613.csv) | 1800-second near-optimal follow-up CSV |
{BLOCK_END}'''
    block_validation_zh = f'''{BLOCK_BEGIN}
## W7900 / gfx1100 large-MPS non-hard23 baseline

| 文件 | 说明 |
|---|---|
| [w7900_large_mps_nonhard23_20260613.md](w7900_large_mps_nonhard23_20260613.md) | W7900 / `gfx1100` 23-case non-hard large-MPS baseline 英文汇总 |
| [w7900_large_mps_nonhard23_20260613.zh-CN.md](w7900_large_mps_nonhard23_20260613.zh-CN.md) | W7900 23-case non-hard large-MPS baseline 中文汇总 |
| [w7900_large_mps_nonhard23_20260613.csv](w7900_large_mps_nonhard23_20260613.csv) | 合并后的 parsed solver summary CSV |
| [w7900_large_mps_nonhard23_20260613_runtime.csv](w7900_large_mps_nonhard23_20260613_runtime.csv) | 合并后的 runtime wall-time CSV |
| [w7900_large_mps_watchlist6_diag_900s_20260613.csv](w7900_large_mps_watchlist6_diag_900s_20260613.csv) | 900 秒 watchlist 诊断 CSV |
| [w7900_large_mps_near_optimal2_1800s_20260613.csv](w7900_large_mps_near_optimal2_1800s_20260613.csv) | 1800 秒 near-optimal follow-up CSV |
{BLOCK_END}'''
    block_docs = f'''{BLOCK_BEGIN}
| W7900 large-MPS non-hard23 baseline / W7900 large-MPS non-hard23 baseline | [../validation/w7900_large_mps_nonhard23_20260613.md](../validation/w7900_large_mps_nonhard23_20260613.md) | [../validation/w7900_large_mps_nonhard23_20260613.zh-CN.md](../validation/w7900_large_mps_nonhard23_20260613.zh-CN.md) | [solver CSV](../validation/w7900_large_mps_nonhard23_20260613.csv), [runtime CSV](../validation/w7900_large_mps_nonhard23_20260613_runtime.csv) |
{BLOCK_END}'''
    insert_or_replace("validation/README.md", block_validation_en, ["## Related project docs", "## W7900 / gfx1100 large-MPS initial17 safe baseline"])
    insert_or_replace("validation/README.zh-CN.md", block_validation_zh, ["## 相关项目文档", "## W7900 / gfx1100 large-MPS initial17 safe baseline"])
    insert_or_replace("docs/README.md", block_docs, ["| W7900 large-MPS initial17 safe baseline / W7900 large-MPS initial17 safe baseline", "## Benchmarks and numerical behavior / Benchmark 与数值行为"])

def main():
    rows = combine_solver_rows()
    runtime_rows = combine_runtime_rows()
    if len(rows) != 23:
        raise SystemExit(f"[error] expected 23 solver rows, got {len(rows)}")
    if any(r.get("terminationCode") != "OPTIMAL" for r in rows):
        bad = [(r.get("case"), r.get("terminationCode")) for r in rows if r.get("terminationCode") != "OPTIMAL"]
        raise SystemExit(f"[error] non-OPTIMAL rows in nonhard23: {bad}")

    write_csv(OUT_CSV, rows, list(rows[0].keys()))
    print("[ok] wrote", OUT_CSV)
    write_csv(OUT_RUNTIME_CSV, runtime_rows, list(runtime_rows[0].keys()))
    print("[ok] wrote", OUT_RUNTIME_CSV)
    build_docs(rows)
    update_indexes()
    print("[done] W7900 non-hard23 documentation generated")

if __name__ == "__main__":
    main()
