#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

README = ROOT / "README.md"
README_EN = ROOT / "README.en.md"
README_ZH = ROOT / "README.zh-CN.md"

ZH_P14 = """## P14-A1 后的最终补充验证 / 2026-06-18

W7900 已补充 P14-A1 quick6 current-vs-pre_tuning repeated validation。结果显示
`current` 在 quick6 的 `6/6` 个 case 上快于 `pre_tuning`，几何平均 speedup 为
`1.18889`，中位数 speedup 为 `1.19502`，且 pre/current 迭代数保持一致。

这作为 quick-set tuning-transfer evidence，与 non-hard23 large-MPS baseline 分开表述。当前项目收尾不再需要额外 W7900 实验；P14-B 仅保留为未来可选稳健性检查。"""

EN_P14 = """## Final supplemental validation after P14-A1 / 2026-06-18

W7900 now includes P14-A1 quick6 current-vs-pre_tuning repeated validation.
`current` is faster than `pre_tuning` on `6/6` quick6 cases, with geometric-mean
speedup `1.18889` and median speedup `1.19502`, while preserving iteration counts.

This is quick-set tuning-transfer evidence and should be reported separately from
the non-hard23 large-MPS baseline. No additional W7900 experiment is required for
the current project closure; P14-B remains future optional only."""

EN_STATUS_OLD = """The ROCm/HIP backend has passed smoke validation, Netlib validation, cross-device benchmark checks, and large-MPS baseline testing on AMD Radeon 890M / `gfx1150`. The W7900 / `gfx1100` branch has completed smoke validation, Netlib 27-case validation, and a 23-case non-hard large-MPS baseline; the remaining large-MPS hard3 cases are tracked separately before full tuning. It is not yet a production-ready or fully tuned ROCm solver release."""

EN_STATUS_NEW = """The ROCm/HIP backend has passed smoke validation, Netlib validation, cross-device benchmark checks, and large-MPS baseline testing on AMD Radeon 890M / `gfx1150`. The W7900 / `gfx1100` branch has completed smoke validation, Netlib validation, non-hard large-MPS baseline, P10 targeted profiling, P11 SpMV tuning, P12 rejected-experiment documentation, and P14-A1 quick6 repeated validation. It is still an experimental ROCm solver branch rather than a production-certified solver release, but the current project-stage W7900 evidence chain is closed."""

def remove_wrong_english_block_from_chinese_readme(path: Path):
    s = path.read_text(encoding="utf-8")
    start = "## Final W7900 validation endpoint after P14-A1 / 2026-06-18"
    end = "## P14-A1 后的最终补充验证 / 2026-06-18"

    if start in s and end in s:
        pattern = re.escape(start) + r".*?(?=" + re.escape(end) + r")"
        s, n = re.subn(pattern, "", s, count=1, flags=re.S)
        if n != 1:
            raise RuntimeError(f"unexpected removal count: {n}")
        path.write_text(s.rstrip() + "\n", encoding="utf-8", newline="\n")
        print(f"[OK] removed wrong English P14 block from {path.relative_to(ROOT)}")
    else:
        print(f"[SKIP] no wrong English P14 block in {path.relative_to(ROOT)}")

def append_once(path: Path, section: str):
    s = path.read_text(encoding="utf-8")
    heading = section.splitlines()[0]
    if heading in s:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return
    path.write_text(s.rstrip() + "\n\n" + section + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] appended {heading} to {path.relative_to(ROOT)}")

def replace_once(path: Path, old: str, new: str):
    s = path.read_text(encoding="utf-8")
    if old not in s:
        print(f"[MISS] old status block not found in {path.relative_to(ROOT)}")
        return
    path.write_text(s.replace(old, new, 1).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] updated status block in {path.relative_to(ROOT)}")

def main():
    remove_wrong_english_block_from_chinese_readme(README)

    replace_once(README_EN, EN_STATUS_OLD, EN_STATUS_NEW)

    append_once(README, ZH_P14)
    append_once(README_ZH, ZH_P14)
    append_once(README_EN, EN_P14)

    # Guardrails
    readme = README.read_text(encoding="utf-8")
    if "## Final W7900 validation endpoint after P14-A1 / 2026-06-18" in readme:
        raise SystemExit("[ERR] README.md still contains wrong English P14 heading")

    en = README_EN.read_text(encoding="utf-8")
    if "## P14-A1 后的最终补充验证 / 2026-06-18" in en:
        raise SystemExit("[ERR] README.en.md contains Chinese P14 heading")

    print("[DONE] root README language/status fixed")

if __name__ == "__main__":
    main()
