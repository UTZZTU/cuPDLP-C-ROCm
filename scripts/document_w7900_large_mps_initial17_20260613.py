#!/usr/bin/env python3
import csv
from pathlib import Path


W7900_CSV = Path("validation/w7900_large_mps_initial17_safe_20260613.csv")
RUNTIME_CSV = Path("validation/w7900_large_mps_initial17_safe_20260613_runtime.csv")
HIST_CSV = Path("results/benchmarks/large_mps_per_case_timing_summary_20260610.csv")

MD_EN = Path("validation/w7900_large_mps_initial17_safe_20260613.md")
MD_ZH = Path("validation/w7900_large_mps_initial17_safe_20260613.zh-CN.md")

BLOCK_BEGIN = "<!-- W7900_LARGE_MPS_INITIAL17_20260613_BEGIN -->"
BLOCK_END = "<!-- W7900_LARGE_MPS_INITIAL17_20260613_END -->"


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


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


def sum_field(rows, field):
    return sum(fnum(r.get(field, "")) for r in rows)


def status_counts(rows, field):
    counts = {}
    for row in rows:
        key = row.get(field, "") or "UNKNOWN"
        counts[key] = counts.get(key, 0) + 1
    return counts


def load_historical_for_cases(cases):
    if not HIST_CSV.exists():
        return {}

    rows = read_csv(HIST_CSV)
    by_case = {r["case"]: r for r in rows}
    selected = [by_case[c + ".mps"] for c in cases if c + ".mps" in by_case]

    devices = [
        ("RTX 3090", "rtx3090_wall", "rtx3090_solve"),
        ("Radeon 890M", "radeon890m_wall", "radeon890m_solve"),
        ("RTX 4090D", "rtx4090d_wall", "rtx4090d_solve"),
        ("H100", "h100_wall", "h100_solve"),
    ]

    totals = {}
    for name, wall_key, solve_key in devices:
        totals[name] = {
            "wall": sum(fnum(r.get(wall_key, "")) for r in selected),
            "solve": sum(fnum(r.get(solve_key, "")) for r in selected),
        }
    return totals


def insert_or_replace(path, block, anchor_candidates):
    p = Path(path)
    s = p.read_text()

    if BLOCK_BEGIN in s and BLOCK_END in s:
        before = s.split(BLOCK_BEGIN)[0].rstrip()
        after = s.split(BLOCK_END, 1)[1].lstrip()
        p.write_text(before + "\n\n" + block.rstrip() + "\n\n" + after)
        print("[ok] replaced block in", path)
        return

    for anchor in anchor_candidates:
        if anchor in s:
            p.write_text(s.replace(anchor, block.rstrip() + "\n\n" + anchor, 1))
            print("[ok] inserted block in", path)
            return

    p.write_text(s.rstrip() + "\n\n" + block.rstrip() + "\n")
    print("[ok] appended block in", path)


