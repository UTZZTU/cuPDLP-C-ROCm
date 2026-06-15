from pathlib import Path

def replace_once(path, old, new):
    p = Path(path)
    s = p.read_text()
    if new in s:
        print(f"{path}: already updated")
        return
    if old not in s:
        raise SystemExit(f"{path}: anchor not found")
    p.write_text(s.replace(old, new, 1))
    print(f"{path}: updated")

replace_once(
    "validation/w7900_vs_cross_device_27cases_20260611.md",
    "- W7900 is not yet faster overall in this current first-port baseline.",
    "- W7900 is not yet faster overall in this current W7900 Netlib engineering baseline. This baseline is before W7900-specific tuning and should not be interpreted as the final optimized ROCm/gfx1100 result."
)

replace_once(
    "validation/w7900_vs_cross_device_27cases_20260611.zh-CN.md",
    "- 当前 first-port baseline 下，W7900 整体还没有快过已有 reference 平台。",
    "- W7900 在当前 W7900 Netlib 工程基线下整体尚未快过已有 reference 平台。该基线位于 W7900-specific tuning 之前，不应解释为最终优化后的 ROCm/gfx1100 结果。"
)

print("done")
