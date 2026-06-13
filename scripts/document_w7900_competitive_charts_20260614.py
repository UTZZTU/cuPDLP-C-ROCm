#!/usr/bin/env python3
import csv
import html
from pathlib import Path

NONHARD23_CSV = Path("validation/w7900_large_mps_nonhard23_20260613.csv")
HIST_CSV = Path("results/benchmarks/large_mps_per_case_timing_summary_20260610.csv")
ASSET_DIR = Path("docs/assets/w7900")

BLOCK_BEGIN = "<!-- W7900_COMPETITIVE_CHARTS_20260614_BEGIN -->"
BLOCK_END = "<!-- W7900_COMPETITIVE_CHARTS_20260614_END -->"

RATIO_SVG = ASSET_DIR / "w7900_nonhard23_wall_ratio_vs_h100.svg"
BANDS_SVG = ASSET_DIR / "w7900_nonhard23_competitiveness_bands.svg"
REP_WALL_SVG = ASSET_DIR / "w7900_nonhard23_representative_wall_compare.svg"
REP_SOLVE_SVG = ASSET_DIR / "w7900_nonhard23_representative_solve_compare.svg"

PERF_EN = Path("docs/W7900_PERFORMANCE_BEHAVIOR.md")
PERF_ZH = Path("docs/W7900_PERFORMANCE_BEHAVIOR.zh-CN.md")
STATUS_EN = Path("docs/W7900_CURRENT_STATUS.md")
STATUS_ZH = Path("docs/W7900_CURRENT_STATUS.zh-CN.md")


def read_csv(path):
    if not path.exists():
        raise SystemExit(f"[error] missing required file: {path}")
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def fnum(x, default=0.0):
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default


def stem_case(name):
    s = str(name).strip()
    return s[:-4] if s.endswith(".mps") else s


def fmt(x, ndigits=2):
    return f"{x:.{ndigits}f}"


def esc(s):
    return html.escape(str(s), quote=True)


def markdown_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |"]
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(out)


def load_data():
    w_rows = read_csv(NONHARD23_CSV)
    h_rows = read_csv(HIST_CSV)
    hist = {stem_case(r["case"]): r for r in h_rows}

    rows = []
    for r in w_rows:
        case = stem_case(r["case"])
        if case not in hist:
            continue
        h = hist[case]
        w_wall = fnum(r["wall_seconds"])
        w_solve = fnum(r["dSolvingTime"])
        rows.append({
            "case": case,
            "source_group": r.get("source_group", ""),
            "w_wall": w_wall,
            "w_solve": w_solve,
            "h100_wall": fnum(h.get("h100_wall")),
            "h100_solve": fnum(h.get("h100_solve")),
            "rtx3090_wall": fnum(h.get("rtx3090_wall")),
            "rtx3090_solve": fnum(h.get("rtx3090_solve")),
            "rtx4090d_wall": fnum(h.get("rtx4090d_wall")),
            "rtx4090d_solve": fnum(h.get("rtx4090d_solve")),
            "radeon890m_wall": fnum(h.get("radeon890m_wall")),
            "radeon890m_solve": fnum(h.get("radeon890m_solve")),
            "nIter": r.get("nIter", ""),
            "gap": r.get("dRelDualityGap", ""),
        })
    if len(rows) != 23:
        raise SystemExit(f"[error] expected 23 matching rows, got {len(rows)}")
    return rows


