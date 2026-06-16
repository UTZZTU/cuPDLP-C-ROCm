#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

SECTIONS = {
    "validation/README.md": dedent("""
        ## W7900 P11 runtime callsite inventory / 2026-06-17

        P11 starts from a source-level runtime callsite inventory before applying
        optimization patches. This is intentionally a pre-patch triage step.

        - Summary: [w7900_p11_runtime_callsite_inventory_20260617.md](w7900_p11_runtime_callsite_inventory_20260617.md)
        - Chinese summary: [w7900_p11_runtime_callsite_inventory_20260617.zh-CN.md](w7900_p11_runtime_callsite_inventory_20260617.zh-CN.md)
        - CSV: [w7900_p11_runtime_callsite_inventory_20260617.csv](w7900_p11_runtime_callsite_inventory_20260617.csv)

        Key interpretation: P10 showed `hipMemcpy` as the rank-1 HIP API cost
        and `rocsparse::csrmvn_general_kernel` as the rank-1 GPU kernel across
        the targeted cases. P11 therefore first maps copy, synchronization,
        sparse-BLAS, BLAS, and kernel-launch callsites before changing code.
    """),
    "validation/README.zh-CN.md": dedent("""
        ## W7900 P11 runtime 调用点清单 / 2026-06-17

        P11 先从源码级 runtime callsite inventory 开始，再决定是否做优化 patch。
        这是有意设计的 pre-patch triage 步骤。

        - 汇总：[w7900_p11_runtime_callsite_inventory_20260617.zh-CN.md](w7900_p11_runtime_callsite_inventory_20260617.zh-CN.md)
        - 英文汇总：[w7900_p11_runtime_callsite_inventory_20260617.md](w7900_p11_runtime_callsite_inventory_20260617.md)
        - CSV：[w7900_p11_runtime_callsite_inventory_20260617.csv](w7900_p11_runtime_callsite_inventory_20260617.csv)

        关键结论：P10 显示 targeted cases 中 rank-1 HIP API 成本是 `hipMemcpy`，
        rank-1 GPU kernel 是 `rocsparse::csrmvn_general_kernel`。因此 P11 先定位
        copy、synchronization、sparse-BLAS、BLAS 和 kernel-launch 调用点，再决定是否改代码。
    """),
    "docs/W7900_CURRENT_STATUS.md": dedent("""
        ## P11 runtime callsite inventory / 2026-06-17

        P11 adds a source-level callsite inventory before making tuning patches.

        Links:

        - [P11 runtime callsite inventory](../validation/w7900_p11_runtime_callsite_inventory_20260617.md)
        - [P11 inventory CSV](../validation/w7900_p11_runtime_callsite_inventory_20260617.csv)
        - [P11 Chinese summary](../validation/w7900_p11_runtime_callsite_inventory_20260617.zh-CN.md)

        This inventory connects the P10 trace findings to source code locations.
        The next optimization patch should be execution-layer only and must not
        blindly change residual, restart, termination, scaling, or floating-point
        update order.
    """),
    "docs/W7900_CURRENT_STATUS.zh-CN.md": dedent("""
        ## P11 runtime 调用点清单 / 2026-06-17

        P11 在正式调优 patch 前，先补充源码级调用点清单。

        链接：

        - [P11 runtime 调用点清单](../validation/w7900_p11_runtime_callsite_inventory_20260617.zh-CN.md)
        - [P11 inventory CSV](../validation/w7900_p11_runtime_callsite_inventory_20260617.csv)
        - [P11 英文汇总](../validation/w7900_p11_runtime_callsite_inventory_20260617.md)

        该清单把 P10 trace 热点和源码位置联系起来。下一步优化 patch 应只属于
        execution-layer，不应盲目改动 residual、restart、termination、scaling 或
        浮点更新顺序。
    """),
}

def append_once(path: Path, section: str) -> bool:
    text = path.read_text(encoding="utf-8")
    heading = section.strip().splitlines()[0].strip()
    if heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return False
    path.write_text(text.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8")
    print(f"[OK] updated {path.relative_to(ROOT)}")
    return True

def main():
    changed = 0
    for rel, section in SECTIONS.items():
        changed += int(append_once(ROOT / rel, section))
    print(f"[DONE] updated {changed} files")

if __name__ == "__main__":
    main()
