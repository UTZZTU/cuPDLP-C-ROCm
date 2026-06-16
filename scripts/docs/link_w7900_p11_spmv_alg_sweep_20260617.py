#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

SECTIONS = {
    "validation/README.md": dedent("""
        ## W7900 P11 SpMV algorithm sweep / 2026-06-17

        This sweep evaluates the opt-in HIP SpMV algorithm switch across the five
        P10 targeted cases and three SpMV modes.

        - Summary: [w7900_p11_spmv_alg_sweep_20260617_summary.md](w7900_p11_spmv_alg_sweep_20260617_summary.md)
        - Chinese summary: [w7900_p11_spmv_alg_sweep_20260617_summary.zh-CN.md](w7900_p11_spmv_alg_sweep_20260617_summary.zh-CN.md)
        - CSV: [w7900_p11_spmv_alg_sweep_20260617.csv](w7900_p11_spmv_alg_sweep_20260617.csv)

        Key interpretation: all 15 runs complete successfully and preserve
        solver status and iteration count across modes. `csr_alg1` is slightly
        faster on most long cases, but the margin is small and should be treated
        as a promising experiment result rather than a final performance
        conclusion.
    """),
    "validation/README.zh-CN.md": dedent("""
        ## W7900 P11 SpMV algorithm sweep / 2026-06-17

        本次 sweep 在 P10 的 5 个 targeted case 上评估 opt-in HIP SpMV
        algorithm switch，共比较 3 种 SpMV mode。

        - 汇总：[w7900_p11_spmv_alg_sweep_20260617_summary.zh-CN.md](w7900_p11_spmv_alg_sweep_20260617_summary.zh-CN.md)
        - 英文汇总：[w7900_p11_spmv_alg_sweep_20260617_summary.md](w7900_p11_spmv_alg_sweep_20260617_summary.md)
        - CSV：[w7900_p11_spmv_alg_sweep_20260617.csv](w7900_p11_spmv_alg_sweep_20260617.csv)

        关键结论：15 个 run 全部成功完成，并且每个 case 在不同 mode 下保持
        solver status 和迭代数一致。`csr_alg1` 在多数长 case 上略快，但幅度很小，
        应写作“有希望的实验结果”，不能直接写成最终性能结论。
    """),
    "docs/W7900_CURRENT_STATUS.md": dedent("""
        ## P11 SpMV algorithm sweep / 2026-06-17

        P11 now includes a five-case, three-mode sweep for the opt-in HIP SpMV
        algorithm switch.

        Links:

        - [P11 SpMV algorithm sweep summary](../validation/w7900_p11_spmv_alg_sweep_20260617_summary.md)
        - [P11 SpMV algorithm sweep CSV](../validation/w7900_p11_spmv_alg_sweep_20260617.csv)
        - [P11 Chinese sweep summary](../validation/w7900_p11_spmv_alg_sweep_20260617_summary.zh-CN.md)

        The sweep confirms that `csr_alg2`, `env_default`, and `csr_alg1` all
        preserve solver status and iteration count on the five targeted cases.
        `csr_alg1` is slightly faster on most long cases in this single sweep,
        but the effect size is small. The next step should either repeat the
        sweep to estimate noise or run rocprofv3 on the most interesting pair,
        `csr_alg1` vs default `csr_alg2`.
    """),
    "docs/W7900_CURRENT_STATUS.zh-CN.md": dedent("""
        ## P11 SpMV algorithm sweep / 2026-06-17

        P11 已补充 opt-in HIP SpMV algorithm switch 的五 case、三 mode sweep。

        链接：

        - [P11 SpMV algorithm sweep 中文汇总](../validation/w7900_p11_spmv_alg_sweep_20260617_summary.zh-CN.md)
        - [P11 SpMV algorithm sweep CSV](../validation/w7900_p11_spmv_alg_sweep_20260617.csv)
        - [P11 英文 sweep 汇总](../validation/w7900_p11_spmv_alg_sweep_20260617_summary.md)

        sweep 确认 `csr_alg2`、`env_default` 和 `csr_alg1` 在 5 个 targeted case
        上都保持 solver status 和迭代数一致。单次 sweep 中，`csr_alg1` 在多数长
        case 上略快，但幅度很小。下一步应选择重复 sweep 估计噪声，或对最有代表性
        的 `csr_alg1` vs 默认 `csr_alg2` 做 rocprofv3 对比。
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
