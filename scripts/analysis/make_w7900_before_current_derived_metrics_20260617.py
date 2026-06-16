#!/usr/bin/env python3
from pathlib import Path
import csv
import io
import math
import re

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "validation"
ASSETS = ROOT / "docs" / "assets" / "w7900" / "latest_experiments"

CURRENT_CSV = VALIDATION / "w7900_before_current_core6_fast_current_solver_20260616.csv"
PRE_CSV = VALIDATION / "w7900_before_current_core6_fast_pre_tuning_solver_20260616.csv"

OUT_CSV = VALIDATION / "w7900_before_current_core6_fast_derived_metrics_20260617.csv"
OUT_MD = VALIDATION / "w7900_before_current_core6_fast_derived_metrics_20260617.md"
OUT_ZH = VALIDATION / "w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md"

FIG_MS = ASSETS / "w7900_before_current_fast_core6_ms_per_iter_ratio.svg"
FIG_ITER = ASSETS / "w7900_before_current_fast_core6_iter_ratio.svg"

CASE_ORDER = [
    "L2CTA3D",
    "rmine15",
    "set-cover-model",
    "square41",
    "thk_48",
    "tpl-tub-ws1617",
]

def normalize_csv_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip() + "\n"
    if text.count("\n") < len(CASE_ORDER):
        for case in CASE_ORDER:
            text = re.sub(rf"\s+({re.escape(case)},)", r"\n\1", text)
    return text

