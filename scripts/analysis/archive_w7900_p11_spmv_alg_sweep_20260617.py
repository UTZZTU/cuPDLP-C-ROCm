#!/usr/bin/env python3
from pathlib import Path
import csv
import math
import re
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "validation"
LATEST = Path("/app/cupdlp_w7900/results/latest_w7900_p11_spmv_alg_sweep.txt")

OUT_CSV = VALIDATION / "w7900_p11_spmv_alg_sweep_20260617.csv"
OUT_MD = VALIDATION / "w7900_p11_spmv_alg_sweep_20260617_summary.md"
OUT_ZH = VALIDATION / "w7900_p11_spmv_alg_sweep_20260617_summary.zh-CN.md"

MODES = ["csr_alg2", "env_default", "csr_alg1"]
CASES = ["L2CTA3D", "set-cover-model", "square41", "thk_48", "tpl-tub-ws1617"]

PATTERNS = {
    "status": re.compile(r"Solving information:\s*(.*)"),
    "primal_objective": re.compile(r"Primal objective:\s*([+-]?\d+\.\d+e[+-]\d+)"),
    "dual_objective": re.compile(r"Dual objective:\s*([+-]?\d+\.\d+e[+-]\d+)"),
    "primal_infeas": re.compile(r"Primal infeas \(abs/rel\):\s*([0-9.eE+-]+)\s*/\s*([0-9.eE+-]+)"),
    "dual_infeas": re.compile(r"Dual infeas \(abs/rel\):\s*([0-9.eE+-]+)\s*/\s*([0-9.eE+-]+)"),
    "duality_gap": re.compile(r"Duality gap \(abs/rel\):\s*([0-9.eE+-]+)\s*/\s*([0-9.eE+-]+)"),
    "niter": re.compile(r"Number of iterations:\s*(\d+)"),
    "total_solver_time": re.compile(r"Total solver time\s*([0-9.eE+-]+)\s+in\s+(\d+)\s+iterations"),
    "solve_time": re.compile(r"Solve time\s*([0-9.eE+-]+)\s+in\s+(\d+)\s+iterations"),
    "iters_per_sec": re.compile(r"Iters per sec\s*([0-9.eE+-]+)"),
    "update_iterates": re.compile(r"UpdateIterates\s*([0-9.eE+-]+)\s+in\s+(\d+)\s+calls"),
}

def read_latest_root() -> Path:
    if not LATEST.exists():
        raise FileNotFoundError(f"missing latest pointer: {LATEST}")
    result_root = Path(LATEST.read_text(encoding="utf-8").strip())
    if not result_root.exists():
        raise FileNotFoundError(f"missing result root: {result_root}")
    return result_root

