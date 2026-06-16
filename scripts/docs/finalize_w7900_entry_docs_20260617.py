#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write(path: Path, text: str):
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] wrote {path.relative_to(ROOT)}")

def replace_all(path: Path, replacements):
    if not path.exists():
        print(f"[MISS] {path.relative_to(ROOT)}")
        return
    text = read(path)
    changed = False
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            changed = True
            print(f"[OK] replaced in {path.relative_to(ROOT)}: {old[:80]}")
    if changed:
        write(path, text)
    else:
        print(f"[SKIP] no exact replacements in {path.relative_to(ROOT)}")

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

README_EN_FINAL = dedent("""
    ## Final W7900 endpoint / 2026-06-17

    The W7900 / `gfx1100` project stage is complete for the current repository
    scope. It should no longer be described as only a future, baseline-only, or
    pre-tuning target.

    Current accepted endpoint:

    - W7900 build, smoke validation, Netlib validation, and large-MPS baseline
      documentation are complete.
    - P10 targeted rocprof profiling is complete.
    - P11 SpMV tuning is complete.
    - Current W7900 default SpMV algorithm:
      `HIPSPARSE_SPMV_CSR_ALG1`.
    - Rollback to the previous default:
      `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
    - P12 records a rejected SpMV buffer-algorithm consistency experiment where
      iteration count changed, so that patch was not accepted.

    Authoritative endpoints:

    - `docs/W7900_CURRENT_STATUS.md`
    - `validation/w7900_p11_spmv_tuning_summary_20260617.md`
    - `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md`
""").strip()

README_ZH_FINAL = dedent("""
    ## W7900 最终终点 / 2026-06-17

    当前仓库范围内，W7900 / `gfx1100` 阶段已经完成。它不应再被描述为未来目标、
    baseline-only 目标或 pre-tuning 目标。

    当前已接受终点：

    - W7900 build、smoke validation、Netlib validation 和 large-MPS baseline
      文档已完成。
    - P10 targeted rocprof profiling 已完成。
    - P11 SpMV tuning 已完成。
    - 当前 W7900 默认 SpMV algorithm：
      `HIPSPARSE_SPMV_CSR_ALG1`。
    - 回退旧默认：
      `CUPDLP_HIP_SPMV_ALG=csr_alg2`。
    - P12 记录了一次被拒绝的 SpMV buffer-algorithm consistency 实验；该实验导致
      迭代数变化，因此未接受该 patch。

    权威入口：

    - `docs/W7900_CURRENT_STATUS.zh-CN.md`
    - `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`
    - `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md`
""").strip()

DOCS_README_SECTION = dedent("""
    ## Final W7900 endpoint documents / 2026-06-17

    The W7900 / `gfx1100` project stage is complete for the current repository
    scope. Use the following documents as the final W7900 entry points:

    | Topic | English | 中文 |
    |---|---|---|
    | W7900 current status | [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md) | [W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md) |
    | P11 SpMV tuning summary | [../validation/w7900_p11_spmv_tuning_summary_20260617.md](../validation/w7900_p11_spmv_tuning_summary_20260617.md) | [../validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md](../validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md) |
    | P12 rejected experiment note | [../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md) | [../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md) |
    | P10 targeted rocprof summary | [../validation/w7900_p10_current_targeted_rocprof_20260617_summary.md](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.md) | [../validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md) |

    Current W7900 tuning policy:

    - default SpMV algorithm: `HIPSPARSE_SPMV_CSR_ALG1`;
    - rollback: `CUPDLP_HIP_SPMV_ALG=csr_alg2`;
    - P12 buffer algorithm consistency patch: tested and rejected because
      iteration count changed.
""").strip()

