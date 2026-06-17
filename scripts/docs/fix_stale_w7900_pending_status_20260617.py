#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write(path: Path, text: str):
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] wrote {path.relative_to(ROOT)}")

def replace_many(path: Path, replacements):
    if not path.exists():
        print(f"[MISS] {path.relative_to(ROOT)}")
        return

    text = read(path)
    changed = False

    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            changed = True
            print(f"[OK] replaced in {path.relative_to(ROOT)}: {old[:90]}")
        else:
            print(f"[MISS] exact text not found in {path.relative_to(ROOT)}: {old[:90]}")

    if changed:
        write(path, text)
    else:
        print(f"[SKIP] no replacements applied in {path.relative_to(ROOT)}")

def append_once(path: Path, section: str):
    if not path.exists():
        print(f"[MISS] {path.relative_to(ROOT)}")
        return

    text = read(path)
    heading = section.strip().splitlines()[0].strip()

    if heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return

    write(path, text.rstrip() + "\n\n" + section.strip() + "\n")

SUBMISSION_ZH_REPL = [
    (
        "| W7900 `rocprof` starter3 | 等 W7900 机器 | case: `set-cover-model.mps`, `square41.mps`, `s100.mps`。 |",
        "| W7900 `rocprof` starter3 | 已完成 | 已由 P10 targeted rocprof 和后续 P11/P12 证据链取代；见 `../validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md`。 |",
    ),
    (
        "| hard3 probe2 | 等 W7900 机器 | case: `dlr1.mps`, `fhnw-binschedule1.mps`。 |",
        "| hard3 probe2 | 已完成 | 已完成 600s probe2 记录；hard3 不混入 primary non-hard23 baseline。 |",
    ),
    (
        "| true before/current core6 | 等 W7900 机器 | `ae3b683 / pre_tuning` 对比当前 `rocm-w7900-gfx1100`。 |",
        "| true before/current core6 | 已完成；后续可补 repeated validation | 已有 fast-core6 before/current summary；若要增强性能说服力，后续在 W7900 代表 case 上补 3-repeat。 |",
    ),
    (
        "| W7900-specific tuning | 等 profiling 证据 | 不盲目调代码；等 profiler 结果后决定第一刀优化目标。 |",
        "| W7900-specific tuning | 已完成当前阶段 | P11 已完成 opt-in SpMV algorithm switch、五 case sweep，并将当前 W7900 默认设为 `HIPSPARSE_SPMV_CSR_ALG1`。 |",
    ),
    (
        "| W7900 profiling 结果摘要 | 等 W7900 机器 | 只提交 compact CSV/Markdown，不提交 raw profiler traces。 |",
        "| W7900 profiling 结果摘要 | 已完成 | P10/P11/P12 compact CSV/Markdown 已提交；raw profiler traces 仍不提交。 |",
    ),
    (
        "使用 `COMPETITION_README`、`COMPETITION_SCORECARD`、`REPRODUCIBILITY`、W7900 状态/性能文档，以及后续 profiling 结果。",
        "使用 `COMPETITION_README`、`COMPETITION_SCORECARD`、`REPRODUCIBILITY`、W7900 状态/性能文档，以及 P10/P11/P12 profiling/tuning 结果。",
    ),
    (
        "等论文大纲和 W7900 profiling 结果后制作。",
        "可基于 W7900 当前状态、P10 targeted profiling、P11 SpMV tuning 和 P12 rejected experiment note 制作。",
    ),
    (
        "在 `rocprof` 结果出来前，不要声称已经优化了 W7900-specific bottleneck。",
        "W7900-specific tuning 结论应以 P10/P11/P12 已提交证据为准；不要超出 `HIPSPARSE_SPMV_CSR_ALG1` 当前默认策略和 P12 rejected finding 的范围。",
    ),
]

