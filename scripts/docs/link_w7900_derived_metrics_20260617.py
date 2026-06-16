#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

TARGETS = {
    "validation/README.md": dedent("""
        ## W7900 before/current derived metrics / 2026-06-17

        The fast-core6 derived analysis separates total solve time into iteration
        count and per-iteration execution time.

        - Summary: [w7900_before_current_core6_fast_derived_metrics_20260617.md](w7900_before_current_core6_fast_derived_metrics_20260617.md)
        - CSV: [w7900_before_current_core6_fast_derived_metrics_20260617.csv](w7900_before_current_core6_fast_derived_metrics_20260617.csv)
        - Chinese summary: [w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md](w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md)
        - ms/iter ratio figure: [w7900_before_current_fast_core6_ms_per_iter_ratio.svg](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)
        - iteration ratio figure: [w7900_before_current_fast_core6_iter_ratio.svg](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

        Key interpretation: current improves per-iteration execution time on all
        six fast-core6 cases, but total solve time remains mixed because several
        cases require more iterations.
    """),

    "validation/README.zh-CN.md": dedent("""
        ## W7900 before/current 派生指标 / 2026-06-17

        fast-core6 派生分析把总求解时间拆分为迭代次数和单迭代执行耗时，
        用于避免只看 solve time 得出片面结论。

        - 汇总：[w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md](w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md)
        - CSV：[w7900_before_current_core6_fast_derived_metrics_20260617.csv](w7900_before_current_core6_fast_derived_metrics_20260617.csv)
        - 英文汇总：[w7900_before_current_core6_fast_derived_metrics_20260617.md](w7900_before_current_core6_fast_derived_metrics_20260617.md)
        - 单迭代耗时比图：[w7900_before_current_fast_core6_ms_per_iter_ratio.svg](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)
        - 迭代次数比图：[w7900_before_current_fast_core6_iter_ratio.svg](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

        关键结论：current 在 6 个 fast-core6 case 上均降低了单迭代执行耗时，
        但由于部分 case 迭代次数增加，总 solve time 仍呈 mixed pattern。
    """),

    "docs/W7900_CURRENT_STATUS.md": dedent("""
        ## Derived before/current analysis / 2026-06-17

        The latest fast-core6 derived metrics split total solve time into
        iteration count and per-iteration execution time:

        - [Derived metrics summary](../validation/w7900_before_current_core6_fast_derived_metrics_20260617.md)
        - [Derived metrics CSV](../validation/w7900_before_current_core6_fast_derived_metrics_20260617.csv)
        - [Chinese summary](../validation/w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md)

        ![W7900 fast-core6 ms/iter ratio](assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)

        ![W7900 fast-core6 iteration ratio](assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

        The derived result is important for tuning interpretation: current
        improves per-iteration execution time on all six fast-core6 cases, but
        total solve time remains mixed because several cases require more
        iterations. Future W7900-specific tuning should therefore optimize
        execution efficiency and convergence behavior together.
    """),

    "docs/W7900_CURRENT_STATUS.zh-CN.md": dedent("""
        ## before/current 派生分析 / 2026-06-17

        最新 fast-core6 派生指标把总求解时间拆分为迭代次数和单迭代执行耗时：

        - [派生指标中文汇总](../validation/w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md)
        - [派生指标 CSV](../validation/w7900_before_current_core6_fast_derived_metrics_20260617.csv)
        - [英文汇总](../validation/w7900_before_current_core6_fast_derived_metrics_20260617.md)

        ![W7900 fast-core6 单迭代耗时比](assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)

        ![W7900 fast-core6 迭代次数比](assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

        该派生结果对后续调优解释很重要：current 在 6 个 fast-core6 case 上
        均降低了单迭代执行耗时，但由于部分 case 迭代次数增加，总 solve time
        仍呈 mixed pattern。因此后续 W7900-specific tuning 应同时优化执行效率
        与收敛行为。
    """),

    "validation/w7900_latest_experiment_figures_20260616.md": dedent("""
        ## Derived before/current ratio figures / 2026-06-17

        These two figures extend the fast-core6 before/current analysis by
        separating iteration-count changes from per-iteration execution cost.

        ![W7900 fast-core6 ms/iter ratio](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)

        ![W7900 fast-core6 iteration ratio](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

        Related summary:
        [w7900_before_current_core6_fast_derived_metrics_20260617.md](w7900_before_current_core6_fast_derived_metrics_20260617.md)
    """),

    "validation/w7900_latest_experiment_figures_20260616.zh-CN.md": dedent("""
        ## before/current 派生比值图 / 2026-06-17

        这两张图扩展 fast-core6 before/current 分析，把迭代次数变化和单迭代
        执行耗时变化分开展示。

        ![W7900 fast-core6 单迭代耗时比](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)

        ![W7900 fast-core6 迭代次数比](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

        相关汇总：
        [w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md](w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md)
    """),

    "validation/w7900_before_current_core6_fast_summary_20260616.md": dedent("""
        ## Derived per-iteration analysis / 2026-06-17

        A follow-up derived analysis is available:

        - [Derived metrics summary](w7900_before_current_core6_fast_derived_metrics_20260617.md)
        - [Derived metrics CSV](w7900_before_current_core6_fast_derived_metrics_20260617.csv)
        - [ms/iter ratio figure](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)
        - [iteration ratio figure](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

        The derived metrics show that current lowers ms/iter on all six cases,
        while total solve time remains mixed because several cases need more
        iterations. This supports the next tuning direction: preserve execution
        efficiency gains while investigating convergence behavior.
    """),

    "validation/w7900_before_current_core6_fast_summary_20260616.zh-CN.md": dedent("""
        ## 派生每迭代分析 / 2026-06-17

        后续派生分析已经补充：

        - [派生指标中文汇总](w7900_before_current_core6_fast_derived_metrics_20260617.zh-CN.md)
        - [派生指标 CSV](w7900_before_current_core6_fast_derived_metrics_20260617.csv)
        - [单迭代耗时比图](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_ms_per_iter_ratio.svg)
        - [迭代次数比图](../docs/assets/w7900/latest_experiments/w7900_before_current_fast_core6_iter_ratio.svg)

        派生指标显示，current 在 6 个 case 上均降低了 ms/iter，但由于部分
        case 需要更多迭代，总 solve time 仍呈 mixed pattern。这说明下一阶段
        调优应保留执行效率收益，同时检查收敛行为变化。
    """),
}

def append_once(path: Path, section: str) -> bool:
    text = path.read_text(encoding="utf-8")
    first_heading = section.strip().splitlines()[0].strip()

    if first_heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already contains {first_heading}")
        return False

    new_text = text.rstrip() + "\n\n" + section.strip() + "\n"
    path.write_text(new_text, encoding="utf-8")
    print(f"[OK] updated {path.relative_to(ROOT)}")
    return True

def main():
    changed = 0
    for rel, section in TARGETS.items():
        path = ROOT / rel
        if not path.exists():
            raise FileNotFoundError(path)
        if append_once(path, section):
            changed += 1

    print(f"[DONE] updated {changed} files")

if __name__ == "__main__":
    main()
