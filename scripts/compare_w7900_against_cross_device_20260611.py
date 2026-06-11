from pathlib import Path
import csv
import math
import statistics


DATE = "20260611"

CROSS = Path("validation/cross_device_full_summary.csv")
W7900 = Path("validation/w7900_27cases_baseline_20260611_aggregated.csv")

OUT_CSV = Path(f"validation/w7900_vs_cross_device_27cases_{DATE}.csv")
OUT_MD = Path(f"validation/w7900_vs_cross_device_27cases_{DATE}.md")
OUT_ZH = Path(f"validation/w7900_vs_cross_device_27cases_{DATE}.zh-CN.md")


def fnum(x):
    try:
        if x is None or x == "":
            return None
        return float(x)
    except Exception:
        return None


def geomean(vals):
    vals = [v for v in vals if v and v > 0]
    if not vals:
        return ""
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


def read_w7900():
    out = {}
    with W7900.open(newline="") as f:
        for r in csv.DictReader(f):
            out[r["case"]] = r
    return out


def read_cross():
    rows = []
    with CROSS.open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def main():
    w = read_w7900()
    cross = read_cross()

    rows = []
    for r in cross:
        case = r["case"]
        if case not in w:
            continue
        if case == "greenbea":
            continue

        old_time = fnum(r.get("gpu_time_sec"))
        w_time = fnum(w[case].get("median_solve_time_sec"))
        if old_time is None or w_time is None or w_time <= 0:
            continue

        ratio = old_time / w_time
        rows.append({
            "device": r["device"],
            "backend": r["backend"],
            "case": case,
            "tier": w[case].get("tier", ""),
            "old_gpu_status": r.get("gpu_status", ""),
            "w7900_statuses": w[case].get("all_statuses", ""),
            "old_gpu_iter": r.get("gpu_iter", ""),
            "w7900_nIter": w[case].get("all_nIter", ""),
            "old_gpu_time_sec": old_time,
            "w7900_median_solve_time_sec": w_time,
            "old_over_w7900_speed_ratio": ratio,
            "winner": "W7900" if ratio > 1 else r["device"],
            "old_note": r.get("note", ""),
        })

    fields = [
        "device",
        "backend",
        "case",
        "tier",
        "old_gpu_status",
        "w7900_statuses",
        "old_gpu_iter",
        "w7900_nIter",
        "old_gpu_time_sec",
        "w7900_median_solve_time_sec",
        "old_over_w7900_speed_ratio",
        "winner",
        "old_note",
    ]

    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    by_dev = {}
    for r in rows:
        key = f"{r['device']} {r['backend']}"
        by_dev.setdefault(key, []).append(r)

    summary = []
    for dev, rs in by_dev.items():
        ratios = [float(r["old_over_w7900_speed_ratio"]) for r in rs]
        w_wins = sum(1 for r in rs if r["winner"] == "W7900")
        old_wins = len(rs) - w_wins
        summary.append({
            "device": dev,
            "cases": len(rs),
            "geomean_old_over_w7900": geomean(ratios),
            "median_old_over_w7900": statistics.median(ratios),
            "w7900_faster_cases": w_wins,
            "other_faster_cases": old_wins,
        })

    def write_table(f, rs):
        f.write("| device | cases | geomean old/W7900 | median old/W7900 | W7900 faster cases | other faster cases |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        for s in summary:
            f.write(
                f"| {s['device']} | {s['cases']} | "
                f"{s['geomean_old_over_w7900']:.6g} | "
                f"{s['median_old_over_w7900']:.6g} | "
                f"{s['w7900_faster_cases']} | "
                f"{s['other_faster_cases']} |\n"
            )

    with OUT_MD.open("w") as f:
        f.write("# W7900 vs existing cross-device Netlib reference 20260611\n\n")
        f.write("> 中文: [w7900_vs_cross_device_27cases_20260611.zh-CN.md](w7900_vs_cross_device_27cases_20260611.zh-CN.md)\n\n")
        f.write("CSV source: [w7900_vs_cross_device_27cases_20260611.csv](w7900_vs_cross_device_27cases_20260611.csv)\n\n")
        f.write("Compared inputs:\n\n")
        f.write("- Existing cross-device reference: [cross_device_full_summary.csv](cross_device_full_summary.csv)\n")
        f.write("- W7900 baseline: [w7900_27cases_baseline_20260611_aggregated.csv](w7900_27cases_baseline_20260611_aggregated.csv)\n\n")
        f.write("Metric definition:\n\n")
        f.write("```text\n")
        f.write("old_over_w7900_speed_ratio = old_platform_gpu_time_sec / W7900_median_solve_time_sec\n")
        f.write("> 1.0 means W7900 is faster for that case.\n")
        f.write("< 1.0 means the existing reference platform is faster for that case.\n")
        f.write("```\n\n")
        f.write("Important caveat: the existing cross-device CSV records single-run `gpu_time_sec`, while the W7900 baseline uses repeated-run median solve time. This is a cross-device reference comparison, not a same-platform tuning-gain measurement.\n\n")
        f.write("## Platform summary\n\n")
        write_table(f, summary)
        f.write("\n## Interpretation\n\n")
        f.write("- W7900 is not yet faster overall in this current first-port baseline.\n")
        f.write("- The result should be used to identify tuning targets, not to judge final hardware capability.\n")
        f.write("- Future W7900 tuning should compare against the W7900 baseline on the same platform, using the same 27-case list and repeated median metric.\n\n")
        f.write("## Per-case comparison\n\n")
        f.write("| device | case | tier | old time | W7900 median | old/W7900 | winner | old iter | W7900 iter |\n")
        f.write("|---|---|---|---:|---:|---:|---|---:|---|\n")
        for r in rows:
            f.write(
                f"| {r['device']} {r['backend']} | {r['case']} | {r['tier']} | "
                f"{r['old_gpu_time_sec']} | {r['w7900_median_solve_time_sec']} | "
                f"{float(r['old_over_w7900_speed_ratio']):.6g} | {r['winner']} | "
                f"{r['old_gpu_iter']} | {r['w7900_nIter']} |\n"
            )

    with OUT_ZH.open("w") as f:
        f.write("# W7900 vs 既有跨设备 Netlib reference 20260611\n\n")
        f.write("> English: [w7900_vs_cross_device_27cases_20260611.md](w7900_vs_cross_device_27cases_20260611.md)\n\n")
        f.write("CSV 来源: [w7900_vs_cross_device_27cases_20260611.csv](w7900_vs_cross_device_27cases_20260611.csv)\n\n")
        f.write("对比输入:\n\n")
        f.write("- 既有跨设备 reference: [cross_device_full_summary.csv](cross_device_full_summary.csv)\n")
        f.write("- W7900 baseline: [w7900_27cases_baseline_20260611_aggregated.csv](w7900_27cases_baseline_20260611_aggregated.csv)\n\n")
        f.write("指标定义:\n\n")
        f.write("```text\n")
        f.write("old_over_w7900_speed_ratio = old_platform_gpu_time_sec / W7900_median_solve_time_sec\n")
        f.write("> 1.0 表示该 case 上 W7900 更快。\n")
        f.write("< 1.0 表示该 case 上既有 reference 平台更快。\n")
        f.write("```\n\n")
        f.write("注意：既有 cross-device CSV 是单次 `gpu_time_sec`，W7900 baseline 是三次 repeated run 的 median solve time。因此这是跨设备参考比较，不是同平台 tuning gain。\n\n")
        f.write("## 平台汇总\n\n")
        write_table(f, summary)
        f.write("\n## 解释\n\n")
        f.write("- 当前 first-port baseline 下，W7900 整体还没有快过已有 reference 平台。\n")
        f.write("- 这个结果更适合用来定位 W7900 后续 tuning 目标，而不是评价 W7900 的最终硬件能力。\n")
        f.write("- 后续 W7900 tuning 应在同一平台上，与本 W7900 baseline 使用同一 27-case list 和 repeated median 指标比较。\n\n")
        f.write("## Per-case 对比\n\n")
        f.write("| device | case | tier | old time | W7900 median | old/W7900 | winner | old iter | W7900 iter |\n")
        f.write("|---|---|---|---:|---:|---:|---|---:|---|\n")
        for r in rows:
            f.write(
                f"| {r['device']} {r['backend']} | {r['case']} | {r['tier']} | "
                f"{r['old_gpu_time_sec']} | {r['w7900_median_solve_time_sec']} | "
                f"{float(r['old_over_w7900_speed_ratio']):.6g} | {r['winner']} | "
                f"{r['old_gpu_iter']} | {r['w7900_nIter']} |\n"
            )

    print(f"[ok] wrote {OUT_CSV}")
    print(f"[ok] wrote {OUT_MD}")
    print(f"[ok] wrote {OUT_ZH}")


if __name__ == "__main__":
    main()