COMPETITION_EN = dedent("""
    ## Final W7900 competition status / 2026-06-17

    The W7900 competition-facing workflow is now complete for the current
    repository scope. Earlier “next planned work” items such as W7900 profiling,
    before/current analysis, and W7900-specific tuning have been closed by the
    P10/P11/P12 evidence chain.

    Final competition-facing conclusion:

    - W7900 / `gfx1100` ROCm build and validation are complete.
    - P10 targeted rocprof profiling has been archived.
    - P11 SpMV tuning is the accepted W7900-specific tuning endpoint.
    - The current W7900 default SpMV algorithm is
      `HIPSPARSE_SPMV_CSR_ALG1`.
    - The old default can be restored with
      `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
    - P12 records a rejected buffer-algorithm consistency patch to show that
      additional execution-layer changes were tested conservatively.

    Recommended final evidence links:

    - `docs/W7900_CURRENT_STATUS.md`
    - `validation/w7900_p11_spmv_tuning_summary_20260617.md`
    - `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md`
""").strip()

COMPETITION_ZH = dedent("""
    ## W7900 竞赛口径最终状态 / 2026-06-17

    当前仓库范围内，面向竞赛展示的 W7900 工作流已经完成。此前写作“next planned
    work”的 W7900 profiling、before/current analysis 和 W7900-specific tuning
    已由 P10/P11/P12 证据链闭环。

    最终竞赛口径结论：

    - W7900 / `gfx1100` ROCm build 和 validation 已完成。
    - P10 targeted rocprof profiling 已归档。
    - P11 SpMV tuning 是已接受的 W7900-specific tuning endpoint。
    - 当前 W7900 默认 SpMV algorithm 为
      `HIPSPARSE_SPMV_CSR_ALG1`。
    - 旧默认可通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 恢复。
    - P12 记录了一次被拒绝的 buffer-algorithm consistency patch，说明额外
      execution-layer 改动也经过了保守验证。

    推荐最终证据入口：

    - `docs/W7900_CURRENT_STATUS.zh-CN.md`
    - `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`
    - `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md`
""").strip()

PLAN_EN = dedent("""
    ## Completion update / 2026-06-17

    This document is the original W7900 profiling plan. The plan has now been
    executed and superseded by committed P10/P11/P12 artifacts.

    Current status:

    - P10 targeted rocprof profiling completed.
    - P11 SpMV algorithm switch, smoke, and five-case sweep completed.
    - Current W7900 default SpMV algorithm:
      `HIPSPARSE_SPMV_CSR_ALG1`.
    - Rollback path:
      `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
    - P12 SpMV buffer algorithm consistency experiment tested and rejected
      because it changed iteration count.

    Superseding documents:

    - `validation/w7900_p10_current_targeted_rocprof_20260617_summary.md`
    - `validation/w7900_p11_spmv_tuning_summary_20260617.md`
    - `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md`
""").strip()

PLAN_ZH = dedent("""
    ## 完成状态更新 / 2026-06-17

    本文档是原始 W7900 profiling plan。该计划现在已经执行完毕，并由已提交的
    P10/P11/P12 artifacts 取代。

    当前状态：

    - P10 targeted rocprof profiling 已完成。
    - P11 SpMV algorithm switch、smoke 和五 case sweep 已完成。
    - 当前 W7900 默认 SpMV algorithm：
      `HIPSPARSE_SPMV_CSR_ALG1`。
    - 回退路径：
      `CUPDLP_HIP_SPMV_ALG=csr_alg2`。
    - P12 SpMV buffer algorithm consistency 实验已测试并拒绝，因为它改变了迭代数。

    取代本文档的最终材料：

    - `validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md`
    - `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`
    - `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md`
""").strip()

OPT_EN = dedent("""
    ## Completion update / 2026-06-17

    This document originally defined the before/after policy for W7900
    optimization. The accepted W7900-specific tuning endpoint is now available.

    Accepted endpoint:

    - P11 changed the current W7900 default SpMV algorithm to
      `HIPSPARSE_SPMV_CSR_ALG1`.
    - The old default remains available with
      `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
    - P11 five-case sweep preserved solver status and iteration count across
      the evaluated SpMV modes.
    - P12 tested one additional SpMV buffer algorithm consistency patch and
      rejected it because the iteration count changed.

    Final references:

    - `validation/w7900_p11_spmv_tuning_summary_20260617.md`
    - `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md`
""").strip()

