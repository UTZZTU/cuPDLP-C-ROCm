#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REPLACEMENTS = {
    "docs/SUBMISSION_CHECKLIST.md": [
        (
            "Do not claim W7900-specific bottlenecks have been optimized before `rocprof` results exist.",
            "Keep W7900-specific tuning claims within the committed P10/P11/P12 evidence: P10 targeted profiling, P11 default `HIPSPARSE_SPMV_CSR_ALG1`, rollback with `CUPDLP_HIP_SPMV_ALG=csr_alg2`, and the P12 rejected experiment note."
        ),
    ],
    "docs/W7900_ROCM_PROFILING_PLAN.zh-CN.md": [
        (
            "不要从 hard3 开始。hard3 应等 profiling workflow 稳定后再用。",
            "原始计划中不从 hard3 开始；当前 hard3 probe2 已归档，后续不再作为 pending profiling 前置项。"
        ),
    ],
    "docs/ROCM_TUNING_HISTORY.zh-CN.md": [
        (
            "- W7900 / `gfx1100` 平台还需要后续实测。",
            "- W7900 / `gfx1100` 已完成独立 P10/P11/P12 证据链；若要增强性能统计说服力，后续只补代表 case repeated validation。"
        ),
        (
            "7. 在 W7900 上针对 `gfx1100` 做平台化调优。",
            "7. W7900 平台化调优已由 P10/P11/P12 证据链闭环；后续仅保留 P14 representative repeated validation 作为可选增强。"
        ),
    ],
}

def main():
    changed_files = 0

    for rel, reps in REPLACEMENTS.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        original = text

        for old, new in reps:
            if old not in text:
                print(f"[MISS] {rel}: {old}")
                continue
            text = text.replace(old, new, 1)
            print(f"[OK] {rel}: replaced {old[:80]}")

        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            changed_files += 1
            print(f"[WRITE] {rel}")

    print(f"[DONE] changed {changed_files} files")

if __name__ == "__main__":
    main()
