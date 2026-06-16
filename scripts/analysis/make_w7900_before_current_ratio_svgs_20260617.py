#!/usr/bin/env python3
from pathlib import Path
import csv
import html

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "validation"
ASSETS = ROOT / "docs" / "assets" / "w7900" / "latest_experiments"

IN_CSV = VALIDATION / "w7900_before_current_core6_fast_derived_metrics_20260617.csv"

FIGS = [
    (
        ASSETS / "w7900_before_current_fast_core6_ms_per_iter_ratio.svg",
        "ms_per_iter_ratio",
        "W7900 fast-core6: current / pre_tuning ms per iteration",
        "Ratio, lower is better",
    ),
    (
        ASSETS / "w7900_before_current_fast_core6_iter_ratio.svg",
        "iter_ratio",
        "W7900 fast-core6: current / pre_tuning iteration count",
        "Ratio, lower is better",
    ),
]

def read_rows():
    with IN_CSV.open("r", encoding="utf-8", newline="") as fp:
        return list(csv.DictReader(fp))

def write_bar_svg(path, rows, key, title, ylabel):
    width = 980
    height = 520
    left = 90
    right = 40
    top = 70
    bottom = 130

    plot_w = width - left - right
    plot_h = height - top - bottom

    cases = [r["case"] for r in rows]
    values = [float(r[key]) for r in rows]
    ymax = max(2.1, max(values) * 1.15, 1.15)

    bar_gap = 18
    bar_w = (plot_w - bar_gap * (len(values) + 1)) / len(values)

    def y(v):
        return top + plot_h - (v / ymax) * plot_h

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    lines.append('<rect width="100%" height="100%" fill="white"/>')

    lines.append(f'<text x="{width/2:.1f}" y="32" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" font-weight="700">{html.escape(title)}</text>')
    lines.append(f'<text x="{width/2:.1f}" y="56" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#555">{html.escape(ylabel)}</text>')

    # Axes
    lines.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#222" stroke-width="1"/>')
    lines.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#222" stroke-width="1"/>')

    # Grid and y labels
    ticks = [0.0, 0.5, 1.0, 1.5, 2.0]
    for t in ticks:
        if t <= ymax:
            yy = y(t)
            stroke = "#222" if abs(t - 1.0) < 1e-9 else "#ddd"
            dash = ' stroke-dasharray="6,4"' if abs(t - 1.0) < 1e-9 else ""
            lines.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left + plot_w}" y2="{yy:.1f}" stroke="{stroke}" stroke-width="1"{dash}/>')
            lines.append(f'<text x="{left - 10}" y="{yy + 4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#333">{t:.1f}</text>')

    # Bars
    for idx, (case, val) in enumerate(zip(cases, values)):
        x = left + bar_gap + idx * (bar_w + bar_gap)
        yy = y(val)
        h = top + plot_h - yy
        fill = "#5f6368" if val <= 1.0 else "#9aa0a6"

        lines.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="{fill}"/>')
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{yy - 7:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#222">{val:.3f}</text>')

        label_x = x + bar_w / 2
        label_y = top + plot_h + 20
        safe_case = html.escape(case)
        lines.append(f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="end" transform="rotate(-35 {label_x:.1f} {label_y:.1f})" font-family="Arial, sans-serif" font-size="12" fill="#222">{safe_case}</text>')

    lines.append(f'<text x="{left + plot_w:.1f}" y="{y(1.0) - 8:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#222">baseline = 1.0</text>')

    lines.append(f'<text x="{left + plot_w/2:.1f}" y="{height - 24}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#555">Source: validation/w7900_before_current_core6_fast_derived_metrics_20260617.csv</text>')
    lines.append("</svg>")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main():
    rows = read_rows()
    for path, key, title, ylabel in FIGS:
        write_bar_svg(path, rows, key, title, ylabel)
        print(f"[OK] wrote {path}")

if __name__ == "__main__":
    main()
