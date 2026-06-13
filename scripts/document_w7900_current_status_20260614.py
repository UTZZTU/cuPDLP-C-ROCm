#!/usr/bin/env python3
"""Generate W7900 current-status docs and SVG charts.

This script is intentionally stdlib-only. It reads the committed W7900
non-hard23 CSV and the existing cross-device large-MPS CSV, then writes:
  - docs/assets/w7900/*.svg
  - docs/W7900_CURRENT_STATUS.md
  - docs/W7900_CURRENT_STATUS.zh-CN.md
It also inserts one index row into docs/README.md and refreshes a few old
W7900 phrases in README.md / README.zh-CN.md when exact text is found.
"""
import csv
import html
from pathlib import Path

NONHARD23_CSV = Path("validation/w7900_large_mps_nonhard23_20260613.csv")
HIST_CSV = Path("results/benchmarks/large_mps_per_case_timing_summary_20260610.csv")
ASSET_DIR = Path("docs/assets/w7900")
DOC_EN = Path("docs/W7900_CURRENT_STATUS.md")
DOC_ZH = Path("docs/W7900_CURRENT_STATUS.zh-CN.md")

BLOCK_BEGIN = "<!-- W7900_CURRENT_STATUS_20260614_BEGIN -->"
BLOCK_END = "<!-- W7900_CURRENT_STATUS_20260614_END -->"


def read_csv(path: Path):
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


def markdown_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |"]
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(out)


def load_data():
    rows = read_csv(NONHARD23_CSV)
    hist_rows = read_csv(HIST_CSV) if HIST_CSV.exists() else []
    hist_by_case = {stem_case(r["case"]): r for r in hist_rows}
    cases = [stem_case(r["case"]) for r in rows]

    totals = {
        "W7900 / ROCm": {
            "wall": sum(fnum(r["wall_seconds"]) for r in rows),
            "solve": sum(fnum(r["dSolvingTime"]) for r in rows),
        }
    }

    devices = [
        ("H100 / CUDA", "h100_wall", "h100_solve"),
        ("RTX 3090 / CUDA", "rtx3090_wall", "rtx3090_solve"),
        ("RTX 4090D / CUDA", "rtx4090d_wall", "rtx4090d_solve"),
        ("Radeon 890M / ROCm", "radeon890m_wall", "radeon890m_solve"),
    ]
    selected_hist = [hist_by_case[c] for c in cases if c in hist_by_case]
    for label, wall_key, solve_key in devices:
        totals[label] = {
            "wall": sum(fnum(r.get(wall_key, "")) for r in selected_hist),
            "solve": sum(fnum(r.get(solve_key, "")) for r in selected_hist),
        }
    return rows, totals


