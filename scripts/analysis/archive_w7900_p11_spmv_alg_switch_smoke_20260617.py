#!/usr/bin/env python3
from pathlib import Path
import csv
import re
from collections import defaultdict
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
RESULTS = Path("/app/cupdlp_w7900/results")
VALIDATION = ROOT / "validation"

OUT_CSV = VALIDATION / "w7900_p11_spmv_alg_switch_smoke_20260617.csv"
OUT_MD = VALIDATION / "w7900_p11_spmv_alg_switch_smoke_20260617_summary.md"
OUT_ZH = VALIDATION / "w7900_p11_spmv_alg_switch_smoke_20260617_summary.zh-CN.md"

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

def mode_from_dir(path: Path) -> str:
    name = path.name
    if "smoke_env_default_" in name:
        return "env_default"
    if "smoke_csr_alg1_" in name:
        return "csr_alg1"
    if "smoke_default_" in name:
        return "default"
    return "unknown"

def read_exit(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    m = re.search(r"exit=(\d+)", text)
    return m.group(1) if m else text

def parse_log(path: Path) -> dict:
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

def collect_rows():
    rows = []
    dirs = sorted(
        d for d in RESULTS.iterdir()
        if d.is_dir() and d.name.startswith("w7900_p11_spmv_alg_switch_smoke_")
    )

    for d in dirs:
        mode = mode_from_dir(d)
        if mode == "unknown":
            continue

        logs = sorted(d.glob("set-cover-model*.log"))
        if not logs:
            continue

        for log in logs:
            if "csr_alg1" in log.name:
                exit_file = d / "set-cover-model_csr_alg1.exit"
            elif "env_default" in log.name:
                exit_file = d / "set-cover-model_env_default.exit"
            else:
                exit_file = d / "set-cover-model_default.exit"

            row = {
                "mode": mode,
                "case": "set-cover-model",
                "run_dir": str(d),
                "log_file": log.name,
                "exitcode": read_exit(exit_file),
            }
            row.update(parse_log(log))
            rows.append(row)

    if not rows:
        raise RuntimeError("No P11 SpMV smoke rows found under /app/cupdlp_w7900/results")

    return rows

def f(x):
    try:
        return float(x)
    except Exception:
        return None

def fmt(x, digits=6):
    if x is None:
        return ""
    if abs(x) >= 100:
        return f"{x:.3f}"
    if abs(x) >= 1:
        return f"{x:.6f}"
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
        "log_file",
    ]

    with OUT_CSV.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] wrote {OUT_CSV.relative_to(ROOT)}")