def read_exit(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    m = re.search(r"exit=(\d+)", text)
    return m.group(1) if m else text

def parse_summary(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    row = {}

    m = PATTERNS["status"].search(text)
    row["status"] = m.group(1).strip() if m else ""

    for key in ["primal_objective", "dual_objective", "niter", "iters_per_sec"]:
        m = PATTERNS[key].search(text)
        row[key] = m.group(1) if m else ""

    m = PATTERNS["primal_infeas"].search(text)
    row["primal_infeas_abs"] = m.group(1) if m else ""
    row["primal_infeas_rel"] = m.group(2) if m else ""

    m = PATTERNS["dual_infeas"].search(text)
    row["dual_infeas_abs"] = m.group(1) if m else ""
    row["dual_infeas_rel"] = m.group(2) if m else ""

    m = PATTERNS["duality_gap"].search(text)
    row["duality_gap_abs"] = m.group(1) if m else ""
    row["duality_gap_rel"] = m.group(2) if m else ""

    m = PATTERNS["total_solver_time"].search(text)
    row["total_solver_time_sec"] = m.group(1) if m else ""

    m = PATTERNS["solve_time"].search(text)
    row["solve_time_sec"] = m.group(1) if m else ""

    m = PATTERNS["update_iterates"].search(text)
    row["update_iterates_sec"] = m.group(1) if m else ""
    row["update_iterates_calls"] = m.group(2) if m else ""

    return row

def collect_rows(result_root: Path):
    rows = []
    for mode in MODES:
        for case in CASES:
            case_dir = result_root / mode / case
            summary_file = case_dir / f"{case}_{mode}.summary.txt"
            exit_file = case_dir / f"{case}_{mode}.exit"

            if not summary_file.exists():
                raise FileNotFoundError(summary_file)
            if not exit_file.exists():
                raise FileNotFoundError(exit_file)

            row = {
                "mode": mode,
                "case": case,
                "exitcode": read_exit(exit_file),
                "run_dir": str(case_dir),
            }
            row.update(parse_summary(summary_file))
            rows.append(row)
    return rows

def f(x):
    try:
        return float(x)
    except Exception:
        return float("nan")

def fmt(x, digits=6):
    if isinstance(x, str):
        return x
    if x is None or not math.isfinite(x):
        return ""
    if abs(x) >= 1000:
        return f"{x:.3f}"
    if abs(x) >= 1:
        return f"{x:.{digits}f}"
    return f"{x:.6e}"

def write_csv(rows):
    fields = [
        "mode",
        "case",
        "exitcode",
        "status",
        "niter",
        "total_solver_time_sec",
        "solve_time_sec",
        "iters_per_sec",
        "update_iterates_sec",
        "update_iterates_calls",
        "primal_objective",
        "dual_objective",
        "primal_infeas_abs",
        "primal_infeas_rel",
        "dual_infeas_abs",
        "dual_infeas_rel",
        "duality_gap_abs",
        "duality_gap_rel",
        "run_dir",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] wrote {OUT_CSV.relative_to(ROOT)}")

def pivot(rows):
    by_case = defaultdict(dict)
    for r in rows:
        by_case[r["case"]][r["mode"]] = r
    return by_case

def geomean(vals):
    vals = [v for v in vals if v > 0 and math.isfinite(v)]
    return math.prod(vals) ** (1.0 / len(vals)) if vals else float("nan")

def winner_for_case(modes):
    return min(MODES, key=lambda m: f(modes[m]["solve_time_sec"]))

def comparison_table(rows):
    by_case = pivot(rows)
    out = [
        "| case | status stable | nIter stable | csr_alg2 solve s | env_default solve s | csr_alg1 solve s | best solve mode | csr_alg1 / csr_alg2 | env_default / csr_alg2 |",
        "|---|---:|---:|---:|---:|---:|---|---:|---:|",
    ]

    ratios_alg1 = []
    ratios_default = []

    for case in CASES:
        modes = by_case[case]
        statuses = {modes[m]["status"] for m in MODES}
        niters = {modes[m]["niter"] for m in MODES}

        base = f(modes["csr_alg2"]["solve_time_sec"])
        alg1 = f(modes["csr_alg1"]["solve_time_sec"])
        env = f(modes["env_default"]["solve_time_sec"])
        ratio_alg1 = alg1 / base
        ratio_env = env / base
        ratios_alg1.append(ratio_alg1)
        ratios_default.append(ratio_env)

        out.append(
            "| {case} | {status_stable} | {niter_stable} | {base} | {env} | {alg1} | {winner} | {ratio_alg1} | {ratio_env} |".format(
                case=case,
                status_stable=str(len(statuses) == 1),
                niter_stable=str(len(niters) == 1),
                base=fmt(base),
                env=fmt(env),
                alg1=fmt(alg1),
                winner=winner_for_case(modes),
                ratio_alg1=fmt(ratio_alg1),
                ratio_env=fmt(ratio_env),
            )
        )

    out.append(
        "| geomean | — | — | — | — | — | — | {alg1_gm} | {env_gm} |".format(
            alg1_gm=fmt(geomean(ratios_alg1)),
            env_gm=fmt(geomean(ratios_default)),
        )
    )
    return "\n".join(out)

def write_md(rows, result_root: Path):
    by_case = pivot(rows)
    all_exit_zero = all(r["exitcode"] == "0" for r in rows)
    status_stable = all(len({by_case[c][m]["status"] for m in MODES}) == 1 for c in CASES)
    niter_stable = all(len({by_case[c][m]["niter"] for m in MODES}) == 1 for c in CASES)

    winners = [winner_for_case(by_case[c]) for c in CASES]
    winner_counts = {m: winners.count(m) for m in MODES}

    md = f"""# W7900 P11 SpMV algorithm sweep summary

Run dir: `{result_root}`

This P11 sweep evaluates the opt-in HIP SpMV algorithm switch introduced by:

- `d1c2465 tuning: add opt-in HIP SpMV algorithm switch`

Modes:

- `csr_alg2`: default behavior, no `CUPDLP_HIP_SPMV_ALG` environment variable
- `env_default`: `CUPDLP_HIP_SPMV_ALG=default`
- `csr_alg1`: `CUPDLP_HIP_SPMV_ALG=csr_alg1`

Cases:

- `L2CTA3D`
- `set-cover-model`
- `square41`
- `thk_48`
- `tpl-tub-ws1617`

Raw logs remain under `/app/cupdlp_w7900/results` and are intentionally not committed.

## Correctness and stability

- All 15 runs exit with code 0: `{all_exit_zero}`
- Solver status is stable across modes for each case: `{status_stable}`
- Iteration count is stable across modes for each case: `{niter_stable}`

## Solve-time comparison

{comparison_table(rows)}

## Interpretation

The three SpMV algorithm modes all preserve solver status and iteration count on the five targeted P10 cases. `csr_alg1` is the fastest mode on four of the five cases by single-run solve time, while the default `csr_alg2` is slightly faster on the short `L2CTA3D` case. The geometric-mean solve-time ratio of `csr_alg1 / csr_alg2` is below 1.0, but the margin is small. This should be treated as a promising experiment result, not yet as a final performance conclusion.

Next validation should either repeat the sweep to estimate run-to-run noise, or profile the most interesting pair, `csr_alg1` vs `csr_alg2`, with rocprofv3 on `set-cover-model`, `square41`, `thk_48`, and `tpl-tub-ws1617`.

## Files

- `w7900_p11_spmv_alg_sweep_20260617.csv`
"""
    OUT_MD.write_text(md, encoding="utf-8", newline="\n")
    print(f"[OK] wrote {OUT_MD.relative_to(ROOT)}")

    zh = f"""# W7900 P11 SpMV algorithm sweep 汇总

运行目录：`{result_root}`

本次 P11 sweep 评估如下提交引入的 opt-in HIP SpMV algorithm switch：

- `d1c2465 tuning: add opt-in HIP SpMV algorithm switch`

模式：

- `csr_alg2`：默认行为，不设置 `CUPDLP_HIP_SPMV_ALG`
- `env_default`：`CUPDLP_HIP_SPMV_ALG=default`
- `csr_alg1`：`CUPDLP_HIP_SPMV_ALG=csr_alg1`

Case：

- `L2CTA3D`
- `set-cover-model`
- `square41`
- `thk_48`
- `tpl-tub-ws1617`

原始日志继续保留在 `/app/cupdlp_w7900/results`，不提交到 Git。

## 正确性与稳定性

- 15 个 run 全部 exit code 为 0：`{all_exit_zero}`
- 每个 case 在三种 mode 下 solver status 稳定：`{status_stable}`
- 每个 case 在三种 mode 下迭代数稳定：`{niter_stable}`

## 求解时间对比

{comparison_table(rows)}

## 解释

三种 SpMV algorithm mode 在 P10 的五个 targeted case 上都保持了 solver status 和迭代数一致。按单次 solve time 看，`csr_alg1` 在 5 个 case 中有 4 个最快，而默认 `csr_alg2` 在短 case `L2CTA3D` 上略快。`csr_alg1 / csr_alg2` 的 solve-time 几何平均低于 1.0，但幅度很小。因此这应被写成“有希望的实验结果”，不能直接写成最终性能结论。

下一步可以选择重复 sweep 估计运行噪声，或者对更有代表性的 `csr_alg1` vs `csr_alg2` 做 rocprofv3 对比，优先 case 为 `set-cover-model`、`square41`、`thk_48`、`tpl-tub-ws1617`。

## 文件

- `w7900_p11_spmv_alg_sweep_20260617.csv`
"""
    OUT_ZH.write_text(zh, encoding="utf-8", newline="\n")
    print(f"[OK] wrote {OUT_ZH.relative_to(ROOT)}")

def main():
    result_root = read_latest_root()
    rows = collect_rows(result_root)
    write_csv(rows)
    write_md(rows, result_root)
    print("[DONE] archived W7900 P11 SpMV algorithm sweep")

if __name__ == "__main__":
    main()
