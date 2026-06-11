from pathlib import Path
import csv
import shutil


DATE = "20260611"

SMOKE_DIR = Path("validation/results/w7900_smoke_20260611_162123")
EXT_DIR = Path("validation/results/w7900_extended_netlib_20260611_162213")

SMOKE_CSV = Path(f"validation/w7900_smoke_summary_{DATE}.csv")
SMOKE_MD = Path(f"validation/w7900_smoke_summary_{DATE}.md")
SMOKE_ZH = Path(f"validation/w7900_smoke_summary_{DATE}.zh-CN.md")

EXT_CSV = Path(f"validation/w7900_extended_netlib_summary_{DATE}.csv")
EXT_MD = Path(f"validation/w7900_extended_netlib_summary_{DATE}.md")
EXT_ZH = Path(f"validation/w7900_extended_netlib_summary_{DATE}.zh-CN.md")


def read_case_rows(summary_csv):
    rows = []
    with summary_csv.open(newline="") as f:
        reader = csv.DictReader(f)
        by_case = {}
        for row in reader:
            by_case.setdefault(row["case"], {})[row["backend"]] = row

    for case, data in by_case.items():
        cpu = data.get("cpu", {})
        rocm = data.get("rocm_w7900", {})
        result = cpu.get("result") or rocm.get("result") or ""
        rows.append((case, result, cpu, rocm))
    return rows


def copy_csv(src_dir, dst_csv):
    src = src_dir / "summary.csv"
    if not src.exists():
        raise SystemExit(f"[error] missing {src}")
    shutil.copyfile(src, dst_csv)
    print(f"[ok] wrote {dst_csv}")


