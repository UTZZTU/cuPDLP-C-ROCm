#!/usr/bin/env python3
"""Validate and regenerate the final W7900 compact release.

Usage:
    python3 scripts/analysis/generate_final_w7900_release.py
    python3 scripts/analysis/generate_final_w7900_release.py --check-only

Dependencies for figure generation:
    pandas, numpy, matplotlib

The script never reads raw MPS or raw profiler traces. It uses only committed
compact evidence under validation/final_w7900_20260729.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
except ImportError as exc:
    raise SystemExit(
        "Missing pandas/numpy. Install with: "
        "python3 -m pip install pandas numpy matplotlib"
    ) from exc

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "validation" / "final_w7900_20260729"
FIGURES = REPO / "docs" / "assets" / "w7900" / "final20260729"

FORMAL_BRANCH = "rocm-w7900-gfx1100"
SOLVER_BASELINE = "735764807d8698ff30811d1a6fcc45d4a3fd4817"
HARNESS_COMMIT = "b5b9a6ffc1a041a48a0e051568d0134a3822556c"
WINDOW1_SHA = "d2ce13091072a7c40c2c89bdd988e94c2fca36772da38e0af87de6332e7cd94a"
WINDOW2_SHA = "7f8fbcd45591f4dbe0899d18df76329b1f9a17ff433b6dcd3c06d743aaead0db"

EXPECTED_CASES = {
    "L2CTA3D",
    "Primal2_1000",
    "a2864",
    "datt256_lp",
    "ex10",
    "graph40-40",
    "irish-electricity",
    "neos-3025225",
    "neos-5052403-cygnet",
    "neos-5251015",
    "qap15",
    "rmine15",
    "s100",
    "s250r10",
    "savsched1",
    "scpm1",
    "set-cover-model",
    "square41",
    "supportcase10",
    "thk_48",
    "thk_63",
    "tpl-tub-ws1617",
    "woodlands09",
}
PRECISION_CASES = {
    "L2CTA3D",
    "set-cover-model",
    "square41",
    "thk_48",
    "tpl-tub-ws1617",
}
TOLERANCES = {1e-3, 1e-4, 1e-5}
REPEATS = {1, 2}


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_csv(name: str) -> pd.DataFrame:
    path = DATA / name
    assert_true(path.is_file() and path.stat().st_size > 0, f"missing {path}")
    return pd.read_csv(path)


def load_json(name: str) -> dict:
    path = DATA / name
    assert_true(path.is_file() and path.stat().st_size > 0, f"missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> dict:
    identity = load_json("formal_experiment_identity.json")
    assert_true(identity["formal_branch"] == FORMAL_BRANCH, "formal branch mismatch")
    assert_true(
        identity["solver_source_baseline"] == SOLVER_BASELINE,
        "solver baseline mismatch",
    )
    assert_true(
        identity["formal_harness_commit"] == HARNESS_COMMIT,
        "harness commit mismatch",
    )
    assert_true(
        identity["window1"]["archive_sha256"] == WINDOW1_SHA,
        "Window 1 SHA mismatch",
    )
    assert_true(
        identity["window2"]["archive_sha256"] == WINDOW2_SHA,
        "Window 2 SHA mismatch",
    )
    assert_true(
        identity["validated_formal_solver_rows"] == 76,
        "formal validated row count mismatch",
    )

    completion = load_json("formal_experiments_complete.json")
    release = load_json("final_analysis_released.json")
    assert_true(completion.get("status") == "PASS", "completion record not PASS")
    assert_true(release.get("status") == "PASS", "analysis release not PASS")

    baseline = load_csv("baseline_aggregated.csv")
    repeats = load_csv("baseline_repeats.csv")
    throughput = load_csv("throughput_summary.csv")
    precision = load_csv("precision_aggregated.csv")
    precision_raw = load_csv("precision_matrix.csv")
    sensitivity = load_csv("precision_sensitivity.csv")
    precision_resources = load_csv("precision_resource_summary.csv")
    profiles = load_csv("profile_summary.csv")
    static = load_csv("nonhard23_mps_structural_features.csv")

    assert_true(len(baseline) == 23, "baseline aggregate must have 23 rows")
    assert_true(set(baseline["case"]) == EXPECTED_CASES, "baseline case set mismatch")
    assert_true(len(repeats) == 46, "baseline repeats must have 46 rows")
    assert_true(set(repeats["case"]) == EXPECTED_CASES, "repeat case set mismatch")
    assert_true(
        set(pd.to_numeric(repeats["repeat"]).astype(int)) == REPEATS,
        "baseline repeat set mismatch",
    )
    assert_true(
        repeats[["case", "repeat"]].drop_duplicates().shape[0] == 46,
        "duplicate baseline identity",
    )
    if "run_outcome" in repeats.columns:
        assert_true(
            set(repeats["run_outcome"]) == {"VALIDATED_OPTIMAL"},
            "baseline contains non-validated outcome",
        )

    assert_true(len(throughput) == 2, "throughput must have two complete repeats")
    assert_true(
        throughput["throughput_valid"].astype(str).str.lower().eq("true").all(),
        "throughput_valid is not true for all repeats",
    )
    assert_true(
        pd.to_numeric(throughput["expected_cases"]).eq(23).all()
        and pd.to_numeric(throughput["validated_optimal_cases"]).eq(23).all()
        and throughput["matrix_complete"].astype(str).str.lower().eq("true").all(),
        "throughput incomplete",
    )

    assert_true(len(precision) == 15, "precision aggregate must have 15 rows")
    assert_true(set(precision["case"]) == PRECISION_CASES, "precision case mismatch")
    assert_true(
        set(pd.to_numeric(precision["tolerance"])) == TOLERANCES,
        "precision tolerance mismatch",
    )
    assert_true(len(precision_raw) == 30, "precision matrix must have 30 rows")
    assert_true(
        precision_raw[["case", "tolerance", "repeat"]]
        .drop_duplicates()
        .shape[0]
        == 30,
        "duplicate precision identity",
    )
    assert_true(
        set(precision_raw["case"]) == PRECISION_CASES,
        "precision raw case mismatch",
    )
    assert_true(
        set(pd.to_numeric(precision_raw["repeat"]).astype(int)) == REPEATS,
        "precision repeat mismatch",
    )
    assert_true(
        set(pd.to_numeric(precision_raw["tolerance"])) == TOLERANCES,
        "precision raw tolerance mismatch",
    )
    assert_true(
        set(precision_raw["run_outcome"]) == {"VALIDATED_OPTIMAL"},
        "precision contains non-validated outcome",
    )

    precision_raw["max_rel_error"] = precision_raw[
        ["dRelPrimalFeas", "dRelDualFeas", "dRelDualityGap"]
    ].max(axis=1)
    precision_raw["quality_ratio"] = (
        precision_raw["max_rel_error"] / precision_raw["tolerance"]
    )
    assert_true(
        (precision_raw["quality_ratio"] <= 1.0 + 1e-12).all(),
        "achieved error exceeds requested tolerance",
    )

    assert_true(len(sensitivity) == 5, "sensitivity must have five rows")
    assert_true(set(sensitivity["case"]) == PRECISION_CASES, "sensitivity case mismatch")

    assert_true(len(profiles) == 5, "profile summary must have five rows")
    assert_true(set(profiles["case"]) == PRECISION_CASES, "profile case mismatch")
    assert_true(
        profiles["runtime_status"].eq("DONE").all(),
        "profile runtime status not DONE",
    )
    assert_true(
        profiles["profile_validation_status"].eq("PASS").all(),
        "profile validation not PASS",
    )
    assert_true(
        pd.to_numeric(profiles["trace_csv_count"]).gt(0).all(),
        "missing profile trace CSV",
    )
    assert_true(
        pd.to_numeric(profiles["kernel_trace_count"]).gt(0).all(),
        "missing kernel trace",
    )

    assert_true(len(static) == 23, "static features must have 23 rows")
    static_cases = set(static["case"].str.replace(r"\.mps$", "", regex=True))
    assert_true(static_cases == EXPECTED_CASES, "static feature case mismatch")

    baseline["wall_cv_pct"] = baseline["wall_seconds_cv"] * 100
    baseline["runtime_share_pct"] = (
        baseline["wall_seconds_median"]
        / baseline["wall_seconds_median"].sum()
        * 100
    )
    ordered = baseline.sort_values("wall_seconds_median", ascending=False)
    iteration_consistent = int(
        (repeats.groupby("case")["iterations"].nunique() == 1).sum()
    )

    metrics = {
        "mean_throughput": float(throughput["cases_per_hour"].mean()),
        "median_wall_cv_pct": float(baseline["wall_cv_pct"].median()),
        "under_2_pct": int((baseline["wall_cv_pct"] < 2).sum()),
        "iteration_consistent": iteration_consistent,
        "top3_share_pct": float(ordered.head(3)["runtime_share_pct"].sum()),
        "quality_ratio_max": float(precision_raw["quality_ratio"].max()),
        "time_ratio_min": float(
            sensitivity["time_ratio_1e-5_over_1e-3"].min()
        ),
        "time_ratio_max": float(
            sensitivity["time_ratio_1e-5_over_1e-3"].max()
        ),
        "iteration_ratio_min": float(
            sensitivity["iteration_ratio_1e-5_over_1e-3"].min()
        ),
        "iteration_ratio_max": float(
            sensitivity["iteration_ratio_1e-5_over_1e-3"].max()
        ),
    }
    assert_true(abs(metrics["mean_throughput"] - 28.0616106535) < 1e-8,
                "throughput mean mismatch")
    assert_true(abs(metrics["top3_share_pct"] - 82.220638) < 1e-4,
                "top-three share mismatch")
    assert_true(metrics["under_2_pct"] == 22, "repeatability count mismatch")
    assert_true(metrics["iteration_consistent"] == 23,
                "iteration consistency mismatch")
    assert_true(metrics["quality_ratio_max"] <= 1.0, "quality ratio invalid")

    return {
        "identity": identity,
        "baseline": baseline,
        "repeats": repeats,
        "throughput": throughput,
        "precision": precision,
        "precision_raw": precision_raw,
        "sensitivity": sensitivity,
        "precision_resources": precision_resources,
        "profiles": profiles,
        "static": static,
        "metrics": metrics,
    }


def spearman_frame(data: dict) -> pd.DataFrame:
    baseline = data["baseline"].copy()
    static = data["static"].copy()
    static["case_clean"] = static["case"].str.replace(r"\.mps$", "", regex=True)
    baseline["overhead_seconds_median"] = (
        baseline["wall_seconds_median"] - baseline["solver_seconds_median"]
    )
    merged = baseline.merge(
        static,
        left_on="case",
        right_on="case_clean",
        how="left",
        validate="one_to_one",
    )

    features = [
        "file_bytes",
        "constraint_rows",
        "columns",
        "matrix_nnz",
        "matrix_density",
        "row_degree_mean",
        "column_degree_mean",
        "row_degree_gini",
        "column_degree_gini",
        "coefficient_log10_dynamic_range",
        "rhs_dynamic_range",
        "objective_dynamic_range",
    ]
    metrics = [
        "wall_seconds_median",
        "solver_seconds_median",
        "iterations_median",
        "time_per_iteration_seconds_median",
        "overhead_seconds_median",
        "vram_peak_sampled_bytes_median",
        "gpu_util_pct_mean_across_runs",
    ]

    rows = []
    for feature in features:
        for metric in metrics:
            pair = merged[[feature, metric]].replace([np.inf, -np.inf], np.nan).dropna()
            if len(pair) < 8 or pair[feature].nunique() <= 2:
                continue
            rho = pair[feature].rank(method="average").corr(
                pair[metric].rank(method="average")
            )
            rows.append(
                {
                    "feature": feature,
                    "metric": metric,
                    "n": len(pair),
                    "spearman_rho": rho,
                }
            )
    return pd.DataFrame(rows)


def configure_fonts():
    import matplotlib
    from matplotlib import font_manager as fm

    candidates = [
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.otf"),
    ]
    for path in candidates:
        if path.exists():
            prop = fm.FontProperties(fname=str(path))
            matplotlib.rcParams["font.family"] = prop.get_name()
            return prop
    return fm.FontProperties()


def generate_figures(data: dict) -> None:
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib import font_manager as fm
    except ImportError as exc:
        raise SystemExit(
            "Missing matplotlib. Install with: "
            "python3 -m pip install pandas numpy matplotlib"
        ) from exc

    regular = configure_fonts()
    bold = fm.FontProperties(
        fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    ) if Path(
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    ).exists() else fm.FontProperties(weight="bold")

    matplotlib.rcParams["axes.unicode_minus"] = False
    matplotlib.rcParams["font.size"] = 10
    FIGURES.mkdir(parents=True, exist_ok=True)

    baseline = data["baseline"].copy()
    baseline["solver_share_pct"] = (
        baseline["solver_seconds_median"] / baseline["wall_seconds_median"] * 100
    )
    baseline["vram_peak_gib"] = (
        baseline["vram_peak_sampled_bytes_median"] / (2**30)
    )
    baseline["wall_cv_pct"] = baseline["wall_seconds_cv"] * 100
    precision = data["precision"].copy()
    precision["max_rel_error"] = precision[
        [
            "dRelPrimalFeas_median",
            "dRelDualFeas_median",
            "dRelDualityGap_median",
        ]
    ].max(axis=1)
    precision["quality_ratio"] = (
        precision["max_rel_error"] / precision["tolerance"]
    )
    sensitivity = data["sensitivity"].copy()
    resources = data["precision_resources"].copy()
    resources["vram_peak_gib"] = (
        resources["vram_peak_sampled_bytes"] / (2**30)
    )
    vram = resources.groupby(
        ["case", "tolerance"], as_index=False
    )["vram_peak_gib"].median()
    tradeoff = precision.merge(vram, on=["case", "tolerance"], how="left")

    def style(ax, title, xlabel, ylabel, zh):
        ax.set_title(title, fontproperties=bold if zh else None, pad=9)
        ax.set_xlabel(xlabel, fontproperties=regular if zh else None)
        ax.set_ylabel(ylabel, fontproperties=regular if zh else None)
        if zh:
            for label in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
                label.set_fontproperties(regular)
        ax.grid(alpha=0.2)

    def save(fig, stem):
        fig.tight_layout()
        png_path = FIGURES / f"{stem}.png"
        svg_path = FIGURES / f"{stem}.svg"
        fig.savefig(png_path, dpi=320, bbox_inches="tight")
        fig.savefig(svg_path, bbox_inches="tight")
        plt.close(fig)

        # Matplotlib SVG output may contain trailing spaces in path data.
        # Normalize it so git diff --check and release checks remain clean.
        svg_text = svg_path.read_text(encoding="utf-8")
        svg_text = "\n".join(
            line.rstrip(" \t") for line in svg_text.splitlines()
        ) + "\n"
        svg_path.write_text(svg_text, encoding="utf-8", newline="\n")

    for lang in ("zh-CN", "en"):
        zh = lang == "zh-CN"

        plot = baseline.sort_values("wall_seconds_median")
        fig, ax = plt.subplots(figsize=(9.0, 7.3))
        ax.barh(plot["case"], plot["wall_seconds_median"])
        ax.set_xscale("log")
        ax.set_xlim(plot["wall_seconds_median"].min() / 1.5,
                    plot["wall_seconds_median"].max() * 2)
        style(
            ax,
            "W7900 单卡基线运行总时间" if zh
            else "W7900 Single-GPU Baseline Total Time",
            "总时间中位数（秒，对数坐标）" if zh
            else "Median total time (seconds, log scale)",
            "",
            zh,
        )
        ax.grid(axis="x", alpha=0.22)
        for y, value in enumerate(plot["wall_seconds_median"]):
            ax.text(value * 1.055, y, f"{value:.2f}s",
                    va="center", fontsize=8.3)
        save(fig, f"baseline_total_time.{lang}")

        plot = baseline.sort_values("wall_cv_pct")
        fig, ax = plt.subplots(figsize=(8.8, 7.0))
        ax.scatter(plot["wall_cv_pct"], plot["case"], s=38)
        ax.axvline(2.0, linestyle="--", linewidth=1)
        style(
            ax,
            "W7900 基线实验重复性" if zh
            else "W7900 Baseline Repeatability",
            "总时间变异系数 CV（%）" if zh
            else "Total-time coefficient of variation (%)",
            "",
            zh,
        )
        ax.grid(axis="x", alpha=0.22)
        for _, row in plot.tail(3).iterrows():
            ax.annotate(
                f"{row['case']}  {row['wall_cv_pct']:.2f}%",
                (row["wall_cv_pct"], row["case"]),
                xytext=(8, 0),
                textcoords="offset points",
                va="center",
                fontsize=8.3,
            )
        save(fig, f"baseline_repeatability.{lang}")

        fig, ax = plt.subplots(figsize=(8.8, 6.5))
        sizes = 55 + 115 * np.sqrt(baseline["vram_peak_gib"])
        ax.scatter(
            baseline["wall_seconds_median"],
            baseline["solver_share_pct"],
            s=sizes,
            alpha=0.72,
        )
        ax.set_xscale("log")
        style(
            ax,
            "W7900 工作负载画像" if zh else "W7900 Workload Profile",
            "总时间中位数（秒，对数坐标）" if zh
            else "Median total time (seconds, log scale)",
            "求解阶段时间占总时间比例（%）" if zh
            else "Solver-stage share of total time (%)",
            zh,
        )
        offsets = {
            "s100": (8, 8),
            "Primal2_1000": (-95, -9),
            "thk_63": (8, 7),
            "square41": (8, 7),
            "tpl-tub-ws1617": (-96, -12),
            "set-cover-model": (-88, -12),
            "L2CTA3D": (8, -12),
            "a2864": (8, 7),
        }
        for _, row in baseline[baseline["case"].isin(offsets)].iterrows():
            dx, dy = offsets[row["case"]]
            ax.annotate(
                row["case"],
                (row["wall_seconds_median"], row["solver_share_pct"]),
                xytext=(dx, dy),
                textcoords="offset points",
                fontsize=8.2,
            )
        guides = [0.5, 1.5, 2.8]
        handles = [
            ax.scatter([], [], s=55 + 115 * math.sqrt(value), alpha=0.72)
            for value in guides
        ]
        legend = ax.legend(
            handles,
            [f"{value:.1f} GiB" for value in guides],
            title="采样峰值显存" if zh else "Sampled peak VRAM",
            frameon=False,
            loc="lower right",
            fontsize=8,
        )
        if zh:
            legend.get_title().set_fontproperties(regular)
            for text in legend.get_texts():
                text.set_fontproperties(regular)
        save(fig, f"workload_profile.{lang}")

        plot = sensitivity.sort_values(
            "time_ratio_1e-5_over_1e-3"
        ).reset_index(drop=True)
        x = np.arange(len(plot))
        width = 0.24
        fig, ax = plt.subplots(figsize=(9.0, 5.8))
        ax.bar(x - width, plot["time_ratio_1e-5_over_1e-3"],
               width, label="总时间" if zh else "Total time")
        ax.bar(x, plot["solver_time_ratio_1e-5_over_1e-3"],
               width, label="求解时间" if zh else "Solver time")
        ax.bar(x + width, plot["iteration_ratio_1e-5_over_1e-3"],
               width, label="迭代次数" if zh else "Iterations")
        ax.set_xticks(x)
        ax.set_xticklabels(plot["case"], rotation=18, ha="right")
        style(
            ax,
            "收紧目标精度带来的时间与迭代代价" if zh
            else "Cost of Tightening the Target Tolerance",
            "",
            "倍率（1e-5 相对 1e-3）" if zh
            else "Ratio: 1e-5 relative to 1e-3",
            zh,
        )
        ax.grid(axis="y", alpha=0.22)
        legend = ax.legend(frameon=False, fontsize=8.4)
        if zh:
            for text in legend.get_texts():
                text.set_fontproperties(regular)
        save(fig, f"precision_cost.{lang}")

        fig, ax = plt.subplots(figsize=(9.2, 6.3))
        colors = {1e-3: "C0", 1e-4: "C1", 1e-5: "C2"}
        markers = {
            "L2CTA3D": "P",
            "set-cover-model": "o",
            "square41": "^",
            "thk_48": "s",
            "tpl-tub-ws1617": "D",
        }
        for case, marker in markers.items():
            group = tradeoff[tradeoff["case"] == case]
            for _, row in group.iterrows():
                ax.scatter(
                    row["wall_seconds_median"],
                    row["vram_peak_gib"],
                    marker=marker,
                    s=85,
                    c=colors[float(row["tolerance"])],
                    alpha=0.86,
                    edgecolors="none",
                )
        ax.set_xscale("log")
        style(
            ax,
            "目标精度、运行时间与显存占用" if zh
            else "Target Tolerance, Runtime, and VRAM",
            "总时间中位数（秒，对数坐标）" if zh
            else "Median total time (seconds, log scale)",
            "采样峰值显存（GiB）" if zh
            else "Sampled peak VRAM (GiB)",
            zh,
        )
        tolerance_handles = [
            ax.scatter([], [], s=70, c=color, marker="o")
            for color in colors.values()
        ]
        tolerance_labels = (
            ["宽松精度（1e-3）", "默认精度（1e-4）", "较高精度（1e-5）"]
            if zh else
            ["Loose tolerance (1e-3)", "Default tolerance (1e-4)",
             "Tighter tolerance (1e-5)"]
        )
        legend1 = ax.legend(
            tolerance_handles,
            tolerance_labels,
            title="目标精度" if zh else "Target tolerance",
            frameon=False,
            loc="upper left",
            fontsize=8.3,
        )
        ax.add_artist(legend1)
        case_handles = [
            ax.scatter([], [], s=70, marker=marker, c="0.25")
            for marker in markers.values()
        ]
        legend2 = ax.legend(
            case_handles,
            list(markers),
            title="代表实例" if zh else "Representative case",
            frameon=False,
            loc="lower right",
            fontsize=8.0,
        )
        if zh:
            for legend in (legend1, legend2):
                legend.get_title().set_fontproperties(regular)
                for text in legend.get_texts():
                    text.set_fontproperties(regular)
        save(fig, f"precision_resource_tradeoff.{lang}")

        order = [1e-3, 1e-4, 1e-5]
        labels = ["1e-3", "1e-4", "1e-5"]
        fig, ax = plt.subplots(figsize=(8.6, 5.8))
        for case, group in precision.groupby("case"):
            values = (
                group.set_index("tolerance")
                .reindex(order)["quality_ratio"]
                .to_numpy()
            )
            ax.plot(labels, values, marker="o", linewidth=1.7, label=case)
        ax.axhline(
            1.0,
            linestyle="--",
            linewidth=1,
            label="目标精度边界" if zh
            else "Requested-tolerance boundary",
        )
        ax.set_ylim(0, 1.08)
        style(
            ax,
            "实际结果精度与目标精度的一致性" if zh
            else "Achieved Accuracy versus Requested Tolerance",
            "目标精度" if zh else "Requested tolerance",
            "实际误差 / 目标精度" if zh
            else "Achieved error / requested tolerance",
            zh,
        )
        legend = ax.legend(frameon=False, fontsize=8)
        if zh:
            for text in legend.get_texts():
                text.set_fontproperties(regular)
        save(fig, f"precision_quality.{lang}")

        corr = pd.read_csv(DATA / "static_performance_spearman.csv")
        feature_labels_zh = {
            "file_bytes": "MPS 文件大小",
            "constraint_rows": "约束行数",
            "columns": "变量数",
            "matrix_nnz": "非零元数",
            "matrix_density": "矩阵密度",
            "row_degree_mean": "平均行度",
            "column_degree_mean": "平均列度",
            "row_degree_gini": "行度不均衡度",
            "column_degree_gini": "列度不均衡度",
            "coefficient_log10_dynamic_range": "系数跨度（log10）",
            "rhs_dynamic_range": "右端项跨度",
            "objective_dynamic_range": "目标系数跨度",
        }
        chart = corr[
            corr["metric"] == "vram_peak_sampled_bytes_median"
        ].copy()
        chart["label"] = (
            chart["feature"].map(feature_labels_zh)
            if zh else chart["feature"]
        )
        chart = chart.sort_values("spearman_rho")
        fig, ax = plt.subplots(figsize=(8.8, 6.2))
        ax.barh(chart["label"], chart["spearman_rho"])
        ax.axvline(0, linewidth=1)
        ax.set_xlim(-1, 1)
        style(
            ax,
            "静态结构特征与峰值显存的相关性" if zh
            else "Static Structure versus Sampled Peak VRAM",
            "Spearman 相关系数（探索性，n=23）" if zh
            else "Spearman correlation (exploratory, n=23)",
            "",
            zh,
        )
        ax.grid(axis="x", alpha=0.22)
        for y, value in enumerate(chart["spearman_rho"]):
            ax.text(
                value + (0.025 if value >= 0 else -0.025),
                y,
                f"{value:.2f}",
                va="center",
                ha="left" if value >= 0 else "right",
                fontsize=8.2,
            )
        save(fig, f"static_vram_association.{lang}")


def write_generated_summary(data: dict, corr: pd.DataFrame) -> None:
    metrics = data["metrics"]
    output = {
        "schema_version": 1,
        "formal_branch": FORMAL_BRANCH,
        "solver_source_baseline": SOLVER_BASELINE,
        "formal_harness_commit": HARNESS_COMMIT,
        "formal_solver_rows": 76,
        "validated_formal_solver_rows": 76,
        **metrics,
    }
    (DATA / "generated_summary.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    corr.to_csv(
        DATA / "static_performance_spearman_regenerated.csv",
        index=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="validate compact evidence without rewriting figures",
    )
    args = parser.parse_args()

    data = validate()
    print("baseline_rows=46/46")
    print("precision_rows=30/30")
    print("profile_rows=5/5")
    print("static_cases=23/23")
    print(f"mean_throughput={data['metrics']['mean_throughput']:.9f}")
    print(f"top3_share={data['metrics']['top3_share_pct']:.6f}")
    print(f"quality_ratio_max={data['metrics']['quality_ratio_max']:.9f}")
    print("FINAL_W7900_RELEASE_DATA_PASS")

    if args.check_only:
        return

    corr = spearman_frame(data)
    write_generated_summary(data, corr)
    generate_figures(data)
    print(f"figures={FIGURES}")
    print("FINAL_W7900_RELEASE_FIGURES_PASS")


if __name__ == "__main__":
    main()
