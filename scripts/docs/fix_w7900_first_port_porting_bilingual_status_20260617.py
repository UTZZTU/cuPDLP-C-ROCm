#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent
import re

ROOT = Path(__file__).resolve().parents[2]

FIRST_EN = ROOT / "docs" / "W7900_FIRST_PORT.md"
FIRST_ZH = ROOT / "docs" / "W7900_FIRST_PORT.zh-CN.md"
PORT_EN = ROOT / "docs" / "ROCM_PORTING_GUIDE.md"
PORT_ZH = ROOT / "docs" / "ROCM_PORTING_GUIDE.zh-CN.md"

FIRST_EN_NEW = dedent("""
    ## 9. Known limitations and current completion status

    This document is kept as the historical W7900 / `gfx1100` first-port smoke
    milestone. The original first-port limitations have been superseded by later
    W7900 validation and tuning documents:

    * extended Netlib validation: completed.
    * large MPS benchmark: non-hard23 baseline completed; hard3 tracked separately.
    * W7900 profiling: P10 targeted rocprof archived.
    * W7900 single-GPU tuning: P11 SpMV tuning completed, with current default
      `HIPSPARSE_SPMV_CSR_ALG1`.
    * 8-GPU concurrent throughput experiment: fast8 batch throughput archived.
    * cross-device benchmark matrix: curated summaries are available.

    The project still should not be described as a production-certified ROCm
    solver release, but it has moved beyond the first-port smoke stage. The
    authoritative status is [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md).

    ## 10. Next-step status

    The original next-step list is now mostly completed. The only remaining
    optional enhancements are:

    1. W7900 P14-A: current-vs-before representative repeated validation.
    2. W7900 P14-B: CSR ALG1-vs-ALG2 representative repeated validation.

    Deeper numerical-path optimization is not part of the current project endpoint.
""").strip()

FIRST_ZH_NEW = dedent("""
    ## 9. 已知限制与当前完成状态

    本文保留为 W7900 / `gfx1100` first-port smoke milestone 的历史记录。原始
    first-port 限制已经由后续 W7900 validation 和 tuning 文档取代：

    * extended Netlib validation：已完成。
    * large MPS benchmark：non-hard23 baseline 已完成，hard3 单独记录。
    * W7900 profiling：P10 targeted rocprof 已归档。
    * W7900 单卡调优：P11 SpMV tuning 已完成，当前默认
      `HIPSPARSE_SPMV_CSR_ALG1`。
    * 8 GPU 并发吞吐实验：fast8 batch throughput 已归档。
    * 跨设备 benchmark matrix：已有 curated summaries。

    当前仍不应描述为生产级 ROCm solver release，但已经超过 first-port smoke
    阶段。权威状态见 [W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md)。

    ## 10. 后续计划状态

    原下一步计划已基本完成。当前仅保留可选增强：

    1. W7900 P14-A：current-vs-before representative repeated validation。
    2. W7900 P14-B：CSR ALG1-vs-ALG2 representative repeated validation。

    其他深层数值路径优化不纳入当前项目终点。
""").strip()

PORT_EN_NEW = dedent("""
    ## 14. Current limitations and completion status

    - The ROCm/HIP backend is still experimental and should not be described as
      a production-certified solver release.
    - Both `gfx1150` / 890M and `gfx1100` / W7900 now have validation records.
    - The W7900 validation pass has been completed for the current project stage:
      smoke validation, Netlib validation, large-MPS baseline, P10 profiling,
      P11 SpMV tuning, and the P12 rejected experiment note are all documented.
    - Some internal CUDA-style names remain at the C/HIP compatibility boundary.
    - Broad large-MPS validation has curated summaries; raw MPS files and raw
      logs remain outside Git.
    - ROCm CI is not yet available.

    ## 15. Recommended next-step status

    The original recommended next steps are mostly completed. The only remaining
    optional enhancements are:

    1. W7900 P14-A: current-vs-before representative repeated validation.
    2. W7900 P14-B: CSR ALG1-vs-ALG2 representative repeated validation.

    Beyond these, do not add deeper numerical-path optimization unless a full
    validation protocol is designed first.
""").strip()

PORT_ZH_NEW = dedent("""
    ## 14. 当前限制与完成状态

    - ROCm/HIP backend 仍是实验性，不应描述为生产级 solver release。
    - `gfx1150` / 890M 与 `gfx1100` / W7900 都已有验证记录。
    - W7900 validation pass 已完成当前阶段闭环：smoke validation、Netlib
      validation、large-MPS baseline、P10 profiling、P11 SpMV tuning 和 P12
      rejected experiment note 均已归档。
    - 部分内部 CUDA-style 名称因 C/HIP 兼容边界仍保留。
    - Broad large-MPS validation 已有 curated summaries；raw MPS 和 raw logs
      仍不提交到 Git。
    - 尚无 ROCm CI。

    ## 15. 推荐下一步状态

    原推荐下一步已基本完成。当前只保留两个可选增强：

    1. W7900 P14-A：current-vs-before representative repeated validation。
    2. W7900 P14-B：CSR ALG1-vs-ALG2 representative repeated validation。

    除此之外，不建议继续新增深层数值路径优化，除非先重新设计完整验证协议。
""").strip()

def replace_tail(path: Path, marker: str, replacement: str):
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        raise RuntimeError(f"marker not found in {path}: {marker}")

    new_text = re.sub(
        re.escape(marker) + r".*\Z",
        replacement + "\n",
        text,
        count=1,
        flags=re.S,
    )
    path.write_text(new_text.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] replaced tail from {marker!r} in {path.relative_to(ROOT)}")

def replace_optional(path: Path, old: str, new: str):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        print(f"[SKIP] exact phrase not found in {path.relative_to(ROOT)}: {old[:80]}")
        return
    text = text.replace(old, new, 1)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] replaced phrase in {path.relative_to(ROOT)}")

def main():
    replace_tail(FIRST_EN, "## 9. Known Limitations", FIRST_EN_NEW)
    replace_tail(FIRST_ZH, "## 9. 已知限制", FIRST_ZH_NEW)

    replace_tail(PORT_EN, "## 14. Current limitations", PORT_EN_NEW)
    replace_tail(PORT_ZH, "## 14. 当前限制", PORT_ZH_NEW)

    replace_optional(
        PORT_EN,
        "Current validated ROCm target:",
        "Initial validated ROCm target:"
    )
    replace_optional(
        PORT_ZH,
        "当前已验证 ROCm 目标：",
        "最初验证的 ROCm 目标："
    )

    print("[DONE] synchronized W7900 first-port and ROCm porting guide status in English and Chinese")

if __name__ == "__main__":
    main()
