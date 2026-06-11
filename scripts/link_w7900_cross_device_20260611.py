from pathlib import Path


def insert_section_before_anchor(path, anchor, block, marker):
    p = Path(path)
    s = p.read_text()

    if marker in s:
        print(f"[skip] {path}: already linked")
        return

    if anchor not in s:
        raise SystemExit(f"[error] anchor not found in {path}: {anchor}")

    p.write_text(s.replace(anchor, block.rstrip() + "\n\n" + anchor, 1))
    print(f"[ok] updated {path}")


def insert_table_row_after(path, after_line, row, marker):
    p = Path(path)
    s = p.read_text()

    if marker in s:
        print(f"[skip] {path}: already linked")
        return

    if after_line not in s:
        raise SystemExit(f"[error] table anchor not found in {path}: {after_line}")

    p.write_text(s.replace(after_line, after_line + "\n" + row, 1))
    print(f"[ok] updated {path}")


validation_en = """<!-- W7900_CROSS_DEVICE_20260611_BEGIN -->
## W7900 vs existing cross-device reference

| File | Description |
|---|---|
| [w7900_vs_cross_device_27cases_20260611.md](w7900_vs_cross_device_27cases_20260611.md) | W7900 / `gfx1100` vs existing RTX 3090, RTX 4090D, and Radeon 890M cross-device Netlib reference |
| [w7900_vs_cross_device_27cases_20260611.zh-CN.md](w7900_vs_cross_device_27cases_20260611.zh-CN.md) | Chinese W7900 cross-device reference comparison |
| [w7900_vs_cross_device_27cases_20260611.csv](w7900_vs_cross_device_27cases_20260611.csv) | Per-case cross-device comparison CSV |
<!-- W7900_CROSS_DEVICE_20260611_END -->"""

validation_zh = """<!-- W7900_CROSS_DEVICE_20260611_BEGIN -->
## W7900 vs 既有跨设备 reference

| 文件 | 说明 |
|---|---|
| [w7900_vs_cross_device_27cases_20260611.md](w7900_vs_cross_device_27cases_20260611.md) | W7900 / `gfx1100` 与既有 RTX 3090、RTX 4090D、Radeon 890M Netlib 跨设备 reference 的英文对比 |
| [w7900_vs_cross_device_27cases_20260611.zh-CN.md](w7900_vs_cross_device_27cases_20260611.zh-CN.md) | W7900 跨设备 reference 中文对比 |
| [w7900_vs_cross_device_27cases_20260611.csv](w7900_vs_cross_device_27cases_20260611.csv) | per-case 跨设备对比 CSV |
<!-- W7900_CROSS_DEVICE_20260611_END -->"""

docs_row = "| W7900 vs cross-device reference / W7900 跨设备参考对比 | [../validation/w7900_vs_cross_device_27cases_20260611.md](../validation/w7900_vs_cross_device_27cases_20260611.md) | [../validation/w7900_vs_cross_device_27cases_20260611.zh-CN.md](../validation/w7900_vs_cross_device_27cases_20260611.zh-CN.md) | [CSV](../validation/w7900_vs_cross_device_27cases_20260611.csv) |"

insert_section_before_anchor(
    "validation/README.md",
    "## Related project docs",
    validation_en,
    "W7900_CROSS_DEVICE_20260611_BEGIN",
)

insert_section_before_anchor(
    "validation/README.zh-CN.md",
    "## 相关项目文档",
    validation_zh,
    "W7900_CROSS_DEVICE_20260611_BEGIN",
)

insert_table_row_after(
    "docs/README.md",
    "| W7900 27-case ROCm baseline / W7900 27-case ROCm baseline | [../validation/w7900_27cases_baseline_20260611.md](../validation/w7900_27cases_baseline_20260611.md) | [../validation/w7900_27cases_baseline_20260611.zh-CN.md](../validation/w7900_27cases_baseline_20260611.zh-CN.md) | [aggregated CSV](../validation/w7900_27cases_baseline_20260611_aggregated.csv), [raw CSV](../validation/w7900_27cases_baseline_20260611_raw.csv) |",
    docs_row,
    "w7900_vs_cross_device_27cases_20260611.md",
)

print("[done] linked W7900 cross-device comparison")
