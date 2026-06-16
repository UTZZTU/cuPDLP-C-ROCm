#!/usr/bin/env python3
from pathlib import Path
import re
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

FINAL_EN = dedent("""
    ## Final W7900 project status / 2026-06-17

    The W7900 / `gfx1100` project stage is now complete for the current
    repository scope. The branch has progressed beyond first-port and baseline
    documentation:

    - W7900 ROCm build, smoke validation, Netlib validation, large-MPS baseline,
      targeted profiling, and P11 SpMV tuning have been completed.
    - P10 targeted profiling identified rocSPARSE/hipSPARSE CSR SpMV as the main
      GPU kernel hotspot on the selected W7900 cases.
    - P11 added an opt-in HIP SpMV algorithm switch and validated three modes:
      `csr_alg2`, `default`, and `csr_alg1`.
    - The current W7900 default SpMV algorithm is
      `HIPSPARSE_SPMV_CSR_ALG1`.
    - The previous default remains recoverable with
      `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
    - This is a W7900-specific current-default tuning choice, not a final
      cross-platform peak-performance claim.

    For the authoritative W7900 endpoint, see:

    - `docs/W7900_CURRENT_STATUS.md`
    - `validation/w7900_p11_spmv_tuning_summary_20260617.md`
""").strip()

FINAL_ZH = dedent("""
    ## W7900 项目最终状态 / 2026-06-17

    当前仓库范围内，W7900 / `gfx1100` 阶段已经完成。该分支已经不再停留在
    first-port 或 baseline 文档阶段：

    - W7900 ROCm build、smoke validation、Netlib validation、large-MPS baseline、
      targeted profiling 和 P11 SpMV tuning 均已完成。
    - P10 targeted profiling 确认 rocSPARSE/hipSPARSE CSR SpMV 是所选 W7900
      case 上的主要 GPU kernel 热点。
    - P11 增加 opt-in HIP SpMV algorithm switch，并验证了 `csr_alg2`、
      `default`、`csr_alg1` 三种模式。
    - 当前 W7900 默认 SpMV algorithm 已设为
      `HIPSPARSE_SPMV_CSR_ALG1`。
    - 旧默认仍可通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 显式恢复。
    - 这是 W7900-specific 当前默认调优策略，不是最终跨平台峰值性能结论。

    W7900 当前权威入口见：

    - `docs/W7900_CURRENT_STATUS.zh-CN.md`
    - `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`
""").strip()

