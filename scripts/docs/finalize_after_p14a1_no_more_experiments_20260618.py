#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

P14_EN = dedent("""
    ## Final W7900 validation endpoint after P14-A1 / 2026-06-18

    The current project endpoint no longer requires additional experiments.

    Final W7900 evidence chain:

    - W7900 build, smoke validation, Netlib validation, and large-MPS baseline are documented.
    - P10 targeted rocprof profiling is documented.
    - P11 SpMV tuning is documented; current default is `HIPSPARSE_SPMV_CSR_ALG1`.
    - P12 records a rejected SpMV buffer-algorithm consistency experiment.
    - P14-A1 adds repeated quick6 current-vs-pre_tuning validation.

    P14-A1 result:

    - `current` is faster than `pre_tuning` on `6/6` quick6 cases.
    - geometric-mean speedup: `1.18889`.
    - median speedup: `1.19502`.
    - iteration counts are preserved across compared versions.

    P14-B CSR ALG1-vs-ALG2 repeated validation is no longer a blocker. It can remain a future optional robustness check, but it is not required for the current project closure.

    See [P14-A1 quick6 summary](validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md).
""").strip()

P14_ZH = dedent("""
    ## P14-A1 后的 W7900 最终验证终点 / 2026-06-18

    当前项目终点不再需要继续补实验。

    W7900 最终证据链：

    - W7900 build、smoke validation、Netlib validation 和 large-MPS baseline 已归档。
    - P10 targeted rocprof profiling 已归档。
    - P11 SpMV tuning 已归档；当前默认 SpMV algorithm 为 `HIPSPARSE_SPMV_CSR_ALG1`。
    - P12 记录了被拒绝的 SpMV buffer-algorithm consistency 实验。
    - P14-A1 补充了 quick6 current-vs-pre_tuning repeated validation。

    P14-A1 结果：

    - `current` 在 quick6 的 `6/6` 个 case 上快于 `pre_tuning`。
    - 几何平均 speedup：`1.18889`。
    - 中位数 speedup：`1.19502`。
    - pre/current 迭代数保持一致。

    P14-B CSR ALG1-vs-ALG2 repeated validation 不再是当前收尾 blocker。它可以保留为未来可选稳健性检查，但当前项目闭环不再需要继续补实验。

    见 [P14-A1 quick6 中文汇总](validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md)。
""").strip()

DOCS_EN = dedent("""
    ## Final W7900 repeated validation / 2026-06-18

    P14-A1 is the final repeated validation added for this project stage.

    - [P14-A1 quick6 summary](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md)
    - [P14-A1 quick6 Chinese summary](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md)
    - [P14-A1 comparison CSV](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv)

    Result: `current` is faster on `6/6` quick6 cases, with geometric-mean
    speedup `1.18889` and median speedup `1.19502`, while preserving iteration
    counts. P14-B remains future optional and is not a current blocker.
""").strip()

STATUS_EN = dedent("""
    ## Final W7900 closure after P14-A1 / 2026-06-18

    P14-A1 has now completed the representative repeated validation that was
    previously listed as optional. It compares `pre_tuning` (`ae3b683`) with
    current HEAD on the 890M-style quick6 set, with three repeats per
    case/version pair.

    Result:

    - `current` faster on `6/6` quick6 cases;
    - geometric-mean speedup `1.18889`;
    - median speedup `1.19502`;
    - iteration counts preserved.

    The current W7900 closure is therefore P10 + P11 + P12 + P14-A1. P14-B
    CSR ALG1-vs-ALG2 repeated validation is not required for current closure.
""").strip()

STATUS_ZH = dedent("""
    ## P14-A1 后的 W7900 最终收口 / 2026-06-18

    P14-A1 已完成此前列为可选增强的 representative repeated validation。它在
    890M-style quick6 case set 上对比 `pre_tuning`（`ae3b683`）与当前 HEAD，
    每个 case/version 组合重复 3 次。

    结果：

    - `current` 在 quick6 的 `6/6` 个 case 上更快；
    - 几何平均 speedup 为 `1.18889`；
    - 中位数 speedup 为 `1.19502`；
    - 迭代数保持一致。

    当前 W7900 收口证据链为 P10 + P11 + P12 + P14-A1。P14-B CSR ALG1-vs-ALG2
    repeated validation 不再是当前收尾所需实验。
""").strip()

