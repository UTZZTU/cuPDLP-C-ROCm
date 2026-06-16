#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "validation"

SUMMARY = VALIDATION / "w7900_p11_spmv_tuning_summary_20260617.md"
SUMMARY_ZH = VALIDATION / "w7900_p11_spmv_tuning_summary_20260617.zh-CN.md"

README_SECTION = dedent("""
    ## W7900 P11 SpMV tuning summary / 2026-06-17

    This final P11 note summarizes the W7900 SpMV tuning path from P10 profiling
    to the default `HIPSPARSE_SPMV_CSR_ALG1` policy.

    - Summary: [w7900_p11_spmv_tuning_summary_20260617.md](w7900_p11_spmv_tuning_summary_20260617.md)
    - Chinese summary: [w7900_p11_spmv_tuning_summary_20260617.zh-CN.md](w7900_p11_spmv_tuning_summary_20260617.zh-CN.md)

    Key interpretation: P11 changes the current W7900 default SpMV algorithm to
    `csr_alg1` based on the five-case sweep, while preserving explicit rollback
    with `CUPDLP_HIP_SPMV_ALG=csr_alg2`. This is a W7900-specific tuning policy,
    not a final cross-platform performance claim.
""").strip()

README_ZH_SECTION = dedent("""
    ## W7900 P11 SpMV tuning 总结 / 2026-06-17

    本 P11 final note 总结 W7900 SpMV 调优路径：从 P10 profiling 到默认
    `HIPSPARSE_SPMV_CSR_ALG1` 策略。

    - 汇总：[w7900_p11_spmv_tuning_summary_20260617.zh-CN.md](w7900_p11_spmv_tuning_summary_20260617.zh-CN.md)
    - 英文汇总：[w7900_p11_spmv_tuning_summary_20260617.md](w7900_p11_spmv_tuning_summary_20260617.md)

    关键结论：P11 基于五 case sweep，将当前 W7900 默认 SpMV algorithm 改为
    `csr_alg1`，同时保留 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 显式回退路径。这是
    W7900-specific tuning 策略，不是最终跨平台性能结论。
""").strip()

STATUS_SECTION = dedent("""
    ## P11 SpMV tuning final note / 2026-06-17

    P11 closes the first W7900-specific tuning loop:

    - P10 targeted profiling identified rocSPARSE CSR SpMV as the dominant GPU
      kernel hotspot on the selected cases.
    - P11 added an opt-in HIP SpMV algorithm switch.
    - P11 smoke validation confirmed that `csr_alg2`, `default`, and `csr_alg1`
      modes are runnable on `set-cover-model`.
    - P11 five-case sweep confirmed that all three modes preserve solver status
      and iteration count on the targeted cases.
    - The current W7900 default is now `HIPSPARSE_SPMV_CSR_ALG1`.
    - The old default remains available with `CUPDLP_HIP_SPMV_ALG=csr_alg2`.

    Links:

    - [P11 SpMV tuning summary](../validation/w7900_p11_spmv_tuning_summary_20260617.md)
    - [P11 Chinese tuning summary](../validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md)

    This closes P11 as a conservative policy update. The result should be
    described as a W7900 current-default tuning choice, not as a final global
    performance conclusion.
""").strip()

STATUS_ZH_SECTION = dedent("""
    ## P11 SpMV tuning final note / 2026-06-17

    P11 完成第一条 W7900-specific tuning 闭环：

    - P10 targeted profiling 发现 rocSPARSE CSR SpMV 是所选 case 上的主要
      GPU kernel 热点。
    - P11 增加了 opt-in HIP SpMV algorithm switch。
    - P11 smoke validation 确认 `csr_alg2`、`default` 和 `csr_alg1` 三种模式
      在 `set-cover-model` 上均可运行。
    - P11 五 case sweep 确认三种模式在 targeted cases 上保持 solver status 和
      迭代数一致。
    - 当前 W7900 默认策略已切换为 `HIPSPARSE_SPMV_CSR_ALG1`。
    - 旧默认仍可通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 恢复。

    链接：

    - [P11 SpMV tuning 中文总结](../validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md)
    - [P11 英文 tuning summary](../validation/w7900_p11_spmv_tuning_summary_20260617.md)

    这使 P11 成为一个保守的策略更新闭环。该结果应表述为 W7900 当前默认调优
    选择，不应表述为最终全局性能结论。
""").strip()

def append_once(path: Path, section: str):
    text = path.read_text(encoding="utf-8")
    heading = section.splitlines()[0].strip()
    if heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return
    path.write_text(text.rstrip() + "\n\n" + section + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] updated {path.relative_to(ROOT)}")