def write_svg(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n")
    print("[ok] wrote", path)


def bar_chart_ratio_vs_h100(rows):
    data = []
    for r in rows:
        if r["w_wall"] > 0 and r["h100_wall"] > 0:
            ratio = r["h100_wall"] / r["w_wall"]
            data.append((r["case"], ratio, r["w_wall"], r["h100_wall"]))
    data.sort(key=lambda x: x[1], reverse=True)

    width = 1040
    row_h = 32
    margin_left = 250
    margin_right = 160
    margin_top = 72
    margin_bottom = 52
    height = margin_top + margin_bottom + len(data) * row_h
    bar_max = width - margin_left - margin_right
    max_ratio = max([x[1] for x in data] + [1.0])

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-size="21" font-family="Arial, sans-serif" font-weight="700">W7900 per-case wall-time competitiveness vs H100</text>',
        f'<text x="{width/2}" y="52" text-anchor="middle" font-size="13" font-family="Arial, sans-serif" fill="#555">H100 wall / W7900 wall. Values above 1.0 mean W7900 is faster on that case.</text>',
    ]

    # vertical 1x reference
    one_x = margin_left + (1.0 / max_ratio) * bar_max
    parts.append(f'<line x1="{one_x:.2f}" y1="{margin_top-8}" x2="{one_x:.2f}" y2="{height-margin_bottom+4}" stroke="#111" stroke-width="1" stroke-dasharray="4,4"/>')
    parts.append(f'<text x="{one_x+4:.2f}" y="{margin_top-14}" font-size="12" font-family="Arial, sans-serif">1.0x parity</text>')

    for i, (case, ratio, w_wall, h_wall) in enumerate(data):
        y = margin_top + i * row_h
        bar_w = ratio / max_ratio * bar_max
        fill = "#4b5563" if ratio >= 1 else "#9ca3af"
        parts.append(f'<text x="{margin_left-12}" y="{y+21}" text-anchor="end" font-size="12" font-family="Arial, sans-serif">{esc(case)}</text>')
        parts.append(f'<rect x="{margin_left}" y="{y+7}" width="{bar_w:.2f}" height="18" rx="3" fill="{fill}"/>')
        parts.append(f'<text x="{margin_left + bar_w + 8:.2f}" y="{y+21}" font-size="12" font-family="Arial, sans-serif">{ratio:.2f}x</text>')

    parts.append(f'<text x="{margin_left}" y="{height-18}" font-size="12" font-family="Arial, sans-serif" fill="#555">This chart highlights case-level wins/near-parity that are hidden by aggregate totals.</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def competitiveness_bands(rows):
    refs = [
        ("H100", "h100_wall"),
        ("RTX 4090D", "rtx4090d_wall"),
        ("RTX 3090", "rtx3090_wall"),
        ("Radeon 890M", "radeon890m_wall"),
    ]
    data = []
    for label, key in refs:
        faster = near = slower = 0
        for r in rows:
            ref = r[key]
            w = r["w_wall"]
            if w <= 0 or ref <= 0:
                continue
            if w <= ref:
                faster += 1
            elif w <= 1.5 * ref:
                near += 1
            else:
                slower += 1
        data.append((label, faster, near, slower))

    width = 900
    height = 330
    margin_left = 160
    margin_top = 72
    bar_w_max = 560
    row_h = 52

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="30" text-anchor="middle" font-size="21" font-family="Arial, sans-serif" font-weight="700">W7900 wall-time competitiveness bands</text>',
        f'<text x="{width/2}" y="53" text-anchor="middle" font-size="13" font-family="Arial, sans-serif" fill="#555">Faster: W7900 wall ≤ reference. Near: W7900 wall ≤ 1.5× reference. Slower: above 1.5× reference.</text>',
    ]

    legend_x = margin_left
    legend_y = height - 28
    legend = [("Faster", "#374151"), ("Near", "#9ca3af"), ("Slower", "#d1d5db")]
    for j, (name, color) in enumerate(legend):
        x = legend_x + j * 120
        parts.append(f'<rect x="{x}" y="{legend_y-13}" width="18" height="12" fill="{color}"/>')
        parts.append(f'<text x="{x+24}" y="{legend_y-3}" font-size="12" font-family="Arial, sans-serif">{name}</text>')

    for i, (label, faster, near, slower) in enumerate(data):
        y = margin_top + i * row_h
        total = max(faster + near + slower, 1)
        x = margin_left
        fw = faster / total * bar_w_max
        nw = near / total * bar_w_max
        sw = slower / total * bar_w_max
        parts.append(f'<text x="{margin_left-14}" y="{y+26}" text-anchor="end" font-size="14" font-family="Arial, sans-serif">{esc(label)}</text>')
        parts.append(f'<rect x="{x}" y="{y+8}" width="{fw:.2f}" height="24" fill="#374151"/>')
        x += fw
        parts.append(f'<rect x="{x:.2f}" y="{y+8}" width="{nw:.2f}" height="24" fill="#9ca3af"/>')
        x += nw
        parts.append(f'<rect x="{x:.2f}" y="{y+8}" width="{sw:.2f}" height="24" fill="#d1d5db"/>')
        parts.append(f'<text x="{margin_left + bar_w_max + 12}" y="{y+26}" font-size="13" font-family="Arial, sans-serif">{faster} faster, {near} near, {slower} slower</text>')

    parts.append("</svg>")
    return "\n".join(parts), data


