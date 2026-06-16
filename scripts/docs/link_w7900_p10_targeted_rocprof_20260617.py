#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

SECTIONS = {
    "validation/README.md": dedent("""
        ## W7900 P10 targeted rocprof / 2026-06-17

        P10 profiles the current W7900/gfx1100 branch on five representative
        cases selected from the P9 derived metrics.

        - Summary: [w7900_p10_current_targeted_rocprof_20260617_summary.md](w7900_p10_current_targeted_rocprof_20260617_summary.md)
        - Chinese summary: [w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md](w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md)
        - Runtime CSV: [w7900_p10_current_targeted_rocprof_20260617_runtime.csv](w7900_p10_current_targeted_rocprof_20260617_runtime.csv)
        - Kernel top CSV: [w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv](w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv)
        - HIP API top CSV: [w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv](w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv)
        - Memory copy top CSV: [w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv](w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv)

        Key interpretation: all five targeted cases complete successfully under
        current. The traces confirm that rocSPARSE CSR SpMV kernels are major GPU
        hotspots, while `hipMemcpy`, `hipMemcpyAsync`, and `hipLaunchKernel` are
        prominent HIP API costs on the longer cases.
    """),
    "validation/README.zh-CN.md": dedent("""
        ## W7900 P10 targeted rocprof / 2026-06-17

        P10 基于 P9 派生指标选择 5 个代表 case，对 current W7900/gfx1100
        分支做 targeted profiling。

        - 汇总：[w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md](w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md)
        - 英文汇总：[w7900_p10_current_targeted_rocprof_20260617_summary.md](w7900_p10_current_targeted_rocprof_20260617_summary.md)
        - 运行 CSV：[w7900_p10_current_targeted_rocprof_20260617_runtime.csv](w7900_p10_current_targeted_rocprof_20260617_runtime.csv)
        - Kernel top CSV：[w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv](w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv)
        - HIP API top CSV：[w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv](w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv)
        - Memory copy top CSV：[w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv](w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv)

        关键结论：5 个 targeted case 在 current 下均成功完成。trace 结果确认
        rocSPARSE CSR SpMV kernel 是主要 GPU 热点之一；较长 case 中
        `hipMemcpy`、`hipMemcpyAsync` 和 `hipLaunchKernel` 也是突出的 HIP API 成本。
    """),
    "docs/W7900_CURRENT_STATUS.md": dedent("""
        ## P10 targeted rocprof summary / 2026-06-17

        P10 adds targeted rocprofv3 profiling for five representative cases from
        the P9 derived-metric analysis:

        - positive execution-efficiency sample: `thk_48`
        - stable iteration-count sample: `square41`
        - convergence-regression samples: `L2CTA3D`, `set-cover-model`,
          `tpl-tub-ws1617`

        Links:

        - [P10 summary](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.md)
        - [P10 runtime CSV](../validation/w7900_p10_current_targeted_rocprof_20260617_runtime.csv)
        - [P10 kernel top CSV](../validation/w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv)
        - [P10 HIP API top CSV](../validation/w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv)
        - [P10 memory copy top CSV](../validation/w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv)

        All five targeted cases finish successfully under current. The compact
        traces show that rocSPARSE CSR SpMV kernels dominate several GPU kernel
        profiles, while `hipMemcpy`, `hipMemcpyAsync`, and `hipLaunchKernel`
        remain important HIP API costs. This supports the next tuning direction:
        focus on SpMV behavior, kernel-launch volume, and host-device copy
        reduction without changing solver numerical logic blindly.
    """),
    "docs/W7900_CURRENT_STATUS.zh-CN.md": dedent("""
        ## P10 targeted rocprof 汇总 / 2026-06-17

        P10 基于 P9 派生指标选择 5 个代表 case 做 targeted rocprofv3 profiling：

        - 正向执行效率样本：`thk_48`
        - 迭代数稳定样本：`square41`
        - 收敛迭代数回退样本：`L2CTA3D`、`set-cover-model`、
          `tpl-tub-ws1617`

        链接：

        - [P10 中文汇总](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.zh-CN.md)
        - [P10 runtime CSV](../validation/w7900_p10_current_targeted_rocprof_20260617_runtime.csv)
        - [P10 kernel top CSV](../validation/w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv)
        - [P10 HIP API top CSV](../validation/w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv)
        - [P10 memory copy top CSV](../validation/w7900_p10_current_targeted_rocprof_20260617_memory_copy_top.csv)

        5 个 targeted case 在 current 下均成功完成。compact trace 显示，
        rocSPARSE CSR SpMV kernel 在多个 case 中是主要 GPU kernel 热点；
        `hipMemcpy`、`hipMemcpyAsync` 和 `hipLaunchKernel` 也是较长 case 上突出的
        HIP API 成本。这说明后续调优应重点关注 SpMV 行为、kernel launch 数量
        和 host-device copy reduction，同时不要盲目改动 solver 数值逻辑。
    """),
}

def append_once(path: Path, section: str) -> bool:
    text = path.read_text(encoding="utf-8")
    heading = section.strip().splitlines()[0].strip()
    if heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return False
    path.write_text(text.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8")
    print(f"[OK] updated {path.relative_to(ROOT)}")
    return True

def main():
    changed = 0
    for rel, section in SECTIONS.items():
        path = ROOT / rel
        if not path.exists():
            raise FileNotFoundError(path)
        changed += int(append_once(path, section))
    print(f"[DONE] updated {changed} files")

if __name__ == "__main__":
    main()
