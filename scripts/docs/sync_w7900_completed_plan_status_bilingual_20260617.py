#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent
import re

ROOT = Path(__file__).resolve().parents[2]

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write(path: Path, text: str):
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] wrote {path.relative_to(ROOT)}")

def replace_once(path: Path, old: str, new: str):
    text = read(path)
    if old not in text:
        print(f"[MISS] {path.relative_to(ROOT)}: {old[:100]}")
        return False
    text = text.replace(old, new, 1)
    write(path, text)
    print(f"[OK] replaced in {path.relative_to(ROOT)}")
    return True

def replace_section(path: Path, start_marker: str, end_marker: str, replacement: str):
    text = read(path)
    start = text.find(start_marker)
    if start < 0:
        print(f"[MISS] start marker in {path.relative_to(ROOT)}: {start_marker}")
        return False
    if end_marker:
        end = text.find(end_marker, start)
        if end < 0:
            print(f"[MISS] end marker in {path.relative_to(ROOT)}: {end_marker}")
            return False
    else:
        end = len(text)
    new_text = text[:start] + replacement.strip() + "\n\n" + text[end:]
    write(path, new_text)
    print(f"[OK] replaced section {start_marker!r} -> {end_marker or 'EOF'!r} in {path.relative_to(ROOT)}")
    return True

def append_once(path: Path, section: str):
    text = read(path)
    heading = section.strip().splitlines()[0].strip()
    if heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return False
    write(path, text.rstrip() + "\n\n" + section.strip() + "\n")
    print(f"[OK] appended {heading} to {path.relative_to(ROOT)}")
    return True

COMP_EN = Path("docs/COMPETITION_README.md")
COMP_ZH = Path("docs/COMPETITION_README.zh-CN.md")
STATUS_EN = Path("docs/W7900_CURRENT_STATUS.md")
STATUS_ZH = Path("docs/W7900_CURRENT_STATUS.zh-CN.md")
WORKFLOW_EN = Path("docs/ROCM_WORKFLOW.md")
WORKFLOW_ZH = Path("docs/ROCM_WORKFLOW.zh-CN.md")
VALID_EN = Path("docs/VALIDATION.md")
VALID_ZH = Path("docs/VALIDATION.zh-CN.md")
HIST_EN = Path("docs/ROCM_TUNING_HISTORY.md")
HIST_ZH = Path("docs/ROCM_TUNING_HISTORY.zh-CN.md")

COMP_EN_REPL = [
    (
        "Radeon PRO W7900 / `gfx1100` | Large-MPS workstation GPU validation and future W7900-specific profiling/tuning",
        "Radeon PRO W7900 / `gfx1100` | Large-MPS workstation GPU validation, P10 profiling, P11 SpMV tuning, and P12 rejected experiment record",
    ),
    (
        "| After | future W7900-specific tuning branch | final W7900-specific optimized result |",
        "| After / accepted endpoint | P11 current W7900 tuning policy | current default `HIPSPARSE_SPMV_CSR_ALG1`, rollback with `CUPDLP_HIP_SPMV_ALG=csr_alg2` |",
    ),
    (
        "| Demo PPT | to be created after first profiling results |",
        "| Demo PPT | can be created from W7900 current status, P10 targeted profiling, P11 SpMV tuning, P12 rejected finding, and cuPDLPx positioning |",
    ),
]

COMP_ZH_REPL = [
    (
        "Radeon PRO W7900 / `gfx1100` | large-MPS 工作站 GPU 验证和后续 W7900-specific profiling/tuning",
        "Radeon PRO W7900 / `gfx1100` | large-MPS 工作站 GPU 验证、P10 profiling、P11 SpMV tuning 与 P12 rejected experiment 记录",
    ),
    (
        "| After | future W7900-specific tuning branch | 最终 W7900-specific optimized result |",
        "| After / accepted endpoint | P11 current W7900 tuning policy | 当前默认 `HIPSPARSE_SPMV_CSR_ALG1`，旧默认可用 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 回退 |",
    ),
    (
        "| 演示说明 PPT | 第一轮 profiling 结果完成后制作 |",
        "| 演示说明 PPT | 可基于 W7900 current status、P10 targeted profiling、P11 SpMV tuning、P12 rejected finding 和 cuPDLPx positioning 制作 |",
    ),
]