OPT_ZH = dedent("""
    ## 完成状态更新 / 2026-06-17

    本文档最初定义 W7900 optimization 的 before/after policy。当前已存在被接受的
    W7900-specific tuning endpoint。

    已接受终点：

    - P11 将当前 W7900 默认 SpMV algorithm 改为
      `HIPSPARSE_SPMV_CSR_ALG1`。
    - 旧默认仍可通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 恢复。
    - P11 五 case sweep 在评估的 SpMV modes 上保持 solver status 和迭代数稳定。
    - P12 额外测试了一个 SpMV buffer algorithm consistency patch，并因迭代数变化
      将其拒绝。

    最终参考：

    - `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`
    - `validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md`
""").strip()

def main():
    # README exact phrase replacements for stale W7900 table/bullets.
    readme_common_replacements = [
        (
            "已建立 baseline 的额外 ROCm 目标 | AMD Radeon PRO W7900 / `gfx1100`",
            "已完成验证与调优的额外 ROCm 目标 | AMD Radeon PRO W7900 / `gfx1100`"
        ),
        (
            "W7900 / `gfx1100` build、smoke validation、Netlib 27-case validation 和 large-MPS non-hard23 baseline 记录。",
            "W7900 / `gfx1100` build、smoke validation、Netlib validation、large-MPS baseline、P10 profiling、P11 SpMV tuning 和 P12 rejected experiment 记录。"
        ),
        (
            "Radeon PRO W7900 | ROCm/HIP 当前继承 890M 调优后的工程基线 | non-hard large-MPS 23/23 OPTIMAL；hard3 单独跟踪",
            "Radeon PRO W7900 | ROCm/HIP W7900 当前调优终点 | non-hard large-MPS 23/23 OPTIMAL；P10 profiling、P11 SpMV tuning、P12 rejected experiment 已归档"
        ),
        (
            "Radeon PRO W7900 | ROCm/HIP inherited engineering baseline after 890M tuning | non-hard large-MPS 23/23 OPTIMAL; hard3 tracked separately",
            "Radeon PRO W7900 | ROCm/HIP W7900 current tuning endpoint | non-hard large-MPS 23/23 OPTIMAL; P10 profiling, P11 SpMV tuning, and P12 rejected experiment archived"
        ),
    ]

    for rel in ["README.md", "README.zh-CN.md", "README.en.md"]:
        replace_all(ROOT / rel, readme_common_replacements)

    append_once(ROOT / "README.md", README_ZH_FINAL)
    append_once(ROOT / "README.zh-CN.md", README_ZH_FINAL)
    append_once(ROOT / "README.en.md", README_EN_FINAL)

    append_once(ROOT / "docs" / "README.md", DOCS_README_SECTION)

    for rel, section in [
        ("docs/COMPETITION_README.md", COMPETITION_EN),
        ("docs/COMPETITION_SCORECARD.md", COMPETITION_EN),
        ("docs/SUBMISSION_CHECKLIST.md", COMPETITION_EN),
        ("docs/COMPETITION_README.zh-CN.md", COMPETITION_ZH),
        ("docs/COMPETITION_SCORECARD.zh-CN.md", COMPETITION_ZH),
        ("docs/SUBMISSION_CHECKLIST.zh-CN.md", COMPETITION_ZH),
        ("docs/W7900_ROCM_PROFILING_PLAN.md", PLAN_EN),
        ("docs/W7900_ROCM_PROFILING_PLAN.zh-CN.md", PLAN_ZH),
        ("docs/W7900_OPTIMIZATION_BASELINES.md", OPT_EN),
        ("docs/W7900_OPTIMIZATION_BASELINES.zh-CN.md", OPT_ZH),
    ]:
        append_once(ROOT / rel, section)

    print("[DONE] finalized W7900 entry, competition, plan, and baseline documents")

if __name__ == "__main__":
    main()