OPT_EN = dedent("""
    ## Final before/after interpretation after P14-A1 / 2026-06-18

    The earlier “future before/after policy” has now been partially closed by
    P14-A1. The project does not need a new full W7900-specific after branch for
    the current endpoint.

    Current interpretation:

    | Role | Version | Current interpretation |
    |---|---|---|
    | Before | `pre_tuning` / `ae3b683` | true first-runnable/pre-tuning ROCm anchor |
    | Current endpoint | current `rocm-w7900-gfx1100` HEAD | accepted W7900 engineering endpoint with P11 default `HIPSPARSE_SPMV_CSR_ALG1` |
    | Repeated evidence | P14-A1 quick6 | current is faster on `6/6` quick6 cases; geomean `1.18889`; median `1.19502` |

    Do not describe P14-B as required. It remains a future optional robustness check only.
""").strip()

OPT_ZH = dedent("""
    ## P14-A1 后的最终 before/after 解释 / 2026-06-18

    早期 “future before/after policy” 已由 P14-A1 部分闭环。当前项目终点不需要再
    新建完整 W7900-specific after branch。

    当前解释：

    | 角色 | 版本 | 当前解释 |
    |---|---|---|
    | Before | `pre_tuning` / `ae3b683` | 真正 first-runnable / pre-tuning ROCm anchor |
    | Current endpoint | 当前 `rocm-w7900-gfx1100` HEAD | 已接受的 W7900 工程终点，包含 P11 默认 `HIPSPARSE_SPMV_CSR_ALG1` |
    | Repeated evidence | P14-A1 quick6 | current 在 quick6 的 `6/6` case 上更快；geomean `1.18889`；median `1.19502` |

    不要把 P14-B 描述为必做项。它仅保留为未来可选稳健性检查。
""").strip()

TUNING_EN = dedent("""
    ## Final W7900 tuning-guide status after P14-A1 / 2026-06-18

    This guide was originally centered on 890M / `gfx1150` tuning. The W7900 /
    `gfx1100` follow-up now has its own closure evidence:

    - P10 targeted profiling;
    - P11 SpMV algorithm policy, current default `HIPSPARSE_SPMV_CSR_ALG1`;
    - P12 rejected buffer-algorithm consistency experiment;
    - P14-A1 quick6 repeated current-vs-pre_tuning validation.

    P14-A1 shows `current` faster on `6/6` quick6 cases, with geomean speedup
    `1.18889` and median speedup `1.19502`.

    No further W7900 experiment is required for the current project closure.
""").strip()

TUNING_ZH = dedent("""
    ## P14-A1 后的 W7900 tuning-guide 最终状态 / 2026-06-18

    本指南最初围绕 890M / `gfx1150` tuning 编写。W7900 / `gfx1100` follow-up
    现在已有独立收口证据：

    - P10 targeted profiling；
    - P11 SpMV algorithm policy，当前默认 `HIPSPARSE_SPMV_CSR_ALG1`；
    - P12 rejected buffer-algorithm consistency experiment；
    - P14-A1 quick6 repeated current-vs-pre_tuning validation。

    P14-A1 显示 `current` 在 quick6 的 `6/6` 个 case 上更快，geomean speedup
    为 `1.18889`，median speedup 为 `1.19502`。

    当前项目收尾不再需要额外 W7900 实验。
""").strip()

def append_once(path: Path, section: str):
    text = path.read_text(encoding="utf-8")
    heading = section.splitlines()[0].strip()
    if heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return
    path.write_text(text.rstrip() + "\n\n" + section + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] updated {path.relative_to(ROOT)}")

