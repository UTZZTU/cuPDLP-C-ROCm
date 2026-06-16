#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

SECTIONS = {
    "validation/README.md": dedent("""
        ## W7900 P11 first patch candidates / 2026-06-17

        P11 first-patch candidate analysis combines the P10 targeted rocprof
        results with the P11 runtime callsite inventory. It ranks the safest
        next optimization directions before changing solver code.

        - Summary: [w7900_p11_first_patch_candidates_20260617.md](w7900_p11_first_patch_candidates_20260617.md)
        - Chinese summary: [w7900_p11_first_patch_candidates_20260617.zh-CN.md](w7900_p11_first_patch_candidates_20260617.zh-CN.md)
        - CSV: [w7900_p11_first_patch_candidates_20260617.csv](w7900_p11_first_patch_candidates_20260617.csv)

        Key interpretation: copy reduction is attractive because P10 shows
        `hipMemcpy` as the rank-1 HIP API cost, but it is also numerically risky
        if the copies are tied to residual, restart, or termination logic. The
        first code patch should therefore be opt-in and validation-driven.
    """),
    "validation/README.zh-CN.md": dedent("""
        ## W7900 P11 第一轮优化候选 / 2026-06-17

        P11 first-patch candidate analysis 把 P10 targeted rocprof 结果和
        P11 runtime 调用点清单结合起来，在真正改 solver 代码前，对下一步安全
        优化方向进行排序。

        - 汇总：[w7900_p11_first_patch_candidates_20260617.zh-CN.md](w7900_p11_first_patch_candidates_20260617.zh-CN.md)
        - 英文汇总：[w7900_p11_first_patch_candidates_20260617.md](w7900_p11_first_patch_candidates_20260617.md)
        - CSV：[w7900_p11_first_patch_candidates_20260617.csv](w7900_p11_first_patch_candidates_20260617.csv)

        关键结论：copy reduction 很诱人，因为 P10 显示 `hipMemcpy` 是 rank-1
        HIP API 成本；但如果这些 copy 绑定 residual、restart 或 termination 逻辑，
        就具有数值风险。因此第一个代码 patch 应该是 opt-in 且必须经过验证。
    """),
    "docs/W7900_CURRENT_STATUS.md": dedent("""
        ## P11 first patch candidates / 2026-06-17

        P11 first-patch candidate analysis ranks the next safe tuning directions
        after P10 profiling and P11 callsite inventory.

        Links:

        - [P11 first patch candidates](../validation/w7900_p11_first_patch_candidates_20260617.md)
        - [P11 first patch candidates CSV](../validation/w7900_p11_first_patch_candidates_20260617.csv)
        - [P11 Chinese summary](../validation/w7900_p11_first_patch_candidates_20260617.zh-CN.md)

        The current recommendation is to avoid blind `hipMemcpy` removal. The
        first real code change should be an opt-in experiment, preferably either
        an SpMV algorithm-selection/profiling switch or a narrowly guarded
        scalar-copy experiment with explicit fast-core6 and P10 validation.
    """),
    "docs/W7900_CURRENT_STATUS.zh-CN.md": dedent("""
        ## P11 第一轮优化候选 / 2026-06-17

        P11 first-patch candidate analysis 在 P10 profiling 和 P11 调用点清单
        之后，对下一步安全调优方向进行排序。

        链接：

        - [P11 第一轮优化候选中文汇总](../validation/w7900_p11_first_patch_candidates_20260617.zh-CN.md)
        - [P11 first patch candidates CSV](../validation/w7900_p11_first_patch_candidates_20260617.csv)
        - [P11 英文汇总](../validation/w7900_p11_first_patch_candidates_20260617.md)

        当前建议是不要盲目删除 `hipMemcpy`。第一个真正代码改动应是 opt-in
        实验，优先考虑 SpMV algorithm-selection/profiling 开关，或一个窄范围、
        有保护的 scalar-copy experiment，并用 fast-core6 和 P10 targeted cases 明确验证。
    """),
}

def append_once(path: Path, section: str) -> bool:
    text = path.read_text(encoding="utf-8")
    heading = section.strip().splitlines()[0].strip()
    if heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return False
    path.write_text(text.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] updated {path.relative_to(ROOT)}")
    return True

def main():
    changed = 0
    for rel, section in SECTIONS.items():
        changed += int(append_once(ROOT / rel, section))
    print(f"[DONE] updated {changed} files")

if __name__ == "__main__":
    main()