def representative_case_list(rows):
    preferred = [
        "square41",
        "set-cover-model",
        "supportcase10",
        "L2CTA3D",
        "a2864",
        "thk_48",
        "tpl-tub-ws1617",
        "s100",
        "Primal2_1000",
    ]
    by_case = {r["case"]: r for r in rows}
    return [by_case[c] for c in preferred if c in by_case]


def representative_grouped_bars(rows, metric):
    reps = representative_case_list(rows)
    devices = [
        ("W7900", "w_" + metric),
        ("H100", "h100_" + metric),
        ("RTX 4090D", "rtx4090d_" + metric),
        ("RTX 3090", "rtx3090_" + metric),
        ("890M", "radeon890m_" + metric),
    ]
    width = 1120
    group_h = 86
    margin_left = 190
    margin_right = 140
    margin_top = 72
    margin_bottom = 44
    height = margin_top + margin_bottom + len(reps) * group_h
    bar_max = width - margin_left - margin_right

    # Use log-style normalized length so slow cases do not hide fast cases.
    values = []
    for r in reps:
        for _, key in devices:
            values.append(max(r[key], 0.001))
    import math
    max_log = max(math.log10(v + 1.0) for v in values)

    title_metric = "wall time" if metric == "wall" else "solve time"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="30" text-anchor="middle" font-size="21" font-family="Arial, sans-serif" font-weight="700">Representative large-MPS {title_metric} comparison</text>',
        f'<text x="{width/2}" y="53" text-anchor="middle" font-size="13" font-family="Arial, sans-serif" fill="#555">Bars use log-style length for readability; numeric labels show seconds. Lower is better.</text>',
    ]

    shade = ["#374151", "#6b7280", "#9ca3af", "#b6bbc3", "#d1d5db"]
    for i, r in enumerate(reps):
        y0 = margin_top + i * group_h
        parts.append(f'<text x="{margin_left-14}" y="{y0+45}" text-anchor="end" font-size="13" font-family="Arial, sans-serif" font-weight="700">{esc(r["case"])}</text>')
        for j, (device, key) in enumerate(devices):
            y = y0 + 7 + j * 15
            val = max(r[key], 0.001)
            bw = math.log10(val + 1.0) / max_log * bar_max
            parts.append(f'<text x="{margin_left}" y="{y+11}" text-anchor="start" font-size="10" font-family="Arial, sans-serif" fill="#333">{esc(device)}</text>')
            x0 = margin_left + 72
            parts.append(f'<rect x="{x0}" y="{y}" width="{bw:.2f}" height="10" rx="2" fill="{shade[j]}"/>')
            parts.append(f'<text x="{x0 + bw + 6:.2f}" y="{y+10}" font-size="10" font-family="Arial, sans-serif">{val:.2f}s</text>')

    parts.append("</svg>")
    return "\n".join(parts)


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
    for anchor in anchors:
        if anchor in s:
            p.write_text(s.replace(anchor, block.rstrip() + "\n\n" + anchor, 1))
            print("[ok] inserted block in", path)
            return
    p.write_text(s.rstrip() + "\n\n" + block.rstrip() + "\n")
    print("[ok] appended block in", path)


def build_tables(rows, bands_data):
    ratio_rows = []
    for r in rows:
        if r["w_wall"] > 0 and r["h100_wall"] > 0:
            ratio_rows.append([r["case"], fmt(r["w_wall"]), fmt(r["h100_wall"]), f"{r['h100_wall']/r['w_wall']:.2f}x"])
    ratio_rows.sort(key=lambda x: float(x[3].replace("x", "")), reverse=True)

    band_rows = []
    for label, faster, near, slower in bands_data:
        band_rows.append([label, faster, near, slower])

    top_ratio_rows = ratio_rows[:12]
    return top_ratio_rows, band_rows