UPDATES = {
    "README.md": FINAL_ZH,
    "README.zh-CN.md": FINAL_ZH,
    "README.en.md": FINAL_EN,
    "docs/LARGE_MPS_BENCHMARK_PLAN.md": dedent("""
        ## Completion update / 2026-06-17

        The original benchmark plan has now been executed beyond the planning
        stage. CUDA baselines, Radeon 890M ROCm baselines, W7900 / `gfx1100`
        baselines, targeted profiling, and P11 SpMV tuning summaries have been
        committed as curated validation artifacts.

        The W7900 target should no longer be described as a future platform in
        this branch. It is the completed second ROCm target for the current
        project stage. Raw `.mps` files and raw solver logs remain outside Git;
        curated summaries and links live under `validation/` and
        `docs/W7900_CURRENT_STATUS.md`.
    """).strip(),
    "docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md": dedent("""
        ## 完成状态更新 / 2026-06-17

        原始 benchmark plan 已经不再只是计划阶段。CUDA baselines、Radeon 890M
        ROCm baselines、W7900 / `gfx1100` baselines、targeted profiling 和 P11
        SpMV tuning summaries 都已经作为整理后的 validation artifacts 提交。

        在当前分支中，W7900 不应再写成未来平台。它已经是当前项目阶段完成的第二个
        ROCm 目标。原始 `.mps` 文件和 raw solver logs 仍不提交到 Git；整理后的
        summaries 和入口位于 `validation/` 与 `docs/W7900_CURRENT_STATUS.zh-CN.md`。
    """).strip(),
    "docs/CROSS_DEVICE_BENCHMARKS.md": dedent("""
        ## W7900 completion update / 2026-06-17

        The cross-device story has been extended beyond the original Netlib and
        890M-only benchmark stage. The current branch now includes W7900 /
        `gfx1100` validation, large-MPS summaries, targeted profiling, and P11
        SpMV tuning documentation.

        The previous “next stage” items are now partially or fully completed for
        the current project scope. The current endpoint is:

        - W7900 first-port and baseline documentation completed.
        - P10 targeted rocprof evidence collected.
        - P11 opt-in SpMV algorithm switch implemented.
        - W7900 default SpMV algorithm set to `HIPSPARSE_SPMV_CSR_ALG1`.
        - Rollback path preserved with `CUPDLP_HIP_SPMV_ALG=csr_alg2`.

        See `docs/W7900_CURRENT_STATUS.md` and
        `validation/w7900_p11_spmv_tuning_summary_20260617.md`.
    """).strip(),
    "docs/CROSS_DEVICE_BENCHMARKS.zh-CN.md": dedent("""
        ## W7900 完成状态更新 / 2026-06-17

        cross-device 叙事已经从最初的 Netlib 和 890M-only benchmark 阶段扩展到
        W7900 / `gfx1100`。当前分支已经包含 W7900 validation、large-MPS summaries、
        targeted profiling 和 P11 SpMV tuning 文档。

        之前写作“下一阶段”的事项，在当前项目范围内已经部分或全部完成。当前终点是：

        - W7900 first-port 和 baseline 文档已完成。
        - P10 targeted rocprof 证据已收集。
        - P11 opt-in SpMV algorithm switch 已实现。
        - W7900 默认 SpMV algorithm 已设为 `HIPSPARSE_SPMV_CSR_ALG1`。
        - 旧默认可通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 回退。

        详见 `docs/W7900_CURRENT_STATUS.zh-CN.md` 和
        `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`。
    """).strip(),
    "docs/TUNING_GUIDE_ROCM.md": dedent("""
        ## W7900 tuning endpoint / 2026-06-17

        This guide was originally written around the Radeon 890M / `gfx1150`
        tuning sequence. The W7900 / `gfx1100` follow-up is now complete for the
        current project scope.

        Current W7900 policy:

        - default HIP SpMV algorithm: `HIPSPARSE_SPMV_CSR_ALG1`
        - rollback to old default: `CUPDLP_HIP_SPMV_ALG=csr_alg2`
        - experimental hipSPARSE default: `CUPDLP_HIP_SPMV_ALG=default`

        No additional long profiling run is required for the current project
        endpoint. Further tuning should be treated as future work and should
        focus on carefully validated scalar-copy or reduction-path changes.
    """).strip(),
    "docs/TUNING_GUIDE_ROCM.zh-CN.md": dedent("""
        ## W7900 tuning 终点 / 2026-06-17

        本指南最初围绕 Radeon 890M / `gfx1150` 调优序列编写。当前项目范围内，
        W7900 / `gfx1100` follow-up 已经完成。

        当前 W7900 策略：

        - 默认 HIP SpMV algorithm：`HIPSPARSE_SPMV_CSR_ALG1`
        - 回退旧默认：`CUPDLP_HIP_SPMV_ALG=csr_alg2`
        - 实验 hipSPARSE default：`CUPDLP_HIP_SPMV_ALG=default`

        当前项目终点不需要继续追加长 profiling。后续若继续调优，应作为未来工作，
        并重点关注需要严格验证的 scalar-copy 或 reduction-path 改动。
    """).strip(),
    "docs/ROCM_PROFILING_NOTES.md": dedent("""
        ## W7900 profiling completion update / 2026-06-17

        The W7900 migration mentioned earlier in this document has now been
        completed for the current project stage. Instead of remaining a future
        profiling target, W7900 now has committed P10 targeted rocprof summaries
        and a P11 SpMV tuning endpoint.

        Current W7900 profiling/tuning links:

        - `validation/w7900_p10_current_targeted_rocprof_20260617_summary.md`
        - `validation/w7900_p11_spmv_alg_sweep_20260617_summary.md`
        - `validation/w7900_p11_spmv_tuning_summary_20260617.md`

        The current conclusion is that SpMV is the first completed
        W7900-specific tuning path. Copy-reduction and reduction-kernel work
        remain possible future directions but are not part of the current
        project endpoint.
    """).strip(),
    "docs/ROCM_PROFILING_NOTES.zh-CN.md": dedent("""
        ## W7900 profiling 完成状态更新 / 2026-06-17

        本文前面提到的 W7900 migration，在当前项目阶段已经完成。W7900 不再是未来
        profiling 目标，而是已经拥有 P10 targeted rocprof summaries 和 P11 SpMV
        tuning endpoint。

        当前 W7900 profiling/tuning 入口：

        - `validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md`
        - `validation/w7900_p11_spmv_alg_sweep_20260617_summary.zh-CN.md`
        - `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`

        当前结论是：SpMV 是第一条已经完成的 W7900-specific tuning path。copy
        reduction 和 reduction-kernel 仍可作为未来方向，但不属于当前项目终点。
    """).strip(),
    "docs/ROCM_TUNING_HISTORY.md": dedent("""
        ## W7900 follow-up tuning / 2026-06-17

        The original tuning history in this document records the Radeon 890M /
        `gfx1150` tuning sequence. The W7900 / `gfx1100` follow-up has now been
        completed as a separate P10/P11 evidence chain.

        W7900 endpoint:

        - P10 targeted profiling identified SpMV as the primary kernel hotspot.
        - P11 added an opt-in HIP SpMV algorithm switch.
        - P11 five-case sweep validated `csr_alg2`, `default`, and `csr_alg1`.
        - Current W7900 default: `HIPSPARSE_SPMV_CSR_ALG1`.
        - Rollback: `CUPDLP_HIP_SPMV_ALG=csr_alg2`.

        See `validation/w7900_p11_spmv_tuning_summary_20260617.md`.
    """).strip(),
    "docs/ROCM_TUNING_HISTORY.zh-CN.md": dedent("""
        ## W7900 follow-up tuning / 2026-06-17

        本文原始 tuning history 记录的是 Radeon 890M / `gfx1150` 调优序列。
        W7900 / `gfx1100` follow-up 已经作为独立 P10/P11 证据链完成。

        W7900 终点：

        - P10 targeted profiling 确认 SpMV 是主要 kernel 热点。
        - P11 增加 opt-in HIP SpMV algorithm switch。
        - P11 五 case sweep 验证 `csr_alg2`、`default`、`csr_alg1` 三种模式。
        - 当前 W7900 默认：`HIPSPARSE_SPMV_CSR_ALG1`。
        - 回退旧默认：`CUPDLP_HIP_SPMV_ALG=csr_alg2`。

        详见 `validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`。
    """).strip(),
    "docs/VALIDATION.md": dedent("""
        ## W7900 validation endpoint / 2026-06-17

        In addition to the original Radeon 890M / `gfx1150` validation target,
        the current branch now includes a completed W7900 / `gfx1100` validation
        and tuning endpoint.

        W7900 validation artifacts include:

        - smoke/build validation and platform notes;
        - Netlib validation and large-MPS baseline summaries;
        - P10 targeted rocprof summaries;
        - P11 SpMV algorithm switch smoke and five-case sweep;
        - final P11 SpMV tuning summary.

        The current W7900 default SpMV algorithm is
        `HIPSPARSE_SPMV_CSR_ALG1`, with rollback via
        `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
    """).strip(),
    "docs/VALIDATION.zh-CN.md": dedent("""
        ## W7900 validation 终点 / 2026-06-17

        除了原始 Radeon 890M / `gfx1150` validation target 之外，当前分支已经包含
        完整的 W7900 / `gfx1100` validation 和 tuning endpoint。

        W7900 validation artifacts 包括：

        - smoke/build validation 和 platform notes；
        - Netlib validation 和 large-MPS baseline summaries；
        - P10 targeted rocprof summaries；
        - P11 SpMV algorithm switch smoke 和五 case sweep；
        - final P11 SpMV tuning summary。

        当前 W7900 默认 SpMV algorithm 为 `HIPSPARSE_SPMV_CSR_ALG1`，
        可通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 回退旧默认。
    """).strip(),
}

