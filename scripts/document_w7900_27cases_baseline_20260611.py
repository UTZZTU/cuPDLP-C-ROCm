from pathlib import Path
import csv
import os
import shutil


DATE = "20260611"

RUN_DIR = Path(
    os.environ.get(
        "RUN_DIR",
        "validation/results/w7900_27cases_baseline_20260611_171157",
    )
)

RAW_SRC = RUN_DIR / "raw_runs.csv"
AGG_SRC = RUN_DIR / "aggregated_summary.csv"

RAW_DST = Path(f"validation/w7900_27cases_baseline_{DATE}_raw.csv")
AGG_DST = Path(f"validation/w7900_27cases_baseline_{DATE}_aggregated.csv")
MD_DST = Path(f"validation/w7900_27cases_baseline_{DATE}.md")
ZH_DST = Path(f"validation/w7900_27cases_baseline_{DATE}.zh-CN.md")


def require(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"[error] missing: {path}")


def read_rows(path: Path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv_outputs() -> None:
    require(RAW_SRC)
    require(AGG_SRC)
    shutil.copyfile(RAW_SRC, RAW_DST)
    shutil.copyfile(AGG_SRC, AGG_DST)
    print(f"[ok] wrote {RAW_DST}")
    print(f"[ok] wrote {AGG_DST}")


def status_counts(rows):
    counts = {}
    for row in rows:
        statuses = row.get("all_statuses", "")
        key = ";".join(sorted(set(x for x in statuses.split(";") if x)))
        counts[key] = counts.get(key, 0) + 1
    return counts


def top_slowest(rows, n=8):
    def key(row):
        try:
            return float(row.get("median_solve_time_sec", "0"))
        except Exception:
            return 0.0

    return sorted(rows, key=key, reverse=True)[:n]


def write_en(rows):
    counts = status_counts(rows)
    slow = top_slowest(rows)

    with MD_DST.open("w") as f:
        f.write("# W7900 27-case repeated ROCm baseline 20260611\n\n")
        f.write("> 中文: [w7900_27cases_baseline_20260611.zh-CN.md](w7900_27cases_baseline_20260611.zh-CN.md)\n\n")
        f.write("> Validation index: [README.md](README.md)\n\n")
        f.write("CSV sources: ")
        f.write("[raw](w7900_27cases_baseline_20260611_raw.csv), ")
        f.write("[aggregated](w7900_27cases_baseline_20260611_aggregated.csv)\n\n")

        f.write(f"Run directory:\n\n```text\n{RUN_DIR}\n```\n\n")
        f.write("Configuration:\n\n```text\n")
        f.write("Platform: AMD Radeon PRO W7900 / gfx1100\n")
        f.write("Backend: ROCm/HIP only\n")
        f.write("Case list: validation/cases_benchmark_200m_w7900_27.txt\n")
        f.write("Excluded case: greenbea\n")
        f.write("Repeats per case: 3\n")
        f.write("Timeout per repeat: 900 seconds\n")
        f.write("Primary metric: median solve time across repeated ROCm/W7900 runs\n")
        f.write("```\n\n")

        f.write("This file establishes the W7900 baseline for later same-platform tuning comparisons. It should not be interpreted as a tuning gain by itself; future optimized branches should be compared against this baseline using the same 27-case list, repeat count, timeout, and W7900 platform.\n\n")

        f.write("## Status counts\n\n")
        f.write("| status set | cases |\n")
        f.write("|---|---:|\n")
        for key, count in sorted(counts.items()):
            f.write(f"| {key} | {count} |\n")

        f.write("\n## Slowest cases by median solve time\n\n")
        f.write("| case | tier | median solve time | mean solve time | CV | median matvec | nIter |\n")
        f.write("|---|---|---:|---:|---:|---:|---|\n")
        for r in slow:
            f.write(
                f"| {r['case']} | {r['tier']} | "
                f"{r['median_solve_time_sec']} | {r['mean_solve_time_sec']} | "
                f"{r['cv_solve_time']} | {r['median_DeviceMatVecProdTime']} | "
                f"{r['all_nIter']} |\n"
            )

        f.write("\n## Full per-case aggregated results\n\n")
        f.write("| case | tier | valid n | median solve | mean solve | CV | median matvec | statuses | nIter |\n")
        f.write("|---|---|---:|---:|---:|---:|---:|---|---|\n")
        for r in rows:
            f.write(
                f"| {r['case']} | {r['tier']} | {r['valid_n']} | "
                f"{r['median_solve_time_sec']} | {r['mean_solve_time_sec']} | "
                f"{r['cv_solve_time']} | {r['median_DeviceMatVecProdTime']} | "
                f"{r['all_statuses']} | {r['all_nIter']} |\n"
            )

        f.write("\n## Interpretation\n\n")
        f.write("- All 27 non-`greenbea` benchmark cases reached `OPTIMAL` in all three repeated ROCm/W7900 runs.\n")
        f.write("- The slowest cases are expected to dominate future tuning comparisons, especially `pilot4`, `greenbeb`, `pilot87`, `lotfi`, and `stair`.\n")
        f.write("- This is a baseline. Future ROCm tuning should compare against this file with median solve time and CV as the primary stability-aware metrics.\n")

    print(f"[ok] wrote {MD_DST}")


def write_zh(rows):
    counts = status_counts(rows)
    slow = top_slowest(rows)

    with ZH_DST.open("w") as f:
        f.write("# W7900 27-case repeated ROCm baseline 20260611\n\n")
        f.write("> English: [w7900_27cases_baseline_20260611.md](w7900_27cases_baseline_20260611.md)\n\n")
        f.write("> Validation 索引: [README.zh-CN.md](README.zh-CN.md)\n\n")
        f.write("CSV 来源: ")
        f.write("[raw](w7900_27cases_baseline_20260611_raw.csv), ")
        f.write("[aggregated](w7900_27cases_baseline_20260611_aggregated.csv)\n\n")

        f.write(f"运行目录:\n\n```text\n{RUN_DIR}\n```\n\n")
        f.write("配置:\n\n```text\n")
        f.write("平台: AMD Radeon PRO W7900 / gfx1100\n")
        f.write("后端: 仅 ROCm/HIP\n")
        f.write("Case list: validation/cases_benchmark_200m_w7900_27.txt\n")
        f.write("排除 case: greenbea\n")
        f.write("每个 case 重复次数: 3\n")
        f.write("每次运行 timeout: 900 秒\n")
        f.write("主指标: repeated ROCm/W7900 runs 的 median solve time\n")
        f.write("```\n\n")

        f.write("本文档用于建立 W7900 后续同平台调优对比的 baseline。它本身不表示调优收益；未来优化分支应使用同一 27-case list、重复次数、timeout 和 W7900 平台与该 baseline 做比较。\n\n")

        f.write("## 状态计数\n\n")
        f.write("| status set | cases |\n")
        f.write("|---|---:|\n")
        for key, count in sorted(counts.items()):
            f.write(f"| {key} | {count} |\n")

        f.write("\n## 按 median solve time 排序的最慢 case\n\n")
        f.write("| case | tier | median solve time | mean solve time | CV | median matvec | nIter |\n")
        f.write("|---|---|---:|---:|---:|---:|---|\n")
        for r in slow:
            f.write(
                f"| {r['case']} | {r['tier']} | "
                f"{r['median_solve_time_sec']} | {r['mean_solve_time_sec']} | "
                f"{r['cv_solve_time']} | {r['median_DeviceMatVecProdTime']} | "
                f"{r['all_nIter']} |\n"
            )

        f.write("\n## 全部 case 聚合结果\n\n")
        f.write("| case | tier | valid n | median solve | mean solve | CV | median matvec | statuses | nIter |\n")
        f.write("|---|---|---:|---:|---:|---:|---:|---|---|\n")
        for r in rows:
            f.write(
                f"| {r['case']} | {r['tier']} | {r['valid_n']} | "
                f"{r['median_solve_time_sec']} | {r['mean_solve_time_sec']} | "
                f"{r['cv_solve_time']} | {r['median_DeviceMatVecProdTime']} | "
                f"{r['all_statuses']} | {r['all_nIter']} |\n"
            )

        f.write("\n## 解释\n\n")
        f.write("- 排除 `greenbea` 后，27 个 benchmark case 在三次 ROCm/W7900 重复运行中全部达到 `OPTIMAL`。\n")
        f.write("- 后续调优对比中，最慢 case 会主导整体表现，尤其是 `pilot4`、`greenbeb`、`pilot87`、`lotfi` 和 `stair`。\n")
        f.write("- 这是一份 baseline。后续 ROCm tuning 应优先使用 median solve time 和 CV 作为稳定性敏感的主要指标。\n")

    print(f"[ok] wrote {ZH_DST}")


def upsert_block(path, begin, end, block, anchors):
    p = Path(path)
    s = p.read_text()

    if begin in s and end in s:
        pre = s.split(begin, 1)[0]
        post = s.split(end, 1)[1]
        p.write_text(pre + block + post)
        print(f"[ok] replaced block in {path}")
        return

    for anchor in anchors:
        if anchor in s:
            p.write_text(s.replace(anchor, block + "\n" + anchor, 1))
            print(f"[ok] inserted block in {path}")
            return

    p.write_text(s.rstrip() + "\n\n" + block + "\n")
    print(f"[ok] appended block in {path}")


def update_indexes():
    block_en = """<!-- W7900_27CASE_BASELINE_20260611_BEGIN -->
## W7900 / gfx1100 27-case baseline

| File | Description |
|---|---|
| [w7900_27cases_baseline_20260611.md](w7900_27cases_baseline_20260611.md) | W7900 / `gfx1100` 27-case repeated ROCm baseline |
| [w7900_27cases_baseline_20260611.zh-CN.md](w7900_27cases_baseline_20260611.zh-CN.md) | Chinese W7900 / `gfx1100` 27-case repeated ROCm baseline |
| [w7900_27cases_baseline_20260611_aggregated.csv](w7900_27cases_baseline_20260611_aggregated.csv) | Aggregated median/mean/CV baseline CSV |
| [w7900_27cases_baseline_20260611_raw.csv](w7900_27cases_baseline_20260611_raw.csv) | Raw repeated-run baseline CSV |
<!-- W7900_27CASE_BASELINE_20260611_END -->
"""

    block_zh = """<!-- W7900_27CASE_BASELINE_20260611_BEGIN -->
## W7900 / gfx1100 27-case baseline

| 文件 | 说明 |
|---|---|
| [w7900_27cases_baseline_20260611.md](w7900_27cases_baseline_20260611.md) | W7900 / `gfx1100` 27-case repeated ROCm baseline 英文汇总 |
| [w7900_27cases_baseline_20260611.zh-CN.md](w7900_27cases_baseline_20260611.zh-CN.md) | W7900 / `gfx1100` 27-case repeated ROCm baseline 中文汇总 |
| [w7900_27cases_baseline_20260611_aggregated.csv](w7900_27cases_baseline_20260611_aggregated.csv) | 聚合 median/mean/CV baseline CSV |
| [w7900_27cases_baseline_20260611_raw.csv](w7900_27cases_baseline_20260611_raw.csv) | repeated-run raw baseline CSV |
<!-- W7900_27CASE_BASELINE_20260611_END -->
"""

    docs_block = """<!-- W7900_27CASE_BASELINE_20260611_BEGIN -->
| W7900 27-case ROCm baseline / W7900 27-case ROCm baseline | [../validation/w7900_27cases_baseline_20260611.md](../validation/w7900_27cases_baseline_20260611.md) | [../validation/w7900_27cases_baseline_20260611.zh-CN.md](../validation/w7900_27cases_baseline_20260611.zh-CN.md) | [aggregated CSV](../validation/w7900_27cases_baseline_20260611_aggregated.csv), [raw CSV](../validation/w7900_27cases_baseline_20260611_raw.csv) |
<!-- W7900_27CASE_BASELINE_20260611_END -->
"""

    upsert_block(
        "validation/README.md",
        "<!-- W7900_27CASE_BASELINE_20260611_BEGIN -->",
        "<!-- W7900_27CASE_BASELINE_20260611_END -->",
        block_en,
        ["## Related project docs", "## W7900 / gfx1100 validation summaries"],
    )

    upsert_block(
        "validation/README.zh-CN.md",
        "<!-- W7900_27CASE_BASELINE_20260611_BEGIN -->",
        "<!-- W7900_27CASE_BASELINE_20260611_END -->",
        block_zh,
        ["## 相关项目文档", "## W7900 / gfx1100 validation 汇总"],
    )

    upsert_block(
        "docs/README.md",
        "<!-- W7900_27CASE_BASELINE_20260611_BEGIN -->",
        "<!-- W7900_27CASE_BASELINE_20260611_END -->",
        docs_block,
        ["| Validation directory index / validation 目录索引 |"],
    )


def main():
    require(RUN_DIR)
    write_csv_outputs()
    rows = read_rows(AGG_DST)
    write_en(rows)
    write_zh(rows)
    update_indexes()
    print("[done] W7900 27-case baseline documentation generated")


if __name__ == "__main__":
    main()
