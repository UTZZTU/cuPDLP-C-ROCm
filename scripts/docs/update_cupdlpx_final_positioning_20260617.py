#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

SHORT13_EN = ROOT / "docs/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.md"
SHORT13_ZH = ROOT / "docs/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.zh-CN.md"
BASELINE_EN = ROOT / "docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.md"
BASELINE_ZH = ROOT / "docs/benchmarks/large_mps_cuda_rocm_baseline_20260610.zh-CN.md"
PROF_EN = ROOT / "docs/ROCM_PROFILING_NOTES.md"
PROF_ZH = ROOT / "docs/ROCM_PROFILING_NOTES.zh-CN.md"
CASE_ZH = ROOT / "docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md"
HIST_ZH = ROOT / "docs/ROCM_TUNING_HISTORY.zh-CN.md"

def append_once(path: Path, section: str):
    text = path.read_text(encoding="utf-8")
    heading = section.strip().splitlines()[0].strip()
    if heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return
    path.write_text(text.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] appended {path.relative_to(ROOT)}")

def replace_once(path: Path, old: str, new: str):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        print(f"[MISS] {path.relative_to(ROOT)} did not contain expected text")
        return
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"[OK] replaced text in {path.relative_to(ROOT)}")

def main():
    append_once(SHORT13_EN, dedent("""
        ## Final positioning after W7900 project closure

        After the W7900 ROCm/HIP migration and P11 SpMV tuning work, this
        short13 comparison should be interpreted as a CUDA-side algorithmic
        reference, not as a replacement for the cuPDLP-C ROCm migration baseline.

        Final interpretation:

        - cuPDLPx v0.2.9 solved all 13 selected short/medium cases on RTX 4090D.
        - cuPDLPx was faster than upstream cuPDLP-C on most short13 cases, with
          about 1.55x median solve-time speedup and 1.60x geometric-mean
          solve-time speedup.
        - The result supports cuPDLPx as a future algorithmic direction.
        - It does not invalidate the cuPDLP-C-ROCm work, because cuPDLPx changes
          the solver algorithm and implementation stack, while this repository
          focuses on CUDA-to-ROCm/HIP migration of the cuPDLP-C code path.
        - A fair cuPDLPx-ROCm comparison would require a separate porting effort
          and aligned hardware, tolerances, case set, and output parsing.
    """))

    append_once(SHORT13_ZH, dedent("""
        ## W7900 项目收尾后的最终定位

        在 W7900 ROCm/HIP 迁移和 P11 SpMV tuning 完成后，本 short13 对比应解释为
        CUDA 侧算法路线参考，而不是 cuPDLP-C ROCm 迁移 baseline 的替代品。

        最终解释：

        - cuPDLPx v0.2.9 在 RTX 4090D 上成功求解全部 13 个 short/medium case。
        - cuPDLPx 在 short13 多数 case 上快于 upstream cuPDLP-C，median solve-time
          speedup 约 1.55x，geomean solve-time speedup 约 1.60x。
        - 该结果支持 cuPDLPx 作为未来算法路线。
        - 这不否定 cuPDLP-C-ROCm 工作，因为 cuPDLPx 改变了 solver algorithm 和
          implementation stack，而本仓库聚焦 cuPDLP-C 代码路径的 CUDA 到 ROCm/HIP
          迁移。
        - 公平的 cuPDLPx-ROCm 对比需要单独 porting，并对齐硬件、tolerance、case set
          和输出解析。
    """))

    replace_once(
        BASELINE_EN,
        "5. cuPDLPx is being benchmarked separately on RTX 4090D and should be documented separately.",
        "5. cuPDLPx short13 has been benchmarked separately on RTX 4090D and documented separately. It remains a separate solver/algorithm comparison and should not be mixed into the cuPDLP-C ROCm baseline table."
    )

    replace_once(
        BASELINE_ZH,
        "5. cuPDLPx 正在 4090D 上进行 short-case 对比，属于另一条 solver/算法路线，建议单独成文档，不直接合并进 cuPDLP-C baseline 表。",
        "5. cuPDLPx short13 已经在 4090D 上单独完成并成文档，属于另一条 solver/算法路线，不直接合并进 cuPDLP-C ROCm baseline 表。"
    )

    append_once(PROF_EN, dedent("""
        ## cuPDLPx final positioning after W7900 closure

        The repository already contains a separate RTX 4090D short13 comparison
        between cuPDLP-C and cuPDLPx. That comparison showed cuPDLPx v0.2.9 was
        stable on the selected short/medium cases and faster on most of them.
        It should be used as an algorithmic reference only.

        It should not be merged into W7900 ROCm profiling conclusions because it
        differs in solver algorithm, implementation stack, hardware backend, and
        output conventions. A future cuPDLPx-ROCm study would need a separate
        benchmark protocol.
    """))

    append_once(PROF_ZH, dedent("""
        ## W7900 收尾后的 cuPDLPx 最终定位

        本仓库已经包含 RTX 4090D short13 的 cuPDLP-C 与 cuPDLPx 单独对比。该对比
        显示 cuPDLPx v0.2.9 在所选 short/medium cases 上稳定，并在多数 case 上更快。
        该结果应作为算法路线参考。

        它不应混入 W7900 ROCm profiling 结论，因为两者在 solver algorithm、
        implementation stack、hardware backend 和输出约定上都不同。未来若做
        cuPDLPx-ROCm 研究，需要单独 benchmark protocol。
    """))

    append_once(CASE_ZH, dedent("""
        ## cuPDLPx 对比收尾说明 / 2026-06-17

        本项目已经包含 RTX 4090D short13 上的 cuPDLP-C vs cuPDLPx 对比。该结果表明
        cuPDLPx 作为更新算法路线值得后续关注，但它不替代 cuPDLP-C-ROCm 主线。本文的
        ROCm migration case study 仍以 cuPDLP-C CUDA→ROCm/HIP 迁移、W7900 验证和
        P11 SpMV tuning 为主线。
    """))

    append_once(HIST_ZH, dedent("""
        ## cuPDLPx 对比收尾说明 / 2026-06-17

        已有 RTX 4090D short13 对比显示 cuPDLPx 在多数 short/medium case 上快于
        upstream cuPDLP-C。该结果应作为未来算法路线参考，而不是 W7900 ROCm/HIP
        tuning 历史的一部分。W7900 当前终点仍是 cuPDLP-C-ROCm 分支中的
        `HIPSPARSE_SPMV_CSR_ALG1` 默认策略与可回退 P11 tuning 闭环。
    """))

    print("[DONE] updated cuPDLPx final positioning based on existing short13 artifacts")

if __name__ == "__main__":
    main()
