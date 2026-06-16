#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "validation"

NOTE = VALIDATION / "w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md"
NOTE_ZH = VALIDATION / "w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md"

README_SECTION = dedent("""
    ## W7900 P12 negative finding: SpMV buffer algorithm consistency / 2026-06-17

    This note records a rejected low-risk execution-layer tuning attempt after
    P11: aligning `hipsparseSpMV_bufferSize()` with the selected runtime SpMV
    algorithm.

    - Summary: [w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md](w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md)
    - Chinese summary: [w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md](w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md)

    Key interpretation: although the patch was reasonable as an implementation
    consistency experiment, it changed the `set-cover-model` iteration count
    from the previously stable `7480` to `7600`. The patch was therefore
    rejected and not committed.
""").strip()

README_ZH_SECTION = dedent("""
    ## W7900 P12 negative finding：SpMV buffer algorithm consistency / 2026-06-17

    本条记录 P11 之后一次被拒绝的低风险执行层调优尝试：让
    `hipsparseSpMV_bufferSize()` 使用与实际 runtime SpMV 一致的 algorithm。

    - 汇总：[w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md](w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md)
    - 英文汇总：[w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md](w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md)

    关键结论：该 patch 作为实现一致性实验是合理的，但它使
    `set-cover-model` 的迭代数从此前稳定的 `7480` 变为 `7600`。因此该 patch
    已被拒绝，未合入源码。
""").strip()

STATUS_SECTION = dedent("""
    ## P12 negative finding: rejected SpMV buffer algorithm consistency patch / 2026-06-17

    After P11, one additional low-risk execution-layer candidate was tested:
    making `hipsparseSpMV_bufferSize()` use the same algorithm selected by
    `cupdlp_hip_spmv_alg()`.

    The experiment was rejected because `set-cover-model` still solved
    successfully but changed iteration count from `7480` to `7600`. This
    indicates that even SpMV buffer/algorithm consistency changes can affect the
    solver trajectory. The source patch was reverted and not committed.

    Links:

    - [P12 negative finding summary](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md)
    - [P12 Chinese negative finding summary](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md)
""").strip()

