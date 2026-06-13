#!/usr/bin/env python3
import csv
import html
from pathlib import Path


NONHARD23_CSV = Path("validation/w7900_large_mps_nonhard23_20260613.csv")
HIST_CSV = Path("results/benchmarks/large_mps_per_case_timing_summary_20260610.csv")

ASSET_DIR = Path("docs/assets/w7900")
DOC_EN = Path("docs/W7900_PERFORMANCE_BEHAVIOR.md")
DOC_ZH = Path("docs/W7900_PERFORMANCE_BEHAVIOR.zh-CN.md")

BLOCK_BEGIN = "<!-- W7900_PERFORMANCE_BEHAVIOR_20260614_BEGIN -->"
BLOCK_END = "<!-- W7900_PERFORMANCE_BEHAVIOR_20260614_END -->"


def read_csv(path):
    if not path.exists():
        raise SystemExit(f"[error] missing required file: {path}")
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def fnum(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def stem_case(name):
    s = str(name).strip()
    return s[:-4] if s.endswith(".mps") else s


def fmt(x, ndigits=3):
    return f"{x:.{ndigits}f}"


def fmt_ratio(x):
    if x >= 100:
        return f"{x:.1f}x"
    if x >= 10:
        return f"{x:.2f}x"
    return f"{x:.3f}x"


def markdown_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |"]
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(out)


def load_rows():
    rows = read_csv(NONHARD23_CSV)
    hist = read_csv(HIST_CSV) if HIST_CSV.exists() else []
    hist_by_case = {stem_case(r["case"]): r for r in hist}
    return rows, hist_by_case


def make_bar_svg(path, title, data, unit="", width=960, row_h=36, max_items=None):
    if max_items:
        data = data[:max_items]
    max_v = max([float(v) for _, v in data], default=1.0)
    margin_left = 230
    margin_right = 140
    margin_top = 62
    margin_bottom = 34
    height = margin_top + margin_bottom + row_h * len(data)
    bar_max = width - margin_left - margin_right

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="30" text-anchor="middle" font-size="20" font-family="Arial, sans-serif" font-weight="700">{html.escape(title)}</text>',
    ]

    for i, (label, value) in enumerate(data):
        value = float(value)
        y = margin_top + i * row_h
        bar_w = 0 if max_v == 0 else value / max_v * bar_max
        parts.append(f'<text x="{margin_left-12}" y="{y+23}" text-anchor="end" font-size="13" font-family="Arial, sans-serif">{html.escape(label)}</text>')
        parts.append(f'<rect x="{margin_left}" y="{y+7}" width="{bar_w:.2f}" height="22" rx="3" fill="#6b7280"/>')
        if unit == "x":
            text = fmt_ratio(value)
        elif unit:
            text = f"{value:.2f}{unit}"
        else:
            text = f"{value:.2f}"
        parts.append(f'<text x="{margin_left + bar_w + 8}" y="{y+23}" font-size="13" font-family="Arial, sans-serif">{html.escape(text)}</text>')

    parts.append(f'<text x="{margin_left}" y="{height-10}" font-size="12" font-family="Arial, sans-serif" fill="#555">Generated from repository CSV summaries. Higher is better for speedup charts; lower is better for time charts.</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n")


def make_category_svg(path, counts, width=760, height=330):
    labels = list(counts.keys())
    values = [counts[k] for k in labels]
    total = sum(values) or 1
    max_v = max(values) if values else 1
    margin_left = 210
    margin_top = 60
    row_h = 48
    bar_max = width - margin_left - 120

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="30" text-anchor="middle" font-size="20" font-family="Arial, sans-serif" font-weight="700">W7900 non-hard23 case classes</text>',
    ]
    for i, label in enumerate(labels):
        value = counts[label]
        y = margin_top + i * row_h
        bar_w = value / max_v * bar_max if max_v else 0
        pct = value / total * 100
        parts.append(f'<text x="{margin_left-12}" y="{y+28}" text-anchor="end" font-size="14" font-family="Arial, sans-serif">{html.escape(label)}</text>')
        parts.append(f'<rect x="{margin_left}" y="{y+10}" width="{bar_w:.2f}" height="24" rx="3" fill="#6b7280"/>')
        parts.append(f'<text x="{margin_left + bar_w + 8}" y="{y+28}" font-size="14" font-family="Arial, sans-serif">{value} ({pct:.1f}%)</text>')
    parts.append('<text x="20" y="305" font-size="12" font-family="Arial, sans-serif" fill="#555">Fast: solve &lt; 10s; medium: 10–120s; slow-but-solvable: &gt; 120s and OPTIMAL; hard3 is tracked separately.</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n")


def classify_case(row):
    solve = fnum(row["dSolvingTime"])
    if solve < 10:
        return "fast (<10s)"
    if solve <= 120:
        return "medium (10-120s)"
    return "slow-but-solvable (>120s)"


def make_assets(rows, hist_by_case):
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    speedup_890m = []
    speedup_best_cuda = []
    w7900_solve_times = []

    for r in rows:
        case = stem_case(r["case"])
        w = fnum(r["dSolvingTime"])
        h = hist_by_case.get(case, {})
        solve_890m = fnum(h.get("radeon890m_solve", ""))
        cuda_solves = [
            fnum(h.get("rtx3090_solve", "")),
            fnum(h.get("rtx4090d_solve", "")),
            fnum(h.get("h100_solve", "")),
        ]
        cuda_solves = [x for x in cuda_solves if x > 0]
        if w > 0 and solve_890m > 0:
            speedup_890m.append((case, solve_890m / w))
        if w > 0 and cuda_solves:
            best_cuda = min(cuda_solves)
            speedup_best_cuda.append((case, best_cuda / w))
        w7900_solve_times.append((case, w))

    speedup_890m.sort(key=lambda x: x[1], reverse=True)
    speedup_best_cuda.sort(key=lambda x: x[1], reverse=True)
    w7900_solve_times.sort(key=lambda x: x[1], reverse=True)

    make_bar_svg(ASSET_DIR / "w7900_nonhard23_speedup_vs_890m.svg", "W7900 solve-time speedup vs Radeon 890M", speedup_890m, unit="x", max_items=15)
    make_bar_svg(ASSET_DIR / "w7900_nonhard23_relative_to_best_cuda.svg", "Best CUDA solve time divided by W7900 solve time", speedup_best_cuda, unit="x", max_items=15)
    make_bar_svg(ASSET_DIR / "w7900_nonhard23_solve_time_by_case.svg", "W7900 solve time by case", w7900_solve_times, unit="s", max_items=15)

    counts = {"fast (<10s)": 0, "medium (10-120s)": 0, "slow-but-solvable (>120s)": 0, "hard3 (separate)": 3}
    for r in rows:
        counts[classify_case(r)] += 1
    make_category_svg(ASSET_DIR / "w7900_nonhard23_case_classes.svg", counts)


def build_docs(rows, hist_by_case):
    total_wall = sum(fnum(r["wall_seconds"]) for r in rows)
    total_solve = sum(fnum(r["dSolvingTime"]) for r in rows)
    total_matvec = sum(fnum(r["DeviceMatVecProdTime"]) for r in rows)

    speedup_rows = []
    suitability_rows = []
    for r in rows:
        case = stem_case(r["case"])
        w = fnum(r["dSolvingTime"])
        h = hist_by_case.get(case, {})
        solve_890m = fnum(h.get("radeon890m_solve", ""))
        if w > 0 and solve_890m > 0:
            speedup_rows.append([case, fmt(solve_890m), fmt(w), fmt_ratio(solve_890m / w), r["source_group"]])
        suitability_rows.append([case, classify_case(r), r["nIter"], fmt(fnum(r["dSolvingTime"])), r["dRelDualityGap"]])

    speedup_rows = sorted(speedup_rows, key=lambda x: float(x[3].replace("x", "")), reverse=True)[:12]
    suitability_rows = sorted(suitability_rows, key=lambda x: float(x[3]), reverse=True)

    en = f"""# W7900 performance behavior analysis

> 中文: [W7900_PERFORMANCE_BEHAVIOR.zh-CN.md](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)

This document explains the current W7900 / `gfx1100` performance behavior beyond the raw benchmark tables. It is intended to support later competition reports and ROCm profiling/tuning.

## What this analysis adds

The current W7900 evidence is not only that the code runs. The branch now has a reproducible 23-case non-hard large-MPS baseline, plus a hard3 split for difficult convergence behavior.

This analysis adds three points:

1. theoretical value: why PDLP-style LP solvers are suitable for GPU acceleration;
2. application value: why W7900 is relevant for large LP/MPS workloads;
3. performance interpretation: why some cases are fast, while others are slow or hard.

## Hardware and solver interpretation

W7900 is attractive for large LP/MPS workloads because it combines high FP32 throughput with 48GB GDDR6 memory, a 384-bit memory interface, 864GB/s peak memory bandwidth, and ECC support. These properties are useful when a solver repeatedly touches large sparse matrices and dense vectors.

However, PDLP total time should not be interpreted as pure GPU throughput:

```text
total time ≈ per-iteration cost × number of iterations
```

The per-iteration cost is related to sparse matrix-vector products, vector operations, reductions, and data movement. The iteration count is controlled by the numerical path: residuals, duality gap, step-size evolution, scaling, restarts, and problem conditioning.

## Non-hard23 result summary

{markdown_table(["Metric", "Value"], [
    ["Cases", len(rows)],
    ["Termination", "23/23 OPTIMAL"],
    ["Total wall time", fmt(total_wall) + " s"],
    ["Total solve time", fmt(total_solve) + " s"],
    ["Total DeviceMatVecProdTime", fmt(total_matvec) + " s"],
])}

## W7900 vs 890M speedup

The following table and chart focus on solve time, which is closer to solver computation than end-to-end wall time.

{markdown_table(["Case", "890M solve", "W7900 solve", "Speedup", "Source group"], speedup_rows)}

![W7900 speedup vs 890M](assets/w7900/w7900_nonhard23_speedup_vs_890m.svg)

## W7900 relative to best CUDA reference

Values above 1 mean W7900 is faster than the best CUDA reference on that case; values below 1 mean the best CUDA reference is faster.

![W7900 relative to best CUDA](assets/w7900/w7900_nonhard23_relative_to_best_cuda.svg)

## Case classes

![W7900 case classes](assets/w7900/w7900_nonhard23_case_classes.svg)

{markdown_table(["Case", "Class", "nIter", "W7900 solve time", "Rel gap"], suitability_rows)}

## What W7900 appears to be good at

Current data suggests that W7900 is most suitable for cases with:

- enough scale to amortize HIP setup, file parsing, matrix transfer, and launch overhead;
- stable convergence behavior, so the iteration count does not dominate;
- high sparse matrix-vector and vector-operation work, where memory bandwidth and parallelism matter;
- large memory footprints where 48GB VRAM and ECC support are valuable.

## Why some cases are slow

A slow W7900 result does not always imply a slow GPU. It can happen when:

- the LP instance needs many PDLP iterations;
- the gap trajectory stalls near the tolerance;
- adaptive restart or step-size behavior differs across hardware/backend paths;
- reductions or sparse operations expose ROCm/gfx1100 kernel inefficiencies;
- fixed overhead dominates tiny or very short cases.

## Tuning implication

The next ROCm tuning stage should not only optimize kernels. It should also record numerical trajectory evidence:

- per-case `nIter`;
- `DeviceMatVecProdTime`;
- residuals and duality gap;
- HIP/kernel/reduction profile;
- before/after changes on the same case list.

Hard3 should stay separate until its convergence trajectory is documented.
"""

    zh = f"""# W7900 性能行为分析

> English: [W7900_PERFORMANCE_BEHAVIOR.md](W7900_PERFORMANCE_BEHAVIOR.md)

本文解释当前 W7900 / `gfx1100` 的性能行为，不只是重复 benchmark 表格。它用于支撑后续比赛报告和 ROCm profiling/tuning。

## 本文补充什么

当前 W7900 证据已经不只是“代码能跑”。分支已经有可复现的 23-case non-hard large-MPS baseline，并且把困难收敛行为拆成 hard3 单独处理。

本文补充三点：

1. 理论价值：为什么 PDLP 类 LP 求解器适合 GPU 加速；
2. 应用价值：为什么 W7900 对 large LP/MPS 工作负载有意义；
3. 性能解释：为什么有些 case 快，有些 case 慢或 hard。

## 硬件与求解器解释

W7900 对 large LP/MPS 有吸引力，是因为它同时具备较高 FP32 吞吐、48GB GDDR6 显存、384-bit 显存接口、864GB/s 峰值显存带宽和 ECC 支持。这些特性适合反复访问大规模稀疏矩阵和稠密向量的求解器。

但是，PDLP 总时间不能只理解成 GPU 算力：

```text
total time ≈ per-iteration cost × number of iterations
```

单次迭代成本与稀疏矩阵向量乘、向量操作、归约和数据移动相关。迭代次数则由数值路径决定：residual、duality gap、step-size 演化、scaling、restart 和问题条件数都会影响收敛。

## Non-hard23 结果汇总

{markdown_table(["指标", "数值"], [
    ["Case 数量", len(rows)],
    ["Termination", "23/23 OPTIMAL"],
    ["Total wall time", fmt(total_wall) + " s"],
    ["Total solve time", fmt(total_solve) + " s"],
    ["Total DeviceMatVecProdTime", fmt(total_matvec) + " s"],
])}

## W7900 相对 890M 的加速

下表和图使用 solve time，更接近 solver 计算本身，而不是端到端 wall time。

{markdown_table(["Case", "890M solve", "W7900 solve", "Speedup", "Source group"], speedup_rows)}

![W7900 speedup vs 890M](assets/w7900/w7900_nonhard23_speedup_vs_890m.svg)

## W7900 相对最佳 CUDA 参考

数值大于 1 表示 W7900 在该 case 上快于最佳 CUDA 参考；小于 1 表示最佳 CUDA 参考更快。

![W7900 relative to best CUDA](assets/w7900/w7900_nonhard23_relative_to_best_cuda.svg)

## Case 分类

![W7900 case classes](assets/w7900/w7900_nonhard23_case_classes.svg)

{markdown_table(["Case", "类别", "nIter", "W7900 solve time", "Rel gap"], suitability_rows)}

## W7900 更适合什么类型的数据

当前数据表明，W7900 更适合：

- 规模足够大，能够摊薄 HIP setup、文件解析、矩阵搬运和 launch 固定开销的 case；
- 收敛轨迹稳定，迭代次数不会极端膨胀的 case；
- SpMV 和向量操作占比较高，能够利用显存带宽和并行度的 case；
- 显存占用较大、需要 48GB VRAM 和 ECC 支持的工作负载。

## 为什么有些 case 慢

W7900 上某个 case 慢，不一定说明 GPU 算得慢，可能是：

- LP instance 需要大量 PDLP 迭代；
- gap trajectory 在阈值附近停滞；
- adaptive restart 或 step-size 在不同硬件/后端上的路径不同；
- reduction 或 sparse operation 暴露出 ROCm/gfx1100 kernel 效率问题；
- tiny case 中固定开销占主导。

## 对调优的启示

下一阶段 ROCm tuning 不能只盯 kernel 时间，还要记录数值轨迹：

- per-case `nIter`；
- `DeviceMatVecProdTime`；
- residual 与 duality gap；
- HIP/kernel/reduction profile；
- 同一 case list 上的 before/after 变化。

Hard3 在完成收敛轨迹记录前，仍应保持单独分组。
"""

    DOC_EN.write_text(en.rstrip() + "\n")
    DOC_ZH.write_text(zh.rstrip() + "\n")


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


def update_indexes():
    docs_block = f"""{BLOCK_BEGIN}
| W7900 performance behavior / W7900 性能行为分析 | [W7900_PERFORMANCE_BEHAVIOR.md](W7900_PERFORMANCE_BEHAVIOR.md) | [W7900_PERFORMANCE_BEHAVIOR.zh-CN.md](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md) | Theory/application value, speedup charts, case classes, and tuning implications |
{BLOCK_END}"""
    insert_or_replace("docs/README.md", docs_block, ["| W7900 current status / W7900 当前状态", "## Benchmarks and numerical behavior / Benchmark 与数值行为"])

    status_block_en = f"""{BLOCK_BEGIN}
## Related performance behavior analysis

For an explanation of why W7900 is fast on some large-MPS cases but slow on others, see:

- [W7900 performance behavior analysis](W7900_PERFORMANCE_BEHAVIOR.md)
- [W7900 性能行为分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)
{BLOCK_END}"""
    insert_or_replace("docs/W7900_CURRENT_STATUS.md", status_block_en, ["## Next documentation tasks", "## Why W7900 can be fast on some cases and slow on others"])

    status_block_zh = f"""{BLOCK_BEGIN}
## 相关性能行为分析

关于为什么 W7900 在部分 large-MPS case 上快、在另一些 case 上慢，详见：

- [W7900 performance behavior analysis](W7900_PERFORMANCE_BEHAVIOR.md)
- [W7900 性能行为分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)
{BLOCK_END}"""
    insert_or_replace("docs/W7900_CURRENT_STATUS.zh-CN.md", status_block_zh, ["## 下一步文档任务", "## 为什么 W7900 有些 case 快、有些 case 慢"])


def main():
    rows, hist_by_case = load_rows()
    if len(rows) != 23:
        raise SystemExit(f"[error] expected 23 non-hard rows, got {len(rows)}")
    if any(r.get("terminationCode") != "OPTIMAL" for r in rows):
        raise SystemExit("[error] non-hard23 CSV contains non-OPTIMAL row")
    make_assets(rows, hist_by_case)
    build_docs(rows, hist_by_case)
    update_indexes()
    print("[done] W7900 performance behavior docs and charts generated")


if __name__ == "__main__":
    main()