def update_docs(rows, bands_data):
    top_ratio_rows, band_rows = build_tables(rows, bands_data)

    perf_block_en = f"""{BLOCK_BEGIN}
## W7900 competitiveness against H100 and CUDA references

The earlier aggregate solve-time chart is useful for bottleneck analysis, but it can hide the fact that W7900 is already competitive on many individual large-MPS cases. The charts below therefore use per-case wall time to show where W7900 matches or exceeds high-end references.

### W7900 vs H100 per-case wall-time ratio

Values above 1.0 mean W7900 is faster than H100 on that case.

{markdown_table(["Case", "W7900 wall", "H100 wall", "H100/W7900"], top_ratio_rows)}

![W7900 wall ratio vs H100](assets/w7900/w7900_nonhard23_wall_ratio_vs_h100.svg)

### Competitiveness bands

{markdown_table(["Reference", "W7900 faster", "Near within 1.5x", "Slower above 1.5x"], band_rows)}

![W7900 competitiveness bands](assets/w7900/w7900_nonhard23_competitiveness_bands.svg)

### Representative case comparison

This chart deliberately mixes cases where W7900 is strong and cases where it is slow-but-solvable. This is a better competition narrative than only showing aggregate totals, because it separates hardware competitiveness from convergence-sensitive cases.

![Representative wall comparison](assets/w7900/w7900_nonhard23_representative_wall_compare.svg)

![Representative solve comparison](assets/w7900/w7900_nonhard23_representative_solve_compare.svg)
{BLOCK_END}"""

    perf_block_zh = f"""{BLOCK_BEGIN}
## W7900 与 H100 / CUDA 参考的竞争力

之前的 aggregate solve-time 图适合分析瓶颈，但容易掩盖 W7900 在许多单个 large-MPS case 上已经具备竞争力这一点。因此下面改用 per-case wall time 展示 W7900 在哪些 case 上接近或超过高端参考设备。

### W7900 vs H100 per-case wall-time ratio

数值大于 1.0 表示 W7900 在该 case 上比 H100 更快。

{markdown_table(["Case", "W7900 wall", "H100 wall", "H100/W7900"], top_ratio_rows)}

![W7900 wall ratio vs H100](assets/w7900/w7900_nonhard23_wall_ratio_vs_h100.svg)

### 竞争力分段

{markdown_table(["参考设备", "W7900 更快", "1.5x 内接近", "超过 1.5x 较慢"], band_rows)}

![W7900 competitiveness bands](assets/w7900/w7900_nonhard23_competitiveness_bands.svg)

### 代表 case 对比

这张图刻意同时包含 W7900 表现强的 case 和 slow-but-solvable case。相比只看 aggregate totals，这种叙事更适合比赛展示，因为它把硬件竞争力和收敛敏感 case 区分开。

![Representative wall comparison](assets/w7900/w7900_nonhard23_representative_wall_compare.svg)

![Representative solve comparison](assets/w7900/w7900_nonhard23_representative_solve_compare.svg)
{BLOCK_END}"""

    status_block_en = f"""{BLOCK_BEGIN}
## Per-case competitiveness highlight

The non-hard23 aggregate totals are useful, but the strongest W7900 story is per-case: W7900 can match or exceed H100 wall time on selected large-MPS cases, while the slow cases are better interpreted through convergence behavior.

![W7900 wall ratio vs H100](assets/w7900/w7900_nonhard23_wall_ratio_vs_h100.svg)

See [W7900 performance behavior analysis](W7900_PERFORMANCE_BEHAVIOR.md) for the full competitiveness and case-class discussion.
{BLOCK_END}"""

    status_block_zh = f"""{BLOCK_BEGIN}
## Per-case 竞争力亮点

non-hard23 aggregate totals 有分析价值，但 W7900 最有说服力的故事是 per-case：W7900 在部分 large-MPS case 上可以接近甚至超过 H100 的 wall time，而慢 case 更适合从收敛行为解释。

![W7900 wall ratio vs H100](assets/w7900/w7900_nonhard23_wall_ratio_vs_h100.svg)

完整竞争力和 case 分类讨论见 [W7900 性能行为分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md)。
{BLOCK_END}"""

    insert_or_replace(PERF_EN, perf_block_en, ["## W7900 vs 890M speedup", "## Tuning implication"])
    insert_or_replace(PERF_ZH, perf_block_zh, ["## W7900 相对 890M 的加速", "## 对调优的启示"])
    insert_or_replace(STATUS_EN, status_block_en, ["## Cross-device reference on matching 23 cases", "## W7900 slowest non-hard cases"])
    insert_or_replace(STATUS_ZH, status_block_zh, ["## 同 23 个 case 的跨设备参考", "## W7900 最慢 non-hard cases"])


def main():
    rows = load_data()
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    write_svg(RATIO_SVG, bar_chart_ratio_vs_h100(rows))
    bands_svg, bands_data = competitiveness_bands(rows)
    write_svg(BANDS_SVG, bands_svg)
    write_svg(REP_WALL_SVG, representative_grouped_bars(rows, "wall"))
    write_svg(REP_SOLVE_SVG, representative_grouped_bars(rows, "solve"))
    update_docs(rows, bands_data)
    print("[done] W7900 competitive charts generated")


if __name__ == "__main__":
    main()