STATUS_ZH_SECTION = dedent("""
    ## P12 negative finding：拒绝 SpMV buffer algorithm consistency patch / 2026-06-17

    P11 之后额外测试了一个低风险执行层候选：让
    `hipsparseSpMV_bufferSize()` 使用与 `cupdlp_hip_spmv_alg()` 选择结果一致的
    algorithm。

    该实验被拒绝，因为 `set-cover-model` 虽然仍能成功求解，但迭代数从 `7480`
    变为 `7600`。这说明即使是 SpMV buffer/algorithm 一致性改动，也可能影响
    solver 轨迹。源码 patch 已撤回，未提交。

    链接：

    - [P12 negative finding 中文汇总](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md)
    - [P12 英文 negative finding summary](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md)
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
    NOTE.write_text(dedent("""
        # W7900 P12 negative finding: SpMV buffer algorithm consistency

        This note records a rejected post-P11 low-risk execution-layer tuning
        experiment.

        ## Context

        P11 changed the current W7900 default HIP SpMV algorithm to
        `HIPSPARSE_SPMV_CSR_ALG1`, while preserving rollback with
        `CUPDLP_HIP_SPMV_ALG=csr_alg2`.

        After that, source audit showed one remaining consistency candidate:
        `cuda_alloc_MVbuffer()` still queried `hipsparseSpMV_bufferSize()` with a
        local algorithm variable set to `HIPSPARSE_SPMV_CSR_ALG2`, while actual
        runtime `hipsparseSpMV()` calls used `cupdlp_hip_spmv_alg()`.

        ## Experiment

        The rejected patch attempted two changes:

        1. cache `CUPDLP_HIP_SPMV_ALG` parsing in `cupdlp_hip_spmv_alg()`;
        2. make `cuda_alloc_MVbuffer()` use `cupdlp_hip_spmv_alg()` for
           `hipsparseSpMV_bufferSize()`.

        ## Observed result

        Test case: `set-cover-model`

        Observed after the patch:

        - exit code: `0`
        - solver status: `Optimal current solution`
        - iteration count: `7600`
        - solve time: `1.148008e+01`
        - total solver time: `1.278179e+01`
        - primal objective: `+7.58183814e+09`
        - dual objective: `+7.58170468e+09`
        - relative primal infeasibility: `9.84e-05`
        - relative dual infeasibility: `0.00e+00`
        - relative duality gap: `8.80e-06`

        Previous P11 smoke and sweep runs had `set-cover-model` stable at
        `7480` iterations under the accepted SpMV algorithm-switch policy.

        ## Decision

        The patch was rejected and reverted.

        Although the implementation idea was reasonable, it changed the solver
        trajectory. This violates the low-risk tuning rule used in this project:
        execution-layer changes should preserve solver status, iteration count,
        primal infeasibility, dual infeasibility, and duality gap unless the
        change is explicitly treated as a deeper numerical experiment.

        ## Interpretation

        This is useful evidence. It shows that even apparently local
        SpMV-buffer/algorithm consistency changes can affect the observed PDLP
        iteration trajectory on W7900. Therefore, further work in this direction
        should be treated as future deeper validation work rather than as a final
        quick tuning patch.

        ## Final status

        Not committed:

        - `cupdlp/hip/cupdlp_hip_linalg.cpp` patch was reverted.
        - temporary patch script was removed.

        Accepted endpoint remains:

        - current W7900 default SpMV algorithm: `HIPSPARSE_SPMV_CSR_ALG1`
        - rollback: `CUPDLP_HIP_SPMV_ALG=csr_alg2`
    """).strip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] wrote {NOTE.relative_to(ROOT)}")

    NOTE_ZH.write_text(dedent("""
        # W7900 P12 negative finding：SpMV buffer algorithm consistency

        本文记录 P11 之后一次被拒绝的低风险执行层调优实验。

        ## 背景

        P11 已将当前 W7900 默认 HIP SpMV algorithm 切换为
        `HIPSPARSE_SPMV_CSR_ALG1`，并保留
        `CUPDLP_HIP_SPMV_ALG=csr_alg2` 作为旧默认回退路径。

        随后的源码审计发现一个一致性候选点：
        `cuda_alloc_MVbuffer()` 中的 `hipsparseSpMV_bufferSize()` 仍使用本地
        algorithm 变量 `HIPSPARSE_SPMV_CSR_ALG2`，而实际 runtime
        `hipsparseSpMV()` 调用已经使用 `cupdlp_hip_spmv_alg()`。

        ## 实验内容

        被拒绝的 patch 尝试做两件事：

        1. 在 `cupdlp_hip_spmv_alg()` 中缓存 `CUPDLP_HIP_SPMV_ALG` 解析结果；
        2. 让 `cuda_alloc_MVbuffer()` 中的 `hipsparseSpMV_bufferSize()` 使用
           `cupdlp_hip_spmv_alg()`。

        ## 观察结果

        测试 case：`set-cover-model`

        patch 后观察结果：

        - exit code：`0`
        - solver status：`Optimal current solution`
        - 迭代数：`7600`
        - solve time：`1.148008e+01`
        - total solver time：`1.278179e+01`
        - primal objective：`+7.58183814e+09`
        - dual objective：`+7.58170468e+09`
        - relative primal infeasibility：`9.84e-05`
        - relative dual infeasibility：`0.00e+00`
        - relative duality gap：`8.80e-06`

        此前 P11 smoke 和 sweep 中，`set-cover-model` 在已接受的 SpMV
        algorithm-switch 策略下稳定为 `7480` iterations。

        ## 决策

        该 patch 被拒绝并撤回。

        虽然这个实现一致性思路是合理的，但它改变了 solver 轨迹。它违反了本项目
        对低风险调优的判断标准：执行层改动应保持 solver status、迭代数、
        primal infeasibility、dual infeasibility 和 duality gap 不变，除非明确把它
        作为更深层数值实验处理。

        ## 解释

        这个结果本身很有价值。它说明即使是看起来局部的 SpMV buffer/algorithm
        一致性改动，也可能影响 W7900 上观察到的 PDLP 迭代轨迹。因此该方向如果后续
        继续推进，应作为未来更深层验证工作，而不是当前阶段的快速调优 patch。

        ## 最终状态

        未提交：

        - `cupdlp/hip/cupdlp_hip_linalg.cpp` patch 已撤回。
        - 临时 patch 脚本已删除。

        已接受终点仍为：

        - 当前 W7900 默认 SpMV algorithm：`HIPSPARSE_SPMV_CSR_ALG1`
        - 回退旧默认：`CUPDLP_HIP_SPMV_ALG=csr_alg2`
    """).strip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] wrote {NOTE_ZH.relative_to(ROOT)}")

    append_once(ROOT / "validation" / "README.md", README_SECTION)
    append_once(ROOT / "validation" / "README.zh-CN.md", README_ZH_SECTION)
    append_once(ROOT / "docs" / "W7900_CURRENT_STATUS.md", STATUS_SECTION)
    append_once(ROOT / "docs" / "W7900_CURRENT_STATUS.zh-CN.md", STATUS_ZH_SECTION)

if __name__ == "__main__":
    main()
