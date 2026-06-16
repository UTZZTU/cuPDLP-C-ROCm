#!/usr/bin/env python3
import csv, html
from pathlib import Path

VAL = Path("validation")
OUT = Path("docs/assets/w7900/latest_experiments")
OUT.mkdir(parents=True, exist_ok=True)

def read_csv(p):
    with open(p, newline="") as f:
        return list(csv.DictReader(f))

def num(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def esc(x):
    return html.escape(str(x), quote=True)

def bar_svg(path, title, rows, unit="", w=1100, left=300):
    rows = [(str(k), float(v)) for k, v in rows]
    m = max([v for _, v in rows] + [1.0])
    h = 95 + len(rows) * 46 + 45
    plot = w - left - 90
    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{w/2}" y="32" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700">{esc(title)}</text>',
    ]
    y = 75
    for k, v in rows:
        bw = v / m * plot if m else 0
        s += [
            f'<text x="{left-12}" y="{y+20}" text-anchor="end" font-family="Arial" font-size="15">{esc(k)}</text>',
            f'<rect x="{left}" y="{y}" width="{bw:.1f}" height="26" fill="#4e79a7"/>',
            f'<text x="{left+bw+8}" y="{y+20}" font-family="Arial" font-size="15">{v:.3g}{unit}</text>',
        ]
        y += 46
    s.append("</svg>")
    Path(path).write_text("\n".join(s))
    print("wrote", path)

def grouped_svg(path, title, rows, w=1200, left=230):
    rows = [(str(c), float(a), float(b)) for c, a, b in rows]
    m = max([max(a, b) for _, a, b in rows] + [1.0])
    h = 110 + len(rows) * 72 + 40
    plot = w - left - 110
    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{w/2}" y="32" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700">{esc(title)}</text>',
        f'<rect x="{left}" y="55" width="18" height="12" fill="#999"/><text x="{left+25}" y="66" font-family="Arial" font-size="14">pre_tuning</text>',
        f'<rect x="{left+145}" y="55" width="18" height="12" fill="#4e79a7"/><text x="{left+170}" y="66" font-family="Arial" font-size="14">current</text>',
    ]
    y = 90
    for c, pre, cur in rows:
        s += [
            f'<text x="{left-12}" y="{y+25}" text-anchor="end" font-family="Arial" font-size="15">{esc(c)}</text>',
            f'<rect x="{left}" y="{y}" width="{pre/m*plot:.1f}" height="18" fill="#999"/>',
            f'<text x="{left+pre/m*plot+8}" y="{y+15}" font-family="Arial" font-size="13">{pre:.3g}s</text>',
            f'<rect x="{left}" y="{y+28}" width="{cur/m*plot:.1f}" height="18" fill="#4e79a7"/>',
            f'<text x="{left+cur/m*plot+8}" y="{y+43}" font-family="Arial" font-size="13">{cur:.3g}s</text>',
        ]
        y += 72
    s.append("</svg>")
    Path(path).write_text("\n".join(s))
    print("wrote", path)

batch = read_csv(VAL / "w7900_8card_batch_fast8_comparison_20260616.csv")
con = max(num(r["concurrent_wall_seconds"]) for r in batch)
seq = sum(num(r["sequential_wall_seconds"]) for r in batch)
bar_svg(
    OUT / "w7900_8card_fast8_makespan.svg",
    f"W7900 fast8 batch makespan: {seq/con:.2f}x speedup",
    [("single GPU sequential", seq), ("8-card concurrent", con)],
    "s",
)

bc = read_csv(VAL / "w7900_before_current_core6_fast_comparison_20260616.csv")
bc_rows = sorted(
    [(r["case"], num(r["pre_tuning_solve_time"]), num(r["current_solve_time"])) for r in bc],
    key=lambda x: max(x[1], x[2]),
    reverse=True,
)
grouped_svg(
    OUT / "w7900_before_current_fast_core6_solve_time.svg",
    "W7900 before/current fast-core6 solve time",
    bc_rows,
)

hard = read_csv(VAL / "w7900_large_mps_hard3_probe2_600s_solver_20260616.csv")
bar_svg(
    OUT / "w7900_hard3_probe2_relative_gap.svg",
    "W7900 hard3 probe2: relative gap after 600s",
    [(r["case"], num(r["dRelDualityGap"])) for r in hard],
)

kern = read_csv(VAL / "w7900_rocprof_starter3_kernel_top_20260616.csv")
s100 = [r for r in kern if r.get("case") == "s100"][:5]
bar_svg(
    OUT / "w7900_rocprof_s100_top_kernel_percent.svg",
    "W7900 rocprof starter3: s100 top kernel share",
    [(r["name"].replace("void ", "")[:52] + "...", num(r["percentage"])) for r in s100],
    "%",
    w=1300,
    left=560,
)

md = VAL / "w7900_latest_experiment_figures_20260616.md"
zh = VAL / "w7900_latest_experiment_figures_20260616.zh-CN.md"

md.write_text(f"""# W7900 latest experiment figures

![8-card fast8 makespan](../docs/assets/w7900/latest_experiments/w7900_8card_fast8_makespan.svg)

![before/current fast-core6 solve time](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_solve_time.svg)

![hard3 probe2 relative gap](../docs/assets/w7900/latest_experiments/w7900_hard3_probe2_relative_gap.svg)

![s100 top kernel share](../docs/assets/w7900/latest_experiments/w7900_rocprof_s100_top_kernel_percent.svg)

Key numbers:

- 8-card fast8 concurrent makespan: `{con:.0f}s`.
- Single-GPU sequential fast8 makespan: `{seq:.0f}s`.
- Measured batch makespan speedup: `{seq/con:.2f}x`.
""")

zh.write_text(f"""# W7900 最新实验图表

![8-card fast8 makespan](../docs/assets/w7900/latest_experiments/w7900_8card_fast8_makespan.svg)

![before/current fast-core6 solve time](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_solve_time.svg)

![hard3 probe2 relative gap](../docs/assets/w7900/latest_experiments/w7900_hard3_probe2_relative_gap.svg)

![s100 top kernel share](../docs/assets/w7900/latest_experiments/w7900_rocprof_s100_top_kernel_percent.svg)

关键数字：

- 8-card fast8 并发 makespan：`{con:.0f}s`。
- 单 GPU 顺序 fast8 makespan：`{seq:.0f}s`。
- 实测 batch makespan speedup：`{seq/con:.2f}x`。
""")

print("done")