COMP_NEXT_EN = dedent("""
    ## Next planned work status

    The original W7900 starter profiling, hard3 short probes, before/current
    comparison, and W7900-specific tuning items have been closed by the P10/P11/P12
    evidence chain:

    1. P10 targeted rocprof profiling has been archived.
    2. hard3 probe2 has been archived; hard3 is not mixed into the primary
       non-hard23 baseline.
    3. before/current fast-core6 has been completed; if stronger timing evidence
       is needed, only add representative repeated validation later.
    4. P11 completed the SpMV algorithm switch, smoke validation, five-case sweep,
       and current default `HIPSPARSE_SPMV_CSR_ALG1` policy.
    5. P12 recorded a rejected SpMV buffer-algorithm consistency patch.

    Remaining W7900 work is optional evidence strengthening only: P14-A
    current-vs-before repeated validation and P14-B CSR ALG1-vs-ALG2 repeated
    validation, when a W7900 machine is available.
""")

COMP_NEXT_ZH = dedent("""
    ## 下一步计划状态

    原计划中的 W7900 starter profiling、hard3 short probes、before/current
    comparison 和 W7900-specific tuning 已由 P10/P11/P12 证据链闭环：

    1. P10 targeted rocprof profiling 已归档。
    2. hard3 probe2 已归档；hard3 不混入 primary non-hard23 baseline。
    3. before/current fast-core6 已完成；若要增强性能统计说服力，后续只补
       representative repeated validation。
    4. P11 已完成 SpMV algorithm switch、smoke validation、five-case sweep，并将
       当前默认设为 `HIPSPARSE_SPMV_CSR_ALG1`。
    5. P12 已记录一个被拒绝的 SpMV buffer-algorithm consistency patch。

    剩余 W7900 工作只是可选证据增强：等 W7900 机器可用后补 P14-A
    current-vs-before repeated validation 和 P14-B CSR ALG1-vs-ALG2 repeated
    validation。
""")

STATUS_PROFILE_EN = dedent("""
    ## ROCm profiling and tuning completion status

    The original profiling plan has been executed and superseded by the P10/P11/P12
    evidence chain. Starter profiling and W7900-specific tuning should no longer
    be described as pending blockers.

    Final references:

    - [W7900 ROCm profiling plan](W7900_ROCM_PROFILING_PLAN.md)
    - [P11 SpMV tuning summary](../validation/w7900_p11_spmv_tuning_summary_20260617.md)
    - [P12 rejected experiment note](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md)
""")

STATUS_NEXT_EN = dedent("""
    ## Next-action status

    The earlier W7900 starter profiling, hard3 probe2, before/current core6,
    compact profiling summary, and first W7900-specific tuning pass are complete
    for the current project stage:

    1. P10 targeted rocprof profiling has been archived.
    2. hard3 probe2 has been archived; hard3 is not mixed into the primary
       non-hard23 baseline.
    3. before/current fast-core6 has been completed; if stronger timing evidence
       is needed, only add representative repeated validation later.
    4. P11 SpMV tuning has been accepted. The current default SpMV algorithm is
       `HIPSPARSE_SPMV_CSR_ALG1`.
    5. The P12 rejected experiment note records the unaccepted buffer-algorithm
       consistency patch.

    The remaining items are optional evidence strengthening, not blockers:
    P14-A current-vs-before repeated validation and P14-B CSR ALG1-vs-ALG2
    repeated validation, when a W7900 machine becomes available.
""")

WORKFLOW_EN_SECTION = dedent("""
    ## 13. Current next-priority status

    The original priorities are mostly complete: the large-MPS benchmark matrix,
    890M tuning history, W7900 / `gfx1100` migration, profiling, and P11 tuning
    have all been archived.

    Current remaining recommendations:

    1. Keep English and Chinese documentation plus validation indexes in sync.
    2. Add P14-A current-vs-before repeated validation only when a W7900 machine
       is available.
    3. Add P14-B CSR ALG1-vs-ALG2 repeated validation only when a W7900 machine
       is available.
    4. Do not add deeper numerical-path optimization unless a complete validation
       protocol is designed first.
""")