def append_once(path: Path, section: str):
    if not path.exists():
        print(f"[MISS] {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    heading = section.splitlines()[0].strip()
    if heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return
    path.write_text(text.rstrip() + "\n\n" + section + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] updated {path.relative_to(ROOT)}")

def replace_readme_status(path: Path):
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")

    replacements = {
        r"> 状态：实验性但可构建。当前 ROCm/HIP 后端已经通过 smoke validation、Netlib 验证、跨设备 benchmark，以及 Radeon 890M / `gfx1150` 上的大规模 MPS baseline 测试。W7900 / `gfx1100` 分支已经完成 smoke validation、Netlib 27-case validation，以及 23-case non-hard large-MPS baseline；剩余 large-MPS hard3 case 会在完整调优前单独跟踪。它还不是生产级、完全调优、广泛认证的 ROCm solver release。":
        r"> 状态：实验性但可构建。当前 ROCm/HIP 后端已经通过 smoke validation、Netlib 验证、跨设备 benchmark、large-MPS baseline，以及 Radeon 890M / `gfx1150` 与 Radeon PRO W7900 / `gfx1100` 上的验证与调优记录。W7900 阶段已经完成 P10 targeted profiling 和 P11 SpMV tuning；当前默认 SpMV algorithm 为 `HIPSPARSE_SPMV_CSR_ALG1`，旧默认可用 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 回退。它仍不是生产级、广泛认证的 ROCm solver release，但当前项目阶段已经完成。"
    }

    changed = False
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            changed = True

    if changed:
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"[OK] replaced stale status in {path.relative_to(ROOT)}")

def main():
    for rel, section in UPDATES.items():
        append_once(ROOT / rel, section)

    replace_readme_status(ROOT / "README.md")
    replace_readme_status(ROOT / "README.zh-CN.md")

    print("[DONE] finalized W7900 project documentation status blocks")

if __name__ == "__main__":
    main()
