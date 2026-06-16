#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

SECTIONS = {
    "validation/README.md": dedent("""
        ## W7900 P11 default SpMV ALG1 smoke / 2026-06-17

        This smoke validation checks the P11 default-policy update after the
        five-case SpMV algorithm sweep.

        - Summary: [w7900_p11_default_spmv_alg1_smoke_20260617_summary.md](w7900_p11_default_spmv_alg1_smoke_20260617_summary.md)
        - Chinese summary: [w7900_p11_default_spmv_alg1_smoke_20260617_summary.zh-CN.md](w7900_p11_default_spmv_alg1_smoke_20260617_summary.zh-CN.md)
        - CSV: [w7900_p11_default_spmv_alg1_smoke_20260617.csv](w7900_p11_default_spmv_alg1_smoke_20260617.csv)

        Key interpretation: the no-env default path now uses
        `HIPSPARSE_SPMV_CSR_ALG1`, while the previous default can still be
        restored with `CUPDLP_HIP_SPMV_ALG=csr_alg2`. The smoke confirms both
        paths solve `set-cover-model` successfully with the same iteration count.
    """),
    "validation/README.zh-CN.md": dedent("""
        ## W7900 P11 default SpMV ALG1 smoke / 2026-06-17

        本次 smoke validation 检查 P11 在五 case SpMV algorithm sweep 之后的
        默认策略更新。

        - 汇总：[w7900_p11_default_spmv_alg1_smoke_20260617_summary.zh-CN.md](w7900_p11_default_spmv_alg1_smoke_20260617_summary.zh-CN.md)
        - 英文汇总：[w7900_p11_default_spmv_alg1_smoke_20260617_summary.md](w7900_p11_default_spmv_alg1_smoke_20260617_summary.md)
        - CSV：[w7900_p11_default_spmv_alg1_smoke_20260617.csv](w7900_p11_default_spmv_alg1_smoke_20260617.csv)

        关键结论：无环境变量默认路径现在使用 `HIPSPARSE_SPMV_CSR_ALG1`，
        旧默认仍可通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 恢复。smoke 确认两个路径
        都能成功求解 `set-cover-model`，且迭代数一致。
    """),
    "docs/W7900_CURRENT_STATUS.md": dedent("""
        ## P11 default SpMV ALG1 smoke / 2026-06-17

        P11 now defaults the HIP SpMV algorithm to `HIPSPARSE_SPMV_CSR_ALG1`
        for W7900 current tuning, while preserving an explicit rollback path:

        - rollback: `CUPDLP_HIP_SPMV_ALG=csr_alg2`
        - hipSPARSE default experiment: `CUPDLP_HIP_SPMV_ALG=default`

        Links:

        - [P11 default SpMV ALG1 smoke summary](../validation/w7900_p11_default_spmv_alg1_smoke_20260617_summary.md)
        - [P11 default SpMV ALG1 smoke CSV](../validation/w7900_p11_default_spmv_alg1_smoke_20260617.csv)
        - [P11 Chinese smoke summary](../validation/w7900_p11_default_spmv_alg1_smoke_20260617_summary.zh-CN.md)

        This is a policy update based on the P11 five-case sweep. It should be
        described as the current W7900 default tuning choice, not as a final
        cross-platform performance conclusion.
    """),
    "docs/W7900_CURRENT_STATUS.zh-CN.md": dedent("""
        ## P11 default SpMV ALG1 smoke / 2026-06-17

        P11 现在将 W7900 当前调优默认 HIP SpMV algorithm 设为
        `HIPSPARSE_SPMV_CSR_ALG1`，同时保留显式回退路径：

        - 回退旧默认：`CUPDLP_HIP_SPMV_ALG=csr_alg2`
        - hipSPARSE default 实验：`CUPDLP_HIP_SPMV_ALG=default`

        链接：

        - [P11 default SpMV ALG1 smoke 中文汇总](../validation/w7900_p11_default_spmv_alg1_smoke_20260617_summary.zh-CN.md)
        - [P11 default SpMV ALG1 smoke CSV](../validation/w7900_p11_default_spmv_alg1_smoke_20260617.csv)
        - [P11 英文 smoke 汇总](../validation/w7900_p11_default_spmv_alg1_smoke_20260617_summary.md)

        这是基于 P11 五 case sweep 的策略更新。应描述为当前 W7900 默认调优选择，
        不应写成最终跨平台性能结论。
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