def replace_phrases(path: Path, pairs):
    text = path.read_text(encoding="utf-8")
    old_text = text
    for old, new in pairs:
        text = text.replace(old, new)
    if text != old_text:
        path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
        print(f"[OK] replaced phrases in {path.relative_to(ROOT)}")

def main():
    for rel in ["README.md", "README.en.md"]:
        append_once(ROOT / rel, P14_EN)
    append_once(ROOT / "README.zh-CN.md", P14_ZH)

    append_once(ROOT / "docs/README.md", DOCS_EN)
    append_once(ROOT / "docs/W7900_CURRENT_STATUS.md", STATUS_EN)
    append_once(ROOT / "docs/W7900_CURRENT_STATUS.zh-CN.md", STATUS_ZH)
    append_once(ROOT / "docs/W7900_OPTIMIZATION_BASELINES.md", OPT_EN)
    append_once(ROOT / "docs/W7900_OPTIMIZATION_BASELINES.zh-CN.md", OPT_ZH)
    append_once(ROOT / "docs/TUNING_GUIDE_ROCM.md", TUNING_EN)
    append_once(ROOT / "docs/TUNING_GUIDE_ROCM.zh-CN.md", TUNING_ZH)

    replace_phrases(ROOT / "docs/W7900_CURRENT_STATUS.md", [
        ("The remaining items are optional evidence strengthening, not blockers: P14-A current-vs-before repeated validation and P14-B CSR ALG1-vs-ALG2 repeated validation, when a W7900 machine becomes available.",
         "P14-A1 current-vs-before quick6 repeated validation is now complete. P14-B CSR ALG1-vs-ALG2 repeated validation remains future optional only, not a closure blocker."),
        ("Future W7900-specific tuning should therefore optimize execution efficiency and convergence behavior together.",
         "P14-A1 now provides repeated quick-set evidence for the current endpoint; further tuning is future optional and should not be treated as a current blocker."),
    ])

    replace_phrases(ROOT / "docs/W7900_CURRENT_STATUS.zh-CN.md", [
        ("当前剩余内容不是 blocker，而是可选增强：P14-A current-vs-before repeated validation 与 P14-B CSR ALG1-vs-ALG2 repeated validation，等待 W7900 机器可用后再做。",
         "P14-A1 current-vs-before quick6 repeated validation 已完成。P14-B CSR ALG1-vs-ALG2 repeated validation 仅保留为未来可选项，不是当前收尾 blocker。"),
    ])

    replace_phrases(ROOT / "docs/W7900_OPTIMIZATION_BASELINES.md", [
        ("## Future before/after policy", "## Before/after policy status"),
        ("| After | future W7900-specific tuning branch | final W7900-specific optimized result |",
         "| Current endpoint | current `rocm-w7900-gfx1100` HEAD | accepted W7900 endpoint after P11/P14-A1 |"),
    ])

    replace_phrases(ROOT / "docs/W7900_OPTIMIZATION_BASELINES.zh-CN.md", [
        ("## 后续 before/after 策略", "## Before/after 策略状态"),
        ("| After | future W7900-specific tuning branch | 最终 W7900-specific optimized result |",
         "| Current endpoint | 当前 `rocm-w7900-gfx1100` HEAD | P11/P14-A1 后已接受的 W7900 endpoint |"),
    ])

    replace_phrases(ROOT / "docs/TUNING_GUIDE_ROCM.md", [
        ("- Compare `gfx1150` with `gfx1100` after W7900 migration.",
         "- `gfx1150` vs `gfx1100` comparison is now represented by W7900 P10/P11/P12/P14-A1 artifacts."),
    ])

    replace_phrases(ROOT / "docs/TUNING_GUIDE_ROCM.zh-CN.md", [
        ("对比 W7900 migration 之后的 `gfx1150` 与 `gfx1100`。",
         "`gfx1150` 与 `gfx1100` 的对比现在由 W7900 P10/P11/P12/P14-A1 artifacts 表示。"),
    ])

if __name__ == "__main__":
    main()