def make_bar_svg(path, title, data, unit="s", width=900, row_h=42):
    max_v = max([v for _, v in data] or [1.0])
    left, right, top, bottom = 220, 120, 60, 34
    height = top + bottom + row_h * len(data)
    bar_max = width - left - right

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="30" text-anchor="middle" font-size="20" font-family="Arial, sans-serif" font-weight="700">{html.escape(title)}</text>',
    ]
    for i, (label, value) in enumerate(data):
        y = top + i * row_h
        w = 0 if max_v == 0 else value / max_v * bar_max
        parts.append(f'<text x="{left-12}" y="{y+25}" text-anchor="end" font-size="14" font-family="Arial, sans-serif">{html.escape(label)}</text>')
        parts.append(f'<rect x="{left}" y="{y+7}" width="{w:.2f}" height="24" rx="3" fill="#6b7280"/>')
        parts.append(f'<text x="{left+w+8}" y="{y+25}" font-size="14" font-family="Arial, sans-serif">{value:.2f}{html.escape(unit)}</text>')
    parts.append(f'<text x="{left}" y="{height-10}" font-size="12" font-family="Arial, sans-serif" fill="#555">Lower is better. Generated from repository CSV summaries.</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n")


def generate_charts(rows, totals):
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    wall_data = sorted([(k, v["wall"]) for k, v in totals.items()], key=lambda x: x[1])
    solve_data = sorted([(k, v["solve"]) for k, v in totals.items()], key=lambda x: x[1])
    slowest_data = sorted(
        [(r["case"], fnum(r["dSolvingTime"])) for r in rows],
        key=lambda x: x[1],
        reverse=True,
    )[:10]
    make_bar_svg(ASSET_DIR / "w7900_nonhard23_wall_compare.svg", "Non-hard23 total wall time", wall_data)
    make_bar_svg(ASSET_DIR / "w7900_nonhard23_solve_compare.svg", "Non-hard23 total solver time", solve_data)
    make_bar_svg(ASSET_DIR / "w7900_nonhard23_slowest_cases.svg", "W7900 slowest non-hard23 cases", slowest_data)


def build_docs(rows, totals):
    total_wall = totals["W7900 / ROCm"]["wall"]
    total_solve = totals["W7900 / ROCm"]["solve"]
    source_counts = {}
    for r in rows:
        source_counts[r["source_group"]] = source_counts.get(r["source_group"], 0) + 1

    compare_rows = []
    for device, values in sorted(totals.items(), key=lambda kv: kv[1]["wall"]):
        compare_rows.append([
            device,
            fmt(values["wall"]),
            fmt(values["solve"]),
            f"{values['wall']/total_wall:.2f}x" if total_wall else "NA",
            f"{values['solve']/total_solve:.2f}x" if total_solve else "NA",
        ])

    slowest = sorted(rows, key=lambda r: fnum(r["dSolvingTime"]), reverse=True)[:10]
    slowest_rows = [
        [r["case"], r["source_group"], r["nIter"], fmt(fnum(r["wall_seconds"])), fmt(fnum(r["dSolvingTime"])), r["dRelDualityGap"]]
        for r in slowest
    ]

    summary_en = markdown_table(["Metric", "Value"], [
        ["Cases", len(rows)],
        ["Termination", "23/23 OPTIMAL"],
        ["Source groups", ", ".join(f"{k}: {v}" for k, v in sorted(source_counts.items()))],
        ["W7900 total wall time", fmt(total_wall) + " s"],
        ["W7900 total solve time", fmt(total_solve) + " s"],
    ])

    compare_en = markdown_table(["Device", "Wall time sum", "Solve time sum", "Wall vs W7900", "Solve vs W7900"], compare_rows)
    slow_en = markdown_table(["Case", "Source group", "nIter", "Wall time", "Solve time", "Rel gap"], slowest_rows)

    en = f"""# W7900 current status and documentation refresh anchor

> 中文: [W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md)

This page is the current W7900 / `gfx1100` status anchor. It should be used to replace older first-port-only wording across the repository.

## Current status

The W7900 branch is no longer only an `afiro` smoke experiment. It now has:

- W7900 first-port build and smoke validation.
- W7900 Netlib 27-case baseline.
- W7900 large-MPS `initial17_safe` baseline.
- W7900 large-MPS `non-hard23` baseline.
- Remaining large-MPS hard cases intentionally split out: `dlr1.mps`, `Dual2_5000.mps`, and `fhnw-binschedule1.mps`.

## Large-MPS non-hard23 summary

{summary_en}

## Cross-device reference on matching 23 cases

{compare_en}

![Non-hard23 wall comparison](assets/w7900/w7900_nonhard23_wall_compare.svg)

![Non-hard23 solve comparison](assets/w7900/w7900_nonhard23_solve_compare.svg)

## W7900 slowest non-hard cases

{slow_en}

![W7900 slowest cases](assets/w7900/w7900_nonhard23_slowest_cases.svg)

## Theory and application value

cuPDLP/PDLP-style solvers target large-scale LP problems where the core operation is sparse matrix-vector multiplication. This is a good match for GPU acceleration, but the total time depends on both per-iteration throughput and convergence behavior.

For project reporting, this W7900 milestone demonstrates:

- A reproducible CUDA-to-ROCm migration path for a scientific computing solver.
- A large-memory AMD workstation GPU validation path for large LP/MPS workloads.
- A data-driven benchmark split between safe, slow-but-solvable, and hard-case behavior.
- A basis for future ROCm profiling and tuning with clear before-tuning baselines.

## Why W7900 can be fast on some cases and slow on others

W7900 has high FP32 throughput, large VRAM, and high memory bandwidth, so cases with enough sparse matrix-vector work and stable convergence can benefit from the hardware. However, PDLP total time is not only a hardware-throughput problem:

```text
total time ≈ per-iteration cost × number of iterations
```

For hard LP instances, small differences in sparse reductions, floating-point ordering, adaptive restart timing, step-size evolution, or residual/gap behavior can change the iteration path. That explains why W7900 can be strong on some large cases but unexpectedly slow on cases such as `s100`, `Primal2_1000`, or the excluded hard3.

## Next documentation tasks

1. Update `README.md` and `README.zh-CN.md` so W7900 is described as a validated baseline target, not merely a planned target.
2. Update `docs/README.md` and validation indexes so this page, non-hard23, initial17, watchlist6, near2, and hard3 are linked clearly.
3. Update `docs/W7900_FIRST_PORT.md` and platform notes to describe the bootstrap and volatile-machine workflow.
4. Add a hard3 note before full tuning: do not mix hard3 into the first primary baseline.
5. Start ROCm profiling/tuning only after the W7900 documentation state is consistent.
"""
    zh = f"""# W7900 当前状态与文档修订锚点

> English: [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md)

本文是 W7900 / `gfx1100` 的当前状态锚点，用来替换仓库中较旧的 first-port-only 描述。

## 当前状态

W7900 分支已经不再只是 `afiro` smoke 实验。目前已经具备：

- W7900 first-port build 与 smoke validation。
- W7900 Netlib 27-case baseline。
- W7900 large-MPS `initial17_safe` baseline。
- W7900 large-MPS `non-hard23` baseline。
- 剩余 large-MPS hard cases 单独拆出分析：`dlr1.mps`、`Dual2_5000.mps`、`fhnw-binschedule1.mps`。

## Large-MPS non-hard23 汇总

{summary_en}

## 同 23 个 case 的跨设备参考

{compare_en}

![Non-hard23 wall comparison](assets/w7900/w7900_nonhard23_wall_compare.svg)

![Non-hard23 solve comparison](assets/w7900/w7900_nonhard23_solve_compare.svg)

## W7900 最慢 non-hard cases

{slow_en}

![W7900 slowest cases](assets/w7900/w7900_nonhard23_slowest_cases.svg)

## 理论价值与应用价值

cuPDLP/PDLP 类求解器面向大规模线性规划问题，其核心操作是稀疏矩阵向量乘法，因此适合 GPU 加速。但总耗时同时取决于单次迭代开销和收敛路径。

对于项目报告，这一阶段的 W7900 工作能够体现：

- 科学计算求解器从 CUDA 到 ROCm 的可复现迁移路径。
- 大显存 AMD 工作站 GPU 面向 large LP/MPS 工作负载的验证流程。
- 基于数据的 safe、slow-but-solvable、hard-case 分层方法。
- 后续 ROCm profiling 与 tuning 的调优前 baseline。

## 为什么 W7900 有些 case 快、有些 case 慢

W7900 具备较高 FP32 峰值、较大显存和较高显存带宽，因此当 case 有足够的稀疏矩阵向量乘工作量并且收敛稳定时，能够发挥硬件优势。但 PDLP 总耗时不只是硬件吞吐问题：

```text
total time ≈ per-iteration cost × number of iterations
```

对于 hard LP instance，稀疏归约、浮点顺序、adaptive restart 时机、step-size 演化、residual/gap 轨迹上的微小差异，都可能改变迭代路径。这可以解释为什么 W7900 在部分 large case 上表现较好，但在 `s100`、`Primal2_1000` 或 hard3 上表现不一定理想。

## 下一步文档任务

1. 更新 `README.md` 和 `README.zh-CN.md`，把 W7900 描述为已经具备 baseline 的验证目标，而不是 planned/first-port-only 状态。
2. 更新 `docs/README.md` 和 validation index，让当前状态页、non-hard23、initial17、watchlist6、near2、hard3 都有清晰入口。
3. 更新 `docs/W7900_FIRST_PORT.md` 和平台记录，补充 bootstrap 与临时机器易丢失的恢复流程。
4. 在正式调优前先补 hard3 note，不把 hard3 混入第一轮主 baseline。
5. 等 W7900 文档状态统一后，再开始 ROCm profiling/tuning。
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
| W7900 current status / W7900 当前状态 | [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md) | [W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md) | Current W7900 baseline, charts, non-hard23 status, and hard3 split |
{BLOCK_END}"""
    insert_or_replace("docs/README.md", docs_block, ["| W7900 large-MPS non-hard23 baseline / W7900 large-MPS non-hard23 baseline", "## Main entry points / 主入口"])


def refresh_readme_status():
    replacements_en = {
        "The W7900 / `gfx1100` branch has passed first-port CPU-vs-ROCm `afiro` smoke validation and is now in extended validation and tuning.": "The W7900 / `gfx1100` branch has completed smoke validation, Netlib 27-case validation, and a 23-case non-hard large-MPS baseline; the remaining large-MPS hard3 cases are tracked separately before full tuning.",
        "| Additional ROCm target under validation | AMD Radeon PRO W7900 / `gfx1100` |": "| Additional validated ROCm target | AMD Radeon PRO W7900 / `gfx1100` |",
        "- W7900 / `gfx1100` first-port build scripts and smoke validation notes.": "- W7900 / `gfx1100` build, smoke validation, Netlib 27-case validation, and large-MPS non-hard23 baseline notes.",
    }
    replacements_zh = {
        "W7900 / `gfx1100` 分支已通过 first-port CPU-vs-ROCm `afiro` smoke validation，正在进入 extended validation 和 tuning 阶段。": "W7900 / `gfx1100` 分支已经完成 smoke validation、Netlib 27-case validation，以及 23-case non-hard large-MPS baseline；剩余 large-MPS hard3 case 会在完整调优前单独跟踪。",
        "| 正在验证的额外 ROCm 目标 | AMD Radeon PRO W7900 / `gfx1100` |": "| 已建立 baseline 的额外 ROCm 目标 | AMD Radeon PRO W7900 / `gfx1100` |",
        "- W7900 / `gfx1100` first-port 构建脚本和 smoke validation 记录。": "- W7900 / `gfx1100` build、smoke validation、Netlib 27-case validation 和 large-MPS non-hard23 baseline 记录。",
    }
    for path, reps in [("README.md", replacements_en), ("README.zh-CN.md", replacements_zh)]:
        p = Path(path)
        if not p.exists():
            continue
        s = p.read_text()
        old = s
        for a, b in reps.items():
            s = s.replace(a, b)
        if s != old:
            p.write_text(s)
            print("[ok] refreshed", path)
        else:
            print("[skip] no README replacements applied in", path)


def main():
    if not NONHARD23_CSV.exists():
        raise SystemExit(f"[error] missing {NONHARD23_CSV}")
    rows, totals = load_data()
    if len(rows) != 23:
        raise SystemExit(f"[error] expected 23 rows, got {len(rows)}")
    if any(r.get("terminationCode") != "OPTIMAL" for r in rows):
        raise SystemExit("[error] non-hard23 CSV contains non-OPTIMAL row")
    generate_charts(rows, totals)
    build_docs(rows, totals)
    update_indexes()
    refresh_readme_status()
    print("[done] W7900 current status docs and charts generated")


if __name__ == "__main__":
    main()
