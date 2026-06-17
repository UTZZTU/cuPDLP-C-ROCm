#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REPLACEMENTS = {
    "docs/W7900_CURRENT_STATUS.md": [
        (
            "The remaining items are optional evidence strengthening, not blockers:\nP14-A current-vs-before repeated validation and P14-B CSR ALG1-vs-ALG2\nrepeated validation, when a W7900 machine becomes available.",
            "P14-A1 current-vs-before quick6 repeated validation is now complete. P14-B CSR ALG1-vs-ALG2 repeated validation remains future optional only, not a current closure blocker."
        ),
        (
            "Future W7900-specific tuning should therefore optimize\nexecution efficiency and convergence behavior together.",
            "P14-A1 now provides repeated quick-set evidence for the current endpoint. Further W7900-specific tuning is future optional and should not be treated as a current closure blocker."
        ),
    ],
    "docs/W7900_CURRENT_STATUS.zh-CN.md": [
        (
            "因此后续 W7900-specific tuning 应同时优化执行效率\n和收敛行为。",
            "P14-A1 已提供 current endpoint 的 repeated quick-set 证据。后续 W7900-specific tuning 仅保留为未来可选项，不是当前收尾 blocker。"
        ),
        (
            "当前剩余内容不是 blocker，而是可选增强：P14-A current-vs-before repeated validation 与 P14-B CSR ALG1-vs-ALG2 repeated validation，等待 W7900 机器可用后再做。",
            "P14-A1 current-vs-before quick6 repeated validation 已完成。P14-B CSR ALG1-vs-ALG2 repeated validation 仅保留为未来可选项，不是当前收尾 blocker。"
        ),
    ],
    "docs/W7900_ROCM_PROFILING_PLAN.md": [
        (
            "The current W7900 branch has already inherited earlier 890M/gfx1150 ROCm tuning. Future profiling should therefore distinguish `ae3b683` as the true pre-tuning anchor, current W7900 as the post-890M-tuning engineering baseline, and a future W7900-specific tuning branch as the final after-tuning result.",
            "The current W7900 branch inherited earlier 890M/gfx1150 ROCm tuning and has now completed its own P10/P11/P12/P14-A1 evidence chain. `ae3b683` remains the true pre-tuning anchor, while current W7900 HEAD is the accepted project endpoint after P11 and P14-A1."
        ),
    ],
    "docs/W7900_ROCM_PROFILING_PLAN.zh-CN.md": [
        (
            "当前 W7900 分支已经继承此前 890M/gfx1150 ROCm tuning。后续 profiling 应区分：`ae3b683` 作为真正 pre-tuning anchor，current W7900 作为 post-890M-tuning engineering baseline，future W7900-specific tuning branch 作为最终 after-tuning 结果。",
            "当前 W7900 分支继承了此前 890M/gfx1150 ROCm tuning，并已经完成自身 P10/P11/P12/P14-A1 证据链。`ae3b683` 仍作为真正 pre-tuning anchor，当前 W7900 HEAD 是 P11 和 P14-A1 后已接受的项目终点。"
        ),
    ],
    "validation/w7900_before_current_core6_fast_summary_20260616.md": [
        (
            "This mixed result further supports the need for W7900-specific profiling and tuning.",
            "This mixed result was later addressed by the W7900 P10/P11/P12/P14-A1 evidence chain. In particular, P14-A1 provides repeated quick-set current-vs-pre_tuning validation, while this fast-core6 result remains a historical mixed-pattern note."
        ),
    ],
    "validation/w7900_before_current_core6_fast_summary_20260616.zh-CN.md": [
        (
            "该混合结果进一步说明后续 W7900-specific profiling 和 tuning 是必要的。",
            "该混合结果后来由 W7900 P10/P11/P12/P14-A1 证据链进一步补充说明。尤其是 P14-A1 已提供 repeated quick-set current-vs-pre_tuning validation；本文保留为 fast-core6 mixed-pattern 历史记录。"
        ),
    ],
}

README_APPEND = {
    "README.md": """
## P14-A1 后的最终补充验证 / 2026-06-18

W7900 已补充 P14-A1 quick6 current-vs-pre_tuning repeated validation。结果显示
`current` 在 quick6 的 `6/6` 个 case 上快于 `pre_tuning`，几何平均 speedup 为
`1.18889`，中位数 speedup 为 `1.19502`，且 pre/current 迭代数保持一致。

这作为 quick-set tuning-transfer evidence，与 non-hard23 large-MPS baseline 分开表述。当前项目收尾不再需要额外 W7900 实验；P14-B 仅保留为未来可选稳健性检查。
""",
    "README.zh-CN.md": """
## P14-A1 后的最终补充验证 / 2026-06-18

W7900 已补充 P14-A1 quick6 current-vs-pre_tuning repeated validation。结果显示
`current` 在 quick6 的 `6/6` 个 case 上快于 `pre_tuning`，几何平均 speedup 为
`1.18889`，中位数 speedup 为 `1.19502`，且 pre/current 迭代数保持一致。

这作为 quick-set tuning-transfer evidence，与 non-hard23 large-MPS baseline 分开表述。当前项目收尾不再需要额外 W7900 实验；P14-B 仅保留为未来可选稳健性检查。
""",
    "README.en.md": """
## Final supplemental validation after P14-A1 / 2026-06-18

W7900 now includes P14-A1 quick6 current-vs-pre_tuning repeated validation.
`current` is faster than `pre_tuning` on `6/6` quick6 cases, with geometric-mean
speedup `1.18889` and median speedup `1.19502`, while preserving iteration counts.

This is quick-set tuning-transfer evidence and should be reported separately from
the non-hard23 large-MPS baseline. No additional W7900 experiment is required for
the current project closure; P14-B remains future optional only.
""",
}

def replace_file(rel: str, pairs):
    p = ROOT / rel
    if not p.exists():
        print("[MISS]", rel)
        return
    s = p.read_text(encoding="utf-8")
    old = s
    for a, b in pairs:
        if a in s:
            s = s.replace(a, b, 1)
            print("[OK]", rel, "replace:", a[:60])
        else:
            print("[MISS]", rel, "phrase:", a[:60])
    if s != old:
        p.write_text(s.rstrip() + "\n", encoding="utf-8", newline="\n")

def append_once(rel: str, section: str):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    heading = section.strip().splitlines()[0]
    if heading in s:
        print("[SKIP]", rel, heading)
        return
    p.write_text(s.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8", newline="\n")
    print("[OK]", rel, "append:", heading)

def main():
    for rel, pairs in REPLACEMENTS.items():
        replace_file(rel, pairs)
    for rel, section in README_APPEND.items():
        append_once(rel, section)
    print("[DONE] fixed remaining stale P14-A1/W7900 wording")

if __name__ == "__main__":
    main()