WORKFLOW_ZH_SECTION = dedent("""
    ## 13. 当前下一步优先级状态

    原优先级已基本完成：large-MPS benchmark matrix、890M tuning history、W7900 /
    `gfx1100` migration、profiling 和 P11 tuning 均已归档。

    当前剩余建议：

    1. 保持中英文文档和 validation 索引同步。
    2. 只在 W7900 机器可用时补 P14-A current-vs-before repeated validation。
    3. 只在 W7900 机器可用时补 P14-B CSR ALG1-vs-ALG2 repeated validation。
    4. 不再新增深层数值路径优化，除非先重新设计完整验证协议。
""")

VALID_EN_TAIL = dedent("""
    ## Current limitations and completed validation scope

    - The ROCm/HIP backend remains experimental and is not a production-certified
      solver release.
    - The original `gfx1150` / 890M validation target is complete for the current
      scope.
    - W7900 / `gfx1100` validation is also complete for the current scope: smoke,
      Netlib, large-MPS baseline, P10 profiling, P11 SpMV tuning, and P12 rejected
      experiment note are documented.
    - `share2b` remains INCOMPLETE at the current Netlib iteration/time limit.
    - `greenbea` is convergence-sensitive and should remain documented separately.
    - No ROCm CI runner is currently available.
    - Some legacy CUDA-style names remain intentionally for C/HIP compatibility.

    ## Future validation work

    Completed or superseded items:

    - larger sparse LP validation: completed for the curated large-MPS benchmark
      scope;
    - validate `gfx1100`: completed for W7900 current project scope;
    - profiling/tuning validation: completed through P10/P11/P12.

    Optional future work:

    - add more Netlib LP cases;
    - add infeasible and unbounded LP cases;
    - add badly scaled cases;
    - record periodic validation snapshots;
    - add ROCm CI when a suitable runner is available;
    - add P14-A W7900 current-vs-before repeated validation when W7900 is
      available;
    - add P14-B W7900 CSR ALG1-vs-ALG2 repeated validation when W7900 is
      available.
""")

VALID_ZH_TAIL = dedent("""
    ## 当前限制与已完成验证范围

    - ROCm/HIP backend 仍是实验性，不是生产级认证 solver release。
    - 原始 `gfx1150` / 890M validation target 已完成当前范围。
    - W7900 / `gfx1100` validation 也已完成当前范围：smoke、Netlib、
      large-MPS baseline、P10 profiling、P11 SpMV tuning、P12 rejected
      experiment note 均已归档。
    - `share2b` 在当前 Netlib 迭代或时间限制下仍为 INCOMPLETE。
    - `greenbea` 是 convergence-sensitive case，应继续单独记录。
    - 当前还没有 ROCm CI runner。
    - 部分 legacy CUDA-style 名称因 C/HIP 兼容边界仍保留。

    ## 后续验证工作

    已完成或已被取代的项目：

    - larger sparse LP validation：已在 curated large-MPS benchmark 范围完成；
    - validate `gfx1100`：已在 W7900 当前项目范围完成；
    - profiling/tuning validation：已由 P10/P11/P12 完成。

    可选未来工作：

    - 增加更多 Netlib LP cases；
    - 增加 infeasible 和 unbounded LP cases；
    - 增加 badly scaled cases；
    - 定期记录 validation snapshots；
    - 有合适 runner 时添加 ROCm CI；
    - W7900 可用后补 P14-A current-vs-before repeated validation；
    - W7900 可用后补 P14-B CSR ALG1-vs-ALG2 repeated validation。
""")