def main():
    SUMMARY.write_text(dedent("""
        # W7900 P11 SpMV tuning summary

        This note closes the P11 W7900-specific SpMV tuning loop.

        ## Motivation

        P10 targeted profiling showed that rocSPARSE CSR SpMV is the dominant
        GPU kernel hotspot on the selected W7900 cases, while HIP API traces also
        showed significant host-device copy pressure. Because copy reduction can
        affect residual, restart, or termination logic, P11 first chose a safer
        execution-layer experiment: SpMV algorithm selection.

        ## What changed

        P11 introduced an opt-in HIP SpMV algorithm switch around the existing
        generic `hipsparseSpMV` calls:

        - default mode before P11-8-lite: `HIPSPARSE_SPMV_CSR_ALG2`
        - opt-in experiment: `CUPDLP_HIP_SPMV_ALG=default`
        - opt-in experiment: `CUPDLP_HIP_SPMV_ALG=csr_alg1`
        - rollback after default update: `CUPDLP_HIP_SPMV_ALG=csr_alg2`

        The final W7900 current default is now `HIPSPARSE_SPMV_CSR_ALG1`.

        ## Evidence chain

        1. `f1fe620` added P10 targeted rocprof summaries.
        2. `28f3796` added the P11 runtime callsite inventory.
        3. `f48b5fd` ranked first-patch candidates.
        4. `d1c2465` added the opt-in HIP SpMV algorithm switch.
        5. `48b1ad9` validated the switch on `set-cover-model`.
        6. `6ccf722` ran the five-case, three-mode SpMV sweep.
        7. `2643849` changed the W7900 default to CSR ALG1.
        8. `0649024` validated the new default and the CSR ALG2 rollback path.

        ## Final interpretation

        P11 should be described as a conservative W7900 tuning policy update:

        - The solver numerical path is not intentionally changed.
        - Solver status and iteration count remained stable in the five-case sweep.
        - `csr_alg1` showed a small favorable tendency on most long targeted cases.
        - The effect size is small, so this is not a final performance conclusion.
        - The old default is explicitly recoverable with `CUPDLP_HIP_SPMV_ALG=csr_alg2`.

        ## Next recommended work

        With limited time, P11 can be considered complete. The next useful work is
        documentation/report integration, not another long profiling run. If more
        tuning time becomes available later, the next technical direction is a
        careful scalar-copy analysis with explicit validation of residual,
        restart, termination, primal infeasibility, dual infeasibility, and
        duality gap.
    """).strip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] wrote {SUMMARY.relative_to(ROOT)}")

    SUMMARY_ZH.write_text(dedent("""
        # W7900 P11 SpMV tuning 总结

        本文档用于收尾 P11 的 W7900-specific SpMV 调优闭环。

        ## 动机

        P10 targeted profiling 显示，在所选 W7900 case 上，rocSPARSE CSR SpMV
        是主要 GPU kernel 热点；同时 HIP API trace 也显示 host-device copy 压力
        明显。由于 copy reduction 可能影响 residual、restart 或 termination 逻辑，
        P11 首先选择了更安全的执行层实验：SpMV algorithm selection。

        ## 改了什么

        P11 围绕已有 generic `hipsparseSpMV` 调用增加了 opt-in HIP SpMV
        algorithm switch：

        - P11-8-lite 之前的默认模式：`HIPSPARSE_SPMV_CSR_ALG2`
        - opt-in 实验：`CUPDLP_HIP_SPMV_ALG=default`
        - opt-in 实验：`CUPDLP_HIP_SPMV_ALG=csr_alg1`
        - 默认策略更新后的回退：`CUPDLP_HIP_SPMV_ALG=csr_alg2`

        最终当前 W7900 默认策略已切换为 `HIPSPARSE_SPMV_CSR_ALG1`。

        ## 证据链

        1. `f1fe620` 添加 P10 targeted rocprof summaries。
        2. `28f3796` 添加 P11 runtime callsite inventory。
        3. `f48b5fd` 排序 first-patch candidates。
        4. `d1c2465` 增加 opt-in HIP SpMV algorithm switch。
        5. `48b1ad9` 在 `set-cover-model` 上验证 switch。
        6. `6ccf722` 完成五 case、三 mode SpMV sweep。
        7. `2643849` 将 W7900 默认策略改为 CSR ALG1。
        8. `0649024` 验证新默认和 CSR ALG2 回退路径。

        ## 最终解释

        P11 应表述为一个保守的 W7900 tuning policy update：

        - 没有主动改变 solver 数值路径。
        - 五 case sweep 中 solver status 和迭代数保持稳定。
        - `csr_alg1` 在多数长 targeted case 上表现出小幅有利倾向。
        - 幅度较小，因此不能写成最终性能结论。
        - 旧默认可以通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 显式恢复。

        ## 下一步建议

        在时间有限的情况下，P11 可以视为完成。下一步更适合做文档/报告整合，
        而不是继续跑长 profiling。如果后续还有调优时间，再进入更谨慎的 scalar-copy
        分析，并明确验证 residual、restart、termination、primal infeasibility、
        dual infeasibility 和 duality gap。
    """).strip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] wrote {SUMMARY_ZH.relative_to(ROOT)}")

    append_once(ROOT / "validation" / "README.md", README_SECTION)
    append_once(ROOT / "validation" / "README.zh-CN.md", README_ZH_SECTION)
    append_once(ROOT / "docs" / "W7900_CURRENT_STATUS.md", STATUS_SECTION)
    append_once(ROOT / "docs" / "W7900_CURRENT_STATUS.zh-CN.md", STATUS_ZH_SECTION)

if __name__ == "__main__":
    main()