def write_en(title, src_dir, dst_md, dst_csv, rows, note):
    with dst_md.open("w") as f:
        f.write(f"# {title}\n\n")
        f.write("> 中文: ")
        f.write(f"[{dst_md.with_suffix('').name}.zh-CN.md]({dst_md.with_suffix('').name}.zh-CN.md)\n\n")
        f.write(f"CSV source: [{dst_csv.name}]({dst_csv.name})\n\n")
        f.write(f"Generated result directory: `{src_dir}`\n\n")
        f.write(note)
        f.write("\n\n")
        f.write("| case | result | CPU status | ROCm/W7900 status | CPU iter | ROCm iter | CPU rel primal | ROCm rel primal | CPU rel dual | ROCm rel dual | CPU rel gap | ROCm rel gap |\n")
        f.write("|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for case, result, cpu, rocm in rows:
            cpu_status = f"{cpu.get('terminationCode','')}/{cpu.get('primalCode','')}/{cpu.get('dualCode','')}"
            rocm_status = f"{rocm.get('terminationCode','')}/{rocm.get('primalCode','')}/{rocm.get('dualCode','')}"
            f.write(
                f"| {case} | {result} | {cpu_status} | {rocm_status} | "
                f"{cpu.get('nIter','')} | {rocm.get('nIter','')} | "
                f"{cpu.get('dRelPrimalFeas','')} | {rocm.get('dRelPrimalFeas','')} | "
                f"{cpu.get('dRelDualFeas','')} | {rocm.get('dRelDualFeas','')} | "
                f"{cpu.get('dRelDualityGap','')} | {rocm.get('dRelDualityGap','')} |\n"
            )

        counts = {}
        for _, result, _, _ in rows:
            counts[result] = counts.get(result, 0) + 1

        f.write("\n## Counts\n\n")
        f.write("```text\n")
        f.write(f"PASS: {counts.get('PASS', 0)}\n")
        f.write(f"INCOMPLETE: {counts.get('INCOMPLETE', 0)}\n")
        f.write(f"FAIL: {counts.get('FAIL', 0)}\n")
        f.write("```\n\n")
        f.write("## Interpretation\n\n")
        f.write(
            "This W7900 run follows the repository validation policy: CPU is used as the baseline, "
            "ROCm/W7900 is compared against CPU by solver status, and OPTIMAL cases are checked "
            "against relative primal feasibility, relative dual feasibility, and relative gap thresholds.\n"
        )
    print(f"[ok] wrote {dst_md}")


def write_zh(title, src_dir, dst_md, dst_csv, rows, note):
    with dst_md.open("w") as f:
        f.write(f"# {title}\n\n")
        f.write("> English: ")
        f.write(f"[{dst_md.name.replace('.zh-CN', '')}]({dst_md.name.replace('.zh-CN', '')})\n\n")
        f.write(f"CSV 来源: [{dst_csv.name}]({dst_csv.name})\n\n")
        f.write(f"生成结果目录: `{src_dir}`\n\n")
        f.write(note)
        f.write("\n\n")
        f.write("| case | 结果 | CPU 状态 | ROCm/W7900 状态 | CPU 迭代 | ROCm 迭代 | CPU rel primal | ROCm rel primal | CPU rel dual | ROCm rel dual | CPU rel gap | ROCm rel gap |\n")
        f.write("|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for case, result, cpu, rocm in rows:
            cpu_status = f"{cpu.get('terminationCode','')}/{cpu.get('primalCode','')}/{cpu.get('dualCode','')}"
            rocm_status = f"{rocm.get('terminationCode','')}/{rocm.get('primalCode','')}/{rocm.get('dualCode','')}"
            f.write(
                f"| {case} | {result} | {cpu_status} | {rocm_status} | "
                f"{cpu.get('nIter','')} | {rocm.get('nIter','')} | "
                f"{cpu.get('dRelPrimalFeas','')} | {rocm.get('dRelPrimalFeas','')} | "
                f"{cpu.get('dRelDualFeas','')} | {rocm.get('dRelDualFeas','')} | "
                f"{cpu.get('dRelDualityGap','')} | {rocm.get('dRelDualityGap','')} |\n"
            )

        counts = {}
        for _, result, _, _ in rows:
            counts[result] = counts.get(result, 0) + 1

        f.write("\n## 计数\n\n")
        f.write("```text\n")
        f.write(f"PASS: {counts.get('PASS', 0)}\n")
        f.write(f"INCOMPLETE: {counts.get('INCOMPLETE', 0)}\n")
        f.write(f"FAIL: {counts.get('FAIL', 0)}\n")
        f.write("```\n\n")
        f.write("## 解释\n\n")
        f.write(
            "本次 W7900 运行遵循仓库 validation 语义：CPU 作为 baseline，"
            "ROCm/W7900 与 CPU 比较 solver status；对于 OPTIMAL case，"
            "再检查 relative primal feasibility、relative dual feasibility 和 relative gap 是否满足容差。\n"
        )
    print(f"[ok] wrote {dst_md}")


def insert_once(path, anchor, block):
    p = Path(path)
    s = p.read_text()
    if block.strip() in s:
        print(f"[skip] {path}: already has W7900 block")
        return
    if anchor not in s:
        raise SystemExit(f"[error] anchor not found in {path}: {anchor}")
    p.write_text(s.replace(anchor, block + "\n" + anchor, 1))
    print(f"[ok] updated {path}")


def main():
    smoke_rows = read_case_rows(SMOKE_DIR / "summary.csv")
    ext_rows = read_case_rows(EXT_DIR / "summary.csv")

    copy_csv(SMOKE_DIR, SMOKE_CSV)
    copy_csv(EXT_DIR, EXT_CSV)

    write_en(
        "W7900 smoke validation summary 20260611",
        SMOKE_DIR,
        SMOKE_MD,
        SMOKE_CSV,
        smoke_rows,
        "This smoke validation runs the repository smoke case list on W7900 / `gfx1100`: `afiro` and `sc50b`.",
    )
    write_zh(
        "W7900 smoke validation 汇总 20260611",
        SMOKE_DIR,
        SMOKE_ZH,
        SMOKE_CSV,
        smoke_rows,
        "本 smoke validation 在 W7900 / `gfx1100` 上运行仓库 smoke case list：`afiro` 和 `sc50b`。",
    )

    write_en(
        "W7900 extended Netlib validation summary 20260611",
        EXT_DIR,
        EXT_MD,
        EXT_CSV,
        ext_rows,
        "This extended Netlib validation runs `afiro`, `adlittle`, `blend`, `sc50a`, `sc50b`, and `share2b` on W7900 / `gfx1100`.",
    )
    write_zh(
        "W7900 extended Netlib validation 汇总 20260611",
        EXT_DIR,
        EXT_ZH,
        EXT_CSV,
        ext_rows,
        "本 extended Netlib validation 在 W7900 / `gfx1100` 上运行 `afiro`、`adlittle`、`blend`、`sc50a`、`sc50b` 和 `share2b`。",
    )

    validation_block_en = """## W7900 / gfx1100 validation summaries

| File | Description |
|---|---|
| [w7900_smoke_summary_20260611.md](w7900_smoke_summary_20260611.md) | W7900 / `gfx1100` smoke validation summary |
| [w7900_smoke_summary_20260611.zh-CN.md](w7900_smoke_summary_20260611.zh-CN.md) | Chinese W7900 / `gfx1100` smoke validation summary |
| [w7900_smoke_summary_20260611.csv](w7900_smoke_summary_20260611.csv) | W7900 smoke validation CSV |
| [w7900_extended_netlib_summary_20260611.md](w7900_extended_netlib_summary_20260611.md) | W7900 / `gfx1100` extended Netlib validation summary |
| [w7900_extended_netlib_summary_20260611.zh-CN.md](w7900_extended_netlib_summary_20260611.zh-CN.md) | Chinese W7900 / `gfx1100` extended Netlib validation summary |
| [w7900_extended_netlib_summary_20260611.csv](w7900_extended_netlib_summary_20260611.csv) | W7900 extended Netlib validation CSV |
"""

    validation_block_zh = """## W7900 / gfx1100 validation 汇总

| 文件 | 说明 |
|---|---|
| [w7900_smoke_summary_20260611.md](w7900_smoke_summary_20260611.md) | W7900 / `gfx1100` smoke validation 英文汇总 |
| [w7900_smoke_summary_20260611.zh-CN.md](w7900_smoke_summary_20260611.zh-CN.md) | W7900 / `gfx1100` smoke validation 中文汇总 |
| [w7900_smoke_summary_20260611.csv](w7900_smoke_summary_20260611.csv) | W7900 smoke validation CSV |
| [w7900_extended_netlib_summary_20260611.md](w7900_extended_netlib_summary_20260611.md) | W7900 / `gfx1100` extended Netlib validation 英文汇总 |
| [w7900_extended_netlib_summary_20260611.zh-CN.md](w7900_extended_netlib_summary_20260611.zh-CN.md) | W7900 / `gfx1100` extended Netlib validation 中文汇总 |
| [w7900_extended_netlib_summary_20260611.csv](w7900_extended_netlib_summary_20260611.csv) | W7900 extended Netlib validation CSV |
"""

    insert_once("validation/README.md", "## Related project docs", validation_block_en)
    insert_once("validation/README.zh-CN.md", "## 相关项目文档", validation_block_zh)

    docs_block = """| W7900 smoke validation / W7900 smoke 验证 | [../validation/w7900_smoke_summary_20260611.md](../validation/w7900_smoke_summary_20260611.md) | [../validation/w7900_smoke_summary_20260611.zh-CN.md](../validation/w7900_smoke_summary_20260611.zh-CN.md) | [CSV](../validation/w7900_smoke_summary_20260611.csv) |
| W7900 extended Netlib validation / W7900 扩展 Netlib 验证 | [../validation/w7900_extended_netlib_summary_20260611.md](../validation/w7900_extended_netlib_summary_20260611.md) | [../validation/w7900_extended_netlib_summary_20260611.zh-CN.md](../validation/w7900_extended_netlib_summary_20260611.zh-CN.md) | [CSV](../validation/w7900_extended_netlib_summary_20260611.csv) |"""
    insert_once(
        "docs/README.md",
        "| Validation directory index / validation 目录索引 | [../validation/README.md](../validation/README.md) | [../validation/README.zh-CN.md](../validation/README.zh-CN.md) | See validation index |",
        "| Validation directory index / validation 目录索引 | [../validation/README.md](../validation/README.md) | [../validation/README.zh-CN.md](../validation/README.zh-CN.md) | See validation index |\n" + docs_block,
    )

    print("[done] W7900 validation documentation generated and indexed")


if __name__ == "__main__":
    main()