HIST_EN_SECTION = dedent("""
    ## Completed-plan markers / 2026-06-17

    Several items from the earlier “recommended next steps” have now been
    completed or superseded by newer W7900 documents:

    - W7900 / `gfx1100` platform validation: completed through smoke, Netlib, and
      large-MPS baseline.
    - W7900 profiling: archived through P10 targeted rocprof.
    - W7900 platform-specific tuning: closed by P11 SpMV tuning.
    - Additional execution-layer candidate: P12 records a rejected experiment.
    - cuPDLP-C vs cuPDLPx comparison: short13 is documented separately with final
      positioning.

    Remaining optional enhancements:

    - P14-A: W7900 current-vs-before representative repeated validation.
    - P14-B: W7900 CSR ALG1-vs-ALG2 representative repeated validation.
""")

HIST_ZH_SECTION = dedent("""
    ## 后续计划完成标记 / 2026-06-17

    早期“推荐下一步”中的多项工作已经完成或被新的 W7900 文档取代：

    - W7900 / `gfx1100` 平台验证：已完成 smoke、Netlib 和 large-MPS baseline。
    - W7900 profiling：已由 P10 targeted rocprof 归档。
    - W7900 平台化调优：已由 P11 SpMV tuning 闭环。
    - 额外 execution-layer 候选：P12 已记录一个被拒绝实验。
    - cuPDLP-C 与 cuPDLPx 对比：short13 已单独成文档，并已补最终定位说明。

    仍可选增强：

    - P14-A：W7900 current-vs-before representative repeated validation。
    - P14-B：W7900 CSR ALG1-vs-ALG2 representative repeated validation。
""")

def main():
    # Competition README bilingual sync.
    for rel, reps in [(COMP_EN, COMP_EN_REPL), (COMP_ZH, COMP_ZH_REPL)]:
        for old, new in reps:
            replace_once(ROOT / rel, old, new)

    replace_section(ROOT / COMP_EN, "## Next planned work", "## Reproducibility", COMP_NEXT_EN)
    replace_section(ROOT / COMP_ZH, "## 下一步计划", "## 可复现性", COMP_NEXT_ZH)

    # W7900 current status English sync.
    replace_section(ROOT / STATUS_EN, "## ROCm profiling and tuning plan", "## Next actions", STATUS_PROFILE_EN)
    replace_section(ROOT / STATUS_EN, "## Next actions", "## Latest W7900 experiment status", STATUS_NEXT_EN)

    # For Chinese status, only append if equivalent section is missing; your local file may already have it.
    append_once(ROOT / STATUS_ZH, dedent("""
        ## P14 可选增强说明 / 2026-06-17

        当前 W7900 状态页不再把 profiling/tuning 写成 pending blocker。后续仅在
        W7900 机器可用时补两个可选 repeated validation：

        1. P14-A：current-vs-before representative repeated validation。
        2. P14-B：CSR ALG1-vs-ALG2 representative repeated validation。
    """))

    # ROCM workflow bilingual sync.
    replace_once(
        ROOT / WORKFLOW_EN,
        "The currently verified ROCm target is AMD Radeon 890M / `gfx1150`.",
        "The currently verified ROCm targets include AMD Radeon 890M / `gfx1150` and Radeon PRO W7900 / `gfx1100`. W7900 has completed P10 targeted profiling, P11 SpMV tuning, and the P12 rejected experiment note.",
    )
    replace_section(ROOT / WORKFLOW_EN, "## 13. Current next priorities", "", WORKFLOW_EN_SECTION)
    replace_section(ROOT / WORKFLOW_ZH, "## 13. 当前下一步优先级", "", WORKFLOW_ZH_SECTION)

    # VALIDATION bilingual sync: replace stale tail from Current limitations to EOF.
    replace_section(ROOT / VALID_EN, "## Current limitations", "", VALID_EN_TAIL)
    replace_section(ROOT / VALID_ZH, "## 当前限制", "", VALID_ZH_TAIL)

    # ROCm tuning history bilingual sync.
    append_once(ROOT / HIST_EN, HIST_EN_SECTION)
    append_once(ROOT / HIST_ZH, HIST_ZH_SECTION)

    print("[DONE] synchronized W7900 completed-plan status in English and Chinese")

if __name__ == "__main__":
    main()
