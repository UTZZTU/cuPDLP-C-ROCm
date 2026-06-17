#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

VAL_EN = dedent("""
    ## W7900 P14-A1 quick6 current vs pre_tuning repeated validation / 2026-06-18

    This experiment repeats the earlier 890M-style quick6 methodology on W7900
    / `gfx1100`. It compares `pre_tuning` (`ae3b683`) with the current
    `rocm-w7900-gfx1100` branch, with three repeats per case/version pair.

    - Summary: [w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md)
    - Chinese summary: [w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md)
    - Comparison CSV: [w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv)
    - Aggregated CSV: [w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_aggregated.csv](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_aggregated.csv)
    - Raw CSV: [w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_raw.csv](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_raw.csv)

    Result: `current` is faster on `6/6` quick6 cases, with geometric-mean
    speedup `1.18889` and median speedup `1.19502`, while preserving iteration
    counts across the compared versions.
""").strip()

VAL_ZH = dedent("""
    ## W7900 P14-A1 quick6 current vs pre_tuning repeated validation / 2026-06-18

    本实验在 W7900 / `gfx1100` 上复用此前 890M-style quick6 方法论，对比
    `pre_tuning`（`ae3b683`）与当前 `rocm-w7900-gfx1100` 分支，每个
    case/version 组合重复运行 3 次。

    - 汇总：[w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md)
    - 英文汇总：[w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md)
    - 对比 CSV：[w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv)
    - 聚合 CSV：[w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_aggregated.csv](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_aggregated.csv)
    - 原始 CSV：[w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_raw.csv](w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_raw.csv)

    结果：`current` 在 quick6 的 `6/6` 个 case 上均更快，几何平均 speedup 为
    `1.18889`，中位数 speedup 为 `1.19502`，同时保持 pre/current 迭代数一致。
""").strip()

STATUS_EN = dedent("""
    ## P14-A1 quick6 repeated validation update / 2026-06-18

    W7900 now has quick-set repeated timing evidence matching the earlier
    890M-style methodology. P14-A1 compares `pre_tuning` (`ae3b683`) with the
    current branch on six quick Netlib cases, with three repeats per
    case/version pair.

    Result: `current` is faster on `6/6` cases, with geometric-mean speedup
    `1.18889` and median speedup `1.19502`, while preserving iteration counts.

    See [P14-A1 quick6 summary](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md).
""").strip()

STATUS_ZH = dedent("""
    ## P14-A1 quick6 repeated validation 更新 / 2026-06-18

    W7900 现在已有与此前 890M-style 方法论对应的 quick-set repeated timing
    证据。P14-A1 在 6 个 quick Netlib case 上对比 `pre_tuning`（`ae3b683`）与
    当前分支，每个 case/version 组合重复运行 3 次。

    结果：`current` 在 `6/6` 个 case 上更快，几何平均 speedup 为 `1.18889`，
    中位数 speedup 为 `1.19502`，同时保持迭代数一致。

    见 [P14-A1 quick6 中文汇总](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md)。
""").strip()

def append_once(path: Path, section: str):
    text = path.read_text(encoding="utf-8")
    heading = section.splitlines()[0].strip()
    if heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return
    path.write_text(text.rstrip() + "\n\n" + section + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] updated {path.relative_to(ROOT)}")

def main():
    append_once(ROOT / "validation" / "README.md", VAL_EN)
    append_once(ROOT / "validation" / "README.zh-CN.md", VAL_ZH)
    append_once(ROOT / "docs" / "W7900_CURRENT_STATUS.md", STATUS_EN)
    append_once(ROOT / "docs" / "W7900_CURRENT_STATUS.zh-CN.md", STATUS_ZH)

if __name__ == "__main__":
    main()
