#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent
import re

ROOT = Path(__file__).resolve().parents[2]

FIRST = ROOT / "docs" / "W7900_FIRST_PORT.zh-CN.md"
PORTING = ROOT / "docs" / "ROCM_PORTING_GUIDE.zh-CN.md"

FIRST_NEW = dedent("""
    ## 9. 已知限制与当前完成状态

    本文是 W7900 / `gfx1100` first-port smoke milestone 的历史记录。原始
    first-port 限制已经由后续 W7900 文档取代：

    * extended Netlib validation：已完成。
    * large MPS benchmark：non-hard23 baseline 已完成，hard3 单独记录。
    * W7900 profiling：P10 targeted rocprof 已归档。
    * W7900 单卡调优：P11 SpMV tuning 已完成，当前默认
      `HIPSPARSE_SPMV_CSR_ALG1`。
    * 8 GPU 并发吞吐实验：fast8 batch throughput 已归档。
    * 跨设备 benchmark matrix：已有 curated summaries。

    当前仍不应描述为生产级 solver release，但已经超过 first-port smoke 阶段。
    权威状态见 [W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md)。

    ## 10. 后续计划状态

    原下一步计划已基本完成。当前仅保留可选增强：

    1. W7900 P14-A：current-vs-before representative repeated validation。
    2. W7900 P14-B：CSR ALG1-vs-ALG2 representative repeated validation。

    其他深层数值路径优化不纳入当前项目终点。
""").strip()

PORTING_NEW = dedent("""
    ## 14. 当前限制与完成状态

    - ROCm/HIP backend 仍是实验性，不应描述为生产级 solver release。
    - `gfx1150` / 890M 与 `gfx1100` / W7900 都已有验证记录。
    - W7900 validation pass 已完成当前阶段闭环：smoke、Netlib、
      large-MPS baseline、P10 profiling、P11 SpMV tuning、P12 rejected
      experiment note。
    - 部分内部 CUDA-style 名称因 C/HIP 兼容边界仍保留。
    - Broad large MPS validation 已有 curated summaries；raw MPS 和 raw logs
      仍不提交到 Git。
    - 尚无 ROCm CI。

    ## 15. 推荐下一步状态

    原推荐下一步已基本完成。当前只保留两个可选增强：

    1. W7900 P14-A：current-vs-before representative repeated validation。
    2. W7900 P14-B：CSR ALG1-vs-ALG2 representative repeated validation。

    除此之外，不建议继续新增深层数值路径优化，除非重新设计完整验证协议。
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

def main():
    replace_tail(FIRST, "## 9. 已知限制", FIRST_NEW)
    replace_tail(PORTING, "## 14. 当前限制", PORTING_NEW)
    print("[DONE] fixed W7900 first-port and ROCm porting guide stale tail sections")

if __name__ == "__main__":
    main()