def aggregate(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[r["mode"]].append(r)

    out = []
    for mode in ["default", "env_default", "csr_alg1"]:
        rs = groups.get(mode, [])
        if not rs:
            continue
        solve_times = [f(r["solve_time_sec"]) for r in rs if f(r["solve_time_sec"]) is not None]
        total_times = [f(r["total_solver_time_sec"]) for r in rs if f(r["total_solver_time_sec"]) is not None]
        update_times = [f(r["update_iterates_sec"]) for r in rs if f(r["update_iterates_sec"]) is not None]
        niter_values = sorted(set(r["niter"] for r in rs))
        status_values = sorted(set(r["status"] for r in rs))
        exit_values = sorted(set(r["exitcode"] for r in rs))

        out.append({
            "mode": mode,
            "runs": len(rs),
            "exitcodes": ", ".join(exit_values),
            "statuses": "; ".join(status_values),
            "niter": ", ".join(niter_values),
            "solve_mean": mean(solve_times) if solve_times else None,
            "solve_min": min(solve_times) if solve_times else None,
            "solve_max": max(solve_times) if solve_times else None,
            "total_mean": mean(total_times) if total_times else None,
            "update_mean": mean(update_times) if update_times else None,
        })
    return out

def md_table(rows):
    out = [
        "| mode | runs | exitcodes | status | nIter | mean solve s | min solve s | max solve s | mean total s | mean UpdateIterates s |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        out.append(
            "| {mode} | {runs} | {exitcodes} | {statuses} | {niter} | {solve_mean} | {solve_min} | {solve_max} | {total_mean} | {update_mean} |".format(
                mode=r["mode"],
                runs=r["runs"],
                exitcodes=r["exitcodes"],
                statuses=r["statuses"],
                niter=r["niter"],
                solve_mean=fmt(r["solve_mean"]),
                solve_min=fmt(r["solve_min"]),
                solve_max=fmt(r["solve_max"]),
                total_mean=fmt(r["total_mean"]),
                update_mean=fmt(r["update_mean"]),
            )
        )
    return "\n".join(out)

def write_md(rows):
    agg = aggregate(rows)
    all_exit_zero = all(r["exitcode"] == "0" for r in rows)
    all_optimal = all("Optimal current solution" in r["status"] for r in rows)
    all_niter_same = len(set(r["niter"] for r in rows)) == 1

    md = f"""# W7900 P11 SpMV algorithm switch smoke summary

This smoke validation checks the first real P11 tuning patch:

- commit: `d1c2465 tuning: add opt-in HIP SpMV algorithm switch`
- case: `set-cover-model`
- default behavior: `HIPSPARSE_SPMV_CSR_ALG2`
- opt-in modes:
  - `CUPDLP_HIP_SPMV_ALG=default`
  - `CUPDLP_HIP_SPMV_ALG=csr_alg1`

Raw logs remain under `/app/cupdlp_w7900/results` and are not committed.

## Result

- All runs exit with code 0: `{all_exit_zero}`
- All runs report `Optimal current solution`: `{all_optimal}`
- All runs use the same iteration count: `{all_niter_same}`
- Observed iteration count: `{rows[0]["niter"]}`

## Aggregated timing

{md_table(agg)}

## Interpretation

The opt-in SpMV algorithm switch passes the initial smoke validation on `set-cover-model`. All three modes preserve solver status, iteration count, objective values, primal infeasibility, dual infeasibility, and duality gap. The timing differences in this small smoke are within a narrow range and should not yet be treated as a performance conclusion.

The patch is therefore suitable for a broader P11 sweep on the five targeted P10 cases. The next validation should compare `default`, `csr_alg1`, and the default `csr_alg2` mode across `L2CTA3D`, `set-cover-model`, `square41`, `thk_48`, and `tpl-tub-ws1617`.

## Files

- `w7900_p11_spmv_alg_switch_smoke_20260617.csv`
"""
    OUT_MD.write_text(md, encoding="utf-8", newline="\n")
    print(f"[OK] wrote {OUT_MD.relative_to(ROOT)}")

    zh = f"""# W7900 P11 SpMV algorithm switch smoke 汇总

本次 smoke validation 检查第一个真正的 P11 tuning patch：

- commit：`d1c2465 tuning: add opt-in HIP SpMV algorithm switch`
- case：`set-cover-model`
- 默认行为：`HIPSPARSE_SPMV_CSR_ALG2`
- opt-in 模式：
  - `CUPDLP_HIP_SPMV_ALG=default`
  - `CUPDLP_HIP_SPMV_ALG=csr_alg1`

原始日志继续保留在 `/app/cupdlp_w7900/results`，不提交到 Git。

## 结果

- 所有运行 exit code 均为 0：`{all_exit_zero}`
- 所有运行均报告 `Optimal current solution`：`{all_optimal}`
- 所有运行迭代数一致：`{all_niter_same}`
- 观察到的迭代数：`{rows[0]["niter"]}`

## 聚合时间

{md_table(agg)}

## 解释

opt-in SpMV algorithm switch 在 `set-cover-model` 上通过初始 smoke validation。三种模式均保持 solver status、迭代数、目标值、primal infeasibility、dual infeasibility 和 duality gap 一致。本次小规模 smoke 中的时间差异范围较窄，暂时不能作为性能结论。

因此该 patch 适合进入更完整的 P11 sweep。下一步应在 P10 的五个 targeted cases 上比较 `default`、`csr_alg1` 和默认 `csr_alg2` 模式，即 `L2CTA3D`、`set-cover-model`、`square41`、`thk_48`、`tpl-tub-ws1617`。

## 文件

- `w7900_p11_spmv_alg_switch_smoke_20260617.csv`
"""
    OUT_ZH.write_text(zh, encoding="utf-8", newline="\n")
    print(f"[OK] wrote {OUT_ZH.relative_to(ROOT)}")

def main():
    rows = collect_rows()
    rows.sort(key=lambda r: (r["mode"], r["run_dir"], r["log_file"]))
    write_csv(rows)
    write_md(rows)
    print("[DONE] archived P11 SpMV algorithm switch smoke validation")

if __name__ == "__main__":
    main()