SUBMISSION_EN_REPL = [
    (
        "| W7900 `rocprof` starter3 | Waiting for W7900 machine | cases: `set-cover-model.mps`, `square41.mps`, `s100.mps`. |",
        "| W7900 `rocprof` starter3 | Completed | Superseded by P10 targeted rocprof and the P11/P12 evidence chain; see `../validation/w7900_p10_current_targeted_rocprof_20260617_summary.md`. |",
    ),
    (
        "| hard3 probe2 | Waiting for W7900 machine | cases: `dlr1.mps`, `fhnw-binschedule1.mps`. |",
        "| hard3 probe2 | Completed | 600s probe2 record completed; hard3 is not mixed into the primary non-hard23 baseline. |",
    ),
    (
        "| true before/current core6 | Waiting for W7900 machine | `ae3b683 / pre_tuning` versus current `rocm-w7900-gfx1100`. |",
        "| true before/current core6 | Completed; repeated validation optional | fast-core6 before/current summary exists; representative W7900 3-repeat validation can be added later if stronger timing evidence is needed. |",
    ),
    (
        "| W7900-specific tuning | Waiting for profiling evidence | Do not tune blindly; use profiler results to choose the first optimization target. |",
        "| W7900-specific tuning | Completed for the current stage | P11 completed the opt-in SpMV algorithm switch, five-case sweep, and current default `HIPSPARSE_SPMV_CSR_ALG1` policy. |",
    ),
    (
        "| W7900 profiling summary | Waiting for W7900 machine | Commit compact CSV/Markdown only, not raw profiler trace directories. |",
        "| W7900 profiling summary | Completed | P10/P11/P12 compact CSV/Markdown artifacts are committed; raw profiler traces remain outside Git. |",
    ),
    (
        "Do not claim a W7900-specific bottleneck has been optimized before `rocprof` results exist.",
        "W7900-specific tuning claims should stay within the committed P10/P11/P12 evidence: current default `HIPSPARSE_SPMV_CSR_ALG1`, rollback with `CUPDLP_HIP_SPMV_ALG=csr_alg2`, and the P12 rejected experiment note.",
    ),
]

HIST_ZH_SECTION = dedent("""
    ## W7900 后续状态更新 / 2026-06-17

    本文档前半部分记录的是 890M / `gfx1150` 阶段的 repeated tuning ablation。
    其中，`current` 相对 `pre_tuning` 在 6-case quick set 上几何平均约为
    `1.094x speedup`，说明 ROCm/HIP 后端 tuning 在 890M 上有可测收益。

    但该结论不能直接替代 W7900 / `gfx1100` 的性能结论。W7900 是不同硬件目标，
    因此 W7900 已单独完成：

    - W7900 build、smoke validation、Netlib validation 和 large-MPS baseline；
    - P10 targeted rocprof profiling；
    - P11 SpMV algorithm switch、smoke 和五 case sweep；
    - 当前 W7900 默认 SpMV algorithm：
      `HIPSPARSE_SPMV_CSR_ALG1`；
    - 回退旧默认：
      `CUPDLP_HIP_SPMV_ALG=csr_alg2`；
    - P12 记录了被拒绝的 SpMV buffer algorithm consistency patch。

    若后续还要增强 W7900 的性能说服力，推荐只补一个小规模
    `current` vs `pre_tuning` repeated validation，而不是重跑完整 890M 式
    6-milestone ablation。
""").strip()

HIST_EN_SECTION = dedent("""
    ## W7900 follow-up status update / 2026-06-17

    The earlier part of this document records the 890M / `gfx1150` repeated
    tuning ablation. In that quick set, `current` achieved about `1.094x`
    geometric-mean speedup over `pre_tuning`, showing that ROCm/HIP tuning had
    measurable benefit on 890M.

    That result should not be used as a direct substitute for W7900 / `gfx1100`
    performance evidence. W7900 is a different hardware target, and it now has
    its own completed evidence chain:

    - W7900 build, smoke validation, Netlib validation, and large-MPS baseline;
    - P10 targeted rocprof profiling;
    - P11 SpMV algorithm switch, smoke, and five-case sweep;
    - current W7900 default SpMV algorithm:
      `HIPSPARSE_SPMV_CSR_ALG1`;
    - rollback:
      `CUPDLP_HIP_SPMV_ALG=csr_alg2`;
    - P12 rejected SpMV buffer algorithm consistency experiment.

    If stronger W7900 timing evidence is needed later, add a small
    `current` vs `pre_tuning` repeated validation instead of rerunning the full
    890M-style six-milestone ablation.
""").strip()

def main():
    replace_many(ROOT / "docs" / "SUBMISSION_CHECKLIST.zh-CN.md", SUBMISSION_ZH_REPL)
    replace_many(ROOT / "docs" / "SUBMISSION_CHECKLIST.md", SUBMISSION_EN_REPL)

    append_once(ROOT / "docs" / "ROCM_TUNING_HISTORY.zh-CN.md", HIST_ZH_SECTION)
    append_once(ROOT / "docs" / "ROCM_TUNING_HISTORY.md", HIST_EN_SECTION)

    print("[DONE] fixed stale W7900 pending status and updated 890M-vs-W7900 tuning interpretation")

if __name__ == "__main__":
    main()