def read_rows(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    text = normalize_csv_text(path.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        raise RuntimeError(f"No rows parsed from {path}")
    return {row["case"]: row for row in rows}

def f(row: dict, key: str) -> float:
    return float(row[key])

def i(row: dict, key: str) -> int:
    return int(float(row[key]))

def ratio(a: float, b: float) -> float:
    return float("nan") if b == 0 else a / b

def geomean(values):
    vals = [v for v in values if v > 0 and math.isfinite(v)]
    return math.prod(vals) ** (1.0 / len(vals)) if vals else float("nan")

def fmt(x, digits=6):
    if isinstance(x, str):
        return x
    if isinstance(x, int):
        return str(x)
    if x == 0:
        return "0"
    if abs(x) < 1e-4:
        return f"{x:.6e}"
    return f"{x:.{digits}g}"

def interpretation(r):
    ms = r["ms_per_iter_ratio"]
    solve = r["solve_ratio"]
    it = r["iter_ratio"]
    gap_worse = (
        r["current_gap"] > max(1e-12, 2.0 * r["pre_tuning_gap"])
        or r["current_rel_primal"] > max(1e-12, 2.0 * r["pre_tuning_rel_primal"])
        or r["current_rel_dual"] > max(1e-12, 2.0 * r["pre_tuning_rel_dual"])
    )

    if ms < 1.0 and solve > 1.0:
        base = "current lower ms/iter, but higher iteration count makes total solve time worse"
    elif ms < 1.0 and solve < 1.0:
        base = "current improves both ms/iter and total solve time"
    elif ms > 1.0 and solve < 1.0:
        base = "current solves faster mainly through fewer iterations despite higher ms/iter"
    elif ms > 1.0 and abs(it - 1.0) < 0.05:
        base = "current slower mainly from higher ms/iter with similar iteration count"
    else:
        base = "mixed pattern; inspect execution and convergence together"

    if gap_worse:
        base += "; feasibility/gap worsened materially, treat as numerically sensitive"
    return base

def make_rows():
    cur = read_rows(CURRENT_CSV)
    pre = read_rows(PRE_CSV)
    rows = []

    for case in CASE_ORDER:
        c = cur[case]
        p = pre[case]

        current_iter = i(c, "nIter")
        pre_iter = i(p, "nIter")
        current_solve = f(c, "dSolvingTime")
        pre_solve = f(p, "dSolvingTime")

        current_ms_iter = current_solve * 1000.0 / current_iter
        pre_ms_iter = pre_solve * 1000.0 / pre_iter

        row = {
            "case": case,
            "pre_tuning_nIter": pre_iter,
            "current_nIter": current_iter,
            "iter_ratio": ratio(current_iter, pre_iter),
            "pre_tuning_solve_time": pre_solve,
            "current_solve_time": current_solve,
            "solve_ratio": ratio(current_solve, pre_solve),
            "pre_tuning_ms_per_iter": pre_ms_iter,
            "current_ms_per_iter": current_ms_iter,
            "ms_per_iter_ratio": ratio(current_ms_iter, pre_ms_iter),
            "pre_tuning_gap": f(p, "dRelDualityGap"),
            "current_gap": f(c, "dRelDualityGap"),
            "pre_tuning_rel_primal": f(p, "dRelPrimalFeas"),
            "current_rel_primal": f(c, "dRelPrimalFeas"),
            "pre_tuning_rel_dual": f(p, "dRelDualFeas"),
            "current_rel_dual": f(c, "dRelDualFeas"),
        }
        row["interpretation"] = interpretation(row)
        rows.append(row)

    return rows

def write_csv(rows):
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with OUT_CSV.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def table_md(rows, zh=False):
    headers = [
        "case",
        "iter ratio" if not zh else "迭代数比",
        "solve ratio" if not zh else "求解时间比",
        "ms/iter ratio" if not zh else "单迭代耗时比",
        "current ms/iter",
        "pre ms/iter",
        "interpretation" if not zh else "解释",
    ]

    out = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]

    for r in rows:
        interp = r["interpretation"]
        if zh:
            interp = (
                interp
                .replace(
                    "current lower ms/iter, but higher iteration count makes total solve time worse",
                    "current 单迭代更快，但迭代数增加使总求解时间变差",
                )
                .replace(
                    "current improves both ms/iter and total solve time",
                    "current 同时改善单迭代耗时和总求解时间",
                )
                .replace(
                    "current solves faster mainly through fewer iterations despite higher ms/iter",
                    "current 主要靠更少迭代取得更短总时间，尽管单迭代更慢",
                )
                .replace(
                    "current slower mainly from higher ms/iter with similar iteration count",
                    "迭代数接近，current 主要因单迭代更慢而变慢",
                )
                .replace(
                    "mixed pattern; inspect execution and convergence together",
                    "混合模式，需要同时检查执行效率和收敛行为",
                )
                .replace(
                    "; feasibility/gap worsened materially, treat as numerically sensitive",
                    "；gap/可行性明显变差，应作为数值敏感样本谨慎处理",
                )
            )

        out.append(
            "| {case} | {iter_ratio} | {solve_ratio} | {ms_ratio} | {cur_ms} | {pre_ms} | {interp} |".format(
                case=r["case"],
                iter_ratio=fmt(r["iter_ratio"]),
                solve_ratio=fmt(r["solve_ratio"]),
                ms_ratio=fmt(r["ms_per_iter_ratio"]),
                cur_ms=fmt(r["current_ms_per_iter"]),
                pre_ms=fmt(r["pre_tuning_ms_per_iter"]),
                interp=interp,
            )
        )

    return "\n".join(out)

def write_md(rows):
    gm_iter = geomean([r["iter_ratio"] for r in rows])
    gm_solve = geomean([r["solve_ratio"] for r in rows])
    gm_ms = geomean([r["ms_per_iter_ratio"] for r in rows])

    faster_solve = sum(1 for r in rows if r["solve_ratio"] < 1.0)
    faster_ms = sum(1 for r in rows if r["ms_per_iter_ratio"] < 1.0)
    higher_iter = sum(1 for r in rows if r["iter_ratio"] > 1.0)

    md = f"""# W7900 before/current fast-core6 derived metrics

Source files:

- `validation/w7900_before_current_core6_fast_current_solver_20260616.csv`
- `validation/w7900_before_current_core6_fast_pre_tuning_solver_20260616.csv`

This derived table separates total solve time into iteration count and per-iteration execution time.

## Summary

- Correctness status remains unchanged: all six cases are `OPTIMAL` in both runs.
- `current` has lower ms/iter on {faster_ms}/6 cases.
- `current` has lower total solve time on {faster_solve}/6 cases.
- `current` has higher iteration count on {higher_iter}/6 cases.
- Geomean current/pre solve-time ratio: `{fmt(gm_solve)}`.
- Geomean current/pre iteration ratio: `{fmt(gm_iter)}`.
- Geomean current/pre ms-per-iteration ratio: `{fmt(gm_ms)}`.

## Derived table

{table_md(rows, zh=False)}

## Interpretation

The current W7900/gfx1100 branch keeps fast-core6 correctness stable, but performance remains mixed. The derived metrics show that per-iteration execution time improved on all six cases, while iteration count increased on four cases. Therefore, the next tuning stage should not be framed as pure kernel optimization only. It should preserve the execution-layer gains while investigating why convergence iteration count increased on cases such as `L2CTA3D`, `set-cover-model`, and `tpl-tub-ws1617`.

## Figures

- `../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg`
- `../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg`
"""
    OUT_MD.write_text(md, encoding="utf-8")

    zh = f"""# W7900 before/current fast-core6 派生指标

来源文件：

- `validation/w7900_before_current_core6_fast_current_solver_20260616.csv`
- `validation/w7900_before_current_core6_fast_pre_tuning_solver_20260616.csv`

本表把总求解时间拆成“迭代次数”和“每迭代执行耗时”，用于避免只看 solve time 得出片面结论。

## 总结

- 正确性状态保持不变：6 个 case 在两组运行中均为 `OPTIMAL`。
- `current` 在 {faster_ms}/6 个 case 上降低了 ms/iter。
- `current` 在 {faster_solve}/6 个 case 上降低了总 solve time。
- `current` 在 {higher_iter}/6 个 case 上迭代数增加。
- current/pre solve-time 几何平均比值：`{fmt(gm_solve)}`。
- current/pre iteration 几何平均比值：`{fmt(gm_iter)}`。
- current/pre ms-per-iteration 几何平均比值：`{fmt(gm_ms)}`。

## 派生表

{table_md(rows, zh=True)}

## 解释

当前 W7900/gfx1100 分支在 fast-core6 上保持正确性稳定，但性能仍是 mixed pattern。派生指标显示，6 个 case 的单迭代执行耗时全部下降，但 4 个 case 的迭代次数增加。因此下一阶段不应只按“kernel 越快越好”的单线叙事推进，而应保留执行层收益，同时追查 `L2CTA3D`、`set-cover-model`、`tpl-tub-ws1617` 等 case 的收敛迭代数为什么增加。

## 图表

- `../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg`
- `../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg`
"""
    OUT_ZH.write_text(zh, encoding="utf-8")

def write_figures(rows):
    ASSETS.mkdir(parents=True, exist_ok=True)

    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"[WARN] matplotlib unavailable; skip SVG figures: {exc}")
        return

    cases = [r["case"] for r in rows]

    for path, key, ylabel, title in [
        (
            FIG_MS,
            "ms_per_iter_ratio",
            "current / pre_tuning ms per iteration",
            "W7900 fast-core6 ms/iter ratio",
        ),
        (
            FIG_ITER,
            "iter_ratio",
            "current / pre_tuning iterations",
            "W7900 fast-core6 iteration ratio",
        ),
    ]:
        values = [r[key] for r in rows]
        fig = plt.figure(figsize=(9, 4.8))
        ax = fig.add_subplot(111)
        ax.bar(cases, values)
        ax.axhline(1.0, linestyle="--", linewidth=1)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.tick_params(axis="x", labelrotation=30)
        fig.tight_layout()
        fig.savefig(path, format="svg")
        plt.close(fig)

def main():
    rows = make_rows()
    write_csv(rows)
    write_md(rows)
    write_figures(rows)

    print(f"[OK] wrote {OUT_CSV}")
    print(f"[OK] wrote {OUT_MD}")
    print(f"[OK] wrote {OUT_ZH}")

    if FIG_MS.exists():
        print(f"[OK] wrote {FIG_MS}")
    if FIG_ITER.exists():
        print(f"[OK] wrote {FIG_ITER}")

if __name__ == "__main__":
    main()