def build_docs():
    rows = read_csv(W7900_CSV)
    runtime_rows = read_csv(RUNTIME_CSV) if RUNTIME_CSV.exists() else []

    cases = [r["case"] for r in rows]
    case_count = len(rows)

    total_wall = sum_field(rows, "wall_seconds")
    total_solve = sum_field(rows, "dSolvingTime")
    total_matvec = sum_field(rows, "DeviceMatVecProdTime")

    termination_counts = status_counts(rows, "terminationCode")
    runtime_counts = status_counts(rows, "runtime_status")

    historical = load_historical_for_cases(cases)

    device_rows = [
        ["W7900 / ROCm", fmt(total_wall), fmt(total_solve), "1.00x", "1.00x"],
    ]
    for device in ["H100", "RTX 3090", "Radeon 890M", "RTX 4090D"]:
        if device not in historical:
            continue
        wall = historical[device]["wall"]
        solve = historical[device]["solve"]
        wall_rel = wall / total_wall if total_wall else 0.0
        solve_rel = solve / total_solve if total_solve else 0.0
        device_rows.append([
            device,
            fmt(wall),
            fmt(solve),
            f"{wall_rel:.2f}x",
            f"{solve_rel:.2f}x",
        ])

    slowest = sorted(rows, key=lambda r: fnum(r["dSolvingTime"]), reverse=True)[:8]
    slowest_rows = []
    for r in slowest:
        slowest_rows.append([
            r["case"],
            r["terminationCode"],
            r["nIter"],
            fmt_short(fnum(r["wall_seconds"])),
            fmt_short(fnum(r["dSolvingTime"])),
            fmt_short(fnum(r["DeviceMatVecProdTime"])),
            r["dRelDualityGap"],
        ])

    full_rows = []
    for r in sorted(rows, key=lambda x: x["case"]):
        full_rows.append([
            r["case"],
            r["runtime_status"],
            r["terminationCode"],
            r["primalCode"],
            r["dualCode"],
            r["nIter"],
            fmt_short(fnum(r["wall_seconds"])),
            fmt_short(fnum(r["dSolvingTime"])),
            fmt_short(fnum(r["DeviceMatVecProdTime"])),
            r["dRelPrimalFeas"],
            r["dRelDualFeas"],
            r["dRelDualityGap"],
        ])

    en = f"""# W7900 large-MPS initial17 safe baseline 20260613

> 中文: [w7900_large_mps_initial17_safe_20260613.zh-CN.md](w7900_large_mps_initial17_safe_20260613.zh-CN.md)

> Validation index: [README.md](README.md)

CSV sources: [solver summary](w7900_large_mps_initial17_safe_20260613.csv), [runtime summary](w7900_large_mps_initial17_safe_20260613_runtime.csv)

## Scope

This document records the first W7900 / `gfx1100` large-MPS initial baseline on the conservative `initial17_safe` subset.

The full downloaded large-MPS dataset contains 26 cases. For this first W7900 baseline, the run intentionally excludes the known or suspected long-running cases and records only the safer first batch:

- `initial17_safe`: completed in this document.
- `watchlist6`: to be tested later with short 600/900-second diagnostics before full runs.
- `hard3`: to be documented separately as hard-case behavior.

## Configuration

```text
Platform: AMD Radeon PRO W7900 / gfx1100
Backend: ROCm/HIP
Case list: validation/cases_w7900_large_mps_initial17_safe.txt
Run date: 2026-06-13
nIterLim: 1000000000
dTimeLim: 7200 seconds
External timeout: 7500 seconds per case
Primary metrics: external wall time and solver JSON dSolvingTime
```

## Summary

{markdown_table(["Metric", "Value"], [
    ["Cases", case_count],
    ["Runtime status", ", ".join(f"{k}: {v}" for k, v in sorted(runtime_counts.items()))],
    ["Termination status", ", ".join(f"{k}: {v}" for k, v in sorted(termination_counts.items()))],
    ["Total wall time", fmt(total_wall) + " s"],
    ["Total solve time", fmt(total_solve) + " s"],
    ["Total DeviceMatVecProdTime", fmt(total_matvec) + " s"],
])}

## Cross-device reference on the same 17 cases

The existing cross-device large-MPS baseline is used only as a reference. It was produced on the full 26-case dataset, while this table sums the matching 17 `initial17_safe` cases only.

{markdown_table(["Device", "Wall time sum", "Solve time sum", "Wall vs W7900", "Solve vs W7900"], device_rows)}

## Slowest W7900 cases by solve time

{markdown_table(["Case", "Termination", "nIter", "Wall time", "Solve time", "Matvec time", "Rel gap"], slowest_rows)}

## Full W7900 per-case results

{markdown_table([
    "Case", "Runtime", "Termination", "Primal", "Dual", "nIter",
    "Wall time", "Solve time", "Matvec time",
    "Rel primal", "Rel dual", "Rel gap",
], full_rows)}

## Follow-up plan

The `initial17_safe` subset is now a usable W7900 large-MPS baseline for the first-port stage. It should be used as the stable reference before ROCm/gfx1100 tuning.

Next large-MPS work is split into two follow-up groups:

- `validation/cases_w7900_large_mps_watchlist6.txt`: medium-risk cases that should first be run with shorter diagnostics to check the gap trajectory.
- `validation/cases_w7900_large_mps_hard3.txt`: hard cases that should be run and documented separately, not mixed into the first safe baseline.

## Interpretation

All 17 safe large-MPS cases completed successfully on W7900 with `OPTIMAL` termination.

The total W7900 wall time is close to the H100 reference on the same 17 cases, while W7900 solve time is still higher than the CUDA high-end references. This suggests the first-port W7900 path is already usable for the safe subset, but ROCm/gfx1100 kernel, reduction, data movement, and solver-path tuning still have room for improvement.
"""

    zh = f"""# W7900 large-MPS initial17 safe baseline 20260613

> English: [w7900_large_mps_initial17_safe_20260613.md](w7900_large_mps_initial17_safe_20260613.md)

> Validation 索引: [README.zh-CN.md](README.zh-CN.md)

CSV 来源: [solver summary](w7900_large_mps_initial17_safe_20260613.csv), [runtime summary](w7900_large_mps_initial17_safe_20260613_runtime.csv)

## 范围

本文记录 W7900 / `gfx1100` 上第一轮 large-MPS 初始 baseline，使用较保守的 `initial17_safe` 子集。

完整下载的数据集共有 26 个 case。本轮为了避免机器时间被极慢 case 吃掉，先只记录较安全的第一批：

- `initial17_safe`：本文已完成。
- `watchlist6`：后续先做 600/900 秒短诊断，再决定是否完整跑。
- `hard3`：作为 hard-case behavior 单独记录，不混入第一轮安全 baseline。

## 配置

```text
平台: AMD Radeon PRO W7900 / gfx1100
后端: ROCm/HIP
Case list: validation/cases_w7900_large_mps_initial17_safe.txt
运行日期: 2026-06-13
nIterLim: 1000000000
dTimeLim: 7200 seconds
外部 timeout: 7500 seconds per case
主要指标: external wall time 和 solver JSON dSolvingTime
```

## 汇总

{markdown_table(["指标", "数值"], [
    ["Case 数量", case_count],
    ["Runtime status", ", ".join(f"{k}: {v}" for k, v in sorted(runtime_counts.items()))],
    ["Termination status", ", ".join(f"{k}: {v}" for k, v in sorted(termination_counts.items()))],
    ["Total wall time", fmt(total_wall) + " s"],
    ["Total solve time", fmt(total_solve) + " s"],
    ["Total DeviceMatVecProdTime", fmt(total_matvec) + " s"],
])}

## 同 17 个 case 的跨设备参考

这里的跨设备数据只作为参考。已有 large-MPS baseline 是 26-case 全量记录；下表只汇总其中与本轮 `initial17_safe` 重合的 17 个 case。

{markdown_table(["设备", "Wall time 总和", "Solve time 总和", "Wall 相对 W7900", "Solve 相对 W7900"], device_rows)}

## W7900 solve time 最慢 case

{markdown_table(["Case", "Termination", "nIter", "Wall time", "Solve time", "Matvec time", "Rel gap"], slowest_rows)}

## W7900 全量 per-case 结果

{markdown_table([
    "Case", "Runtime", "Termination", "Primal", "Dual", "nIter",
    "Wall time", "Solve time", "Matvec time",
    "Rel primal", "Rel dual", "Rel gap",
], full_rows)}

## 后续计划

`initial17_safe` 现在可以作为 W7900 large-MPS first-port 阶段的稳定 baseline。后续 ROCm/gfx1100 调优时，应先用这批结果做对照。

后续 large-MPS 工作分成两组：

- `validation/cases_w7900_large_mps_watchlist6.txt`：中等风险 case，先跑短时间诊断，观察 gap 轨迹。
- `validation/cases_w7900_large_mps_hard3.txt`：hard cases，单独跑、单独写文档，不混入第一轮安全 baseline。

## 解释

17 个 safe large-MPS case 在 W7900 上全部达到 `OPTIMAL`。

W7900 在这 17 个 case 上的总 wall time 已经接近 H100 参考结果，但 solve time 仍高于 CUDA 高端卡参考。这说明当前 W7900 first-port 路径已经能稳定跑通 safe subset，但 ROCm/gfx1100 的 kernel、reduction、数据搬运和 solver path 仍有调优空间。
"""

    MD_EN.write_text(en.rstrip() + "\n")
    MD_ZH.write_text(zh.rstrip() + "\n")
    print("[ok] wrote", MD_EN)
    print("[ok] wrote", MD_ZH)


