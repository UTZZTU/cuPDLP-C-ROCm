#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

SECTIONS = {
    "validation/README.md": dedent("""
        ## W7900 P11 SpMV algorithm switch smoke / 2026-06-17

        This smoke validation checks the first real P11 tuning patch:
        an opt-in HIP SpMV algorithm switch.

        - Summary: [w7900_p11_spmv_alg_switch_smoke_20260617_summary.md](w7900_p11_spmv_alg_switch_smoke_20260617_summary.md)
        - Chinese summary: [w7900_p11_spmv_alg_switch_smoke_20260617_summary.zh-CN.md](w7900_p11_spmv_alg_switch_smoke_20260617_summary.zh-CN.md)
        - CSV: [w7900_p11_spmv_alg_switch_smoke_20260617.csv](w7900_p11_spmv_alg_switch_smoke_20260617.csv)

        Key interpretation: `set-cover-model` succeeds in all three modes:
        default `csr_alg2`, opt-in `default`, and opt-in `csr_alg1`. The patch
        preserves solver status and iteration count in the initial smoke test.
    """),
    "validation/README.zh-CN.md": dedent("""
        ## W7900 P11 SpMV algorithm switch smoke / 2026-06-17

        本次 smoke validation 检查第一个真正的 P11 tuning patch：
        opt-in HIP SpMV algorithm switch。

        - 汇总：[w7900_p11_spmv_alg_switch_smoke_20260617_summary.zh-CN.md](w7900_p11_spmv_alg_switch_smoke_20260617_summary.zh-CN.md)
        - 英文汇总：[w7900_p11_spmv_alg_switch_smoke_20260617_summary.md](w7900_p11_spmv_alg_switch_smoke_20260617_summary.md)
        - CSV：[w7900_p11_spmv_alg_switch_smoke_20260617.csv](w7900_p11_spmv_alg_switch_smoke_20260617.csv)

        关键结论：`set-cover-model` 在三种模式下均成功完成：默认 `csr_alg2`、
        opt-in `default` 和 opt-in `csr_alg1`。初始 smoke 中该 patch 保持了
        solver status 和迭代数一致。
    """),
    "docs/W7900_CURRENT_STATUS.md": dedent("""
        ## P11 SpMV algorithm switch smoke / 2026-06-17

        The first real P11 tuning patch adds an opt-in HIP SpMV algorithm switch.
        Default behavior remains `HIPSPARSE_SPMV_CSR_ALG2`.

        Links:

        - [P11 SpMV algorithm switch smoke summary](../validation/w7900_p11_spmv_alg_switch_smoke_20260617_summary.md)
        - [P11 SpMV algorithm switch smoke CSV](../validation/w7900_p11_spmv_alg_switch_smoke_20260617.csv)
        - [P11 Chinese smoke summary](../validation/w7900_p11_spmv_alg_switch_smoke_20260617_summary.zh-CN.md)

        The initial `set-cover-model` smoke passes for default `csr_alg2`,
        opt-in `default`, and opt-in `csr_alg1`. The next step is a targeted
        five-case sweep across the same three modes.
    """),
    "docs/W7900_CURRENT_STATUS.zh-CN.md": dedent("""
        ## P11 SpMV algorithm switch smoke / 2026-06-17

        第一个真正的 P11 tuning patch 增加了 opt-in HIP SpMV algorithm switch。
        默认行为仍然保持 `HIPSPARSE_SPMV_CSR_ALG2`。

        链接：

        - [P11 SpMV algorithm switch smoke 中文汇总](../validation/w7900_p11_spmv_alg_switch_smoke_20260617_summary.zh-CN.md)
        - [P11 SpMV algorithm switch smoke CSV](../validation/w7900_p11_spmv_alg_switch_smoke_20260617.csv)
        - [P11 英文 smoke 汇总](../validation/w7900_p11_spmv_alg_switch_smoke_20260617_summary.md)

        初始 `set-cover-model` smoke 在默认 `csr_alg2`、opt-in `default` 和
        opt-in `csr_alg1` 三种模式下均通过。下一步是在 P10 五个 targeted case
        上做三模式 sweep。
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