def update_indexes():
    validation_block_en = f"""{BLOCK_BEGIN}
## W7900 / gfx1100 large-MPS initial17 safe baseline

| File | Description |
|---|---|
| [w7900_large_mps_initial17_safe_20260613.md](w7900_large_mps_initial17_safe_20260613.md) | W7900 / `gfx1100` large-MPS initial17 safe baseline summary |
| [w7900_large_mps_initial17_safe_20260613.zh-CN.md](w7900_large_mps_initial17_safe_20260613.zh-CN.md) | Chinese W7900 large-MPS initial17 safe baseline summary |
| [w7900_large_mps_initial17_safe_20260613.csv](w7900_large_mps_initial17_safe_20260613.csv) | Parsed solver summary CSV |
| [w7900_large_mps_initial17_safe_20260613_runtime.csv](w7900_large_mps_initial17_safe_20260613_runtime.csv) | Runtime wall-time summary CSV |
| [cases_w7900_large_mps_initial17_safe.txt](cases_w7900_large_mps_initial17_safe.txt) | Completed safe first-batch large-MPS case list |
| [cases_w7900_large_mps_watchlist6.txt](cases_w7900_large_mps_watchlist6.txt) | Medium-risk large-MPS follow-up case list |
| [cases_w7900_large_mps_hard3.txt](cases_w7900_large_mps_hard3.txt) | Hard-case follow-up list |
{BLOCK_END}"""

    validation_block_zh = f"""{BLOCK_BEGIN}
## W7900 / gfx1100 large-MPS initial17 safe baseline

| 文件 | 说明 |
|---|---|
| [w7900_large_mps_initial17_safe_20260613.md](w7900_large_mps_initial17_safe_20260613.md) | W7900 / `gfx1100` large-MPS initial17 safe baseline 英文汇总 |
| [w7900_large_mps_initial17_safe_20260613.zh-CN.md](w7900_large_mps_initial17_safe_20260613.zh-CN.md) | W7900 large-MPS initial17 safe baseline 中文汇总 |
| [w7900_large_mps_initial17_safe_20260613.csv](w7900_large_mps_initial17_safe_20260613.csv) | parsed solver summary CSV |
| [w7900_large_mps_initial17_safe_20260613_runtime.csv](w7900_large_mps_initial17_safe_20260613_runtime.csv) | runtime wall-time summary CSV |
| [cases_w7900_large_mps_initial17_safe.txt](cases_w7900_large_mps_initial17_safe.txt) | 已完成的 safe 第一批 large-MPS case list |
| [cases_w7900_large_mps_watchlist6.txt](cases_w7900_large_mps_watchlist6.txt) | 后续中等风险 large-MPS case list |
| [cases_w7900_large_mps_hard3.txt](cases_w7900_large_mps_hard3.txt) | hard-case 后续列表 |
{BLOCK_END}"""

    docs_block = f"""{BLOCK_BEGIN}
| W7900 large-MPS initial17 safe baseline / W7900 large-MPS initial17 safe baseline | [../validation/w7900_large_mps_initial17_safe_20260613.md](../validation/w7900_large_mps_initial17_safe_20260613.md) | [../validation/w7900_large_mps_initial17_safe_20260613.zh-CN.md](../validation/w7900_large_mps_initial17_safe_20260613.zh-CN.md) | [solver CSV](../validation/w7900_large_mps_initial17_safe_20260613.csv), [runtime CSV](../validation/w7900_large_mps_initial17_safe_20260613_runtime.csv) |
{BLOCK_END}"""

    insert_or_replace(
        "validation/README.md",
        validation_block_en,
        ["## Related project docs", "## W7900 / gfx1100 validation summaries"],
    )
    insert_or_replace(
        "validation/README.zh-CN.md",
        validation_block_zh,
        ["## 相关项目文档", "## W7900 / gfx1100 validation 汇总"],
    )
    insert_or_replace(
        "docs/README.md",
        docs_block,
        ["| Large MPS CUDA/ROCm baseline / large MPS CUDA/ROCm baseline", "## Benchmarks and numerical behavior / Benchmark 与数值行为"],
    )


def main():
    build_docs()
    update_indexes()
    print("[done] W7900 large-MPS initial17 documentation generated")


if __name__ == "__main__":
    main()
